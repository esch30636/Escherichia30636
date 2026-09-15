# 第二问独立建模包 A2-gpt

已完成前3小时变物性温湿耦合计算，统一采用附录3，从初始状态重算。最终主解：800单元、BDF、rtol=1e-11。建模口径、公式、表3/4和局限见 [建模报告](建模报告.md)，外部文献可访问性见 [参考文献](参考文献.md)。

## 主要交付

- `result2.xlsx`：严格按题目表结构，温度/水分浓度两张表，1—10800秒，0—2 cm每0.1 cm，四位小数，共453600个结果值。
- `data/full_precision.npz`：与Excel一致的完整精度主结果，另含t=0；温度为℃，含水率为干基kg/kg。
- `data/temperature_full_precision.csv`、`data/moisture_full_precision.csv`：不需专用工具即可读取；`table3_temperature.csv`与`table4_moisture.csv`为报告简表。
- `figures/`：6组PNG/SVG科学图，SVG可编辑、PNG可直接用于论文。
- `verification/summary.json`：数值误差估计、BDF/Radau对照、A1回归、收支和输入哈希检查。
- `verification/workbook_check.json`：实际重新打开xlsx后逐格比对的结果；四张工作簿首尾预览已人工视觉检查。
- `verification/reference_access.json`：文献本次访问状态；不把搜索命中或验证页计作全文可用。

## 复算环境与命令

本次科学计算用 `/opt/anaconda3/bin/python`（Python3.13.9，NumPy2.3.5、SciPy1.16.3、Numba0.62.1、Matplotlib3.10.6）。工作簿由Codex捆绑Node和 `@oai/artifact-tool` 生成，使用捆绑Python的openpyxl重新打开检查。捆绑Python没有SciPy，所以科学计算使用本机已有Anaconda环境，没有安装或修改系统依赖。

下面命令在本目录运行，或将脚本路径改为绝对路径。已包含所需环境CSV、模板副本及A1基准副本，因此数值求解和工作簿生成均不依赖A1代码。只有原始附件重新提取和原件哈希核对需要保留原工作区目录结构。

```bash
cd '/Users/wangxinlei/Desktop/Xinlei/HUST/数模/A2/A2-gpt'
/opt/anaconda3/bin/python code/run_verification.py
/opt/anaconda3/bin/python code/analyze.py
/opt/anaconda3/bin/python code/produce_report.py
/Users/wangxinlei/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node code/build_workbook.mjs
/Users/wangxinlei/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 code/check_workbook.py
```

`run_verification.py`默认复用本包已保存的同名NPZ。要实际重新计算而不覆盖交付主解，可使用新的运行名：

```bash
/opt/anaconda3/bin/python code/solver.py --name rerun800 --n 800 --rtol 1e-11
```

要修改模型后重做全套验证，应先把已有 `verification/*.npz` 移至独立备份目录，再执行以上命令；不要把旧缓存与新模型混用。验证程序的误差阈值不通过会报错，不自动宣布成功。图表可独立重新生成，不需再运行数值求解。

`prepare_inputs.py`仅在需要重新读取原始附件时运行。`code/build_workbook.mjs`会清理导出器自动生成的巨大 `.inspect.ndjson` 软件诊断侧文件，保留精简检查日志。`node_modules`是本机捆绑包的符号链接，迁移到另一台机器需重新链接到可用的 `@oai/artifact-tool` 安装；不要复制该链接所指向的整个运行时。

## 求解接口及数据字段

`solver.solve(n, end, rtol, method, q1, hfactor, hmfactor, dfactor, interp, audit)`返回字典，`method`取BDF或Radau，`interp`取linear或pchip。end为正整数秒且不超过附件覆盖范围。q1=True仅供第一问退化回归，不参与第二问主结果。

| 字段 | 说明 |
|---|---|
| time_s、radius_cm | 时间与输出半径 |
| T、C | (end+1,21)完整精度点值 |
| means | 逐秒环形体积平均温度、含水率 |
| x_m、volumes | 内部单元中心及省略公共2πL后的体积权重 |
| final_cells | 内部最终状态，按T₀,C₀,T₁,C₁…交错 |
| balances | 每60秒节点的水分、热积分恒等式残差及积分项 |
| metadata | 运行参数、方法、耗时和积分器统计的JSON字符串 |

主要模块完全独立于A1代码。A1的完整精度数据仅复制为 `a1_reference.npz` 供核验，不用作第二问初值拼接。误差估计低于2e-5是数值检验，不是实验精度保证；没有内部药材实测数据，不提供虚构的R²或RMSE。

## 本次验收结论

- 空间二阶收敛、容差收紧、Radau对照、A1回归均通过。
- 温度/含水率估计数值误差约4.8061e-6℃、2.7500e-6 kg/kg。
- 工作簿453600个结果值与完整精度数据四位舍入逐格完全一致。
- 原题、附件及A1基准的SHA-256复核未变化。
- 图表6组和工作簿两张表的首尾区域均已查看；未进行Microsoft Excel原生程序的打开验证，已完成openpyxl实际读取和Artifact Tool渲染验证。
