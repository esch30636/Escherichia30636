# -*- coding: utf-8 -*-
"""A 题 主求解器 —— 生成 result1..result4.xlsx

用法:
    python solve_a.py 1         # 问题1
    python solve_a.py 2         # 问题2
    python solve_a.py 3         # 问题3
    python solve_a.py 4         # 问题4
    python solve_a.py all
"""
import sys, io, os, time
# 就地重配置, 不要新建 TextIOWrapper —— 否则被 import 时旧 wrapper 析构会关掉共享 buffer
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
import numpy as np
import openpyxl
import a_model as M
from a_output import stream_sample, write_xlsx

DATA = r'D:\CUMCM\A\data'
OUT = r'D:\CUMCM\A\out'
N_GRID = 400
RTOL, ATOL = 1e-8, 1e-10


def tpl_info(prob):
    """读模板: 工作表名 + 表头"""
    wb = openpyxl.load_workbook(rf'{DATA}\templates\result{prob}.xlsx', read_only=True)
    out = []
    for ws in wb.worksheets:
        hdr = next(ws.iter_rows(max_row=1, values_only=True))
        out.append((ws.title, [h for h in hdr if h is not None]))
    wb.close()
    return out


def drying_time(prob, N=N_GRID, t_max=300000.0):
    """求 max C < 0.15 kg/kg 的时刻"""
    m = M.DryingModel(prob, N=N)

    def ev(t, y):
        return y[1::2].max() - 0.15
    ev.terminal = True
    ev.direction = -1
    t0 = time.time()
    s = m.solve(t_max, events=[ev], rtol=RTOL, atol=ATOL)
    te = float(s.t_events[0][0]) if len(s.t_events[0]) else np.nan
    print(f'  [问题{prob}] 烘干时间 t_end = {te:.1f} s = {te/3600:.4f} h '
          f'= {te/86400:.4f} 天   ({s.t.size} 步, {time.time()-t0:.1f}s)')
    return te


def build_header(prob, cols_cm, surface_label):
    """表头与模板一致: 数值列用数值, 整数列写成整数(0, 0.1, ..., 1.9, 2 / 药材表面)。"""
    head = ['时间\\到药材中心的距离']
    cols = list(cols_cm) + ([] if isinstance(surface_label, str) else [surface_label])
    for c in cols:
        cf = float(c)
        head.append(int(round(cf)) if abs(cf - round(cf)) < 1e-9 else round(cf, 10))
    if isinstance(surface_label, str):
        head.append(surface_label)
    return head


def run(prob, limit=None):
    os.makedirs(OUT, exist_ok=True)
    tpl = tpl_info(prob)
    print(f'=== 问题{prob} ===  模板: {[(n, len(h)) for n, h in tpl]}')

    if prob == 1:
        N, cols, surf, t_end, dt, t0 = N_GRID, np.arange(0, 2.0, 0.1), 2.0, 1800.0, 1.0, 0.0
    elif prob == 2:
        # 窗口与 表3/表4 一致("3 h 内"), 与问题1 的 "1800 s 内" 同构;
        # 全流程(2-3 天)的结果由 result3/result4 以 60 s 间隔给出。
        N, cols, surf, t_end, dt, t0 = N_GRID, np.arange(0, 2.0, 0.1), 2.0, 10800.0, 1.0, 0.0
    elif prob == 3:
        N, cols, surf, dt, t0 = N_GRID, np.arange(0, 2.0, 0.1), 2.0, 60.0, 0.0
        t_end = drying_time(3, N)
    elif prob == 4:
        N, cols, surf, dt, t0 = N_GRID, np.arange(0, 1.2, 0.1), '药材表面', 60.0, 0.0
        t_end = drying_time(4, N)
    else:
        raise ValueError(prob)

    if limit:
        t_end = min(t_end, float(limit))

    m = M.DryingModel(prob, N=N)
    lbl = surf if isinstance(surf, str) else f'{surf:g}'
    print(f'  网格 N={N}, 输出 {dt:g}s 步长, 列 {cols[0]:g}..{cols[-1]:g} cm + "{lbl}", '
          f't_end={t_end:g}s')
    print(f'  预计输出行数 ≈ {int(t_end/dt)}')

    t0w = time.time()
    times, T, C = stream_sample(m, t_end, dt, cols, t_start=t0, rtol=RTOL, atol=ATOL)
    print(f'  采样完成: {len(times)} 行 × {T.shape[1]} 列, {time.time()-t0w:.1f}s')

    hdr = build_header(prob, cols, surf)
    if limit:
        times, T, C = times[:limit], T[:limit], C[:limit]

    # 模型内部温度用 K (附录3/4 的 exp(-3850/T) 要求 K), 输出按题目要求转回 degC
    T = T - 273.15

    name0 = tpl[0][0]
    if prob in (1, 2):
        name1 = tpl[1][0]
        sheets = [
            (name0, hdr, ([int(t)] + [round(float(v), 4) for v in T[k]]
                          for k, t in enumerate(times))),
            (name1, hdr, ([int(t)] + [round(float(v), 4) for v in C[k]]
                          for k, t in enumerate(times))),
        ]
    else:
        sheets = [
            (name0, hdr, ([int(t)] + [round(float(v), 4) for v in C[k]]
                          for k, t in enumerate(times))),
        ]

    path = rf'{OUT}\result{prob}.xlsx'
    t0w = time.time()
    write_xlsx(path, sheets)
    print(f'  写出 {path}  ({os.path.getsize(path)/1024/1024:.1f} MB, '
          f'{time.time()-t0w:.1f}s)')

    if prob in (3, 4):
        with open(rf'{OUT}\drytime{prob}.txt', 'w') as f:
            f.write(f'{t_end:.1f}\n{t_end/3600:.4f}\n{t_end/86400:.4f}\n')
    return t_end


if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else 'all'
    lim = int(sys.argv[2]) if len(sys.argv) > 2 else None
    if arg == 'all':
        for p in (1, 2, 3, 4):
            run(p, lim)
    else:
        run(int(arg), lim)
