"""Joint reproducible workflow; adaptively refine until both accuracy gates pass."""
from pathlib import Path
import argparse,json,os,sys,subprocess,hashlib
from drying_common.engine import solve
from joint_verify import root,read,meta,assess,compare,finalize,WORKSPACE

def support_cases(recompute=False):
    labels={'mean':'末小时均值外推','temp_low':'环境温度 −1℃','temp_high':'环境温度 +1℃','humid_low':'环境含水率 −10%','humid_high':'环境含水率 +10%'}
    results={}
    for q in (3,4):
        solve(root(q),q,'scenario_base',n=400,recompute=recompute)
        with read(q,'scenario_base') as d:base=meta(d)['crossing_s']
        cases=['mean','temp_low','temp_high','humid_low','humid_high'] if q==3 else ['pchip','temp_low','temp_high','humid_low','humid_high']
        rows=[]
        for case in cases:
            options=dict(interp='pchip') if case=='pchip' else dict(scenario=case)
            solve(root(q),q,'scenario_'+case,n=400,recompute=recompute,**options)
            with read(q,'scenario_'+case) as d:
                mm=meta(d);rows.append(dict(label=labels.get(case,'半径PCHIP插值'),n=400,time_h=mm['crossing_s']/3600,delta_h=(mm['crossing_s']-base)/3600))
        results[q]=rows
    return results

def numerical(recompute=False):
    selected={}
    for q,start_n,ind_n in ((3,3200,6400),(4,6400,6400)):
        n=800
        # 6400 is the production finest grid retained for both questions;
        # Q4 uses the independent 6400-cell track as its second full check.
        while n<=min(2*start_n,6400):
            solve(root(q),q,f'hp{n}',n=n,recompute=recompute);n*=2
        ni=1600
        while ni<=ind_n:
            solve(root(q),q,f'ind{ni}',n=ni,backend='independent',recompute=recompute);ni*=2
        main_n=start_n
        while True:
            solve(root(q),q,f'time{main_n}',n=main_n,rtol=1e-12,max_step=150.,recompute=recompute)
            solve(root(q),q,f'quad{main_n}',n=main_n,order=5,recompute=recompute)
            a=assess(q,main_n,ind_n,strict=False)
            if a['passed']:break
            print('Refining failed budget',q,a['C_error_estimate'],a['time_error_estimate_s'],flush=True)
            # Refine whichever spatial contribution currently dominates.
            if a['checks']['independent_convergence']['C']>a['checks']['space']['C']:
                ind_n*=2;solve(root(q),q,f'ind{ind_n}',n=ind_n,backend='independent',recompute=recompute)
            else:
                main_n*=2;solve(root(q),q,f'hp{main_n*2}',n=main_n*2,recompute=recompute)
            if max(main_n,ind_n)>51200:raise RuntimeError('Accuracy target not reached; investigate error floor rather than publish')
        selected[q]=(main_n,ind_n)
    return selected

def finish(selected,sensitivity):
    q3n=selected[3][0]
    solve(root(4),4,'q3_regression',n=q3n,shrink=False,appendix=3)
    # Controlled appendix-4 fixed-radius experiment gets its own grid check.
    n=3200
    while True:
        for k in (n,2*n):solve(root(4),4,f'fixed4_{k}',n=k,shrink=False,appendix=4)
        check=compare(4,f'fixed4_{n}',f'fixed4_{2*n}')
        if check['C']<=1e-6 and check['time_s']<=1:break
        n*=2
        if n>51200:raise RuntimeError('Mechanism comparison has not converged')
    with read(3,f'hp{q3n}') as a,read(4,f'hp{selected[4][0]}') as b,read(4,f'fixed4_{2*n}') as c:
        mechanisms={'附录3，固定2 cm':meta(a)['crossing_s']/3600,'附录4，固定2 cm':meta(c)['crossing_s']/3600,'附录4，附件2收缩':meta(b)['crossing_s']/3600}
    for q in (3,4):
        report=finalize(q,*selected[q],q3main_n=q3n)
        report.update(sensitivity=sensitivity[q],mechanism=mechanisms,mechanism_grid_check=check)
        (root(q)/'verification/summary.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
    from joint_produce import publish
    publish(3);publish(4)
    # Separate immutable originals from intentionally updated cross-question basis.
    for q in (3,4):
        r=root(q);old=json.loads((r/'data/source_sha256.json').read_text())
        originals={p:h for p,h in old.items() if p.startswith('CUMCM2026Problems')}
        for p,h in originals.items():assert hashlib.sha256((WORKSPACE/p).read_bytes()).hexdigest()==h
        (r/'data/source_sha256.json').write_text(json.dumps(originals,indent=2,ensure_ascii=False))
    revision(selected)

def revision(selected):
    ss={q:json.loads((root(q)/'verification/summary.json').read_text()) for q in (3,4)}
    rows='| 问题 | 旧临界时刻/h | 新临界时刻/h | 改变量/s | 主网格 | 含水率误差估计 | 时间误差估计/s |\n|---|---:|---:|---:|---:|---:|---:|\n'
    for q,s in ss.items():rows+=f'| 第{q}问 | {s["old_crossing_s"]/3600:.6f} | {s["main"]["crossing_s"]/3600:.6f} | {s["change_from_old_s"]:+.6f} | {s["main_n"]} | {s["C_error_estimate"]:.3e} | {s["time_error_estimate_s"]:.6f} |\n'
    text='''# 第三、四问联合修订说明

本次按统一有效模型完成高精度复算；潜热仅保留在模型改进的文字讨论中，没有潜热算例或时长修正计算。

'''+rows+'''
两问共用A3/A3-codex/code/drying_common中的材料坐标内核。第三问固定半径使用附录3，第四问使用附录4与题给收缩数据；第四问从初始状态计算。两问物性与几何造成的差异被保留，没有拟合已有时长。

主要改进：每分钟1001个材料坐标点全场误差检查；独立节点型有限体积/Radau全轨迹；固定域与移动域制造解；独立方法自身加密；时间和界面求积误差分离；严格整分钟终点核验。误差预算对最后一次空间加密按二阶收敛估计细网格余项，时间、求积和独立方法差保留原值，并取最大分量，避免同一空间截断误差重复计数。

细网格表面单元极小，自动启动步长的显式试探可能进入负含水率。生产网格N≥6400时显式指定首步1e-14 s，之后交由隐式自适应积分控制；没有裁剪解或修改物理系数。该修复不改变低于6400网格的执行分支。较早算例的实际源码哈希保留在元数据，历史引擎源文件保存在verification/source_versions；一键复算会按完整当前源码哈希重算失效缓存。

干物质和热物性密度继续分开处理，显热收支只是有效方程诊断，不被解释为完整蒸发能量守恒。没有内部实测数据，因此这里的高精度只针对数值离散。

旧报告、代码、数据、图和验证文件已在各自archive目录归档，未复制运行时依赖链接。当前建模报告、题定Excel、表5/表6及hp前缀图像是新版交付；旧图和早期算例仅供溯源，不用于新版结论。
'''
    for q in (3,4):
        r=root(q);s=ss[q];m=s['main'];end=m['minute_s'];hour=int(end//3600);minute=int(end%3600//60)
        (r/'联合修订说明.md').write_text(text)
        readme=f'''# A{q}-codex：统一高精度建模交付

先阅读 **建模报告.md**；与另一问的协调修订见 **联合修订说明.md**。题定文件为 **result{q}.xlsx**，简表为 **表{q+2}.md**。

- 连续临界时刻：{m['crossing_s']/3600:.6f} h（最大含水率恰等于0.15）。
- 首次严格达标整分钟：{hour}小时{minute}分钟，{end/3600:.4f} h、{end:.0f} s。
- 主网格{s['main_n']}单元，独立Radau解{s['independent_n']}个区间。
- 工程数值误差估计：含水率{s['C_error_estimate']:.3e} kg/kg，临界时间{s['time_error_estimate_s']:.6f} s；均通过新目标。

潜热仅留在后续模型改进的文字讨论，本轮没有潜热算例。4 h后环境固定为末值，采用显热、有效气固平衡及径向近似；数值误差不代表实验预测精度。

## 文件与接口

| 文件 | 内容 |
|---|---|
| 建模报告.md、联合修订说明.md | 完整推导、时长、精度和新旧差异 |
| result{q}.xlsx、表{q+2}.md | 每60 s、每0.1 cm及每6 h简表 |
| data/full_precision.npz、CSV | 同一条验收通过轨迹，含t=0；Excel从60 s开始 |
| figures/hp*.png、hp*.svg | 新版图像，SVG中的场色块栅格化，文字坐标为矢量 |
| verification/summary.json | 误差分量、退化回归、制造解、收支、旧版差异 |
| verification/workbook_check.json | 全工作簿逐格回读与题定表一致性 |
| archive/ | 修改前归档；latest.json指向本轮旧版 |

共享生产包位于A3/A3-codex/code/drying_common；两问入口只传入各自配置。保留整个A3、A4及原题目录，避免只移动第四问而丢失共享依赖。独立节点型有限体积不调用生产物性、面通量或表面闭合。

NPZ保留原字段：第三问T/C为21个固定距离列，第四问为21个固定距离列加真实表面列，域外为NaN；CSV/Excel域外为空。第三问x、v单位m、m²，第四问x、v为ξ、∫ξdξ；新增xi_cells、v_xi是共同内部坐标。原xi/T_xi/C_xi为101点，新xi_validation/T_validation/C_validation为1001点。time_s为秒，radius_m为米，温度℃，含水率kg/kg。第三问metadata中原integrals/ balances口径保留，新增integrals_material说明共同参考权重下的积分量。

## 一键复算

任一问入口都会协调重算并更新两问，顺序为主解和独立解、精度门槛、制造解、敏感性与受控算例、回归、报告和Excel回读。不会重复归档；如需保留当前版本，应先另存。

```bash
OPENBLAS_NUM_THREADS=1 /opt/anaconda3/bin/python '{r}/code/run_all.py' --recompute
```

其他计算机使用安装了requirements.txt依赖的Python；保持目录相对位置。完整严格复算包含细网格和独立求解，可能需要较长时间。只计算与生成报告、不导出Excel：

```bash
python code/run_all.py --math-only
python code/verify.py
python code/produce.py
python code/check_workbook.py
```

未加--recompute时，仅当全部数学源码、输入和配置哈希一致才复用缓存；更新源码后失效的旧算例会重算，不伪造新的来源哈希。单独produce只根据已通过验收的summary整理该问，不自动重算物理模型。

Excel由Codex捆绑Node及@oai/artifact-tool生成；A{q}_NODE、A{q}_NODE_MODULES可覆盖工具位置。code/node_modules是本机依赖链接，迁移时重建。openpyxl仅用于读取检查，未启动原生Excel应用。

## 验证边界

误差在每分钟全部题定有效距离、真实表面及1001个材料坐标点上比较，并检查全单元最大值与径向次序；它是有限验证网格上的工程误差估计，不是连续场严格上界。最后一次空间加密按观测二阶阶数估计细网格余项，时间、求积和独立方法差保留原值，取最大分量并避免重复计数。敏感性情景采用400单元，与同网格基准比较，不作为高精度主解的误差证据。首次达标根据未舍入结果，不能用Excel显示0.1500作判据。
'''
        (r/'README.md').write_text(readme)

def main():
    p=argparse.ArgumentParser();p.add_argument('--recompute',action='store_true');p.add_argument('--math-only',action='store_true');a=p.parse_args()
    selected=numerical(a.recompute)
    subprocess.run([sys.executable,str(root(3)/'code/manufactured.py')],check=True)
    sens=support_cases(a.recompute);finish(selected,sens)
    if not a.math_only:
        deps=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies'
        for q in (3,4):
            node=Path(os.environ.get(f'A{q}_NODE',str(deps/'node/bin/node')));link=root(q)/'code/node_modules'
            if not link.exists():link.symlink_to(Path(os.environ.get(f'A{q}_NODE_MODULES',str(deps/'node/node_modules'))),target_is_directory=True)
            subprocess.run([str(node),str(root(q)/'code/build_workbook.mjs')],check=True)
            subprocess.run([sys.executable,str(root(q)/'code/check_workbook.py')],check=True)

if __name__=='__main__':main()
