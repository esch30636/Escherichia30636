# A1-codex：第一问交付与复算

先阅读 **建模报告.md**。题目要求的完整表格是 **result1.xlsx**；每个工作表含 1–1800 s、0–2 cm 每隔0.1 cm的结果，数值保留四位小数。

## 已完成的结果

- 创新组合：Kirchhoff 积分通量、表面加密网格、全隐式守恒求解与自适应时间误差预算。
- 最终计算：800 个径向单元，表面加密指数2，热/质自适应预算各为2.5e-5。
- 全场估计数值误差：温度5.34e-6 ℃、含水率8.11e-6 kg/kg；均小于2e-5。
- 核验：解析解、独立 BDF、网格/时间收敛、质量/显热收支、输入敏感性、端部情景及 Excel 逐格回读。
- 没有药材内部实测数据，因此上述误差不等于真实预测误差。

## 文件结构

| 文件或目录 | 用途 |
|---|---|
| 建模报告.md | 完整推导、题定两表、创新对照、验证与局限 |
| result1.xlsx | 温度、水分浓度两张输出表；共75600个结果数值 |
| data/full_precision.npz | time_s、radius_cm、T_C、C_kgkg及1800 s完整单元值 |
| data/temperature_full_precision.csv、moisture_full_precision.csv | 17位有效数字导出；含t=0初始行 |
| data/ambient.csv | 附件1的只读提取副本 |
| data/source_sha256.json | 题面、环境附件、原模板的校验值 |
| figures/ | 5张可直接用于报告的中文PNG图 |
| verification/summary.json | 最终误差、守恒、运行版本和关键结果 |
| verification/*.csv | 空间/时间误差、创新对照、敏感性 |
| verification/*.npz、*.config.json | 各次算例结果与参数，可用于复核，单位见报告 |
| verification/workbook_check.json、final_checks.json | Excel逐格检查、物理极限及交付一致性结果 |
| code/ | 全部可运行源码，未依赖已有“A题建模”代码 |

## 本机复算

数学计算使用已有 `E:\anaconda\python.exe`，版本及科学库详见 requirements.txt。输入读取和 Excel 检查使用 Codex 自带 Python；工作簿由自带 Node 和 `@oai/artifact-tool` 生成，未使用 openpyxl 写入。

在本目录打开 PowerShell：

```powershell
python code/run_all.py --recompute
```

此命令按顺序重新提取输入、计算收敛试验、独立基准、敏感性、最终精度结果、报告和图像，再导出 Excel 并回读检查。需要数分钟，具体时间依赖硬件；高精度后向 Euler 计算较慢是已披露的方法成本。省略 `--recompute` 会复用已有同参数数值缓存；修改源码或输入后应使用 `--recompute`。

只重算数学结果、不生成 Excel：

```powershell
python code/run_all.py --recompute --math-only
```

仅重新汇总已保存的结果与图像：

```powershell
python code/produce.py
```

核心接口：`solver.solve(n, dt, budget, interpolation, h_factor, hm_factor, d_factor, end, power)`。其中 dt 是最大候选大步长，budget=0 表示固定步长，budget>0 表示步长加倍；power=1为均匀网格，power=2为表面加密。返回 T/C 的形状为 `(end+1,21)`，包含t=0，半径单位cm，温度单位℃，含水率单位kg/kg。该接口为本题实验代码，默认输入要求已生成 data/ambient.csv。

结果缓存文件中 Tstats/Cstats 的顺序为：接受大步数、拒绝大步数、Newton迭代数、最小/最大大步长、单元值最小/最大值、累计向外边界交换量。自适应每个接受大步由两次半步组成。

## 在其他电脑上运行

数学代码可用 Python 3.13 与 requirements.txt 中的依赖运行。保留项目上级的 `CUMCM2026Problems/A题` 输入目录，或调整 extract_inputs.py 的 source 路径。环境CSV已随交付保存，可直接调用 solver，无需重新读取Excel。

工作簿生成另需 Node.js 及 `@oai/artifact-tool`。本机 run_all.py 会在 code/node_modules 建立指向 Codex 自带库的目录联接；它是本机运行设置，不是交付数据。其他电脑可配置该包后执行 `node code/build_workbook.mjs`，再运行 `python code/check_workbook.py`。如果没有该工作簿工具，可直接使用已交付的 XLSX；数学结果、CSV、NPZ不依赖它。

## 复现和解释边界

输入参数扰动±5%是敏感性情景，不是统计置信区间。Ce=Ca、显热方程、固定半径与中截面径向近似均是显式模型假设。预算收紧和 Richardson 估计支持数值精度，但不构成区间算术意义下的严格误差界。四位小数格式不能保证所有邻近舍入分界值的末位不变。

原有“A题建模”文件和题目附件未被修改。
