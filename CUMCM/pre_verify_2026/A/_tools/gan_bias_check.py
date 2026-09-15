# -*- coding: utf-8 -*-
"""诊断: gan_scen.npz 三条情景源的残余(偏差)均值 —— 判定 GAN 干时 -0.11% 偏移的来源。

若偏移源于"生成序列的残余均值偏置", 则应满足
    dt/t = -0.79 * (a/T^2) * <dT>,   a = 3850 K, T ~ 323 K
即 <dT> ~ +0.038 K 可解释 -0.11%; 而凸性整流(Jensen)的二阶量只有 1e-5 量级。
本脚本只读 npz, 不做任何求解。
"""
import numpy as np

z = np.load(r'D:\CUMCM\A\out\gan_scen.npz')
n_steps = int(z['n_steps'])
print(f'n_steps = {n_steps}  ({(n_steps - 1) * 60 / 3600:.1f} h @ 60 s)')
print(f'{"源":>5} {"<dT>/K":>10} {"<dC>":>12} {"逐条时均 dT 范围":>24} '
      f'{"逐条时均 dC 范围":>24}')
for k in ('gan', 'boot', 'param'):
    Y = z[k]
    T = Y[:, :, 0]
    C = Y[:, :, 1]
    tm, cm = T.mean(1), C.mean(1)
    print(f'{k:>5} {T.mean():+10.5f} {C.mean():+12.3e} '
          f'{tm.min():+11.5f}~{tm.max():+.5f}  {cm.min():+11.3e}~{cm.max():+.3e}')

# 灵敏度换算: dt/t = -0.79 * (3850/Tbar^2) * <dT>   (Tbar 取恒温段 323.3 K)
Tbar = 323.30
for k in ('gan', 'boot', 'param'):
    T = z[k][:, :, 0]
    print(f'{k:>5}: 预测 dt/t = {-0.79 * 3850.0 / Tbar ** 2 * T.mean() * 100:+.3f} %')
print('(实测干时偏移: gan -0.11%, boot -0.01%, param -0.00%)')
