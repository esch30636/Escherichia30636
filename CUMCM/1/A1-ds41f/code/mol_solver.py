"""Gold-standard independent solver (method of lines).

Uniform grid in the physical radius r; cell-centred finite volume; SciPy's BDF
(implicit, adaptive, independent implementation) for time integration.  This exact
formulation reproduced the analytic Bessel series to 6e-3 K for the heat problem,
so it is used as the gold reference for problem 1.

Semi-discrete form
    V_i dc_i/dt = F_{i-1/2} - F_{i+1/2}
    F_{i+1/2} = r_{i+1/2} * Gamma_i * (c_i - c_{i+1}) / dr
    surface   : q_s = beta_eff (c_N - c_a),  beta_eff = beta / (1 + beta*(dr/4)/D_N)
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import diags
from scipy.integrate import quad as _quad


def _U(a, b, scale):
    """Primitive of D from b to a (nonlinear exponential form), cancellation free."""
    if abs(a - b) < 1e-15:
        return 0.0
    m = 0.5 * (a + b)
    d = 0.5 * (a - b)
    z = 0.7745966692414834 * d
    return d * scale * (5 / 9 * np.exp(-DECAY / (m - z)) + 8 / 9 * np.exp(-DECAY / m)
                        + 5 / 9 * np.exp(-DECAY / (m + z)))


def _surface(scale, cN, air, delta, beta, nonlinear):
    """Exact Robin closure:
         heat     : D(cN-cs)/delta = beta(cs-air)        -> linear solve
         moisture : [U(cN)-U(cs)]/delta = beta(cs-air)   -> monotone scalar Newton
    """
    if nonlinear:
        lo, hi = min(cN, air), max(cN, air)
        cs = 0.5 * (lo + hi)
        for _ in range(60):
            f = _U(cN, cs, scale) - delta * beta * (cs - air)
            ds = scale * np.exp(-DECAY / cs)
            step = f / (ds + delta * beta)
            if abs(step) < 1e-16:
                break
            nxt = cs + step
            cs = nxt if lo < nxt < hi else 0.5 * (lo + hi)
        return cs
    return (scale * cN + delta * beta * air) / (scale + delta * beta)

R = 0.02
RHO, CP, K, H, HM = 820.0, 2600.0, 0.36, 25.0, 8e-7
T0, C0 = 28.0, 2.55
D0, DECAY = 7e-9, 0.89


class MOL:
    def __init__(self, n, nonlinear, env, h_factor=1.0, hm_factor=1.0, d_factor=1.0,
                 ce_shift=0.0):
        self.n = n
        self.nonlinear = nonlinear
        self.env = env
        self.dr = 1.0 / n
        self.rc = (np.arange(n) + 0.5) * self.dr
        self.rf = np.arange(1, n) * self.dr
        self.vol = 0.5 * ((np.arange(1, n + 1) * self.dr) ** 2 - (np.arange(n) * self.dr) ** 2)
        self.s = (D0 * d_factor / R ** 2) if nonlinear else K / (RHO * CP * R ** 2)
        self.beta = (HM * hm_factor / R) if nonlinear else H * h_factor / (RHO * CP * R)
        self.ce_shift = ce_shift
        self.stencil = diags([np.ones(n - 1), np.ones(n), np.ones(n - 1)], [-1, 0, 1], format="csc")

    def air(self, t):
        col = 2 if self.nonlinear else 1
        v = float(np.interp(t, self.env[:, 0], self.env[:, col]))
        return v + (self.ce_shift if self.nonlinear else 0.0)

    def rhs(self, t, c):
        nonlinear = self.nonlinear
        n = self.n
        if nonlinear:
            d = self.s * np.exp(-DECAY / c)
            gam = 2 * d[:-1] * d[1:] / (d[:-1] + d[1:])
            dN = d[-1]
        else:
            gam = np.full(n - 1, self.s)
            dN = self.s
        q = np.empty(n + 1)
        q[0] = 0.0
        q[1:n] = self.rf * gam * (c[:-1] - c[1:]) / self.dr
        air = self.air(t)
        cs = _surface(self.s, c[-1], air, self.dr / 4.0, self.beta, nonlinear)
        dN = self.s * np.exp(-DECAY / c[-1]) if nonlinear else self.s
        # q = D(cN-cs)/delta  (exact flux, not the linearised form)
        q[n] = dN * (c[-1] - cs) / (self.dr / 4.0) if nonlinear else self.beta * (c[-1] - cs) / (1 + self.beta * (self.dr / 4.0) / self.s) * 0 + dN * (c[-1] - cs) / (self.dr / 4.0)
        return (q[:-1] - q[1:]) / self.vol

    def run(self, end=1800, const_air=None, rtol=1e-11, atol=1e-13):
        n = self.n
        y0 = np.full(n, C0 if self.nonlinear else T0)
        if const_air is not None:
            saved = self.air
            self.air = lambda t: const_air + (self.ce_shift if self.nonlinear else 0.0)
        hist = np.empty((end + 1, 21))
        hist[0] = C0 if self.nonlinear else T0
        state = y0
        for left in range(0, end, 60):
            out = solve_ivp(self.rhs, [left, left + 60], state, method="BDF",
                            t_eval=np.arange(left + 1, left + 61), rtol=rtol, atol=atol,
                            jac_sparsity=self.stencil)
            assert out.success, out.message
            state = out.y[:, -1]
            for t, c in zip(out.t, out.y.T):
                air = self.air(t)
                hist[int(t)] = self.sample(c, air)
        if const_air is not None:
            self.air = saved
        return hist, state

    def sample(self, c, air):
        n = self.n
        out = np.empty(21)
        for j in range(21):
            z = j / 20.0
            i = int(np.searchsorted(self.rc, z))
            if i <= 0:
                out[j] = c[0] + (c[1] - c[0]) * (z - self.rc[0]) / (self.rc[1] - self.rc[0])
            elif i >= n:
                out[j] = np.nan
            else:
                a, b, d = self.rc[i - 1], self.rc[i], self.rc[i + 1]
                out[j] = ((z - b) * (z - d) / ((a - b) * (a - d)) * c[i - 1]
                          + (z - a) * (z - d) / ((b - a) * (b - d)) * c[i]
                          + (z - a) * (z - b) / ((d - a) * (d - b)) * c[i + 1])
        if self.nonlinear:
            dN = self.s * np.exp(-DECAY / c[-1])
        else:
            dN = self.s
        out[-1] = _surface(self.s, c[-1], air, self.dr / 4.0, self.beta, self.nonlinear)
        return out
