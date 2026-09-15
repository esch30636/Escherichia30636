"""Publish two compatible datasets/reports from the accepted shared-engine runs."""
from pathlib import Path
import json,csv,hashlib,os,platform
import numpy as np
from joint_verify import root,read,meta,WORKSPACE
os.environ.setdefault('MPLCONFIGDIR',str(root(3)/'verification/mpl-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties,fontManager
FONT='/System/Library/Fonts/STHeiti Light.ttc'
if Path(FONT).exists():fontManager.addfont(FONT);plt.rcParams['font.family']=FontProperties(fname=FONT).get_name()
plt.rcParams.update({'font.size':11,'axes.unicode_minus':False,'axes.spines.top':False,'axes.spines.right':False})

def plot_save(r,name):
    plt.tight_layout();plt.savefig(r/'figures'/f'{name}.png',dpi=200);plt.savefig(r/'figures'/f'{name}.svg');plt.close()

def publish(q):
    r=root(q);s=json.loads((r/'verification/summary.json').read_text());d=read(q,s['main_name']);m=meta(d)
    t=d['time_s'];hours=t/3600;C=d['C'];T=d['T'];R=d['radius_m']*100;xi=d['xi'];cx=d['C_xi']
    # Preserve A4's original 101-point visualization interface; add full QA arrays.
    payload={k:d[k] for k in d.files}
    payload.update(xi_validation=xi,C_validation=cx,T_validation=d['T_xi'],xi=xi[::10],C_xi=cx[:,::10],T_xi=d['T_xi'][:,::10])
    if q==3:
        legacy=dict(m)
        legacy['integrals_material']=m['integrals']
        legacy['integrals']=[m['integrals'][1],.02**2*m['integrals'][0],m['integrals'][2]]
        legacy['balances']=[.02**2*m['balance'][0],m['balance'][1]]
        legacy['relative_balances']=m['relative_balance']
        payload['metadata']=json.dumps(legacy)
    np.savez_compressed(r/'data/full_precision.npz',**payload)
    for name,vals in [('moisture',C),('temperature',T)]:
        header=['time_s']+[f'r_{x:.1f}_cm' for x in d['distance_cm']]+(['surface'] if q==4 else [])
        with (r/'data'/f'{name}_full_precision.csv').open('w',newline='') as f:
            w=csv.writer(f);w.writerow(header)
            for tt,row in zip(t,vals):w.writerow([int(tt)]+['' if np.isnan(v) else format(v,'.17g') for v in row])
    np.savetxt(r/'data/radius_by_time.csv',np.c_[t,R],delimiter=',',header='time_s,radius_cm',comments='',fmt='%.17g')
    indices=list(range(360,len(t),360))
    if not indices or indices[-1]!=len(t)-1:indices.append(len(t)-1)
    cols=[0,5,10,15,20] if q==3 else [0,5,10,21]
    columns=['时间/h','0 cm','0.5 cm','1.0 cm']+(['1.5 cm','2.0 cm'] if q==3 else ['药材表面','表面位置/cm'])
    table='| '+' | '.join(columns)+' |\n|---'+'|---:'*(len(columns)-1)+'|\n';tabledata=[]
    for i in indices:
        row=[*C[i,cols]]+([R[i]] if q==4 else []);tabledata.append([hours[i],*row])
        label=f'{hours[i]:.4f}（结束）' if i==len(t)-1 else f'{hours[i]:.0f}'
        table+='| '+label+' | '+' | '.join('—' if np.isnan(v) else f'{v:.4f}' for v in row)+' |\n'
    (r/f'表{q+2}.md').write_text(f'# 表{q+2} 药材干基含水率（kg/kg）\n\n'+table)
    np.savetxt(r/f'data/table{q+2}.csv',tabledata,delimiter=',',fmt='%.17g',header=','.join(columns),comments='')
    rows=[[int(tt)]+[None if np.isnan(v) else float(f'{v:.4f}') for v in row] for tt,row in zip(t[1:],C[1:])]
    (r/'data/workbook.json').write_text(json.dumps(dict(header=['时间/s（距离/cm）',*d['distance_cm'].tolist()]+(['药材表面'] if q==4 else []),rows=rows),ensure_ascii=False,allow_nan=False))
    fig,ax=plt.subplots(figsize=(8.6,4.8))
    im=ax.pcolormesh(hours,xi,cx.T,shading='auto',cmap='viridis',rasterized=True)
    ax.contour(hours,xi,cx.T,levels=[.15],colors='white',linewidths=1)
    ax.set(xlabel='时间 / h',ylabel='材料坐标 ξ = r/R(t)',title=f'第{q}问：含水率时空分布')
    fig.colorbar(im,ax=ax,label='干基含水率 / (kg/kg)');plot_save(r,'hp01_field')
    fig,ax=plt.subplots(figsize=(9,4.8))
    for i in indices[::2]:ax.plot(R[i]*xi,cx[i],label=f'{hours[i]:g} h')
    ax.plot(R[-1]*xi,cx[-1],color='black',lw=1.5,label=f'结束 {hours[-1]:.4f} h')
    ax.axhline(.15,color='gray',ls='--');ax.set(xlabel='实际半径 / cm',ylabel='干基含水率 / (kg/kg)',title='径向剖面')
    ax.legend(loc='upper left',bbox_to_anchor=(1.02,1));plot_save(r,'hp02_profiles')
    fig,axes=plt.subplots(1,2,figsize=(10.5,4.5))
    for ax in axes:
        ax.plot(hours,d['maxC'],label='全场最大');ax.plot(hours,d['means'],label='加权平均');ax.plot(hours,C[:,-1],label='表面')
        ax.axhline(.15,color='gray',ls='--');ax.set(xlabel='时间 / h',ylabel='干基含水率 / (kg/kg)')
    axes[0].legend();axes[0].set_title('完整干燥过程');axes[1].set(xlim=(hours[-1]-6,hours[-1]),ylim=(.045,.18),title='终点附近')
    plot_save(r,'hp03_drying')
    fig,ax=plt.subplots(figsize=(8.6,4.8));keys=['space','time','quadrature','independent_convergence','independent_agreement']
    labels=['空间加密','时间收紧','界面求积','独立解加密','两方法差异']
    vals=[s.get('component_estimates',{}).get(k,s['checks'][k]['C']) for k in keys]
    ax.bar(labels,vals,color='#486c88');ax.set_yscale('log')
    ax.set(ylabel='含水率误差估计 / (kg/kg)',title=f'最大误差分量 {s["C_error_estimate"]:.2e} kg/kg');plot_save(r,'hp04_accuracy')
    if s.get('sensitivity'):
        fig,ax=plt.subplots(figsize=(9,4.8));ax.barh([a['label'] for a in s['sensitivity']],[a['delta_h'] for a in s['sensitivity']],color='#486c88')
        ax.axvline(0,color='gray');ax.set(xlabel='相对同网格基准的时间变化 / h',title='环境与插值情景（不含潜热）');plot_save(r,'hp05_sensitivity')
    checks='| 对照 | 含水率最大差/(kg/kg) | 温度最大差/℃ | 临界时间差/s |\n|---|---:|---:|---:|\n'
    names={'space_previous':'前一级空间加密','space':'主网格→双倍网格','time':'容差收紧且步长减半','quadrature':'三点→五点Gauss','independent_convergence':'独立解网格加倍','independent_agreement':'主解↔独立细网格解'}
    for key,values in s['checks'].items():checks+=f'| {names[key]} | {values["C"]:.3e} | {values["T"]:.3e} | {values["time_s"]:.6f} |\n'
    physics=(r'\rho=650+128C,\quad c_p=1450+2736\frac{C}{1+C},\quad k=0.21+0.38\frac{C}{1+C},\quad D=2.4\times10^{-3}e^{-0.45/C}e^{-3850/(T+273.15)}'
        if q==3 else r'\rho=760+90C,\quad c_p=1850+2150\frac{C}{1+C},\quad k=0.12+0.20\frac{C}{1+C},\quad D=4.2\times10^{-4}e^{-0.30/C}e^{-3850/(T+273.15)}')
    sens='| 情景 | 临界时间/h | 相对同网格基准变化/h |\n|---|---:|---:|\n'
    for a in s.get('sensitivity',[]):sens+=f'| {a["label"]} | {a["time_h"]:.6f} | {a["delta_h"]:+.6f} |\n'
    mechanism=''
    if 'mechanism' in s:
        mechanism='| 受控算例 | 连续临界时间/h |\n|---|---:|\n'
        for label,value in s['mechanism'].items():mechanism+=f'| {label} | {value:.6f} |\n'
    reg=s['degenerate_regression'];H=int(t[-1]//3600);M=int(t[-1]%3600//60)
    report=rf'''# 第{q}问：统一材料坐标下的高精度药材烘干模型

## 1. 结果、精度与修订范围

本次统一修订后，连续临界时刻为 **{m['crossing_s']/3600:.6f} h（{m['crossing_s']:.6f} s）**，此时最大干基含水率等于0.15。首次严格达标整分钟为 **{hours[-1]:.4f} h，即{H}小时{M}分钟（{t[-1]:.0f} s）**。结束时间与每分钟输出采用同一轨迹。

前一分钟最大值为{s['previous_max']:.10f}，结束时为{s['final_max']:.10f} kg/kg。判定使用未舍入值；四位小数显示0.1500并不意味着两时刻状态相同。结束时表面为{C[-1,-1]:.8f}，加权平均为{d['means'][-1]:.8f} kg/kg，半径为{R[-1]:.6f} cm。

主计算{m['n']}单元，含水率误差估计 **{s['C_error_estimate']:.3e} kg/kg**，临界时间误差估计 **{s['time_error_estimate_s']:.6f} s**，分别满足10⁻⁶ kg/kg和1 s目标。相对旧版连续时刻改变{s['change_from_old_s']:+.6f} s。六位小数用于数值复核，不表示具有同等实验预测精度。

本轮两问共用同一个生产内核、同一环境输入和边界口径。第三问是第四问关闭收缩、恢复附录3后的特例。没有通过调参压小两问时长差，没有计算潜热影响。

## 2. 原始数据、假设与符号

药材初始长L=0.25 m、半径R₀=0.02 m、T₀=28℃、C₀=2.55 kg/kg（干基）。采用均质、轴对称、中截面径向近似，忽略轴向梯度与端面。第三问固定半径、采用附录3；第四问采用附录4和附件2的145个半径观测（0—72 h，每1800 s），长度不变，内部均匀比例收缩。

两问都从初始状态重算；第四问不接第三问的最终状态。附件1的241个观测覆盖0—14400 s，逐段线性插值；之后保持50.165℃、0.04986 kg/kg。第四问半径逐段线性插值。若超出72 h，半径取末值并在元数据中标记；实际第四问主结果未超过原半径数据范围。

状态T以℃存储，只有Arrhenius指数换成K。向外通量为正；h=25 W/(m²·K)、h_m=8×10⁻⁷ m/s。取有效表面平衡含水率C_e=C_a作为题给参数下的闭合假设，并不声称气相与固相kg/kg天然具有相同参照质量。

本问附录{q}物性为

$${physics}.$$

ρ(C)仅用于有效体积热容A=ρc_p；守恒辅助干密度ρ_d用于说明干物质运动，两者不强行混同。本次采用显热近似，不加入潜热、机械功或水分携带焓。

## 3. 统一模型推导

设收缩速度u=rṘ/R、干物质守恒：

$$\partial_t\rho_d+\frac1r\partial_r(r\rho_du)=0,$$
$$\partial_t(\rho_dC)+\frac1r\partial_r(r\rho_dCu)=\frac1r\partial_r(r\rho_dD C_r).$$

均匀比例收缩给出ρ_d(t)=ρ_d(0)(R₀/R)²，其空间梯度为零。消去干物质守恒式得到

$$C_t+uC_r=\frac1r\partial_r(rDC_r),\qquad A(C)(T_t+uT_r)=\frac1r\partial_r(rkT_r).$$

C是水质量与干物质质量的比值，不能添加−2ṘC/R这一体积浓度压缩源项。取材料坐标ξ=r/R(t)，时间导数换算中的−ξṘ/R项与uC_r抵消，得到固定计算域0≤ξ≤1上的共同方程：

$$\boxed{{C_t=\frac1{{R^2\xi}}\partial_\xi(\xi DC_\xi)}},\qquad
\boxed{{A(C)T_t=\frac1{{R^2\xi}}\partial_\xi(\xi kT_\xi)}}.$$

此处时间导数固定ξ。第三问R≡R₀、u=0，严格退化为固定圆柱方程。变系数k、D均保留在散度内；温度影响D，水分影响ρ、c_p、k，温湿状态同时推进。

中心T_ξ=C_ξ=0；表面条件为

$$-\frac kR T_\xi=h(T_s-T_a),\qquad -\frac DR C_\xi=h_m(C_s-C_a).$$

浓度有效通量J_C=−DC_r单位m/s；真实质量通量为ρ_dJ_C。若换成真实质量通量，边界两侧同时包含ρ_d并相消，不能只把某一侧乘密度。所有边界梯度都使用物理距离，半径以米传入。

## 4. 主数值方法与独立求解器

主方法采用单元中心有限体积，网格面ξ_j=1−(1−j/N)²，v_i=(ξ²_{{i+1/2}}−ξ²_{{i−1/2}})/2。内部每个面只计算一次通量：

$$Q^T_{{i+1/2}}=\frac{{\xi_{{i+1/2}}\bar k}}{{\xi_{{i+1}}-\xi_i}}(T_i-T_{{i+1}}),\qquad
Q^C_{{i+1/2}}=\frac{{\xi_{{i+1/2}}\bar D}}{{\xi_{{i+1}}-\xi_i}}(C_i-C_{{i+1}}).$$

界面物性沿相邻温湿状态线性路径作三点Gauss积分，另以五点求积检验。离散方程为R²v_iA_iṪ_i=Q^T_{{i−1/2}}−Q^T_{{i+1/2}}、R²v_iĊ_i=Q^C_{{i−1/2}}−Q^C_{{i+1/2}}。中心面面积为零，不计算1/0。

表面物理半单元距离δ=R(1−ξ_N)，求解k̄(T_N−T_s)=hδ(T_s−T_a)、D̄(C_N−C_s)=h_mδ(C_s−C_a)。最后边界面通量为Rh(T_s−T_a)、Rh_m(C_s−C_a)，与R²v匹配。非线性边界迭代差小于2×10⁻¹³才接受，否则报错；不裁剪含水率或回填通量。

主结果使用BDF、rtol={m['rtol']:.0e}、atol_T={m['rtol']*.1:.0e}℃、atol_C={m['rtol']*.01:.0e}。前4 h最大步长10 s，此后{m['max_step']:g} s；在环境和半径数据节点处重启。每60 s输出由稠密解采样，不等同于积分步长。

独立方法重新实现节点型有限体积：节点ξ_j=1−(1−j/N)^1.5，包含真实中心和表面，控制体面为节点中点；表面节点具有半控制体，直接施加Robin通量，不调用主方法的表面代数重构。独立物性、五点Gauss通量及Radau积分完成从t=0到终点的全轨迹，细网格为{s['independent_n']}个区间。两方法只共用输入、时间分段和输出调度，不共用空间算子。

主方法中心按ξ²对称重构，其他位置三点二次插值；第四问实际距离通过ξ=r/R(t)映射，域外填空而不是0。每分钟同时保存1001个材料坐标验证点，检查全部单元及重构输出的最大值。事件函数包含全单元、中心与表面；加密和独立解必须得到相同的首次达标整分钟。

## 5. 题定表格与图像

{table}

表{q+2}结束行采用首次严格达标整分钟，与result{q}.xlsx末行一致；中间6 h行来自同一轨迹。工作簿{len(t)-1}条时间记录，NPZ/CSV另保留t=0。第四问域外为空、末列为真实表面，不能把收缩后的表面硬标成某个固定距离。

![时空分布](figures/hp01_field.png)

![径向剖面](figures/hp02_profiles.png)

![干燥过程与终点](figures/hp03_drying.png)

## 6. 数值精度与联合验证

{checks}

比较同时覆盖共同每60 s时刻的有效实际距离点、真实表面及1001个材料坐标点。空间观测阶为{s['observed_order']:.4f}。生产网格和独立网格的最后一次空间差按二阶收敛换算为细网格剩余误差；时间、求积和两方法差保留原值，含水率误差取各分量最大值，避免同一截断误差被重复相加。这是有限验证轨迹上的工程估计，不是连续场严格上界，更不是实验预测误差。

![误差分量](figures/hp04_accuracy.png)

第四问关闭收缩、切换附录3后，同配置回归第三问的最大含水率差为{reg['C']:.3e}、温度差{reg['T']:.3e}、时间差{reg['time_s']:.6g} s，满足10⁻⁹ kg/kg与0.01 s要求。前3 h与第二问的比对另记录在第三问验证摘要；新旧网格不同导致的微小差异需与旧版误差范围一起解释。

固定域与线性收缩域制造解测试使用T=35+3sin(t/3000)+4ξ²、C=1+0.1sin(t/2000)−0.2ξ²，解析代回生成体积源和边界，仅用于测试，不进入实际题目。两套方法均在40/80/160网格上检验二阶收敛。另在零换热、零传质下验证均匀收缩不改变干基含水率。原始记录见verification/manufactured.json。

## 7. 水分收支与显热诊断

材料参考权重下M=Σv_iC_i，Ṁ=−Q_C/R²。真实水质量只需乘公共常数2πLρ_d(0)R₀²，不必虚构ρ_d(0)。显热诊断量E=R²Σv_iA(C_i)T_i满足

$$\dot E=-Q_T+R^2\sum_i v_iA'(C_i)T_i\dot C_i+2\frac{{\dot R}}R E.$$

最后两项来自链式法则中的变热容与几何体积变化，不是给PDE添加潜热或焓输运。本次对实际接受步内的边界通量与修正项作三点Gauss时间积分，水分相对残差{m['relative_balance'][0]:.3e}，显热诊断相对残差{m['relative_balance'][1]:.3e}。固定半径时几何项自动为0。没有用结果倒推通量令残差闭合。

这些检验说明所选有效方程被一致离散，不表示已经建立完整多相能量模型。

## 8. 物性、收缩与环境情景

{mechanism}

物性变化和收缩效应分别通过受控算例比较，不能把第三、四问的净差全部归于收缩，也不能为了让两问数值接近而调整物性。中间固定半径附录4算例另作网格复核。

{sens}

环境情景只在4 h后启用；半径PCHIP情景保留每个原始观测。敏感性采用400单元并与同网格基准比较，用来描述模型输入影响，不作为主结果的10⁻⁶精度证据，也不是置信区间。

![情景敏感性](figures/hp05_sensitivity.png)

## 9. 局限与后续模型改进

主模型保留显热近似、C_e=C_a、径向近似和4 h后恒定环境；第四问另假设长度不变和均匀比例收缩。题给有效热密度ρ(C)与干物质守恒辅助密度未建立完整多相本构关系。端面、内部非均匀收缩、开裂和气固平衡关系都可能影响真实结果；没有实测内部数据，不能给出实验RMSE或预测准确率。

潜热留待论文“模型改进”部分：后续需先统一真实水质量通量及干密度口径，再按蒸发发生位置选择表面热汇或内部相变源，避免重复计入。本次不计算、不估算潜热导致的时长修正。

## 10. 文件接口与复现

一键入口见README.md。两问唯一生产内核位于A3/A3-codex/code/drying_common，第四问显式导入该包。输入、配置和数学源码均纳入缓存哈希；原题附件只读。旧版交付完整归档在各自archive目录，本报告所有新数字由当前验收通过的主轨迹生成。

兼容数据字段time_s、T、C、maxC、means、final_cells继续保留。第三问x、v仍为物理m与m²；第四问x、v仍为无量纲ξ与∫ξdξ。新增xi_cells、v_xi明确共同计算网格，新增xi_validation、T_validation、C_validation保存1001点验证数据；原xi/T_xi/C_xi维持101点可视化接口。第四问C/T前21列为实际0—2 cm，末列为真实表面；域外NaN、CSV/Excel为空。温度℃，含水率kg/kg，半径radius_m为m。

输入来源为原题第三、四问及附录3、4、附件1、2与结果模板；数值接口参考[SciPy solve_ivp官方文档](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html)。已有物理背景参考文献保留在第四问参考文献.md；本轮未引入新的材料经验系数。完整验收、制造解、场误差、终点和工作簿回读证据见verification。
'''
    (r/'建模报告.md').write_text(report)
    dependency={str(p.relative_to(WORKSPACE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (root(3)/'code/drying_common').glob('*.py')}
    dependency['A3/A3-codex/data/full_precision.npz']=hashlib.sha256((root(3)/'data/full_precision.npz').read_bytes()).hexdigest()
    (r/'data/shared_basis_sha256.json').write_text(json.dumps(dependency,ensure_ascii=False,indent=2))
    return s

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('question',type=int,choices=[3,4]);a=p.parse_args();publish(a.question)
