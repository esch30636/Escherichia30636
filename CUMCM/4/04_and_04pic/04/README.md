# 04：数值计算与核验

当前与A3-codex(1)组合时保留独立实现与原主结果，不调用对方的联合生成入口。固定半径主结果57.169383 h、205860 s；本目录收缩主结果50.8242826 h、183000 s。模型关系及版本界限见problem4.md开头。潜热仅为收缩工况扩展，不替代显热主结果。图03使用本目录固定半径对照，不是A3-codex(1)的3200单元主轨迹。本次衔接不修改数值源码、结果数据或图片；重新生成文档可能覆盖人工衔接说明，发布前须再次核对这些口径。

当前修订：audit-fix-20260912。主模型及对照共25个情景已重算。
结果见 [汇总.md](汇总.md)，论文说明见 [problem4.md](problem4.md)。

## 运行

本目录需要含 numpy、scipy、numba、pandas、openpyxl、matplotlib、Pillow 的 Python。

    python a4_sweep.py audit --nproc 4
    python a4_output.py --plots-only
    python a4_verify.py

也可运行 run_all.bat；用 A4_PYTHON 指定 Python 可执行文件。任一步失败立即退出。
默认保留已验证工作簿。需要重新导出时使用 python a4_output.py，会覆盖两个同名工作簿。

输入优先从 A4_DATA_DIR 读取 attach1_chamber_temp_moisture.xlsx 和 attach2_radius_vs_time.xlsx。
未设置时使用源代码内本机原数据目录及原竞赛资料后备路径。跨机器运行请配置 A4_DATA_DIR。

## 输出与口径

- result4.xlsx：末值环境、800单元、60 s采样，末行183000 s。
- result4_50度设定值.xlsx：50°C与湿度末值、800单元，末行183960 s。
- out/：状态、采样场及元数据。当前图表只读取本次revision的指定结果。
- ../04-pic/：六张300 dpi图，两张干燥图读取不同情景。
- table6.csv、tables4.json、fig4_p4.png：六小时及终点采样数据与图。
- sec44_guosai.tex：论文小节片段，需中文支持、amsmath、graphicx、booktabs，不是独立文档。
- verification.json：运行 a4_verify.py 生成的自动核验报告。

连续临界时间不等于首个严格整分钟。四位小数显示0.1500不意味着未达标。
主方案终点半径1.2000 cm，不是72 h观测末值1.198 cm。

## 修复及限制

修复全局采样、潜热表面重构、事件后实际积分、情景混用、共同参考收敛图及动态六小时输出。
平滑变体采用边缘延拓，避免零填充造成末端温度人为下降；该变体未纳入本次25情景结论。
旧dry/bulk密度变体已禁用，保留历史文件但不用于当前图文。
没有本次revision的历史输出、日志和审计笔记只供追溯。

不含潜热是基准假设，含潜热是替代模型，单位系数试验不是物理标定。
不再宣称潜热已被参数吸收、四位小数完全收敛或离散残差证明完整物理守恒。
截图来源未确认，前两问温度尚未独立复算。

修改前完整备份：D:\trash\Temp\04_and_04pic_before_fix_20260912.zip。
