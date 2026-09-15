# 02 · 问题 2 解题包(整个烘干过程:预热平衡 + 恒温干燥)

本目录是 **问题 2** 的完整解题包:IEEE 格式解题报告 + 独立求解代码 + 已验证结果。

- 解题报告(IEEE 格式:摘要 / 问题重述 / 假设与符号 / 数学模型 / 数值方法 / 结果 / 结论 / 参考文献):**`problem2.md`**
- 代码:`problem2.py`(问题 2 驱动,四模式 `all`/`diag`/`tables`/`verify`)、`a_model.py` + `a_output.py`(核心模型与输出层,与 A 根目录验证版一致,2026-09-11 拷贝)
- 结果:`result2.xlsx`(10800 行 × 2 工作表)、`tables2.json`(表 3/表 4 原始值)、`fig2_p2.png`(剖面图)
- 校验:`compare_r2.py`(与 `out/` 已验证产物逐格比对)

## 运行(legion,conda 环境 cumcm_a)

```powershell
Set-Location D:\CUMCM\A\02
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' problem2.py          # 全流程: 诊断 -> 表3/表4 -> result2.xlsx -> fig2_p2.png
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' problem2.py diag     # 仅量级诊断(附录3 物性 + 附件1 两阶段结构)
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' problem2.py tables   # 仅打印表3/表4(读 tables2.json)
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' problem2.py verify   # 问题2 专属验证: 质量守恒 + 网格收敛
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' compare_r2.py        # 与 out/ 已验证产物逐格比对
```

附件 1 与 result2.xlsx 模板**不在本目录**(在 `D:\CUMCM\A\data`,避免官方数据混入交付物)。

**配套佐证图包**:`../02-pic/`(vivid-figures 原则生成,8 张,配色全文统一,见其 README)。

## 验证记录(2026-09-11,legion)

- **产物一致性**:`02\result2.xlsx` 与 `A\out\result2.xlsx`(已验证交付版)逐格比对,温度/水分浓度两工作表各 10800 行,**零差异**(逐格不同行 0、最大数值差 0);表 3/表 4 与 `out\tables.json` 最大绝对差 0。
- **质量守恒**:相对残差 1.051×10⁻⁷(1 s 细网格通量积分)。
- **网格收敛**:N = 100/200/400/800,收敛阶 ≈ 2.09(100→400 段);N=400 表面 C 误差 7.3×10⁻⁸、中心 T 误差 9.6×10⁻⁶,分别为 4 位小数阈值 5×10⁻⁵ 的 0.1% 与 19%(上界)。
- **积分成本**:3 h 积分 2515 步、1.8 s(N=400);result2.xlsx 写出 10.7 s。

## 关键结论(3 h)

| 量 | 值 |
|---|---|
| 表面温度 | 28 → **49.9664 °C**(径向温差 3.22 → 0.12 °C,趋于准稳态) |
| 中心温度 | 28 → **49.8495 °C** |
| 表面水分 | 2.55 → **1.0081 kg/kg**(−60.5%) |
| 中心水分 | 2.55 → **1.7662 kg/kg**(−30.7%) |

附录 3 物性:ρ = 650+128C、c_p = 1450+2736C/(C+1)、k = 0.21+0.38C/(C+1)、D = 2.4×10⁻³e^(−0.45/C)e^(−3850/T)。热特征时间 τ_T = 46.0 min,水分基模时间常数 τ_1 ≈ 3.4 h(与 3 h 考察窗同量级:干燥锋约 1 h 推进到中心);C → 0.15 时 D 衰减 16.8 倍(**自锁效应**,后期松弛时间常数增至约 24 h)。全流程烘干 **57.1840 h = 2.3827 天**(问题 3 正式求解),与题面"2–3 天"一致。

**result2.xlsx 两种理解**:默认交付 3 h 版(本目录,与问题 1"1800 s 内"同构);全流程 1 s 变体在 `../result2_full_1s/result2.xlsx`(26.2 MB),全流程 60 s 版在 `../out/result2_全流程_60s.xlsx`——打包支撑材料时与默认版二选一。
