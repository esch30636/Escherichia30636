# 03-pic · 问题 3 佐证图包(IEEE 报告配套科研图)

按 **vivid-figures** 原则生成:低饱和、高区分度;配色复用成熟方案(ColorBrewer / seaborn
muted 学术色号),**全文图表配色统一**(所有图从 `palette.py` 取色),禁 jet 与 Excel 原生
撞色;选型跳出老三样(全流程时空热力图 + 判据前沿等值线、自锁效应量级图、烘干时间
对数收敛图、干燥速率三阶段图)。300 dpi,IEEE 双栏宽度。

## 配色模块 `palette.py`(全文唯一取色入口,与 01-pic/02-pic 同一模块)

| 套系 | 来源 | 用途 |
|---|---|---|
| `MUTED` 六色 + 语义色 `C_SURF/C_CENTER/C_AIR/...` | seaborn "muted" | 折线/散点/类目 |
| `SEQ_TIME`(7 级) | viridis 均匀取样 + 与白色 25% 混合降饱和 | 时间序着色 |
| `HEAT_T` / `HEAT_C` | ColorBrewer YlOrRd / YlGnBu(9 级) | 温度 / 水分热力图 |

## 图索引(与 problem3.md 章节对应)

| 文件 | 内容 | 佐证 |
|---|---|---|
| `fig01_chamber.png` | 附件1 烘房条件全流程视角(预热/恒温/外推三段阴影、维持末值虚线、表5 时刻、烘干结束线) | §III.D |
| `fig02_moist_map.png` | 全流程水分时空热力图(57.2 h × 0–2 cm)+ 判据前沿 C=0.15 等值线(干壳/湿芯标注) | §V.C |
| `fig03_drying_curve.png` | (a) 温度前 6 h 瞬态(准稳态) (b) 表面/中心水分全流程 + 判据 + 表5 时刻 | §V.C |
| `fig04_selflock.png` | 自锁效应量化:(a) D_eff 升温加速→衰减 (b) τ₁(t) 3.41 h→约 24 h | §V.C |
| `fig05_cross_p4.png` | 交叉校验: 问题3 vs 问题4 中心水分(约 41.0 h 交叉,两问干时标注) | §V.D |
| `fig06_convergence.png` | 烘干时间网格收敛 log-log(二阶参考 + Richardson 基准 + 观测阶说明) | §V.F 表 III |
| `fig07_conservation.png` | 水分质量守恒(全流程): 域积分 vs 边界通量积分 + 残差 | §V.F 表 III |
| `fig08_dryingrate.png` | 平均含水率 + 干燥速率三阶段(预热加速 / 恒温降速 / 末段自锁) | §V.C |

## 运行(legion,conda 环境 cumcm_a)

```powershell
Set-Location D:\CUMCM\A\03-pic
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' make_figs.py             # 全部 8 张
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' make_figs.py fig03 fig05  # 指定
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' check_pngs.py            # PNG 抽检(尺寸 + 灰度极差)
```

模型复用 A 根目录(legion 在 `A\src\`)的 `a_model.py` / `a_output.py`(经 sys.path 引用,
不拷贝,避免版本分叉);数据在 `D:\CUMCM\A\data`。fig02/03/04/07/08 各需一次全流程求解,
fig05 需问题3+问题4 各一次,fig06 需重解 N=100/200/400/800 四个网格,全套约 3–6 min。

## 一致性说明

- 本包图中全部数值(烘干时间 57.1840 h、表 5 时刻、交叉 41.0 h、Richardson 极限
  57.1703 h、N=400 误差 49.3 s、守恒残差、D_eff/τ₁ 演化)与 `03/tables3.json`、
  `03/result3.xlsx` 及 `03/problem3.md` 表 II–III 一致,由同一模型同一精度求解;
- fig05 的问题 4 曲线用于交叉校验,其烘干时间 50.8261 h 由同一事件判据求解
  (问题 4 的正式解题包见 04/);
- 论文中其他问题的插图继续从 `palette.py` 取色,保持全文配色统一。
