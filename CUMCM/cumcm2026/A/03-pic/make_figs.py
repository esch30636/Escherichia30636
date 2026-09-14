# -*- coding: utf-8 -*-
"""03-pic · 问题3 IEEE 解题报告佐证图生成(运行在 legion, conda 环境 cumcm_a)。

用法:
    python make_figs.py                 # 生成全部 8 张图
    python make_figs.py fig03 fig05     # 只生成指定图

vivid-figures 原则: 配色统一从 palette.py 导入(低饱和、高区分度、ColorBrewer/
seaborn muted 成熟色号、禁 jet); 选型跳出老三样(全流程时空热力图、判据前沿等值线、
自锁效应量级图、烘干时间对数收敛图)。300 dpi, IEEE 双栏宽度。
"""
import os, sys
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
# 复用已验证模型 a_model / a_output(不拷贝, 避免版本分叉)。
# legion 布局: 代码在 A\src\(本地在 A); 两个候选目录取存在 a_model.py 者。
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
C_END = 0.15                                   # 烘干判据
T_TABLE_H = [6.0, 12.0, 18.0, 24.0, 30.0, 36.0, 42.0, 48.0, 54.0]
T_HOLD = 7200.0                                # 附件1 恒温干燥段起点
T_ATT1 = 14400.0                               # 附件1 采样末点
T_END3 = 205862.4                              # 问题3 烘干时间(s, 正式结果)
T_END4 = 182974.1                              # 问题4 烘干时间(s, 用于交叉校验)
LAM1 = 2.404825557695773

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


def edges(p):
    p = np.asarray(p, float)
    return np.concatenate([[p[0]], (p[:-1] + p[1:]) / 2, [p[-1]]])


def solve3(m, t_max=300000.0):
    """问题3 全流程求解(事件在 max C < 0.15 时终止), 返回 (t_end, sol)。"""
    def ev(t, y):
        return y[1::2].max() - C_END
    ev.terminal = True
    ev.direction = -1
    sol = m.solve(t_max, events=[ev], rtol=RTOL, atol=ATOL)
    te = float(sol.t_events[0][0]) if len(sol.t_events[0]) else np.nan
    print(f'    求解完成: t_end = {te:.1f} s({te/3600:.4f} h), {sol.t.size} 步')
    return te, sol


# --------------------------------------------------------------------------
# fig01 附件1 烘房条件: 全流程视角(附件1 0-4 h + 维持末值外推 + 表5 时刻 + 烘干结束)
# --------------------------------------------------------------------------
def fig01_chamber():
    t, T, C = M.load_chamber()
    th = t / 3600.0
    fig, ax = panel2(sharex=True)
    for a in ax:
        a.axvspan(0, T_HOLD / 3600, color=P.C_SHADE, alpha=.75, zorder=0)
        a.axvspan(T_HOLD / 3600, T_ATT1 / 3600, color='#E3F0E3', alpha=.9, zorder=0)
        a.axvspan(T_ATT1 / 3600, 58, color='#F5F0E6', alpha=.9, zorder=0)
        a.axvline(T_END3 / 3600, color=P.C_THRESH, ls=':', lw=1.4)
        a.set_xlabel('时间 t / h')
        a.set_xlim(0, 58)
    ax[0].plot(th, T - 273.15, color=P.BLUE, lw=1.8, label='附件1 烘房温度(0–4 h)')
    ax[0].plot([4, 58], [T[-1] - 273.15] * 2, ls='--', lw=1.4, color=P.BLUE, alpha=.65,
               label='维持末值(全流程假设)')
    ax[0].scatter(T_TABLE_H, [T[-1] - 273.15] * len(T_TABLE_H), s=14, color=P.RED,
                  zorder=5, label='表5 时刻')
    ax[0].set_ylabel('烘房温度 $T_{air}$ / °C')
    ax[0].set_title('(a) 附件1 烘房温度')
    ax[1].plot(th, C, color=P.GREEN, lw=1.8, label='附件1 烘房水分浓度(0–4 h)')
    ax[1].plot([4, 58], [C[-1]] * 2, ls='--', lw=1.4, color=P.GREEN, alpha=.65)
    ax[1].scatter(T_TABLE_H, [C[-1]] * len(T_TABLE_H), s=14, color=P.RED, zorder=5)
    ax[1].set_ylabel('烘房水分浓度 $C_{air}$ / (kg/kg)')
    ax[1].set_title('(b) 附件1 烘房水分浓度')
    for a in ax:
        a.grid(alpha=.3)
        a.legend(fontsize=7.5, loc='lower right')
    ax[0].text(1.0, 33.5, '预热平衡\n(0–2 h)', fontsize=8.5, ha='center')
    ax[0].text(3.0, 33.5, '恒温干燥\n(2–4 h)', fontsize=8.5, ha='center')
    ax[0].text(31, 47.3, '维持末值 50.1650 °C(全流程外推)', fontsize=8, color=P.BLUE)
    ax[0].text(57.8, 43.5, '烘干结束\n57.1840 h', fontsize=8, color=P.C_THRESH, ha='right')
    save(fig, 'fig01_chamber.png')


# --------------------------------------------------------------------------
# fig02 全流程水分时空热力图(57.2 h × 0–2 cm)+ 判据前沿等值线
# --------------------------------------------------------------------------
def fig02_moist_map():
    m = M.DryingModel(3, N=400)
    te, sol = solve3(m)
    cols = np.arange(0, 1.95, 0.1)                 # 0..1.8, 19 个内部点
    tt = np.arange(0.0, te + 1e-9, 60.0)
    Y = sol.sol(tt)
    T, C = sample(m, Y, tt, cols, add_surface=True)
    pts_r = np.append(cols, 2.0)
    r_mid = (pts_r[:-1] + pts_r[1:]) / 2
    t_mid = (tt[:-1] + tt[1:]) / 2 / 3600.0
    Xm, Ym = np.meshgrid(r_mid, t_mid)
    fig, ax = plt.subplots(figsize=(4.6, 4.2))
    pc = ax.pcolormesh(edges(pts_r), edges(tt / 3600.0), C, cmap=P.HEAT_C,
                       vmin=0.0, vmax=2.55, shading='flat')
    cb = fig.colorbar(pc, ax=ax, fraction=.046, pad=.04)
    cb.set_label('水分浓度 / (kg/kg)')
    cb.ax.tick_params(labelsize=8)
    ax.contour(Xm, Ym, C[:-1, :-1], levels=[C_END], colors=P.C_THRESH, linewidths=1.3,
               linestyles='--')
    ax.annotate('干壳(表面快速失水)', xy=(1.9, 4), xytext=(0.35, 12), fontsize=9,
                bbox=dict(fc='white', ec='none', alpha=.8, pad=2),
                arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1.2))
    ax.annotate('湿芯(中心保持初值)', xy=(0.25, 8), xytext=(0.5, 22), fontsize=9,
                bbox=dict(fc='white', ec='none', alpha=.8, pad=2),
                arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1.2))
    ax.annotate('烘干判据前沿 C = 0.15\n(约 13 h 从表面出发, 57.18 h 到达中心)',
                xy=(1.05, 33), xytext=(0.15, 48), fontsize=9,
                bbox=dict(fc='white', ec='none', alpha=.8, pad=2),
                arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1.2))
    ax.set_xlabel('到药材中心的距离 r / cm')
    ax.set_ylabel('时间 t / h')
    ax.set_title('水分浓度时空演化(全流程 57.2 h)', fontsize=11)
    ax.grid(False)
    save(fig, 'fig02_moist_map.png')


# --------------------------------------------------------------------------
# fig03 表面/中心时间历程: (a) 温度瞬态(前 6 h) (b) 水分全流程 + 判据
# --------------------------------------------------------------------------
def fig03_drying_curve():
    m = M.DryingModel(3, N=400)
    te, sol = solve3(m)
    tta = np.arange(0.0, 21600.0 + 1e-9, 60.0)
    Ya = sol.sol(tta)
    Ta, Ca = sample(m, Ya, tta, np.asarray([0.0]), add_surface=True)
    Tair_a = np.interp(tta, m.t_ch, m.T_ch) - 273.15
    tt = np.arange(0.0, te + 1e-9, 600.0)
    Y = sol.sol(tt)
    T, C = sample(m, Y, tt, np.asarray([0.0]), add_surface=True)
    fig, ax = panel2()
    ax[0].plot(tta / 3600, Tair_a, ls='--', lw=1.3, color=P.C_AIR, label='烘房 $T_{air}$')
    ax[0].plot(tta / 3600, Ta[:, -1] - 273.15, color=P.C_SURF, lw=1.8, label='表面')
    ax[0].plot(tta / 3600, Ta[:, 0] - 273.15, color=P.C_CENTER, lw=1.8, label='中心')
    ax[0].annotate(f'约 2 h 后全场 = 烘房温度(准稳态)\n'
                   f'(此后恒为 {Tair_a[-1]:.4f} °C)', xy=(2.2, 50.1), xytext=(3.3, 40),
                   fontsize=8.5, arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1))
    ax[0].set_xlabel('时间 t / h')
    ax[0].set_ylabel('温度 / °C')
    ax[0].set_title('(a) 温度时间历程(前 6 h)')
    ax[0].set_xlim(0, 6.2)
    ax[0].grid(alpha=.3)
    ax[0].legend(fontsize=8, loc='lower right')

    ax[1].plot(tt / 3600, C[:, -1], color=P.C_SURF, lw=1.8,
               label=f'表面 r=2 cm(结束 {C[-1, -1]:.4f})')
    ax[1].plot(tt / 3600, C[:, 0], color=P.C_CENTER, lw=1.8,
               label=f'中心 r=0(结束 {C[-1, 0]:.4f})')
    ax[1].axhline(C_END, color=P.C_THRESH, ls='--', lw=1.5, label=f'烘干判据 {C_END} kg/kg')
    ax[1].axvline(te / 3600, color=P.C_REF, ls=':', lw=1.4)
    ax[1].scatter(T_TABLE_H, np.interp(np.asarray(T_TABLE_H) * 3600, tt, C[:, 0]), s=14,
                  color=P.C_CENTER, zorder=5)
    ax[1].scatter([te / 3600], [C_END], s=40, color=P.C_THRESH, zorder=5)
    ax[1].annotate(f't = {te/3600:.4f} h\n(= {te/86400:.4f} 天)',
                   xy=(te / 3600, C_END), xytext=(33, 0.72), fontsize=8.5,
                   arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1))
    ax[1].set_xlabel('时间 t / h')
    ax[1].set_ylabel('水分浓度 / (kg/kg)')
    ax[1].set_title('(b) 水分浓度时间历程(全流程)')
    ax[1].set_xlim(0, 60)
    ax[1].grid(alpha=.3)
    ax[1].legend(fontsize=8, loc='upper right')
    save(fig, 'fig03_drying_curve.png')


# --------------------------------------------------------------------------
# fig04 自锁效应全流程量化: (a) 有效扩散系数 (b) 基模时间常数
# --------------------------------------------------------------------------
def fig04_selflock():
    m = M.DryingModel(3, N=400)
    te, sol = solve3(m)
    tt = np.arange(0.0, te + 1e-9, 600.0)
    Y = sol.sol(tt)
    T, C = sample(m, Y, tt, np.asarray([0.0]), add_surface=True)
    Cc, Tc = C[:, 0], T[:, 0]
    D_eff = m.Dfun(Cc, Tc)
    tau1 = m.Rmax ** 2 / (LAM1 ** 2 * D_eff) / 3600.0
    i_peak = int(np.argmax(D_eff))
    fig, ax = panel2(height=3.0)
    ax[0].semilogy(tt / 3600, D_eff, color=P.PURPLE, lw=1.8, label='$D(C_c, T_c)$')
    ax[0].scatter([tt[i_peak] / 3600], [D_eff[i_peak]], s=30, color=P.PURPLE, zorder=5)
    ax[0].annotate(f'升温加速(Arrhenius): 峰值 {D_eff[i_peak]:.2e} m²/s\n'
                   f'(t ≈ {tt[i_peak]/3600:.1f} h)',
                   xy=(tt[i_peak] / 3600, D_eff[i_peak]), xytext=(7, 2.2e-9),
                   fontsize=8.5, arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1))
    ax[0].annotate(f'自锁衰减(浓度依赖): 末段 {D_eff[-1]:.1e} m²/s\n'
                   f'(降 {D_eff.max()/D_eff[-1]:.0f} 倍)',
                   xy=(tt[-1] / 3600, D_eff[-1]), xytext=(28, 3.5e-9), fontsize=8.5,
                   arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1))
    ax[0].set_xlabel('时间 t / h')
    ax[0].set_ylabel('有效扩散系数 / (m²/s)')
    ax[0].set_title('(a) 中心处有效扩散系数')
    ax[0].set_xlim(0, 60)
    ax[0].legend(fontsize=8, loc='lower left')

    ax[1].plot(tt / 3600, tau1, color=P.OLIVE, lw=1.8,
               label=r'$\tau_1 = R^2/(\lambda_1^2 D_{\rm eff})$')
    ax[1].axhline(tau1[0], color=P.C_REF, ls='--', lw=1.2,
                  label=f'初值 {tau1[0]:.2f} h')
    ax[1].scatter([tt[-1] / 3600], [tau1[-1]], s=30, color=P.OLIVE, zorder=5)
    ax[1].annotate(f'末段 τ₁ ≈ {tau1[-1]:.0f} h\n("越烘越慢"的时间尺度)',
                   xy=(tt[-1] / 3600, tau1[-1]), xytext=(33, 16), fontsize=8.5,
                   arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1))
    ax[1].set_xlabel('时间 t / h')
    ax[1].set_ylabel('基模时间常数 / h')
    ax[1].set_title('(b) 基模时间常数(自锁效应)')
    ax[1].set_xlim(0, 60)
    ax[1].set_ylim(0, 26)
    ax[1].legend(fontsize=8, loc='upper left')
    for a in ax:
        a.grid(alpha=.3, which='both')
    save(fig, 'fig04_selflock.png')


# --------------------------------------------------------------------------
# fig05 与问题4 交叉校验: 中心水分浓度对比(约 37 h 处交叉)
# --------------------------------------------------------------------------
def fig05_cross_p4():
    m3 = M.DryingModel(3, N=400)
    te3, sol3 = solve3(m3)
    m4 = M.DryingModel(4, N=400)
    te4, sol4 = solve3(m4)
    tt = np.arange(0.0, min(te3, te4) + 1e-9, 600.0)
    Y3 = sol3.sol(tt)
    Y4 = sol4.sol(tt)
    C3 = sample(m3, Y3, tt, np.asarray([0.0]), add_surface=False)[1][:, 0]
    C4 = sample(m4, Y4, tt, np.asarray([0.0]), add_surface=False)[1][:, 0]
    diff = C3 - C4
    i = np.argwhere(diff[:-1] * diff[1:] < 0)
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    ax.plot(tt / 3600, C3, color=P.BLUE, lw=1.8, label='问题3(不考虑收缩)')
    ax.plot(tt / 3600, C4, color=P.RED, lw=1.8, label='问题4(考虑收缩, 附录4)')
    ax.axhline(C_END, color=P.C_THRESH, ls='--', lw=1.5, label='烘干判据 0.15 kg/kg')
    ax.axvline(te4 / 3600, color=P.RED, ls=':', lw=1.2)
    ax.axvline(te3 / 3600, color=P.BLUE, ls=':', lw=1.2)
    if len(i):
        k = int(i[0][0])
        tc = tt[k] + (tt[k + 1] - tt[k]) * abs(diff[k]) / (abs(diff[k]) + abs(diff[k + 1]))
        ax.scatter([tc / 3600], [np.interp(tc, tt, C3)], s=40, color=P.C_REF, zorder=6)
        ax.annotate(f'交叉 ≈ {tc/3600:.1f} h\n(前期: 问题4 更慢 — 初态 D 小 5.4 倍)\n'
                    f'(后期: 问题4 更快 — 1/R² 放大 2.79 倍 + 浓度依赖更弱)',
                    xy=(tc / 3600, np.interp(tc, tt, C3)), xytext=(12, 1.0), fontsize=8.5,
                    arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1))
    ax.annotate(f'问题4 结束 {te4/3600:.4f} h', xy=(te4 / 3600, 0.4), xytext=(te4 / 3600 - 13, 0.42),
                fontsize=8, color=P.RED)
    ax.annotate(f'问题3 结束 {te3/3600:.4f} h', xy=(te3 / 3600, 0.15), xytext=(te3 / 3600 - 12, 0.22),
                fontsize=8, color=P.BLUE)
    ax.set_xlabel('时间 t / h')
    ax.set_ylabel('中心水分浓度 / (kg/kg)')
    ax.set_title('交叉校验: 问题3 与问题4 的中心水分浓度')
    ax.set_xlim(0, 60)
    ax.grid(alpha=.3)
    ax.legend(fontsize=8, loc='upper right')
    save(fig, 'fig05_cross_p4.png')


# --------------------------------------------------------------------------
# fig06 烘干时间网格收敛: log-log + 二阶参考(Richardson 基准)
# --------------------------------------------------------------------------
def fig06_convergence():
    vals = {}
    for N in (100, 200, 400, 800):
        mn = M.DryingModel(3, N=N)
        teN, _ = solve3(mn)
        vals[N] = teN
    rich = vals[800] + (vals[800] - vals[400]) / 3.0
    Ns = np.array([100, 200, 400, 800])
    err = np.array([abs(vals[N] - rich) for N in Ns])
    p = np.log2(abs(vals[100] - vals[200]) / abs(vals[200] - vals[400]))
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    ax.loglog(Ns, err, 'o-', lw=1.8, ms=5, color=P.C_CENTER,
              label='烘干时间误差(相对 Richardson 基准)')
    ax.loglog(Ns, err[1] * (Ns / Ns[1]) ** -2.0, '--', lw=1.4, color=P.C_REF,
              label='二阶参考 $\\propto N^{-2}$')
    ax.annotate(f'N=400 误差 ≈ {err[2]:.0f} s(相对 {err[2]/vals[400]*100:.3f}%)\n'
                f'观测收敛阶 ≈ {p:.2f}(末端慢动力学 + 时间容差底噪)\n'
                f'按 p=1.4~2 外推误差均 ≤ 50 s',
                xy=(Ns[2], err[2]), xytext=(125, 3.5), fontsize=8.5,
                arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1))
    ax.set_xlabel('网格数 N')
    ax.set_ylabel('烘干时间误差 / s')
    ax.set_title('烘干时间的网格收敛(N=400 误差 ≤ 50 s, 0.02%)')
    ax.grid(alpha=.3, which='both')
    ax.legend(fontsize=8, loc='lower left')
    save(fig, 'fig06_convergence.png')


# --------------------------------------------------------------------------
# fig07 水分质量守恒(全流程): 域积分 vs 边界通量积分 + 残差
# --------------------------------------------------------------------------
def fig07_conservation():
    trapz = getattr(np, 'trapezoid', None) or np.trapz
    m = M.DryingModel(3, N=400)
    te, sol = solve3(m)
    tt = np.concatenate([np.arange(0.0, 3600.0, 1.0), np.arange(3600.0, te + 1e-9, 60.0)])
    Y = sol.sol(tt)
    xi = m.xi_c
    Mt = (Y[1::2, :] * xi[:, None]).sum(axis=0) * m.dxi
    _, Cs = sample(m, Y, tt, np.asarray([0.0]), add_surface=True)
    flux = m.hm * (Cs[:, -1] - np.interp(tt, m.t_ch, m.C_ch)) / m.Rmax
    cum = np.concatenate([[0.0], np.cumsum((flux[1:] + flux[:-1]) / 2 * np.diff(tt))])
    resid = (Mt - Mt[0]) + cum
    fig, ax = panel2(height=2.7)
    ax[0].plot(tt / 3600, Mt, color=P.BLUE, lw=1.6, label='域积分 $\\tilde M(t)=\\int C\\,\\xi d\\xi$')
    ax[0].plot(tt / 3600, Mt[0] - cum, ls='--', lw=1.2, color=P.OLIVE,
               label='边界通量积分 $\\tilde M(0)-\\int q dt$')
    ax[0].set_xlabel('时间 t / h')
    ax[0].set_ylabel('归一化总水分 $\\tilde M$')
    ax[0].set_title('(a) 总水分(全流程)')
    ax[0].legend(fontsize=8, loc='upper right')
    ax[1].plot(tt / 3600, resid, color=P.RED, lw=1.4, label='守恒残差')
    ax[1].axhline(0, color=P.C_REF, ls='--', lw=.8)
    ax[1].annotate(f'最大 |残差| = {np.abs(resid).max():.1e}\n'
                   f'(相对 {np.abs(resid).max()/Mt[0]:.1e})',
                   xy=(tt[np.argmax(np.abs(resid))] / 3600, np.abs(resid).max()),
                   xytext=(8, np.abs(resid).max() * 0.55), fontsize=9)
    ax[1].set_xlabel('时间 t / h')
    ax[1].set_ylabel('残差')
    ax[1].set_title('(b) 守恒残差(首 1 h 按 1 s、其后 60 s 细网格积分)')
    ax[1].legend(fontsize=8)
    for a in ax:
        a.set_xlim(0, 58)
        a.grid(alpha=.3)
    save(fig, 'fig07_conservation.png')


# --------------------------------------------------------------------------
# fig08 干燥速率: (a) 平均含水率 (b) 干燥速率三阶段(预热加速 -> 降速 -> 自锁)
# --------------------------------------------------------------------------
def fig08_dryingrate():
    m = M.DryingModel(3, N=400)
    te, sol = solve3(m)
    tt = np.arange(0.0, te + 1e-9, 60.0)
    Y = sol.sol(tt)
    Mt = (Y[1::2, :] * m.xi_c[:, None]).sum(axis=0) * m.dxi
    T, C = sample(m, Y, tt, np.asarray([0.0]), add_surface=False)
    Cc, Tc = C[:, 0], T[:, 0]
    Cbar = Mt / Mt[0]
    rate = -np.gradient(Cbar, tt) * 3600.0            # 归一化干燥速率 [1/h]
    w = 30                                             # 30 min 滑动平均(60 s 采样)
    rate_s = np.convolve(rate, np.ones(w) / w, mode='same')
    rate_s = np.maximum(rate_s, 1e-6)
    tau1_end = m.Rmax ** 2 / (LAM1 ** 2 * float(m.Dfun(Cc[-1:], Tc[-1:])[0])) / 3600.0
    i_peak = int(np.argmax(rate_s))
    fig, ax = panel2(height=3.0)
    ax[0].plot(tt / 3600, Cbar, color=P.BLUE, lw=1.8,
               label=f'平均含水率(结束 {Cbar[-1]:.4f})')
    ax[0].scatter([tt[i_peak] / 3600], [Cbar[i_peak]], s=30, color=P.BLUE, zorder=5)
    ax[0].set_xlabel('时间 t / h')
    ax[0].set_ylabel('平均含水率 $\\bar C(t)$(归一化)')
    ax[0].set_title('(a) 平均含水率')
    ax[0].set_xlim(0, 60)
    ax[0].legend(fontsize=8, loc='upper right')

    ax[1].semilogy(tt / 3600, rate_s, color=P.GREEN, lw=1.5,
                   label='干燥速率(30 min 滑动平均)')
    ax[1].scatter([tt[i_peak] / 3600], [rate_s[i_peak]], s=30, color=P.GREEN, zorder=5)
    ax[1].annotate(f'预热平衡: 升温加速, 峰值 {rate_s[i_peak]:.3f} 1/h\n'
                   f'(t ≈ {tt[i_peak]/3600:.1f} h)',
                   xy=(tt[i_peak] / 3600, rate_s[i_peak]), xytext=(7, 3e-3), fontsize=8.5,
                   arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1))
    ax[1].annotate('恒温降速干燥\n(速率单调衰减)', xy=(20, 4e-4), xytext=(26, 4e-3),
                   fontsize=8.5, arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1))
    ax[1].annotate(f'末段自锁: 速率仅 {rate_s[-1]:.1e} 1/h\n'
                   f'(τ₁ → {tau1_end:.0f} h)',
                   xy=(tt[-1] / 3600, rate_s[-1]), xytext=(30, 2e-4), fontsize=8.5,
                   arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1))
    ax[1].set_xlabel('时间 t / h')
    ax[1].set_ylabel('干燥速率 / (1/h)')
    ax[1].set_title('(b) 干燥速率')
    ax[1].set_xlim(0, 60)
    ax[1].legend(fontsize=8, loc='lower left')
    for a in ax:
        a.grid(alpha=.3, which='both')
    save(fig, 'fig08_dryingrate.png')


FIGS = {'fig01': fig01_chamber, 'fig02': fig02_moist_map, 'fig03': fig03_drying_curve,
        'fig04': fig04_selflock, 'fig05': fig05_cross_p4, 'fig06': fig06_convergence,
        'fig07': fig07_conservation, 'fig08': fig08_dryingrate}


def main():
    sel = [s for s in sys.argv[1:] if s in FIGS] or list(FIGS)
    print(f'生成 {len(sel)} 张图 -> {HERE}')
    for k in sel:
        print(f'[{k}]')
        FIGS[k]()
    print('完成。')


if __name__ == '__main__':
    main()
