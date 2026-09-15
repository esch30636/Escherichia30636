"""Independent re-solve of A-question 2 (0-10800 s), deliberately built with
DIFFERENT numerical choices from A2-gpt/code/solver.py, so that agreement is
evidence and not a shared-implementation artifact.

Differences from the pack under review
--------------------------------------
* uniform (or low-power) radial mesh instead of the r = R(1-(1-s)^2) grading
* interface transport coefficients from a MIDPOINT state (T,C) evaluation
  instead of a 3-point Gauss average along the cell-to-cell state path
* boundary flux taken from the half-cell Robin closure with a GHOST state at
  r = R (Kelvin conversion applied inside the same property functions)
* constant diagonal mass matrix diag(V_i) handed to the integrator, i.e. the
  discrete conservation law V_i dy_i/dt = F_i is imposed exactly rather than
  divided through
* scipy Radau (implicit RK, order 5) with its own dense finite-difference
  Jacobian, restarting only at the 1800 s ambient-slope breakpoints

State ordering y = (T_0, C_0, T_1, C_1, ...); Celsius; C is dry-basis kg/kg.
"""
from pathlib import Path
import argparse, json, time
import numpy as np
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[1]
A2 = ROOT.parent / "A2-gpt"
R = 0.02
P_ATM = 101325.0
RHO_AIR = 1.15
LV0, LV_SLOPE = 2.501e6, 2.361e3
X0_MONO = 0.10     # sorption activity parameter a_w = exp(-X0/C_s); the题目
                   # provides no isotherm, so this is a labelled scenario value


def p_sat(t_c):
    tt = np.asarray(t_c, dtype=float) + 273.15
    return np.exp(-5.8002206e3 / tt + 1.3914993 - 4.8640239e-2 * tt
                  + 4.1764768e-5 * tt ** 2 - 1.4452093e-8 * tt ** 3
                  + 6.5459673 * np.log(tt))


def y_sat(t_c):
    ps = p_sat(t_c)
    return 0.621945 * ps / (P_ATM - ps)


def props(t, c):
    """Appendix-3 properties. t in Celsius; last exponential is Arrhenius in K."""
    rho = 650.0 + 128.0 * c
    cp = 1450.0 + 2736.0 * c / (1.0 + c)
    k = 0.21 + 0.38 * c / (1.0 + c)
    d = 2.4e-3 * np.exp(-0.45 / c - 3850.0 / (t + 273.15))
    return rho * cp, k, d


def make_mesh(n, p=1.0):
    """faces from s_j = 1-(1-j/n)^p; p=1 gives a strictly uniform mesh."""
    s = 1.0 - (1.0 - np.linspace(0.0, 1.0, n + 1)) ** p
    faces = R * s
    x = 0.5 * (faces[1:] + faces[:-1])
    v = 0.5 * (faces[1:] ** 2 - faces[:-1] ** 2)      # omits common 2*pi*L
    xf = 0.5 * (x[:-1] + x[1:])
    dm = x[1:] - x[:-1]
    np.testing.assert_allclose(faces[0], 0.0, atol=0)
    np.testing.assert_allclose(faces[-1], R, atol=0)
    assert np.all(v > 0)
    return x, v, xf, dm, R - x[-1]


def sparse_pattern(n):
    """Tridiagonal block coupling: cell i talks to i-1, i, i+1 only."""
    from scipy.sparse import lil_matrix
    a = lil_matrix((2 * n, 2 * n), dtype=int)
    for i in range(n):
        a[2 * i:2 * i + 2, 2 * max(0, i - 1):2 * min(n, i + 2)] = 1
    return a.tocsr()


def solve(n=100, p=1.0, end=10800, rtol=1e-10, atol_t=1e-12, atol_c=1e-14,
          method="Radau", h=25.0, hm=8e-7, block=1800, save_every=1800,
          use_sparsity=False, physics="review"):
    """physics='review'  : A2-gpt closure, j = h_m (C_s - C_a), no latent heat
       physics='psychro' : j = h_m rho_a (Y_sat(T_s) - Y_a), no latent heat
       physics='latent'  : psychro + L_v(T_s) j_R in the surface energy balance
    """
    env = np.loadtxt(A2 / "data/ambient.csv", delimiter=",", skiprows=1)
    if end > env[-1, 0]:
        raise ValueError("no ambient extrapolation allowed")
    x, v, xf, dm, half = make_mesh(n, p)
    nvar = 2 * n
    y0 = np.empty(nvar)
    y0[0::2] = 28.0
    y0[1::2] = 2.55

    def surface(tl, cl, ta, ca, kl, dl):
        """Half-cell closure; returns (Ts, Cs, j_out, q_out), positive outward.

        Fluxes are returned as FLUX DENSITIES [kg/(m2 s)] and [W/m2]; the caller
        applies the geometric factor R (total flux per unit length = 2*pi*R*j).
        """
        if physics == "review":
            cs = (dl * cl + hm * half * ca) / (dl + hm * half)
            j = hm * (cs - ca)
            ts = (kl * tl + h * half * ta) / (kl + h * half)
            return ts, cs, j, h * (ts - ta)
        # corrected closures: driving force is the vapour-pressure / humidity-ratio
        # deficit; the solid side enters through the sorption activity
        # a_w = exp(-X0/C_s) (scenario parameter - the题目 gives no isotherm).
        aw = min(np.exp(-X0_MONO / max(cl, 1e-9)), 1.0)
        f = 1.0 + h * half / kl
        ts = tl - (tl - ta) / f
        for _ in range(200):
            lv = LV0 - LV_SLOPE * ts
            j = hm * RHO_AIR * (aw * float(y_sat(ts)) - ca)
            ts_new = tl - (tl - ta) / f - ((half * lv * j / kl) / f
                                           if physics == "latent" else 0.0)
            if abs(ts_new - ts) < 1e-14:
                ts = ts_new
                break
            ts = 0.5 * (ts + ts_new)
        lv = LV0 - LV_SLOPE * ts
        j = hm * RHO_AIR * (aw * float(y_sat(ts)) - ca)
        q = h * (ts - ta) + (lv * j if physics == "latent" else 0.0)
        # solid-side surface value from the internal gradient of the cell state
        cs = cl - (half * j * (R / (R - 0.5 * half))) / dl
        return ts, cs, j, q

    def fun(t, y):
        t_, c_ = y[0::2], y[1::2]
        n_ = t_.size
        cap, k, d = props(t_, c_)
        ta = np.interp(t, env[:, 0], env[:, 1])
        ca = np.interp(t, env[:, 0], env[:, 2])
        kf = np.empty(n_ - 1); df = np.empty(n_ - 1)
        tf = 0.5 * (t_[:-1] + t_[1:]); cf = 0.5 * (c_[:-1] + c_[1:])
        _, kf[:], df[:] = props(tf, cf)
        g = xf / dm
        flux_t = g * kf * (t_[:-1] - t_[1:])          # positive = outward
        flux_c = g * df * (c_[:-1] - c_[1:])
        _, _, j_s, q_s = surface(t_[-1], c_[-1], ta, ca, k[-1], d[-1])
        flux_t_s = R * q_s
        flux_c_s = R * j_s
        Ti = np.concatenate(([0.0], flux_t))
        To = np.concatenate((flux_t, [flux_t_s]))
        Ci = np.concatenate(([0.0], flux_c))
        Co = np.concatenate((flux_c, [flux_c_s]))
        # V_i * cap_i * dT_i/dt = F^T_i  and  V_i * dC_i/dt = F^C_i
        out = np.empty(nvar)
        out[0::2] = (Ti - To) / (v * cap)
        out[1::2] = (Ci - Co) / v
        return out

    sp = sparse_pattern(n) if use_sparsity else None
    t0 = time.perf_counter()
    y = y0.copy()
    snaps = {0: y.copy()}
    nst = nje = nlu = 0
    t = 0
    audit = []
    while t < end:
        t1 = min(t + block, end)
        sol = solve_ivp(fun, (t, t1), y, method=method, rtol=rtol,
                        atol=np.concatenate([[atol_t], [atol_c]] * n),
                        jac_sparsity=sp, dense_output=True, max_step=20.0)
        if not sol.success:
            raise RuntimeError(sol.message)
        nst += len(sol.t) - 1; nje += getattr(sol, "njev", 0); nlu += getattr(sol, "nlu", 0)
        # audit the surface fluxes along the accepted trajectory
        mids = 0.5 * (sol.t[1:] + sol.t[:-1]); wid = 0.5 * (sol.t[1:] - sol.t[:-1])
        for z, w in ((-0.7745966692414834, 5 / 9), (0.0, 8 / 9), (0.7745966692414834, 5 / 9)):
            tq = mids + z * wid
            yq = sol.sol(tq)
            for jq in range(len(tq)):
                tq_ = yq[0::2, jq]; cq_ = yq[1::2, jq]
                _, kq, dq = props(tq_, cq_)
                taq = np.interp(tq[jq], env[:, 0], env[:, 1])
                caq = np.interp(tq[jq], env[:, 0], env[:, 2])
                _, _, jj, qq = surface(tq_[-1], cq_[-1], taq, caq, kq[-1], dq[-1])
                audit.append((tq[jq], qq, jj, taq))
        for tt in range(int(t) + 1, int(t1) + 1):
            if tt % save_every == 0:
                snaps[tt] = sol.sol(tt).copy()
        y = sol.y[:, -1]; t = t1
    if end not in snaps:
        snaps[end] = y.copy()
    wall = time.perf_counter() - t0
    aud = np.array(audit) if audit else np.zeros((0, 4))
    return dict(x=x, v=v, half=half, snaps=snaps, n=n, p=p, end=end, rtol=rtol,
                method=method, steps=nst, njev=nje, nlu=nlu, seconds=wall,
                sparsity=use_sparsity, physics=physics,
                mass_check=float(np.min(y[1::2])),
                audit=aud)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--p", type=float, default=1.0)
    ap.add_argument("--end", type=int, default=10800)
    ap.add_argument("--rtol", type=float, default=1e-10)
    ap.add_argument("--method", default="Radau")
    ap.add_argument("--name", default="indep")
    ap.add_argument("--sparsity", type=int, default=0)
    ap.add_argument("--physics", default="review",
                    choices=("review", "psychro", "latent"))
    a = ap.parse_args()
    z = solve(n=a.n, p=a.p, end=a.end, rtol=a.rtol, method=a.method,
              use_sparsity=bool(a.sparsity), physics=a.physics)
    out = ROOT / "verification" / f"{a.name}_{a.physics}_n{a.n}_p{a.p}.npz"
    np.savez_compressed(out, x=z["x"], v=z["v"], half=z["half"], audit=z["audit"],
                        meta=json.dumps({k: z[k] for k in
                                         ("n", "p", "end", "rtol", "method",
                                          "steps", "njev", "nlu", "seconds",
                                          "sparsity", "physics", "mass_check")}),
                        **{f"y{t}": y for t, y in z["snaps"].items()})
    print("saved", out.name, "sec", round(z["seconds"], 2),
          "steps", z["steps"], "minC", z["mass_check"])
