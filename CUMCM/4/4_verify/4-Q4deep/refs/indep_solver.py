# -*- coding: utf-8 -*-
"""INDEPENDENT re-derivation of CUMCM2026 A-Q3 drying time.

Deliberately uses DIFFERENT numerics from all three candidates:
  Method B : cell-centered FV, method-of-lines, scipy Radau (implicit RK, adaptive)
  Method C : node-centered FD on [0,R] with ghost node at r=-dr and Robin at r=R,
             Crank-Nicolson-free: fully implicit BDF2 with adaptive step.
  Method D : 2D axisymmetric (r,z) FV, to quantify the axial-end effect.

Physics (附录3), cylinder R=2cm, L=25cm, T0=28C, C0=2.55, h=25 W/m2K, hm=8e-7 m/s.
rho=650+128C, cp=1450+2736C/(C+1), k=0.21+0.38C/(C+1),
D = 2.4e-3 exp(-0.45/C) exp(-3850/T)  [m^2/s], T in K.
Chamber from 附件1 (t=0..14400 s, dt=60 s), HELD at final value beyond.
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import diags, csr_matrix
import pandas as pd

CHAMBER = r'D:\CUMCM\A\data\attach1_chamber_temp_moisture.xlsx'
R0 = 0.02
L0 = 0.25
T0 = 28.0
C0 = 2.55
HCONV = 25.0
HM = 8.0e-7
CTARGET = 0.15


def chamber_series():
    a = pd.read_excel(CHAMBER, header=0)
    t = a.iloc[:, 0].to_numpy(float)
    T = a.iloc[:, 1].to_numpy(float) + 273.15
    C = a.iloc[:, 2].to_numpy(float)
    return t, T, C


CH_T, CH_TT, CH_CC = chamber_series()


def chamber(t):
    """hold final value beyond last sample"""
    return float(np.interp(t, CH_T, CH_TT)), float(np.interp(t, CH_T, CH_CC))


def props(C):
    Cc = np.clip(C, 1e-12, None)
    rho = 650.0 + 128.0 * Cc
    cp = 1450.0 + 2736.0 * Cc / (Cc + 1.0)
    k = 0.21 + 0.38 * Cc / (Cc + 1.0)
    return rho, cp, k


def Dfun(C, T):
    Cc = np.clip(C, 1e-9, None)
    return 2.4e-3 * np.exp(-0.45 / Cc) * np.exp(-3850.0 / np.asarray(T, float))


def harm(a, b):
    return 2.0 * a * b / (a + b)


# ----------------------------------------------------------------------------
# Method B: cell-centered FV in r (not xi), cylindrical, MOL + Radau
# ----------------------------------------------------------------------------
class FV:
    def __init__(self, N):
        self.N = N
        self.dr = R0 / N
        # face radii: 0, dr, ..., R
        self.rf = np.arange(N + 1) * self.dr
        # cell centers
        self.rc = (np.arange(N) + 0.5) * self.dr

    def rhs(self, t, y):
        N, dr, rf, rc = self.N, self.dr, self.rf, self.rc
        T = y[0::2]
        C = y[1::2]
        rho, cp, k = props(C)
        D = Dfun(C, T)
        Ta, Ca = chamber(t)

        # internal faces f=1..N-1 : conductance = r_f * <k> / dr
        Gt = rf[1:N] * harm(k[:-1], k[1:]) / dr
        Gm = rf[1:N] * harm(D[:-1], D[1:]) / dr
        # surface face f=N: series of half-cell conduction + convection.
        # 1/G = (R - rc)/(k R) + 1/(h R)   [in "reduced flux" units Phi = r*J]
        Ht_s = 1.0 / ((R0 - rc[-1]) / (k[-1] * R0) + 1.0 / (HCONV * R0))
        Hm_s = 1.0 / ((R0 - rc[-1]) / (D[-1] * R0) + 1.0 / (HM * R0))

        PT = np.empty(N + 1)
        PC = np.empty(N + 1)
        PT[0] = 0.0
        PC[0] = 0.0
        PT[1:N] = Gt * (T[:-1] - T[1:])
        PC[1:N] = Gm * (C[:-1] - C[1:])
        PT[N] = Ht_s * (T[-1] - Ta)
        PC[N] = Hm_s * (C[-1] - Ca)

        vol = rc * dr  # (r dr) per unit 2*pi*H
        dT = (PT[:-1] - PT[1:]) / (rho * cp * vol)
        dC = (PC[:-1] - PC[1:]) / vol
        out = np.empty(2 * N)
        out[0::2] = dT
        out[1::2] = dC
        return out

    def jac(self):
        n = 2 * self.N
        offs = (-3, -2, -1, 0, 1, 2, 3)
        return diags([np.ones(n - abs(o)) for o in offs], list(offs),
                     shape=(n, n), format='csr')

    def y0(self):
        y = np.empty(2 * self.N)
        y[0::2] = T0 + 273.15
        y[1::2] = C0
        return y

    def centerC_event(self, t, y):
        return y[1] - CTARGET

    centerC_event.terminal = True
    centerC_event.direction = -1

    def solve(self, t_end=300000.0, method='Radau', rtol=1e-9, atol=1e-11):
        return solve_ivp(self.rhs, (0.0, t_end), self.y0(), method=method,
                         rtol=rtol, atol=atol, events=self.centerC_event,
                         jac_sparsity=self.jac())


# ----------------------------------------------------------------------------
# Method C: node-centered FD including r=0 and r=R, ghost node, implicit
# ----------------------------------------------------------------------------
class FD:
    """nodes r_i = i*dr, i=0..N ; ghost r_{-1} = -dr (symmetry), Robin at r_N."""
    def __init__(self, N):
        self.N = N
        self.dr = R0 / N
        self.r = np.arange(N + 1) * self.dr

    def rhs(self, t, y):
        N, dr, r = self.N, self.dr, self.r
        T = y[0::2]
        C = y[1::2]
        rho, cp, k = props(C)
        D = Dfun(C, T)
        Ta, Ca = chamber(t)

        # --- second-order cylindrical Laplacian, node-centered ---
        # 1/r d/dr(r k dT/dr)  at interior i:
        #   [ r_{i+1/2} k_{i+1/2} (T_{i+1}-T_i) - r_{i-1/2} k_{i-1/2}(T_i-T_{i-1}) ] / (r_i dr^2)
        rh = (np.arange(N) + 0.5) * dr          # faces r_{1/2}, r_{3/2}, ..., r_{N-1/2} (N of them)
        kf = harm(k[:-1], k[1:])
        Df = harm(D[:-1], D[1:])
        # interior i=1..N-1
        numT = np.zeros(N + 1)
        numC = np.zeros(N + 1)
        numT[1:N] = rh[1:N] * kf[1:N] * (T[2:] - T[1:-1]) - rh[:N - 1] * kf[:N - 1] * (T[1:-1] - T[:-2])
        numC[1:N] = rh[1:N] * Df[1:N] * (C[2:] - C[1:-1]) - rh[:N - 1] * Df[:N - 1] * (C[1:-1] - C[:-2])
        lapT = numT / (r * dr * dr)
        lapC = numC / (r * dr * dr)

        # --- r=0 symmetry: L'Hopital -> 2 * d2u/dr2  (limit of (1/r)d/dr(r du/dr))
        lapT[0] = 4.0 * (T[1] - T[0]) / (dr * dr)
        lapC[0] = 4.0 * (C[1] - C[0]) / (dr * dr)

        # --- r=R Robin: ghost node i=N+1 ---
        # (T_{N+1} - T_{N-1})/(2dr) = -h/k (T_N - Ta)
        # d2T/dr2 at N = (T_{N-1} - 2 T_N + T_{N+1})/dr^2
        GtR = -2.0 * dr * HCONV / k[-1]
        GcR = -2.0 * dr * HM / D[-1]
        Tgh = T[-2] + GtR * (T[-1] - Ta)
        Cgh = C[-2] + GcR * (C[-1] - Ca)
        lapT[-1] = (T[-2] - 2.0 * T[-1] + Tgh) / (dr * dr) + (Tgh - T[-2]) / (2.0 * R0 * dr)
        lapC[-1] = (C[-2] - 2.0 * C[-1] + Cgh) / (dr * dr) + (Cgh - C[-2]) / (2.0 * R0 * dr)

        dT = lapT * k / (rho * cp)
        dC = lapC * D
        out = np.empty(2 * (N + 1))
        out[0::2] = dT
        out[1::2] = dC
        return out

    def jac(self):
        n = 2 * (self.N + 1)
        offs = (-3, -2, -1, 0, 1, 2, 3)
        return diags([np.ones(n - abs(o)) for o in offs], list(offs),
                     shape=(n, n), format='csr')

    def y0(self):
        y = np.empty(2 * (self.N + 1))
        y[0::2] = T0 + 273.15
        y[1::2] = C0
        return y

    def centerC_event(self, t, y):
        return y[1] - CTARGET
    centerC_event.terminal = True
    centerC_event.direction = -1

    def solve(self, t_end=300000.0, method='Radau', rtol=1e-9, atol=1e-11):
        return solve_ivp(self.rhs, (0.0, t_end), self.y0(), method=method,
                         rtol=rtol, atol=atol, events=self.centerC_event,
                         jac_sparsity=self.jac())


if __name__ == '__main__':
    print('chamber samples:', len(CH_T), 't_end=', CH_T[-1],
          'T_end=', CH_TT[-1] - 273.15, 'C_end=', CH_CC[-1])
    print()
    print('--- Method B (cell-centered FV in r, Radau) ---')
    for N in (200, 400, 800, 1600):
        m = FV(N)
        s = m.solve()
        tstar = s.t_events[0][0]
        print(f'  N={N:5d}  t* = {tstar:12.3f} s = {tstar/3600:9.5f} h = {tstar/86400:.6f} d')
    print()
    print('--- Method C (node-centered FD + ghost node, Radau) ---')
    for N in (200, 400, 800, 1600):
        m = FD(N)
        s = m.solve()
        tstar = s.t_events[0][0]
        print(f'  N={N:5d}  t* = {tstar:12.3f} s = {tstar/3600:9.5f} h = {tstar/86400:.6f} d')
