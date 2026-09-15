# -*- coding: utf-8 -*-
"""A 题 问题 2 —— 整个烘干过程药材温度与水分浓度变化规律(独立求解代码)

完整解题报告(IEEE 格式)见同目录 problem2.md。

用法(legion, conda 环境 cumcm_a, 工作目录 D:\\CUMCM\\A\\02):
    python problem2.py            # 完整流程: 量级诊断 -> 表3/表4 -> result2.xlsx -> fig2_p2.png
    python problem2.py diag       # 仅量级诊断(附录3 物性 + 附件1 两阶段结构, 不求解)
    python problem2.py tables     # 仅打印 表3/表4 与关键数字(读 tables2.json, 不再求解)
    python problem2.py verify     # 问题2 专属验证: 质量守恒 + 网格收敛

依赖:
    a_model.py / a_output.py   同目录(A 根目录验证版的拷贝, 2026-09-11)
    附件1(烘房温湿度) + result2.xlsx 模板   D:\\CUMCM\\A\\data
输出(同目录):
    result2.xlsx   t = 1..10800 s(3 h), 1 s 间隔 × r = 0, 0.1, ..., 1.9, 2 cm, 4 位小数,
                   两个工作表("温度"/"水分浓度", 与模板一致)
    tables2.json   表3/表4 原始值
    fig2_p2.png    温度/水分浓度剖面图(0.5 ~ 3.0 h, 6 个时刻)
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
T_END = 10800.0                                     # 3 h 考察窗(与表3/表4 一致)
T_TABLE_H = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]          # 表3/表4 的行(小时)
T_TABLE = [h * 3600.0 for h in T_TABLE_H]
R_TABLE = [0.0, 0.5, 1.0, 1.5, 2.0]                 # 表3/表4 的列(末列"2"= 表面, 由边界条件反解)
T_HOLD = 7200.0                                     # 附件1 恒温干燥段起点(烘房达设定值)


# --------------------------------------------------------------------------
# 0) 量级诊断: 附录3 物性、特征时间与附件1 两阶段结构(求解前解析预估)
# --------------------------------------------------------------------------
def diagnostics():
    print('=== 0) 量级诊断(解析预估, 附录3 物性) ===')
    R = M.R0
    rho, cp, k = (float(v[0]) for v in M.props_p3(np.array([M.C_INIT])))
    T0K = M.T_INIT + 273.15
    D0 = float(M.D_p3(np.array([M.C_INIT]), np.array([T0K]))[0])
    alpha = k / (rho * cp)
    tau_T = R * R / alpha
    tau_C = R * R / D0
    Bi = M.H_CONV * R / k
    Bi_m = M.HM * R / D0
    print(f'附录3 物性(C = {M.C_INIT}):  rho = {rho:.4f} kg/m3,  cp = {cp:.2f} J/(kg K),  '
          f'k = {k:.6f} W/(m K)')
    print(f'D(C = {M.C_INIT}, T = {M.T_INIT} degC) = {D0:.4e} m^2/s;  '
          f'alpha = k/(rho*cp) = {alpha:.4e} m^2/s')
    print(f'tau_T = R^2/alpha = {tau_T:.1f} s = {tau_T/60:.2f} min(热平衡特征时间)')
    print(f'tau_C = R^2/D    = {tau_C:.1f} s = {tau_C/3600:.2f} h(水分扩散特征时间)')
    print(f'tau_C/tau_T = {tau_C/tau_T:.1f};  Bi = h*R/k = {Bi:.4f};  '
          f'Bi_m = hm*R/D = {Bi_m:.4f}')

    def D_of(C, Tc=M.T_INIT):
        return float(M.D_p3(np.array([C]), np.array([Tc + 273.15]))[0])

    print('物性的含水率/温度依赖(烘干后期变慢的根源):')
    print(f'  D(0.5)/D(2.55)  = {D_of(0.5)/D0:.4f}   (C 降至 0.5 时扩散放慢 '
          f'{1/(D_of(0.5)/D0):.1f} 倍)')
    print(f'  D(0.15)/D(2.55) = {D_of(0.15)/D0:.4f}   (C 降至 0.15 时扩散放慢 '
          f'{1/(D_of(0.15)/D0):.1f} 倍)')
    print(f'  D(60degC)/D(28degC) = {D_of(M.C_INIT, 60.0)/D0:.4f}   '
          f'(Arrhenius exp(-3850/T), 每升 1 K 约 +3.7%)')

    print()
    print('=== 1) 附件1 烘房条件与两阶段结构 ===')
    t, T, C = M.load_chamber()
    dt = np.unique(np.diff(t))
    print(f'数据范围: t = {t[0]:.0f} .. {t[-1]:.0f} s({t.size} 点, 间隔 '
          f'{dt[0]:.0f} s)' if dt.size == 1 else f'间隔非均匀')
    msk = t >= T_HOLD
    print(f'恒温干燥段(附件1 后 2 h, t = {T_HOLD:.0f} .. {t[-1]:.0f} s, {msk.sum()} 点):')
    print(f'  T_air = {T[msk].mean()-273.15:.4f} ± {T[msk].std():.4f} degC,  '
          f'C_air = {C[msk].mean():.5f} ± {C[msk].std():.5f} kg/kg')
    print('表3/表4 各时刻的烘房条件(线性插值):')
    for h, tt in zip(T_TABLE_H, T_TABLE):
        print(f'  t = {h:>3.1f} h({tt:>6.0f} s):  T_air = {np.interp(tt, t, T)-273.15:8.4f} degC   '
              f'C_air = {np.interp(tt, t, C):.5f}')
    print(f'维持末值假设(问题2/3 全流程): t > {t[-1]:.0f} s 后 T_air = {T[-1]-273.15:.4f} degC, '
          f'C_air = {C[-1]:.5f}')


# --------------------------------------------------------------------------
# 1) 表3/表4 + 3 h 剖面
# --------------------------------------------------------------------------
def print_tables(T, C):
    print('=== 2) 表3  3 小时内药材的温度 (degC, 4 位小数) ===')
    print('时间/h    0         0.5       1         1.5       2')
    for h, row in zip(T_TABLE_H, T):
        print(f'{h:>7.1f}' + ''.join(f'{v:>10.4f}' for v in row))
    print()
    print('=== 3) 表4  3 小时内药材的水分浓度 (kg/kg, 4 位小数) ===')
    print('时间/h    0         0.5       1         1.5       2')
    for h, row in zip(T_TABLE_H, C):
        print(f'{h:>7.1f}' + ''.join(f'{v:>10.4f}' for v in row))
    print()
    Ts, Cs = T[-1], C[-1]
    print('=== 4) 关键数字(t = 3 h) ===')
    print(f'中心温度 {Ts[0]:.4f} degC(初值 28, 温升 +{Ts[0]-28:.4f})')
    print(f'表面温度 {Ts[-1]:.4f} degC(初值 28, 温升 +{Ts[-1]-28:.4f})')
    print(f'表面水分 {Cs[-1]:.4f}(初值 2.55, 降幅 {(2.55-Cs[-1])/2.55*100:.1f}%)')
    print(f'中心水分 {Cs[0]:.4f}(全场最大, 降幅 {(2.55-Cs[0])/2.55*100:.1f}%)')
    print(f'径向温差 {Ts[-1]-Ts[0]:.4f} degC;  最大-最小水分差 {Cs[0]-Cs[-1]:.4f} kg/kg')


def solve_tables():
    m = M.DryingModel(2, N=N_GRID)
    t0 = time.time()
    sol = m.solve(T_END, rtol=RTOL, atol=ATOL)
    print(f'积分完成: {sol.t.size} 步, {time.time()-t0:.1f}s', flush=True)
    ts = np.asarray(T_TABLE, float)
    Y = sol.sol(ts)
    # 内部列 0, 0.5, 1, 1.5 cm 线性插值; 末列"2"(表面)由边界条件反解(sample 的 add_surface)
    T, C = sample(m, Y, ts, np.asarray(R_TABLE[:-1], float), add_surface=True)
    T = T - 273.15                       # 输出单位 °C (与 out/tables.json 一致)
    with open(os.path.join(HERE, 'tables2.json'), 'w', encoding='utf-8') as f:
        json.dump({'times_h': T_TABLE_H, 'cols': [str(c) for c in R_TABLE],
                   'T': T.tolist(), 'C': C.tolist()}, f, ensure_ascii=False, indent=1)
    print('表3/表4 原始值 -> tables2.json')
    print_tables(T, C)
    # 3 h 的 0.1 cm 剖面(观察干燥前沿深度)
    Y1 = sol.sol(np.array([T_END]))
    cols = np.arange(0, 1.95, 0.1)
    Tc, Cc = sample(m, Y1, np.array([T_END]), cols, add_surface=True)
    print('=== 5) t = 3 h 径向剖面 (0.1 cm 间隔, 末列表面) ===')
    for c, tv, cv in zip(np.append(cols, 2.0), Tc[0], Cc[0]):
        print(f'r = {c:>4.1f} cm:  T = {tv-273.15:8.4f} degC   C = {cv:8.4f}')
    return m


# --------------------------------------------------------------------------
# 2) result2.xlsx(模板同款表头, 流式写出)
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


def write_result2(m):
    tpl = tpl_info(2)
    print(f'模板工作表: {[n for n, _ in tpl]}')
    print(f'模板表头: {tpl[0][1][:4]} ... {tpl[0][1][-2:]}')
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
    path = os.path.join(HERE, 'result2.xlsx')
    write_xlsx(path, sheets)
    print(f'result2.xlsx: {len(times)} 行 × 2 工作表, '
          f'{os.path.getsize(path)/1024:.1f} KB, {time.time()-t0:.1f}s')


# --------------------------------------------------------------------------
# 3) 插图: 温度/水分浓度剖面(0.5 ~ 3.0 h)
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

    m = M.DryingModel(2, N=N_GRID)
    sol = m.solve(T_END, rtol=RTOL, atol=ATOL)
    ts = np.asarray(T_TABLE, float)
    Y = sol.sol(ts)
    cols = np.arange(0, 1.95, 0.2)                # 0, 0.2, ..., 1.8 + 表面 2.0
    T, C = sample(m, Y, ts, cols, add_surface=True)
    x = np.append(cols, 2.0)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    for i, lab in enumerate([f'{h:g} h' for h in T_TABLE_H]):
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
    fig.suptitle('问题2 烘干前 3 h(预热平衡→恒温干燥): 温度与水分浓度分布', fontsize=12)
    path = os.path.join(HERE, 'fig2_p2.png')
    fig.savefig(path)
    plt.close(fig)
    print(f'fig2_p2.png -> {os.path.getsize(path)/1024:.1f} KB')


# --------------------------------------------------------------------------
# 4) 问题2 专属验证
# --------------------------------------------------------------------------
def verify():
    """(a) 水分质量守恒残差; (b) 网格收敛(Richardson 外推, 二阶)。"""
    trapz = getattr(np, 'trapezoid', None) or np.trapz

    # (a) 守恒: 归一化总水分 M~ = int_0^1 C xi dxi,
    #     dM~/dt = -hm (C_s - C_air)/R  (由边界通量解析给出)。
    #     表面通量在 t=0 附近有 sqrt(t) 奇异性, 通量积分用 1 s 细网格梯形法。
    print('=== (a) 水分质量守恒 ===')
    m = M.DryingModel(2, N=N_GRID)
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

    # (b) 网格收敛: 3 h 的表面 C 与中心 T
    print('=== (b) 网格收敛 (t = 3 h) ===')
    vals = {}
    for N in (100, 200, 400, 800):
        mn = M.DryingModel(2, N=N)
        sn = mn.solve(T_END, rtol=RTOL, atol=ATOL)
        Yn = sn.sol(np.array([T_END]))
        Tn, Cn = sample(mn, Yn, np.array([T_END]), np.asarray([0.0]), add_surface=True)
        vals[N] = (Tn[0, 0] - 273.15, Cn[0, 0], Cn[0, -1])
        print(f'N={N:>4}:  中心 T = {vals[N][0]:.9f} C   '
              f'中心 C = {vals[N][1]:.9f}   表面 C = {vals[N][2]:.9f}')
    for key, lab in ((2, '表面 C'), (0, '中心 T')):
        e = abs(vals[800][key] - vals[400][key]) * 4.0 / 3.0     # 二阶 Richardson
        print(f'N=400 的 {lab} 误差估计 = {e:.2e}(4 位小数阈值 5e-5, 比值 {e/5e-5:.3f})')
    # 收敛阶: vN = v∞ + c N^{-p}  =>  (v100-v200)/(v200-v400) = 2^p
    # N=400→800 段的差值已接近 BDF 时间容差的底噪, 仅作参考
    p1 = np.log2(abs(vals[100][2] - vals[200][2]) / abs(vals[200][2] - vals[400][2]))
    p2 = np.log2(abs(vals[200][2] - vals[400][2]) / abs(vals[400][2] - vals[800][2]))
    print(f'表面 C 收敛阶: 100→400 段 ≈ {p1:.2f};  400→800 段 ≈ {p2:.2f}'
          f'(受时间积分容差底噪影响, 仅供参考)')

# --------------------------------------------------------------------------
def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if mode == 'diag':
        diagnostics()
        return
    if mode == 'tables':
        with open(os.path.join(HERE, 'tables2.json'), encoding='utf-8') as f:
            d = json.load(f)
        print_tables(np.asarray(d['T']), np.asarray(d['C']))
        return
    if mode == 'verify':
        verify()
        return
    diagnostics()
    m = solve_tables()
    write_result2(m)
    make_figure()
    print('完成。')


if __name__ == '__main__':
    main()
