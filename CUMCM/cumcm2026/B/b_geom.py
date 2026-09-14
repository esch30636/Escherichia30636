# -*- coding: utf-8 -*-
"""B 题几何核心: 交会定位区域(楔形交集)、直径、最小包围圆、覆盖判定。

定位区域 = 每个检测点处 ±1° 示向度楔形的交集 = 2k 个半平面之交。
用 Sutherland-Hodgman 半平面精确裁剪求交; 直径按"凸集直径必在顶点对取得"枚举;
最小包围圆穷举 2/3 点组合(顶点数少, 精确且直观)。

约定: 方位角为 x 轴正向逆时针, [0,360), 单位度。
"""
import numpy as np

D2R = np.pi / 180.0
BOX = 1.0e6            # 裁剪框半径, 远大于 1800 m 目标区域, 用于探测"区域无界"


def bearing(ax, ay, bx, by):
    """从 (ax,ay) 看向 (bx,by) 的方位角(度, [0,360))。"""
    return float(np.degrees(np.arctan2(by - ay, bx - ax)) % 360.0)


def _clip(poly, s, d, keep_left):
    """用半平面 {P: cross(d, P-s) >= 0 (keep_left) 或 <= 0} 裁剪凸多边形。"""
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


def region(stops, svds, half=1.0):
    """k 个 ±half 度楔形(检测点 stops[i], 示向度 svds[i])的交集。

    返回 (pts, unbounded):
      pts        顶点数组 (N,2), 区域为空时 None
      unbounded  是否触及裁剪框(真实区域无界)
    """
    poly = [(-BOX, -BOX), (BOX, -BOX), (BOX, BOX), (-BOX, BOX)]
    for s, az in zip(stops, svds):
        for ang, left in ((az - half, True), (az + half, False)):
            d = (np.cos(ang * D2R), np.sin(ang * D2R))
            poly = _clip(poly, s, d, left)
            if len(poly) < 3:
                return None, False
    pts = np.array(poly, dtype=float)
    unbounded = bool(np.any(np.abs(pts) > BOX * 0.999))
    return pts, unbounded


def diameter(pts):
    """凸多边形直径 = 顶点两两最大距离, 返回 (D, (i, j))。"""
    dm, pair = 0.0, (0, 0)
    for i in range(len(pts)):
        d = np.hypot(pts[:, 0] - pts[i, 0], pts[:, 1] - pts[i, 1])
        j = int(d.argmax())
        if d[j] > dm:
            dm, pair = float(d[j]), (i, j)
    return dm, pair


def mec(pts):
    """最小包围圆: 穷举 2/3 点组合(定点圆由直径两端或三点外接圆确定)。

    返回 (center, r) 或 None。
    """
    n = len(pts)
    scale = max(1.0, float(np.abs(pts).max()))
    tol = 1e-9 * scale
    best = None

    def ok(c, r):
        return all(np.hypot(p[0] - c[0], p[1] - c[1]) <= r + tol for p in pts)

    for i in range(n):
        for j in range(i + 1, n):
            c = (pts[i] + pts[j]) / 2.0
            r = np.hypot(*(pts[i] - c))
            if ok(c, r) and (best is None or r < best[1]):
                best = (c, r)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                ax, ay = pts[i]
                bx, by = pts[j]
                cx, cy = pts[k]
                d = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
                if abs(d) < 1e-12 * scale * scale:
                    continue
                ux = ((ax ** 2 + ay ** 2) * (by - cy) + (bx ** 2 + by ** 2) * (cy - ay)
                      + (cx ** 2 + cy ** 2) * (ay - by)) / d
                uy = ((ax ** 2 + ay ** 2) * (cx - bx) + (bx ** 2 + by ** 2) * (ax - cx)
                      + (cx ** 2 + cy ** 2) * (bx - ax)) / d
                c = np.array([ux, uy])
                r = np.hypot(ax - ux, ay - uy)
                if ok(c, r) and (best is None or r < best[1]):
                    best = (c, r)
    return best


def in_convex(pts, p):
    """点 p 是否在凸多边形内(边界按内)。"""
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        if (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) < -1e-6:
            return False
    return True


def cover_check(pts):
    """覆盖判定: 返回 dict(D, r_min, ratio=r_min/(D/2), covered)。"""
    D, pair = diameter(pts)
    if D < 1e-9:
        return None
    c, r = mec(pts)
    return dict(D=D, pair=pair, r_min=float(r), ratio=float(r / (D / 2.0)),
                covered=bool(r <= D / 2.0 + 1e-9 * max(1.0, D)))
