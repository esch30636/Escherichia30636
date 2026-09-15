# A3-codex：统一高精度建模交付

先阅读 **建模报告.md**；与另一问的协调修订见 **联合修订说明.md**。题定文件为 **result3.xlsx**，简表为 **表5.md**。

- 连续临界时刻：57.169383 h（最大含水率恰等于0.15）。
- 首次严格达标整分钟：57小时11分钟，57.1833 h、205860 s。
- 主网格3200单元，独立Radau解6400个区间。
- 工程数值误差估计：含水率2.138e-07 kg/kg，临界时间0.059491 s；均通过新目标。

潜热仅留在后续模型改进的文字讨论，本轮没有潜热算例。4 h后环境固定为末值，采用显热、有效气固平衡及径向近似；数值误差不代表实验预测精度。

## 文件与接口

| 文件 | 内容 |
|---|---|
| 建模报告.md、联合修订说明.md | 完整推导、时长、精度和新旧差异 |
| result3.xlsx、表5.md | 每60 s、每0.1 cm及每6 h简表 |
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
OPENBLAS_NUM_THREADS=1 /opt/anaconda3/bin/python '/Users/wangxinlei/Desktop/Xinlei/HUST/数模/A3/A3-codex/code/run_all.py' --recompute
```

其他计算机使用安装了requirements.txt依赖的Python；保持目录相对位置。完整严格复算包含细网格和独立求解，可能需要较长时间。只计算与生成报告、不导出Excel：

```bash
python code/run_all.py --math-only
python code/verify.py
python code/produce.py
python code/check_workbook.py
```

未加--recompute时，仅当全部数学源码、输入和配置哈希一致才复用缓存；更新源码后失效的旧算例会重算，不伪造新的来源哈希。单独produce只根据已通过验收的summary整理该问，不自动重算物理模型。

Excel由Codex捆绑Node及@oai/artifact-tool生成；A3_NODE、A3_NODE_MODULES可覆盖工具位置。code/node_modules是本机依赖链接，迁移时重建。openpyxl仅用于读取检查，未启动原生Excel应用。

## 验证边界

误差在每分钟全部题定有效距离、真实表面及1001个材料坐标点上比较，并检查全单元最大值与径向次序；它是有限验证网格上的工程误差估计，不是连续场严格上界。最后一次空间加密按观测二阶阶数估计细网格余项，时间、求积和独立方法差保留原值，取最大分量并避免重复计数。敏感性情景采用400单元，与同网格基准比较，不作为高精度主解的误差证据。首次达标根据未舍入结果，不能用Excel显示0.1500作判据。

上一版 6astra 报告和 README 已原样保存在 **建模报告_6astra原稿.md**、**README_6astra原稿.md** 及 **archive/** 中。
