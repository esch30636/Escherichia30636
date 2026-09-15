"""Build report and publication-style static scientific figures from checked runs."""
from pathlib import Path
import os,json,csv
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'verification/mpl_cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from solver import properties
z=np.load(ROOT/'data/full_precision.npz')
s=json.loads((ROOT/'verification/summary.json').read_text())
sens=json.loads((ROOT/'verification/sensitivity.json').read_text())
t=z['time_s']/3600;r=z['radius_cm'];T=z['T'];C=z['C']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,
                     'axes.titleweight':'bold','figure.dpi':130,'savefig.dpi':220,'axes.grid':False})
colors=['#17365D','#247BA0','#2A9D8F','#D99637','#C75146']
def save(fig,name):
    fig.canvas.draw()
    fig.savefig(ROOT/'figures'/f'{name}.png',bbox_inches='tight')
    fig.savefig(ROOT/'figures'/f'{name}.svg',bbox_inches='tight');plt.close(fig)

fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
for ax,arr,label,cmap in zip(axs,[T,C],['Temperature (°C)','Moisture (kg/kg, dry basis)'],['inferno','viridis']):
    im=ax.pcolormesh(t[::10],r,arr[::10].T,shading='auto',cmap=cmap)
    ax.set(xlabel='Time (h)',ylabel='Radius (cm)',title=label);fig.colorbar(im,ax=ax)
save(fig,'01_fields')

fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
for j,col in zip([0,5,10,15,20],colors):
    axs[0].plot(t,T[:,j],color=col,label=f'{r[j]:.1f} cm')
    axs[1].plot(t,C[:,j],color=col,label=f'{r[j]:.1f} cm')
for ax,yl in zip(axs,['Temperature (°C)','Moisture (kg/kg)']):
    ax.set(xlabel='Time (h)',ylabel=yl);ax.grid(alpha=.15);ax.legend(frameon=False)
save(fig,'02_evolution')

fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
for sec,col in zip([1800,3600,5400,7200,10800],colors):
    axs[0].plot(r,T[sec],color=col,label=f'{sec/3600:g} h');axs[1].plot(r,C[sec],color=col,label=f'{sec/3600:g} h')
for ax,yl in zip(axs,['Temperature (°C)','Moisture (kg/kg)']):
    ax.set(xlabel='Radius (cm)',ylabel=yl);ax.grid(alpha=.15);ax.legend(frameon=False)
fig.set_layout_engine(None)
fig.subplots_adjust(left=.10,right=.98,bottom=.18,top=.95,wspace=.30)
axs[0].legend(frameon=False,loc='center left')
save(fig,'03_profiles')

fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
for ax,key,yl in zip(axs,['T','C'],['Temperature difference (°C)','Moisture difference (kg/kg)']):
    errs=[q[key] for q in s['space_differences_200_400_800']]+[s['space_difference_800_1600'][key]]
    ax.loglog([200,400,800],errs,'o-',color=colors[0],label='Grid N vs 2N')
    ax.loglog([200,400,800],np.array([1,1/4,1/16])*errs[0],'--',color=colors[3],label='Second-order reference')
    ax.axhline(2e-5,color=colors[-1],ls=':',label='Target error scale')
    ax.set(xlabel='Coarser grid cells N',ylabel=yl);ax.grid(alpha=.15,which='both');ax.legend(frameon=False)
save(fig,'04_convergence')

fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
labels=['h -5%','h +5%','hm -5%','hm +5%','D -5%','D +5%','PCHIP']
for ax,key,unit in zip(axs,['T','C'],['°C','kg/kg']):
    ax.barh(labels,[ss[f'max_delta_{key}'] for ss in sens],color=colors[1]);ax.invert_yaxis()
    ax.set(xlabel=f'Maximum absolute change ({unit})',title=f'{"Temperature" if key=="T" else "Moisture"} sensitivity');ax.grid(axis='x',alpha=.15)
save(fig,'05_sensitivity')

fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
a1=np.load(ROOT/'data/a1_reference.npz')
for ax,key,ak,yl in zip(axs,['T','C'],['T_C','C_kgkg'],['Temperature difference (°C)','Moisture difference (kg/kg)']):
    for j,col in zip([0,10,20],[colors[0],colors[2],colors[4]]):
        ax.plot(t[:1801]*60,z[key][:1801,j]-a1[ak][:,j],color=col,label=f'{r[j]:.1f} cm')
    ax.set(xlabel='Time (min)',ylabel=yl,title='Q2 minus Q1: changed material laws');ax.legend(frameon=False);ax.grid(alpha=.15)
save(fig,'06_q1_comparison')

def table(arr):
    lines=['| 时间/h | 0 cm | 0.5 cm | 1 cm | 1.5 cm | 2 cm |','|---|---:|---:|---:|---:|---:|']
    for sec in range(1800,10801,1800):lines.append('| '+f'{sec/3600:.1f}'+' | '+' | '.join(f'{arr[sec,j]:.4f}' for j in [0,5,10,15,20])+' |')
    return '\n'.join(lines)
conv=['| 网格对照 | 温度最大差/℃ | 含水率最大差/(kg/kg) |','|---|---:|---:|']
for title,dd in zip(['200→400','400→800','800→1600'],s['space_differences_200_400_800']+[s['space_difference_800_1600']]):conv.append(f'| {title} | {dd["T"]:.6e} | {dd["C"]:.6e} |')
sens_table=['| 情景 | 全场最大温度变化/℃ | 全场最大含水率变化 | 末期表面温度变化/℃ | 末期表面含水率变化 |','|---|---:|---:|---:|---:|']
for label,row in zip(labels,sens):sens_table.append(f'| {label} | {row["max_delta_T"]:.6f} | {row["max_delta_C"]:.6f} | {row["final_surface_delta_T"]:+.6f} | {row["final_surface_delta_C"]:+.6f} |')
cap,k,d,_=properties(28.,2.55,False,1.)
e=s['estimated_errors'];b=s['balances'];reg=s['a1_regression'];f=s['final']
report=r'''# 第二问：变物性与温湿双向耦合的药材干燥模型

## 摘要

对半径2 cm、长度25 cm的圆柱药材，从初始状态开始统一采用附录3的经验公式，建立固定几何下的径向导热—水分扩散耦合模型。模型可描述预热向近恒温环境的连续演化；本次严格使用附件1提供的环境数据，计算0—10800 s，不另设1800 s物性切换，也不对4小时之后的环境作外推。

最终采用800单元表面加密有限体积与BDF积分。3小时末中心与表面温度为 **@TC@℃、@TS@℃**，含水率为 **@CC@、@CS@ kg/kg**。所有10800×21个输出点的温度和含水率数值误差估计分别为 **@ET@℃、@EC@ kg/kg**，均低于2×10⁻⁵。此为所建模型的工程数值误差估计，不是药材实测预测误差，也不是严格数学误差上界。

## 1. 数据、研究对象与假设

初值为均匀的28℃和干基含水率2.55 kg/kg。附件1含241个环境观测，0—14400 s、间隔60 s。相邻点间线性插值，严格使用每个观测，不平滑替换。结果取轴向中截面的径向分布；假设均质、轴对称，忽略轴向梯度，第二问半径固定。第一问的中截面端部检验只覆盖30分钟，不能直接作为本问3小时端部误差的定量证明。

附录3未另给界面系数，因此沿用附录2的 h=25 W/(m²·K)、h_m=8×10⁻⁷ m/s。固体表面有效平衡含水率设为 C_e=C_a；气相与固相的 kg/kg 参照质量通常不同，此处是使用题给传质系数的有效闭合，不是已经由实验验证的吸附等温线。

主模型采用显热近似；不额外加入潜热、辐射、内部流动和收缩。ρ(C)作为有效热物性使用，不将其与固定体积下严格守恒的干物质量强行等同。因此本模型描述的是题给经验条件下的有效场演化，不是完整多相质量与能量模型。全文引用编号对应《参考文献.md》。

## 2. 经验公式与耦合机制

题给公式[1]为

$$
\rho(C)=650+128C,\quad c_p(C)=1450+2736\frac{C}{1+C},
$$
$$
k(C)=0.21+0.38\frac{C}{1+C},\quad
D(C,T)=2.4\times10^{-3}\exp\left(-\frac{0.45}{C}\right)
\exp\left(-\frac{3850}{T+273.15}\right).
$$

这里代码状态变量T以℃计，只有最后一个指数使用K；C以干基kg/kg计。所有常数来自题目，不将它们归给外部论文。初始状态下有效体积热容为 @CAP@ J/(m³·K)，k=@K@ W/(m·K)，D=@D@ m²/s。

热质双向耦合具体表现为：温度改变D，从而改变失水速度；C改变ρ、c_p、k，从而改变温度分布。[2]给出变物性热质传递建模实例，[3]提供农产品耦合干燥研究背景，[4]展示温度波动相关的扩散建模。它们支持方法选择，但各自材料参数不能直接移植。

局部温度扩散系数 α=k/(ρc_p) 与水分扩散系数不同；不能把温度和含水率看作同一时间尺度的均匀状态，也不能用纯时间经验拟合代替题目要求的空间分布。

## 3. 控制方程及边界

令A(C)=ρ(C)c_p(C)，取向外为正的通量。圆柱薄壳积分后得到

$$
A(C)\partial_tT=\frac1r\partial_r\big(rk(C)\partial_rT\big),\qquad
\partial_tC=\frac1r\partial_r\big(rD(C,T)\partial_rC\big).
$$

初值为T(r,0)=28、C(r,0)=2.55。中心对称条件为T_r(0,t)=C_r(0,t)=0；真实表面的Robin条件为

$$
-k(C_s)T_r(R,t)=h(T_s-T_a(t)),\qquad
-D(C_s,T_s)C_r(R,t)=h_m(C_s-C_a(t)).
$$

当环境较热时热通量为负，表示热流入；C_s>C_a时水分向外输运。中心用零面积通量处理，不直接计算1/r。

必须保留k、D在散度内。水分方程展开后包含 D_C(C_r)²+D_T T_r C_r，热方程含 k_C C_r T_r；简单把D或k乘在常系数拉普拉斯算子外会漏掉这些项。附录3从t=0就使用，阶段变化通过边界驱动与局部物性自然体现。

## 4. 数值离散与实现

### 4.1 径向网格与通量

取网格面r_j=R[1-(1-j/N)²]，单元中心取相邻面的中点；环形体积权重（略去公共2πL）为 V_i=(r_{i+1/2}²-r_{i-1/2}²)/2。采用点值型单元中心有限体积近似，并用网格收敛验证其精度。

内部界面上定义线性状态路径(T(ξ),C(ξ))=(T_i,C_i)+ξ[(T_{i+1},C_{i+1})-(T_i,C_i)]，ξ∈[0,1]。用三点Gauss积分求平均系数 k̄、D̄，两侧共享同一个通量：

$$
Q^T_{i+1/2}=\frac{r_{i+1/2}\bar k_{i+1/2}}{r_{i+1}-r_i}(T_i-T_{i+1}),\quad
Q^C_{i+1/2}=\frac{r_{i+1/2}\bar D_{i+1/2}}{r_{i+1}-r_i}(C_i-C_{i+1}).
$$

同一个界面通量在相邻单元内一正一负，保证内部通量抵消。与第一问不同，D同时依赖T、C，此处不声称存在单变量的全局Kirchhoff变换；它是沿局部状态路径的界面求积。有限体积的理论背景见[5]。

### 4.2 表面值重构

最后一个单元中心到表面的距离为δ，耦合解

$$
\bar k(T_N-T_s)/\delta=h(T_s-T_a),\quad
\bar D(C_N-C_s)/\delta=h_m(C_s-C_a).
$$

采用固定点迭代，同时更新T_s、C_s和路径系数；更新差必须小于2×10⁻¹³，否则显式报错。该重构是半单元边界近似，不能把最外单元中心当作真实表面。最终状态的边界残差另经独立代回检查。

中心按r²对称重构，内部目标半径用局部三点二次插值，输出表面采用上述Robin重构。t=0单独保留均匀初值；初始含水率与Robin边界不兼容，时间推进负责解析初始表面薄层。结果不进行负值裁剪。

### 4.3 耦合积分

离散方程是 V_i A(C_i)Ṫ_i=Q^T_{i-1/2}-Q^T_{i+1/2}、V_i Ċ_i=Q^C_{i-1/2}-Q^C_{i+1/2}。T、C交错存储并同时推进，避免热、质先后单次更新产生的分裂误差。

采用SciPy BDF[6]，提供块三对角稀疏结构，每60秒数据节点重启，避免跨越线性插值斜率突变。最终rtol=10⁻¹¹，温度atol=10⁻¹²℃、含水率atol=10⁻¹³ kg/kg，最大内部步长10 s；通过积分器稠密输出在每个整秒采样，整秒采样不等于采用1 s时间步。800单元主计算实际接受18820个步；运行耗时受机器与编译缓存影响，以保存日志为准。

## 5. 数值验证与误差估计

### 5.1 全场空间、时间与积分方法验证

@CONV@

以上差异覆盖全部10800×21个输出点。200/400/800序列观测阶为温度 @PT@、含水率 @PC@。800/1600比较采用收紧后的容差，避免时间误差主导。

800单元BDF容差从10⁻⁹收紧至10⁻¹¹的最大差为温度 @TT@℃、含水率 @CT@ kg/kg。同网格同容差Radau与BDF最大差为温度 @TR@℃、含水率 @CR@ kg/kg。Radau更换的是时间积分算法，使用相同的空间离散，不能据此宣称两套完全独立的PDE实现。

采用有数值二阶证据支持的保守组合估计

$$
E_u=\frac43\|u_{800}-u_{1600}\|_\infty
+\|u_{800,10^{-9}}-u_{800,10^{-11}}\|_\infty
+\|u_{800,\mathrm{BDF}}-u_{800,\mathrm{Radau}}\|_\infty.
$$

4/3对应保留的800单元较粗解；不误用细网格的1/3系数。温度E_T=@ET@℃，含水率E_C=@EC@ kg/kg。交付采用800单元BDF实际结果，不用Richardson外推替换。此估计包括输出重构的网格差异，但不是区间证明；四位小数附近的舍入边界仍可能出现末位差别。

![网格收敛检查](figures/04_convergence.png)

### 5.2 方程收支与基本检查

水分检验为 ΣV_i C_i(t)-ΣV_i C_i(0)+∫Q^C_Rdt。热方程不能直接验证ΣV_i A(C_i)T_i的变化等于边界热量，因为A随C变化。利用链式法则验证

$$
\sum_iV_i[A(C_i)T_i]_0^t+\int_0^tQ^T_R\,ds
-\int_0^t\sum_iV_i A'(C_i)T_i\dot C_i\,ds=0.
$$

积分在每个接受时间步的稠密轨迹上用三点Gauss重新求积，检查值在每60秒节点保存。水分相对残差为 @MB@，热方程积分恒等式相对残差为 @HB@；分别以最终边界水分交换量、热交换量的绝对值归一化。这些是所建方程的收支检验，不是潜热、多相总能量或变密度下绝对失水质量的证明。

均匀平衡态右端、物性解析导数、开尔文换算、界面求积对照以及表面通量代回均通过。所有逐秒内部状态和输出值有限，未出现负含水率；机器舍入可在28℃或2.55附近产生10⁻¹⁴量级偏差，不以裁剪掩盖。

### 5.3 A1回归与物理口径差异

将同一套求解器退化为附录2物性，在0—1800 s与A1完整精度数据比较，全场最大差为温度 @AT@℃、含水率 @AC@ kg/kg，均小于2×10⁻⁵。计算代码不导入A1求解模块，A1数据只作为核验基准。

实际第二问采用不同的物性公式，因此它与A1前30分钟结果不应完全相同。0—1800 s最大温度差为 @QAT@℃，最大含水率差为 @QAC@ kg/kg；这是模型变化，不是把A1“纠正”为另一组结果。第二问初始有效体积热容较大，表面与内部升温表现随之改变，同时温度与含水率对扩散的反馈改变失水分布。

![第二问与第一问对比](figures/06_q1_comparison.png)

## 6. 第二问结果

### 表3：3小时内药材的温度，单位℃

@TABLET@

### 表4：3小时内药材的水分浓度，单位kg/kg（干基）

@TABLEC@

前期表面先升温、先失水；3小时末温差降至约 @TDIFF@℃，而中心到表面的含水率差仍约 @CDIFF@ kg/kg，表明热均衡较快，水分均匀化仍需较长时间。不能把温度接近烘房温度视作干燥已经完成。

体积平均含水率定义为 C̄=2/R²∫₀ᴿrCdr，用实际环形体积权重计算；末值为 @CMEAN@ kg/kg。它不同于21个输出点的简单算术平均，也不直接给出真实失水克数。第一问已有审核文本中的平均量结论不直接移植，本问平均量始终由本问网格计算。

![温度与含水率时空分布](figures/01_fields.png)

![代表半径的时间演化](figures/02_evolution.png)

![代表时刻的径向剖面](figures/03_profiles.png)

## 7. 敏感性与适用范围

同为400单元、rtol=10⁻⁹的对照实验，仅改变单个参数或插值方式，其余保持一致。

@SENS@

±5%是人为设置的确定性情景，不是参数误差标准差或置信区间。与第一问的解耦结构不同，此处h扰动也影响水分，h_m和D扰动也会反过来影响温度；这是双向耦合的可检查结果。

![输入敏感性](figures/05_sensitivity.png)

局限包括：有效表面平衡关系未由吸附数据辨识；显热近似没有验证蒸发潜热可忽略；固定几何与径向中截面近似不描述端部和收缩；经验参数只在题给建模口径下使用。附件1是环境输入，不是药材内部温湿测量，故没有实验RMSE、R²或统计置信区间。文献内的实验验证结果不属于本模型。

方程在提供完整环境边界且经验公式仍适用时可继续描述更长干燥过程；本次输出严格止于3小时，不推算第三问干燥终点，也不假定后续72小时保持某个环境值。

## 8. 交付与复算

`result2.xlsx`含“温度”“水分浓度”两张工作表，各10800行时间记录、21个径向值，数值保留四位小数；`data/full_precision.npz`与CSV另含t=0初始行。报告表3、表4从同一完整精度结果生成。

`code/`提供数据读取、求解、复算、分析、作图和工作簿生成程序；`verification/`保存每个工况、误差和逐格检查；`参考文献.md`给出规范题录、实际可用链接和访问失败记录。所有新增文件位于A2/A2-gpt，原题、附件及A1基准的哈希复核保持一致。具体环境、命令和输出字段见README。
'''
replace={'TC':f'{f["T_center"]:.4f}','TS':f'{f["T_surface"]:.4f}','CC':f'{f["C_center"]:.4f}','CS':f'{f["C_surface"]:.4f}',
         'ET':f'{e["T"]:.6e}','EC':f'{e["C"]:.6e}','CAP':f'{cap:.3f}','K':f'{k:.6f}','D':f'{d:.6e}',
         'CONV':'\n'.join(conv),'PT':f'{s["observed_order"]["T"]:.4f}','PC':f'{s["observed_order"]["C"]:.4f}',
         'TT':f'{s["time_tightening_difference"]["T"]:.6e}','CT':f'{s["time_tightening_difference"]["C"]:.6e}',
         'TR':f'{s["BDF_Radau_difference"]["T"]:.6e}','CR':f'{s["BDF_Radau_difference"]["C"]:.6e}',
         'MB':f'{b["mass_relative"]:.6e}','HB':f'{b["heat_identity_relative"]:.6e}',
         'AT':f'{reg["T"]:.6e}','AC':f'{reg["C"]:.6e}','QAT':f'{s["q2_vs_a1_first1800"]["T"]:.6f}',
         'QAC':f'{s["q2_vs_a1_first1800"]["C"]:.6f}','TABLET':table(T),'TABLEC':table(C),
         'TDIFF':f'{T[-1,-1]-T[-1,0]:.4f}','CDIFF':f'{C[-1,0]-C[-1,-1]:.4f}','CMEAN':f'{f["volume_mean_C"]:.8f}',
         'SENS':'\n'.join(sens_table)}
for key,value in replace.items():report=report.replace('@'+key+'@',value)
assert '@TABLE' not in report
(ROOT/'建模报告.md').write_text(report,encoding='utf-8')
for key,arr in [('table3_temperature',T),('table4_moisture',C)]:
    np.savetxt(ROOT/f'data/{key}.csv',np.column_stack((np.arange(1,7)/2,arr[1800::1800][:,[0,5,10,15,20]])),delimiter=',',
               fmt='%.4f',header='time_h,r_0_cm,r_0.5_cm,r_1_cm,r_1.5_cm,r_2_cm',comments='')
print('Report and 6 PNG/SVG figures saved.')
