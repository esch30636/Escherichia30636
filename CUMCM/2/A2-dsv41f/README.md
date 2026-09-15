# A2-dsv41f：A2-gpt 第二问模型审核包

**任务**：审核 `A2/A2-gpt`（GPT-6 Astra 对 A 题第二问的建模）是否正确，提出修改意见。

- **主文档**：[`A2-gpt第二问模型审核报告.md`](A2-gpt第二问模型审核报告.md)
- **机读结论**：[`verification/00_审核结论汇总.json`](verification/00_审核结论汇总.json)

---

## 一页结论

| 方面 | 评定 |
|---|---|
| 交付格式（表名 / 时间轴 1—10800 s / 半径轴 0—2 cm / 四位小数 / 453600 格） | ✅ 正确，与附件 3 模板一致 |
| 控制方程、几何、初值、第三类边界 | ✅ 正确 |
| 空间离散与表面重构的自洽性 | ✅ 自洽（表面节点热平衡残差 ≤7e-9 W/m²） |
| 可复现性 | ✅ 用原始模块重算 10800 s，全场最大差 **7.4e-11** |
| 数值精度 | ✅ 独立复算证实误差 ≤2e-5，与自报一致 |
| 质量守恒（按代码写下的公式） | ✅ 机器精度 |
| **失水量与表面可供能量不相容** | ❌ 潜热需求是可供相变能量的 **66 倍**、是进入药材总能量的 **11.5 倍** |
| **表面能量平衡缺蒸发潜热汇 `L_v·j`** | ❌ 上一条的直接原因 |
| 水分边界通量量纲 `h_m(C_s−C_a)` | ⚠️ 量纲不成立（m/s × kg/kg）；与内部梯度自洽但与外部传热不相容 |
| 网格鲁棒性 | ⚠️ 最外单元 δ→1.6e-8 m，刚度比 >1e12，仅特定容差下稳定 |

**核心结论**：**数学与代码实现是正确的，交付解可以被逐位复现，数值精度也经受住了独立复算；问题出在物理闭合**——表面能量平衡缺了蒸发吸热，使模型排出的水量超出它自己表面所能获得能量的约 12 倍。**表 3 与表 4 需要重算。**

---

## 目录

```
A2-dsv41f/
├─ A2-gpt第二问模型审核报告.md      ← 主报告（结论、证据、修改意见、最小改动清单）
├─ README.md                        ← 本文件
├─ code/                            ← 全部复算与审计脚本（16 个）
└─ verification/                    ← 全部数值证据
```

---

## 如何复现

环境：Windows / Python 3.13.9 / NumPy 2.3.5 / SciPy 1.16.3 / Numba 0.62.1 / openpyxl 3.1.5

```powershell
cd E:\HUST\国赛\A2\A2-dsv41f

# ① 交付格式与内部一致性（秒级，通过）
python code\check_workbook.py

# ② 用原始模块重算 10800 s，与交付逐位比对（约 1 分钟，通过，差 7.4e-11）
python code\reproduce_reference.py

# ③ 表面节点热平衡残差（约 1 分钟，通过）
python code\audit_surface_node.py

# ④ 能量与水量收支 —— 本报告核心证据（秒级，不通过）
python code\audit_energy.py

# ⑤ 质量守恒与通量量纲核对（秒级）
python code\audit_conservation.py

# ⑥ 网格分辨率与刚度（秒级）
python code\diag_mesh.py

# ⑦ 参考格式的稳定性压力测试（分钟级，会实际求解）
python code\diag_stability.py 400 600 1e-9 10
python code\diag_stability.py 800 600 1e-9 10

# ⑧ 独立求解器复算（分钟—小时级；也可直接复用已保存的 npz）
python code\independent_solver.py --n 50  --name indep
python code\independent_solver.py --n 100 --name indep
python code\independent_solver.py --n 200 --name indep
python code\independent_solver.py --n 100 --p 2 --name indepq
python code\independent_solver.py --n 200 --p 2 --name indepq
python code\compare_independent.py verification\indep_n50_p1.0.npz `
    verification\indep_n100_p1.0.npz verification\indep_n200_p1.0.npz `
    verification\indepq_n100_p2.0.npz verification\indepq_n200_p2.0.npz

# ⑨ 汇总机读结论
python code\make_summary.py
```

---

## 脚本说明

| 脚本 | 作用 |
|---|---|
| `check_workbook.py` | 交付物结构、时间/半径轴、四位小数逐格比对 |
| `reproduce_reference.py` | **直接 import `A2-gpt/code/solver.py`**，用相同设置重算 10800 s |
| `audit_surface_node.py` | 表面节点是否满足本方案自身的能量平衡 |
| `audit_energy.py` | **能量与水量收支（核心证据）**：进入药材的能量 vs 蒸发所需潜热 |
| `audit_conservation.py` | 体积平均失水 vs 表面通量积分；说明量纲问题 |
| `diag_mesh.py` | 网格单元尺寸、表面单元时间常数、二阶差分振荡检测 |
| `diag_stability.py` | 用原始模块在 rtol=1e-9 与交付设置下对比，复现近表面失稳 |
| `diag_where.py` | 独立解与交付解差异的空间/时间分布定位 |
| `independent_solver.py` | 独立求解器：网格族、界面系数取法、边界近似、时间积分器全部更换 |
| `compare_independent.py` | 独立解与交付解逐时刻逐半径比对、观测阶 |
| `compare_physics.py` | 均匀网格参考算例汇总 |
| `model_ref.py` | 审计脚本共用的几何与附录 3 物性 |
| `make_summary.py` | 汇总机读结论 |

---

## 证据文件

| 文件 | 内容 |
|---|---|
| `00_审核结论汇总.json` | 报告全部数值结论的机读汇总（**建议先看这个**） |
| `workbook_audit.json` | 交付物格式与逐格比对（通过） |
| `energy_audit.json` | **能量缺口核算（核心证据）** |
| `conservation_check.json` | 通量量纲问题的定量证据 |
| `mesh_resolution.json` | 网格分辨率与刚度表 |
| `independent_comparison.json` | 独立解 vs 交付解（5 个算例） |
| `physics_comparison.json` | 均匀网格参考算例汇总 |
| `indep*_n*.npz` | 独立求解器原始输出（含逐 1800 s 快照） |
| `uni_*_n200_p1.0.npz` | 独立求解器在均匀网格上复现三种边界物理的输出 |

---

## 两点方法学说明

1. **审核方也曾出错，并已更正**：审核过程中一度认为交付终态违反了自身热平衡（残差 6e6 W/m²），据此写了"近表面数值病理"的结论。经用原始模块回代确认，那是**审核方自己的推理错误**，该结论已从报告中全部删除并改为"通过"。报告中保留这条更正记录，便于读者判断其余证据的强度。

2. **定量结论的来源**：报告的核心定量结论（§3 能量缺口、§4 通量量纲）**全部只用交付数据本身与题给参数**（`h`、`h_m`、附录 3 物性、附件 1 环境），**不依赖审核方的任何模型**。`uni_latent` / `uni_psychro` 两个修正物理算例依赖一个题目未给的吸附等温线参数，因此只在报告 §4.3 作**定性**参考，不作为数值结论。
