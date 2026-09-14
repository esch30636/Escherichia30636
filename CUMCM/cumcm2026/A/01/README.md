# 01 · 问题 1 解题包(预热平衡阶段)

本目录是 **问题 1** 的完整解题包:IEEE 格式解题报告 + 独立求解代码 + 已验证结果。

- 解题报告(IEEE 格式:摘要 / 问题重述 / 假设与符号 / 数学模型 / 数值方法 / 结果 / 结论 / 参考文献):**`problem1.md`**
- 代码:`problem1.py`(问题 1 驱动)、`a_model.py` + `a_output.py`(核心模型与输出层,与 A 根目录验证版一致,2026-09-11 拷贝)
- 结果:`result1.xlsx`(1800 行 × 2 工作表)、`tables1.json`(表 1/表 2 原始值)、`fig1_p1.png`(剖面图)

## 运行(legion,conda 环境 cumcm_a)

```powershell
Set-Location D:\CUMCM\A\01
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' problem1.py          # 全流程: 诊断 -> 表1/表2 -> result1.xlsx -> fig1_p1.png
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' problem1.py tables   # 仅打印表1/表2(读 tables1.json)
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' problem1.py verify   # 问题1 专属验证: 质量守恒 + 网格收敛
& 'D:\Applications\Anaconda3\envs\cumcm_a\python.exe' compare_r1.py        # 与 out/ 已验证产物逐格比对
```

附件 1 与 result1.xlsx 模板**不在本目录**(在 `D:\CUMCM\A\data`,避免官方数据混入交付物)。

**配套佐证图包**:`../01-pic/`(vivid-figures 原则生成,Fig. 1/2/4–8,配色全文统一,见其 README)。

## 验证记录(2026-09-11,legion)

- **产物一致性**:`01\result1.xlsx` 与 `A\out\result1.xlsx`(已验证交付版)逐格比对,温度/水分浓度两工作表各 1800 行,**零差异**;表 1/表 2 与 `out\tables.json` 最大绝对差 0。
- **质量守恒**:相对残差 9.7×10⁻⁸(1 s 细网格通量积分)。
- **网格收敛**:N = 100/200/400/800,收敛阶 1.99;N=400 表面 C 误差 2.6×10⁻⁶、中心 T 误差 3.6×10⁻⁵,均小于 4 位小数阈值 5×10⁻⁵。

## 关键结论(30 min)

| 量 | 值 |
|---|---|
| 表面温度 | 28 → **36.7856 °C**(+8.79) |
| 中心温度 | 28 → **33.5753 °C**(+5.58) |
| 表面水分 | 2.55 → **1.5102 kg/kg**(−40.8%) |
| 中心水分 | 2.5500(不变) |

预热平衡阶段呈**干壳湿芯**:热特征时间 τ_T ≈ 39.5 min 与 30 min 考察窗同量级(温度场正在建立、表面仍比烘房低 4.73 °C),水分特征时间 τ_C ≈ 22.5 h(水分仅表面 0.5 cm 薄层下降)。
