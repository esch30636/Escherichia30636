# -*- coding: utf-8 -*-
"""全文统一学术配色(依 vivid-figures 原则)。

原则: 低饱和、高区分度; 颜色服务数据; 拒绝 jet 与 Excel 原生撞色。
色号直接复用成熟方案 —— ColorBrewer 与 seaborn muted 调色盘。
**所有论文图表一律 import 本模块取色, 全文配色保持统一。**

用法:
    import palette as P
    ax.plot(x, y, color=P.C_SURF, lw=2)          # 语义色
    ax.plot(x, y, color=P.SEQ_TIME[3])           # 时间序第 4 级
    ax.pcolormesh(..., cmap=P.HEAT_T)            # 温度热力图
"""
import numpy as np
import matplotlib
from matplotlib.colors import LinearSegmentedColormap

# --------------------------------------------------------------------------
# 1) seaborn "muted" 学术六色(低饱和类目/折线主色)
# --------------------------------------------------------------------------
MUTED = ['#4878CF', '#6ACC65', '#D65F5F', '#B47CC7', '#C4AD66', '#77BEDB']
BLUE, GREEN, RED, PURPLE, OLIVE, CYAN = MUTED

# 语义色(问题1 专有, 全文统一)
C_SURF = RED        # '#D65F5F'  表面(红)
C_CENTER = BLUE     # '#4878CF'  中心(蓝)
C_AIR = '#8C8C8C'   # 烘房条件(灰)
C_REF = '#333333'   # 参考线/理论(近黑)
C_THRESH = '#A33B3B'  # 阈值线(暗红)
C_SHADE = '#D9D9D9'   # 阶段阴影(浅灰)

# --------------------------------------------------------------------------
# 2) 时间序 7 级色带(100~1800 s):
#    viridis 均匀取样 + 与白色 25% 混合降饱和 -> 低饱和且感知均匀, 由浅到深=时间推进
# --------------------------------------------------------------------------
def _desat(rgb, w=0.25):
    """与白色按 w 混合降低饱和度。rgb: 色名/hex/元组。"""
    c = matplotlib.colors.to_rgb(rgb)
    return matplotlib.colors.to_hex(tuple(v * (1 - w) + w for v in c))


_VIRIDIS = matplotlib.colormaps['viridis']
SEQ_TIME = [_desat(_VIRIDIS(i / 6)) for i in range(7)]   # 7 级, 浅->深

# --------------------------------------------------------------------------
# 3) 热力图顺序色带(ColorBrewer 9 级):
#    HEAT_T  YlOrRd(温度语义)   HEAT_C  YlGnBu(水分/湿润语义)
# --------------------------------------------------------------------------
_YlOrRd = ['#ffffcc', '#ffeda0', '#fed976', '#feb24c', '#fd8d3c',
           '#fc4e2a', '#e31a1c', '#bd0026', '#800026']
_YlGnBu = ['#ffffd9', '#edf8b1', '#c7e9b4', '#7fcdbb', '#41b6c4',
           '#1d91c0', '#225ea8', '#253494', '#081d58']

HEAT_T = LinearSegmentedColormap.from_list('heat_t', _YlOrRd)
HEAT_C = LinearSegmentedColormap.from_list('heat_c', _YlGnBu)
