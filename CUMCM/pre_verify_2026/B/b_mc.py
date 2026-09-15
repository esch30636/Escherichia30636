# -*- coding: utf-8 -*-
"""B 题 问题3/4 蒙特卡洛演练统计 (在 legion 上跑)。

每个案例: 随机生成场景 -> SimClient 进程内直连自研环境 -> 策略运行 -> 统计。
统计量(与题目演练要求一致):
  * 被清除干扰源个数比例 = 被清除个数 / 干扰源总数 (期望 100%)
  * 平均定位清除时间 = 定位清除总时间 / 被清除干扰源个数
     (含移动、频道切换、检测、光学精确定位与清除等全部时间, 即虚拟总时间)
输出: out/b_p3_mc.json / out/b_p4_mc.json
用法: python b_mc.py --problem 3 --n 400 --seed 2026 [--verbose]
"""
import sys
import os
import json
import time
import argparse

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
import numpy as np

from b_sim import SimWorld, gen_scenario
from b_robot import Strategy, SimClient

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')


def run_batch(problem, n, seed, p_dir=0.5, verbose=False):
    mixed = problem == 4
    rng = np.random.default_rng(seed)
    seeds = rng.integers(0, 2 ** 31 - 1, size=n)
    ratios, avg_times, totals, sweeps = [], [], [], []
    n_srcs, fail_runs, homing_fails = [], [], 0
    per_source_times = []               # 每个源的清除虚拟时刻(分布直方图用)
    for i, sd in enumerate(seeds):
        scenario = gen_scenario(seed=int(sd), mixed=mixed, p_dir=p_dir)
        world = SimWorld(scenario, seed=int(sd))
        st = Strategy(SimClient(world), problem=problem)
        res = st.run()
        ns = len(scenario)
        ratios.append(res['n_cleared'] / ns)
        avg_times.append(res['total_virtual_time_s'] / max(res['n_cleared'], 1))
        totals.append(res['total_virtual_time_s'])
        sweeps.append(res['sweep_time_s'])
        n_srcs.append(ns)
        per_source_times.extend(res['per_source'].values())
        if res['n_cleared'] < ns:
            fail_runs.append(dict(seed=int(sd), cleared=res['n_cleared'], n=ns,
                                  total=res['total_virtual_time_s']))
            if verbose:
                print(f'  !! seed={sd}: 只清除 {res["n_cleared"]}/{ns}')
        if verbose and (i + 1) % 50 == 0:
            print(f'  {i + 1}/{n} 完成, 用时 {time.time() - t0:.1f}s')
    t1 = time.time()
    ratios = np.array(ratios)
    avg_times = np.array(avg_times)
    totals = np.array(totals)
    sweeps = np.array(sweeps)
    out = dict(problem=problem, n=n, seed=seed,
               clear_ratio=dict(mean=float(ratios.mean()), min=float(ratios.min()),
                                n_not_full=int((ratios < 1.0).sum())),
               avg_clear_time_s=dict(mean=float(avg_times.mean()), std=float(avg_times.std()),
                                     p5=float(np.percentile(avg_times, 5)),
                                     p50=float(np.percentile(avg_times, 50)),
                                     p95=float(np.percentile(avg_times, 95)),
                                     max=float(avg_times.max())),
               total_virtual_time_s=dict(mean=float(totals.mean()), std=float(totals.std()),
                                         p5=float(np.percentile(totals, 5)),
                                         p95=float(np.percentile(totals, 95)),
                                         max=float(totals.max())),
               sweep_time_s=dict(mean=float(sweeps.mean()),
                                 frac_of_total=float((sweeps / totals).mean())),
               n_sources=dict(min=int(np.min(n_srcs)), max=int(np.max(n_srcs)),
                              mean=float(np.mean(n_srcs))),
               n_fail_runs=len(fail_runs), fail_runs=fail_runs[:20],
               per_source_clear_time_s=dict(mean=float(np.mean(per_source_times)),
                                            std=float(np.std(per_source_times)),
                                            p50=float(np.percentile(per_source_times, 50)),
                                            p95=float(np.percentile(per_source_times, 95))),
               wall_time_s=round(t1 - t0, 1))
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--problem', type=int, required=True, choices=(3, 4))
    ap.add_argument('--n', type=int, default=400)
    ap.add_argument('--seed', type=int, default=2026)
    ap.add_argument('--p-dir', type=float, default=0.5)
    ap.add_argument('--verbose', action='store_true')
    args = ap.parse_args()
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    print(f'B 题问题{args.problem} 蒙特卡洛: N={args.n}, seed={args.seed}'
          + (f', 定向源概率={args.p_dir}' if args.problem == 4 else ''))
    out = run_batch(args.problem, args.n, args.seed, args.p_dir, args.verbose)
    path = os.path.join(OUT, f'b_p{args.problem}_mc.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f'  清除比例: 均值 {out["clear_ratio"]["mean"]:.4f}, '
          f'未全清 {out["clear_ratio"]["n_not_full"]}/{args.n}')
    print(f'  平均定位清除时间: {out["avg_clear_time_s"]["mean"]:.0f} ± '
          f'{out["avg_clear_time_s"]["std"]:.0f} s  (P5 {out["avg_clear_time_s"]["p5"]:.0f}, '
          f'P95 {out["avg_clear_time_s"]["p95"]:.0f}, 最大 {out["avg_clear_time_s"]["max"]:.0f})')
    print(f'  总虚拟时间: 均值 {out["total_virtual_time_s"]["mean"]:.0f} s '
          f'(P95 {out["total_virtual_time_s"]["p95"]:.0f}, 最大 {out["total_virtual_time_s"]["max"]:.0f})')
    print(f'  扫描阶段占比: {out["sweep_time_s"]["frac_of_total"]:.1%}')
    print(f'  干扰源个数: {out["n_sources"]["min"]}-{out["n_sources"]["max"]} '
          f'(均 {out["n_sources"]["mean"]:.1f})')
    print(f'  墙钟 {out["wall_time_s"]} s, 结果写入 {path}')
