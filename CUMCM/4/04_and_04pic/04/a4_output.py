# -*- coding: utf-8 -*-
"""Regenerate audited figures and reports; --plots-only preserves validated workbooks."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'out'
FIG = ROOT.parent / '04-pic'
FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.sans-serif': ['Microsoft YaHei', 'SimHei', 'DejaVu Sans'],
                     'axes.unicode_minus': False, 'axes.spines.top': False,
                     'axes.spines.right': False})
BLUE, GREEN, RED = '#3478A5', '#4B9271', '#C46B5A'
SCENARIOS = [('final', '数据末值'), ('last_hour_mean', '末小时均值'),
 ('last_hour_meanT_finalC', '末小时均温、末值湿度'), ('t50', '50°C、末值湿度'),
 ('t50c05', '50°C、湿度0.05'), ('stage_mean', '恒温段均值'), ('last2h_mean', '末两小时均值')]
LATENT = [('scen_final', '不含潜热'), ('lat_surf_dry0', '表面潜热：初始干密度'),
 ('lat_vol_dry0', '体积潜热：初始干密度'), ('lat_surf_unit', '表面潜热：单位系数试验'),
 ('lat_vol_unit', '体积潜热：单位系数试验')]

def load(name):
    z = np.load(OUT / (name + '.npz'), allow_pickle=False)
    m = json.loads(str(z['metadata']))
    if m.get('revision') != 'audit-fix-20260912':
        raise ValueError('Stale result: ' + name)
    return z, m

def meta(name):
    return load(name)[1]

def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / name, dpi=300)
    plt.close(fig)

def build_result4(case, filename):
    # Retained exporter; audit regeneration uses --plots-only, preserving verified originals.
    import openpyxl
    z, m = load(case)
    if m['sample_dt'] != 60:
        raise ValueError('Workbook requires 60-second samples')
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Sheet1'
    ws.append(['时间\\到药材中心的距离'] + [round(x, 1) for x in m['field_cols']] + ['药材表面'])
    for t, f in zip(z['time_s'], z['field']):
        if t > 0:
            ws.append([int(t)] + [round(float(v), 4) for v in f[:, 1]])
    for row in ws.iter_rows(min_row=2, min_col=2):
        for cell in row:
            cell.number_format = '0.0000'
    ws.freeze_panes = 'B2'
    wb.save(ROOT / filename)

def fig_drying(case, label, filename):
    from a4_run import Q4Solver
    z, m = load(case)
    s = Q4Solver(n=3)
    ts = z['time_s'] / 3600
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.3))
    for j, color, name in [(0, BLUE, '中心'), (-1, RED, '表面')]:
        ax[0].plot(ts, z['field'][:, j, 1], color=color, label=name)
    ax[0].axhline(.15, color='gray', ls='--', label='阈值 0.15')
    ax[0].axvline(m['minute_h'], color='gray', ls=':')
    ax[0].set(title=f'水分浓度（{label}）', xlabel='时间 / h', ylabel='水分浓度 / (kg/kg)')
    ax[0].legend()
    tr = np.linspace(0, 72, 721)
    ax[1].plot(tr, [s.R_of(t * 3600)*100 for t in tr], color=GREEN)
    ax[1].plot(m['minute_h'], m['endpoint_radius_cm'], 'o', color=RED)
    ax[1].annotate(f"达标 {m['minute_h']:.4f} h\n半径 {m['endpoint_radius_cm']:.4f} cm",
                   (m['minute_h'], m['endpoint_radius_cm']), xytext=(28, 1.48),
                   arrowprops={'arrowstyle': '->', 'color': 'gray'})
    ax[1].set(title='半径变化（72 h观测末值为1.198 cm）', xlabel='时间 / h', ylabel='半径 / cm')
    save(fig, filename)

def fig_cross():
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for name, label, color in [('q3_x800', '固定半径、第三组物性', BLUE),
                                ('q4_tight800', '收缩半径、第四组物性', GREEN)]:
        z, m = load(name)
        ax.plot(z['time_s']/3600, z['field'][:, 0, 1], color=color,
                label=f"{label}（临界 {m['crossing_h']:.2f} h）")
    ax.axhline(.15, color='gray', ls='--')
    ax.set(title='不同几何与物性组合的比较（非收缩单因素试验）',
           xlabel='时间 / h', ylabel='中心水分浓度 / (kg/kg)')
    ax.legend(fontsize=9)
    save(fig, 'fig03_cross_p3.png')

def fig_convergence():
    ref = meta('conv_graded1600')['crossing_s']
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for mesh, label, color in [('graded', '表面加密网格', BLUE), ('uniform', '均匀网格', GREEN)]:
        ns = [400, 800]
        err = [abs(meta(f'conv_{mesh}{n}')['crossing_s'] - ref) for n in ns]
        ax.loglog(ns, err, 'o-', color=color, label=label)
    ax.set(title='共同参考：1600单元加密网格（参考点不绘制零误差）',
           xlabel='单元数 N', ylabel='相对共同参考的临界时刻绝对差 / s')
    ax.legend()
    save(fig, 'fig04_convergence.png')

def fig_scenarios():
    base = meta('scen_final')['crossing_h']
    values = [meta('scen_'+s)['crossing_h'] for s, _ in SCENARIOS]
    delta = [(v/base-1)*100 for v in values]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.barh([l for _, l in SCENARIOS], delta, color=GREEN)
    for i, (v, d) in enumerate(zip(values, delta)):
        ax.text(max(d, 0)+.015, i, f'{v:.4f} h ({d:+.3f}%)', va='center', fontsize=9)
    ax.set_xlim(min(delta)-.03, max(delta)+.34)
    ax.set(title='4 h后环境外推的敏感性（同为400单元）', xlabel='相对数据末值方案的时间变化 / %')
    save(fig, 'fig05_scenarios.png')

def fig_latent():
    fig, ax = plt.subplots(figsize=(9, 4.8))
    for i, (name, label) in enumerate(LATENT):
        m = meta(name)
        assert m['scenario'] == 'final' and m['n'] == 400
        ax.barh(label, m['crossing_h'], color=BLUE if i == 0 else GREEN)
        ax.text(m['crossing_h']+.4, i, f"{m['crossing_h']:.3f} h", va='center')
    ax.set_xlim(0, max(meta(n)['crossing_h'] for n, _ in LATENT)*1.15)
    ax.set(title='潜热模型对照（全部采用数据末值环境、400单元）', xlabel='连续临界时间 / h')
    fig.text(.5, .005, '单位系数仅为人工敏感性试验；表面项与体积项为替代模型，不同时计入。', ha='center', fontsize=9)
    save(fig, 'fig06_latent.png')

def tables():
    z, _ = load('q4_tight800')
    rows = np.column_stack([z['table6_times'], z['table6_field'][:, :, 1]])
    np.savetxt(ROOT/'table6.csv', rows, delimiter=',', fmt='%.4f',
               header='time_h,0cm,0.5cm,1.0cm,surface', comments='')
    (ROOT/'tables4.json').write_text(json.dumps({'time_h': z['table6_times'].tolist(),
            'field_temperature_concentration': z['table6_field'].tolist()}, ensure_ascii=False, indent=2), encoding='utf-8')
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for j, label in enumerate(['0 cm', '0.5 cm', '1.0 cm', '表面']):
        ax.plot(rows[:, 0], rows[:, j+1], 'o-', label=label)
    ax.set(xlabel='时间 / h', ylabel='水分浓度 / (kg/kg)', title='六小时采样与烘干结束时刻')
    ax.legend()
    fig.tight_layout()
    fig.savefig(ROOT/'fig4_p4.png', dpi=300)
    plt.close(fig)

def summary():
    a, b = meta('q4_tight800'), meta('q4_t50_tight800')
    ref = meta('conv_graded1600')
    base = meta('scen_final')['crossing_h']
    fixed = meta('q4_fixed_props_control')['crossing_h']
    lines = ['# 数值核验与修正汇总', '', '## 主结果', '',
             '| 4 h后环境 | 连续临界时间/h | 首个严格达标整分钟/h | 终点半径/cm |',
             '|---|---:|---:|---:|']
    for label, m in [('数据末值维持', a), ('50°C、湿度末值', b)]:
        lines.append(f"| {label} | {m['crossing_h']:.7f} | {m['minute_h']:.7f} | {m['endpoint_radius_cm']:.4f} |")
    lines += ['', f"800→1600加密单元的临界时间差为 {abs(a['crossing_s']-ref['crossing_s']):.6f} s；"
              f"1600单元结果为 {ref['crossing_h']:.7f} h。四位小数的末位仍会变化，不宣称逐位收敛。",
              '', '## 单因素与潜热对照', '',
              f"相同第四组物性、同为400单元：固定半径 {fixed:.6f} h，收缩半径 {base:.6f} h，"
              f"时间变化 {(base/fixed-1)*100:+.3f}%。该对照不等于与第三组物性模型的比较。",
              '', '| 潜热模型（末值环境、400单元） | 临界时间/h |', '|---|---:|']
    lines += [f"| {label} | {meta(name)['crossing_h']:.6f} |" for name, label in LATENT]
    lines += ['', '潜热未被证明已吸收到给定参数中。不含潜热是简化假设，含潜热是明确密度换算后的替代模型；单位系数不是物理标定值。',
              '旧的 dry/bulk 试验采用未加权均值，已禁用，历史文件保留但不参与当前结论。',
              '', '## 环境外推', '', '| 方案 | 临界时间/h | 相对基准 |', '|---|---:|---:|']
    lines += [f"| {label} | {meta('scen_'+s)['crossing_h']:.6f} | {(meta('scen_'+s)['crossing_h']/base-1)*100:+.6f}% |" for s,label in SCENARIOS]
    lines += ['', '## 截图数据', '',
              '截图来源与计算口径未得到确认，不能称为官方答案。以下只给出在指定假设下的复算差异，不把差异直接归因于数值噪声。',
              '', '| 项目 | 截图/h | 本次复算/h | 差值/s |', '|---|---:|---:|---:|']
    for name, target, label in [('scen3_t50',57.46681156,'固定半径、不含潜热'),
              ('q3_lat_surf_dry0_t50',60.46750514,'固定半径、表面潜热'),
              ('q4_t50_tight800',51.0823,'收缩、不含潜热'),
              ('q4_lat_surf_dry0_t50',56.4362,'收缩、表面潜热')]:
        m=meta(name)
        lines.append(f"| {label} | {target} | {m['crossing_h']:.7f} | {(m['crossing_h']-target)*3600:+.3f} |")
    lines += ['', '截图前两问温度尚未在本目录独立复算，不能据此判为正确。',
              '', '## 验证边界', '',
              '修复了辅助情景早期采样缺失、潜热表面重构遗漏、事件后整分钟外推、图2误用主情景、图6混合情景和缺项。',
              '离散恒等式与积分残差只验证所实现方程的一致性，不能证明完整物理质量及能量守恒。热物性有效密度与仿射收缩的干物质密度采用不同闭合，需要独立物理标定。',
              '图像位于 ../04-pic；原工作簿保留，通过 a4_verify.py 逐单元格对照重算数组。']
    (ROOT/'汇总.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--plots-only', action='store_true')
    args=p.parse_args()
    if not args.plots_only:
        build_result4('q4_tight800', 'result4.xlsx')
        build_result4('q4_t50_tight800', 'result4_50度设定值.xlsx')
    fig_drying('q4_tight800', '数据末值维持', 'fig01_drying.png')
    fig_drying('q4_t50_tight800', '50°C设定值', 'fig02_drying_t50.png')
    fig_cross()
    fig_convergence()
    fig_scenarios()
    fig_latent()
    tables()
    summary()
    print('Regenerated six figures, table, and audited summary.')
