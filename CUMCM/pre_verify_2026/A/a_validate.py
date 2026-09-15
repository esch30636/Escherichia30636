# -*- coding: utf-8 -*-
"""A 题模型正确性验证
  1) 离散格式对照: xi 形式 vs 物理坐标 r 形式 (同网格, 逐单元中心比较)
  2) 表面值的精确重构 (用边界条件) vs 线性外推 —— 收敛性
  3) 守恒律残差 (精细采样)
  4) 网格收敛性 + 求解耗时
"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import diags
import a_model as M

R0, H, HC, HM = M.R0, M.H_CYL, M.H_CONV, M.HM
GRID_CM = np.arange(0.0, 2.0 + 1e-9, 0.1)
COLS = [0, 5, 10, 15, 20]          # 0, 0.5, 1, 1.5, 2 cm


# ==========================================================================
# 参考实现: 物理坐标 r (独立编写)
# ==========================================================================
class RefPhysical:
    def __init__(self, N=200, problem=1):
        self.N = N
        self.dr = R0 / N
        self.rf = np.arange(N + 1) * self.dr
        self.rc = (np.arange(N) + 0.5) * self.dr
        self.V = np.pi * (self.rf[1:] ** 2 - self.rf[:-1] ** 2) * H
        self.A = 2 * np.pi * self.rf * H
        self.A[0] = 0.0
        self.t_ch, self.T_ch, self.C_ch = M.load_chamber()
        self.props = {1: M.props_p1, 2: M.props_p3, 3: M.props_p3, 4: M.props_p4}[problem]
        self.Dfun = {1: M.D_p1, 2: M.D_p3, 3: M.D_p3, 4: M.D_p4}[problem]

    def rhs(self, t, y):
        N, dr = self.N, self.dr
        T, C = y[0::2], y[1::2]
        rho, cp, k = self.props(C)
        D = self.Dfun(C, T)
        Ta = float(np.interp(t, self.t_ch, self.T_ch))
        Ca = float(np.interp(t, self.t_ch, self.C_ch))
        Te = np.concatenate([[T[0]], T, [Ta]])
        Ce = np.concatenate([[C[0]], C, [Ca]])
        Gt = np.zeros(N + 1); Gm = np.zeros(N + 1)
        Gt[1:N] = M.harm(k[:-1], k[1:]) * self.A[1:N] / dr
        Gm[1:N] = M.harm(D[:-1], D[1:]) * self.A[1:N] / dr
        Gt[N] = self.A[N] / (dr / (2 * k[-1]) + 1 / HC)
        Gm[N] = self.A[N] / (dr / (2 * D[-1]) + 1 / HM)
        fT = Gt * (Te[:-1] - Te[1:])
        fC = Gm * (Ce[:-1] - Ce[1:])
        dT = (fT[:-1] - fT[1:]) / (rho * cp * self.V)
        dC = (fC[:-1] - fC[1:]) / self.V
        out = np.empty(2 * N); out[0::2] = dT; out[1::2] = dC
        return out

    def solve(self, t_end, rtol=1e-9, atol=1e-11):
        y0 = np.empty(2 * self.N); y0[0::2] = M.T_INIT + 273.15; y0[1::2] = M.C_INIT
        n = 2 * self.N
        offs = (-3, -2, -1, 0, 1, 2, 3)
        sp = diags([np.ones(n - abs(o)) for o in offs], list(offs),
                   shape=(n, n), format='csr')
        return solve_ivp(self.rhs, (0, t_end), y0, method='BDF', rtol=rtol,
                         atol=atol, jac_sparsity=sp, dense_output=True)


# ==========================================================================
print('=' * 86)
print('1) 离散格式对照 (问题1, N=200, 逐单元中心)')
print('=' * 86)
tq = np.array([100., 300., 600., 900., 1200., 1500., 1800.])

mdl = M.DryingModel(1, N=200)
t0 = time.time(); s_xi = mdl.solve(1800.0, t_eval=tq); e1 = time.time() - t0
ref = RefPhysical(N=200, problem=1)
t0 = time.time(); s_rf = ref.solve(1800.0); e2 = time.time() - t0

dmaxT = dmaxC = 0.0
for k, tk in enumerate(tq):
    a = s_xi.y[:, k]; b = s_rf.sol(tk)
    dmaxT = max(dmaxT, np.abs(a[0::2] - b[0::2]).max())
    dmaxC = max(dmaxC, np.abs(a[1::2] - b[1::2]).max())
print(f'  xi 形式内部步数 {s_xi.t.size} / 物理形式内部步数 {s_rf.t.size}')
print(f'  (耗时 {e1:.2f}s vs {e2:.2f}s)')
print(f'  逐单元中心最大偏差:  |dT| = {dmaxT:.3e} K    |dC| = {dmaxC:.3e} kg/kg')
print(f'  -> 两者为同一方程的等价离散' if dmaxT < 1e-3 else '  -> 不一致, 需排查!')

# --------------------------------------------------------------------------
print()
print('=' * 86)
print('2) 表面值重构: 边界条件反解 vs 线性外推')
print('=' * 86)
print('  边界条件给出精确关系:  Phi_N = h*R*(T_air - T_s)  ->  T_s = T_air - Phi_N/(h R)')
print('                        Phi_N = hm*R*(C_air - C_s) ->  C_s = C_air - Phi_N/(hm R)')
print()
print(f'  {"N":>5} {"T_s(外推)":>13} {"T_s(BC)":>13} {"C_s(外推)":>13} {"C_s(BC)":>13}')
prev = None
for N in (50, 100, 200, 400, 800):
    m = M.DryingModel(1, N=N)
    s = m.solve(1800.0, t_eval=[1800.0])
    Tq, Cq = m.interp_xi(s.y[:, -1], [1.0])
    T_s_bc, C_s_bc = m.surface_value(s.y[:, -1], 1800.0)
    print(f'  {N:>5} {Tq[0]-273.15:>13.6f} {T_s_bc-273.15:>13.6f} '
          f'{Cq[0]:>13.6f} {C_s_bc:>13.6f}')
    prev = (Tq[0], T_s_bc)

# --------------------------------------------------------------------------
print()
print('=' * 86)
print('3) 守恒律残差 (问题1, 对流项用 dense_output 精细积分)')
print('=' * 86)
N = 400
m = M.DryingModel(1, N=N)
s = m.solve(1800.0)
tt = s.t
dr = R0 / N
rf = np.arange(N + 1) * dr
rc = (np.arange(N) + .5) * dr
V = np.pi * (rf[1:] ** 2 - rf[:-1] ** 2) * H
A_s = 2 * np.pi * R0 * H

# 细采样
tf = np.linspace(0, 1800.0, 20001)
Y = s.sol(tf)
Ts = Y[-2, :]; Cs = Y[-1, :]
Ta_f = np.interp(tf, m.t_ch, m.T_ch)
Ca_f = np.interp(tf, m.t_ch, m.C_ch)
Econv = np.trapezoid(HC * A_s * (Ta_f - Ts), tf)
Mflux = np.trapezoid(HM * A_s * (Ca_f - Cs), tf)

rho0, cp0, _ = M.props_p1(Y[1::2, 0])
rho1, cp1, _ = M.props_p1(Y[1::2, -1])
E0 = np.sum(rho0 * cp0 * Y[0::2, 0] * V)
E1 = np.sum(rho1 * cp1 * Y[0::2, -1] * V)
M0 = np.sum(Y[1::2, 0] * V)
M1 = np.sum(Y[1::2, -1] * V)

print(f'  能量: dE={E1-E0:+.6e}  J   对流输入={Econv:+.6e} J   '
      f'残差={E1-E0-Econv:+.3e} (相对 {abs(E1-E0-Econv)/abs(Econv):.2e})')
print(f'  水分: dM={M1-M0:+.6e}      表面传质={Mflux:+.6e}     '
      f'残差={M1-M0-Mflux:+.3e} (相对 {abs(M1-M0-Mflux)/abs(Mflux):.2e})')

# --------------------------------------------------------------------------
print()
print('=' * 86)
print('4) 网格收敛性 (问题1, t=1800 s)')
print('=' * 86)
print(f'  {"N":>5} {"步数":>6} {"t(s)":>7} {"C(0)":>12} {"C(R)":>12} {"T(0)":>12} {"T(R)":>12}')
prev = None
for N in (50, 100, 200, 400, 800):
    m = M.DryingModel(1, N=N)
    t0 = time.time(); s = m.solve(1800.0); el = time.time() - t0
    T0, C0 = m.interp_xi(s.y[:, -1], [0.0])
    Tr, Cr = m.interp_xi(s.y[:, -1], [1.0])
    print(f'  {N:>5} {s.t.size:>6} {el:>7.2f} {C0[0]:>12.6f} {Cr[0]:>12.6f} '
          f'{T0[0]-273.15:>12.6f} {Tr[0]-273.15:>12.6f}')
    if prev is not None:
        print(f'        Δ:  dC0={C0[0]-prev[0]:+.2e}  dCR={Cr[0]-prev[1]:+.2e}  '
              f'dT0={T0[0]-prev[2]:+.2e}  dTR={Tr[0]-prev[3]:+.2e}')
    prev = (C0[0], Cr[0], T0[0], Tr[0])

print('\n验证结束')
