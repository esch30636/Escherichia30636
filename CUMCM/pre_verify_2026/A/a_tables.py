# -*- coding: utf-8 -*-
"""A 题 —— 生成论文所需 表1~表6 (全部保留四位小数)。

距离约定
--------
* 表1~表5 / result1~3: 药材半径恒为 2 cm, 列为 0, 0.5, 1, 1.5 cm, 末列 = 2 cm(表面,
  由边界条件反解, 精度优于线性外推)。
* 表6 / result4: 药材半径由附件2 收缩到 R_min = 1.198 cm, 固定距离列只能取
  0, 0.5, 1.0 cm (全程位于药材内部); 末列由模板规定为“药材表面”, 故表面单列。
"""
import sys, io, json
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
import numpy as np
import a_model as M
from a_output import sample
from solve_a import drying_time, RTOL, ATOL

N = 400
OUT = r'D:\CUMCM\A\out'
DIST5 = [0.0, 0.5, 1.0, 1.5]      # + 表面列
DIST6 = [0.0, 0.5, 1.0]           # + 药材表面
HDR5 = ['0', '0.5', '1', '1.5', '2']
HDR6 = ['0', '0.5', '1', '药材表面']


def evaluate(model, t_end, times, dist, rtol=RTOL, atol=ATOL):
    """返回 (T_degC, C) 形状 (len(times), len(dist)+1), 末列为表面。"""
    sol = model.solve(t_end, rtol=rtol, atol=atol)
    ts = np.asarray(times, float)
    Y = sol.sol(ts)
    T, C = sample(model, Y, ts, np.asarray(dist, float), add_surface=True)
    return T - 273.15, C, sol


def show(title, tlabels, arr, collabs, unit=''):
    print(f'\n{title}   {unit}')
    head = f'{"时间":>12} | ' + ' | '.join(f'{c:>8}' for c in collabs)
    print(head)
    print('-' * len(head))
    for lab, row in zip(tlabels, arr):
        print(f'{lab:>12} | ' + ' | '.join(f'{v:>8.4f}' for v in row))


def main():
    res = {}

    # ---------------- 问题1: 表1 / 表2 ----------------
    t1 = [100, 300, 600, 900, 1200, 1500, 1800]
    m1 = M.DryingModel(1, N=N)
    T, C, _ = evaluate(m1, 1800.0, t1, DIST5)
    show('表1  30 分钟内药材的温度 (degC)', t1, T, HDR5)
    show('表2  30 分钟内药材的水分浓度 (kg/kg)', t1, C, HDR5)
    res['表1'] = dict(times=t1, cols=HDR5, T=T.tolist())
    res['表2'] = dict(times=t1, cols=HDR5, C=C.tolist())

    # ---------------- 问题2: 表3 / 表4 (3 小时内每隔 0.5 h) ----------------
    t2_h = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    t2 = [h * 3600.0 for h in t2_h]
    m2 = M.DryingModel(2, N=N)
    T, C, _ = evaluate(m2, 10800.0, t2, DIST5)
    show('表3  3 小时内药材的温度 (degC)', t2_h, T, HDR5)
    show('表4  3 小时内药材的水分浓度 (kg/kg)', t2_h, C, HDR5)
    res['表3'] = dict(times_h=t2_h, cols=HDR5, T=T.tolist())
    res['表4'] = dict(times_h=t2_h, cols=HDR5, C=C.tolist())

    # ---------------- 问题3: 表5 (每隔 6 h + 烘干结束时间) ----------------
    te3 = drying_time(3, N)
    t3_h = [6.0 * k for k in range(1, int(te3 // 21600) + 1)]
    t3 = [h * 3600.0 for h in t3_h] + [te3]
    lbl3 = [f'{h:g}' for h in t3_h] + ['烘干结束']
    m3 = M.DryingModel(3, N=N)
    _, C, _ = evaluate(m3, te3, t3, DIST5)
    show(f'表5  药材烘干过程的水分浓度 (kg/kg)   [烘干结束 {te3:.0f} s = {te3/3600:.4f} h]',
         lbl3, C, HDR5)
    res['表5'] = dict(times_h=t3_h, t_end=te3, cols=HDR5, C=C.tolist())
    res['t3_end'] = te3

    # ---------------- 问题4: 表6 (含收缩) ----------------
    te4 = drying_time(4, N)
    t4_h = [6.0 * k for k in range(1, int(te4 // 21600) + 1)]
    t4 = [h * 3600.0 for h in t4_h] + [te4]
    lbl4 = [f'{h:g}' for h in t4_h] + ['烘干结束']
    m4 = M.DryingModel(4, N=N)
    _, C, _ = evaluate(m4, te4, t4, DIST6)
    show(f'表6  药材烘干过程的水分浓度 (kg/kg, 考虑收缩)   '
         f'[烘干结束 {te4:.0f} s = {te4/3600:.4f} h]', lbl4, C, HDR6)
    res['表6'] = dict(times_h=t4_h, t_end=te4, cols=HDR6, C=C.tolist())
    res['t4_end'] = te4

    with open(rf'{OUT}\tables.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(f'\n已保存 {OUT}\\tables.json')

    # 关键数字
    print(f'\n关键结果: 问题3 烘干时间 = {te3:.1f} s = {te3/3600:.4f} h = {te3/86400:.4f} 天')
    print(f'          问题4 烘干时间 = {te4:.1f} s = {te4/3600:.4f} h = {te4/86400:.4f} 天')


if __name__ == '__main__':
    main()
