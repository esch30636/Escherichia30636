# -*- coding: utf-8 -*-
"""A 题 问题 1 —— 预热平衡阶段药材温度与水分浓度变化规律(独立求解代码)

完整解题报告(IEEE 格式)见同目录 problem1.md。

用法(legion, conda 环境 cumcm_a, 工作目录 D:\\CUMCM\\A\\01):
    python problem1.py            # 完整流程: 量级诊断 -> 表1/表2 -> result1.xlsx -> fig1_p1.png
    python problem1.py tables     # 仅打印 表1/表2 与关键数字(读 tables1.json, 不再求解)

依赖:
    a_model.py / a_output.py   同目录(A 根目录验证版的拷贝, 2026-09-11)
    附件1(烘房温湿度) + result1.xlsx 模板   D:\\CUMCM\\A\\data
输出(同目录):
    result1.xlsx   t = 1..1800 s, 1 s 间隔 × r = 0, 0.1, ..., 1.9, 2 cm, 4 位小数,
                   两个工作表("温度"/"水分浓度", 与模板一致)
    tables1.json   表1/表2 原始值
    fig1_p1.png    温度/水分浓度剖面图(7 个时刻)
"""
import os, sys, json, time
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
import numpy as np
import openpyxl
import a_model as M
from a_output import stream_sample, write_xlsx, sample

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = r'D:\CUMCM\A\data'
N_GRID = 400
RTOL, ATOL = 1e-8, 1e-10
T_END = 1800.0                              # 预热平衡阶段 30 min
T_TABLE = [100, 300, 600, 900, 1200, 1500, 1800]   # 表1/表2 的行
R_TABLE = [0.0, 0.5, 1.0, 1.5, 2.0]                # 表1/表2 的列(末列"2"= 表面, 由边界条件反解)


# --------------------------------------------------------------------------
# 0) 量级诊断: 求解前的解析预估(特征时间与 Biot 数)
# --------------------------------------------------------------------------
def diagnostics():
    print('=== 0) 量级诊断(解析预估) ===')
    rho, cp, k = 820.0, 2600.0, 0.36
    R = 0.02
    D0 = 7.0e-9 * np.exp(-0.89 / 2.55)
    alpha = k / (rho * cp)
    tau_T = R * R / alpha
    tau_C = R * R / D0
    Bi = M.H_CONV * R / k
    Bi_m = M.HM * R / D0
    print(f'D(C=2.55) = {D0:.4e} m^2/s;  alpha = k/(rho*cp) = {alpha:.4e} m^2/s')
    print(f'tau_T = R^2/alpha = {tau_T:.1f} s = {tau_T/60:.2f} min(热平衡特征时间)')
    print(f'tau_C = R^2/D    = {tau_C:.1f} s = {tau_C/3600:.2f} h(水分扩散特征时间)')
    print(f'tau_C/tau_T = {tau_C/tau_T:.1f};  Bi = h*R/k = {Bi:.4f};  '
          f'Bi_m = hm*R/D0 = {Bi_m:.4f}')
    print()
    print('=== 1) 附件1 烘房条件(表1/表2 各时刻) ===')
    t, T, C = M.load_chamber()
    for tt in T_TABLE:
        print(f't = {tt:>5d} s:  T_air = {np.interp(tt, t, T) - 273.15:8.4f} degC   '
              f'C_air = {np.interp(tt, t, C):.5f}')
    tR, Rv = M.load_radius()
    R1800 = float(np.interp(1800.0, tR, Rv))
    print(f'附件2 半径: R(0) = {Rv[0]*100:.4f} cm, R(1800 s) = {R1800*100:.4f} cm'
          f'(30 min 收缩 {(Rv[0]-R1800)/Rv[0]*100:.3f}%)')


# --------------------------------------------------------------------------
# 1) 表1/表2 + 1800 s 剖面
# --------------------------------------------------------------------------
def r4(v):
    return f'{float(v):.4f}'


def print_tables(T, C):
    print('=== 2) 表1  30 分钟内药材的温度 (degC, 4 位小数) ===')
    print('时间/s    0         0.5       1         1.5       2')
    for t, row in zip(T_TABLE, T):
        print(f'{t:>7d}' + ''.join(f'{v:>10.4f}' for v in row))
    print()
    print('=== 3) 表2  30 分钟内药材的水分浓度 (kg/kg, 4 位小数) ===')
    print('时间/s    0         0.5       1         1.5       2')
    for t, row in zip(T_TABLE, C):
        print(f'{t:>7d}' + ''.join(f'{v:>10.4f}' for v in row))
    print()
    Ts, Cs = T[-1], C[-1]
    print(f'=== 4) 关键数字 (t = 1800 s) ===')
    print(f'中心温度 {Ts[0]:.4f} degC(初值 28, 温升 +{Ts[0]-28:.4f})')
    print(f'表面温度 {Ts[-1]:.4f} degC(初值 28, 温升 +{Ts[-1]-28:.4f})')
    print(f'表面水分 {Cs[-1]:.4f}(初值 2.55, 降幅 {(2.55-Cs[-1])/2.55*100:.1f}%)')
    print(f'内部水分: r=1.5 cm {Cs[3]:.4f}, r=1.0 cm {Cs[2]:.4f}, '
          f'r=0.5 cm {Cs[1]:.4f}, 中心 {Cs[0]:.4f}')


def solve_tables():
    m = M.DryingModel(1, N=N_GRID)
    t0 = time.time()
    sol = m.solve(T_END, rtol=RTOL, atol=ATOL)
    print(f'积分完成: {sol.t.size} 步, {time.time()-t0:.1f}s', flush=True)
    ts = np.asarray(T_TABLE, float)
    Y = sol.sol(ts)
    # 内部列 0, 0.5, 1, 1.5 cm 线性插值; 末列"2"(表面)由边界条件反解(sample 的 add_surface)
    T, C = sample(m, Y, ts, np.asarray(R_TABLE[:-1], float), add_surface=True)
    T = T - 273.15                       # 输出单位 °C (与 out/tables.json 一致)
    with open(os.path.join(HERE, 'tables1.json'), 'w', encoding='utf-8') as f:
        json.dump({'times': T_TABLE, 'cols': [str(c) for c in R_TABLE],
                   'T': T.tolist(), 'C': C.tolist()}, f, ensure_ascii=False, indent=1)
    print('表1/表2 原始值 -> tables1.json')
    print_tables(T, C)
    # 1800 s 的 0.1 cm 剖面(观察水分渗透深度)
    Y1 = sol.sol(np.array([1800.0]))
    cols = np.arange(0, 1.95, 0.1)
    Tc, Cc = sample(m, Y1, np.array([1800.0]), cols, add_surface=True)
    print('=== 5) t = 1800 s 径向剖面 (0.1 cm 间隔, 末列表面) ===')
    for c, tv, cv in zip(np.append(cols, 2.0), Tc[0], Cc[0]):
        print(f'r = {c:>4.1f} cm:  T = {tv-273.15:8.4f} degC   C = {cv:8.4f}')
    return m


# --------------------------------------------------------------------------
# 2) result1.xlsx(模板同款表头, 流式写出)
# --------------------------------------------------------------------------
def tpl_info(prob):
    wb = openpyxl.load_workbook(rf'{DATA}\templates\result{prob}.xlsx', read_only=True)
    out = []
    for ws in wb.worksheets:
        hdr = next(ws.iter_rows(max_row=1, values_only=True))
        out.append((ws.title, [h for h in hdr if h is not None]))
    wb.close()
    return out


def build_header(cols_cm, surface_label):
    """表头与模板一致: 数值列用数值, 整数列写成整数。"""
    head = ['时间\\到药材中心的距离']
    cols = list(cols_cm) + ([] if isinstance(surface_label, str) else [surface_label])
    for c in cols:
        cf = float(c)
        head.append(int(round(cf)) if abs(cf - round(cf)) < 1e-9 else round(cf, 10))
    if isinstance(surface_label, str):
        head.append(surface_label)
    return head


def write_result1(m):
    tpl = tpl_info(1)
    print(f'模板工作表: {[n for n, _ in tpl]}')
    cols = np.arange(0, 2.0, 0.1)
    hdr = build_header(cols, 2.0)
    t0 = time.time()
    times, T, C = stream_sample(m, T_END, 1.0, cols, t_start=0.0, rtol=RTOL, atol=ATOL)
    T = T - 273.15                       # 模型内部用 K, 输出按题目要求转回 degC
    sheets = [
        (tpl[0][0], hdr, ([int(t)] + [round(float(v), 4) for v in T[k]]
                          for k, t in enumerate(times))),
        (tpl[1][0], hdr, ([int(t)] + [round(float(v), 4) for v in C[k]]
                          for k, t in enumerate(times))),
    ]
    path = os.path.join(HERE, 'result1.xlsx')
    write_xlsx(path, sheets)
    print(f'result1.xlsx: {len(times)} 行 × 2 工作表, '
          f'{os.path.getsize(path)/1024:.1f} KB, {time.time()-t0:.1f}s')


# --------------------------------------------------------------------------
# 3) 插图: 温度/水分浓度剖面
# --------------------------------------------------------------------------
def make_figure():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['figure.dpi'] = 150
    plt.rcParams['savefig.bbox'] = 'tight'
    CM = plt.cm.viridis

    m = M.DryingModel(1, N=N_GRID)
    sol = m.solve(T_END, rtol=RTOL, atol=ATOL)
    ts = np.asarray(T_TABLE, float)
    Y = sol.sol(ts)
    cols = np.arange(0, 1.95, 0.2)                # 0, 0.2, ..., 1.8 + 表面 2.0
    T, C = sample(m, Y, ts, cols, add_surface=True)
    x = np.append(cols, 2.0)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    for i, lab in enumerate([f'{t} s' for t in T_TABLE]):
        c = CM(i / (len(ts) - 1))
        ax[0].plot(x, T[i] - 273.15, 'o-', ms=3, lw=1.5, color=c, label=lab)
        ax[1].plot(x, C[i], 'o-', ms=3, lw=1.5, color=c, label=lab)
    ax[0].set_ylabel('温度 / °C')
    ax[1].set_ylabel('水分浓度 / (kg/kg)')
    for a, tt in zip(ax, ('(a) 温度分布', '(b) 水分浓度分布')):
        a.set_xlabel('到药材中心的距离 / cm')
        a.grid(alpha=.3)
        a.set_title(tt)
    ax[0].legend(fontsize=8)
    fig.suptitle('问题1 预热平衡阶段: 温度与水分浓度分布(30 min 内)', fontsize=12)
    path = os.path.join(HERE, 'fig1_p1.png')
    fig.savefig(path)
    plt.close(fig)
    print(f'fig1_p1.png -> {os.path.getsize(path)/1024:.1f} KB')


# --------------------------------------------------------------------------
# 4) 问题1 专属验证
# --------------------------------------------------------------------------
def verify():
    """(a) 水分质量守恒残差; (b) 网格收敛(Richardson 外推, 二阶)。"""
    trapz = getattr(np, 'trapezoid', None) or np.trapz

    # (a) 守恒: 归一化总水分 M~ = int_0^1 C xi dxi,
    #     dM~/dt = -hm (C_s - C_air)/R  (由边界通量解析给出)。
    #     表面通量在 t=0 附近有 sqrt(t) 奇异性, 通量积分用 1 s 细网格梯形法。
    print('=== (a) 水分质量守恒 ===')
    m = M.DryingModel(1, N=N_GRID)
    sol = m.solve(T_END, rtol=RTOL, atol=ATOL)
    tt = np.arange(0.0, T_END + 1e-9, 1.0)         # 1 s 间隔
    Y = sol.sol(tt)
    xi = m.xi_c
    Mt = (Y[1::2, :] * xi[:, None]).sum(axis=0) * m.dxi
    _, Cs = sample(m, Y, tt, np.asarray([0.0]), add_surface=True)
    flux = m.hm * (Cs[:, -1] - np.interp(tt, m.t_ch, m.C_ch)) / m.Rmax
    cum = np.zeros(len(tt))
    for k in range(1, len(tt)):
        cum[k] = trapz(flux[:k + 1], tt[:k + 1])
    resid = (Mt - Mt[0]) + cum
    print(f'总水分 M~(0) = {Mt[0]:.6f}; 最大 |残差| = {np.abs(resid).max():.3e}, '
          f'相对 {np.abs(resid).max()/Mt[0]:.3e}')

    # (b) 网格收敛: 1800 s 的表面 C 与中心 T
    print('=== (b) 网格收敛 (t = 1800 s) ===')
    vals = {}
    for N in (100, 200, 400, 800):
        mn = M.DryingModel(1, N=N)
        sn = mn.solve(T_END, rtol=RTOL, atol=ATOL)
        Yn = sn.sol(np.array([1800.0]))
        Tn, Cn = sample(mn, Yn, np.array([1800.0]), np.asarray([0.0]), add_surface=True)
        vals[N] = (Tn[0, 0] - 273.15, Cn[0, 0], Cn[0, -1])
        print(f'N={N:>4}:  中心 T = {vals[N][0]:.6f} C   '
              f'中心 C = {vals[N][1]:.6f}   表面 C = {vals[N][2]:.6f}')
    for key, lab in ((2, '表面 C'), (0, '中心 T')):
        e = abs(vals[800][key] - vals[400][key]) * 4.0 / 3.0     # 二阶 Richardson
        print(f'N=400 的 {lab} 误差估计 = {e:.2e}(4 位小数阈值 5e-5, 比值 {e/5e-5:.3f})')
    # 收敛阶: vN = v∞ + c N^{-p}  =>  (v200-v400)/(v400-v800) = 2^p
    p = np.log2(abs(vals[200][2] - vals[400][2]) / abs(vals[400][2] - vals[800][2]))
    print(f'表面 C 收敛阶 ≈ {p:.2f}')

# --------------------------------------------------------------------------
def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if mode == 'tables':
        with open(os.path.join(HERE, 'tables1.json'), encoding='utf-8') as f:
            d = json.load(f)
        print_tables(np.asarray(d['T']), np.asarray(d['C']))
        return
    if mode == 'verify':
        verify()
        return
    diagnostics()
    m = solve_tables()
    write_result1(m)
    make_figure()
    print('完成。')


if __name__ == '__main__':
    main()
