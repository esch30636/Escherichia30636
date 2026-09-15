# 02-pic · 问题 2 佐证图包(IEEE 报告配套科研图)

按 **vivid-figures** 原则生成:低饱和、高区分度;配色复用成熟方案(ColorBrewer / seaborn
muted 学术色号),**全文图表配色统一**(所有图从 `palette.py` 取色),禁 jet 与 Excel 原生
撞色;选型跳出老三样(时空热力图、对数量级图、对数收敛图)。300 dpi,IEEE 双栏宽度。

## 配色模块 `palette.py`(全文唯一取色入口,与 01-pic 同一模块)

| 套系 | 来源 | 用途 |
|---|---|---|
| `MUTED` 六色 + 语义色 `C_SURF/C_CENTER/C_AIR/...` | seaborn "muted" | 折线/散点/类目 |
| `SEQ_TIME`(7 级) | viridis 均匀取样 + 与白色 25% 混合降饱和 | 时间序着色(浅→深 = 时间推进) |
| `HEAT_T` / `HEAT_C` | ColorBrewer YlOrRd / YlGnBu(9 级) | 温度 / 水分热力图 |

## 图索引(与 problem2.md 章节对应)

| 文件 | 内容 | 佐证 |
|---|---|---|
| `fig01_chamber.png` | 附件1 烘房条件与两阶段结构(预热平衡/恒温干燥阴影、3 h 窗口、维持末值虚线) | §III.D 表 III |
| `fig02_temp_map.png` | 温度场时空热力图(3 h × 0–2 cm) | §V.B |
| `fig03_moist_map.png` | 水分浓度时空热力图(干壳/湿芯标注) | §V.B |
| `fig04_params.png` | 附录3 物性:归一化 ρ/c_p/k 随 C 变化 + D(C,T) 三温度衰减(双对数) | §III.B 表 II |
| `fig05_timeseries.png` | 表面/中心 vs 烘房 时间曲线(6 表时刻标记,终值标注) | §V.C |
| `fig06_drying.png` | 全流程(60 h)水分浓度 + 0.15 判据(57.1840 h)+ 有效扩散系数自锁衰减 | §V.C(4) |
| `fig07_convergence.png` | 网格收敛 log-log(二阶参考 + 4 位小数阈值线) | §V.D 表 VI |
| `fig08_conservation.png` | 水分质量守恒:域积分 vs 边界通量积分 + 残差 | §V.D 表 VI |

## 运行(legion,conda 环境 cumcm_a)

```powershell
Set-Location D:\CUMCM\A\02-pic
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' make_figs.py             # 全部 8 张
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' make_figs.py fig03 fig06  # 指定
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' check_pngs.py            # PNG 抽检(尺寸 + 灰度极差)
```

模型复用 A 根目录(legion 在 `A\src\`)的 `a_model.py` / `a_output.py`(经 sys.path 引用,
不拷贝,避免版本分叉);数据在 `D:\CUMCM\A\data`。fig06 需全流程(60 h)求解、fig07 需重解
N=100/200/400/800 四个网格、fig08 需 1 s 细采样,全套约 3–6 min。

## 一致性说明

- 本包图中全部数值(表时刻、终值、收敛误差、守恒残差、烘干时间 57.1840 h)与
  `02/tables2.json`、`02/result2.xlsx` 及 `02/problem2.md` 表 IV–VI 一致,由同一模型同一精度求解;
- fig06(a) 的烘干完成时刻 57.1840 h(2.3827 天)由**问题 3** 正式求解(见 `out/drytime3.txt`),
  此处用于展示模型覆盖全流程、引出"自锁效应";
- 论文中其他问题(3/4)的插图继续从 `palette.py` 取色,保持全文配色统一。
