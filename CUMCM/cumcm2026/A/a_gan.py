# -*- coding: utf-8 -*-
"""A 题 —— GAN 烘房环境情景生成与烘干时间传播 (WGAN-GP)。

背景: 问题3/4 的积分区间 (57 h / 51 h) 远超附件1 的 4 h 实测,
「恒温干燥阶段烘房维持末值」是全场最大建模假设 (±5 °C -> 干时 ∓14.6%/+18.2%)。
本脚本用 WGAN-GP 学习附件1 恒温段(后 2 h)温湿度偏差的联合分布与短时相关,
生成随机情景轨迹, 经 FVM 求解器传播得到烘干时间分布, 把该假设的影响
从「常数偏移的保守界」升级为「数据驱动的随机波动量化」, 并与两个基线
(块自助 / 参数化) 交叉校验。

实测恒温段统计特征: 温度偏差 ~ i.i.d. (水平 lag-1 自相关≈0.08,
差分 lag-1≈−0.53); 湿度偏差持续型 AR(1) (水平 lag-1≈0.72)。
GAN 必须复现这两个特征, 训练后自动校验。

用法:
  python a_gan.py train             # 训练 WGAN-GP -> out/gan_env.pt
  python a_gan.py gen --n 200       # 生成情景 + 基线 -> out/gan_scen.npz
  python a_gan.py prop --n 200      # FVM 传播(18 worker) -> out/gan_uq.json
"""
import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ.setdefault(_v, '1')
import sys, json, time, argparse
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
import numpy as np
import multiprocessing as mp
import a_model as M

OUT = r'D:\CUMCM\A\out'
DT = 60.0                 # 附件1 采样间隔 (s)
T_MEAS = 14400.0          # 实测时长 (s)
T_GEN = 220000.0          # 生成时长 (s), 覆盖问题3(206 ks)/4(183 ks)
WIN = 30                  # 训练窗口 (min)
OVL = 10                  # 拼接重叠 (min)
LATENT = 16
N_ITER = 4000
BATCH = 64
GP_LAMBDA = 10.0
MOMENT_LAMBDA = 2.0
NCRIT = 5
CCRIT = 0.15
N_FVM = 400
T_MAX = 400000.0
NWORK = 24
STEP = 5                  # 尾段传播采样 (5×60 s = 300 s)


# --------------------------------------------------------------------------
# 数据准备
# --------------------------------------------------------------------------
def load_deviations():
    """恒温段(后 2 h)线性去趋势后的偏差, (n,2) = [dT(degC), dC(kg/kg)]."""
    t, T, C = M.load_chamber()
    T = T - 273.15
    m = t >= T_MEAS - 7200.0
    tt, TT, CC = t[m], T[m], C[m]
    aT, bT = np.polyfit(tt, TT, 1)
    aC, bC = np.polyfit(tt, CC, 1)
    res = np.stack([TT - (aT * tt + bT), CC - (aC * tt + bC)], axis=1)
    return res


def make_windows(X, win=WIN):
    return np.stack([X[i:i + win] for i in range(len(X) - win + 1)])


# --------------------------------------------------------------------------
# WGAN-GP (torch 惰性导入, prop 模式不需要)
# --------------------------------------------------------------------------
def _build_gan(win, std):
    import torch
    import torch.nn as nn
    W = win * 2

    class Gen(nn.Module):
        def __init__(self):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(LATENT, 128), nn.ReLU(),
                nn.Linear(128, 128), nn.ReLU(),
                nn.Linear(128, W))          # 线性输出: tanh 会把幅值限在 ±1σ, 削掉极值

        def forward(self, z):
            return self.net(z).view(-1, win, 2)

    class Disc(nn.Module):
        def __init__(self):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(W, 128), nn.LeakyReLU(0.2),
                nn.Linear(128, 128), nn.LeakyReLU(0.2),
                nn.Linear(128, 1))

        def forward(self, x):
            return self.net(x.view(x.size(0), -1))

    return Gen(), Disc()


def train_mode():
    import torch

    def _corr(a, b):
        a = a - a.mean()
        b = b - b.mean()
        return (a * b).mean() / (a.std() * b.std() + 1e-9)

    def _batch_stats(x):
        """(B,win,2) -> [sT, sC, T差分lag1, C水平lag1, corr(T,C)] 可微统计量。

        逐窗口去均值后再求相关/标准差, 再跨窗口平均: 全局去均值会把窗口间
        漂移混入, 稀释真实相关 (实测 C lag-1 0.54 -> 0.33)。"""
        sT = x[:, :, 0].std(dim=1).mean()
        sC = x[:, :, 1].std(dim=1).mean()
        dT = x[:, 1:, 0] - x[:, :-1, 0]
        dm = dT - dT.mean(dim=1, keepdim=True)
        c1 = ((dm[:, :-1] * dm[:, 1:]).mean(dim=1)
              / (dm[:, :-1].std(dim=1) * dm[:, 1:].std(dim=1) + 1e-9)).mean()
        Tm = x[:, :, 0] - x[:, :, 0].mean(dim=1, keepdim=True)
        Cm = x[:, :, 1] - x[:, :, 1].mean(dim=1, keepdim=True)
        cC = ((Cm[:, :-1] * Cm[:, 1:]).mean(dim=1)
              / (Cm[:, :-1].std(dim=1) * Cm[:, 1:].std(dim=1) + 1e-9)).mean()
        jc = ((Tm * Cm).mean(dim=1)
              / (Tm.std(dim=1) * Cm.std(dim=1) + 1e-9)).mean()
        return torch.stack([sT, sC, c1, cC, jc])

    torch.manual_seed(2026)
    np.random.seed(2026)
    X = load_deviations()                    # (121, 2)
    W = make_windows(X)                      # (92, 30, 2)
    std = W.reshape(-1, 2).std(0)
    Xn = W / std
    print(f'训练集: {len(Xn)} 个窗口 × {WIN} min × 2 通道, 归一化 std = '
          f'T {std[0]:.4f} degC, C {std[1]:.2e} kg/kg')
    G, D = _build_gan(WIN, std)
    optG = torch.optim.Adam(G.parameters(), lr=1e-4, betas=(0.0, 0.9))
    optD = torch.optim.Adam(D.parameters(), lr=1e-4, betas=(0.0, 0.9))
    data = torch.from_numpy(Xn.astype(np.float32))
    tgt = _batch_stats(data).detach()        # 二阶统计目标 (实测)
    print('  统计目标: sT %.3f  sC %.3f  T差分l1 %+.3f  C水平l1 %+.3f  '
          'corr(T,C) %+.3f' % tuple(tgt.tolist()))
    t0 = time.time()
    for it in range(N_ITER):
        for _ in range(NCRIT):
            idx = torch.randint(len(data), (BATCH,))
            real = data[idx]
            z = torch.randn(BATCH, LATENT)
            fake = G(z).detach()
            # 小样本平滑增广: 2% 标准差噪声, 防生成器记忆训练窗
            real = real + 0.02 * torch.randn_like(real)
            eps = torch.rand(BATCH, 1, 1)
            xhat = (eps * real + (1 - eps) * fake).requires_grad_(True)
            gp = ((torch.autograd.grad(D(xhat).sum(), xhat,
                                       create_graph=True)[0]
                   .view(BATCH, -1).norm(2, 1) - 1) ** 2).mean()
            lossD = D(fake).mean() - D(real).mean() + GP_LAMBDA * gp
            optD.zero_grad()
            lossD.backward()
            optD.step()
        z = torch.randn(BATCH, LATENT)
        fake = G(z)
        # 矩匹配正则: 直接惩罚二阶统计偏差 (小样本下保证 T i.i.d. / C AR(1)
        # 特征与 T-C 耦合被复现, 这是判别器不直接约束的)
        lossG = -D(fake).mean() + MOMENT_LAMBDA * ((_batch_stats(fake) - tgt) ** 2).mean()
        optG.zero_grad()
        lossG.backward()
        optG.step()
        if (it + 1) % 500 == 0:
            st = _batch_stats(G(torch.randn(BATCH, LATENT)).detach()).tolist()
            print(f'  iter {it + 1}/{N_ITER}  lossD {lossD.item():+.3f}  '
                  f'lossG {lossG.item():+.3f}  stats {st[0]:.3f}/{st[1]:.3f}/'
                  f'{st[2]:+.2f}/{st[3]:+.2f}/{st[4]:+.2f}  '
                  f'({time.time() - t0:.0f} s)')
    torch.save({'G': G.state_dict(), 'std': std, 'win': WIN,
                'latent': LATENT}, rf'{OUT}\gan_env.pt')
    print(f'已保存 {OUT}\\gan_env.pt  (训练 {time.time() - t0:.0f} s)')


# --------------------------------------------------------------------------
# 情景生成 (GAN + 两个基线) 与统计校验
# --------------------------------------------------------------------------
def gen_mode(n):
    import torch
    torch.manual_seed(2026)
    ck = torch.load(rf'{OUT}\gan_env.pt', map_location='cpu', weights_only=False)
    G, _ = _build_gan(ck['win'], ck['std'])
    G.load_state_dict(ck['G'])
    G.eval()
    std = ck['std']
    X = load_deviations()
    n_steps = int((T_GEN - T_MEAS) / DT) + 1

    def gen_traj():
        """逐窗生成 + OVL 步线性交叉淡化拼接。"""
        nwin = int(np.ceil((n_steps - OVL) / (WIN - OVL)))
        z = torch.randn(nwin, LATENT)
        W = (G(z).detach().numpy() * std).astype(float)
        traj = np.zeros((n_steps, 2))
        for k in range(nwin):
            st = k * (WIN - OVL)
            if st >= n_steps:
                break
            seg = W[k][:n_steps - st]
            L = len(seg)
            ovl = min(OVL, L)
            wgt = np.linspace(0.0, 1.0, ovl)[:, None]
            if k == 0:
                traj[st:st + L] = seg
            else:
                traj[st:st + ovl] = (traj[st:st + ovl] * (1 - wgt)
                                     + seg[:ovl] * wgt)
                if L > ovl:
                    traj[st + ovl:st + L] = seg[ovl:]
        return traj

    rng = np.random.default_rng(2026)

    def traj_boot():
        """块自助基线: 循环重采样 10 min 块, 保留短时相关。"""
        block = 10
        out = np.empty((n_steps, 2))
        k = 0
        nn = len(X)
        while k < n_steps:
            i = rng.integers(0, nn - block + 1)
            seg = X[i:i + block]
            m = min(len(seg), n_steps - k)
            out[k:k + m] = seg[:m]
            k += m
        return out

    def traj_param():
        """参数化基线: T ~ i.i.d. N(0,sT); C ~ AR(1) (rho=水平 lag-1 自相关)。"""
        sT = X[:, 0].std()
        sC = X[:, 1].std()
        rho = np.corrcoef(X[:-1, 1], X[1:, 1])[0, 1]
        out = np.empty((n_steps, 2))
        out[:, 0] = rng.normal(0.0, sT, n_steps)
        e = rng.normal(0.0, sC * np.sqrt(1 - rho ** 2), n_steps)
        c = 0.0
        for i in range(n_steps):
            c = rho * c + e[i]
            out[i, 1] = c
        return out

    print(f'生成 {n} 条 {T_GEN / 3600:.0f} h 轨迹 (n_steps={n_steps}) ...')
    t0 = time.time()
    gan = np.stack([gen_traj() for _ in range(n)])
    boot = np.stack([traj_boot() for _ in range(n)])
    param = np.stack([traj_param() for _ in range(n)])
    print(f'  完成, {time.time() - t0:.1f} s')
    np.savez(rf'{OUT}\gan_scen.npz', gan=gan, boot=boot, param=param,
             n_steps=n_steps)
    print(f'已保存 {OUT}\\gan_scen.npz')

    # ---------------- 统计校验: 生成 vs 实测 ----------------
    def stats(Y, name):
        YT = Y[:, :, 0]
        YC = Y[:, :, 1]
        dT = np.diff(YT, axis=1)
        lvl = [np.corrcoef(YT[i, :-1], YT[i, 1:])[0, 1] for i in range(len(YT))]
        dl1 = [np.corrcoef(dT[i, :-1], dT[i, 1:])[0, 1] for i in range(len(dT))]
        cl1 = [np.corrcoef(YC[i, :-1], YC[i, 1:])[0, 1] for i in range(len(YC))]
        jc = [np.corrcoef(YT[i], YC[i])[0, 1] for i in range(len(YT))]
        rngT = (YT.max(1) - YT.min(1)).mean()
        rngC = (YC.max(1) - YC.min(1)).mean()
        print(f'  {name:>5}: sT {YT.std():.4f}  sC {YC.std():.2e} | '
              f'T 水平l1 {np.mean(lvl):+.3f}  差分l1 {np.mean(dl1):+.3f} | '
              f'C 水平l1 {np.mean(cl1):+.3f} | corr(T,C) {np.mean(jc):+.3f} | '
              f'平均极差 T {rngT:.3f} degC  C {rngC:.2e}')

    t, T, C = M.load_chamber()
    T = T - 273.15
    m = t >= T_MEAS - 7200.0
    tt, TT, CC = t[m], T[m], C[m]
    aT, bT = np.polyfit(tt, TT, 1)
    aC, bC = np.polyfit(tt, CC, 1)
    Xr = np.stack([TT - (aT * tt + bT), CC - (aC * tt + bC)], axis=1)
    dTr = np.diff(Xr[:, 0])
    print('  实测: sT %.4f  sC %.2e | T 水平l1 %+.3f  差分l1 %+.3f | '
          'C 水平l1 %+.3f | corr(T,C) %+.3f | 极差 T %.3f degC  C %.2e'
          % (Xr[:, 0].std(), Xr[:, 1].std(),
             np.corrcoef(Xr[:-1, 0], Xr[1:, 0])[0, 1],
             np.corrcoef(dTr[:-1], dTr[1:])[0, 1],
             np.corrcoef(Xr[:-1, 1], Xr[1:, 1])[0, 1],
             np.corrcoef(Xr[:, 0], Xr[:, 1])[0, 1],
             Xr[:, 0].max() - Xr[:, 0].min(),
             Xr[:, 1].max() - Xr[:, 1].min()))
    stats(gan, 'GAN')
    stats(boot, 'boot')
    stats(param, 'param')
    print('(T 差分 lag-1 ≈ −0.5 = i.i.d. 水平; C 水平 lag-1 ≈ 0.7 = AR(1) 持续)')
    print('(平均极差: 57 h 长轨迹的极值偏移, 体现长时程波动积累)')


# --------------------------------------------------------------------------
# FVM 传播
# --------------------------------------------------------------------------
def dry_time(prob, series):
    """返回 max C 首次降到 ccrit 的时刻 (s)。series = (t, T[K], C)。"""
    m = M.DryingModel(prob, N=N_FVM, chamber_series=series)

    def ev(t, y):
        return y[1::2].max() - CCRIT
    ev.terminal = True
    ev.direction = -1
    s = m.solve(T_MAX, events=[ev], rtol=1e-8, atol=1e-10, dense=False)
    if len(s.t_events[0]) == 0:
        return float('nan')
    return float(s.t_events[0][0])


def _job(a):
    return dry_time(*a)


def prop_mode(n):
    d = np.load(rf'{OUT}\gan_scen.npz')
    n_steps = int(d['n_steps'])
    t_meas, T_meas, C_meas = M.load_chamber()
    t_meas = np.asarray(t_meas, float)
    T_meas = np.asarray(T_meas, float)          # K
    C_meas = np.asarray(C_meas, float)
    # 尾段从 14400+300 s 起, 按 STEP×60=300 s 采样: 烘干热/湿时间常数 ~1 h,
    # 亚小时波动被系统滤波; 60 s 全采样 ×3427 跳变点令 BDF 每点重启 -> 单求解 152 s,
    # 300 s 采样保留全部有效统计结构, 求解降到 ~40 s (实测段 60 s 原样保留)。
    j = np.arange(1, n_steps // STEP + 1)          # 1..685
    t_tail = T_MEAS + DT * STEP * j                # 14700 .. 219900 s
    base_series = (t_meas, T_meas, C_meas)      # 维持末值基准 (interp 自动外推)

    def series_of(traj):
        # T_meas 已是 K (load_chamber 加了 273.15), traj 是 °C 偏差, 直接相加
        T_tail = T_meas[-1] + traj[STEP * j, 0]
        C_tail = np.clip(C_meas[-1] + traj[STEP * j, 1], 0.0, None)
        return (np.concatenate([t_meas, t_tail]),
                np.concatenate([T_meas, T_tail]),
                np.concatenate([C_meas, C_tail]))

    jobs, meta = [], []
    jobs.append((3, base_series))
    meta.append(('hold', 3))
    jobs.append((4, base_series))
    meta.append(('hold', 4))
    for src, arr in (('gan', d['gan']), ('boot', d['boot']), ('param', d['param'])):
        for i in range(len(arr)):
            s = series_of(arr[i])
            for p in (3, 4):
                jobs.append((p, s))
                meta.append((src, p))
    print(f'共 {len(jobs)} 个求解 (N={N_FVM}, {NWORK} worker, 尾段 {STEP * DT:.0f} s 采样) ...')
    t0 = time.time()
    with mp.Pool(NWORK) as pool:
        res = pool.map(_job, jobs, chunksize=4)
    print(f'  完成, {time.time() - t0:.1f} s')

    by = {}
    for (src, p), v in zip(meta, res):
        by.setdefault((src, p), []).append(v)
    hold = {p: by[('hold', p)][0] for p in (3, 4)}

    # ---------------- 汇总 ----------------
    out = {'hold_h': {str(p): hold[p] / 3600.0 for p in (3, 4)}}
    print('\n' + '=' * 92)
    print('烘干时间分布: GAN 波动情景 vs 基线 (小时)')
    print('=' * 92)
    print(f'{"情景源":>7} | {"问题3 均值±std":>17} {"P05":>8} {"P95":>8} '
          f'{"Δ均值/维持":>11} | {"问题4 均值±std":>17} {"P05":>8} {"P95":>8} '
          f'{"Δ均值/维持":>11}')
    print('-' * 92)
    for src in ('hold', 'gan', 'boot', 'param'):
        line = f'{src:>7} |'
        for p in (3, 4):
            v = np.array(by[(src, p)]) / 3600.0
            if src == 'hold':
                line += f' {v[0]:>10.4f} {"—":>6} {"—":>8} {"—":>8} {"—":>11} |'
                out[f'{src}_{p}'] = float(v[0])
            else:
                m_, s_ = v.mean(), v.std(ddof=1)
                q05, q95 = np.percentile(v, [5, 95])
                dlt = (v.mean() - hold[p] / 3600.0) / (hold[p] / 3600.0)
                line += f' {m_:>10.4f}±{s_:.4f} {q05:>8.4f} {q95:>8.4f} '
                line += f'{dlt:>+11.2%} |'
                out[f'{src}_{p}'] = dict(mean_h=float(m_), std_h=float(s_),
                                         p05=float(q05), p95=float(q95),
                                         dmean_vs_hold=float(dlt),
                                         raw_h=v.tolist())
        print(line)
    print('-' * 92)

    # 与既有 LHS 参数不确定性、±5 °C 情景对比
    try:
        with open(rf'{OUT}\uq.json', encoding='utf-8') as f:
            uq = json.load(f)
        print('\n对照 (uq.json):')
        for p in (3, 4):
            mc = uq['mc'][str(p)]
            print(f'  LHS 参数不确定性 问题{p}: {mc["mean_h"]:.3f} ± '
                  f'{mc["std_h"]:.3f} h  (P95 {mc["p95"]:.3f})')
        print('  ±5 °C 情景: 问题3 ∓14.6%/+18.2%, 问题4 同量级 (见 uq.json scen)')
    except Exception as e:
        print(f'\n(未读 uq.json: {e})')

    with open(rf'{OUT}\gan_uq.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f'\n已保存 {OUT}\\gan_uq.json')

    # ---------------- 图 ----------------
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
        ax = axes[0]
        T_c = T_meas - 273.15
        ax.plot(t_meas / 3600.0, T_c, 'k-', lw=1.2, label='measured (4 h)')
        for i in range(min(40, len(d['gan']))):
            s = series_of(d['gan'][i])
            ax.plot(s[0] / 3600.0, s[1] - 273.15, color='tab:blue',
                    alpha=0.10, lw=0.5)
        s = series_of(d['gan'][0])
        ax.plot(s[0] / 3600.0, s[1] - 273.15, color='tab:blue', lw=0.8,
                label='GAN scenarios (tail)')
        ax.set_xlabel('time (h)')
        ax.set_ylabel('chamber T (degC)')
        ax.set_title('(a) Chamber temperature: measured + GAN scenarios')
        ax.legend(fontsize=8)
        ax.set_xlim(0, 60)
        ax = axes[1]
        for p, c, lab in ((3, 'tab:green', 'P3'), (4, 'tab:red', 'P4')):
            v = np.array(by[('gan', p)]) / 3600.0
            ax.hist(v, bins=30, alpha=0.5, color=c,
                    label=f'{lab} GAN (n={len(v)})')
            ax.axvline(hold[p] / 3600.0, color=c, ls='--', lw=1.2,
                       label=f'{lab} hold-final')
        ax.set_xlabel('drying time (h)')
        ax.set_title('(b) Drying time under GAN scenarios')
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(rf'{OUT}\gan_fig.png', dpi=130)
        print(f'已保存 {OUT}\\gan_fig.png')
    except Exception as e:
        print(f'(图生成失败: {e})')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=('train', 'gen', 'prop'))
    ap.add_argument('--n', type=int, default=200)
    args = ap.parse_args()
    if args.mode == 'train':
        train_mode()
    elif args.mode == 'gen':
        gen_mode(args.n)
    else:
        prop_mode(args.n)
