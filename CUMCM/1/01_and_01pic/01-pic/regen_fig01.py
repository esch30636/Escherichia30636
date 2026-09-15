# -*- coding: utf-8 -*-
"""fig01_chamber 修复版重生成（fix: 汉字与图像重叠）。

原版问题:
  1) a.text(14500, ylim[0], '14400 s 后按末值维持\\n(问题2/3 假设)') 把两行字放在
     轴外右下角（x=14500 超出 0~14400 轴范围，第二行压到 x 轴标签），
     tight bbox 随之把画布撑大；
  2) ax[1] 图例 loc='center right' 压在水分浓度曲线上。

修复:
  - 图例移到空区（ax0: lower right，曲线在右侧是高位；ax1: upper left，曲线在左侧是低位）；
  - "预热平衡阶段" 标注放在 ax0 顶部安全区（ha='center', va='top'）；
  - "14400 s 后按末值维持" 改为单行、放在 ax1 右下空区（ha='right', va='bottom'），
    全部文字均在轴内，画布用 tight_layout 固定，不再出现轴外文字。

输出: 本目录 fig01_chamber.png 与 D:\\CUMCM\\fig01_chamber.png（论文用）。
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)                                # palette
sys.path.insert(0, os.path.join(HERE, '..', '01'))      # a_model

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import a_model as M
import palette as P

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

T_TABLE = [100, 300, 600, 900, 1200, 1500, 1800]


def main():
    t, T, C = M.load_chamber()
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8), sharex=True)
    for a in ax:
        a.axvspan(0, 1800, color=P.C_SHADE, alpha=.7, zorder=0)
        a.axvline(14400, color=P.C_REF, ls='--', lw=1)
        a.set_xlim(0, 14400)
        a.set_xlabel('时间 t / s')
        a.grid(alpha=.3)

    ax[0].plot(t, T - 273.15, color=P.BLUE, lw=1.8, label='烘房温度')
    ax[0].scatter(T_TABLE, np.interp(T_TABLE, t, T) - 273.15, s=18,
                  color=P.RED, zorder=5, label='表1/表2 时刻')
    ax[0].set_ylabel('烘房温度 $T_{air}$ / °C')
    ax[0].set_title('(a) 附件1 烘房温度')
    ax[0].legend(fontsize=8, loc='lower right')
    ax[0].text(900, 49.0, '预热平衡阶段\n(本问 30 min)', fontsize=9,
               ha='center', va='top')

    ax[1].plot(t, C, color=P.GREEN, lw=1.8, label='烘房水分浓度')
    ax[1].scatter(T_TABLE, np.interp(T_TABLE, t, C), s=18,
                  color=P.RED, zorder=5, label='表1/表2 时刻')
    ax[1].set_ylabel('烘房水分浓度 $C_{air}$ / (kg/kg)')
    ax[1].set_title('(b) 附件1 烘房水分浓度')
    ax[1].legend(fontsize=8, loc='upper left')
    ax[1].text(14000, 0.0212, '14400 s 后按末值维持(问题2/3 假设)', fontsize=7.5,
               ha='right', va='bottom')

    fig.tight_layout()
    for p in (os.path.join(HERE, 'fig01_chamber.png'),
              r'D:\CUMCM\fig01_chamber.png'):
        fig.savefig(p, dpi=300)
        print('saved', p, os.path.getsize(p) // 1024, 'KB')
    plt.close(fig)


if __name__ == '__main__':
    main()
