# -*- coding: utf-8 -*-
"""A 题 药材烘干 —— 轴对称热-湿耦合有限体积模型, xi = r/R(t) 曲线坐标。

控制方程 (柱坐标, 轴对称, 仅径向):
    rho*cp * dT/dt = (1/r) d/dr ( k r dT/dr )
    dC/dt          = (1/r) d/dr ( D r dC/dr )

令 xi = r/R(t) 并假设**均匀(仿射)收缩**——每个材料点固定在自身 xi 上, 则

    dT/dt = 1/(rho*cp*R^2*xi) * d/dxi ( xi*k*dT/dxi )
    dC/dt = 1/(R^2*xi)        * d/dxi ( xi*D*dC/dxi )

推导要点: 干物质守恒给出 rho_d*R^2 = const, 代入守恒律后 rho_d 完全约去,
故 C 方程不含物性密度; 收缩的全部影响体现为有效扩散系数 D/R(t)^2 随 R 减小而增大。
仿射收缩下材料相对 xi 静止 -> **无对流项**。

边界条件:
    xi=0 : 对称   flux = 0
    xi=1 : -k/R  dT/dxi = h  (T_s - T_air)
           -D/R  dC/dxi = hm (C_s - C_air)

有限体积离散 (单元 i 覆盖 [xi_i, xi_{i+1}], 面 f 在 xi_f = f/N):
    Phi_f = G_f (u_{f-1} - u_f),   f = 1..N,   Phi_0 = 0
    G_f   = xi_f * D_f / dxi                       (内部面, D_f 取调和平均)
    G_N   = 1 / [ (dxi/2)/(xi_c*k_{N-1}) + 1/(h*R) ]   (半单元导热 + 对流)
    du_i/dt = (Phi_i - Phi_{i+1}) / (rho*cp*R^2*xi_c[i]*dxi)
"""
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from scipy.sparse import diags

DATA_DIR = r'D:\CUMCM\A\data'

H_CYL = 0.25        # 药材长度 (m)
R0 = 0.02           # 初始半径 (m)
T_INIT = 28.0       # 初始温度 (degC)
C_INIT = 2.55       # 初始干基含水率 (kg/kg)
H_CONV = 25.0       # 对流换热系数 W/(m^2 K)
HM = 8.0e-7         # 对流传质系数 m/s
T_END_STD = 259200.0  # 3 天


# --------------------------------------------------------------------------
# 数据加载
# --------------------------------------------------------------------------
def load_chamber(hold='final'):
    """附件1: 烘房温度(degC)与水分浓度(kg/kg)。hold='final' 表示超过 14400 s 后保持末值。"""
    a = pd.read_excel(rf'{DATA_DIR}\attach1_chamber_temp_moisture.xlsx', header=0)
    t = a.iloc[:, 0].to_numpy(float)
    T = a.iloc[:, 1].to_numpy(float) + 273.15
    C = a.iloc[:, 2].to_numpy(float)
    if hold == 'final':
        return t, T, C
    raise ValueError(hold)


def load_radius():
    """附件2: 半径(cm)随时间(s)。返回 (t_s, R_m)。"""
    a = pd.read_excel(rf'{DATA_DIR}\attach2_radius_vs_time.xlsx', header=0)
    t = a.iloc[:, 0].to_numpy(float)
    R = a.iloc[:, 1].to_numpy(float) * 1e-2      # cm -> m
    return t, R


# --------------------------------------------------------------------------
# 物性 / 扩散系数
# --------------------------------------------------------------------------
def props_p1(C):
    """附录2 (问题1): 常数物性"""
    C = np.asarray(C, float)
    return (np.full_like(C, 820.0), np.full_like(C, 2600.0), np.full_like(C, 0.36))


def props_p3(C):
    """附录3 (问题2/3)"""
    C = np.clip(np.asarray(C, float), 1e-12, None)
    rho = 650.0 + 128.0 * C
    cp = 1450.0 + 2736.0 * C / (C + 1.0)
    k = 0.21 + 0.38 * C / (C + 1.0)
    return rho, cp, k


def props_p4(C):
    """附录4 (问题4)"""
    C = np.clip(np.asarray(C, float), 1e-12, None)
    rho = 760.0 + 90.0 * C
    cp = 1850.0 + 2150.0 * C / (C + 1.0)
    k = 0.12 + 0.20 * C / (C + 1.0)
    return rho, cp, k


def D_p1(C, T):
    """附录2: D = 7e-9 exp(-0.89/C)  [m^2/s]"""
    C = np.clip(np.asarray(C, float), 1e-8, None)
    return 7.0e-9 * np.exp(-0.89 / C)


def D_p3(C, T):
    """附录3: D = 2.4e-3 exp(-0.45/C) exp(-3850/T)  [m^2/s]"""
    C = np.clip(np.asarray(C, float), 1e-9, None)
    return 2.4e-3 * np.exp(-0.45 / C) * np.exp(-3850.0 / np.asarray(T, float))


def D_p4(C, T):
    """附录4: D = 4.2e-4 exp(-0.30/C) exp(-3850/T)  [m^2/s]"""
    C = np.clip(np.asarray(C, float), 1e-9, None)
    return 4.2e-4 * np.exp(-0.30 / C) * np.exp(-3850.0 / np.asarray(T, float))


def harm(a, b):
    return 2.0 * a * b / (a + b)


# --------------------------------------------------------------------------
# 模型
# --------------------------------------------------------------------------
class DryingModel:
    """problem = 1 / 2 / 3 / 4"""

    def __init__(self, problem, N=200, chamber_hold='final', radius=None,
                 scales=None, chamber_shift=None, chamber_series=None):
        """scales: 物性/边界系数乘子 {'h','hm','D','k','rho','cp'}, 默认全 1.
        chamber_shift: 恒温干燥阶段烘房 (dT, dC) 偏移, 用于敏感性分析。
        chamber_series: 自定义烘房时序 (t, T[K], C), 覆盖附件1 序列
            (GAN 情景生成等); 超出区间后按末值外推, chamber_shift 仍叠加。"""
        self.problem = problem
        self.N = int(N)
        self.xi_f = np.arange(self.N + 1) / self.N          # 面
        self.xi_c = (np.arange(self.N) + 0.5) / self.N      # 单元中心
        self.dxi = 1.0 / self.N

        self.t_ch, self.T_ch, self.C_ch = load_chamber(chamber_hold)
        if chamber_series is not None:
            ts, Ts, Cs = chamber_series
            self.t_ch = np.asarray(ts, float)
            self.T_ch = np.asarray(Ts, float)
            self.C_ch = np.asarray(Cs, float)

        sc = {'h': 1.0, 'hm': 1.0, 'D': 1.0, 'k': 1.0, 'rho': 1.0, 'cp': 1.0}
        if scales:
            sc.update({k: float(v) for k, v in scales.items()})
        self.sc = sc
        self.h_conv = H_CONV * sc['h']
        self.hm = HM * sc['hm']
        self.dT_ch, self.dC_ch = chamber_shift if chamber_shift else (0.0, 0.0)

        if problem == 4:
            if radius is None:
                self.t_R, self.R_tab = load_radius()
            else:
                self.t_R, self.R_tab = radius
            self.Rmax = float(self.R_tab[0])
        else:
            self.Rmax = R0

        if problem == 1:
            self.props, self.Dfun = props_p1, D_p1
        elif problem in (2, 3):
            self.props, self.Dfun = props_p3, D_p3
        elif problem == 4:
            self.props, self.Dfun = props_p4, D_p4
        else:
            raise ValueError(problem)

    # ---- 几何 ----
    def R_of(self, t):
        if self.problem != 4:
            return R0
        if np.isscalar(t) or np.ndim(t) == 0:
            return float(np.interp(t, self.t_R, self.R_tab))
        return np.interp(t, self.t_R, self.R_tab)

    def chamber(self, t):
        T = float(np.interp(t, self.t_ch, self.T_ch)) + self.dT_ch
        C = float(np.interp(t, self.t_ch, self.C_ch)) + self.dC_ch
        return T, C

    # ---- 右端项 ----
    def rhs(self, t, y):
        N, dxi, xi_f, xi_c = self.N, self.dxi, self.xi_f, self.xi_c
        T = y[0::2]
        C = y[1::2]
        R = self.R_of(t)
        R2 = R * R
        sc = self.sc
        rho, cp, k = self.props(C)
        rho = rho * sc['rho']
        cp = cp * sc['cp']
        k = k * sc['k']
        D = self.Dfun(C, T) * sc['D']

        Ta, Ca = self.chamber(t)

        # ---- 各面传导度 ----
        # 内部面 f=1..N-1
        Gt = xi_f[1:N] * harm(k[:-1], k[1:]) / dxi
        Gm = xi_f[1:N] * harm(D[:-1], D[1:]) / dxi
        # 表面 f=N: 半单元导热 + 对流。
        # 由单元中心到表面 xi=1 的导热热阻 = ∫_{xi_c}^{1} dxi/(xi k) = ln(1/xi_c)/k (k 取常数时精确)
        lnc = np.log(1.0 / xi_c[-1])
        Gt_s = 1.0 / (lnc / k[-1] + 1.0 / (self.h_conv * R))
        Gm_s = 1.0 / (lnc / D[-1] + 1.0 / (self.hm * R))

        # ---- 面通量 Phi_f (f = 0..N), 规定由左侧流入右侧 ----
        # 进入单元 i 的净通量 = Phi_i - Phi_{i+1}
        PhiT = np.empty(N + 1)
        PhiC = np.empty(N + 1)
        PhiT[0] = 0.0                       # xi=0 对称
        PhiC[0] = 0.0
        PhiT[1:N] = Gt * (T[:-1] - T[1:])   # 内部面 f=1..N-1
        PhiC[1:N] = Gm * (C[:-1] - C[1:])
        PhiT[N] = Gt_s * (T[-1] - Ta)       # 表面 f=N: 左侧=表面单元, 右侧=烘房
        PhiC[N] = Gm_s * (C[-1] - Ca)

        # 除以 (rho cp R^2 xi_c dxi)  /  (R^2 xi_c dxi)
        vol = R2 * xi_c * dxi
        dTdt = (PhiT[:-1] - PhiT[1:]) / (rho * cp * vol)
        dCdt = (PhiC[:-1] - PhiC[1:]) / vol

        out = np.empty(2 * N)
        out[0::2] = dTdt
        out[1::2] = dCdt
        return out

    def jac_sparsity(self):
        """交错排列 [T0,C0,T1,C1,...] 下, 单元 i 仅与 i-1,i,i+1 耦合 -> 带宽 3。"""
        n = 2 * self.N
        offs = (-3, -2, -1, 0, 1, 2, 3)
        return diags([np.ones(n - abs(o)) for o in offs], list(offs),
                     shape=(n, n), format='csr')

    # ---- 初始条件 ----
    def y0(self):
        y = np.empty(2 * self.N)
        y[0::2] = T_INIT + 273.15
        y[1::2] = C_INIT
        return y

    # ---- 求解 ----
    def solve(self, t_end, t_eval=None, events=None, rtol=1e-7, atol=1e-9,
              max_step=np.inf, y0=None, dense=True, method='BDF'):
        y0 = self.y0() if y0 is None else y0
        sol = solve_ivp(self.rhs, (0.0, float(t_end)), y0, method=method,
                        t_eval=t_eval, events=events, rtol=rtol, atol=atol,
                        max_step=max_step, jac_sparsity=self.jac_sparsity(),
                        dense_output=dense)
        return sol

    def surface_value(self, y, t):
        """由边界条件反解 xi=1 处的表面值。

        Phi_N 为 +xi 方向(向外)的约化通量, 物理总通量 Q = 2*pi*H*Phi_N;
        又 Q = h*A_s*(T_s - T_air) = h*2*pi*R*H*(T_s - T_air)
          =>  Phi_N = h*R*(T_s - T_air)  =>  T_s = T_air + Phi_N/(h*R)
        (水分同理: C_s = C_air + Phi_C/(hm*R))
        """
        N, dxi, xi_c = self.N, self.dxi, self.xi_c
        T, C = y[0::2], y[1::2]
        R = self.R_of(t)
        rho, cp, k = self.props(C)
        D = self.Dfun(C, T) * self.sc['D']
        k = k * self.sc['k']
        Ta, Ca = self.chamber(t)
        lnc = np.log(1.0 / xi_c[-1])
        Rs_T = lnc / k[-1] + 1.0 / (self.h_conv * R)
        Rs_C = lnc / D[-1] + 1.0 / (self.hm * R)
        PhiT = (T[-1] - Ta) / Rs_T
        PhiC = (C[-1] - Ca) / Rs_C
        return Ta + PhiT / (self.h_conv * R), Ca + PhiC / (self.hm * R)

    # ---- 插值到查询点 (xi 坐标系) ----
    def interp_xi(self, y, xi_q):
        """把单元中心值线性插值/外推到查询点 xi_q (可为标量或数组)。"""
        T = y[0::2]
        C = y[1::2]
        Tq = _lin_extrap(self.xi_c, T, xi_q)
        Cq = _lin_extrap(self.xi_c, C, xi_q)
        return Tq, Cq


def _lin_extrap(xp, fp, xq):
    xq = np.atleast_1d(np.asarray(xq, float))
    out = np.interp(xq, xp, fp)
    # 两端线性外推
    lo = xq < xp[0]
    hi = xq > xp[-1]
    if lo.any():
        s = (fp[1] - fp[0]) / (xp[1] - xp[0])
        out[lo] = fp[0] + s * (xq[lo] - xp[0])
    if hi.any():
        s = (fp[-1] - fp[-2]) / (xp[-1] - xp[-2])
        out[hi] = fp[-1] + s * (xq[hi] - xp[-1])
    return out
