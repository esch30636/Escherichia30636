# -*- coding: utf-8 -*-
"""A 题:
 1) RHS 恒等性检验 —— 直接在同一状态上比较 xi 形式与物理坐标形式的右端项
    (排除 ODE 求解器噪声, 是离散是否等价的判定性检验)
 2) 输出网格各列的收敛性: r=0 外推 / 内部插值 / 表面 BC 重构
 3) 问题3 烘干时间的网格收敛性
"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import numpy as np
import a_model as M
from a_ref import RefPhysical

R0 = M.R0

print('=' * 88)
print('1) RHS 恒等性检验 (同一状态下逐分量比较)')
print('=' * 88)
N = 200
m = M.DryingModel(1, N=N)
rp = RefPhysical(N=N, problem=1)

rng = np.random.default_rng(0)
for trial, label in enumerate(['均匀初值', '随机扰动状态', '强梯度状态']):
    if trial == 0:
        y = m.y0()
    elif trial == 1:
        y = m.y0() * (1 + 0.05 * rng.standard_normal(2 * N))
    else:
        y = m.y0()
        y[0::2] += 20.0 * np.linspace(-1, 1, N)      # T 梯度
        y[1::2] *= np.linspace(0.2, 1.2, N)          # C 梯度
    for t in (0.0, 137.0, 1800.0):
        a = m.rhs(t, y)
        b = rp.rhs(t, y)
        rel = np.abs(a - b).max() / max(np.abs(b).max(), 1e-300)
        print(f'  {label:<12} t={t:>7.1f}s   max|diff|={np.abs(a-b).max():.3e}   '
              f'相对={rel:.3e}')

print()
print('=' * 88)
print('2) 输出网格各列收敛性 (问题1, t=1800 s; 以 N=1600 Richardson 外推为基准)')
print('=' * 88)
Ns = [50, 100, 200, 400, 800, 1600]
rows = {}
for N in Ns:
    mm = M.DryingModel(1, N=N)
    s = mm.solve(1800.0, t_eval=[1800.0], rtol=1e-10, atol=1e-12)
    y = s.y[:, -1]
    Tc, Cc = mm.interp_xi(y, [0.0])
    T9, C9 = mm.interp_xi(y, [1.9e-2 / R0])
    Ts, Cs = mm.surface_value(y, 1800.0)
    rows[N] = dict(T0=Tc[0]-273.15, C0=Cc[0], T19=T9[0]-273.15, C19=C9[0],
                   Ts=Ts-273.15, Cs=Cs)
    print(f'  N={N:>5}:  C0={Cc[0]:.6f}  C@1.9={C9[0]:.6f}  Cs_BC={Cs:.6f}  '
          f'Ts_BC={Ts-273.15:.6f}')

def rich(key):
    return rows[1600][key] + (rows[1600][key] - rows[800][key]) / 3

print('\n  相对 Richardson 基准的误差 (需要 < 5e-5 才能保证 4 位小数):')
print(f'  {"N":>5} {"C(r=0)":>13} {"C(r=1.9)":>13} {"C(表面)BC":>13} {"T(表面)BC":>13}')
ref = {k: rich(k) for k in ('C0', 'C19', 'Cs', 'Ts')}
for N in Ns[:-1]:
    print(f'  {N:>5} {rows[N]["C0"]-ref["C0"]:>13.2e} {rows[N]["C19"]-ref["C19"]:>13.2e} '
          f'{rows[N]["Cs"]-ref["Cs"]:>13.2e} {rows[N]["Ts"]-ref["Ts"]:>13.2e}')

print()
print('=' * 88)
print('3) 问题3 烘干时间 (max C < 0.15 kg/kg) 的网格收敛性')
print('=' * 88)
print(f'  {"N":>5} {"t_end(s)":>12} {"(h)":>9} {"(天)":>7} {"步数":>7} {"耗时(s)":>9}')
for N in (100, 200, 400, 800):
    m3 = M.DryingModel(3, N=N)

    def ev(t, y):
        return y[1::2].max() - 0.15
    ev.terminal = True
    ev.direction = -1

    t0 = time.time()
    s = m3.solve(300000.0, events=[ev], rtol=1e-8, atol=1e-10)
    el = time.time() - t0
    te = s.t_events[0][0] if len(s.t_events[0]) else np.nan
    print(f'  {N:>5} {te:>12.1f} {te/3600:>9.4f} {te/86400:>7.4f} {s.t.size:>7} {el:>9.2f}')
