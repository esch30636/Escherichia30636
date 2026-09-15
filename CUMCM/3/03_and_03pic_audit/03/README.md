# 03：数值计算与核验（按高精度复核值重做）

当前修订：audit-fix-20260912。第三问主算例与对照共 10 个情景已重算（含 5 个环境外推情景）。
结果见 [汇总.md](汇总.md)，完整论证见 [problem3.md](problem3.md)。

## 运行

本目录需要含 numpy、scipy、numba、pandas、openpyxl、matplotlib 的 Python。

    python run_all.py --recompute     # 重算全部算例 → 生成报告/图 → 重建 workbook → 逐格校验
    python run_all.py --math-only     # 只重算与报告，跳过 workbook（无需 node）
    python produce.py                 # 从已存 tight800 轨迹重建报告/图/表（不重解）
    python check_workbook.py          # 只读校验 result3.xlsx 与轨迹逐格一致

run_all 对每个算例记录 solver/core/输入 的 SHA-256，未变化时复用已有结果。
workbook 重建需 node 与 @oai/artifact-tool（可用环境变量 A3_NODE / A3_NODE_MODULES 指定）。

## 输出与口径

- result3.xlsx：末值环境、800 单元、60 s 采样，3431 行（不含表头），末行 205860 s。
- data/：附件 1 环境序列（ambient.csv）、表 5 原始值、完整精度 NPZ/CSV、workbook 数据。
- verification/：各算例 npz+json、灵敏度、自动核验报告 summary.json 与 workbook_check.json。
- ../03-pic/：四张 200 dpi 图（时空分布/剖面/干燥曲线/敏感性）。
- problem3.md：IEEE 格式解题报告。

连续临界时间不等于首个严格整分钟。四位小数显示 0.1500 不意味着未达标：末行中心
未舍入值 0.149985…，判断使用完整精度。

## 与高精度复核值对照

旧管线（03_and_03pic）给出 57.1840 h = 205862.4 s，并自报 Richardson 极限 205813.1 s、
N=400 网格不确定度 ±49.3 s。本次收敛解：连续临界 205810.08 s（N=800；1600 差 0.24 s），
与旧管线 Richardson 极限差 3.0 s，落在其自报误差带内；由两管线收敛极限推得的首严格
整分钟均为 205860 s，逐秒一致。旧管线把 N=400 未收敛原始临界 205862.4 s 作为主数字，
其与自身收敛极限之差 49.3 s 正是其网格误差估计——复核值与本解在交付分辨率上完全吻合。

## 修复及限制

继承第二问 A2-gpt 的 audited 离散内核，第三问不再使用的旧实现（53.02 h 报告及其
a3_model/a3_solver）已按可定位缺陷逐条说明（见 problem3.md 第 8 节），未修改其原文件。
不含潜热是基准假设；本目录不重算潜热变体。本目录与 03_and_03pic 的旧管线文件并存，
旧包未作任何修改，供追溯。截图来源与计算设置未经确认，不能称为已核实标准答案。
