# -*- coding: utf-8 -*-
"""result2 的第二种理解: 1 s 间隔输出到烘干结束(全流程)。

题面"将每隔1 s 的完整结果保存到 result2.xlsx"有两种读法:
  理解一(默认交付, solve_a.py): 作用域承接前一句的"3 h 内"
        -> out/result2.xlsx (10800 行)
  理解二(本脚本): "完整结果"指整个烘干过程
        -> result2_full_1s/result2.xlsx (205862 行)
本脚本按理解二生成, 与理解一同模板、同表头、同精度, 仅行数不同。
文件约 20.6 万行 ≈ 26 MB, 超出支撑材料 20 MB 上限, 故放在独立目录,
不进入默认交付集; 打包时二选一。
"""
import sys, os, time
# 就地重配置, 不要新建 TextIOWrapper —— 否则被 import 时旧 wrapper 析构会关掉共享 buffer
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
import numpy as np
import a_model as M
from a_output import stream_sample, write_xlsx
from solve_a import build_header, drying_time, tpl_info

OUT = r'D:\CUMCM\A\result2_full_1s'
N_GRID = 400
RTOL, ATOL = 1e-8, 1e-10


def run():
    os.makedirs(OUT, exist_ok=True)
    prob = 2
    cols = np.arange(0, 2.0, 0.1)
    surf = 2.0
    # 问题2 与问题3 同用附录3 物性, 烘干时间相同 ≈ 205862.4 s
    t_end = drying_time(prob, N=N_GRID)
    m = M.DryingModel(prob, N=N_GRID)
    print(f'网格 N={N_GRID}, 1 s 步长, 列 0..1.9 cm + 表面, t_end={t_end:.1f}s, '
          f'预计 {int(t_end)} 行')

    t0 = time.time()
    times, T, C = stream_sample(m, t_end, 1.0, cols, t_start=0.0, rtol=RTOL, atol=ATOL)
    print(f'采样完成: {len(times)} 行 × {T.shape[1]} 列, {time.time()-t0:.1f}s')

    # 模型内部温度用 K (附录3/4 的 exp(-3850/T) 要求 K), 输出转回 degC
    T = T - 273.15

    tpl = tpl_info(prob)
    hdr = build_header(prob, cols, surf)
    name0, name1 = tpl[0][0], tpl[1][0]
    sheets = [
        (name0, hdr, ([int(t)] + [round(float(v), 4) for v in T[k]]
                      for k, t in enumerate(times))),
        (name1, hdr, ([int(t)] + [round(float(v), 4) for v in C[k]]
                      for k, t in enumerate(times))),
    ]
    path = rf'{OUT}\result2.xlsx'
    t0 = time.time()
    write_xlsx(path, sheets)
    print(f'写出 {path} ({os.path.getsize(path)/1024/1024:.1f} MB, '
          f'{time.time()-t0:.1f}s)')


if __name__ == '__main__':
    run()
