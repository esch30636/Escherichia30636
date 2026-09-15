"""B 题 问题1 建模路径验证
交会定位法: 定位区域(凸多边形)的直径计算 与 "以直径为直径的圆能否覆盖" 判定

目的: 验证 shapely 几何栈可用,并把问题1的数学结论先钉死。
"""
import numpy as np
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union

D2R = np.pi / 180.0

def bearing(ax, ay, bx, by):
    """从 A 看向 B 的方位角(度, x轴正向逆时针, [0,360))"""
    return np.degrees(np.arctan2(by - ay, bx - ax)) % 360.0

def wedge_polygon(sx, sy, az_deg, half_deg, L=1.0e6):
    """示向度 az ± half 的楔形(用大三角形近似), 返回 shapely Polygon"""
    d_lo = (np.cos((az_deg - half_deg) * D2R), np.sin((az_deg - half_deg) * D2R))
    d_hi = (np.cos((az_deg + half_deg) * D2R), np.sin((az_deg + half_deg) * D2R))
    p1 = (sx + L * d_lo[0], sy + L * d_lo[1])
    p2 = (sx + L * d_hi[0], sy + L * d_hi[1])
    return Polygon([(sx, sy), p1, p2])

def polygon_diameter(poly):
    """凸多边形的直径 = 顶点两两最大距离(凸集的直径必在顶点对取得)"""
    c = np.array(poly.exterior.coords[:-1])
    if len(c) < 2:
        return 0.0
    dm, pair = 0.0, (0, 0)
    for i in range(len(c)):
        d = np.hypot(c[:, 0] - c[i, 0], c[:, 1] - c[i, 1])
        j = int(d.argmax())
        if d[j] > dm:
            dm, pair = float(d[j]), (i, j)
    return dm, pair


def circle_from_2(p, q):
    c = (p + q) / 2.0
    return c, np.hypot(*(p - c))


def circle_from_3(p, q, r):
    ax, ay, bx, by, cx, cy = *p, *q, *r
    d = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-12:
        return None
    ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay)
          + (cx**2 + cy**2) * (ay - by)) / d
    uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx)
          + (cx**2 + cy**2) * (bx - ax)) / d
    c = np.array([ux, uy])
    return c, np.hypot(ax - ux, ay - uy)


def min_enclosing_circle(pts):
    """穷举 2/3 点组合求最小包围圆(顶点数少时精确且直观)"""
    n = len(pts)
    best = None
    for i in range(n):
        for j in range(i + 1, n):
            circ = circle_from_2(pts[i], pts[j])
            if circ and all(np.hypot(*(p - circ[0])) <= circ[1] + 1e-9 for p in pts):
                if best is None or circ[1] < best[1]:
                    best = circ
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                circ = circle_from_3(pts[i], pts[j], pts[k])
                if circ and all(np.hypot(*(p - circ[0])) <= circ[1] + 1e-9 for p in pts):
                    if best is None or circ[1] < best[1]:
                        best = circ
    return best

print('=' * 64)
print('B 题问题1 建模路径验证: 交会定位区域直径与圆覆盖判定')
print('=' * 64)

# ---------- 算例 ----------
S1 = (-600.0, -200.0)
S2 = (500.0, 400.0)
G = (120.0, 250.0)          # 真实干扰源
err1, err2 = 0.7, -0.5      # 示向度误差(度), |e| <= 1

true1 = bearing(*S1, *G)
true2 = bearing(*S2, *G)
svd1 = (true1 + err1) % 360.0
svd2 = (true2 + err2) % 360.0

print(f'真实源 G = {G}, |S1G| = {np.hypot(G[0]-S1[0], G[1]-S1[1]):.1f} m, '
      f'|S2G| = {np.hypot(G[0]-S2[0], G[1]-S2[1]):.1f} m')
print(f'真实方位角: S1->G {true1:.4f}°,  S2->G {true2:.4f}°')
print(f'测得示向度: S1 {svd1:.4f}°,  S2 {svd2:.4f}°  (误差 {err1:+.1f}°, {err2:+.1f}°)')

# ---------- 定位区域 = 两个 ±1° 楔形的交集 ----------
W1 = wedge_polygon(*S1, svd1, 1.0)
W2 = wedge_polygon(*S2, svd2, 1.0)
reg = W1.intersection(W2)

# 截断到合理范围(楔形用有限大三角形近似, 交集可能含远端误交)
if not reg.is_empty:
    reg = reg.intersection(Point(0, 0).buffer(3000.0).buffer(0))

print(f'\n定位区域类型: {reg.geom_type},  面积 = {reg.area:.1f} m^2')
verts = np.array(reg.exterior.coords[:-1]) if reg.geom_type == 'Polygon' else None
if verts is not None:
    print(f'顶点数 = {len(verts)}  (题目图2 描述为四边形)')
    for v in verts:
        print(f'   ({v[0]:9.2f}, {v[1]:9.2f})')

D, pair = polygon_diameter(reg)
print(f'\n定位区域直径 D = {D:.2f} m   (由顶点 {pair} 取得)')

# ---------- 真值是否落在区域内(区域应包含真实源) ----------
print(f'真实源是否落在定位区域内: {reg.contains(Point(*G))}')

# ---------- 核心问题: 以 D 为直径的圆能否覆盖该区域 ----------
verts_arr = np.array(reg.exterior.coords[:-1])
cen_mec, r_min = min_enclosing_circle(verts_arr)
r_D = D / 2.0

# "以定位区域直径为直径的圆" 取直径对的中点为中心
p, q = verts_arr[pair[0]], verts_arr[pair[1]]
cen_D = (p + q) / 2.0
max_dev = max(np.hypot(*(v - cen_D)) for v in verts_arr)

print(f'\n最小包围圆(精确, 穷举 2/3 点):  r_min = {r_min:.2f} m, 圆心 = ({cen_mec[0]:.2f}, {cen_mec[1]:.2f})')
print(f'以直径对中点为圆心的圆:        r_D   = {r_D:.2f} m, 圆心 = ({cen_D[0]:.2f}, {cen_D[1]:.2f})')
print(f'  该圆到最远顶点的距离 = {max_dev:.2f} m  -> '
      f'{"圆内容纳得下" if max_dev <= r_D + 1e-6 else "圆内容纳不下"}')
print(f'Jung 定理上界 D/sqrt(3) = {D/np.sqrt(3):.2f} m  (平面上最小包围圆半径 <= D/sqrt(3))')
covered = r_min <= r_D + 1e-9
print(f'\n*** 能否覆盖: {"能" if covered else "不能"}   (r_min {"<=" if covered else ">"} D/2) ***')
print(f'    比值 r_min/(D/2) = {r_min/r_D:.4f},  松弛比 (r_min-r_D)/r_D = {(r_min-r_D)/r_D:+.2%}')

# ---------- 构造"不能覆盖"的反例, 确认结论不是算例偶然 ----------
print('\n--- 反例构造(证明一般结论) ---')
# 等边三角形: 直径 = 边长 a, 最小包围圆半径 = a/sqrt(3) > a/2
tri = Polygon([(0, 0), (1000, 0), (500, 1000 * np.sqrt(3) / 2)])
Dt, _ = polygon_diameter(tri)
tverts = np.array(tri.exterior.coords[:-1])
_, rt = min_enclosing_circle(tverts)
print(f'等边三角形: D = {Dt:.2f} m, r_min = {rt:.2f} m, D/2 = {Dt/2:.2f} m, '
      f'r_min/(D/2) = {rt/(Dt/2):.4f}  (理论值 2/sqrt(3) = {2/np.sqrt(3):.4f})')
print(f'  -> 最小包围圆比"以直径为直径的圆"大 {rt/(Dt/2)-1:.2%}, 故不能被覆盖')

print('\n结论:')
print('  1) 交会定位区域是两个 ±1° 楔形的交集, 为凸多边形;')
print('  2) 其直径 D 由顶点两两最大距离给出, 顶点数少时直接枚举即可;')
print('  3) 以 D 为直径的圆一般不能覆盖该区域 —— 只有当 r_min <= D/2 时才行;')
print('     平面上恒有 r_min <= D/sqrt(3) (Jung 定理), 两者比值上限 2/sqrt(3) ≈ 1.1547。')
