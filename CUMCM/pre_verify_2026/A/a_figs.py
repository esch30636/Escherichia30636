# -*- coding: utf-8 -*-
"""A 题 —— 论文插图 (运行在 legion, 输出到 out/fig/*.png)。"""
import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
import sys, json
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import a_model as M
from a_output import sample

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.bbox'] = 'tight'

N = 400
OUT = r'D:\CUMCM\A\out'
FIG = rf'{OUT}\fig'
RTOL, ATOL = 1e-8, 1e-10
CM = plt.cm.viridis


def drying_time(model, ccrit=0.15, t_max=400000.0):
    def ev(t, y):
        return y[1::2].max() - ccrit
    ev.terminal = True
    ev.direction = -1
    s = model.solve(t_max, events=[ev], rtol=RTOL, atol=ATOL, dense=False)
    return float(s.t_events[0][0]) if len(s.t_events[0]) else np.nan


def profiles(prob, times, t_end, dist, t_unit='s'):
    m = M.DryingModel(prob, N=N)
    sol = m.solve(t_end, rtol=RTOL, atol=ATOL)
    ts = np.asarray(times, float)
    Y = sol.sol(ts)
    T, C = sample(m, Y, ts, np.asarray(dist, float), add_surface=True)
    return m, ts, T - 273.15, C


def fig_profiles(prob, times, t_end, dist, labels, fname, title):
    m, ts, T, C = profiles(prob, times, t_end, dist)
    x = np.append(np.asarray(dist, float), m.Rmax * 100.0)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    for i, lab in enumerate(labels):
        c = CM(i / max(len(times) - 1, 1))
        ax[0].plot(x, T[i], 'o-', ms=3, lw=1.5, color=c, label=lab)
        ax[1].plot(x, C[i], 'o-', ms=3, lw=1.5, color=c, label=lab)
    ax[0].set_ylabel('温度 / °C')
    ax[1].set_ylabel('水分浓度 / (kg/kg)')
    for a, t in zip(ax, ('(a) 温度分布', '(b) 水分浓度分布')):
        a.set_xlabel('到药材中心的距离 / cm')
        a.grid(alpha=.3)
        a.set_title(t)
    ax[0].legend(fontsize=8)
    fig.suptitle(title, fontsize=12)
    fig.savefig(rf'{FIG}\{fname}')
    plt.close(fig)
    print('  ', fname)


def fig_drying():
    m3 = M.DryingModel(3, N=N)
    m4 = M.DryingModel(4, N=N)
    te3, te4 = drying_time(m3), drying_time(m4)
    fig, ax = plt.subplots(1, 3, figsize=(14.5, 4.2))

    for m, te, lab, ls in ((m3, te3, '问题3(不考虑收缩)', '-'), (m4, te4, '问题4(考虑收缩)', '--')):
        sol = m.solve(te, rtol=RTOL, atol=ATOL)
        t = np.linspace(0, te, 400)
        Y = sol.sol(t)
        C = Y[1::2, :]
        ax[0].plot(t / 3600, C.max(axis=0), ls, lw=2, label=lab + ' 最大')
        ax[1].plot(t / 3600, C[-1], ls, lw=2, label=lab + ' 表面')
        ax[1].plot(t / 3600, C[0], ls, lw=1.2, alpha=.6, label=lab + ' 中心')
    ax[0].axhline(0.15, color='r', lw=1.2, ls=':', label='判据 0.15')
    ax[0].set_ylabel('水分浓度 / (kg/kg)')
    ax[0].set_title('(a) 药材最大水分浓度')
    ax[1].set_ylabel('水分浓度 / (kg/kg)')
    ax[1].set_title('(b) 表面与中心水分浓度')
    for a in ax[:2]:
        a.set_xlabel('时间 / h')
        a.grid(alpha=.3)
        a.legend(fontsize=8)

    # 半径随时间变化
    tR, R = M.load_radius()
    ax[2].plot(tR / 3600, R * 100, 'k-', lw=2)
    for te, lab, c in ((te3, '问题3 结束', 'C0'), (te4, '问题4 结束', 'C3')):
        ax[2].axvline(te / 3600, color=c, ls='--', lw=1.5, label=lab)
    ax[2].set_xlabel('时间 / h')
    ax[2].set_ylabel('半径 / cm')
    ax[2].set_title('(c) 附件2 药材半径(收缩)')
    ax[2].grid(alpha=.3)
    ax[2].legend(fontsize=8)
    fig.savefig(rf'{FIG}\fig3_drying.png')
    plt.close(fig)
    print('   fig3_drying.png  te3=%.1fs te4=%.1fs' % (te3, te4))
    return te3, te4


def fig_boundary():
    t, T, C = M.load_chamber()
    fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.8))
    ax[0].plot(t / 3600, T - 273.15, 'r-', lw=2)
    ax[1].plot(t / 3600, C, 'b-', lw=2)
    for a, yl, tt in ((ax[0], '烘房温度 / °C', '(a) 附件1 烘房温度'),
                      (ax[1], '烘房水分浓度 / (kg/kg)', '(b) 附件1 烘房水分浓度')):
        a.axvline(4.0, color='gray', ls='--', lw=1.2)
        a.text(4.05, a.get_ylim()[0], ' 14400 s 后按末值维持\n (恒温干燥阶段假设)', fontsize=8)
        a.set_xlabel('时间 / h')
        a.set_ylabel(yl)
        a.set_title(tt)
        a.grid(alpha=.3)
    fig.tight_layout()
    fig.savefig(rf'{FIG}\fig_boundary.png')
    plt.close(fig)
    print('   fig_boundary.png')


def fig_convergence():
    Ns = np.array([50, 100, 200, 400, 800, 1600])
    te = []
    for n in Ns:
        m = M.DryingModel(3, N=int(n))
        te.append(drying_time(m))
    te = np.array(te)
    ref = te[-1] + (te[-1] - te[-2]) / 3
    err = np.abs(te - ref)
    fig, ax = plt.subplots(figsize=(5.6, 4.0))
    ax.loglog(Ns, err, 'o-', lw=2, ms=5, label='实际误差')
    ax.loglog(Ns, err[-2] * (Ns / Ns[-2]) ** -2.0, 'k--', lw=1.5, label='二阶参考 $N^{-2}$')
    ax.set_xlabel('网格数 N')
    ax.set_ylabel('烘干时间误差 / s')
    ax.set_title('问题3 烘干时间的网格收敛性')
    ax.grid(alpha=.3, which='both')
    ax.legend(fontsize=9)
    fig.savefig(rf'{FIG}\fig_convergence.png')
    plt.close(fig)
    print('   fig_convergence.png  te=%s' % np.round(te, 1))


def fig_tornado():
    p = rf'{OUT}\uq.json'
    if not os.path.exists(p):
        print('   (跳过 tornado: uq.json 尚未生成)')
        return
    with open(p, encoding='utf-8') as f:
        uq = json.load(f)
    # 与 a_uq.py 的 FACTORS 一致: 扰动幅度
    REL = {'h': 0.20, 'hm': 0.20, 'D': 0.20, 'k': 0.20, 'rho': 0.10, 'cp': 0.10}
    names = ['h', 'hm', 'D', 'k', 'rho', 'cp']
    zh = {'h': '$h$ 对流换热', 'hm': '$h_m$ 对流传质', 'D': '$D$ 扩散系数',
          'k': '$k$ 导热系数', 'rho': r'$\rho$ 密度', 'cp': '$c_p$ 比热容'}
    fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.2))
    for j, prob in enumerate(('3', '4')):
        base = uq[f'base_{prob}']
        vals = []
        for nm in names:
            rel = REL[nm]
            o = uq['oat'][prob][nm]
            d_hi = (o[f'{rel:.1f}'] - base) / base        # +rel 扰动
            d_lo = (o[f'{-rel:.1f}'] - base) / base       # -rel 扰动
            vals.append((zh[nm], min(d_hi, d_lo), max(d_hi, d_lo), rel))
        # 按影响幅度升序排序 -> 影响最大的画在最上方
        vals.sort(key=lambda z: abs(z[2] - z[1]))
        y = np.arange(len(vals))
        lo = np.array([v[1] for v in vals])
        hi = np.array([v[2] for v in vals])
        ax[j].barh(y, hi - lo, left=lo, color='#3b6ea5', height=.6)
        ax[j].set_yticks(y)
        ax[j].set_yticklabels([f'{v[0]} (±{v[3]*100:.0f}%)' for v in vals], fontsize=8.5)
        ax[j].axvline(0, color='k', lw=.8)
        ax[j].set_xlabel('烘干时间的相对变化 $\\Delta t/t$')
        ax[j].set_title(f'({"ab"[j]}) 问题{prob} 烘干时间的单因子敏感度')
        ax[j].grid(alpha=.3, axis='x')
    fig.tight_layout()
    fig.tight_layout()
    fig.savefig(rf'{FIG}\fig_tornado.png')
    plt.close(fig)
    print('   fig_tornado.png')


def main():
    os.makedirs(FIG, exist_ok=True)
    print('生成插图 ->', FIG)

    fig_boundary()

    d1 = [0.0, 0.5, 1.0, 1.5]
    t1 = [100, 300, 600, 900, 1200, 1500, 1800]
    fig_profiles(1, t1, 1800.0, d1,
                 [f'{t} s' for t in t1], 'fig1_p1.png',
                 '问题1 预热平衡阶段: 温度与水分浓度分布')
    fig_profiles(2, [1800, 3600, 5400, 7200, 9000, 10800], 10800.0, d1,
                 [f'{t/3600:.1f} h' for t in [1800, 3600, 5400, 7200, 9000, 10800]],
                 'fig2_p2.png', '问题2 前 3 小时: 温度与水分浓度分布')

    fig_drying()
    fig_convergence()
    fig_tornado()
    print('完成。')


if __name__ == '__main__':
    main()
