# -*- coding: utf-8 -*-
"""B 题 问题1: 交会定位法定位区域直径的算法 + "以直径为直径的圆能否覆盖"的判定。

结论(经 MC 验证):
  1) 定位区域 = k 个 ±1° 楔形的交集 = 2k 个半平面之交, 凸多边形(非退化时 2k 边形);
  2) 直径 D 必在顶点对取得, 枚举 O(V^2) 即可(可用旋转卡壳降到 O(V));
  3) 以 D 为直径的圆能否覆盖 <=> 最小包围圆半径 r_min <= D/2;
     数值上 r_min/(D/2) 几乎恒等于 1(偏差 < 1e-3 且仅出现在近退化配置),
     即"以定位区域直径为直径的圆"在交会定位法下(几乎总是)恰好覆盖;
  4) 但对一般凸区域不能覆盖: 等边三角形反例, 比值上限 2/sqrt(3) (Jung 定理)。
"""
import sys
import os
import json
import time

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
import numpy as np
from b_geom import bearing, region, diameter, mec, in_convex, cover_check

RNG = np.random.default_rng(20260910)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
DISK = 1800.0          # 目标区域半径


def rand_disk(n):
    r = DISK * np.sqrt(RNG.uniform(0, 1, n))
    a = RNG.uniform(0, 2 * np.pi, n)
    return np.column_stack([r * np.cos(a), r * np.sin(a)])


def demo_k2():
    S1 = np.array([-600.0, -200.0])
    S2 = np.array([500.0, 400.0])
    G = np.array([120.0, 250.0])
    err = np.array([0.7, -0.5])
    svds = [(bearing(*S1, *G) + err[0]) % 360.0, (bearing(*S2, *G) + err[1]) % 360.0]
    pts, unb = region([S1, S2], svds)
    D, pair = diameter(pts)
    ck = cover_check(pts) if D > 0 else None
    print('--- 算例(k=2) ---')
    print(f'S1={tuple(S1)}, S2={tuple(S2)}, G={tuple(G)}, 误差 {err}')
    print(f'示向度 {svds[0]:.4f}, {svds[1]:.4f}')
    print(f'定位区域: {len(pts)} 边形, 无界={unb}, 真实源在内={in_convex(pts, G)}')
    print(f'直径 D = {D:.2f} m, r_min = {ck["r_min"]:.2f} m, '
          f'比值 r_min/(D/2) = {ck["ratio"]:.6f}, 覆盖={ck["covered"]}')
    return dict(k=2, S1=tuple(S1), S2=tuple(S2), G=tuple(G), svds=svds, nvert=len(pts),
                D=float(D), r_min=ck['r_min'], ratio=ck['ratio'], covered=ck['covered'])


def demo_k3():
    G = np.array([120.0, 250.0])
    S = np.array([[-700.0, -300.0], [600.0, 500.0], [-200.0, 900.0]])
    err = np.array([0.6, -0.4, 0.8])
    svds = [(bearing(*S[i], *G) + err[i]) % 360.0 for i in range(3)]
    pts, unb = region(S, svds)
    D, pair = diameter(pts)
    ck = cover_check(pts) if D > 0 else None
    print('\n--- 算例(k=3) ---')
    print(f'示向度 {[f"{v:.4f}" for v in svds]}')
    print(f'定位区域: {len(pts)} 边形, 无界={unb}, 真实源在内={in_convex(pts, G)}')
    print(f'直径 D = {D:.2f} m, r_min = {ck["r_min"]:.2f} m, '
          f'比值 r_min/(D/2) = {ck["ratio"]:.6f}, 覆盖={ck["covered"]}')
    return dict(k=3, nvert=len(pts), D=float(D), r_min=ck['r_min'],
                ratio=ck['ratio'], covered=ck['covered'])


def run_mc(k, n):
    """k 个检测点随机配置的覆盖判定统计。

    额外统计: 偏差是否只出现在退化配置(区域不是 2k 边形)中。
    """
    ratios = []
    ratios_2k, ratios_deg = [], []      # 2k 边形 / 非 2k 边形 各自的比值
    stat = dict(n=n, valid=0, degenerate=0, unbounded=0, miss_truth=0, non2k=0)
    for _ in range(n):
        S = rand_disk(k)
        G = rand_disk(1)[0]
        dmin_G = np.hypot(S[:, 0] - G[0], S[:, 1] - G[1]).min()
        if dmin_G < 10.0:
            stat['degenerate'] += 1
            continue
        # 任两个检测点不能太近(避免完全退化)
        dmin = 1e9
        for i in range(k):
            d = np.hypot(S[:, 0] - S[i, 0], S[:, 1] - S[i, 1])
            d[i] = 1e9
            dmin = min(dmin, d.min())
        if dmin < 30.0:
            stat['degenerate'] += 1
            continue
        svds = [(bearing(*S[i], *G) + RNG.uniform(-1, 1)) % 360.0 for i in range(k)]
        pts, unb = region(S, svds)
        if pts is None or len(pts) < 3:
            stat['degenerate'] += 1
            continue
        if unb:
            stat['unbounded'] += 1
            continue
        if len(pts) != 2 * k:
            stat['non2k'] += 1
        if not in_convex(pts, G):
            stat['miss_truth'] += 1
            continue
        D, _ = diameter(pts)
        if D < 1e-6:
            stat['degenerate'] += 1
            continue
        c, r = mec(pts)
        ratio = r / (D / 2.0)
        ratios.append(ratio)
        (ratios_2k if len(pts) == 2 * k else ratios_deg).append(ratio)
        stat['valid'] += 1
    ratios = np.array(ratios)
    ratios_2k = np.array(ratios_2k)
    ratios_deg = np.array(ratios_deg)
    out = dict(stat)
    out['ratio_min'] = float(ratios.min())
    out['ratio_med'] = float(np.median(ratios))
    out['ratio_max'] = float(ratios.max())
    out['ratio_mean'] = float(ratios.mean())
    out['ratio_p99'] = float(np.percentile(ratios, 99))
    out['covered'] = int((ratios <= 1.0 + 1e-9).sum())
    out['covered_frac'] = float((ratios <= 1.0 + 1e-9).mean())
    out['n_excess_1e6'] = int((ratios > 1.0 + 1e-6).sum())
    out['n2k'] = len(ratios_2k)
    out['ratio_2k_max'] = float(ratios_2k.max()) if len(ratios_2k) else None
    out['ratio_2k_p99'] = float(np.percentile(ratios_2k, 99)) if len(ratios_2k) else None
    out['ratio_deg_max'] = float(ratios_deg.max()) if len(ratios_deg) else None
    out['ratio_deg_frac'] = float((ratios_deg > 1.0 + 1e-6).mean()) if len(ratios_deg) else None
    return out


def counterexample():
    """等边三角形反例: 直径圆的半径 D/2 不足以覆盖, 需 D/sqrt(3)。"""
    a = 1000.0
    tri = np.array([[0.0, 0.0], [a, 0.0], [a / 2, a * np.sqrt(3) / 2]])
    D, _ = diameter(tri)
    c, r = mec(tri)
    print('\n--- 反例: 一般凸区域 ---')
    print(f'等边三角形: D = {D:.2f} m, r_min = {r:.2f} m = D/sqrt(3), '
          f'D/2 = {D/2:.2f} m -> 直径圆覆盖不了, 需放大 {r/(D/2):.4f} 倍 (= 2/sqrt(3))')
    return dict(D=float(D), r_min=float(r), ratio=float(r / (D / 2.0)))


def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    print('=' * 68)
    print('B 题问题1: 定位区域直径算法与覆盖圆判定')
    print('=' * 68)
    res = dict(demo_k2=demo_k2(), demo_k3=demo_k3(), counterexample=counterexample(),
               mc={})
    for k, n in ((2, 20000), (3, 8000), (4, 8000), (5, 8000), (6, 8000)):
        m = run_mc(k, n)
        res['mc'][k] = m
        print(f'\n[k={k}, N={n}] 有效 {m["valid"]}, 退化 {m["degenerate"]}, '
              f'无界 {m["unbounded"]}, 非2k边形 {m["non2k"]}, 漏真值 {m["miss_truth"]}')
        print(f'  r_min/(D/2): min {m["ratio_min"]:.6f}  med {m["ratio_med"]:.6f}  '
              f'max {m["ratio_max"]:.6f}  mean {m["ratio_mean"]:.6f}  '
              f'p99 {m["ratio_p99"]:.6f}')
        print(f'  覆盖 = {m["covered"]}/{m["valid"]} = {m["covered_frac"]:.4%},  '
              f'超出1e-6 的样本 = {m["n_excess_1e6"]}')
        print(f'  2k 边形({m["n2k"]} 个): 比值最大 {m["ratio_2k_max"]}, '
              f'p99 {m["ratio_2k_p99"]} | 退化形: 比值最大 {m["ratio_deg_max"]}, '
              f'超1e-6 比例 {m["ratio_deg_frac"]}')
    with open(os.path.join(OUT, 'b_p1.json'), 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(f'\n结果写入 out/b_p1.json, 耗时 {time.time()-t0:.1f}s')


if __name__ == '__main__':
    main()
