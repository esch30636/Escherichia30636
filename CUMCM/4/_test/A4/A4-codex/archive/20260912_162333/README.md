# A4-codex：考虑收缩的第四问建模包

先阅读 **建模报告.md**，其中给出烘干时长、表6、方程推导、机制对照、收敛与敏感性。**参考文献.md** 包含正式题录、链接和访问核验范围。

结果统一来自800单元、BDF、rtol=1e-11的tight800轨迹。连续临界时刻50.824283 h；首次严格达标整分钟为50小时50分钟（50.8333 h、183000 s），终点半径1.2 cm。含水率工程数值误差估计7.582e-6 kg/kg。

主工作簿为result4.xlsx，含3050条时间记录，表6另存表6.md。

| 内容 | 用途 |
|---|---|
| 建模报告.md、参考文献.md、表6.md | 中文模型、解释、文献、简表 |
| result4.xlsx | 60 s × 0.1 cm完整含水率表，末列是真实表面 |
| data/full_precision.npz | 温度、含水率、半径、最大值和平均值等完整精度数据 |
| data/*full_precision.csv、radius_by_time.csv | 实际距离输出及对应半径；域外留空 |
| data/table6.csv | 表6完整精度数值 |
| data/ambient.csv、radius.csv、source_sha256.json | 原始输入提取副本及来源哈希 |
| figures/ | 六组科学图，PNG与SVG；场分布图的色块栅格化，坐标文字仍为矢量 |
| verification/ | 12个算例、配置、数值与工作簿核验记录 |
| code/ | 求解、复算、报告和工作簿生成脚本 |

## 复算

本机科学环境为 `/opt/anaconda3/bin/python`。在任意工作目录执行：

```bash
OPENBLAS_NUM_THREADS=1 /opt/anaconda3/bin/python '/Users/wangxinlei/Desktop/Xinlei/HUST/数模/A4/A4-codex/code/run_all.py' --recompute
```

其他计算机安装requirements.txt后可用`python code/run_all.py --recompute`。保持本目录在A4/A4-codex，保留原题及codex/gpt前三问目录，以便提取输入和执行第三问回归。原A2目录真实名称为`A2 `，有尾随空格。

```bash
python code/run_all.py --math-only   # 数值、验证、报告、图像，不导出工作簿
python code/produce.py              # 根据已验证结果重新生成报告、数据与图像
python code/check_workbook.py       # 只读回查已经生成的工作簿
python code/solve.py --name rerun800 --n 800 --rtol 1e-11 --recompute
```

未加`--recompute`时，只有算例配置、core.py、solve.py、环境CSV、半径CSV的SHA-256全部匹配才复用缓存。改变模型时还须更新报告中的相应公式说明。每次复算只覆盖本目录内派生文件，不修改原题或其他方案。

Excel生成使用Codex捆绑Node和`@oai/artifact-tool`；run_all.py默认从本机Codex运行时定位，亦可通过A4_NODE、A4_NODE_MODULES指定。code/node_modules只是本机符号链接，迁移机器应重建链接。科学计算和CSV/NPZ使用不依赖Node包。

## 坐标和时间

- result4.xlsx：A列为秒；B—V列为到中心实际距离0—2 cm，每0.1 cm；W列为当时真实表面的含水率。超出药材范围的格子为空，不表示含水率为零。2 cm列在t>0时全部位于域外。
- NPZ/CSV含t=0，Excel从60 s开始。主终点为首次全场严格低于0.15的整分钟，按未舍入值判断，不能凭Excel显示0.1500判断未达标。
- NPZ的T、C共22列，末列为表面；T_xi、C_xi为101个无量纲ξ坐标点，不是实际0.1 cm距离网格。内部x也是ξ，v为∫ξdξ。
- 题给ρ(C)用于有效热容，干物质守恒辅助密度ρ_d随R⁻²变化，两者不能混同。模型仍采用前问的显热、有效气固平衡及后续恒定环境假设。

## 验证边界

收敛估计、BDF/Radau、第三问退化回归、独立选定状态算子复核、均匀无交换收缩测试、通量收支及Excel逐格回读均为计算核验。没有内部药材实测数据，不宣称实验预测误差已验证。工作簿经Artifact Tool渲染及openpyxl重新打开检查，未在原生Microsoft Excel中启动验证。
