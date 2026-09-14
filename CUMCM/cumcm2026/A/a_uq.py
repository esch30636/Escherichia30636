# -*- coding: utf-8 -*-
"""A 题 —— 参数敏感性分析与不确定度传递 (问题3 / 问题4 的烘干时间)。

需要回答两个问题:
  (1) 烘干时间对哪些参数最敏感?            -> OAT 龙卷风图 + 弹性系数
  (2) 参数不确定时, 烘干时间的分布如何?      -> LHS 蒙特卡洛, 给出均值/分位数
  (3) “恒温干燥阶段烘房维持末值”这一建模假设的影响有多大? -> 情景分析

并行策略: 28 逻辑核 / 20 物理核, 18 个 worker 进程。
每个样本是一次完整的刚性 ODE 积分 (N=400 -> 800 维, BDF, ~3600 步)。
"""
import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ.setdefault(_v, '1')
import sys, json, time
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
import numpy as np
import multiprocessing as mp
import a_model as M

N = 400
CCRIT = 0.15
T_MAX = 400000.0
OUT = r'D:\CUMCM\A\out'
NWORK = 18


# --------------------------------------------------------------------------
def dry_time(prob, scales=None, shift=None, ccrit=CCRIT, N=N):
    """返回 max C 首次降到 ccrit 的时刻 (s)。"""
    m = M.DryingModel(prob, N=N, scales=scales, chamber_shift=shift)

    def ev(t, y):
        return y[1::2].max() - ccrit
    ev.terminal = True
    ev.direction = -1
    s = m.solve(T_MAX, events=[ev], rtol=1e-8, atol=1e-10, dense=False)
    if len(s.t_events[0]) == 0:
        return float('nan')
    return float(s.t_events[0][0])


def _job(a):
    prob, scales, shift = a
    return dry_time(prob, scales, shift)


# --------------------------------------------------------------------------
def main():
    t_start = time.time()
    print(f'worker 进程数 = {NWORK}, 网格 N = {N}, 判据 C < {CCRIT}\n')

    jobs, meta = [], []
    base = {}

    # ---------------- 基准 ----------------
    for prob in (3, 4):
        jobs.append((prob, None, None))
        meta.append(('base', prob, 0.0))
    res = []

    # ---------------- OAT: 单因子 ±20% / ±10% ----------------
    FACTORS = [('h', 0.20), ('hm', 0.20), ('D', 0.20), ('k', 0.20),
               ('rho', 0.10), ('cp', 0.10)]
    for name, rel in FACTORS:
        for sgn in (+1, -1):
            for prob in (3, 4):
                jobs.append((prob, {name: 1.0 + sgn * rel}, None))
                meta.append(('oat', prob, (name, sgn * rel)))

    # ---------------- 情景: 恒温干燥阶段烘房条件 ----------------
    SCEN = [('烘房 -5 degC', (0.0, -5.0, 0.0)),
            ('烘房 +5 degC', (0.0, +5.0, 0.0)),
            ('烘房 +10 degC', (0.0, +10.0, 0.0)),
            ('湿度 +0.02 kg/kg', (0.0, 0.0, +0.02)),
            ('湿度 -0.02 kg/kg', (0.0, 0.0, -0.02))]
    for lab, (_, dT, dC) in SCEN:
        for prob in (3, 4):
            jobs.append((prob, None, (dT, dC)))
            meta.append(('scen', prob, lab))

    print(f'OAT + 情景 共 {len(jobs)} 个求解 ...')
    t0 = time.time()
    with mp.Pool(NWORK) as pool:
        res = pool.map(_job, jobs, chunksize=1)
    print(f'  完成, {time.time()-t0:.1f} s\n')

    base = {p: res[i] for i, (k, p, m) in enumerate(meta) if k == 'base'}
    for p in (3, 4):
        print(f'  基准 问题{p}: t_dry = {base[p]:.1f} s = {base[p]/3600:.4f} h')

    # ---------------- 汇总 OAT ----------------
    oat = {3: {}, 4: {}}
    scen = {3: [], 4: []}
    for (k, p, m), v in zip(meta, res):
        if k == 'oat':
            name, delta = m
            oat[p].setdefault(name, {})[delta] = v
        elif k == 'scen':
            scen[p].append((m, v))

    print('\n' + '=' * 76)
    print('OAT 敏感性 (弹性系数 S = (Δt/t) / (Δp/p), 即参数变化 1% 引起烘干时间变化的 %)')
    print('=' * 76)
    print(f'{"参数":>6} {"扰动":>7} | {"问题3 t(h)":>11} {"Δt/t":>9} {"S":>7} '
          f'| {"问题4 t(h)":>11} {"Δt/t":>9} {"S":>7}')
    print('-' * 76)
    elast = {3: {}, 4: {}}
    for name, rel in FACTORS:
        for sgn in (+1, -1):
            line = f'{name:>6} {sgn*rel:>+7.0%} |'
            for p in (3, 4):
                v = oat[p][name][sgn * rel]
                dt = (v - base[p]) / base[p]
                s = dt / (sgn * rel)
                elast[p][name] = s
                line += f' {v/3600:>11.4f} {dt:>+9.2%} {s:>7.3f} |'
            print(line)
    print('-' * 76)
    print('(|S| > 1 表示烘干时间对该参数的变化被放大)')

    print('\n' + '=' * 76)
    print('情景分析: 恒温干燥阶段的烘房条件假设')
    print('=' * 76)
    print(f'{"情景":>20} | {"问题3 t(h)":>11} {"相对基准":>10} | {"问题4 t(h)":>11} {"相对基准":>10}')
    print('-' * 76)
    print(f'{"基准(维持末值)":>20} | {base[3]/3600:>11.4f} {"—":>10} | '
          f'{base[4]/3600:>11.4f} {"—":>10}')
    for p in (3, 4):
        pass
    for i, (lab, _) in enumerate(SCEN):
        v3, v4 = scen[3][i][1], scen[4][i][1]
        print(f'{lab:>20} | {v3/3600:>11.4f} {(v3-base[3])/base[3]:>+10.2%} | '
              f'{v4/3600:>11.4f} {(v4-base[4])/base[4]:>+10.2%}')

    # ---------------- 蒙特卡洛 (LHS) ----------------
    NS = 1000
    rng = np.random.default_rng(20260910)
    names = [f[0] for f in FACTORS]
    d = len(names)
    u = np.empty((NS, d))
    for j in range(d):
        u[:, j] = (rng.permutation(NS) + rng.random(NS)) / NS
    RANGE = {'h': (0.8, 1.2), 'hm': (0.8, 1.2), 'D': (0.85, 1.15),
             'k': (0.9, 1.1), 'rho': (0.95, 1.05), 'cp': (0.95, 1.05)}
    samples = []
    for i in range(NS):
        sc = {nm: float(RANGE[nm][0] + u[i, j] * (RANGE[nm][1] - RANGE[nm][0]))
              for j, nm in enumerate(names)}
        samples.append(sc)

    mc_jobs, mc_prob = [], []
    for i, sc in enumerate(samples):
        for prob in (3, 4):
            mc_jobs.append((prob, sc, None))
            mc_prob.append(prob)

    print(f'\n蒙特卡洛 (LHS) {NS} 组参数 × 2 个问题 = {len(mc_jobs)} 个求解 ...')
    t0 = time.time()
    with mp.Pool(NWORK) as pool:
        mc_res = pool.map(_job, mc_jobs, chunksize=4)
    print(f'  完成, {time.time()-t0:.1f} s')

    mc = {3: [], 4: []}
    for pr, v in zip(mc_prob, mc_res):
        mc[pr].append(v)
    mc = {p: np.array(v) for p, v in mc.items()}

    print('\n' + '=' * 76)
    print(f'蒙特卡洛结果 (N={NS})')
    print('=' * 76)
    corr = {}
    for p in (3, 4):
        v = mc[p] / 3600.0
        q = np.percentile(v, [5, 50, 95])
        print(f'  问题{p}: 均值 {v.mean():.3f} h  标准差 {v.std(ddof=1):.3f} h  '
              f'变异系数 {v.std(ddof=1)/v.mean():.2%}')
        print(f'          P05 {q[0]:.3f}  P50 {q[1]:.3f}  P95 {q[2]:.3f} h   '
              f'(95% 区间宽 {q[2]-q[0]:.3f} h)')
        corr[p] = {nm: float(np.corrcoef(
            [s[nm] for s in samples], v)[0, 1]) for nm in names}
    print('\n  各参数与烘干时间的相关系数 (线性相关强度):')
    print(f'  {"参数":>6} | {"问题3":>9} | {"问题4":>9}')
    print('  ' + '-' * 30)
    for nm in names:
        print(f'  {nm:>6} | {corr[3][nm]:>+9.3f} | {corr[4][nm]:>+9.3f}')

    out = dict(base_3=base[3], base_4=base[4], oat={str(k): v for k, v in oat.items()},
               elast={str(k): v for k, v in elast.items()},
               scen={str(k): v for k, v in scen.items()},
               mc={str(k): dict(mean_h=float((mc[k]/3600).mean()),
                                std_h=float((mc[k]/3600).std(ddof=1)),
                                p05=float(np.percentile(mc[k]/3600, 5)),
                                p50=float(np.percentile(mc[k]/3600, 50)),
                                p95=float(np.percentile(mc[k]/3600, 95)))
                   for k in (3, 4)},
               corr={str(k): v for k, v in corr.items()},
               n_workers=NWORK, n_mc=NS)
    with open(rf'{OUT}\uq.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f'\n已保存 {OUT}\\uq.json   总耗时 {time.time()-t_start:.1f} s')


if __name__ == '__main__':
    main()
