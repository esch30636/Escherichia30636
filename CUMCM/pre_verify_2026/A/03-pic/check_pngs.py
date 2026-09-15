# -*- coding: utf-8 -*-
"""03-pic PNG 抽检工具: 尺寸 + 灰度极差检查(排除空白图)。"""
import glob
from PIL import Image
for f in sorted(glob.glob(r'D:\CUMCM\A\03-pic\*.png')):
    im = Image.open(f).convert('L')
    lo, hi = im.getextrema()
    print(f'{f.split(chr(92))[-1]:26s} {im.size[0]}x{im.size[1]}  灰度范围 {lo}-{hi} '
          f'{"OK" if hi - lo > 30 else "疑似空白!"}')
