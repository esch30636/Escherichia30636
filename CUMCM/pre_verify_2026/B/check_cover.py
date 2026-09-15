# -*- coding: utf-8 -*-
"""扫描站集覆盖性数值验证。

问题3(全向): 站集 = 原点 + 1200m 六边形, 需 max_G min_S |SG| <= 1000。
问题4(定向): 对每个 G, 取 disk(G,1000) 内所有站, 从 G 看的方向角最大间隙 <= 180°
  <=> 任意 180° 扇区窗(定向覆盖)内必有站 (充要条件)。
"""
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
import numpy as np

RNG = np.random.default_rng(20260910)


def ring(r, k):
    a = np.deg2rad(np.arange(0.0, 360.0, 360.0 / k))
    return r * np.column_stack([np.cos(a), np.sin(a)])


def stops_p3():
    return np.vstack([[0.0, 0.0], ring(1200.0, 6)])


def stops_p4(k_mid=12, k_in=12, k_out=24, r_out=2100.0):
    return np.vstack([[0.0, 0.0], ring(600.0, k_mid), ring(1200.0, k_in), ring(r_out, k_out)])


def check_p3(n=200000):
    S = stops_p3()
    G = 1800.0 * np.sqrt(RNG.uniform(0, 1, n)) * np.exp(1j * RNG.uniform(0, 2 * np.pi, n))
    G = np.column_stack([G.real, G.imag])
    d = np.hypot(G[:, None, 0] - S[None, :, 0], G[:, None, 1] - S[None, :, 1]).min(axis=1)
    return d.max(), np.percentile(d, 99.99)


def check_p4_gaps(S, n=60000):
    """对每个 G: disk(G,1000) 内站的方向角最大间隙(含首尾环绕) <= 180°?"""
    G = 1800.0 * np.sqrt(RNG.uniform(0, 1, n)) * np.exp(1j * RNG.uniform(0, 2 * np.pi, n))
    G = np.column_stack([G.real, G.imag])
    worst = 0.0
    worst_g = None
    fails = 0
    for i in range(n):
        d = np.hypot(S[:, 0] - G[i, 0], S[:, 1] - G[i, 1])
        m = d <= 1000.0
        if not m.any():
            fails += 1
            continue
        ang = np.sort(np.degrees(np.arctan2(S[m, 1] - G[i, 1], S[m, 0] - G[i, 0])) % 360.0)
        gaps = np.diff(np.concatenate([ang, [ang[0] + 360.0]]))
        g = gaps.max()
        if g > worst:
            worst, worst_g = g, (G[i], ang, gaps)
        if g > 180.0:
            fails += 1
    return worst, worst_g, fails


if __name__ == '__main__':
    print('问题3 站集(7站):', stops_p3().shape[0], '站')
    m, q = check_p3()
    print(f'  max_G min_S |SG| = {m:.2f} m  (理论 969.0, 需 <= 1000 -> {"通过" if m <= 1000 else "失败"})')
    print(f'  99.99% 分位 = {q:.2f} m')

    for (km, ki, ko, ro) in ((12, 12, 24, 2100.0), (12, 12, 24, 2150.0), (12, 12, 12, 2100.0), (12, 12, 24, 2200.0)):
        S = stops_p4(km, ki, ko, ro)
        w, wg, fails = check_p4_gaps(S)
        nst = len(S)
        print(f'\n问题4 站集 原点+中环{km}+内环{ki}+外环{ko}(R={ro:.0f}) = {nst} 站:')
        print(f'  disk(G,1000)内站方向角最大间隙 = {w:.2f}°  (需 <= 180° -> {"通过" if w <= 180 else "失败"})')
        print(f'  失败样本数 = {fails}')
        if wg is not None:
            G, ang, gaps = wg
            print(f'  最坏: G=({G[0]:.1f}, {G[1]:.1f}) (|G|={np.hypot(*G):.1f}), '
                  f'圆内站方向 = {np.round(ang, 1)}, 间隙 = {np.round(gaps, 1)}°')
