# -*- coding: utf-8 -*-
"""01-pic PNG 完整性抽检: 尺寸 + 像素亮度极差(排除空白图)。"""
import glob
from PIL import Image
for f in sorted(glob.glob(r'D:\CUMCM\A\01-pic\*.png')):
    im = Image.open(f).convert('L')
    lo, hi = im.getextrema()
    print(f'{f.split(chr(92))[-1]:26s} {im.size[0]}x{im.size[1]}  亮度范围 {lo}-{hi} '
          f'{"OK" if hi - lo > 30 else "疑似空白!"}')
