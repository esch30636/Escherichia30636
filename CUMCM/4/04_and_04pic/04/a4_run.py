# -*- coding: utf-8 -*-
"""Q4 deep-solve driver: drying time, table 6, verification; CLI for one case.

Conventions (A3-codex aligned):
  - continuous crossing: event max(C_field) - 0.15 = 0, direction -1
  - first strict minute: first 60-s grid point with max C < 0.15 (unrounded)
  - output columns: fixed distances 0,0.1,...,1.1 cm + surface column
"""
import sys, io, os, json, time
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
import numpy as np
from scipy.integrate import solve_ivp, OdeSolution
import a4_model as M

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'out')
os.makedirs(OUT, exist_ok=True)

N_DEFAULT = 800
RTOL = 1e-11


def chamber_tail(scenario):
    """Post-14400-s hold. Returns (Ta, Ca) degC, kg/kg."""
    t, T, C = M.CH_T, M.CH_TC, M.CH_CC
    tail = [T[-1], C[-1]]
    if scenario == 'final':
        pass
    elif scenario == 'stage_mean':
        seg = (t >= 7200) & (t <= 14400)
        tail = [T[seg].mean(), C[seg].mean()]
    elif scenario == 'last_hour_mean':
        w = (t >= 10800) & (t <= 14400)
        tail = [np.trapezoid(T[w], t[w]) / 3600.0, np.trapezoid(C[w], t[w]) / 3600.0]
    elif scenario == 'last2h_mean':
        w = (t >= 7200) & (t <= 14400)
        tail = [np.trapezoid(T[w], t[w]) / 7200.0, np.trapezoid(C[w], t[w]) / 7200.0]
    elif scenario == 't50':
        tail = [50.0, C[-1]]
    elif scenario == 't50c05':
        tail = [50.0, 0.05]
    elif scenario == 'last_hour_meanT_finalC':
        w = (t >= 10800) & (t <= 14400)
        tail = [np.trapezoid(T[w], t[w]) / 3600.0, C[-1]]
    elif scenario == 'finalT_meanc':
        tail = [T[-1], np.trapezoid(C[(t >= 10800) & (t <= 14400)], t[(t >= 10800) & (t <= 14400)]) / 3600.0]
    elif scenario == 'smooth11':
        w = np.ones(11) / 11.0
        tail = [np.convolve(np.pad(T, (5, 5), mode='edge'), w, mode='valid')[-1],
                np.convolve(np.pad(C, (5, 5), mode='edge'), w, mode='valid')[-1]]
    else:
        raise ValueError(scenario)
    return tuple(tail)


class Q4Solver:
    def __init__(self, n=N_DEFAULT, rtol=RTOL, scenario='final', mesh='graded',
                 radius_mode='linear', latent=None, appx=4, df=1.0,
                 tmax_h=96.0, max_step=300.0, sample_dt=60.0, chamber_series=None):
        self.n = int(n)
        self.rtol = rtol
        self.scenario = scenario
        self.mesh_kind = mesh
        self.radius_mode = radius_mode
        self.latent = latent or {'mode': 'none', 'rho': 'dry0', 'lv': M.LV_STD}
        self.appx = appx
        self.df = df
        self.tmax = tmax_h * 3600.0
        self.max_step = max_step
        self.sample_dt = sample_dt
        if n < 3 or sample_dt <= 0 or abs(21600 / sample_dt - round(21600 / sample_dt)) > 1e-9:
            raise ValueError('n >= 3; sample_dt must be a positive divisor of 21600 s')
        if radius_mode not in ('linear', 'fixed'):
            raise ValueError('radius_mode must be linear or fixed')
        self.x, self.v, self.g, self.half = M.mesh(self.n, mesh)
        self.sp = M.sparsity(self.n)
        if scenario == 'smooth11':
            w = np.ones(11) / 11.0
            self.t_ch = M.CH_T
            self.T_ch = np.convolve(np.pad(M.CH_TC, (5, 5), mode='edge'), w, mode='valid')
            self.C_ch = np.convolve(np.pad(M.CH_CC, (5, 5), mode='edge'), w, mode='valid')
        elif chamber_series is not None:
            self.t_ch, self.T_ch, self.C_ch = chamber_series
        else:
            self.t_ch, self.T_ch, self.C_ch = M.CH_T, M.CH_TC, M.CH_CC
        self.tail = chamber_tail(scenario)
        lm = self.latent['mode']
        if lm not in ('none', 'vol', 'surf'):
            raise ValueError('Unknown latent mode')
        self.lmode = 0 if lm == 'none' else (1 if lm == 'vol' else 2)
        self.lv = float(self.latent.get('lv', M.LV_STD))
        if appx == 4:
            self.rho_d0 = (760. + 90. * 2.55) / (1. + 2.55)   # 278.732 kg/m^3
        else:
            self.rho_d0 = (650. + 128. * 2.55) / (1. + 2.55)  # 275.042 kg/m^3
        rmode = self.latent.get('rho', 'dry0')
        if rmode not in ('dry0', 'unit'):
            raise ValueError('Only dry0 and unit are supported. Legacy dry/bulk grid means lack a consistent density closure.')
        self.rhoc_mode = rmode
        self.rhoc0 = {'dry0': self.rho_d0, 'unit': 1.0}[rmode]

    # ---------- environment / radius ----------
    def air(self, t):
        t = np.asarray(t, float)
        T = np.interp(t, self.t_ch, self.T_ch)
        C = np.interp(t, self.t_ch, self.C_ch)
        T = np.where(t > 14400.0, self.tail[0], T)
        C = np.where(t > 14400.0, self.tail[1], C)
        return np.stack([T, C], axis=-1)

    def R_of(self, t):
        if self.appx != 4 or self.radius_mode == 'fixed':
            return np.full_like(np.asarray(t, float), M.R0)
        t = np.asarray(t, float)
        if self.radius_mode == 'linear':
            return np.interp(t, M.RD_T, M.RD_R)
        idx = np.clip(np.searchsorted(M.RD_T, t, side='right') - 1, 0, len(M.RD_T) - 1)
        return M.RD_R[idx]

    def _rhoc0_from_state(self, y):
        return self.rhoc0

    def sample(self, states, times, distances):
        Rs = self.R_of(times)
        rhocs = np.array([self._rhoc0_from_state(y) for y in states]) * (M.R0 / Rs) ** 2
        return M.sample_many(states.T, self.x, self.half, self.air(times), Rs,
                             M.queries_for(distances, Rs), M.HCONV, M.HM, self.df,
                             self.appx, self.lmode, rhocs, self.lv)

    # ---------- RHS / event ----------
    def make_rhs(self):
        def rhs(t, y):
            R = float(self.R_of(t))
            ta, ca = self.air(t)
            return M.kernel(y, self.x, self.v, self.g, self.half,
                            ta, ca, R, M.HCONV, M.HM, self.df,
                            self.lmode, self._rhoc0_from_state(y), self.lv,
                            self.appx)[0]
        return rhs

    def make_event(self):
        def center(c):
            return (self.x[1] ** 2 * c[0] - self.x[0] ** 2 * c[1]) / (self.x[1] ** 2 - self.x[0] ** 2)

        def event(t, y):
            c = y[1::2]
            R = float(self.R_of(t))
            ta, ca = self.air(t)
            cs = M.boundary(y[-2], y[-1], ta, ca, self.half, R, M.HCONV, M.HM, self.df,
                            self.lmode, self._rhoc0_from_state(y) * (M.R0 / R) ** 2,
                            self.lv, self.appx)[1]
            return max(center(c), np.max(c), cs) - M.CTARGET
        event.direction = -1
        event.terminal = True
        return event

    # ---------- integrate ----------
    def integrate(self):
        rhs = self.make_rhs()
        ev = self.make_event()
        y = np.tile([M.T0, M.C0], self.n)
        times = [0.0]
        states = [y.copy()]
        crossing = None
        integrals = np.zeros(6)      # qt, qc, int R2*co, int 2R*Rd*sumC, int 2R*Rd*sumCapT, int co
        max_identity = np.zeros(2)
        stats = {'steps': 0, 'nfev': 0}
        left = 0.0
        while left < self.tmax - 1e-6:
            right = min(self.tmax, min(left + 60.0, 14400.0) if left < 14400.0 else left + 24.0 * 3600.0)
            sol = solve_ivp(rhs, (left, right), y, method='BDF', jac_sparsity=self.sp,
                            rtol=self.rtol, atol=np.tile([self.rtol * .1, self.rtol * .01], self.n),
                            max_step=10.0 if left < 14400.0 else self.max_step,
                            dense_output=True, events=ev)
            if not sol.success:
                raise RuntimeError(f'integrate failed at {left}: {sol.message}')
            stats['steps'] += len(sol.t) - 1
            stats['nfev'] += sol.nfev
            if len(sol.t_events[0]) and crossing is None:
                crossing = float(sol.t_events[0][0])
            end = right if crossing is None else (np.floor(crossing / 60.0) + 1) * 60.0
            if end > self.tmax:
                raise RuntimeError('tmax ends before the first strict minute')
            if crossing is not None:
                # Actually integrate beyond the root; never extrapolate a terminal dense solution.
                extra = solve_ivp(rhs, (crossing, end), sol.y[:, -1], method='BDF',
                                  jac_sparsity=self.sp, rtol=self.rtol,
                                  atol=np.tile([self.rtol * .1, self.rtol * .01], self.n),
                                  max_step=min(10., self.max_step), dense_output=True)
                if not extra.success:
                    raise RuntimeError(extra.message)
                stats['steps'] += len(extra.t) - 1
                stats['nfev'] += extra.nfev
                sol.sol = OdeSolution(np.r_[sol.sol.ts, extra.sol.ts[1:]],
                                      sol.sol.interpolants + extra.sol.interpolants)
                sol.t = np.r_[sol.t, extra.t[1:]]
                if ev(end, extra.y[:, -1]) >= 0:
                    raise RuntimeError('The minute after crossing is not strictly compliant')
            first = (np.floor(left / self.sample_dt + 1e-9) + 1) * self.sample_dt
            ts = np.arange(first, end + 1e-6, self.sample_dt)
            if len(ts):
                ys = sol.sol(ts)
                times.extend(ts)
                states.extend(ys.T)
            # Gauss integration of the actual boundary flux (mass & heat identity)
            knots = np.unique(np.r_[sol.t[sol.t <= end], end])
            mids = (knots[1:] + knots[:-1]) / 2
            widths = np.diff(knots) / 2
            for z, w in ((-.7745966692414834, 5 / 9), (0., 8 / 9), (.7745966692414834, 5 / 9)):
                tq = mids + z * widths
                yq = sol.sol(tq)
                for j in range(len(tq)):
                    Rq = float(self.R_of(tq[j]))
                    taq, caq = self.air(tq[j])
                    dy, qt, qc, co = M.kernel(yq[:, j], self.x, self.v, self.g, self.half,
                                              taq, caq, Rq, M.HCONV, M.HM, self.df,
                                              self.lmode, self._rhoc0_from_state(yq[:, j]),
                                              self.lv, self.appx)
                    cq = yq[1::2, j]
                    tq_ = yq[0::2, j]
                    if self.appx == 4:
                        cap = (760. + 90. * cq) * (1850. + 2150. * cq / (1. + cq))
                    else:
                        cap = (650. + 128. * cq) * (1450. + 2736. * cq / (1. + cq))
                    eps = 0.5
                    Rdot = (self.R_of(tq[j] + eps) - self.R_of(tq[j] - eps)) / (2 * eps)
                    R2 = Rq * Rq
                    integrals += w * widths[j] * np.array([
                        qt, qc, R2 * co, 2 * Rq * Rdot * float(self.v @ cq),
                        2 * Rq * Rdot * float(self.v @ (cap * tq_)), co])
                    latent_sum = (self.lv * self._rhoc0_from_state(yq[:, j]) * (M.R0 / Rq) ** 2
                                  * float(self.v @ (R2 * dy[1::2]))) if self.lmode == 1 else 0.
                    max_identity = np.maximum(max_identity, [
                        abs(self.v @ (R2 * dy[1::2]) + qc),
                        abs((self.v * R2 * cap) @ dy[0::2] + qt - latent_sum)])
            y = sol.sol(end)
            left = end
            if crossing is not None:
                break
        if crossing is None:
            raise RuntimeError(f'no crossing within {self.tmax / 3600:.0f} h')
        # append the final state (first strict minute) to the sample series
        if not times or abs(times[-1] - left) > 1e-9:
            times.append(left)
            states.append(y)
        times = np.array(times)
        states = np.array(states)
        return times, states, crossing, integrals, max_identity, stats

    # ---------- balance diagnostics ----------
    def balances(self, times, states, integrals):
        """Moving-boundary closures (integrals: qt, qc, int R2*co, int 2R*Rd*sumC,
        int 2R*Rd*sumCapT, co):
          M = sum v R^2 C,   dM/dt = 2R Rd sum(vC) - qc
          E = sum v R^2 cap T,  dE/dt = 2R Rd sum(v cap T) + R^2 sum(v cap' T dC/dt) - qt
        (no-latent; E closure valid for lmode==0 only)."""
        R_arr = self.R_of(times)
        M0 = np.sum(self.v * M.R0 ** 2) * M.C0
        Cc = states[-1, 1::2]
        Mnow = float(np.sum(self.v * R_arr[-1] ** 2 * Cc))
        res = dict(mass_closure=float(Mnow - M0 + integrals[1] - integrals[3]),
                   mass_rel=float(abs(Mnow - M0 + integrals[1] - integrals[3]) / M0))
        if self.lmode == 0:
            if self.appx == 4:
                capf = lambda c: (760. + 90. * c) * (1850. + 2150. * c / (1. + c))
            else:
                capf = lambda c: (650. + 128. * c) * (1450. + 2736. * c / (1. + c))
            cap0 = capf(np.array([M.C0]))[0]
            E0 = np.sum(self.v * M.R0 ** 2 * cap0) * M.T0
            cap = capf(Cc)
            Enow = float(np.sum(self.v * R_arr[-1] ** 2 * cap * states[-1, 0::2]))
            res['energy_closure'] = float(Enow - E0 + integrals[0] - integrals[2] - integrals[4])
            res['energy_rel'] = float(abs(res['energy_closure']) / E0)
        return res


def solve_case(name, n=N_DEFAULT, rtol=RTOL, scenario='final', mesh='graded',
               latent=None, tmax_h=96.0, max_step=300.0, appx=4, sample_dt=60.0,
               dist_cols=None, save=True, return_solver=False, radius_mode='linear'):
    """Solve one case; return dict with trajectory, crossing, minute, sampled
    field and table-6 rows."""
    s = Q4Solver(n=n, rtol=rtol, scenario=scenario, mesh=mesh, latent=latent,
                 tmax_h=tmax_h, max_step=max_step, appx=appx, sample_dt=sample_dt,
                 radius_mode=radius_mode)
    t0 = time.perf_counter()
    times, states, crossing, integrals, max_identity, stats = s.integrate()
    secs = time.perf_counter() - t0
    minute = float(times[-1])
    if dist_cols is None:
        dist_cols = np.arange(0, 1.2, 0.1) if appx == 4 else np.arange(0, 2.0, 0.1)
    R_arr = s.R_of(times)
    qs = M.queries_for(dist_cols, R_arr)
    airs = np.stack([s.air(t) for t in times], axis=0)
    fld = s.sample(states, times, dist_cols)
    cvals = np.maximum(np.max(fld[:, :-1, 1], axis=1), fld[:, -1, 1])
    if not cvals[-1] < M.CTARGET:
        raise RuntimeError('last sampled minute not strictly compliant')
    bal = s.balances(times, states, integrals)
    radial_inc = float(np.max(np.diff(states[:, 1::2], axis=1)))
    # Every 6 hours until the actual endpoint, then the endpoint itself.
    t6_rows = np.arange(21600., minute, 21600.).tolist()
    t6_rows = [t / 3600 for t in t6_rows]
    t6q = np.array([th * 3600.0 for th in t6_rows] + [minute])
    Rs6 = s.R_of(t6q)
    qs6 = M.queries_for(np.array([0., 0.5, 1.0]), Rs6)
    airs6 = np.stack([s.air(t) for t in t6q], axis=0)
    st6 = np.stack([states[np.argmin(np.abs(times - t))] for t in t6q], axis=1)
    fld6 = s.sample(st6.T, t6q, np.array([0., 0.5, 1.0]))
    res = dict(name=name, n=n, rtol=rtol, scenario=scenario, mesh=mesh,
               latent=latent, appx=appx, radius_mode=radius_mode,
               sample_dt=sample_dt, field_cols=list(map(float, dist_cols)),
               endpoint_radius_cm=float(s.R_of(minute) * 100),
               revision='audit-fix-20260912', crossing_s=crossing, minute_s=minute,
               crossing_h=crossing / 3600.0, minute_h=minute / 3600.0,
               seconds=secs, steps=stats['steps'], nfev=stats['nfev'],
               balances=bal, radial_increase_max=radial_inc,
               min_C=float(np.min(states[:, 1::2])),
               integrals=integrals.tolist(), max_identity=max_identity.tolist())
    if save:
        np.savez_compressed(os.path.join(OUT, f'{name}.npz'),
                            time_s=times, states=states, field=fld,
                            table6_times=np.array(t6_rows + [minute / 3600.0]),
                            table6_field=fld6,
                            metadata=json.dumps(res, default=str))
        with open(os.path.join(OUT, f'{name}.json'), 'w', encoding='utf-8') as f:
            json.dump(res, f, indent=2, default=str)
    print(json.dumps(res, default=str), flush=True)
    return (res, s) if return_solver else res


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--name', default='q4_tight800')
    p.add_argument('--n', type=int, default=N_DEFAULT)
    p.add_argument('--rtol', type=float, default=RTOL)
    p.add_argument('--scenario', default='final')
    p.add_argument('--mesh', default='graded')
    p.add_argument('--latent-mode', default='none', choices=['none', 'vol', 'surf'])
    p.add_argument('--latent-rho', default='dry0', choices=['dry0', 'unit'])
    p.add_argument('--radius-mode', default='linear', choices=['linear', 'fixed'])
    p.add_argument('--tmax-h', type=float, default=96.0)
    p.add_argument('--max-step', type=float, default=300.0)
    p.add_argument('--appx', type=int, default=4, choices=[3, 4])
    p.add_argument('--sample-dt', type=float, default=60.0)
    a = p.parse_args()
    latent = None
    if a.latent_mode != 'none':
        latent = {'mode': a.latent_mode, 'rho': a.latent_rho, 'lv': M.LV_STD}
    solve_case(a.name, n=a.n, rtol=a.rtol, scenario=a.scenario, mesh=a.mesh,
               latent=latent, tmax_h=a.tmax_h, max_step=a.max_step,
               appx=a.appx, sample_dt=a.sample_dt, radius_mode=a.radius_mode)
