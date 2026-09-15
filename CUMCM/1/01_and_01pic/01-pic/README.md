# 01-pic · 问题 1 佐证图包(IEEE 报告配套科研图)

按 **vivid-figures** 原则生成:低饱和、高区分度;配色复用成熟方案(ColorBrewer / seaborn
muted 学术色号),**全文图表配色统一**(所有图从 `palette.py` 取色),禁 jet 与 Excel 原生
撞色;选型跳出老三样(时空热力图、对数量级图、对数收敛图)。300 dpi,IEEE 双栏宽度。

## 配色模块 `palette.py`(全文唯一取色入口)

| 套系 | 来源 | 用途 |
|---|---|---|
| `MUTED` 六色 + 语义色 `C_SURF/C_CENTER/C_AIR/...` | seaborn "muted" | 折线/散点/类目 |
| `SEQ_TIME`(7 级) | viridis 均匀取样 + 与白色 25% 混合降饱和 | 时间序着色(浅→深 = 时间推进) |
| `HEAT_T` / `HEAT_C` | ColorBrewer YlOrRd / YlGnBu(9 级) | 温度 / 水分热力图 |

## 图索引(与 problem1.md 章节对应)

| 文件 | 内容 | 佐证 |
|---|---|---|
| `fig01_chamber.png` | 附件1 烘房温度/水分浓度,30 min 预热窗口阴影 + 表时刻标记 | §III.D 表 III |
| `fig02_temp_map.png` | 温度场时空热力图(30 min × 0–2 cm) | §V.B |
| `fig03_moist_map.png` | 水分浓度时空热力图(干壳/湿芯标注) | §V.B / V.C(2) |
| `fig04_timeseries.png` | 表面/中心 vs 烘房 时间曲线(7 表时刻标记,终值标注) | §V.C |
| `fig05_timescale.png` | 特征时间量级对比(30 min / τ_T / τ_C, 对数轴) | §III.E 先验分析 |
| `fig06_convergence.png` | 网格收敛 log-log(二阶参考 + 4 位小数阈值线) | §V.D 表 VI |
| `fig07_conservation.png` | 水分质量守恒: 域积分 vs 边界通量积分 + 残差 | §V.D 表 VI |

## 运行(legion,conda 环境 cumcm_a)

```powershell
Set-Location D:\CUMCM\A\01-pic
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' make_figs.py            # 全部 7 张
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' make_figs.py fig03 fig06  # 指定
```

模型复用 A 根目录的 `a_model.py` / `a_output.py`(经 sys.path 引用,不拷贝,避免版本分叉);
数据在 `D:\CUMCM\A\data`。fig06 需重解 N=100/200/400/800 四个网格、fig07 需 1 s 细采样,
全套图约 30–60 s。

## 一致性说明

- 本包图中全部数值(表时刻、终值、收敛误差、守恒残差)与 `01/tables1.json`、
  `01/result1.xlsx` 及 `01/problem1.md` 表 IV–VI 一致,由同一模型同一精度求解;
- 论文中其他问题(2/3/4)的插图应继续从 `palette.py` 取色,保持全文配色统一。
