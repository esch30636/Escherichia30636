# -*- coding: utf-8 -*-
"""01-pic · 问题1 IEEE 解题报告佐证图生成(运行在 legion, conda 环境 cumcm_a)。

用法:
    python make_figs.py                 # 生成全部 7 张图
    python make_figs.py fig03 fig06     # 只生成指定图

vivid-figures 原则: 配色统一从 palette.py 导入(低饱和、高区分度、ColorBrewer/
seaborn muted 成熟色号、禁 jet); 图表选型跳出老三样(时空热力图、对数量级图、
对数收敛图)。300 dpi, IEEE 双栏宽度。
"""
import os, sys
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
# 复用已验证模型 a_model / a_output(不拷贝, 避免版本分叉)。
# legion 布局: 代码在 A\src\(本地在 A\); 两个候选目录取存在 a_model.py 者。
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _cand in (_BASE, os.path.join(_BASE, 'src')):
    if os.path.isdir(_cand) and 'a_model.py' in os.listdir(_cand):
        sys.path.insert(0, _cand)
        break
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import a_model as M
from a_output import sample
import palette as P

HERE = os.path.dirname(os.path.abspath(__file__))
RTOL, ATOL = 1e-8, 1e-10
T_TABLE = [100, 300, 600, 900, 1200, 1500, 1800]

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'


def save(fig, name):
    p = os.path.join(HERE, name)
    fig.savefig(p)
    plt.close(fig)
    print(f'  {name}  {os.path.getsize(p)/1024:.0f} KB')


def solve1(N=400):
    m = M.DryingModel(1, N=N)
    sol = m.solve(1800.0, rtol=RTOL, atol=ATOL)
    return m, sol


def edges(p):
    p = np.asarray(p, float)
    return np.concatenate([[p[0]], (p[:-1] + p[1:]) / 2, [p[-1]]])


# --------------------------------------------------------------------------
# fig01 附件1 烘房条件: 30 min 预热窗口 + 表时刻标记(佐证表 III)
# --------------------------------------------------------------------------
def fig01_chamber():
    t, T, C = M.load_chamber()
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.7), sharex=True)
    for a in ax:
        a.axvspan(0, 1800, color=P.C_SHADE, alpha=.7, zorder=0)
        a.set_xlabel('时间 t / s')
    ax[0].plot(t, T - 273.15, color=P.BLUE, lw=1.8, label='烘房温度')
    ax[0].scatter(T_TABLE, np.interp(T_TABLE, t, T) - 273.15, s=18,
                  color=P.RED, zorder=5, label='表1/表2 时刻')
    ax[0].set_ylabel('烘房温度 $T_{air}$ / °C')
    ax[0].set_title('(a) 附件1 烘房温度')
    ax[1].plot(t, C, color=P.GREEN, lw=1.8, label='烘房水分浓度')
    ax[1].scatter(T_TABLE, np.interp(T_TABLE, t, C), s=18,
                  color=P.RED, zorder=5, label='表1/表2 时刻')
    ax[1].set_ylabel('烘房水分浓度 $C_{air}$ / (kg/kg)')
    ax[1].set_title('(b) 附件1 烘房水分浓度')
    for a in ax:
        a.axvline(14400, color=P.C_REF, ls='--', lw=1)
        a.text(14500, a.get_ylim()[0], ' 14400 s 后按末值维持\n (问题2/3 假设)', fontsize=8)
        a.grid(alpha=.3)
        a.legend(fontsize=8, loc='center right')
    ax[0].text(150, 49.5, '预热平衡阶段\n(本问 30 min)', fontsize=9, ha='center')
    save(fig, 'fig01_chamber.png')


# --------------------------------------------------------------------------
# fig02/fig03 时空热力图: 温度 / 水分浓度(vivid-figures 进阶选型)
# --------------------------------------------------------------------------
def _heatmap(field, cmap, vmin, vmax, cblabel, title, fname, notes=()):
    m, sol = solve1()
    cols = np.arange(0, 1.95, 0.1)                 # 0..1.8, 19 个内部点
    tt = np.arange(0, 1801, 10)                    # 10 s 采样
    Y = sol.sol(tt)
    T, C = sample(m, Y, tt, cols, add_surface=True)
    Z = (T - 273.15) if field == 'T' else C
    pts_r = np.append(cols, 2.0)
    X, Yg = np.meshgrid(edges(pts_r), edges(tt))
    fig, ax = plt.subplots(figsize=(4.6, 4.2))
    pc = ax.pcolormesh(X, Yg, Z, cmap=cmap, vmin=vmin, vmax=vmax, shading='flat')
    cb = fig.colorbar(pc, ax=ax, fraction=.046, pad=.04)
    cb.set_label(cblabel)
    cb.ax.tick_params(labelsize=8)
    for xy, xytext, txt in notes:
        ax.annotate(txt, xy=xy, xytext=xytext, fontsize=9,
                    arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1.2))
    ax.set_xlabel('到药材中心的距离 r / cm')
    ax.set_ylabel('时间 t / s')
    ax.set_title(title, fontsize=11)
    ax.grid(False)
    save(fig, fname)


def fig02_temp_map():
    _heatmap('T', P.HEAT_T, 28, 38, '温度 / °C', '温度场时空演化(30 min)', 'fig02_temp_map.png')


def fig03_moist_map():
    _heatmap('C', P.HEAT_C, 1.45, 2.55, '水分浓度 / (kg/kg)', '水分浓度时空演化(30 min)',
             'fig03_moist_map.png',
             notes=[((1.85, 800), (0.45, 1300), '干壳(表面快速失水)'),
                    ((0.3, 600), (0.6, 200), '湿芯(基本不变)')])


# --------------------------------------------------------------------------
# fig04 表面/中心 vs 烘房 时间曲线(佐证 V.C 分析)
# --------------------------------------------------------------------------
def fig04_timeseries():
    m, sol = solve1()
    tt = np.arange(0, 1801, 10)
    Y = sol.sol(tt)
    T, C = sample(m, Y, tt, np.asarray([0.0]), add_surface=True)
    Ta = np.interp(tt, m.t_ch, m.T_ch) - 273.15
    Ca = np.interp(tt, m.t_ch, m.C_ch)
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.9))
    ax[0].plot(tt, Ta, ls='--', lw=1.3, color=P.C_AIR, label='烘房 $T_{air}$')
    ax[0].plot(tt, T[:, -1] - 273.15, color=P.C_SURF, lw=1.8, label='表面 r=2 cm')
    ax[0].plot(tt, T[:, 0] - 273.15, color=P.C_CENTER, lw=1.8, label='中心 r=0')
    ax[0].scatter(T_TABLE, np.interp(T_TABLE, tt, T[:, -1] - 273.15), s=14,
                  color=P.C_SURF, zorder=5)
    ax[0].scatter(T_TABLE, np.interp(T_TABLE, tt, T[:, 0] - 273.15), s=14,
                  color=P.C_CENTER, zorder=5)
    ax[0].set_ylabel('温度 / °C')
    ax[0].set_title('(a) 温度时间历程')
    ax[0].text(1810, 36.9, '36.7856', fontsize=8, color=P.C_SURF, va='bottom')
    ax[0].text(1810, 33.4, '33.5753', fontsize=8, color=P.C_CENTER, va='bottom')

    ax[1].plot(tt, C[:, -1], color=P.C_SURF, lw=1.8, label='表面 r=2 cm')
    ax[1].plot(tt, C[:, 0], color=P.C_CENTER, lw=1.8, label='中心 r=0')
    ax[1].scatter(T_TABLE, np.interp(T_TABLE, tt, C[:, -1]), s=14,
                  color=P.C_SURF, zorder=5)
    ax[1].set_ylabel('水分浓度 / (kg/kg)')
    ax1b = ax[1].twinx()
    ax1b.plot(tt, Ca, ls='--', lw=1.3, color=P.C_AIR, label='烘房 $C_{air}$(右轴)')
    ax1b.set_ylabel('烘房水分浓度 / (kg/kg)', fontsize=8)
    ax1b.tick_params(labelsize=8)
    ax[1].set_title('(b) 水分浓度时间历程')
    ax[1].text(1810, 1.47, '1.5102', fontsize=8, color=P.C_SURF, va='bottom')
    ax[1].text(1810, 2.53, '2.5500', fontsize=8, color=P.C_CENTER, va='bottom')
    for a in ax:
        a.set_xlabel('时间 t / s')
        a.grid(alpha=.3)
        a.legend(fontsize=8)
    save(fig, 'fig04_timeseries.png')


# --------------------------------------------------------------------------
# fig05 特征时间量级(佐证 III.E 先验分析)
# --------------------------------------------------------------------------
def fig05_timescale():
    fig, ax = plt.subplots(figsize=(6.0, 2.7))
    names = ['考察窗(题面)', 'τ$_T$ = 39.5 min', 'τ$_C$ = 22.5 h']
    vals = [30.0, 39.48, 1350.2]
    colors = [P.C_AIR, P.BLUE, P.RED]
    ax.barh(names, vals, color=colors, height=.55, edgecolor='none')
    ax.set_xscale('log')
    ax.set_xlim(8, 5000)
    ax.set_xticks([10, 30, 100, 1000])
    ax.set_xticklabels(['10', '30', '100', '1000'])
    ax.set_xlabel('时间 / min(对数轴)')
    ax.annotate('$\\tau_C/\\tau_T \\approx 34$(热快湿慢)',
                xy=(39.5, 1), xytext=(300, 1.42), fontsize=10,
                arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1.2))
    ax.text(2000, -0.42, 'Bi = 1.39: 内部温度梯度显著\nBi$_m$ = 3.24: 表面快速失水',
            fontsize=8.5, va='top', ha='center')
    ax.grid(alpha=.3, axis='x', which='both')
    ax.set_ylim(-0.62, 2.62)
    save(fig, 'fig05_timescale.png')


# --------------------------------------------------------------------------
# fig06 网格收敛: log-log + 二阶参考 + 4 位小数阈值(佐证表 VI)
# --------------------------------------------------------------------------
def fig06_convergence():
    vals = {}
    for N in (100, 200, 400, 800):
        mn = M.DryingModel(1, N=N)
        sn = mn.solve(1800.0, rtol=RTOL, atol=ATOL)
        Yn = sn.sol(np.array([1800.0]))
        Tn, Cn = sample(mn, Yn, np.array([1800.0]), np.asarray([0.0]), add_surface=True)
        vals[N] = (Tn[0, 0] - 273.15, Cn[0, -1])      # (中心 T, 表面 C)
    Ns = np.array([100, 200, 400, 800])
    errC = np.array([abs(vals[N][1] - (vals[800][1] + (vals[800][1] - vals[400][1]) / 3))
                     for N in Ns])
    errT = np.array([abs(vals[N][0] - (vals[800][0] + (vals[800][0] - vals[400][0]) / 3))
                     for N in Ns])
    p = np.log2(abs(vals[200][1] - vals[400][1]) / abs(vals[400][1] - vals[800][1]))
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    ax.loglog(Ns, errC, 'o-', lw=1.8, ms=5, color=P.C_SURF, label='表面 C(1800 s)')
    ax.loglog(Ns, errT, 's-', lw=1.8, ms=5, color=P.C_CENTER, label='中心 T(1800 s)')
    ax.loglog(Ns, errC[1] * (Ns / Ns[1]) ** -2.0, '--', lw=1.4, color=P.C_REF,
              label='二阶参考 $\\propto N^{-2}$')
    ax.axhline(5e-5, color=P.C_THRESH, ls=':', lw=1.4, label='4 位小数阈值 $5\\times10^{-5}$')
    ax.annotate(f'收敛阶 p ≈ {p:.2f}', xy=(500, errC[2]), xytext=(170, 1.6e-6),
                fontsize=9, arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1))
    ax.set_xlabel('网格数 N')
    ax.set_ylabel('误差(相对 Richardson 基准)')
    ax.grid(alpha=.3, which='both')
    ax.legend(fontsize=8)
    save(fig, 'fig06_convergence.png')


# --------------------------------------------------------------------------
# fig07 水分质量守恒: 总水分 + 残差(佐证表 VI)
# --------------------------------------------------------------------------
def fig07_conservation():
    trapz = getattr(np, 'trapezoid', None) or np.trapz
    m, sol = solve1()
    tt = np.arange(0, 1801, 1.0)
    Y = sol.sol(tt)
    xi = m.xi_c
    Mt = (Y[1::2, :] * xi[:, None]).sum(axis=0) * m.dxi
    _, Cs = sample(m, Y, tt, np.asarray([0.0]), add_surface=True)
    flux = m.hm * (Cs[:, -1] - np.interp(tt, m.t_ch, m.C_ch)) / m.Rmax
    cum = np.concatenate([[0.0], np.cumsum((flux[1:] + flux[:-1]) / 2 * np.diff(tt))])
    resid = (Mt - Mt[0]) + cum
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.7))
    ax[0].plot(tt, Mt, color=P.BLUE, lw=1.8, label='域积分 $\\tilde M(t)=\\int C\\,\\xi d\\xi$')
    ax[0].plot(tt, Mt[0] - cum, ls='--', lw=1.3, color=P.OLIVE,
               label='边界通量积分 $\\tilde M(0)-\\int q dt$')
    ax[0].set_xlabel('时间 t / s')
    ax[0].set_ylabel('归一化总水分 $\\tilde M$')
    ax[0].set_title('(a) 总水分')
    ax[1].plot(tt, resid, color=P.RED, lw=1.5, label='守恒残差')
    ax[1].axhline(0, color=P.C_REF, ls='--', lw=.8)
    ax[1].set_xlabel('时间 t / s')
    ax[1].set_ylabel('残差')
    ax[1].set_ylim(-3e-7, 3e-7)
    ax[1].annotate(f'最大 |残差| = {np.abs(resid).max():.1e}\n'
                   f'(相对 {np.abs(resid).max()/Mt[0]:.1e})',
                   xy=(900, 2.2e-7), fontsize=9)
    ax[1].set_title('(b) 守恒残差(1 s 细网格通量积分)')
    for a in ax:
        a.grid(alpha=.3)
        a.legend(fontsize=8)
    save(fig, 'fig07_conservation.png')


FIGS = {'fig01': fig01_chamber, 'fig02': fig02_temp_map, 'fig03': fig03_moist_map,
        'fig04': fig04_timeseries, 'fig05': fig05_timescale,
        'fig06': fig06_convergence, 'fig07': fig07_conservation}


def main():
    sel = [s for s in sys.argv[1:] if s in FIGS] or list(FIGS)
    print(f'生成 {len(sel)} 张图 -> {HERE}')
    for k in sel:
        FIGS[k]()
    print('完成。')


if __name__ == '__main__':
    main()
