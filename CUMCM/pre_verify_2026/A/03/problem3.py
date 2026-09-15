# -*- coding: utf-8 -*-
"""A 题 问题 3 —— 药材烘干所需时间与烘干过程水分浓度(独立求解代码)

完整解题报告(IEEE 格式)见同目录 problem3.md。

用法(legion, conda 环境 cumcm_a, 工作目录 D:\\CUMCM\\A\\03):
    python problem3.py            # 完整流程: 量级诊断 -> 表5 -> result3.xlsx -> fig3_p3.png
    python problem3.py diag       # 仅量级诊断(附录3 物性 + 烘干判据 + 自锁效应预估)
    python problem3.py tables     # 仅打印 表5(读 tables3.json, 不再求解)
    python problem3.py verify     # 问题3 专属验证: 质量守恒 + 烘干时间网格收敛 + 与问题4 交叉复核

依赖:
    a_model.py / a_output.py   同目录(A 根目录验证版的拷贝, 2026-09-11)
    附件1(烘房温湿度) + result3.xlsx 模板   D:\\CUMCM\\A\\data
输出(同目录):
    result3.xlsx   t = 60, 120, ..., 205860 s(至烘干结束), 60 s 间隔 × r = 0, 0.1, ..., 2 cm,
                   4 位小数, 单工作表(与模板一致, 只含水分浓度)
    tables3.json   表5 原始值
    fig3_p3.png    表5 时刻水分剖面 + 全流程烘干曲线
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
C_END = 0.15                                # 烘干判据: 药材各处水分浓度 < 0.15 kg/kg
T_TABLE_H = [6.0, 12.0, 18.0, 24.0, 30.0, 36.0, 42.0, 48.0, 54.0]   # 表5 的行(小时)
R_TABLE = [0.0, 0.5, 1.0, 1.5, 2.0]        # 表5 的列(末列"2"= 表面, 由边界条件反解)
DT_OUT = 60.0                              # result3.xlsx 输出间隔(题面规定)
T_MAX = 300000.0                           # 3 天超窗(判据必然在此之前触发)
T_HOLD = 7200.0                            # 附件1 恒温干燥段起点
LAM1 = 2.404825557695773                   # J0 的第一个零点(柱对称基模特征值)


def make_event():
    def ev(t, y):
        return y[1::2].max() - C_END
    ev.terminal = True
    ev.direction = -1
    return ev


def drying_time(model, t_max=T_MAX):
    """求 max C < C_END 的时刻(事件函数在最大水分浓度越过 0.15 时终止积分)。"""
    t0 = time.time()
    sol = model.solve(t_max, events=[make_event()], rtol=RTOL, atol=ATOL)
    te = float(sol.t_events[0][0]) if len(sol.t_events[0]) else np.nan
    print(f'  烘干时间 t_end = {te:.1f} s = {te/3600:.4f} h = {te/86400:.4f} 天'
          f'   ({sol.t.size} 步, {time.time()-t0:.1f}s)')
    return te, sol


# --------------------------------------------------------------------------
# 0) 量级诊断: 附录3 物性、特征时间、烘干判据与自锁效应(求解前解析预估)
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
    tau1 = R * R / (LAM1 ** 2 * D0)
    Bi = M.H_CONV * R / k
    Bi_m = M.HM * R / D0
    print(f'附录3 物性(C = {M.C_INIT}):  rho = {rho:.4f} kg/m3,  cp = {cp:.2f} J/(kg K),  '
          f'k = {k:.6f} W/(m K)')
    print(f'D(C = {M.C_INIT}, T = {M.T_INIT} degC) = {D0:.4e} m^2/s;  '
          f'alpha = k/(rho*cp) = {alpha:.4e} m^2/s')
    print(f'tau_T = R^2/alpha = {tau_T:.1f} s = {tau_T/60:.2f} min(热平衡特征时间)')
    print(f'tau_C = R^2/D    = {tau_C:.1f} s = {tau_C/3600:.2f} h(水分扩散特征时间)')
    print(f'tau_1 = R^2/(lam1^2*D) = {tau1:.1f} s = {tau1/3600:.2f} h'
          f'(柱对称基模时间常数, lam1 = 2.4048)')
    print(f'Bi = h*R/k = {Bi:.4f};  Bi_m = hm*R/D = {Bi_m:.4f}')

    def D_of(C, Tc=M.T_INIT):
        return float(M.D_p3(np.array([C]), np.array([Tc + 273.15]))[0])

    print('物性的含水率/温度依赖(烘干后期变慢的根源):')
    print(f'  D(0.5)/D(2.55)  = {D_of(0.5)/D0:.4f}   (C 降至 0.5 时扩散放慢 '
          f'{1/(D_of(0.5)/D0):.1f} 倍)')
    print(f'  D(0.15)/D(2.55) = {D_of(0.15)/D0:.4f}   (C 降至 0.15 时扩散放慢 '
          f'{1/(D_of(0.15)/D0):.1f} 倍)')
    print(f'  D(60degC)/D(28degC) = {D_of(M.C_INIT, 60.0)/D0:.4f}   '
          f'(Arrhenius exp(-3850/T), 每升 1 K 约 +3.7%)')
    D_end = D_of(C_END, 50.165)
    tau1_end = R * R / (LAM1 ** 2 * D_end)
    print(f'  末段(C = 0.15, T = 50.17 degC)基模时间常数 tau_1 = {tau1_end:.0f} s = '
          f'{tau1_end/3600:.2f} h(自锁后)')
    print(f'  若 D 恒为初值, 基模衰减 2.55 -> 0.15 需 tau_1*ln(2.55/0.15) = '
          f'{tau1*np.log(M.C_INIT/C_END)/3600:.2f} h;  实际远超此值 => 自锁效应把末段拉长')
    print()
    print('=== 1) 烘干判据与附件1 两阶段 ===')
    print(f'判据: 药材各处水分浓度 < {C_END} kg/kg。数值上最大水分浓度始终在中心'
          f'(表面先干、中心最后干), 故判据等价于 中心 C(r=0,t) < {C_END}'
          f'(由求解后的时间历程验证)。')
    t, T, C = M.load_chamber()
    msk = t >= T_HOLD
    print(f'附件1: t = {t[0]:.0f} .. {t[-1]:.0f} s; 恒温干燥段(后 2 h) '
          f'T_air = {T[msk].mean()-273.15:.4f} ± {T[msk].std():.4f} degC,  '
          f'C_air = {C[msk].mean():.5f} ± {C[msk].std():.5f} kg/kg')
    print(f'维持末值假设(问题3 全程唯一外推): t > {t[-1]:.0f} s 后 '
          f'T_air = {T[-1]-273.15:.4f} degC,  C_air = {C[-1]:.5f}')
    print(f'输出约定: result3.xlsx 每 {DT_OUT:.0f} s 一行至烘干结束;  '
          f'{DT_OUT:.0f} s << 最小特征时间 tau_T = {tau_T/60:.1f} min, 足以解析全程时间历程')


# --------------------------------------------------------------------------
# 1) 表5 + 关键数字
# --------------------------------------------------------------------------
def print_table5(te, C):
    print('=== 2) 表5  药材烘干过程的水分浓度 (kg/kg, 4 位小数) ===')
    print('时间/h    0         0.5       1         1.5       2')
    for h, row in zip(T_TABLE_H, C[:-1]):
        print(f'{h:>7.1f}' + ''.join(f'{v:>10.4f}' for v in row))
    print(f'{"烘干结束":>7s}' + ''.join(f'{v:>10.4f}' for v in C[-1]))
    print()
    print(f'(烘干结束时刻 t_end = {te:.1f} s = {te/3600:.4f} h = {te/86400:.4f} 天)')
    print()
    print('=== 3) 关键数字 ===')
    _, _, cch = M.load_chamber()
    cair = float(cch[-1])
    dc = -np.diff(np.concatenate([[M.C_INIT], C[:, 0]]))
    print(f'中心(最后烘干位置): 6 h {C[0, 0]:.4f} -> 24 h {C[3, 0]:.4f} '
          f'-> 48 h {C[7, 0]:.4f} -> 结束 {C[-1, 0]:.4f}')
    print(f'表面: 6 h {C[0, -1]:.4f} -> 12 h {C[1, -1]:.4f} -> 结束 {C[-1, -1]:.4f}   '
          f'(烘房 C_air = {cair:.5f}; 表面从约 12 h 起逼近平衡)')
    print(f'中心-表面差: 6 h {C[0, 0]-C[0, -1]:.4f} -> 24 h {C[3, 0]-C[3, -1]:.4f} '
          f'-> 结束 {C[-1, 0]-C[-1, -1]:.4f}')
    print('每 6 h 中心降幅(自锁证据): ' + '  '.join(f'{v:.4f}' for v in dc))
    print(f'  首 6 h 完成中心总降幅的 {(M.C_INIT-C[0, 0])/(M.C_INIT-C_END)*100:.1f}%;  '
          f'末 3.18 h 仅降 {dc[-1]:.4f}')


def solve_tables():
    m = M.DryingModel(3, N=N_GRID)
    te, sol = drying_time(m)
    t_rows = np.asarray([h * 3600.0 for h in T_TABLE_H] + [te], float)
    Y = sol.sol(t_rows)
    # 内部列 0, 0.5, 1, 1.5 cm 线性插值; 末列"2"(表面)由边界条件反解(sample 的 add_surface)
    T, C = sample(m, Y, t_rows, np.asarray(R_TABLE[:-1], float), add_surface=True)
    with open(os.path.join(HERE, 'tables3.json'), 'w', encoding='utf-8') as f:
        json.dump({'times_h': T_TABLE_H, 't_end': te,
                   'cols': [str(c) for c in R_TABLE], 'C': C.tolist()}, f,
                  ensure_ascii=False, indent=1)
    print('表5 原始值 -> tables3.json')
    print_table5(te, C)
    return te, C


# --------------------------------------------------------------------------
# 2) result3.xlsx(模板同款表头, 流式写出; 单工作表, 只含水分浓度)
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


def write_result3(te):
    tpl = tpl_info(3)
    print(f'模板工作表: {[n for n, _ in tpl]}')
    print(f'模板表头: {tpl[0][1][:4]} ... {tpl[0][1][-2:]}')
    cols = np.arange(0, 2.0, 0.1)
    hdr = build_header(cols, 2.0)
    m = M.DryingModel(3, N=N_GRID)
    t0 = time.time()
    times, T, C = stream_sample(m, te, DT_OUT, cols, t_start=0.0, rtol=RTOL, atol=ATOL)
    sheets = [
        (tpl[0][0], hdr, ([int(t)] + [round(float(v), 4) for v in C[k]]
                          for k, t in enumerate(times))),
    ]
    path = os.path.join(HERE, 'result3.xlsx')
    write_xlsx(path, sheets)
    print(f'result3.xlsx: {len(times)} 行 × 1 工作表, '
          f'{os.path.getsize(path)/1024:.1f} KB, {time.time()-t0:.1f}s')


# --------------------------------------------------------------------------
# 3) 插图: 表5 时刻水分剖面 + 全流程烘干曲线
# --------------------------------------------------------------------------
def make_figure(te, C_table):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['figure.dpi'] = 150
    plt.rcParams['savefig.bbox'] = 'tight'
    CM = plt.cm.viridis
    # 语义色与 03-pic/palette.py 一致(红=表面, 蓝=中心, 暗红=判据, 近黑=参考线)
    C_SURF, C_CENTER, C_THRESH, C_REF = '#D65F5F', '#4878CF', '#A33B3B', '#333333'

    m = M.DryingModel(3, N=N_GRID)
    te2, sol = drying_time(m)
    tt = np.arange(0.0, te2, 60.0)
    Y = sol.sol(tt)
    Tt, Ct = sample(m, Y, tt, np.asarray([0.0]), add_surface=True)

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    cols = np.append(np.asarray(R_TABLE[:-1], float), 2.0)
    n = len(T_TABLE_H) + 1
    for i, lab in enumerate([f'{h:g} h' for h in T_TABLE_H] + ['烘干结束']):
        c = CM(i / (n - 1))
        ax[0].plot(cols, C_table[i], 'o-', ms=3, lw=1.5, color=c, label=lab)
    ax[0].set_xlabel('到药材中心的距离 / cm')
    ax[0].set_ylabel('水分浓度 / (kg/kg)')
    ax[0].set_title('(a) 表5 各时刻的水分浓度分布')
    ax[0].grid(alpha=.3)
    ax[0].legend(fontsize=7, ncol=2)

    ax[1].plot(tt / 3600, Ct[:, -1], color=C_SURF, lw=1.8,
               label=f'表面 r=2 cm(结束 {Ct[-1, -1]:.4f})')
    ax[1].plot(tt / 3600, Ct[:, 0], color=C_CENTER, lw=1.8,
               label=f'中心 r=0(结束 {Ct[-1, 0]:.4f})')
    ax[1].axhline(C_END, color=C_THRESH, ls='--', lw=1.5, label=f'烘干判据 {C_END} kg/kg')
    ax[1].axvline(te2 / 3600, color=C_REF, ls=':', lw=1.4)
    ax[1].scatter([te2 / 3600], [C_END], s=40, color=C_THRESH, zorder=5)
    ax[1].annotate(f't = {te2/3600:.4f} h\n(= {te2/86400:.4f} 天)',
                   xy=(te2 / 3600, C_END), xytext=(te2 / 3600 - 26, 0.95), fontsize=8.5,
                   arrowprops=dict(arrowstyle='->', color=C_REF, lw=1))
    ax[1].set_xlabel('时间 t / h')
    ax[1].set_ylabel('水分浓度 / (kg/kg)')
    ax[1].set_title('(b) 全流程烘干曲线(表面 / 中心)')
    ax[1].grid(alpha=.3)
    ax[1].legend(fontsize=8, loc='upper right')
    ax[1].set_xlim(0, 60)
    fig.suptitle(f'问题3 整个烘干过程({te2/3600:.4f} h): 水分浓度分布与烘干曲线', fontsize=12)
    path = os.path.join(HERE, 'fig3_p3.png')
    fig.savefig(path)
    plt.close(fig)
    print(f'fig3_p3.png -> {os.path.getsize(path)/1024:.1f} KB')


# --------------------------------------------------------------------------
# 4) 问题3 专属验证
# --------------------------------------------------------------------------
def verify():
    """(a) 水分质量守恒(全流程); (b) 烘干时间网格收敛; (c) 与问题4 交叉时刻复核。"""
    trapz = getattr(np, 'trapezoid', None) or np.trapz

    # (a) 守恒: 归一化总水分 M~ = int_0^1 C xi dxi,  dM~/dt = -hm (C_s - C_air)/R。
    #     表面通量在 t=0 附近有 sqrt(t) 奇异性, 首 1 h 用 1 s 细网格, 其后 60 s。
    print('=== (a) 水分质量守恒(全流程) ===')
    m = M.DryingModel(3, N=N_GRID)
    te, sol = drying_time(m)
    tt = np.concatenate([np.arange(0.0, 3600.0, 1.0), np.arange(3600.0, te + 1e-9, 60.0)])
    Y = sol.sol(tt)
    xi = m.xi_c
    Mt = (Y[1::2, :] * xi[:, None]).sum(axis=0) * m.dxi
    _, Cs = sample(m, Y, tt, np.asarray([0.0]), add_surface=True)
    flux = m.hm * (Cs[:, -1] - np.interp(tt, m.t_ch, m.C_ch)) / m.Rmax
    cum = np.zeros(len(tt))
    for k in range(1, len(tt)):
        cum[k] = trapz(flux[:k + 1], tt[:k + 1])
    resid = (Mt - Mt[0]) + cum
    print(f'总水分 M~(0) = {Mt[0]:.6f};  最大 |残差| = {np.abs(resid).max():.3e},  '
          f'相对 {np.abs(resid).max()/Mt[0]:.3e}')

    # (b) 烘干时间的网格收敛 (二阶, Richardson 外推)
    print('=== (b) 烘干时间的网格收敛 ===')
    vals = {}
    for N in (100, 200, 400, 800):
        mn = M.DryingModel(3, N=N)
        ten, _ = drying_time(mn)
        vals[N] = ten
    rich = vals[800] + (vals[800] - vals[400]) / 3.0
    for N in (100, 200, 400, 800):
        print(f'  N={N:>4}:  t_end = {vals[N]:.1f} s({vals[N]/3600:.4f} h)   '
              f'相对 Richardson 基准偏差 {abs(vals[N] - rich):.1f} s')
    e400 = abs(vals[800] - vals[400]) * 4.0 / 3.0
    print(f'Richardson 极限 t_end ~ {rich:.1f} s = {rich/3600:.4f} h;  '
          f'N=400 误差估计 = {e400:.1f} s(相对 {e400/vals[400]*100:.3f}%)')
    p = np.log2(abs(vals[100] - vals[200]) / abs(vals[200] - vals[400]))
    print(f'收敛阶(100 -> 400 段) ≈ {p:.2f}')

    # (c) 与问题4 的交叉时刻(交叉校验: 收缩模型在低含水率段反超)
    print('=== (c) 与问题4 的交叉时刻(交叉校验) ===')
    m4 = M.DryingModel(4, N=N_GRID)
    te4, sol4 = drying_time(m4)
    tt4 = np.arange(0.0, min(te, te4) + 1e-9, 600.0)
    Y3 = sol.sol(tt4)
    Y4 = sol4.sol(tt4)
    C3 = sample(m, Y3, tt4, np.asarray([0.0]), add_surface=False)[1][:, 0]
    C4 = sample(m4, Y4, tt4, np.asarray([0.0]), add_surface=False)[1][:, 0]
    diff = C3 - C4
    i = np.argwhere(diff[:-1] * diff[1:] < 0)
    print(f'问题4 烘干时间 = {te4:.1f} s = {te4/3600:.4f} h = {te4/86400:.4f} 天')
    if len(i):
        k = int(i[0][0])
        t_cross = tt4[k] + (tt4[k + 1] - tt4[k]) * abs(diff[k]) / (abs(diff[k]) + abs(diff[k + 1]))
        print(f'中心水分交叉时刻 ≈ {t_cross/3600:.2f} h')
        print(f'(交叉前: 问题4 更慢 — 附录4 前置因子小 {(2.4e-3/4.2e-4):.2f} 倍'
              f'(初态 C=2.55 处 D 实际小 5.4 倍);  '
              f'交叉后: 问题4 更快 — 收缩使有效扩散系数按 1/R^2 放大, 最大 '
              f'{(M.R0/0.01198)**2:.2f} 倍, 且附录4 的浓度依赖 exp(-0.30/C) 更弱)')
    else:
        print('未检测到交叉')


# --------------------------------------------------------------------------
def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if mode == 'diag':
        diagnostics()
        return
    if mode == 'tables':
        with open(os.path.join(HERE, 'tables3.json'), encoding='utf-8') as f:
            d = json.load(f)
        print_table5(d['t_end'], np.asarray(d['C']))
        return
    if mode == 'verify':
        verify()
        return
    diagnostics()
    te, C = solve_tables()
    write_result3(te)
    make_figure(te, C)
    print('完成。')


if __name__ == '__main__':
    main()
