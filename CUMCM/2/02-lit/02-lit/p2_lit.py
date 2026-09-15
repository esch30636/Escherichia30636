# -*- coding: utf-8 -*-
"""问题2 文献补全版对照 —— 按文献在能量方程里补上蒸发潜热汇项, 重新求解并与
题面简化模型(基线)对照出图。

文献依据(编号见 文献库.md; 汇总见 文献核心模型汇总.md §4 第 1 行 / §5 第 12 句):
    [31] Purlis 2019      能量方程中吸附热/蒸发潜热汇项的严谨处理(主依据)
    [30] Zhu 2021 / [32] Lu 2015   热-湿-力双向耦合多相模型
    [52] LBM 综述         相变潜热对局部温度场的反馈
    [29] Defraeye 2012    h 与 h_m 的关联式依据(用于热质类比校核题面 h_m)
    [10] Berger & Pei 1973  恒速/降速转折 —— 恒速段表面近湿球温度的经典图像

把潜热放进模型的两种写法(基线默认关闭, 打开后 ONLY 能量方程变化):
    vol : 体积汇   rho*cp*dT/dt = (1/r)d/dr(k r dT/dr) + L_v*rho_c*dC/dt
    surf: 表面通量 表面能量边界加 L_v*J_s   (J_s = rho_c*hm*(C_s - C_air))
其中 rho_c 是把"模型的 C 通量"换算成水的质量通量 [kg/(m^2 s)] 的密度 [kg/m^3]:
    dry0 : rho(C0)/(1+C0) = 275.04  kg/m^3   模型自洽口径(推荐) —— 推导见 README §2
    dry  : rho(C)/(1+C)                      随含水率变化(用附录3 密度式)
    bulk : rho(C)                            用附录3 密度本身
    unit : 1                                 量级下界("浓度型"口径)

用法(legion, D:\\CUMCM\\A\\02-lit, conda 环境 cumcm_a):
    python p2_lit.py diag    # 量级诊断(热质类比/潜热占比/干物质密度), 不求解全流程
    python p2_lit.py hot     # 3 h 考察窗: 6 个变体 -> p2_lit_hot.json/.npz
    python p2_lit.py full    # 全流程: 4 个变体 -> p2_lit_full.json/.npz(时间较长)
    python p2_lit.py figs    # 由上面的 json/npz 出 7 张对照图 figs/fig01..fig07
    python p2_lit.py all     # hot + full + figs
"""
import os
import sys
import json
import time

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

import numpy as np
import a_model as M
from a_output import sample

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, 'figs')

N_GRID = 400
RTOL, ATOL = 1e-8, 1e-10
T_HOT = 10800.0                     # 3 h 考察窗(表3/表4 口径)
T_MAX = 1200000.0                   # 全流程积分上限 (~13.9 天)
C_END = 0.15                        # 烘干判据 kg/kg
DT_HOT = 10.0                       # 3 h 窗口采样步长 s
DT_FULL = 600.0                     # 全流程采样步长 s
T_TABLE_H = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]

# (key, 控制台名, 图例名, latent 配置)   None = 基线(题面口径)
VARIANTS = [
    ('base', '基线(无潜热,题面口径)', '基线(无潜热)', None),
    ('vol_d0', 'vol 汇·rho_d=275.04(推荐)', 'vol 汇·$\\rho_d$=275.04', {'mode': 'vol', 'rho': 'dry0'}),
    ('surf_d0', 'surf 汇·rho_d=275.04', 'surf 汇·$\\rho_d$=275.04', {'mode': 'surf', 'rho': 'dry0'}),
    ('vol_dry', 'vol 汇·rho_d=rho/(1+C)', 'vol 汇·$\\rho/(1+C)$', {'mode': 'vol', 'rho': 'dry'}),
    ('vol_bulk', 'vol 汇·rho_d=rho(C)', 'vol 汇·$\\rho(C)$', {'mode': 'vol', 'rho': 'bulk'}),
    ('vol_unit', 'vol 汇·rho_d=1(下界)', 'vol 汇·$\\rho_d$=1(下界)', {'mode': 'vol', 'rho': 'unit'}),
]
FULL_KEYS = ['base', 'vol_d0', 'surf_d0', 'vol_unit']
HOT_KEYS = [v[0] for v in VARIANTS]
NAME = {v[0]: v[1] for v in VARIANTS}
LAB = {v[0]: v[2] for v in VARIANTS}
LAT = {v[0]: v[3] for v in VARIANTS}
# 作图的固定配色(与 01-pic/02-pic 的 palette 语义色一致)
MSTYLE = {'base': ('C_CENTER', '-'), 'vol_d0': ('RED', '-'),
          'surf_d0': ('GREEN', '-'), 'vol_unit': ('C_AIR', '--')}


def model_of(key, N=N_GRID):
    return M.DryingModel(2, N=N, latent=LAT[key])


def idx(t_s):
    """3 h 窗口采样网格(步长 DT_HOT)上时刻 t_s 的下标。"""
    return int(round(t_s / DT_HOT))


# --------------------------------------------------------------------------
# 表面热流诊断(全部换算到 W/m^2; 正 = 由烘房/内部指向表面)
# --------------------------------------------------------------------------
def fluxes(m, T, C, tt):
    """T, C: (N, nt) 单元中心值(模型 K 单位)。
    返回 (对流流, 潜热流, 表面导热流, T_s, C_s, T_air, C_air)。
    表面值由模型自身的 surface_bc_vec 反解(含潜热时自动处理潜热扣减)。"""
    lnc = np.log(1.0 / m.xi_c[-1])
    R_arr = np.full(np.size(tt), m.Rmax)
    rho, cp, k = m.props(C[-1, :])
    Ta = np.interp(tt, m.t_ch, m.T_ch) + m.dT_ch
    Ca = np.interp(tt, m.t_ch, m.C_ch) + m.dC_ch
    Ts, Cs = m.surface_bc_vec(T, C, tt, R_arr)
    if m.latent is not None:
        rho_c = m.rho_c(Cs, rho)
    else:                                   # 基线: 按推荐口径评估"若加潜热"的量级
        rho_c = np.full_like(Cs, m.rho_d0)
    q_conv = m.h_conv * (Ta - Ts)
    q_lat = float(M.LV_STD) * rho_c * m.hm * (Cs - Ca)
    q_cond = k * (T[-1, :] - Ts) / (lnc * m.Rmax)
    return q_conv, q_lat, q_cond, Ts, Cs, Ta, Ca


def diag():
    print('=== 0) 量级诊断: 蒸发潜热项在本问题参数下是不是小量 ===')
    rho0, cp0, k0 = (float(v[0]) for v in M.props_p3(np.array([M.C_INIT])))
    rd = M.dry_density0(M.props_p3)
    print(f'附录3 在 C0 = {M.C_INIT}: rho = {rho0:.2f} kg/m3, cp = {cp0:.1f} J/(kg K), k = {k0:.4f} W/(m K)')
    print(f'干物质密度锚定值 rho_d = rho(C0)/(1+C0) = {rd:.2f} kg/m3  '
          f'(模型结构: R 常数 => rho_d 常数)')
    print(f'汽化潜热 L_v = {M.LV_STD/1e3:.0f} kJ/kg (50 degC 蒸汽表值; '
          f'28~50 degC 内 2435->2383 kJ/kg, 变化 2.2%)')
    print()

    # 热质类比: h_m ~ h/(rho_air*cp_air*Le^(2/3))
    rho_a, cp_a, k_a = 1.129, 1007.0, 0.0275            # 空气 ~39 degC(膜温)
    alpha_a = k_a / (rho_a * cp_a)
    D_ab = 2.85e-5                                      # 水蒸气-空气 ~39 degC
    Le = alpha_a / D_ab
    hm_an = M.H_CONV / (rho_a * cp_a * Le ** (2.0 / 3.0))
    print(f'热质类比校核 [29]: alpha_air = {alpha_a:.3e} m2/s, D_AB = {D_ab:.2e} m2/s, '
          f'Le = {Le:.3f}, Le^(2/3) = {Le**(2/3):.3f}')
    print(f'  h_m(类比) = h/(rho_a cp_a Le^(2/3)) = {hm_an:.4e} m/s')
    print(f'  h_m(题面) = {M.HM:.1e} m/s   -> 相差 {hm_an/M.HM:.3e} 倍'
          f'(题面 h_m 与热质类比不自洽, 见 README §3)')
    print()

    t0 = time.time()
    m = model_of('base')
    sol = m.solve(T_HOT, rtol=RTOL, atol=ATOL)
    tt = np.arange(0.0, T_HOT + 1e-9, DT_HOT)
    Y = sol.sol(tt)
    q_conv, q_lat, q_cond, Ts, Cs, Ta, Ca = fluxes(m, Y[0::2, :], Y[1::2, :], tt)
    print(f'3 h 窗口各项表面热流 (W/m2, 正 = 由烘房/内部传给表面):   ({time.time()-t0:.1f}s)')
    print('   t/h   T_s/degC    C_s     h(Tair-Ts)   L_v*J_s    k*dT/dr   L_v*J_s:对流')
    for h in (0.5, 1.0, 2.0, 3.0):
        i = idx(h * 3600.0)
        r = float(q_lat[i]) / max(abs(float(q_conv[i])), 1e-12)
        print(f'  {h:>4.1f}  {Ts[i]-273.15:9.4f}  {Cs[i]:7.4f}  '
              f'{q_conv[i]:10.3f}  {q_lat[i]:10.3f}  {q_cond[i]:10.3f}  {r:11.2f}')
    print('  (J_s = rho_d*hm*(C_s-C_air), rho_d 取推荐口径 275.04; '
          't=0 时表面 = 28 degC, 对流热流上限 ~550 W/m2)')
    print()
    for h in (1.0, 3.0):
        i = idx(h * 3600.0)
        print(f'  t = {h:.0f} h: 潜热流 {q_lat[i]:7.1f} W/m2 —— 若主要由对流供给, '
              f'表面需比烘房低 {q_lat[i]/M.H_CONV:.2f} K')
    print()


# --------------------------------------------------------------------------
# 1) 3 h 考察窗: 全部变体
# --------------------------------------------------------------------------
def hot():
    print('=== 1) 3 h 考察窗: 6 个变体对照 ===')
    tt = np.arange(0.0, T_HOT + 1e-9, DT_HOT)
    data, rows = {}, {}
    for key in HOT_KEYS:
        m = model_of(key)
        t0 = time.time()
        sol = m.solve(T_HOT, rtol=RTOL, atol=ATOL)
        Y = sol.sol(tt)
        T, C = sample(m, Y, tt, np.asarray([0.0]), add_surface=True)
        Tc, Ts = T[:, 0] - 273.15, T[:, -1] - 273.15
        Cc, Cs = C[:, 0], C[:, -1]
        q_conv, q_lat, q_cond, _, _, _, _ = fluxes(m, Y[0::2, :], Y[1::2, :], tt)
        rows[key] = {
            'name': NAME[key], 'steps': int(sol.t.size), 'secs': round(time.time() - t0, 1),
            'T_center_3h': float(Tc[-1]), 'T_surface_3h': float(Ts[-1]),
            'C_center_3h': float(Cc[-1]), 'C_surface_3h': float(Cs[-1]),
            'dT_radial_3h': float(Ts[-1] - Tc[-1]),
            'T_surface_table': [float(Ts[idx(h * 3600.0)]) for h in T_TABLE_H],
            'T_center_table': [float(Tc[idx(h * 3600.0)]) for h in T_TABLE_H],
            'C_surface_table': [float(Cs[idx(h * 3600.0)]) for h in T_TABLE_H],
            'C_center_table': [float(Cc[idx(h * 3600.0)]) for h in T_TABLE_H],
            'q_conv_3h': float(q_conv[idx(T_HOT)]), 'q_lat_3h': float(q_lat[idx(T_HOT)]),
            'q_cond_3h': float(q_cond[idx(T_HOT)]),
        }
        data.update({f'{key}_t': tt, f'{key}_Ts': Ts, f'{key}_Tc': Tc,
                     f'{key}_Cs': Cs, f'{key}_Cc': Cc,
                     f'{key}_qc': q_conv, f'{key}_ql': q_lat, f'{key}_qd': q_cond})
        print(f'  {NAME[key]:<26} 表面T(3h) = {Ts[-1]:9.4f}  中心T = {Tc[-1]:9.4f}  '
              f'表面C = {Cs[-1]:8.4f}  中心C = {Cc[-1]:8.4f}   ({time.time()-t0:.1f}s)')
    with open(os.path.join(HERE, 'p2_lit_hot.json'), 'w', encoding='utf-8') as f:
        json.dump({'rows': rows, 'order': HOT_KEYS, 'Lv': M.LV_STD,
                   'rho_d0': M.dry_density0(M.props_p3)}, f, ensure_ascii=False, indent=1)
    np.savez_compressed(os.path.join(HERE, 'p2_lit_hot.npz'), **data)
    print('  -> p2_lit_hot.json / p2_lit_hot.npz')
    print()
    print('  相对基线的偏差(表面T / 中心T / 表面C / 中心C):')
    b = rows['base']
    for key in HOT_KEYS[1:]:
        r = rows[key]
        print(f'  {NAME[key]:<26} {r["T_surface_3h"]-b["T_surface_3h"]:+9.4f} '
              f'{r["T_center_3h"]-b["T_center_3h"]:+9.4f} '
              f'{r["C_surface_3h"]-b["C_surface_3h"]:+9.4f} '
              f'{r["C_center_3h"]-b["C_center_3h"]:+9.4f}')
    print()


# --------------------------------------------------------------------------
# 2) 全流程(烘干判据 max C < 0.15)
# --------------------------------------------------------------------------
def full():
    print('=== 2) 全流程烘干时间(判据: 各处 C < 0.15 kg/kg) ===')
    out, data = {}, {}
    for key in FULL_KEYS:
        m = model_of(key)

        def ev(t, y):
            return y[1::2].max() - C_END
        ev.terminal = True
        ev.direction = -1
        t0 = time.time()
        sol = m.solve(T_MAX, events=[ev], rtol=RTOL, atol=ATOL)
        te = float(sol.t_events[0][0]) if len(sol.t_events[0]) else float('nan')
        secs = time.time() - t0
        tt = np.arange(0.0, te + 1e-9, DT_FULL)
        if tt.size == 0 or tt[-1] < te:
            tt = np.append(tt, te)
        Y = sol.sol(tt)
        T, C = sample(m, Y, tt, np.asarray([0.0]), add_surface=True)
        Tc, Ts = T[:, 0] - 273.15, T[:, -1] - 273.15
        Cc, Cs = C[:, 0], C[:, -1]
        out[key] = {'name': NAME[key], 't_end_s': te, 't_end_h': te / 3600,
                    't_end_d': te / 86400, 'steps': int(sol.t.size), 'secs': round(secs, 1),
                    'T_center_end': float(Tc[-1]), 'T_surface_end': float(Ts[-1]),
                    'T_surface_min': float(Ts.min()), 'T_center_min': float(Tc.min()),
                    'T_surface_48h': float(np.interp(172800.0, tt, Ts)),
                    'C_surface_end': float(Cs[-1]),
                    'C_center_24h': float(np.interp(86400.0, tt, Cc)),
                    'C_center_48h': float(np.interp(172800.0, tt, Cc))}
        data.update({f'{key}_t': tt, f'{key}_Ts': Ts, f'{key}_Tc': Tc,
                     f'{key}_Cs': Cs, f'{key}_Cc': Cc})
        tag = f'未在 {T_MAX/86400:.1f} 天内达标' if not np.isfinite(te) else \
            f'{te:.1f} s = {te/3600:.4f} h = {te/86400:.4f} 天'
        print(f'  {NAME[key]:<26} {tag}   ({sol.t.size} 步, {secs:.1f}s)')
    with open(os.path.join(HERE, 'p2_lit_full.json'), 'w', encoding='utf-8') as f:
        json.dump({'rows': out, 'order': FULL_KEYS}, f, ensure_ascii=False, indent=1)
    np.savez_compressed(os.path.join(HERE, 'p2_lit_full.npz'), **data)
    print('  -> p2_lit_full.json / p2_lit_full.npz')
    print()
    b = out['base']['t_end_h']
    for key in FULL_KEYS[1:]:
        r = out[key]
        print(f'  {NAME[key]:<26} 干时 {r["t_end_h"]:9.4f} h '
              f'(基线 {b:.4f} h, {r["t_end_h"]/b-1:+.2%})')
    print()


# --------------------------------------------------------------------------
# 3) 出图
# --------------------------------------------------------------------------
def figs():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import palette as P
    os.makedirs(FIGDIR, exist_ok=True)
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['savefig.bbox'] = 'tight'

    def save(fig, name):
        p = os.path.join(FIGDIR, name)
        fig.savefig(p)
        plt.close(fig)
        print(f'  figs/{name}  {os.path.getsize(p)/1024:.0f} KB')

    def panel2(w=7.2, h=2.9, wspace=0.34):
        fig, ax = plt.subplots(1, 2, figsize=(w, h))
        fig.subplots_adjust(wspace=wspace)
        return fig, ax

    H = np.load(os.path.join(HERE, 'p2_lit_hot.npz'))
    F = np.load(os.path.join(HERE, 'p2_lit_full.npz'))
    hot = json.load(open(os.path.join(HERE, 'p2_lit_hot.json'), encoding='utf-8'))['rows']
    ful = json.load(open(os.path.join(HERE, 'p2_lit_full.json'), encoding='utf-8'))['rows']
    th = H['base_t'] / 3600.0

    # ---- fig01 潜热项量级 ----
    fig, ax = panel2()
    def smooth(v, w=31):
        w = min(w, v.size // 3)
        ker = np.ones(w) / w
        return np.convolve(v, ker, mode='same')
    ax[0].semilogy(th, smooth(np.abs(H['base_qc'])), color=P.BLUE, lw=1.8,
                   label=r'对流 $|h(T_{air}-T_s)|$(300 s 滑平均)')
    ax[0].semilogy(th, H['base_ql'], color=P.RED, lw=1.8,
                   label=r'潜热 $L_v\rho_d h_m(C_s-C_{air})$')
    t_ch_, T_ch_, _ = M.load_chamber()
    qmax = M.H_CONV * (float(T_ch_[-1]) - 273.15 - M.T_INIT)   # h*(T_air - T_初始) 上限
    ax[0].axhline(qmax, color=P.C_THRESH, ls='--', lw=1.4,
                  label=f'最大可供给热流 {qmax:.0f} W/m²')
    i5 = idx(1800.0)
    ax[0].annotate(r'潜热/对流 $\approx$ %.1f' % (H['base_ql'][i5] / abs(H['base_qc'][i5])),
                   xy=(0.5, H['base_ql'][i5]), xytext=(1.05, 1900), fontsize=8.5,
                   arrowprops=dict(arrowstyle='->', color=P.C_REF, lw=1))
    ax[0].set_xlabel('时间 t / h')
    ax[0].set_ylabel('表面热流 / (W/m²)')
    ax[0].set_title('(a) 表面热流: 潜热远大于对流可供给量(基线解)')
    ax[0].set_xlim(0, 3)
    ax[0].set_ylim(1, 4000)
    ax[0].legend(fontsize=6.5, loc='lower left')
    Cs = np.linspace(0.15, M.C_INIT, 300)
    rho, _, _ = M.props_p3(Cs)
    ax[1].semilogy(Cs, np.full_like(Cs, 1.0), color=P.C_AIR, lw=1.6, ls=':',
                   label=r'$\rho_c=1$(下界口径)')
    ax[1].semilogy(Cs, M.rho_conv(Cs, rho, 'dry'), color=P.BLUE, lw=1.8, label=r'$\rho/(1+C)$')
    ax[1].semilogy(Cs, rho, color=P.OLIVE, lw=1.8, label=r'$\rho(C)$')
    ax[1].semilogy(Cs, np.full_like(Cs, M.dry_density0(M.props_p3)), color=P.RED, lw=2.2,
                   label=r'$\rho_d=275.04$(推荐)')
    ax[1].set_xlabel('水分浓度 C / (kg/kg)')
    ax[1].set_ylabel('换算密度 $\\rho_c$ / (kg/m³)')
    ax[1].set_title('(b) 换算密度口径(相差 2~3 个数量级)')
    ax[1].invert_xaxis()
    ax[1].legend(fontsize=7)
    for a in ax:
        a.grid(alpha=.3, which='both')
    save(fig, 'fig01_scale.png')

    # ---- fig02/fig03 3 h 对照 ----
    for fname, kf, ylab, titles in (
            ('fig02_hot_T.png', 'Ts', '温度 / °C', ('(a) 表面 r = 2 cm', '(b) 中心 r = 0')),
            ('fig03_hot_C.png', 'Cs', '水分浓度 / (kg/kg)',
             ('(a) 表面 r = 2 cm', '(b) 中心 r = 0'))):
        fig, ax = panel2()
        key2 = 'Tc' if kf == 'Ts' else 'Cc'
        for key, (cn, ls) in MSTYLE.items():
            c = getattr(P, cn)
            ax[0].plot(th, H[f'{key}_{kf}'], ls, color=c, lw=1.8, label=LAB[key])
            ax[1].plot(th, H[f'{key}_{key2}'], ls, color=c, lw=1.8, label=LAB[key])
        for a, tt2 in zip(ax, titles):
            a.set_xlabel('时间 t / h')
            a.set_ylabel(ylab)
            a.set_title(tt2)
            a.set_xlim(0, 3)
            a.grid(alpha=.3)
            a.legend(fontsize=7)
        save(fig, fname)

    # ---- fig04 全流程水分 ----
    tmax = max(ful[k]['t_end_h'] for k in FULL_KEYS) * 1.05
    fig, ax = panel2(h=3.0)
    for key, (cn, ls) in MSTYLE.items():
        c = getattr(P, cn)
        tf = F[f'{key}_t'] / 3600.0
        ax[0].plot(tf, F[f'{key}_Cc'], ls, color=c, lw=1.8, label=LAB[key])
        ax[1].plot(tf, F[f'{key}_Cs'], ls, color=c, lw=1.8, label=LAB[key])
    ax[0].axhline(C_END, color=P.C_THRESH, ls='--', lw=1.4, label='判据 0.15 kg/kg')
    for key, (cn, ls) in MSTYLE.items():
        c = getattr(P, cn)
        ax[0].scatter([ful[key]['t_end_h']], [C_END], s=30, color=c, zorder=5)
        ax[1].axvline(ful[key]['t_end_h'], color=c, ls=':', lw=1.1)
    ax[0].set_xlabel('时间 t / h')
    ax[0].set_ylabel('中心水分浓度 / (kg/kg)')
    ax[0].set_title('(a) 中心水分(= max C)与烘干判据')
    ax[1].set_xlabel('时间 t / h')
    ax[1].set_ylabel('表面水分浓度 / (kg/kg)')
    ax[1].set_title('(b) 表面水分浓度(对数轴)')
    ax[1].set_yscale('log')
    for a in ax:
        a.set_xlim(0, tmax)
        a.grid(alpha=.3, which='both')
        a.legend(fontsize=7)
    save(fig, 'fig04_full_C.png')

    # ---- fig05 全流程温度 ----
    t_ch, T_ch, _ = M.load_chamber()
    fig, ax = panel2(h=3.0)
    for key, (cn, ls) in MSTYLE.items():
        c = getattr(P, cn)
        tf = F[f'{key}_t'] / 3600.0
        ax[0].plot(tf, F[f'{key}_Ts'], ls, color=c, lw=1.8, label=LAB[key])
        ax[1].plot(tf, F[f'{key}_Tc'], ls, color=c, lw=1.8, label=LAB[key])
    ax[0].plot(F['base_t'] / 3600.0, np.interp(F['base_t'], t_ch, T_ch) - 273.15,
               color=P.C_AIR, lw=1.2, ls='--', label='烘房 $T_{air}$')
    for a, tt2 in zip(ax, ('(a) 表面 r = 2 cm', '(b) 中心 r = 0')):
        a.set_xlabel('时间 t / h')
        a.set_ylabel('温度 / °C')
        a.set_title(tt2)
        a.set_xlim(0, tmax)
        a.grid(alpha=.3)
        a.legend(fontsize=7, loc='center right')
    save(fig, 'fig05_full_T.png')

    # ---- fig06 干时对比 ----
    te = [ful[k]['t_end_h'] for k in FULL_KEYS]
    fig, ax = plt.subplots(figsize=(6.6, 2.9))
    ypos = np.arange(len(FULL_KEYS))[::-1]
    ax.barh(ypos, te, height=.55, color=[getattr(P, MSTYLE[k][0]) for k in FULL_KEYS])
    for y, k, v in zip(ypos, FULL_KEYS, te):
        d = '' if k == 'base' else f'  ({v/te[0]-1:+.1%})'
        ax.text(v + max(te) * 0.015, y, f'{v:.2f} h = {v/24:.2f} 天{d}', va='center', fontsize=8.5)
    ax.axvspan(48, 72, color='#E3F0E3', alpha=.9, zorder=0)
    ax.text(60, len(FULL_KEYS) - .70, '题面"2–3 天"', ha='center', fontsize=8, color='#3A6B3A')
    ax.set_yticks(ypos)
    ax.set_yticklabels([NAME[k] for k in FULL_KEYS], fontsize=8.5)
    ax.set_xlabel('烘干时间 t / h')
    ax.set_title('全流程烘干时间: 基线 vs 文献补全版(含蒸发潜热)', fontsize=11)
    ax.set_xlim(0, max(te) * 1.34)
    ax.grid(alpha=.3, axis='x')
    save(fig, 'fig06_drytime.png')

    # ---- fig07 3 h 温度时空热力图对照 ----
    rr = np.arange(0, 1.95, 0.1)
    xs = np.append(rr, 2.0)
    xe = np.concatenate([[xs[0]], (xs[:-1] + xs[1:]) / 2, [xs[-1]]])
    ye = np.concatenate([[th[0]], (th[:-1] + th[1:]) / 2, [th[-1]]])
    fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.2), sharey=True)
    fig.subplots_adjust(wspace=0.12)
    for a, key, ttl in zip(ax, ('base', 'vol_d0'),
                           ('(a) 基线(无潜热)', '(b) 文献补全版(含蒸发潜热, 共用色标 10~50 °C)')):
        mk = model_of(key)
        sol = mk.solve(T_HOT, rtol=RTOL, atol=ATOL)
        T, _ = sample(mk, sol.sol(H['base_t']), H['base_t'], rr, add_surface=True)
        pc = a.pcolormesh(xe, ye, T - 273.15, cmap=P.HEAT_T, vmin=10, vmax=50.2, shading='flat')
        a.set_xlabel('到药材中心的距离 r / cm')
        a.set_title(ttl, fontsize=10)
        a.grid(False)
    ax[0].set_ylabel('时间 t / h')
    cb = fig.colorbar(pc, ax=ax, fraction=.04, pad=.02)
    cb.set_label('温度 / °C')
    cb.ax.tick_params(labelsize=8)
    save(fig, 'fig07_hot_map.png')
    print('完成。')


# --------------------------------------------------------------------------
# 4) 验证: ① 基线复现 02/tables2.json(重构后必须逐位一致) ② 含潜热的能量守恒
# --------------------------------------------------------------------------
def verify():
    print('=== verify 1) 基线复现冻结版 02/tables2.json(重构后必须逐位一致) ===')
    p = os.path.join(os.path.dirname(HERE), '02', 'tables2.json')
    if not os.path.exists(p):
        print(f'  跳过: 找不到 {p}')
    else:
        d = json.load(open(p, encoding='utf-8'))
        m = model_of('base')
        ts = np.asarray([h * 3600.0 for h in T_TABLE_H])
        T, C = sample(m, m.solve(T_HOT, rtol=RTOL, atol=ATOL).sol(ts), ts,
                      np.asarray([0.0, 0.5, 1.0, 1.5]), add_surface=True)
        eT = np.abs((T - 273.15) - np.asarray(d['T'])).max()
        eC = np.abs(C - np.asarray(d['C'])).max()
        print(f'  表3(温度)最大偏差 = {eT:.3e} degC;  表4(水分)最大偏差 = {eC:.3e} kg/kg')
        print('  ' + ('通过(逐位一致)' if max(eT, eC) < 1e-12 else '!! 不一致, 需排查 !!'))
    print()

    print('=== verify 2) 含潜热右端项的积分恒等性(离散代数恒等式, 任意态可检) ===')
    print('  恒等式:  sum(rho*cp*xi*dxi*dTdt) = (q_conv - q_lat)/R')
    print('  其中 q_conv = h(T_air - T_s), q_lat = L_v*rho_c*hm*(C_s - C_air)')
    print('  (即: 能量方程右端的表面项与表面热流平衡严格一致; 只对 rho_c 为常数的口径成立)')
    for key in ('base', 'vol_d0', 'surf_d0'):
        m = model_of(key)
        sol = m.solve(T_HOT, rtol=RTOL, atol=ATOL)
        for tq in (1800.0, 3600.0, 7200.0):
            y = sol.sol(np.array([tq]))[:, 0]
            f = m.rhs(tq, y)
            T, C = y[0::2], y[1::2]
            rho, cp, k = m.props(C)
            lhs = float(((rho * cp) * m.xi_c * m.dxi * f[0::2]).sum())
            Ta = float(np.interp(tq, m.t_ch, m.T_ch) + m.dT_ch)
            Ca = float(np.interp(tq, m.t_ch, m.C_ch) + m.dC_ch)
            Ts, Cs = m.surface_bc_vec(T[:, None], C[:, None], np.array([tq]),
                                      np.array([m.Rmax]))
            q_conv = m.h_conv * (Ta - float(Ts[0]))
            if m.latent is None:
                q_lat = 0.0                       # 基线模型无潜热项
            else:
                rho_c = float(m.rho_c(np.array([Cs[0]]), m.props(np.array([Cs[0]]))[0])[0])
                q_lat = M.LV_STD * rho_c * m.hm * (float(Cs[0]) - Ca)
            rhs = (q_conv - q_lat) / m.Rmax
            rel = abs(lhs - rhs) / max(abs(lhs), abs(rhs), 1e-30)
            print(f'  {NAME[key]:<26} t = {tq:5.0f} s:  lhs = {lhs:14.6f}  rhs = {rhs:14.6f}  '
                  f'相对残差 = {rel:.2e}')
    print('  注: rho_c 随 C 变化的口径(dry/bulk)残余链式项, 上式不严格成立, 故不列入。')
    print('      时间推进的守恒性另见 A/src/a_check2.py(基线)与 02/ 的表 6。')


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if mode in ('diag', 'all'):
        diag()
    if mode in ('hot', 'all'):
        hot()
    if mode in ('full', 'all'):
        full()
    if mode in ('figs', 'all'):
        figs()
    if mode in ('verify', 'all'):
        verify()


if __name__ == '__main__':
    main()
