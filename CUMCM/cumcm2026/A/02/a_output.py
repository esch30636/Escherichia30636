# -*- coding: utf-8 -*-
"""A 题输出层: 把 ODE 解采样到规定网格并流式写出 xlsx。

输出列约定
----------
* 问题1/2/3: 药材半径恒为 R0=2 cm, 列为 0, 0.1, ..., 1.9 cm (内部点, 线性插值)
  + 末列"2"(表面, 由边界条件反解, 精度明显高于线性外推)
* 问题4: 药材半径 R(t) 由附件2 给定, 最小 1.198 cm。取 0, 0.1, ..., 1.1 cm
  (全程都位于药材内部的 0.1 cm 等距网格) + 末列"药材表面"。
  另存一份按归一化坐标 xi=r/R(t) 的剖面 (a4_normalized_xi.csv) 以备对照。
"""
import numpy as np
import openpyxl
from openpyxl import Workbook


# --------------------------------------------------------------------------
# 采样
# --------------------------------------------------------------------------
def interp_vec(xi_c, field, xi_q):
    """按 xi 线性插值(两端线性外推)。
    xi_c: (N,) 单元中心; field: (N, nt); xi_q: (nt, nc) -> out: (nt, nc)"""
    N, nt = field.shape
    q = np.asarray(xi_q, float)
    idx = np.searchsorted(xi_c, q)
    idx = np.clip(idx, 1, N - 1)
    x0 = xi_c[idx - 1]
    x1 = xi_c[idx]
    w = (q - x0) / (x1 - x0)
    rows = np.arange(nt)[:, None]
    return (1.0 - w) * field[idx - 1, rows] + w * field[idx, rows]


def surface_bc(model, T, C, t_arr, R_arr):
    """由边界条件反解表面值。T,C: (N, nt); t_arr,R_arr: (nt,)"""
    xi_c = model.xi_c
    lnc = np.log(1.0 / xi_c[-1])
    rho, cp, k = model.props(C[-1, :])
    k = k * model.sc['k']
    D = model.Dfun(C[-1, :], T[-1, :]) * model.sc['D']
    Ta = np.interp(t_arr, model.t_ch, model.T_ch) + model.dT_ch
    Ca = np.interp(t_arr, model.t_ch, model.C_ch) + model.dC_ch
    Rs_T = lnc / k + 1.0 / (model.h_conv * R_arr)
    Rs_C = lnc / D + 1.0 / (model.hm * R_arr)
    T_s = Ta + (T[-1, :] - Ta) / Rs_T / (model.h_conv * R_arr)
    C_s = Ca + (C[-1, :] - Ca) / Rs_C / (model.hm * R_arr)
    return T_s, C_s


def sample(model, Y, t_arr, cols_cm, add_surface=True):
    """把解 Y (2N, nt) 采样到 cols_cm 指定的物理半径(cm) 网格。
    返回 (T_out, C_out), 形状 (nt, len(cols_cm) + (1 if add_surface else 0))。"""
    t_arr = np.asarray(t_arr, float)
    nt = t_arr.size
    T = Y[0::2, :]
    C = Y[1::2, :]
    R_arr = np.asarray([model.R_of(t) for t in t_arr]) if model.problem == 4 \
        else np.full(nt, model.Rmax)

    cols_cm = np.asarray(cols_cm, float)
    if model.problem == 4:
        # xi = r / R(t) 随时间变化
        xi_q = (cols_cm * 1e-2)[None, :] / R_arr[:, None]
    else:
        xi_q = np.broadcast_to((cols_cm * 1e-2)[None, :] / model.Rmax, (nt, len(cols_cm)))

    T_out = interp_vec(model.xi_c, T, xi_q)
    C_out = interp_vec(model.xi_c, C, xi_q)

    if add_surface:
        T_s, C_s = surface_bc(model, T, C, t_arr, R_arr)
        T_out = np.column_stack([T_out, T_s])
        C_out = np.column_stack([C_out, C_s])
    return T_out, C_out


def stream_sample(model, t_end, dt_out, cols_cm, t_start=0.0, rtol=1e-8,
                  atol=1e-10, batch=20000, verbose=True):
    """一次积分, 分批采样。返回 (times, T_out, C_out)。"""
    import time as _t
    t0 = _t.time()
    sol = model.solve(t_end, rtol=rtol, atol=atol)
    if verbose:
        print(f'  积分完成: {sol.t.size} 步, {_t.time()-t0:.1f}s', flush=True)

    t_out = np.arange(t_start + dt_out, t_end + 1e-9, dt_out)
    t_out = t_out[t_out > t_start]
    n = t_out.size
    ncol = len(cols_cm) + 1
    T_all = np.empty((n, ncol))
    C_all = np.empty((n, ncol))
    for s in range(0, n, batch):
        e = min(s + batch, n)
        ts = t_out[s:e]
        Y = sol.sol(ts)
        To, Co = sample(model, Y, ts, cols_cm, add_surface=True)
        T_all[s:e] = To
        C_all[s:e] = Co
        if verbose and (s // batch) % 10 == 0:
            print(f'    采样 {e}/{n}', flush=True)
    return t_out, T_all, C_all


# --------------------------------------------------------------------------
# 写出 xlsx (流式, 适用于 26 万行级别)
# --------------------------------------------------------------------------
def write_xlsx(path, sheets):
    """sheets: list of (sheet_name, header_row, rows_iterable)
    header_row: list[str];  rows: iterable of list (长度与 header 一致)"""
    wb = Workbook(write_only=True)
    for name, header, rows in sheets:
        ws = wb.create_sheet(title=name)
        ws.append(list(header))
        for r in rows:
            ws.append(r)
    wb.save(path)


def fmt4(v):
    return None if v is None else round(float(v), 4)


def _row_iter(times, arr, ncol):
    for k in range(len(times)):
        yield [int(times[k])] + [fmt4(arr[k, j]) for j in range(ncol)]
