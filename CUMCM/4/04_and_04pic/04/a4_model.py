# -*- coding: utf-8 -*-
"""Q4 deep model: moving-boundary (xi = r/R(t)) axisymmetric radial drying.

Follows the audited A3-codex architecture (graded mesh, 3-pt Gauss face
coefficients, coupled surface fixed point, BDF tight tolerances), extended to
the shrinking cylinder. 附录4 properties; 附件2 radius curve; appx=3 mode
reproduces Q3 (fixed R, 附录3) for cross-checking on the same code path.

    rho cp dT/dt = (1/(R^2 xi)) d/dxi ( xi k dT/dxi )   [+ latent heat, optional]
    dC/dt        = (1/(R^2 xi)) d/dxi ( xi D dC/dxi ),   xi in [0,1]

Affine shrinkage: material points fixed at their xi -> no advective term.
Drying threshold: inf{t : max_r C(r,t) < 0.15}; root has equality.
"""
import numpy as np
from numba import njit
import pandas as pd

import os
DATA_DIR = os.environ.get('A4_DATA_DIR', r'D:\CUMCM\A\data')
ALT_DIR = r'D:\Escherichia30636\CUMCM\CUMCM2026Problems\A题\附件'
R0 = 0.02          # m
T0 = 28.0          # degC
C0 = 2.55          # kg/kg
HCONV = 25.0       # W/(m^2 K)
HM = 8.0e-7        # m/s
CTARGET = 0.15
LV_STD = 2.383e6   # J/kg, 50 degC steam table

CH_T, CH_TC, CH_CC = None, None, None   # chamber: t, T(degC), C(kg/kg)
RD_T, RD_R = None, None                 # radius: t(s), R(m)


def _pick(base, alt):
    return base if os.path.exists(base) else alt


def load_data():
    global CH_T, CH_TC, CH_CC, RD_T, RD_R
    a = pd.read_excel(_pick(rf'{DATA_DIR}\attach1_chamber_temp_moisture.xlsx',
                            rf'{ALT_DIR}\附件1.xlsx'), header=0)
    CH_T = a.iloc[:, 0].to_numpy(float)
    CH_TC = a.iloc[:, 1].to_numpy(float)
    CH_CC = a.iloc[:, 2].to_numpy(float)
    b = pd.read_excel(_pick(rf'{DATA_DIR}\attach2_radius_vs_time.xlsx',
                            rf'{ALT_DIR}\附件2.xlsx'), header=0)
    RD_T = b.iloc[:, 0].to_numpy(float)
    RD_R = b.iloc[:, 1].to_numpy(float) * 1e-2


load_data()

# --------------------------------------------------------------------------
# property kernels (appx=4: 附录4; appx=3: 附录3)
# --------------------------------------------------------------------------
@njit(cache=True)
def properties(t, c, df=1.0, appx=4):
    """Returns cap, k, D, capprime."""
    if appx == 4:
        rho = 760. + 90. * c
        cp = 1850. + 2150. * c / (1. + c)
        capprime = 90. * cp + rho * 2150. / (1. + c) ** 2
        k = .12 + .20 * c / (1. + c)
        d = df * 4.2e-4 * np.exp(-.30 / c - 3850. / (t + 273.15))
    else:
        rho = 650. + 128. * c
        cp = 1450. + 2736. * c / (1. + c)
        capprime = 128. * cp + rho * 2736. / (1. + c) ** 2
        k = .21 + .38 * c / (1. + c)
        d = df * 2.4e-3 * np.exp(-.45 / c - 3850. / (t + 273.15))
    return rho * cp, k, d, capprime


@njit(cache=True)
def face(t1, c1, t2, c2, df=1.0, appx=4):
    """3-pt Gauss average of k, D along the linear (T,C) path."""
    k, d = 0., 0.
    for z, w in ((.1127016653792583, 5. / 18), (.5, 4. / 9), (.8872983346207417, 5. / 18)):
        _, ki, di, _ = properties(t1 + z * (t2 - t1), c1 + z * (c2 - c1), df, appx)
        k += w * ki
        d += w * di
    return k, d


@njit(cache=True)
def boundary(t, c, ta, ca, half, R, h, hm, df, lmode, rhoc, lv, appx=4):
    """Coupled surface fixed point; returns (ts, cs, jT, jC).
    lmode==2 (surf latent): k(t-ts)/half = R*[ h(ts-ta) + Lv*rhoc*hm(cs-ca) ],
    jT returned is the TOTAL surface heat flux density (convection + latent)."""
    ts, cs = t, c
    for it in range(60):
        k, d = face(t, c, ts, cs, df, appx)
        cn = (d * c + hm * R * half * ca) / (d + hm * R * half)
        if lmode == 2:
            tn = (k * t + R * h * half * ta - R * half * lv * rhoc * hm * (cn - ca)) / (k + R * h * half)
        else:
            tn = (k * t + R * h * half * ta) / (k + R * h * half)
        err = max(abs(tn - ts), abs(cn - cs))
        ts, cs = tn, cn
        if err < 2e-13:
            jT = h * (ts - ta)
            if lmode == 2:
                jT = jT + lv * rhoc * hm * (cs - ca)
            return ts, cs, jT, hm * (cs - ca)
    raise ValueError('surface iteration failed')


@njit(cache=True)
def kernel(y, x, v, g, half, ta, ca, R, h, hm, df, lmode, rhoc0, lv, appx=4):
    """RHS of the moving-boundary FV ODE. y interleaved [T0,C0,T1,C1,...].
    rhoc0>0: latent conversion density rho_c(t)=rhoc0*(R0/R)^2 (dry matter
    conservation under shrinkage). Returns (dy, qt_out, qc_out, correction)."""
    n = len(x)
    out = np.empty(2 * n)
    qt, qc = 0., 0.
    correction = 0.
    rhoc = rhoc0 * (R0 / R) ** 2 if rhoc0 > 0. else 0.
    R2 = R * R
    for i in range(n):
        ti, ci = y[2 * i], y[2 * i + 1]
        cap, _, _, ap = properties(ti, ci, df, appx)
        if i < n - 1:
            k, d = face(ti, ci, y[2 * i + 2], y[2 * i + 3], df, appx)
            nt_ = g[i] * k * (ti - y[2 * i + 2])
            nc_ = g[i] * d * (ci - y[2 * i + 3])
        else:
            if lmode == 2:
                _, _, jt, jc = boundary(ti, ci, ta, ca, half, R, h, hm, df, 2, rhoc, lv, appx)
            else:
                _, _, jt, jc = boundary(ti, ci, ta, ca, half, R, h, hm, df, 0, 0., 0., appx)
            nt_ = R * jt
            nc_ = R * jc
        out[2 * i] = (qt - nt_) / (v[i] * cap * R2)
        out[2 * i + 1] = (qc - nc_) / (v[i] * R2)
        if lmode == 1:
            # vol latent: rho cp dT/dt = ... + Lv*rho_c*dC/dt  (dC/dt<0 -> cooling)
            out[2 * i] = out[2 * i] + lv * rhoc * out[2 * i + 1] / cap
        correction += v[i] * ap * ti * out[2 * i + 1]
        qt, qc = nt_, nc_
    return out, qt, qc, correction


def mesh(n, kind='graded'):
    """Faces/cells/volumes in xi. graded: xi_f = 1-(1-j/N)^2 (dense at surface)."""
    if kind == 'graded':
        faces = 1. - (1. - np.linspace(0, 1, n + 1)) ** 2
    else:
        faces = np.linspace(0, 1, n + 1)
    x = (faces[1:] + faces[:-1]) / 2
    v = (faces[1:] ** 2 - faces[:-1] ** 2) / 2
    g = faces[1:-1] / np.diff(x)
    return x, v, g, 1. - x[-1]


def sparsity(n):
    from scipy.sparse import lil_matrix
    a = lil_matrix((2 * n, 2 * n), dtype=int)
    for i in range(n):
        a[2 * i:2 * i + 2, 2 * max(0, i - 1):2 * min(n, i + 2)] = 1
    return a.tocsr()


@njit(cache=True)
def sample_many(ys, x, half, airs, Rs, qs, h, hm, df, appx=4,
                lmode=0, rhocs=None, lv=0.):
    """Reconstruct at query xi qs[it, j] (m, nq): center via xi^2 quadratic,
    interior via 3-pt quadratic, surface (xi=1) via boundary solve."""
    m = ys.shape[1]
    nq = qs.shape[1]
    out = np.empty((m, nq, 2))
    for it in range(m):
        for field in range(2):
            a = ys[field::2, it]
            out[it, 0, field] = (x[1] ** 2 * a[0] - x[0] ** 2 * a[1]) / (x[1] ** 2 - x[0] ** 2)
            for j in range(1, nq - 1):
                z = qs[it, j]
                i = min(max(np.searchsorted(x, z) - 1, 1), len(x) - 2)
                aa, b, c = x[i - 1], x[i], x[i + 1]
                out[it, j, field] = ((z - b) * (z - c) / ((aa - b) * (aa - c)) * a[i - 1]
                                     + (z - aa) * (z - c) / ((b - aa) * (b - c)) * a[i]
                                     + (z - aa) * (z - b) / ((c - aa) * (c - b)) * a[i + 1])
        rhoc = 0. if rhocs is None else rhocs[it]
        ts, cs, _, _ = boundary(ys[-2, it], ys[-1, it], airs[it, 0], airs[it, 1],
                                half, Rs[it], h, hm, df, lmode, rhoc, lv, appx)
        out[it, nq - 1, 0] = ts
        out[it, nq - 1, 1] = cs
    return out


def queries_for(dist_cm, Rs):
    """Query xi per time: fixed physical distances d (cm) -> xi = d/100/R(t)."""
    out = np.zeros((len(Rs), len(dist_cm) + 1))
    for j, d in enumerate(dist_cm):
        out[:, j] = np.minimum(d / 100.0 / Rs, 1.0 - 1e-12)
    out[:, -1] = 1.0
    return out
