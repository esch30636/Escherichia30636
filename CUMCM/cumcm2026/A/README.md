# A 题 · 药材烘干（CUMCM 2026）

本目录是 A 题的完整求解工程。模型推导、数值方法、验证与敏感性分析的详细内容见
**[成果汇总.md](成果汇总.md)**（论文素材主文档）；本 README 回答"有哪些文件、各在哪里、怎么复现"。

---

## 1. 目录结构

```
A/
├── README.md                     ← 本文件
├── 成果汇总.md                    ← 模型/方法/结果/验证/敏感性 详细文档
├── 文献库.md                      ← 443 条参考文献(10 类) + 引用位置对照 + DOI 核验记录
├── 文献核心模型汇总.md             ← 文献模型提炼: 六代谱系/数学形式/与本题关系 + 选型论证 + 组件映射表
├── *.py                          ← 全部求解与制图代码(见 §2)
├── 01/                           ← 问题1 独立解题包(IEEE 格式报告 + 代码 + 结果)
│   ├── problem1.md               IEEE 格式解题报告(模型/方法/结果/验证/结论)
│   ├── problem1.py               问题1 独立求解脚本(all / tables / verify)
│   ├── a_model.py, a_output.py   模型核心(与根目录版一致)
│   ├── result1.xlsx              问题1 结果(与 out/result1.xlsx 逐格一致)
│   ├── tables1.json + fig1_p1.png   表1/表2 原始值 + 剖面图
│   └── README.md                 本包说明与验证记录
├── 01-pic/                        ← 问题1 佐证图包(vivid-figures 原则)
│   ├── palette.py                全文统一配色(ColorBrewer/seaborn muted, 禁 jet)
│   ├── make_figs.py              7 张佐证图生成脚本(热力图/量级图/收敛图等)
│   ├── fig01~fig07*.png          Fig. 1/2/4-8 的 PNG(300 dpi)
│   └── README.md                 图索引(与 problem1.md 章节对应)
├── 02/                           ← 问题2 独立解题包(整个烘干过程: 预热平衡 + 恒温干燥)
│   ├── problem2.md               IEEE 格式解题报告(变物性/两阶段/自锁效应)
│   ├── problem2.py               问题2 独立求解脚本(all / diag / tables / verify)
│   ├── a_model.py, a_output.py   模型核心(与根目录版一致)
│   ├── result2.xlsx              问题2 结果(与 out/result2.xlsx 逐格一致)
│   ├── tables2.json + fig2_p2.png   表3/表4 原始值 + 剖面图
│   ├── compare_r2.py             与 out/ 逐格比对脚本
│   └── README.md                 本包说明与验证记录
├── 02-pic/                       ← 问题2 佐证图包(vivid-figures 原则)
│   ├── palette.py                全文统一配色(与 01-pic 同一模块)
│   ├── make_figs.py              8 张佐证图生成脚本(物性曲线/全流程自锁/收敛图等)
│   ├── fig01~fig08*.png          Fig. 1/2/4-9 的 PNG(300 dpi)
│   └── README.md                 图索引(与 problem2.md 章节对应)
├── 02-lit/                       ← 问题2 文献补全版对照(蒸发潜热汇项, 2026-09-11)
│   ├── README.md                 结论速览/模型写法/换算口径推导/验证/论文模板句
│   ├── p2_lit.py                 diag · hot · full · figs · verify 五模式
│   ├── a_model.py, a_output.py   模型(新增 latent= 选项; 默认与基线路径逐位一致)
│   ├── palette.py                与 01-pic/02-pic 同一配色模块
│   ├── p2_lit_hot.json/.npz      3 h 六变体结果(数值 + 时间历程)
│   ├── p2_lit_full.json/.npz     全流程四变体结果(干时 + 时间历程)
│   └── figs/fig01~fig07*.png     潜热量级/3 h 温度水分/全流程/干时/时空图(300 dpi)
├── 03/                           ← 问题3 独立解题包(烘干时间 + 表5)
│   ├── problem3.md               IEEE 格式解题报告(事件判据/三阶段/自锁/交叉校验)
│   ├── problem3.py               问题3 独立求解脚本(all / diag / tables / verify)
│   ├── a_model.py, a_output.py   模型核心(与根目录版一致)
│   ├── result3.xlsx              问题3 结果(与 out/result3.xlsx 逐格一致)
│   ├── tables3.json + fig3_p3.png   表5 原始值 + 表5 剖面/烘干曲线图
│   ├── compare_r3.py             与 out/ 逐格比对脚本
│   └── README.md                 本包说明与验证记录
├── 03-pic/                       ← 问题3 佐证图包(vivid-figures 原则)
│   ├── palette.py                全文统一配色(与 01-pic/02-pic 同一模块)
│   ├── make_figs.py              8 张佐证图生成脚本(判据前沿/自锁/交叉/收敛等)
│   ├── fig01~fig08*.png          Fig. 2-9 的 PNG(300 dpi)
│   └── README.md                 图索引(与 problem3.md 章节对应)
├── out/                          ← 默认交付集(支撑材料从这里打包, 共 ≈4.4 MB)
│   ├── result1.xlsx              ( 1800 行,   354 KB)  问题1  t=1..1800 s, 1 s 间隔
│   ├── result2.xlsx              (10800 行,  2.26 MB)  问题2  t=1..10800 s, 1 s 间隔
│   ├── result3.xlsx              ( 3431 行,   326 KB)  问题3  60 s 间隔, 至烘干结束
│   ├── result4.xlsx              ( 3049 行,   202 KB)  问题4  60 s 间隔, 至烘干结束
│   ├── result2_全流程_60s.xlsx    ( 3431 行,   519 KB)  问题2 全流程, 60 s 间隔(补充)
│   ├── tables.json               论文 表1~表6 的全部数值
│   ├── uq.json                   敏感性(OAT)/情景分析/蒙特卡洛 结果
│   ├── gan_env.pt                WGAN-GP 训练权重(§5.4)
│   ├── gan_scen.npz              200×3 条 61 h 情景轨迹(gan/boot/param)
│   ├── gan_uq.json + gan_fig.png 情景传播: 烘干时间分布 + 图(§5.4)
│   ├── summary.json              关键数字汇总
│   ├── drytime3.txt / drytime4.txt   烘干时间(s / h / 天)
│   └── fig/                      6 张论文插图(fig_boundary, fig1_p1, fig2_p2,
│                                    fig3_drying, fig_convergence, fig_tornado)
├── result2_full_1s/              ← 变体: result2 的第二种理解(§4.1), 不进默认交付集
│   └── result2.xlsx              (205862 行, 26.2 MB)  问题2 全流程, 1 s 间隔
└── _tools/                       ← 质检脚本(不进交付包)
    ├── doi_check.py              文献库 DOI 批量核验(Crossref 存在性+题名词重叠)
    └── doi_check_report.txt      核验报告(304 个 DOI: 273 通过 / 29 中文刊 DOI / 2 待复)
```

附件数据与竞赛给的 result 模板**只存放在 legion 的 `D:\CUMCM\A\data\`**，本地不存
（避免把官方数据混进支撑材料）。

## 2. 代码文件

| 文件 | 作用 | 产物 |
|---|---|---|
| `a_model.py` | 核心模型：ξ=r/R(t) 移动边界有限体积 (N=400) + BDF；支持参数乘子 `scales`、烘房偏移 `chamber_shift` 与自定义烘房时序 `chamber_series`（GAN 情景），敏感性/情景全部复用同一代码路径；`latent=` 选项按文献补全蒸发潜热汇项（vol/surf 两种写法，默认关闭时与基线逐位一致） | — |
| `a_ref.py` | 独立参考实现（物理 r 坐标），仅用于交叉验证 | — |
| `a_output.py` | 采样层（ξ 线性插值 + 表面值由边界条件反解）与流式 xlsx 写出 | — |
| `solve_a.py` | 主驱动：生成 result1~4.xlsx；含烘干时间求解与表头构造 | `out/result1-4.xlsx` |
| `solve_a_result2_full.py` | 变体驱动：按第二种理解生成 result2 全流程 (1 s) | `result2_full_1s/result2.xlsx` |
| `a_tables.py` | 生成论文 表1~表6 | `out/tables.json` |
| `a_extra.py` | 问题2 全流程 (60 s) 补充文件 + 关键数字 | `out/result2_全流程_60s.xlsx`, `out/summary.json` |
| `a_uq.py` | 敏感性分析（OAT + 情景 + 拉丁超立方 MC，18 进程并行） | `out/uq.json` |
| `a_gan.py` | §5.4：WGAN-GP 烘房偏差情景生成（train/gen）+ FVM 传播（prop，24 进程） | `out/gan_env.pt`, `out/gan_scen.npz`, `out/gan_uq.json`, `out/gan_fig.png` |
| `a_figs.py` | 论文插图 | `out/fig/*.png` |
| `a_validate.py` | 验证 1：RHS 恒等性（ξ 形式 vs r 形式，偏差 1e-14~1e-15） | — |
| `a_check2.py` | 验证 2：能量/水分守恒（残差 ~2e-9） | — |
| `a_check3.py` | 验证 3：网格收敛性（N=400 二阶收敛，4 位小数有保证） | — |
| `_tools/doi_check.py` | 文献库 DOI 批量核验（Crossref 存在性 + 题名关键词比对，6 线程） | `_tools/doi_check_report.txt` |

## 3. 关键结果速览

| 问题 | 烘干时间 | 判据 |
|---|---|---|
| 问题3（不考虑收缩） | **205862.4 s = 57.1840 h = 2.3827 天** | max C < 0.15 kg/kg |
| 问题4（考虑收缩） | **182974.1 s = 50.8261 h = 2.1178 天** | 收缩使 D/R² 增大，烘干加快 |

两者都落在题面"2–3 天"内，是独立自洽检验。

- 问题1（30 min）：中心 28→33.5753 °C，表面 28→36.7856 °C，水分只在表层下降（干壳湿芯）。
- 问题2（3 h，附录3 变物性）：表面 28→49.9664 °C、中心 28→49.8495 °C（径向温差 3.22→0.12 °C，
  趋于准稳态）；表面水分 2.55→1.0081、中心 2.55→1.7662（干燥锋约 1 h 推进到中心）。
- 问题3/4 交叉现象：问题4 前期更慢（附录4 D 前置因子小 5.4 倍）、后期更快（1/R² 放大 + 更弱的浓度依赖），约 41.0 h 处相交——细节见成果汇总.md §3。
- 敏感性结论：烘干时间几乎只由扩散系数 D 决定（弹性 −0.73/+1.11），传热参数可忽略（|S|<0.003）；
  **最大的不确定度是"恒温干燥阶段烘房维持末值"这一假设**（烘房 +5 °C → 烘干时间 −14.6%）。
- 蒙特卡洛（N=1000）：问题3 57.69±4.53 h（P05–P95: 51.1–65.2 h）。
- GAN 情景传播（§5.4，200 情景 × 3 生成器）：恒温阶段**随机波动**引起的干时分布
  std ≈ 0.01 h（0.6 min）、均值偏置 ≤ 0.11% —— 比参数不确定性小两个数量级以上；
  「维持末值」假设的真实风险是**系统性设定值偏移**（±5 °C 情景），随机波动可忽略。
- 文献补全版对照（`02-lit/`，§5 第 12 句）：按文献补上蒸发潜热汇项后，题目给的
  `h_m = 8×10⁻⁷ m/s` 比热质类比值小 3.07×10⁴ 倍、潜热流（503–847 W/m²）超过烘房最大可供给热流
  （554 W/m²），模型预测早期料温跌到 11–12 °C（实际受湿球温度约束不可能）——说明题面参数按
  「潜热并入有效参数」标定；但**干时仅 60.18–61.09 h（比基线 +5.2%~+6.8%）**，仍满足「2–3 天」，
  故基线简化对结论影响 ≤7%（已量化的模型局限）。

## 4. 两处输出约定（论文中需显式写明）

### 4.1 result2 的两种理解

题面"将每隔 1 s 的完整结果保存到 result2.xlsx"有两种读法，两种都做了：

| 理解 | 文件 | 依据 |
|---|---|---|
| **一（默认交付）**：作用域承接前一句"3 h 内" | `out/result2.xlsx`（10800 行） | 与问题1"1800 s 内"同构；1 s 间隔跑满 2–3 天 = 20.6 万行 = 26.2 MB，**加上其余支撑材料后超出 20 MB 上限** |
| **二（变体）**："完整结果"指整个烘干过程 | `result2_full_1s/result2.xlsx`（205862 行） | 同一模板、同一表头、同一精度，仅行数不同 |

打包支撑材料时**二选一**：默认用理解一；若采用理解二，把该文件移入交付集并注意体积。

### 4.2 result4 的固定距离列

取 0, 0.1, …, 1.1 cm + 末列"药材表面"。半径收缩到 R_min = 1.198 cm，只有 0~1.1 cm 的
0.1 cm 等距网格全程位于药材内部；模板把末列表头写成"药材表面"（而非数字 2），正说明
表面需要单独一列。问题1–3 的表面列头按模板为数值 2。

### 4.3 温度单位

模型内部一律用 K（附录3/4 的 `exp(-3850/T)` 要求 K），**写出文件时已转回 °C**。

## 5. 复现

运行在 legion（`D:\CUMCM\A`，conda 环境 `cumcm_a`，Python 3.11.16），依赖
numpy / scipy / openpyxl / matplotlib：

```powershell
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' 'D:\CUMCM\A\solve_a.py' all       # result1-4
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' 'D:\CUMCM\A\solve_a_result2_full.py'  # 理解二变体
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' 'D:\CUMCM\A\a_tables.py'
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' 'D:\CUMCM\A\a_uq.py'
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' 'D:\CUMCM\A\a_figs.py'
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' 'D:\CUMCM\A\a_gan.py' train       # GAN 训练(~100 s, CPU)
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' 'D:\CUMCM\A\a_gan.py' gen --n 200 # 情景生成 + 校验
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' 'D:\CUMCM\A\a_gan.py' prop --n 200  # FVM 传播(24 进程, ~47 min)
```

全部脚本以 `D:\CUMCM\A` 为工作目录运行（模板/附件在 `data\` 下）。
