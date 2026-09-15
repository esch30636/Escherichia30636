# -*- coding: utf-8 -*-
"""补充结果 —— 问题2 的“全流程”数据 (60 s 间隔) 与关键数字汇总。

理由: result2.xlsx 按题目“3 h 内”的窗口给出 1 s 间隔结果(与 问题1 的 “1800 s 内” 同构);
而整个烘干过程长达 2-3 天, 1 s 间隔将产生 20 万行以上。问题2 与 问题3 使用同一组
经验公式(附录3)与同一组边界条件, 二者模型完全一致, 故全流程结果在此以 60 s 间隔补充,
既保留了完整过程信息, 又满足支撑材料 20 MB 的容量限制。
"""
import sys, io, json, os
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
import numpy as np
import a_model as M
from a_output import sample, write_xlsx
from solve_a import drying_time, build_header, tpl_info, RTOL, ATOL, N_GRID

OUT = r'D:\CUMCM\A\out'
N = N_GRID


def main():
    os.makedirs(OUT, exist_ok=True)

    te3 = drying_time(3, N)
    m3 = M.DryingModel(3, N=N)
    cols = np.arange(0, 2.0, 0.1)
    surf = 2.0

    sol = m3.solve(te3, rtol=RTOL, atol=ATOL)
    t_out = np.arange(60.0, te3 + 1e-9, 60.0)
    n = t_out.size
    Y = sol.sol(t_out)
    T, C = sample(m3, Y, t_out, cols, add_surface=True)
    T = T - 273.15

    hdr = build_header(3, cols, surf)
    tpl = tpl_info(2)
    sheets = [
        (tpl[0][0], hdr, ([int(t)] + [round(float(v), 4) for v in T[k]]
                          for k, t in enumerate(t_out))),
        (tpl[1][0], hdr, ([int(t)] + [round(float(v), 4) for v in C[k]]
                          for k, t in enumerate(t_out))),
    ]
    path = rf'{OUT}\result2_全流程_60s.xlsx'
    write_xlsx(path, sheets)
    print(f'写出 {path}  ({n} 行 × {len(hdr)} 列 × 2 表, '
          f'{os.path.getsize(path)/1024/1024:.2f} MB)')

    # ---------------- 关键数字汇总 ----------------
    # 表面/中心 的 温度峰值 与 水分浓度过程
    Ts, Cs = T[:, -1], C[:, -1]
    Tc, Cc = T[:, 0], C[:, 0]
    summary = {
        '问题3_烘干时间_s': te3,
        '问题3_烘干时间_h': te3 / 3600.0,
        '问题3_烘干时间_天': te3 / 86400.0,
        '表面温度峰值_degC': float(Ts.max()),
        '表面温度峰值时刻_s': float(t_out[int(Ts.argmax())]),
        '中心温度峰值_degC': float(Tc.max()),
        '结束_表面C': float(Cs[-1]),
        '结束_中心C': float(Cc[-1]),
        '结束_表面T': float(Ts[-1]),
        '结束_中心T': float(Tc[-1]),
        '表5时刻_h': [6.0 * k for k in range(1, int(te3 // 21600) + 1)],
    }
    with open(rf'{OUT}\summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)

    print('\n关键数字:')
    for k, v in summary.items():
        print(f'  {k:>22}: {v}')


if __name__ == '__main__':
    main()
