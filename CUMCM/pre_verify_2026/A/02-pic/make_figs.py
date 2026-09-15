# -*- coding: utf-8 -*-
"""02-pic · 问题2 IEEE 解题报告佐证图生成(运行在 legion, conda 环境 cumcm_a)。

用法:
    python make_figs.py                 # 生成全部 8 张图
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
T_END = 10800.0                                       # 3 h 考察窗
T_TABLE_H = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
T_TABLE = [h * 3600.0 for h in T_TABLE_H]
T_HOLD = 7200.0                                       # 附件1 恒温干燥段起点
T_FULL = 216000.0                                     # 全流程作图窗(60 h)

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'


def save(fig, name):
    p = os.path.join(HERE, name)
    fig.savefig(p)
    plt.close(fig)
    print(f'  {name}  {os.path.getsize(p)/1024:.0f} KB')


def panel2(width=7.2, height=2.9, wspace=0.34, **kw):
    """双栏子图: 预留足够的 wspace, 避免右栏 ylabel 压到左栏数据。"""
    fig, ax = plt.subplots(1, 2, figsize=(width, height), **kw)
    fig.subplots_adjust(wspace=wspace)
    return fig, ax


def solve2(N=400, t_end=T_END):
    m = M.DryingModel(2, N=N)
    sol = m.solve(t_end, rtol=RTOL, atol=ATOL)
    return m, sol


def edges(p):
    p = np.asarray(p, float)
    return np.concatenate([[p[0]], (p[:-1] + p[1:]) / 2, [p[-1]]])


# --------------------------------------------------------------------------
# fig01 附件1 烘房条件: 两阶段结构 + 3 h 考察窗 + 维持末值假设(佐证表 III)
# --------------------------------------------------------------------------
def fig01_chamber():
    t, T, C = M.load_chamber()
    fig, ax = panel2(sharex=True)
    for a in ax:
        a.axvspan(0, T_HOLD, color=P.C_SHADE, alpha=.75, zorder=0)
        a.axvspan(T_HOLD, 14400, color='#E3F0E3', alpha=.9, zorder=0)
        a.axvline(10800, color=P.C_THRESH, ls=':', lw=1.4)
        a.set_xlabel('时间 t / s')
        a.set_xlim(0, 21000)
    ax[0].plot(t, T - 273.15, color=P.BLUE, lw=1.8, label='烘房温度')
    ax[0].plot([14400, 21000], [T[-1] - 273.15] * 2, ls='--', lw=1.4, color=P.BLUE,
               alpha=.65, label='维持末值(全流程假设)')
    ax[0].scatter(T_TABLE, np.interp(T_TABLE, t, T) - 273.15, s=16,
                  color=P.RED, zorder=5, label='表3/表4 时刻')
    ax[0].set_ylabel('烘房温度 $T_{air}$ / °C')
    ax[0].set_title('(a) 附件1 烘房温度')
    ax[1].plot(t, C, color=P.GREEN, lw=1.8, label='烘房水分浓度')
    ax[1].plot([14400, 21000], [C[-1]] * 2, ls='--', lw=1.4, color=P.GREEN, alpha=.65)
    ax[1].scatter(T_TABLE, np.interp(T_TABLE, t, C), s=16, color=P.RED, zorder=5,
                  label='表3/表4 时刻')
    ax[1].set_ylabel('烘房水分浓度 $C_{air}$ / (kg/kg)')
    ax[1].set_title('(b) 附件1 烘房水分浓度')
    for a in ax:
        a.grid(alpha=.3)
        a.legend(fontsize=7.5, loc='lower right')
    ax[0].text(3300, 33.5, '预热平衡阶段\n(0 – 2 h)', fontsize=8.5, ha='center')
    ax[0].text(10100, 33.5, '恒温干燥阶段\n(≥ 2 h)', fontsize=8.5, ha='center')
    ax[0].text(10900, 44.0, '3 h\n(表3/表4 窗口)', fontsize=8, color=P.C_THRESH)
    ax[0].text(15900, 47.6, '维持末值\n50.1650 °C', fontsize=8, color=P.BLUE)
    save(fig, 'fig01_chamber.png')


# --------------------------------------------------------------------------
# fig02/fig03 时空热力图: 温度 / 水分浓度(3 h × 0–2 cm)
# --------------------------------------------------------------------------
def _heatmap(field, cmap, vmin, vmax, cblabel, title, fname, notes=()):
    m, sol = solve2()
    cols = np.arange(0, 1.95, 0.1)                 # 0..1.8, 19 个内部点
    tt = np.arange(0, 10800 + 1, 30)               # 30 s 采样
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
                    bbox=dict(fc='white', ec='none', alpha=.8, pad=2),
                    arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1.2))
    ax.set_xlabel('到药材中心的距离 r / cm')
    ax.set_ylabel('时间 t / s')
    ax.set_title(title, fontsize=11)
    ax.grid(False)
    save(fig, fname)


def fig02_temp_map():
    _heatmap('T', P.HEAT_T, 28, 50.2, '温度 / °C', '温度场时空演化(3 h)', 'fig02_temp_map.png')


def fig03_moist_map():
    _heatmap('C', P.HEAT_C, 0.95, 2.55, '水分浓度 / (kg/kg)', '水分浓度时空演化(3 h)',
             'fig03_moist_map.png',
             notes=[((1.9, 3000), (0.35, 8300), '干壳(表面快速失水)'),
                    ((0.3, 6000), (0.55, 4300), '湿芯(中心仍接近初值)')])


# --------------------------------------------------------------------------
# fig04 附录3 物性随含水率变化(佐证 III.B 本构关系)
# --------------------------------------------------------------------------
def fig04_params():
    Cs = np.linspace(0.15, M.C_INIT, 400)
    rho0, cp0, k0 = (float(v[0]) for v in M.props_p3(np.array([M.C_INIT])))
    rho, cp, k = M.props_p3(Cs)
    fig, ax = panel2()
    ax[0].plot(Cs, rho / rho0, color=P.BLUE, lw=1.8, label=r'$\rho/\rho_0$')
    ax[0].plot(Cs, cp / cp0, color=P.GREEN, lw=1.8, label=r'$c_p/c_{p,0}$')
    ax[0].plot(Cs, k / k0, color=P.OLIVE, lw=1.8, label=r'$k/k_0$')
    ax[0].annotate('烘干后期物性同步下降\n(C=0.15 时 $c_p$ 仅剩 53%)',
                   xy=(0.22, 0.53), xytext=(2.45, 0.575), fontsize=8.5, ha='left',
                   va='center', arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1))
    ax[0].set_xlabel('水分浓度 C / (kg/kg)')
    ax[0].set_ylabel('归一化物性(相对初值)')
    ax[0].set_title('(a) 物性随含水率的变化(附录3)')
    ax[0].invert_xaxis()
    ax[0].set_ylim(0.45, 1.06)

    ax[1].plot(Cs, M.D_p3(Cs, np.full_like(Cs, 301.15)), color=P.BLUE, lw=1.8,
               label='T = 28 °C(预热段初值)')
    ax[1].plot(Cs, M.D_p3(Cs, np.full_like(Cs, 318.15)), color=P.PURPLE, lw=1.8,
               label='T = 45 °C')
    ax[1].plot(Cs, M.D_p3(Cs, np.full_like(Cs, 333.15)), color=P.RED, lw=1.8,
               label='T = 60 °C(恒温段)')
    ax[1].set_yscale('log')
    ax[1].annotate('D 降 16.8 倍\n($C: 2.55\\to0.15$, "自锁"效应)',
                   xy=(0.25, 3.4e-10), xytext=(1.35, 2.4e-9), fontsize=8.5,
                   arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1))
    ax[1].set_xlabel('水分浓度 C / (kg/kg)')
    ax[1].set_ylabel('扩散系数 D / (m²/s)')
    ax[1].set_title('(b) 扩散系数 D(C, T)(附录3)')
    ax[1].invert_xaxis()
    for a in ax:
        a.grid(alpha=.3)
        a.legend(fontsize=8)
        a.set_xticks([0.5, 1.0, 1.5, 2.0, 2.5])
    save(fig, 'fig04_params.png')


# --------------------------------------------------------------------------
# fig05 表面/中心 vs 烘房 时间曲线(佐证 V.C 分析)
# --------------------------------------------------------------------------
def fig05_timeseries():
    m, sol = solve2()
    tt = np.arange(0, 10800 + 1, 10)
    Y = sol.sol(tt)
    T, C = sample(m, Y, tt, np.asarray([0.0]), add_surface=True)
    Ta = np.interp(tt, m.t_ch, m.T_ch) - 273.15
    Ca = np.interp(tt, m.t_ch, m.C_ch)
    fig, ax = panel2()
    ax[0].plot(tt / 3600, Ta, ls='--', lw=1.3, color=P.C_AIR, label='烘房 $T_{air}$')
    ax[0].plot(tt / 3600, T[:, -1] - 273.15, color=P.C_SURF, lw=1.8,
               label='表面 r=2 cm(3 h: 49.9664)')
    ax[0].plot(tt / 3600, T[:, 0] - 273.15, color=P.C_CENTER, lw=1.8,
               label='中心 r=0(3 h: 49.8495)')
    ax[0].scatter(np.asarray(T_TABLE_H), np.interp(T_TABLE, tt, T[:, -1] - 273.15), s=14,
                  color=P.C_SURF, zorder=5)
    ax[0].scatter(np.asarray(T_TABLE_H), np.interp(T_TABLE, tt, T[:, 0] - 273.15), s=14,
                  color=P.C_CENTER, zorder=5)
    ax[0].set_ylabel('温度 / °C')
    ax[0].set_title('(a) 温度时间历程')

    ax[1].plot(tt / 3600, C[:, -1], color=P.C_SURF, lw=1.8,
               label='表面 r=2 cm(3 h: 1.0081)')
    ax[1].plot(tt / 3600, C[:, 0], color=P.C_CENTER, lw=1.8,
               label='中心 r=0(3 h: 1.7662)')
    ax[1].scatter(np.asarray(T_TABLE_H), np.interp(T_TABLE, tt, C[:, -1]), s=14,
                  color=P.C_SURF, zorder=5)
    ax[1].set_ylabel('水分浓度 / (kg/kg)')
    ax1b = ax[1].twinx()
    ax1b.plot(tt / 3600, Ca, ls='--', lw=1.3, color=P.C_AIR, label='烘房 $C_{air}$(右轴)')
    ax1b.set_ylabel('烘房水分浓度 / (kg/kg)', fontsize=8)
    ax1b.tick_params(labelsize=8)
    ax1b.set_ylim(0, 0.06)
    ax[1].set_title('(b) 水分浓度时间历程')
    h1, l1 = ax[1].get_legend_handles_labels()
    h2, l2 = ax1b.get_legend_handles_labels()
    ax[1].set_ylim(0.78, 2.72)
    ax[1].legend(h1 + h2, l1 + l2, fontsize=7.5, loc='lower left')
    ax[0].legend(fontsize=8, loc='lower right')
    for a in ax:
        a.set_xlabel('时间 t / h')
        a.set_xlim(0, 3.15)
        a.grid(alpha=.3)
    save(fig, 'fig05_timeseries.png')


# --------------------------------------------------------------------------
# fig06 全流程(60 h): 水分浓度 + 0.15 判据 + 有效扩散系数(佐证"整个烘干过程")
# --------------------------------------------------------------------------
def fig06_drying():
    m, sol = solve2(t_end=T_FULL)
    tt = np.arange(0.0, T_FULL + 1e-9, 600.0)          # 10 min 采样
    Y = sol.sol(tt)
    T, C = sample(m, Y, tt, np.asarray([0.0]), add_surface=True)
    Cc, Cs = C[:, 0], C[:, -1]                         # 中心 = max C(表面先干)
    D_eff = m.Dfun(Cc, T[:, 0])                        # 中心处有效扩散系数
    fig, ax = panel2(height=3.0)
    ax[0].plot(tt / 3600, Cs, color=P.C_SURF, lw=1.8, label='表面 r=2 cm')
    ax[0].plot(tt / 3600, Cc, color=P.C_CENTER, lw=1.8, label='中心 r=0(= max C)')
    ax[0].axhline(0.15, color=P.C_THRESH, ls='--', lw=1.5, label='烘干判据 0.15 kg/kg')
    ax[0].axvline(57.184, color=P.C_REF, ls=':', lw=1.4)
    ax[0].scatter([57.184], [0.15], s=40, color=P.C_THRESH, zorder=5)
    ax[0].annotate('t = 57.1840 h\n(= 2.3827 天)',
                   xy=(57.184, 0.15), xytext=(36, 0.72), fontsize=8.5,
                   arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1))
    ax[0].set_xlabel('时间 t / h')
    ax[0].set_ylabel('水分浓度 / (kg/kg)')
    ax[0].set_title('(a) 全流程水分浓度(60 h)')
    ax[0].set_xlim(0, 60)
    ax[0].legend(fontsize=8, loc='upper right')
    ax[1].semilogy(tt / 3600, D_eff, color=P.PURPLE, lw=1.8, label='$D(C_c, T_c)$')
    ax[1].scatter(tt[:1] / 3600, D_eff[:1], s=30, color=P.PURPLE, zorder=5)
    ax[1].annotate('升温加速\n(Arrhenius)', xy=(1.6, 1.28e-8), xytext=(9, 6.5e-9),
                   fontsize=8.5, arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1))
    ax[1].annotate('自锁衰减\n(浓度依赖, 17×)', xy=(48, 8.5e-10), xytext=(30, 3.4e-9),
                   fontsize=8.5, arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1))
    ax[1].set_xlabel('时间 t / h')
    ax[1].set_ylabel('有效扩散系数 / (m²/s)')
    ax[1].set_title('(b) 有效扩散系数:先升温加速,后自锁衰减')
    ax[1].set_xlim(0, 60)
    ax[1].legend(fontsize=8, loc='lower left')
    for a in ax:
        a.grid(alpha=.3, which='both')
    save(fig, 'fig06_drying.png')


# --------------------------------------------------------------------------
# fig07 网格收敛: log-log + 二阶参考 + 4 位小数阈值(佐证表 VI)
# --------------------------------------------------------------------------
def fig07_convergence():
    vals = {}
    for N in (100, 200, 400, 800):
        mn = M.DryingModel(2, N=N)
        sn = mn.solve(T_END, rtol=RTOL, atol=ATOL)
        Yn = sn.sol(np.array([T_END]))
        Tn, Cn = sample(mn, Yn, np.array([T_END]), np.asarray([0.0]), add_surface=True)
        vals[N] = (Tn[0, 0] - 273.15, Cn[0, -1])      # (中心 T, 表面 C)
    Ns = np.array([100, 200, 400, 800])
    errC = np.array([abs(vals[N][1] - (vals[800][1] + (vals[800][1] - vals[400][1]) / 3))
                     for N in Ns])
    errT = np.array([abs(vals[N][0] - (vals[800][0] + (vals[800][0] - vals[400][0]) / 3))
                     for N in Ns])
    p = np.log2(abs(vals[100][1] - vals[200][1]) / abs(vals[200][1] - vals[400][1]))
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    ax.loglog(Ns, errC, 'o-', lw=1.8, ms=5, color=P.C_SURF, label='表面 C(3 h)')
    ax.loglog(Ns, errT, 's-', lw=1.8, ms=5, color=P.C_CENTER, label='中心 T(3 h)')
    ax.loglog(Ns, errC[1] * (Ns / Ns[1]) ** -2.0, '--', lw=1.4, color=P.C_REF,
              label='二阶参考 $\\propto N^{-2}$')
    ax.axhline(5e-5, color=P.C_THRESH, ls=':', lw=1.4, label='4 位小数阈值 $5\\times10^{-5}$')
    ax.annotate(f'收敛阶 p ≈ {p:.2f}\n(N = 100→400 段)', xy=(500, errC[2]), xytext=(140, 2.5e-6),
                fontsize=9, arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1))
    ax.set_xlabel('网格数 N')
    ax.set_ylabel('误差(相对 Richardson 基准)')
    ax.grid(alpha=.3, which='both')
    ax.legend(fontsize=8)
    save(fig, 'fig07_convergence.png')


# --------------------------------------------------------------------------
# fig08 水分质量守恒: 总水分 + 残差(佐证表 VI)
# --------------------------------------------------------------------------
def fig08_conservation():
    trapz = getattr(np, 'trapezoid', None) or np.trapz
    m, sol = solve2()
    tt = np.arange(0, 10800 + 1, 1.0)
    Y = sol.sol(tt)
    xi = m.xi_c
    Mt = (Y[1::2, :] * xi[:, None]).sum(axis=0) * m.dxi
    _, Cs = sample(m, Y, tt, np.asarray([0.0]), add_surface=True)
    flux = m.hm * (Cs[:, -1] - np.interp(tt, m.t_ch, m.C_ch)) / m.Rmax
    cum = np.concatenate([[0.0], np.cumsum((flux[1:] + flux[:-1]) / 2 * np.diff(tt))])
    resid = (Mt - Mt[0]) + cum
    fig, ax = panel2(height=2.7)
    ax[0].plot(tt / 3600, Mt, color=P.BLUE, lw=1.8, label='域积分 $\\tilde M(t)=\\int C\\,\\xi d\\xi$')
    ax[0].plot(tt / 3600, Mt[0] - cum, ls='--', lw=1.3, color=P.OLIVE,
               label='边界通量积分 $\\tilde M(0)-\\int q dt$')
    ax[0].set_xlabel('时间 t / h')
    ax[0].set_ylabel('归一化总水分 $\\tilde M$')
    ax[0].set_title('(a) 总水分')
    ax[1].plot(tt / 3600, resid, color=P.RED, lw=1.5, label='守恒残差')
    ax[1].axhline(0, color=P.C_REF, ls='--', lw=.8)
    ax[1].set_xlabel('时间 t / h')
    ax[1].set_ylabel('残差')
    ax[1].set_ylim(-3e-7, 3e-7)
    ax[1].annotate(f'最大 |残差| = {np.abs(resid).max():.1e}\n'
                   f'(相对 {np.abs(resid).max()/Mt[0]:.1e})',
                   xy=(1.55, 2.2e-7), fontsize=9)
    ax[1].set_title('(b) 守恒残差(1 s 细网格通量积分)')
    for a in ax:
        a.grid(alpha=.3)
        a.legend(fontsize=8)
    save(fig, 'fig08_conservation.png')


FIGS = {'fig01': fig01_chamber, 'fig02': fig02_temp_map, 'fig03': fig03_moist_map,
        'fig04': fig04_params, 'fig05': fig05_timeseries, 'fig06': fig06_drying,
        'fig07': fig07_convergence, 'fig08': fig08_conservation}


def main():
    sel = [s for s in sys.argv[1:] if s in FIGS] or list(FIGS)
    print(f'生成 {len(sel)} 张图 -> {HERE}')
    for k in sel:
        FIGS[k]()
    print('完成。')


if __name__ == '__main__':
    main()
