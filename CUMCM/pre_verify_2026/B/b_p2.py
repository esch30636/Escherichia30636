# -*- coding: utf-8 -*-
"""B 题 问题2: 已知一个示向度时, 第二个检测点的选择策略与候选区域。

设定: 检测点 S1=(0,0), 测得示向度 0°(平移旋转不改变问题), 误差 ±1°。
真实源 G=(d1,0), d1 先验为盘内均匀(密度 f(d1)∝d1, d1∈[5,1500], 且已被 S1 接收)。
接收半径 r_G ~ U[1000,1500], 已接收 => r_G >= d1。
第二检测点 S2 = L*(cos psi, sin psi)。

度量: 两楔形定位区域直径 D(与问题1一致), 取 E[D | 在 S2 接收到]。
P_s = P(|S2-G| <= r_G | r_G >= d1) 用解析积分精确计算(避免小样本尾部误差)。
理论近似(窄楔形): 定位区域近似为平行四边形, 直径 = 长对角线
  D ≈ (2e/sin phi) * sqrt(d1^2 + d2^2 + 2 d1 d2 cos phi),
  phi = 两示向线在 G 处夹角, sin phi = L sin psi / d2, cos phi = |d1 - L cos psi| / d2。
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
from b_geom import region, diameter

RNG = np.random.default_rng(20260910)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
EPS = np.radians(1.0)


def d2_of(L, psi, d1):
    return np.sqrt(L * L + d1 * d1 - 2 * L * d1 * np.cos(psi))


def ps_analytic(L, psi, ngrid=4001):
    """P_s = ∫ P(d2(d1) <= r_G | r_G>=d1) f(d1) dd1,  f(d1) ∝ d1 于 [5,1500]。

    r_G | r_G>=d1:  d1<=1000 时 r_G~U[1000,1500];  d1>1000 时 r_G~U[d1,1500]。
    """
    d1 = np.linspace(5.0, 1500.0, ngrid)
    d2 = d2_of(L, psi, d1)
    p = np.empty_like(d2)
    lo = d1 <= 1000.0
    p[lo] = np.clip((1500.0 - np.maximum(d2[lo], 1000.0)) / 500.0, 0.0, 1.0)
    hi = ~lo
    den = 1500.0 - d1[hi]
    with np.errstate(divide='ignore', invalid='ignore'):
        p[hi] = np.where(den > 0.0,
                         np.clip((1500.0 - np.maximum(d2[hi], d1[hi])) / den, 0.0, 1.0),
                         (d2[hi] <= 1500.0).astype(float))
    # 关键: S1 已接收到信号 => 观测本身携带信息, 先验须条件化
    #   f(d1 | S1收到) ∝ d1 * P(r_G>=d1 | d1),  P(r_G>=d1|d1) = (1500-d1)/500 (d1>1000)
    prec = np.where(d1 <= 1000.0, 1.0, (1500.0 - d1) / 500.0)
    w = d1 * prec / (d1 * prec).sum()
    return float((p * w).sum())


def ed_mc(L, psi, n):
    """E[D | 成功] 蒙特卡洛: 采样 d1∝d1, r_G~U[1000,1500], 条件 r_G>=d1。"""
    u = RNG.uniform(0, 1, n)
    d1 = np.sqrt(u * (1500.0 ** 2 - 25.0) + 25.0)
    rG = RNG.uniform(1000.0, 1500.0, n)
    keep = rG >= d1
    d1, rG = d1[keep], rG[keep]
    m = len(d1)
    S2 = np.array([L * np.cos(psi), L * np.sin(psi)])
    d2 = np.hypot(d1 - S2[0], -S2[1])
    success = d2 <= rG
    diam = np.full(m, np.nan)
    for i in np.nonzero(success)[0]:
        e1 = RNG.uniform(-1, 1)
        e2 = RNG.uniform(-1, 1)
        svd1 = float((0.0 + e1) % 360.0)
        svd2 = float((np.degrees(np.arctan2(-S2[1], d1[i] - S2[0])) + e2) % 360.0)
        pts, unb = region([(0.0, 0.0), tuple(S2)], [svd1, svd2])
        if pts is not None and not unb:
            D, _ = diameter(pts)
            diam[i] = D
    ok = ~np.isnan(diam)
    return float(success.mean()), diam[ok]


def theory_d(L, psi, d1):
    """理论直径(成功样本上使用)。"""
    d2 = d2_of(L, psi, d1)
    sinphi = np.abs(L * np.sin(psi)) / d2
    cosphi = np.abs(d1 - L * np.cos(psi)) / d2
    return 2.0 * EPS / sinphi * np.sqrt(d1 ** 2 + d2 ** 2 + 2 * d1 * d2 * cosphi)


def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    print('=' * 68)
    print('B 题问题2: 第二检测点选择策略 (网格 MC + 解析 P_s)')
    print('=' * 68)

    Ls = np.arange(700.0, 1650.0, 50.0)
    psis = np.deg2rad(np.arange(15.0, 75.0, 5.0))
    n = 2000
    Ps = np.zeros((len(Ls), len(psis)))
    ED = np.full((len(Ls), len(psis)), np.nan)
    for i, L in enumerate(Ls):
        for j, psi in enumerate(psis):
            Ps[i, j] = ps_analytic(L, psi)
            _, d = ed_mc(L, psi, n)
            ED[i, j] = float(d.mean()) if len(d) else np.nan
    print(f'网格 {len(Ls)}x{len(psis)}, 每单元 {n} 样本, 耗时 {time.time()-t0:.1f}s')

    # ---- 最优: P_s >= 0.90 约束下最小化 E[D] ----
    feas = Ps >= 0.90
    cand = np.where(feas & ~np.isnan(ED))
    k = np.argmin(ED[cand])
    i_opt, j_opt = cand[0][k], cand[1][k]
    L_opt, psi_opt = Ls[i_opt], psis[j_opt]
    print(f'\nP_s >= 0.90 约束下最优: L* = {L_opt:.0f} m, psi* = {np.degrees(psi_opt):.0f}°, '
          f'P_s = {Ps[i_opt, j_opt]:.4f}, E[D|成功] = {ED[i_opt, j_opt]:.1f} m')
    k0 = np.nanargmin(ED)
    i0, j0 = np.unravel_index(k0, ED.shape)
    print(f'无约束最优(参考):     L = {Ls[i0]:.0f} m, psi = {np.degrees(psis[j0]):.0f}°, '
          f'P_s = {Ps[i0, j0]:.4f}, E[D] = {ED[i0, j0]:.1f} m')

    # ---- 候选区域: P_s >= 0.90 且 E[D] <= 1.15x最优 ----
    thr = 1.15 * ED[i_opt, j_opt]
    mask = (Ps >= 0.90) & ~np.isnan(ED) & (ED <= thr)
    L_lo, L_hi = Ls[np.any(mask, axis=1)].min(), Ls[np.any(mask, axis=1)].max()
    psi_lo, psi_hi = psis[np.any(mask, axis=0)].min(), psis[np.any(mask, axis=0)].max()
    print(f'\n候选区域(P_s>=0.90 且 E[D] <= 1.15x最优):')
    print(f'  L ∈ [{L_lo:.0f}, {L_hi:.0f}] m,  psi ∈ [{np.degrees(psi_lo):.0f}°, '
          f'{np.degrees(psi_hi):.0f}°]  (示向度方向两侧对称)')

    # ---- 朴素策略对比 ----
    naive = dict(
        advance500=sim_cell_pair(500.0, 0.0, n),
        advance1k=sim_cell_pair(1000.0, 0.0, n),
        perp500=(ps_analytic(500.0, np.pi / 2), ed_mc(500.0, np.pi / 2, n)[1]),
        perp1k=(ps_analytic(1000.0, np.pi / 2), ed_mc(1000.0, np.pi / 2, n)[1]),
        behind500=(ps_analytic(500.0, np.pi), ed_mc(500.0, np.pi, n)[1]),
    )
    print('\n朴素策略对比:')
    for name, (p, d) in naive.items():
        dd = f'{d.mean():8.1f} m' if len(d) else '  无界(共线)'
        print(f'  {name:10s}: P_s = {p:.4f}, E[D|成功] = {dd}')

    # ---- 理论近似验证 ----
    d1 = np.sqrt(RNG.uniform(0, 1, 20000) * (1500.0 ** 2 - 25.0) + 25.0)
    rG = RNG.uniform(1000.0, 1500.0, 20000)
    keep = rG >= d1
    d1, rG = d1[keep], rG[keep]
    for (L, psi_deg) in ((400.0, 90.0), (800.0, 90.0), (1050.0, 30.0), (1050.0, 45.0)):
        psi = np.deg2rad(psi_deg)
        d2 = d2_of(L, psi, d1)
        ok = d2 <= rG
        Dt = theory_d(L, psi, d1[ok])
        p, d = ed_mc(L, psi, 4000)
        print(f'L={L:.0f}, psi={psi_deg:.0f}°: 理论 E[D] = {Dt.mean():7.1f} m, '
              f'MC E[D] = {d.mean():7.1f} m   (P_s 理论 {ok.mean():.3f} / 解析 {ps_analytic(L, psi):.3f} / MC {p:.3f})')

    out = dict(Ls=Ls.tolist(), psi_deg=np.degrees(psis).tolist(), Ps=Ps.tolist(),
               ED=ED.tolist(), opt=dict(L=float(L_opt), psi_deg=float(np.degrees(psi_opt)),
                                        Ps=float(Ps[i_opt, j_opt]), ED=float(ED[i_opt, j_opt])),
               unconstrained=dict(L=float(Ls[i0]), psi_deg=float(np.degrees(psis[j0])),
                                  Ps=float(Ps[i0, j0]), ED=float(ED[i0, j0])),
               candidate=dict(L_range=[float(L_lo), float(L_hi)],
                              psi_deg_range=[float(np.degrees(psi_lo)), float(np.degrees(psi_hi))],
                              thr=float(thr)))
    with open(os.path.join(OUT, 'b_p2.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f'\n结果写入 out/b_p2.json, 总耗时 {time.time()-t0:.1f}s')


def sim_cell_pair(L, psi, n):
    return ps_analytic(L, psi), ed_mc(L, psi, n)[1]


if __name__ == '__main__':
    main()
