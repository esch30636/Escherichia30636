# -*- coding: utf-8 -*-
"""独立参考实现: 物理坐标 r 上的单元中心有限体积。
仅用于与 a_model 的 xi 形式做交叉验证 —— 两者应给出同一离散结果。"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import diags
import a_model as M

R0, H, HC, HM = M.R0, M.H_CYL, M.H_CONV, M.HM


class RefPhysical:
    def __init__(self, N=200, problem=1):
        self.N = N
        self.dr = R0 / N
        self.rf = np.arange(N + 1) * self.dr
        self.rc = (np.arange(N) + 0.5) * self.dr
        self.V = np.pi * (self.rf[1:] ** 2 - self.rf[:-1] ** 2) * H
        self.A = 2 * np.pi * self.rf * H
        self.A[0] = 0.0
        self.t_ch, self.T_ch, self.C_ch = M.load_chamber()
        self.props = {1: M.props_p1, 2: M.props_p3,
                      3: M.props_p3, 4: M.props_p4}[problem]
        self.Dfun = {1: M.D_p1, 2: M.D_p3, 3: M.D_p3, 4: M.D_p4}[problem]

    def rhs(self, t, y):
        N, dr = self.N, self.dr
        T, C = y[0::2], y[1::2]
        rho, cp, k = self.props(C)
        D = self.Dfun(C, T)
        Ta = float(np.interp(t, self.t_ch, self.T_ch))
        Ca = float(np.interp(t, self.t_ch, self.C_ch))
        Te = np.concatenate([[T[0]], T, [Ta]])
        Ce = np.concatenate([[C[0]], C, [Ca]])
        Gt = np.zeros(N + 1); Gm = np.zeros(N + 1)
        Gt[1:N] = M.harm(k[:-1], k[1:]) * self.A[1:N] / dr
        Gm[1:N] = M.harm(D[:-1], D[1:]) * self.A[1:N] / dr
        # 与 a_model 保持一致: 半单元导热热阻用精确积分 ∫_{r_c}^{R0} dr/(2*pi*r*H*k)
        Gt[N] = self.A[N] / (R0 * np.log(R0 / self.rc[-1]) / k[-1] + 1 / HC)
        Gm[N] = self.A[N] / (R0 * np.log(R0 / self.rc[-1]) / D[-1] + 1 / HM)
        fT = Gt * (Te[:-1] - Te[1:])
        fC = Gm * (Ce[:-1] - Ce[1:])
        dT = (fT[:-1] - fT[1:]) / (rho * cp * self.V)
        dC = (fC[:-1] - fC[1:]) / self.V
        out = np.empty(2 * N); out[0::2] = dT; out[1::2] = dC
        return out

    def solve(self, t_end, rtol=1e-9, atol=1e-11):
        y0 = np.empty(2 * self.N)
        y0[0::2] = M.T_INIT + 273.15
        y0[1::2] = M.C_INIT
        n = 2 * self.N
        offs = (-3, -2, -1, 0, 1, 2, 3)
        sp = diags([np.ones(n - abs(o)) for o in offs], list(offs),
                   shape=(n, n), format='csr')
        return solve_ivp(self.rhs, (0, t_end), y0, method='BDF', rtol=rtol,
                         atol=atol, jac_sparsity=sp, dense_output=True)
