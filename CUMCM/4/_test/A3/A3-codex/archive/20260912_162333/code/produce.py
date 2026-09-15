"""Generate verified report, CSV/NPZ, figures and Excel input from one trajectory."""
from pathlib import Path
import json,os,shutil,platform
import numpy as np
import scipy
from scipy.optimize import root
from core import mesh,kernel,boundary,face
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'verification/mpl-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

def load(name): return np.load(ROOT/'verification'/f'{name}.npz')
def meta(z): return json.loads(str(z['metadata']))
def compare(a,b):
    m=min(len(a['time_s']),len(b['time_s']))
    assert np.array_equal(a['time_s'][:m],b['time_s'][:m])
    return dict(C=float(np.max(abs(a['C'][:m]-b['C'][:m]))),T=float(np.max(abs(a['T'][:m]-b['T'][:m]))),
                time_s=abs(meta(a)['crossing_s']-meta(b)['crossing_s']))

def independent_audit(z):
    """Independent vectorized operator and two-variable surface nonlinear root."""
    n=len(z['x']);x,v,g,half=mesh(n); results=[]
    def p(t,c):
        return (650+128*c)*(1450+2736*c/(1+c)),.21+.38*c/(1+c),.0024*np.exp(-.45/c-3850/(t+273.15))
    def coeff(t1,c1,t2,c2):
        k=0.;d=0.
        for q,w in zip((.1127016653792583,.5,.8872983346207417),(5/18,8/18,5/18)):
            _,kk,dd=p(t1+q*(t2-t1),c1+q*(c2-c1));k+=w*kk;d+=w*dd
        return k,d
    synthetic=np.empty(2*n);synthetic[0::2]=32+10*(x/.02)**2;synthetic[1::2]=2.1-.7*(x/.02)**2
    for label,y in [('final',z['final_cells']),('smooth',synthetic)]:
        t=y[0::2];c=y[1::2];ta,ca=50.165,.04986
        def residual(u):
            ts,cs=u;k,d=coeff(t[-1],c[-1],ts,cs)
            return [ts-(k*t[-1]+25*half*ta)/(k+25*half),cs-(d*c[-1]+8e-7*half*ca)/(d+8e-7*half)]
        opt=root(residual,[t[-1],c[-1]],tol=1e-11)
        if np.max(abs(np.array(residual(opt.x))))>1e-10: raise RuntimeError('Independent surface solve failed')
        ts,cs=opt.x;k,d=coeff(t[:-1],c[:-1],t[1:],c[1:]);cap,_,_=p(t,c)
        qt=np.r_[0.,g*k*(t[:-1]-t[1:]),.02*25*(ts-ta)]
        qc=np.r_[0.,g*d*(c[:-1]-c[1:]),.02*8e-7*(cs-ca)]
        dy=np.empty(2*n);dy[0::2]=-np.diff(qt)/(v*cap);dy[1::2]=-np.diff(qc)/v
        ref=kernel(y,x,v,g,half,ta,ca,False,25.,8e-7,1.)[0]
        kk,dd=coeff(t[-1],c[-1],ts,cs)
        bc=[kk*(t[-1]-ts)/half-25*(ts-ta),dd*(c[-1]-cs)/half-8e-7*(cs-ca)]
        results.append(dict(state=label,rhs_max_absolute=float(np.max(abs(dy-ref))),
            rhs_relative=float(np.max(abs(dy-ref))/max(np.max(abs(ref)),1e-15)),surface_residual=bc))
    return results

def main():
    z=load('tight800');m=meta(z);t=z['time_s'];c=z['C'];T=z['T'];r=z['radius_cm']
    pairs={key:compare(load(a),load(b)) for key,a,b in [
        ('400_to_800','base400','base800'),('800_to_1600','tight800','fine1600'),
        ('tolerance','base800','tight800'),('BDF_vs_Radau','base400','radau400')]}
    order=np.log2(pairs['400_to_800']['C']/pairs['800_to_1600']['C'])
    # Conservative use of the raw fine-grid difference, rather than division by 3.
    err=pairs['800_to_1600']['C']+pairs['tolerance']['C']+pairs['BDF_vs_Radau']['C']
    q2=ROOT.parents[1]/'A2 /A2-gpt/verification/tight800.npz'
    ref=np.load(q2);idx=t[t<=10800].astype(int); n=len(idx)
    q2diff={k:float(np.max(abs(z[k][:n]-ref[k][idx]))) for k in ['C','T']}
    audit=independent_audit(z)
    summary=dict(main=m,comparisons=pairs,observed_C_order=float(order),C_error_estimate=err,
        q2_difference=q2diff,independent_operator=audit,previous_max=float(z['maxC'][-2]),
        final_max=float(z['maxC'][-1]),sampled_min=float(c.min()),sampled_max=float(c.max()),
        versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
        endpoint_stable=bool(z['maxC'][-2]>=.15 and z['maxC'][-1]<.15))
    assert err<2e-5 and pairs['800_to_1600']['time_s']<30
    assert summary['endpoint_stable'] and m['radial_increase_max']<1e-10
    assert max(q2diff.values())<2e-5
    assert max(m['relative_balances'])<1e-7
    # Near thermal equilibrium the RHS is almost zero; use an absolute floor.
    assert all(a['rhs_max_absolute']<1e-10 or a['rhs_relative']<1e-8 for a in audit)
    assert all(abs(a['surface_residual'][0])<5e-7 and abs(a['surface_residual'][1])<1e-14 for a in audit)
    (ROOT/'verification/summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))
    shutil.copy2(ROOT/'verification/tight800.npz',ROOT/'data/full_precision.npz')
    for key,arr in [('moisture',c),('temperature',T)]:
        np.savetxt(ROOT/f'data/{key}_full_precision.csv',np.c_[t,arr],delimiter=',',fmt='%.17g',
            header='time_s,'+','.join(f'r_{rr:.1f}_cm' for rr in r),comments='')
    indices=list(range(360,len(t),360))
    if indices[-1]!=len(t)-1: indices.append(len(t)-1)
    table=np.c_[t[indices]/3600,c[indices][:,[0,5,10,15,20]]]
    np.savetxt(ROOT/'data/table5.csv',table,delimiter=',',fmt='%.17g',header='time_h,r0_cm,r0.5_cm,r1_cm,r1.5_cm,r2_cm',comments='')
    tablemd='| 时间/h | 0 cm | 0.5 cm | 1.0 cm | 1.5 cm | 2.0 cm |\n|---|---:|---:|---:|---:|---:|\n'
    for i,row in enumerate(table):
        label=f'{row[0]:.4f}' if i==len(table)-1 else f'{row[0]:.0f}'
        if i==len(table)-1: label+='（烘干结束）'
        tablemd+='| '+label+' | '+' | '.join(f'{v:.4f}' for v in row[1:])+' |\n'
    (ROOT/'表5.md').write_text('# 表 5 药材水分浓度（kg/kg，干基）\n\n'+tablemd)
    workbook=dict(header=['时间/s（距离/cm）',*r.tolist()],rows=np.c_[t[1:],np.round(c[1:],4)].tolist())
    (ROOT/'data/workbook.json').write_text(json.dumps(workbook,ensure_ascii=False))
    sens=[]
    names={'mean':'末小时时间加权均值','temp_low':'恒温段温度 −1℃','temp_high':'恒温段温度 +1℃',
           'humid_low':'恒温段环境含水率 −10%','humid_high':'恒温段环境含水率 +10%'}
    base400=meta(load('base400'))['crossing_s']
    for scenario,label in names.items():
        sm=meta(load('s_'+scenario));sens.append(dict(scenario=label,time_h=sm['crossing_s']/3600,
            change_h=(sm['crossing_s']-base400)/3600,tail=sm['tail']))
    (ROOT/'verification/sensitivity.json').write_text(json.dumps(sens,indent=2,ensure_ascii=False))
    font='/System/Library/Fonts/STHeiti Light.ttc'
    if Path(font).exists(): font_manager.fontManager.addfont(font);plt.rcParams['font.family']=font_manager.FontProperties(fname=font).get_name()
    plt.rcParams.update({'axes.unicode_minus':False,'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(8.6,4.8));im=ax.pcolormesh(r,t/3600,c,shading='auto',cmap='viridis')
    ax.contour(r,t/3600,c,levels=[.15],colors='white',linewidths=1)
    ax.set(xlabel='距中心半径 / cm',ylabel='烘干时间 / h',title='药材含水率时空分布（白线为 0.15 等值线）')
    fig.colorbar(im,ax=ax,label='干基含水率 / (kg/kg)');fig.tight_layout();fig.savefig(ROOT/'figures/01_moisture_field.png',dpi=200);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.6,4.8))
    for h in [0,3,6,12,24,36,48]: ax.plot(r,c[int(h*60)],label=f'{h} h')
    ax.plot(r,c[-1],color='black',lw=2,label=f'结束 {t[-1]/3600:.4f} h');ax.axhline(.15,color='gray',ls='--',lw=1)
    ax.set(xlabel='距中心半径 / cm',ylabel='干基含水率 / (kg/kg)',title='径向含水率剖面');ax.legend(loc='upper left',bbox_to_anchor=(1.02,1));fig.tight_layout();fig.savefig(ROOT/'figures/02_profiles.png',dpi=200);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4.5))
    for i in [0,5,10,15,20]:
        axes[0].plot(t/3600,c[:,i],label=f'{r[i]:g} cm');axes[1].plot(t/3600,c[:,i])
    for ax in axes: ax.axhline(.15,color='black',ls='--',lw=1);ax.set(xlabel='烘干时间 / h',ylabel='干基含水率 / (kg/kg)')
    axes[0].set_title('全程干燥曲线');axes[0].legend();axes[1].set(xlim=(45,58),ylim=(.045,.18),title='末期达标过程')
    fig.tight_layout();fig.savefig(ROOT/'figures/03_drying_curves.png',dpi=200);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.6,4.8));vals=[s['time_h'] for s in sens]
    ax.barh([s['scenario'] for s in sens],vals,color='#577c99');ax.axvline(base400/3600,color='#b44d36',ls='--',label='基准（400单元）')
    for i,val in enumerate(vals): ax.text(val+.2,i,f'{val:.3f} h',va='center')
    ax.set(xlim=(0,max(vals)+8),xlabel='临界烘干时长 / h',title='4 小时后环境外推的敏感性');ax.legend(loc='lower left');fig.tight_layout();fig.savefig(ROOT/'figures/04_sensitivity.png',dpi=200);plt.close(fig)
    comparison_md='| 对照 | 含水率最大差/(kg/kg) | 温度最大差/℃ | 临界时间差/s |\n|---|---:|---:|---:|\n'
    for name,pair in pairs.items(): comparison_md+=f"| {name} | {pair['C']:.3e} | {pair['T']:.3e} | {pair['time_s']:.6f} |\n"
    sens_md='| 外推情景 | 临界时长/h | 相对同网格基准变化/h |\n|---|---:|---:|\n'
    for s in sens:sens_md+=f"| {s['scenario']} | {s['time_h']:.4f} | {s['change_h']:+.4f} |\n"
    text=rf'''# A 题第三问：固定几何下药材烘干时长的建模与求解

## 1. 结果与适用口径

沿用第二问 A2-gpt 的热质耦合模型，并假设附件1结束后环境保持末值，连续临界时刻为 **{m['crossing_s']/3600:.6f} h**（{m['crossing_s']:.6f} s）。此时最大含水率等于0.15；严格低于阈值需略晚于该时刻。按题目60 s采样精度，首次全场严格达标为 **{m['minute_s']/3600:.4f} h，即57小时11分钟（{m['minute_s']:.0f} s）**。论文可写约57.18 h，并保留上述精确定义。

前一分钟最大含水率为{z['maxC'][-2]:.10f}，终点为{z['maxC'][-1]:.10f} kg/kg；两者四位小数均可能显示0.1500，因此判断必须使用完整精度数据。中心是本计算的最湿点，终点表面含水率为{c[-1,-1]:.8f}，体积平均为{z['means'][-1]:.8f} kg/kg。

本报告给出的是题给经验参数与明确边界假设下的计算结果。没有内部实测数据，不能把数值误差当作实际预测误差，也不能用题面“一般2—3天”反向校准结果。

## 2. 数据、假设与第二问衔接

- 圆柱长0.25 m、半径R=0.02 m，取轴向中截面径向模型。固定几何、均质、轴对称，忽略端面与轴向梯度；收缩属于第四问。
- 初值T=28℃、C=2.55 kg/kg（干基）。从t=0统一使用附录3，不在1800 s人为切换物性。
- 附件1含0—14400 s的241个观测，间隔60 s，逐段线性插值，不平滑原数据。4 h以后取T_a=50.165℃、C_a=0.04986 kg/kg。
- h=25 W/(m²·K)、h_m=8×10⁻⁷ m/s沿用附录2。设有效表面平衡含水率C_e=C_a；气相与固相kg/kg的参照质量不同，此关系为有效闭合假设，不是已知吸附等温线。
- 沿用第二问显热近似，不额外增加潜热或焓输运。ρ(C)只作为有效热物性，不在固定体积内据此声称严格干物质量守恒。
- 独立目录内的core.py继承第二问离散内核；solve.py扩展积分、终点与收支检查。独立向量算子复核不调用内核的物性或边界函数。Radau对照复用空间离散，仅检验时间算法，不能称为完全独立的PDE求解器。

## 3. 模型建立

令A(C)=ρ(C)c_p(C)，则

$$A(C)\frac{{\partial T}}{{\partial t}}=\frac1r\frac{{\partial}}{{\partial r}}\left(rk(C)\frac{{\partial T}}{{\partial r}}\right),\qquad
\frac{{\partial C}}{{\partial t}}=\frac1r\frac{{\partial}}{{\partial r}}\left(rD(C,T)\frac{{\partial C}}{{\partial r}}\right).$$

$$\rho=650+128C,\quad c_p=1450+2736\frac C{{1+C}},\quad k=0.21+0.38\frac C{{1+C}},$$
$$D=2.4\times10^{{-3}}\exp(-0.45/C)\exp[-3850/(T+273.15)].$$

状态温度以℃存储，Arrhenius指数才换算K。k、D必须保留在散度内部：简单使用D∇²C会遗漏变系数梯度项。温度经D影响失水，含水率经ρ、c_p、k影响传热。

中心条件为T_r(0,t)=C_r(0,t)=0；表面取向外为正：

$$-kT_r(R,t)=h(T_s-T_a),\qquad -DC_r(R,t)=h_m(C_s-C_a).$$

湿度通量J_C=−DC_r是浓度方程的有效通量，单位m/s，不直接称为kg/(m²·s)。若引入恒定干物质体积密度ρ_d，则真实质量通量为ρ_dJ_C，且PDE左右和边界两侧必须同时乘ρ_d，因子相消；不能只在边界右侧乘密度。

初始扩散系数约5.642×10⁻⁹ m²/s，质量Biot数h_mR/D约2.84，不能宣称表面传质阻力必然可忽略。随C下降，D明显减小，形成干燥后期的缓慢扩散。

## 4. 数值方法与终点

网格面r_j=R[1−(1−j/N)²]，单元中心为相邻面的中点，体积权V_i=(r²_{{i+1/2}}−r²_{{i−1/2}})/2，省略公共2πL。每个内部面仅计算一次通量，界面系数沿相邻(T,C)线性路径作三点Gauss积分：

$$Q^T_{{i+1/2}}=\frac{{r_{{i+1/2}}\bar k}}{{r_{{i+1}}-r_i}}(T_i-T_{{i+1}}),\quad
Q^C_{{i+1/2}}=\frac{{r_{{i+1/2}}\bar D}}{{r_{{i+1}}-r_i}}(C_i-C_{{i+1}}).$$

离散方程V_iA_iṪ_i=Q^T_{{i−1/2}}−Q^T_{{i+1/2}}、V_iĊ_i=Q^C_{{i−1/2}}−Q^C_{{i+1/2}}。中心面积为零，自然实现零通量，不计算1/0。

真实表面距最外单元中心δ=R−r_N，通过耦合迭代求解

$$\bar k(T_N-T_s)/\delta=h(T_s-T_a),\quad \bar D(C_N-C_s)/\delta=h_m(C_s-C_a).$$

表面面通量必须是R·h(T_s−T_a)、R·h_m(C_s−C_a)，与物理体积V_i匹配。边界迭代更新差小于2×10⁻¹³才接受，否则报错；不裁剪负值或回填通量。

温度和含水率交错排列并同时积分，提供块三对角稀疏结构。主结果采用800单元、BDF、rtol=10⁻¹¹、atol_T=10⁻¹²、atol_C=10⁻¹³。前4 h每60 s数据节点重启且max_step=10 s；后续连续积分max_step=300 s，60 s输出由稠密解采样，并非积分步长。先搜索72 h，若未达标按24 h延长，30天仍未穿越则报错而不伪造时长。

事件函数是所有单元、对称重构中心和真实表面的最大含水率减0.15。中心按r²重构，内部目标点三点二次插值，表面用边界解。每个60 s输出检查全部单元的径向顺序，本次最大向外增量为{m['radial_increase_max']:.3e}（舍入误差量级），支持中心最湿判断；这不是连续空间的严格误差界。

## 5. 表5与图形

{tablemd}

结束行采用首次达标整分钟，与result3.xlsx末行相同；中间6 h行来自同一条轨迹。result3.xlsx有{len(t)-1}条时间记录、21个半径列，不含t=0；完整精度NPZ和CSV另保留t=0。

![含水率时空分布](figures/01_moisture_field.png)

![径向剖面](figures/02_profiles.png)

![干燥曲线](figures/03_drying_curves.png)

3 h时中心/表面含水率分别为{c[180,0]:.6f}/{c[180,-1]:.6f}，温度分别为{T[180,0]:.6f}/{T[180,-1]:.6f}℃。热平衡较快，内部水分扩散持续数十小时。终点仍有径向湿度梯度，因此平均含水率低于阈值不能替代各处达标。

## 6. 数值验证

{comparison_md}

差异覆盖共同60 s×0.1 cm输出网格。含水率观测收敛阶为{order:.4f}。以800与1600单元原始差、容差差及BDF/Radau差相加，取较保守的误差估计{err:.3e} kg/kg，小于2×10⁻⁵；不将原始空间差除以3。这是工程误差估计，不是严格上界，四位小数末位仍可能受舍入分界影响。

对照第二问已保存的tight800轨迹，0—10800 s每60 s采样最大差为：C {q2diff['C']:.3e} kg/kg、T {q2diff['T']:.3e}℃，说明第三问准确承接第二问。独立向量算子在最终状态与非均匀合成状态上复核物性、面通量、几何及独立非线性边界根，详情见verification/summary.json。

水分积分量M=ΣV_iC_i（不直接等于kg），恒等式Ṁ=−Q_C(R)。独立三点Gauss时间积分边界通量后，相对闭合误差为{m['relative_balances'][0]:.3e}。

显热诊断量E=ΣV_iA(C_i)T_i，链式法则给出

$$\dot E=-Q_T(R)+\sum_i V_iA'(C_i)T_i\dot C_i.$$

其中第二项是变热容的导数修正，不是往PDE加入焓输运。积分闭合相对误差为{m['relative_balances'][1]:.3e}；质量和热方程的离散恒等式绝对残差分别为{m['identity_abs'][0]:.3e}、{m['identity_abs'][1]:.3e}。这些验证只说明所选有效PDE和显热方程被正确离散，**不代表完整蒸发质量—能量模型守恒**。未通过调整通量样本消除残差。

## 7. 环境外推敏感性

{sens_md}

敏感性采用400单元，并与相同网格基准相比；末小时均值由10800—14400 s梯形积分除以3600得到。扰动仅在4 h后启用，可能在切换处引入小跳变，求解器在该处重启。以上情景不是概率分布或置信区间。

![外推敏感性](figures/04_sensitivity.png)

## 8. 与A3-ds已有结论的差异

已有报告给出53.02 h；本次首次整分钟结果比其晚约{m['minute_s']/3600-53.02:.4f} h。差异不能只归因于潜热，已有代码存在以下可定位问题：

1. a3_model.py的geom_scaled返回V=R²∫s ds，a3_solver.py内部面采用r_f/Δr，但表面使用q/R、j/R；应为Rq、Rj。数值系数相差1/R²=2500，而且量纲不匹配。通量望远镜抵消成立也不能证明选用的边界尺度正确。
2. 表面传质只在右侧乘ρ_d，而内部浓度方程未作对应换算；并将无量纲网格倒数用作表面传导尺度，不能替代物理半单元宽度。
3. 原报告Biot数计算及“小Biot意味着表面阻力可忽略”的解释有误；以本题初值直接计算h_mR/D≈2.84，不能支持该论断。
4. 原实现额外加入潜热和焓输运，与第二问主模型不同。完整物理扩展需要重新论证质量基准、能量储存与气固平衡，不能用修改后的53.02 h作为本问校准目标。

本次未修改原A3-ds文件，也未声称只修某一个缺陷就能得到当前结果。数值方案与第二问保持一致，差异来自模型及实现口径的整体恢复。

## 9. 局限与复现

固定半径、中截面径向近似忽略端面；前问短时端部误差不能直接推广到57 h。C_e=C_a、显热近似及4 h后恒定环境属于主要模型假设。敏感性只考察规定的环境情景，未覆盖潜热、吸附等温线或轴向扩散。模型精度需内部温湿实验进一步检验。

运行入口与依赖见README.md；核心结果data/full_precision.npz含time_s、radius_cm、T、C、maxC、means、final_cells、x、v及metadata。T单位℃、C单位kg/kg、x单位m、v单位m²，means为环形体积加权含水率。各算例配置、积分残差、版本和时间保存在verification。工作簿回读报告单独存为verification/workbook_check.json。

## 10. 数据与方法来源

1. 本地《2026年高教社杯全国大学生数学建模竞赛 A题：药材的烘干问题》，第三问、附录2和附录3；附件1及附件3/result3.xlsx。题定经验系数直接来自原题，不归给外部论文。输入SHA-256见data/source_sha256.json。
2. 本地第二问A2-gpt的建模报告、code/solver.py和已保存tight800结果：本次衔接与复算基线。
3. [SciPy solve_ivp 官方文档](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html)：隐式BDF、Radau、事件定位、稠密输出及稀疏Jacobian接口。访问日期2026-09-12；程序实际使用SciPy {scipy.__version__}。
'''
    (ROOT/'建模报告.md').write_text(text)
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
