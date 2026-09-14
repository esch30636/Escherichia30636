# -*- coding: utf-8 -*-
"""A 题:  (1) xi/物理 两种离散在紧容差下的一致性
         (2) 表面值收敛性 (BC 重构 vs 线性外推), 以 Richardson 外推为基准
         (3) 守恒律残差 (对流项用 BC 表面值)
         (4) 生产网格选型: N=800 全天积分耗时
"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import diags
import a_model as M
from a_ref import RefPhysical

R0, H, HC, HM = M.R0, M.H_CYL, M.H_CONV, M.HM

print('=' * 88)
print('1) xi 形式 vs 物理坐标形式  (问题1, 紧容差 rtol=1e-10 atol=1e-12, N=200)')
print('=' * 88)
tq = np.array([100., 300., 600., 900., 1200., 1500., 1800.])
m = M.DryingModel(1, N=200)
t0 = time.time(); s1 = m.solve(1800.0, t_eval=tq, rtol=1e-10, atol=1e-12); e1 = time.time()-t0
r = RefPhysical(N=200, problem=1)
t0 = time.time(); s2 = r.solve(1800.0, rtol=1e-10, atol=1e-12); e2 = time.time()-t0
dT = dC = 0.0
for k, tk in enumerate(tq):
    a, b = s1.y[:, k], s2.sol(tk)
    dT = max(dT, np.abs(a[0::2]-b[0::2]).max())
    dC = max(dC, np.abs(a[1::2]-b[1::2]).max())
print(f'  内部步数 {s1.t.size} vs {s2.t.size} ;  耗时 {e1:.2f}s vs {e2:.2f}s')
print(f'  逐单元中心最大偏差: |dT| = {dT:.3e} K   |dC| = {dC:.3e} kg/kg')
print(f'  => {"一致 (同一离散)" if dT < 1e-6 and dC < 1e-7 else "仍不一致"}')

print()
print('=' * 88)
print('2) 表面值收敛性  (问题1, t=1800 s)')
print('=' * 88)
Ns = [50, 100, 200, 400, 800, 1600]
res = {}
for N in Ns:
    mm = M.DryingModel(1, N=N)
    s = mm.solve(1800.0, t_eval=[1800.0], rtol=1e-9, atol=1e-11)
    y = s.y[:, -1]
    T_ex = mm.interp_xi(y, [1.0])[0][0]
    C_ex = mm.interp_xi(y, [1.0])[1][0]
    T_bc, C_bc = mm.surface_value(y, 1800.0)
    res[N] = (T_ex-273.15, C_ex, T_bc-273.15, C_bc)
    print(f'  N={N:>5}:  外推 T={T_ex-273.15:.6f} C={C_ex:.6f}   |   '
          f'BC T={T_bc-273.15:.6f} C={C_bc:.6f}')

# Richardson (2阶): u_inf = u_N + (u_N - u_{N/2})/3
print('\n  以 Richardson 外推 (N=1600 + (u1600-u800)/3) 为基准的相对误差:')
print(f'  {"N":>5} {"err T(外推)":>14} {"err T(BC)":>14} {"err C(外推)":>14} {"err C(BC)":>14}')
Tref_ex = res[1600][0] + (res[1600][0]-res[800][0])/3
Cref_ex = res[1600][1] + (res[1600][1]-res[800][1])/3
Tref_bc = res[1600][2] + (res[1600][2]-res[800][2])/3
Cref_bc = res[1600][3] + (res[1600][3]-res[800][3])/3
for N in Ns[:-1]:
    print(f'  {N:>5} {res[N][0]-Tref_ex:>14.2e} {res[N][2]-Tref_bc:>14.2e} '
          f'{res[N][1]-Cref_ex:>14.2e} {res[N][3]-Cref_bc:>14.2e}')

print()
print('=' * 88)
print('3) 守恒律残差  (问题1, N=400, 对流项用 BC 表面值)')
print('=' * 88)
N = 400
mm = M.DryingModel(1, N=N)
s = mm.solve(1800.0, rtol=1e-10, atol=1e-12)
dr = R0 / N
rf = np.arange(N+1)*dr
V = np.pi*(rf[1:]**2 - rf[:-1]**2)*H
A_s = 2*np.pi*R0*H
tf = np.linspace(0, 1800.0, 40001)
Y = s.sol(tf)
Ts = np.array([mm.surface_value(Y[:, j], tf[j])[0] for j in range(0, len(tf), 1)])
Cs = np.array([mm.surface_value(Y[:, j], tf[j])[1] for j in range(0, len(tf), 1)])
Ta_f = np.interp(tf, mm.t_ch, mm.T_ch)
Ca_f = np.interp(tf, mm.t_ch, mm.C_ch)
Econv = np.trapezoid(HC*A_s*(Ta_f - Ts), tf)
Mflux = np.trapezoid(HM*A_s*(Ca_f - Cs), tf)
rho0, cp0, _ = M.props_p1(Y[1::2, 0]);  rho1, cp1, _ = M.props_p1(Y[1::2, -1])
E0 = np.sum(rho0*cp0*Y[0::2, 0]*V);  E1 = np.sum(rho1*cp1*Y[0::2, -1]*V)
M0 = np.sum(Y[1::2, 0]*V);           M1 = np.sum(Y[1::2, -1]*V)
print(f'  能量残差: {E1-E0-Econv:+.3e} J  (相对 {abs(E1-E0-Econv)/abs(Econv):.2e})')
print(f'  水分残差: {M1-M0-Mflux:+.3e}    (相对 {abs(M1-M0-Mflux)/abs(Mflux):.2e})')

print()
print('=' * 88)
print('4) 生产网格选型: 全天(259200 s)积分耗时, 问题2 (附录3 变物性)')
print('=' * 88)
for N in (200, 400, 800):
    m2 = M.DryingModel(2, N=N)
    t0 = time.time()
    s2 = m2.solve(259200.0, rtol=1e-7, atol=1e-9)
    el = time.time()-t0
    Cend = s2.y[1::2, -1]
    print(f'  N={N:>4}: 步数 {s2.t.size:>6}  耗时 {el:>7.2f}s  '
          f'C_center={Cend[0]:.6f}  C_surf={Cend[-1]:.6f}  C_max={Cend.max():.6f}')
