"""B 题 问题1 第二问的统计判定 (半平面精确求交版)
"以定位区域直径为直径的圆能否覆盖此定位区域?" —— 蒙特卡洛

定位区域 = 两个 ±1° 楔形的交集 = 4 个半平面的交集, 用 Sutherland-Hodgman 精确裁剪。
(先前的有限大三角形近似会引入远端伪交, 已废弃)
"""
import numpy as np

D2R = np.pi / 180.0
RNG = np.random.default_rng(20260910)
BOX = 1.0e5          # 裁剪框半径, 远大于 1800 m 的目标区域

def bearing(ax, ay, bx, by):
    return np.degrees(np.arctan2(by - ay, bx - ax)) % 360.0

def clip(poly, s, d, keep_left):
    """用半平面 {P: cross(d, P-s) >= 0 (keep_left) 或 <= 0} 裁剪凸多边形"""
    if not poly:
        return []
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        fa = d[0] * (a[1] - s[1]) - d[1] * (a[0] - s[0])
        fb = d[0] * (b[1] - s[1]) - d[1] * (b[0] - s[0])
        ina = (fa >= -1e-12) if keep_left else (fa <= 1e-12)
        inb = (fb >= -1e-12) if keep_left else (fb <= 1e-12)
        if ina:
            out.append(a)
        if ina != inb:
            t = fa / (fa - fb)
            out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    return out

def region(s1, s2, az1, az2, half=1.0):
    """两个 ±half 楔形的交集"""
    poly = [(-BOX, -BOX), (BOX, -BOX), (BOX, BOX), (-BOX, BOX)]
    for s, az in ((s1, az1), (s2, az2)):
        for ang, left in ((az - half, True), (az + half, False)):
            d = (np.cos(ang * D2R), np.sin(ang * D2R))
            poly = clip(poly, s, d, left)
            if len(poly) < 3:
                return None, True
    pts = np.array(poly)
    # 是否触及裁剪框 -> 真实区域无界
    unbounded = bool(np.any(np.abs(pts) > BOX * 0.999))
    return pts, unbounded

def diameter(pts):
    dm = 0.0
    for i in range(len(pts)):
        d = np.hypot(pts[:, 0] - pts[i, 0], pts[:, 1] - pts[i, 1])
        dm = max(dm, d.max())
    return dm

def mec(pts):
    """穷举 2/3 点组合的最小包围圆; 容差取相对量级, 避免大坐标下失效"""
    n = len(pts)
    scale = max(1.0, np.abs(pts).max())
    tol = 1e-9 * scale
    best = None
    def ok(c, r):
        return all(np.hypot(*(p - c)) <= r + tol for p in pts)
    for i in range(n):
        for j in range(i + 1, n):
            c = (pts[i] + pts[j]) / 2.0
            r = np.hypot(*(pts[i] - c))
            if ok(c, r) and (best is None or r < best[1]):
                best = (c, r)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                ax, ay = pts[i]; bx, by = pts[j]; cx, cy = pts[k]
                d = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
                if abs(d) < 1e-12 * scale * scale:
                    continue
                ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay)
                      + (cx**2 + cy**2) * (ay - by)) / d
                uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx)
                      + (cx**2 + cy**2) * (bx - ax)) / d
                c = np.array([ux, uy]); r = np.hypot(ax - ux, ay - uy)
                if ok(c, r) and (best is None or r < best[1]):
                    best = (c, r)
    return best

N = 20000
ratios, covered = [], 0
stat = dict(degenerate=0, unbounded=0, nonquad=0, miss_truth=0)
for _ in range(N):
    S1 = RNG.uniform(-1800, 1800, 2)
    S2 = RNG.uniform(-1800, 1800, 2)
    G = RNG.uniform(-1800, 1800, 2)
    if np.hypot(*(S2 - S1)) < 50 or np.hypot(*(G - S1)) < 10 or np.hypot(*(G - S2)) < 10:
        stat['degenerate'] += 1; continue

    az1 = (bearing(*S1, *G) + RNG.uniform(-1, 1)) % 360.0
    az2 = (bearing(*S2, *G) + RNG.uniform(-1, 1)) % 360.0

    pts, unb = region(S1, S2, az1, az2)
    if pts is None or len(pts) < 3:
        stat['degenerate'] += 1; continue
    if unb:
        stat['unbounded'] += 1; continue
    if len(pts) != 4:
        stat['nonquad'] += 1
    # 真实源必须落在区域内, 否则说明楔形取错了分支
    inside = True
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        if (b[0] - a[0]) * (G[1] - a[1]) - (b[1] - a[1]) * (G[0] - a[0]) < -1e-6:
            inside = False; break
    if not inside:
        stat['miss_truth'] += 1; continue

    Dv = diameter(pts)
    if Dv < 1e-6:
        stat['degenerate'] += 1; continue
    m = mec(pts)
    if m is None:
        stat['degenerate'] += 1; continue
    ratios.append(m[1] / (Dv / 2.0))
    if m[1] <= Dv / 2.0 + 1e-9 * max(1.0, Dv):
        covered += 1

ratios = np.array(ratios)
print('=' * 66)
print('B 题问题1 第二问: 蒙特卡洛判定 (半平面精确求交)')
print('=' * 66)
print(f'样本 {N},  有效 {len(ratios)}')
print(f'  退化 {stat["degenerate"]},  区域无界 {stat["unbounded"]},  '
      f'非四边形 {stat["nonquad"]},  楔形分支错误 {stat["miss_truth"]}')
print(f'\nr_min / (D/2) 分布  (恒 >= 1, 因最小包围圆必含直径两端点):')
print(f'  最小 {ratios.min():.6f}   中位 {np.median(ratios):.6f}   最大 {ratios.max():.6f}')
print(f'  均值 {ratios.mean():.6f}   标准差 {ratios.std():.6f}')
for q in (50, 90, 95, 99, 100):
    print(f'  {q:5.1f}% 分位 = {np.percentile(ratios, q):.6f}')
ex = ratios - 1.0
print(f'\n超出 1 的幅度: 最大 {ex.max():.3e},  99% 分位 {np.percentile(ex,99):.3e}')
print(f'超出 1e-6 的样本数 = {int((ex > 1e-6).sum())}')
print(f'\n能覆盖 = {covered}/{len(ratios)} = {covered/len(ratios):.4%}')
print(f'不能覆盖 = {len(ratios)-covered}/{len(ratios)} = {1-covered/len(ratios):.4%}')
print(f'Jung 定理上界 2/sqrt(3) = {2/np.sqrt(3):.6f}')

print('\n' + '=' * 66)
print('结论:')
print('  1) 定位区域 = 两个 ±1° 楔形之交 = 4 个半平面之交, 为凸四边形;')
print('  2) 其直径 D 在顶点对取得, 枚举顶点对即可 (算法直接、精确);')
print('  3) 若 MEC 恒由直径端点确定, 则 r_min == D/2, 圆恰好覆盖;')
print('  4) 只有当配置退化(两测点与源近共线 / 区域无界)时才不成立。')
