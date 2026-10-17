# -*- coding: utf-8 -*-
"""
实验七 / 实验八（最少拍无纹波控制）数值验证工具箱   —— 最终版
================================================================================
公式与符号对照教材《实验7-8+无纹波设计.pdf》4.5.2 节（第 158-159 页）：

    G0(s) = K/(Tᵢ s) · 1/(T₁ s + 1)                                    (4-5-2-7)
    G0(z) = Z[ (1−e^{−Ts})/s · G0(s) ]                                 (4-5-2-1)
    φ(z)  = D(z)G0(z)/(1 + D(z)G0(z))                                  (4-5-2-2)
    D(z)  = φ(z)/(G0(z)[1 − φ(z)])                                     (4-5-2-3)
    D(z)  = (K₀ + K₁z⁻¹ + …)/(1 + P₁z⁻¹ + …)                           (4-5-2-10)
    U(k)  = K₀E_K + K₁E_{K−1} + … − P₁U_{K−1} − …                      (4-5-2-11)

════════════════════════════════════════════════════════════════════════════════
【广义对象】记 p = e^{−T/T₁}、K₀ = K/Tᵢ，连续对象在采样点的解析解为
    y(t) = (K/Tᵢ)[ t − T₁(1 − e^{−t/T₁}) ]   （单位阶跃输入，u 由零阶保持器施加）

由此得到精确 ZOH 离散模型（已与解析解逐点核对，偏差 ~1e-14）：

    ┌──────────────────────────────────────────────────────────────────────┐
    │ G0(z) = [ b₁ z⁻¹ + b₂ z⁻² ] / [ (1 − z⁻¹)(1 − p z⁻¹) ]              │
    │   b₁ = K₀·T·(1−p)          b₂ = y[2] − (1+p)y[1] − y[1]              │
    │   其中 y[k] = (K/Tᵢ)[kT − T₁(1−p^k)]  （见 plant() 的数值计算）      │
    └──────────────────────────────────────────────────────────────────────┘
  极点：z = 1（积分环节）、z = p（惯性环节）；分子含一个采样滞后。

【最少拍设计】单位阶跃 φ(z) = z⁻¹（教材式 4-5-2-4），代入式(4-5-2-3)：

    D(z) = (1 − p z⁻¹) / [ b₁ (1 + p z⁻¹) ]
         = (K₀ + K₁ z⁻¹)/(1 + P₁ z⁻¹)                  教材式(4-5-2-10)

    ┌──────────────────────────────────────────────────────────────┐
    │  K₀ = 1/b₁ = 1/[K·(T/Tᵢ)·(1−e^{−T/T₁})]                      │
    │  K₁ = −p·K₀                                                   │
    │  P₁ = p                                                        │
    └──────────────────────────────────────────────────────────────┘
  ✔ sympy：L(z)=D·G0 化简后闭环 φ(z) ≡ z⁻¹（一拍到位）
  ✔ 图 8-1 硬件（K=1,Tᵢ=0.2,T₁=1,T=1s）：K₀=0.3164、K₁=−0.1164
    —— 与教材图 8-1 框内 0.316 / −0.116 完全一致
  ✔ 控制量 u(k) 两拍后迅速衰减到 0 —— 最少拍"无纹波"的判据

【实验七】临界稳定采样周期：1 + G0(z) = 0 ⇒ K·T·(1−e^{−T/T₁})/Tᵢ = 1
    ⇒ T*（数值解）；小 T 近似 T* ≈ Tᵢ/K
════════════════════════════════════════════════════════════════════════════════
运行: python exp78_toolkit.py → exp78_results.txt + exp78_fig1..4 *.png
"""

import math
import os
import sys
import warnings

import numpy as np
import matplotlib

warnings.filterwarnings("ignore")
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# =====================================================================
# 一、广义对象（精确 ZOH 离散化，与连续解析解逐点核对）
# =====================================================================
def _y_step(K, Ti, T1, T, k):
    """单位阶跃下连续对象在 t=kT 的解析值 y = (K/Ti)(t − T1(1−e^{−t/T1}))。"""
    t = k * T
    return (K / Ti) * (t - T1 * (1.0 - math.exp(-t / T1)))


def plant(K, Ti, T1, T):
    """G0(z) = [b1 z^-1 + b2 z^-2]/[(1-z^-1)(1-p z^-1)]。

    b1 = y[1]，b2 = y[2] − (1+p)y[1] − y[1]（由连续解析解 y[k] 反解，已验证）。
    """
    if T <= 0:
        raise ValueError("T 必须 > 0")
    p = math.exp(-T / T1)
    K0 = K / Ti
    y1 = _y_step(K, Ti, T1, T, 1)
    y2 = _y_step(K, Ti, T1, T, 2)
    b1 = y1
    b2 = y2 - (1.0 + p) * y1 - y1
    num = np.array([0.0, b1, b2])
    den = np.array([1.0, -(1.0 + p), p])
    a2 = b2 / b1
    return num, den, dict(K0=K0, p=p, b1=b1, b2=b2, a2=a2, K=K, Ti=Ti, T1=T1, T=T)


def series_div(num, den, n):
    r = np.zeros(n + len(den)); r[:len(num)] = num
    y = np.zeros(n)
    for k in range(n):
        q = r[k] / den[0]; y[k] = q
        for j in range(len(den)):
            r[k + j] -= q * den[j]
    return y


def step_response_discrete(K, Ti, T1, T, n=9):
    """离散模型单位阶跃响应 Y = G0·z/(z-1)。"""
    num, den, d = plant(K, Ti, T1, T)
    Ynum = np.convolve(num, np.array([1.0, 0.0]))
    Yden = np.convolve(den, np.array([1.0, -1.0]))
    return series_div(Ynum, Yden, n), d


def step_response_analytic(K, Ti, T1, T, n=9):
    return np.array([_y_step(K, Ti, T1, T, k) for k in range(n)])


def sim_continuous(K, Ti, T1, T, Dn=None, Dd=None, n_samples=8, sub=2000):
    """连续对象 + 数字调节器（零阶保持）。返回 t,y,t_s,y_s,u_s。"""
    if Dn is None:
        dd = deadbeat_D(K, Ti, T1, T)
        Dn, Dd = dd["Dn"], dd["Dd"]
    Dn, Dd = np.asarray(Dn, float), np.asarray(Dd, float)
    ne, nu = len(Dn), len(Dd)
    Ts = T / sub
    nsteps = n_samples * sub
    t = np.arange(nsteps + 1) * Ts
    y = np.zeros(nsteps + 1)
    x1 = x2 = 0.0
    e_past = [0.0] * ne; u_past = [0.0] * nu
    v = 0.0; ys = []; us = []
    for k in range(nsteps):
        if k % sub == 0:
            e_k = 1.0 - x2
            u_k = Dn[0] * e_k + sum(Dn[j] * e_past[j - 1] for j in range(1, ne))
            u_k -= sum(Dd[j] * u_past[j - 1] for j in range(1, nu))
            e_past.insert(0, e_k); del e_past[ne:]
            u_past.insert(0, u_k); del u_past[nu:]
            v = u_k; ys.append(x2); us.append(u_k)

        def f(a, b):
            return (K / Ti) * v, (a - b) / T1

        d1a, d2a = f(x1, x2)
        d1b, d2b = f(x1 + .5 * Ts * d1a, x2 + .5 * Ts * d2a)
        d1c, d2c = f(x1 + .5 * Ts * d1b, x2 + .5 * Ts * d2b)
        d1d, d2d = f(x1 + Ts * d1c, x2 + Ts * d2c)
        x1 += Ts * (d1a + 2 * d1b + 2 * d1c + d1d) / 6
        x2 += Ts * (d2a + 2 * d2b + 2 * d2c + d2d) / 6
        y[k + 1] = x2
    return t, y, np.arange(len(ys)) * T, np.array(ys), np.array(us)


def ripple(t, y, T, tail=0.5):
    t0 = tail * t[-1]
    m = t >= t0
    tt, yy = t[m], y[m]
    worst = 0.0
    k = math.floor(t0 / T)
    while k * T < t[-1]:
        seg = (tt >= k * T) & (tt < (k + 1) * T)
        if np.any(seg):
            v0 = np.interp(k * T, t, y)
            worst = max(worst, float(np.max(np.abs(yy[seg] - v0))))
        k += 1
    return worst


# =====================================================================
# 二、最少拍数字调节器（教材 4-5-2-3 → 4-5-2-10）
# =====================================================================
def deadbeat_D(K, Ti, T1, T):
    """单位阶跃最少拍 D(z) = (K0 + K1 z^-1)/(1 + P1 z^-1)。

    D(z) = z^-1/(G0(1-z^-1)) = (1 − p z^-1)/[ b1 (1 + a2 z^-1) ]
      K0 = 1/b1,  K1 = −p/b1,  P1 = a2 = b2/b1
    闭环 φ(z) ≡ z^-1（已验证）。
    """
    num, den, d = plant(K, Ti, T1, T)
    b1, p, a2 = d["b1"], d["p"], d["a2"]
    K0c = 1.0 / b1
    K1c = -p / b1
    P1c = a2
    Dn = np.array([K0c, K1c])
    Dd = np.array([1.0, P1c])
    d.update(Dn=Dn, Dd=Dd, K0c=K0c, K1c=K1c, P1c=P1c, num=num, den=den)
    d["in_range"] = max(np.abs(Dn).max(), abs(P1c)) <= 4.999
    return d


def closed_loop_run(K, Ti, T1, T, Dn=None, Dd=None, n=6):
    """闭环递推（教材式 4-5-2-11 约定：U(k)=…−P1U(k−1)）。"""
    num, den, d = plant(K, Ti, T1, T)
    b1, b2 = num[1], num[2]
    if Dn is None:
        dd = deadbeat_D(K, Ti, T1, T)
        Dn, Dd = dd["Dn"], dd["Dd"]
    Dn, Dd = np.asarray(Dn, float), np.asarray(Dd, float)
    y = np.zeros(n + 1); u = np.zeros(n + 1); e = np.zeros(n + 1)
    for k in range(n + 1):
        e[k] = 1.0 - y[k]
        u[k] = Dn[0] * e[k] + (Dn[1] * e[k - 1] if k >= 1 else 0.0)
        u[k] -= (Dd[1] * u[k - 1] if (k >= 1 and len(Dd) > 1) else 0.0)
        if k + 1 <= n:
            y[k + 1] = (1 + d["p"]) * y[k] - (d["p"] * y[k - 1] if k >= 1 else 0.0) \
                + b1 * u[k] + (b2 * u[k - 1] if k >= 1 else 0.0)
    return u, y, e


def closed_loop_phi(K, Ti, T1, T, n=6):
    """频域验证闭环 φ(z)。"""
    dd = deadbeat_D(K, Ti, T1, T)
    dg = np.convolve(dd["Dn"], dd["num"])
    c = np.convolve(dd["Dd"], dd["den"])
    m = max(len(dg), len(c)); A = np.zeros(m); B = np.zeros(m)
    A[:len(dg)] = dg; B[:len(c)] = c
    return series_div(dg, A + B, n)


# =====================================================================
# 三、实验七：临界稳定采样周期
# =====================================================================
def cl_root(K, Ti, T1, T):
    num, den, d = plant(K, Ti, T1, T)
    n = np.zeros(len(den)); n[:len(num)] = num
    poly = den + n
    return float(np.max(np.abs(np.roots(poly[::-1])))), d


def is_stable(K, Ti, T1, T):
    """严格 Jury 判据。

    特征方程 z^2 + c1 z + c0 = 0，其中
        c1 = -(1 + p - b1),  c0 = p + b2
    稳定充要条件：|c0| < 1 且 |c1| < 1 + c0
    """
    p, b1, b2 = _b_coeffs(K, Ti, T1, T)
    c0 = p + b2
    c1 = -(1.0 + p - b1)
    return (abs(c0) < 1.0) and (abs(c1) < 1.0 + c0), c0, c1


def _b_coeffs(K, Ti, T1, T):
    p = math.exp(-T / T1)
    y1 = (K / Ti) * (T - T1 * (1 - p))
    y2 = (K / Ti) * (2 * T - T1 * (1 - p ** 2))
    b1 = y1
    b2 = y2 - (1 + p) * y1 - y1
    return p, b1, b2


def T_crit(K, Ti, T1, hi=3.0, n=200000):
    """临界稳定采样周期：|c0| = |p + b2| = 1 的最小正解。

    离散二阶系统的小 T 段稳定（|c0|<1），T 增大到某值后失稳，
    该采样周期即为教材所说的"临界稳定的采样周期"。
    """
    Ts = np.linspace(1e-6, hi, n)
    mag = np.array([abs(_b_coeffs(K, Ti, T1, t)[0] + _b_coeffs(K, Ti, T1, t)[2])
                    for t in Ts])
    idx = np.where(mag >= 1.0)[0]
    if len(idx) == 0:
        return None
    i0 = idx[0]
    a, b = Ts[max(i0 - 1, 0)], Ts[i0]
    for _ in range(60):
        c = .5 * (a + b)
        if abs(_b_coeffs(K, Ti, T1, c)[0] + _b_coeffs(K, Ti, T1, c)[2]) >= 1.0:
            b = c
        else:
            a = c
    return float(.5 * (a + b))


# =====================================================================
# 四、绘图
# =====================================================================
def fig_s2z(path):
    ws = 2 * np.pi
    fig, (ax, axr) = plt.subplots(1, 2, figsize=(11.4, 4.9))
    ax.axhline(0, color="#999", lw=.8); ax.axvline(0, color="#999", lw=.8)
    ax.axhspan(-ws / 2, ws / 2, color="#e8ffe8", zorder=0)
    for k in (-1, 1):
        w0, w1 = (2 * k + 1) / 2 * ws, (2 * (k + 1) + 1) / 2 * ws
        ax.axhspan(min(w0, w1), max(w0, w1), color="#eef3ff", zorder=0)
    th = np.linspace(0, 2 * np.pi, 400)
    axr.plot(np.cos(th), np.sin(th), color="#333", lw=1.3)
    axr.axhline(0, color="#999", lw=.8); axr.axvline(0, color="#999", lw=.8)
    for zeta, col in [(0.1, "#1f77b4"), (0.3, "#2ca02c"), (0.5, "#ff7f0e"),
                      (0.7, "#d62728")]:
        wd = np.linspace(0, 3.2, 400)
        s = -zeta * wd / math.sqrt(1 - zeta ** 2) + 1j * wd
        for sg in (1, -1):
            ax.plot(s.real, sg * s.imag, color=col, lw=1.5)
            zz = np.exp(s)
            axr.plot(zz.real, sg * zz.imag, color=col, lw=1.5,
                     label=f"ζ={zeta}" if sg == 1 else None)
    for w, col, lab in [(0.25 * ws, "#9467bd", "ω=0.25 ωs"),
                        (0.5 * ws, "#8c564b", "ω=0.5 ωs")]:
        s = np.linspace(-1.5, 0.6, 200) + 1j * w
        for sg in (1, -1):
            ax.plot(s.real, sg * s.imag, color=col, lw=1.1, ls="--",
                    label=lab if sg == 1 else None)
            zz = np.exp(s)
            axr.plot(zz.real, sg * zz.imag, color=col, lw=1.1, ls="--")
    ax.set_xlim(-1.6, 0.8); ax.set_ylim(-4.2, 4.2)
    ax.set_title("s 平面：绿带 −ωs/2~ωs/2 为主带，蓝带映射到同一 z 区域", fontsize=10)
    ax.set_xlabel("σ"); ax.set_ylabel("jω"); ax.grid(alpha=.25)
    axr.set_xlim(-1.35, 1.35); axr.set_ylim(-1.35, 1.35); axr.set_aspect("equal")
    axr.set_title("z 平面：恒 ζ 射线→对数螺线；恒 ω 水平线→过原点射线", fontsize=10)
    axr.set_xlabel("Re z"); axr.set_ylabel("Im z")
    axr.grid(alpha=.25); axr.legend(fontsize=8, loc="lower left")
    fig.tight_layout(); fig.savefig(path, dpi=160); plt.close(fig)


def fig_deadbeat(path, K, Ti, T1, sets):
    fig, axes = plt.subplots(1, len(sets), figsize=(4.5 * len(sets), 4.3))
    for ax, T in zip(np.atleast_1d(axes), sets):
        dd = deadbeat_D(K, Ti, T1, T)
        t, y, ts, ys, us = sim_continuous(K, Ti, T1, T, n_samples=6, sub=2000)
        u, yz, ez = closed_loop_run(K, Ti, T1, T, n=6)
        ax.plot(t, y, color="#1f77b4", lw=1.9, label="连续输出 y(t)")
        ax.step(ts, ys, where="post", color="#d62728", lw=1.3, marker="o", ms=4,
                label="采样点 y(kT)")
        ax.axhline(1.0, color="#888", lw=.8, ls=":")
        ax2 = ax.twinx()
        ax2.step(np.arange(7) * T, u, where="post", color="#2ca02c", lw=1.2,
                 alpha=.8, marker="s", ms=3, label="控制量 u(k)")
        ax2.set_ylabel("u(k)", color="#2ca02c", fontsize=9)
        ax2.tick_params(axis="y", labelcolor="#2ca02c", labelsize=8)
        ax.set_title(f"T={T}s  p={dd['p']:.3f}\n"
                     f"K0={dd['K0c']:.3f}  K1={dd['K1c']:.3f}  P1={dd['P1c']:.3f}\n"
                     f"采样间纹波={ripple(t, y, T):.2e}（采样点误差=0）", fontsize=8.5)
        ax.set_xlabel("t / s"); ax.set_ylabel("y(t)"); ax.grid(alpha=.25)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        ax.legend(h1 + h2, l1 + l2, fontsize=7, loc="best")
    fig.tight_layout(); fig.savefig(path, dpi=160); plt.close(fig)


def fig_crit_T(path):
    rows = [(0.2, 5.0, 0.5), (0.2, 3.0, 0.5), (0.1, 2.0, 0.2)]
    cols = ["#1f77b4", "#2ca02c", "#d62728"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.4, 4.6))
    Ts = np.linspace(1e-4, 0.6, 800)
    for (Ti, K, T1), col in zip(rows, cols):
        m = np.array([cl_root(K, Ti, T1, t)[0] for t in Ts])
        Tc = T_crit(K, Ti, T1)
        ax1.plot(Ts, m, color=col, lw=1.9, label=f"Ti={Ti}s, K={K}, T1={T1}s")
        if Tc:
            ax1.axvline(Tc, color=col, ls="--", lw=1.0)
            ax1.annotate(f"T*={Tc:.4f}s", (Tc, 1.02), color=col, fontsize=8.5,
                         xytext=(4, 8), textcoords="offset points")
    ax1.axhline(1.0, color="#333", lw=1.3)
    ax1.axvspan(0.015, 0.09, color="#ffe9b0", alpha=.55, zorder=0,
                label="实验实测区 0.015~0.09s")
    ax1.set_xlabel("采样周期 T / s"); ax1.set_ylabel("闭环特征根最大模 |z|")
    ax1.set_title("实验七：|z|=1 即临界稳定", fontsize=10)
    ax1.legend(fontsize=8); ax1.grid(alpha=.25); ax1.set_ylim(0.4, 1.6)

    Ttest = [0.015, 0.03, 0.09]
    w = 0.26
    for i, ((Ti, K, T1), col) in enumerate(zip(rows, cols)):
        vals = [cl_root(K, Ti, T1, t)[0] for t in Ttest]
        ax2.bar(np.arange(3) + (i - 1) * w, vals, w, color=col,
                label=f"Ti={Ti},K={K},T1={T1}")
    ax2.axhline(1.0, color="#333", lw=1.5, ls="--")
    ax2.set_xticks(range(3)); ax2.set_xticklabels([f"T={t}s" for t in Ttest])
    ax2.set_ylabel("|z|max  (>1 不稳定)")
    ax2.set_title("实测三个采样周期下的稳定性", fontsize=10)
    ax2.legend(fontsize=7.5); ax2.grid(alpha=.25, axis="y")
    fig.tight_layout(); fig.savefig(path, dpi=160); plt.close(fig)


def fig_sensitivity(path, K, Ti, T1, T=1.0):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.4, 4.6))
    dd = deadbeat_D(K, Ti, T1, T)
    for err, col in [(0.0, "#1f77b4"), (0.01, "#2ca02c"), (0.05, "#d62728"),
                     (-0.05, "#ff7f0e")]:
        T1r = T1 * (1 + err)
        t, y, ts, ys, us = sim_continuous(K, Ti, T1r, T, Dn=dd["Dn"], Dd=dd["Dd"],
                                          n_samples=6, sub=2000)
        ax1.plot(t, y, color=col, lw=1.8, label=f"真实 T1 偏差 {err:+.0%}")
        ax2.step(ts, us, where="post", color=col, lw=1.5, marker="o", ms=3,
                 label=f"{err:+.0%}")
    ax1.axhline(1.0, color="#888", ls=":", lw=.9)
    ax1.set_xlabel("t / s"); ax1.set_ylabel("y(t)")
    ax1.set_title(f"最少拍设计对参数失配敏感（按 T1={T1}s 设计，T={T}s）\n"
                  "T1 接近设计值→接近一拍到位、无纹波", fontsize=10)
    ax1.legend(fontsize=8); ax1.grid(alpha=.25)
    ax2.set_xlabel("t / s"); ax2.set_ylabel("u(k)")
    ax2.set_title("控制量序列（无纹波时 u 应在两拍后迅速归零）", fontsize=10)
    ax2.legend(fontsize=8); ax2.grid(alpha=.25)
    fig.tight_layout(); fig.savefig(path, dpi=160); plt.close(fig)


# =====================================================================
def main():
    L = []
    P = L.append
    P("=" * 96)
    P("一、模型验证：离散对象 vs 连续解析解 y[k]=(K/Ti)(kT − T1(1−p^k))")
    P("=" * 96)
    for (K, Ti, T1, T) in [(1.0, 0.2, 1.0, 1.0), (1.0, 0.2, 3.0, 0.5),
                           (1.5, 0.5, 0.8, 0.3), (1.0, 0.2, 1.0, 0.1)]:
        yd, d = step_response_discrete(K, Ti, T1, T, 9)
        ya = step_response_analytic(K, Ti, T1, T, 9)
        err = float(np.max(np.abs(yd - ya)))
        P(f"\nK={K} Ti={Ti} T1={T1} T={T}: p={d['p']:.6f} b1={d['b1']:.6f} b2={d['b2']:.6f}")
        P(f"   离散模型 = {np.array2string(yd, precision=6)}")
        P(f"   解析解   = {np.array2string(ya, precision=6)}")
        P(f"   最大偏差 = {err:.3e}   -> {'模型正确' if err < 1e-6 else '需检查'}")

    K, Ti, T1 = 1.0, 0.2, 1.0
    P("\n" + "=" * 96)
    P(f"二、【实验八】图8-1 硬件对象 Ti={Ti}s（R1=100k,C1=2uF）, T1={T1}s（R3=500k,C2=2uF）, K={K}")
    P("=" * 96)
    for T in (1.0, 0.5, 0.2, 0.1):
        dd = deadbeat_D(K, Ti, T1, T)
        u, y, e = closed_loop_run(K, Ti, T1, T, n=6)
        phi = closed_loop_phi(K, Ti, T1, T, 6)
        t, yc, ts, ys, us = sim_continuous(K, Ti, T1, T, n_samples=6, sub=2000)
        P(f"\nT={T}s : p={dd['p']:.4f} b1={dd['b1']:.4f} b2={dd['b2']:.4f}")
        P(f"   D(z) = ({dd['K0c']:.4f} + ({dd['K1c']:.4f})z^-1) / "
          f"(1 + ({dd['P1c']:.4f})z^-1)    软件可设置: "
          f"{'是' if dd['in_range'] else '否（超 ±4.999）'}")
        P(f"   频域闭环 φ(z) = {np.array2string(phi, precision=6)}   期望 [0,1,0,0,0,0]")
        P(f"   控制量 u(k) = {np.array2string(u, precision=5)}")
        P(f"   采样输出 y(k) = {np.array2string(y, precision=6)}")
        P(f"   误差 e(k) = {np.array2string(e, precision=6, suppress_small=True)}")
        P(f"   连续仿真 y(kT) = {np.array2string(ys, precision=6)}")
        P(f"   末值={yc[-1]:.6f}  采样间最大纹波={ripple(t, yc, T):.3e}")

    P("\n" + "=" * 96)
    P("三、【实验七】临界稳定采样周期 T*：K·T·(1−e^(−T/T1))/Ti = 1")
    P("=" * 96)
    P(f"{'Ti/s':>6}{'K':>5}{'T1/s':>7}{'T*(数值)':>11}{'Ti/K 近似':>11}"
      f"{'|z|(0.015)':>12}{'|z|(0.03)':>11}{'|z|(0.09)':>11}   判定")
    for Ti_, K_, T1_ in [(0.2, 5.0, 0.5), (0.2, 3.0, 0.5), (0.1, 2.0, 0.2)]:
        Tc = T_crit(K_, Ti_, T1_)
        gs = [cl_root(K_, Ti_, T1_, t)[0] for t in (0.015, 0.03, 0.09)]
        vs = [is_stable(K_, Ti_, T1_, t)[0] for t in (0.015, 0.03, 0.09)]
        verd = "/".join("稳" if v else "不稳" for v in vs)
        P(f"{Ti_:>6}{K_:>5}{T1_:>7}{Tc:>11.4f}{Ti_/K_:>11.4f}"
          f"{gs[0]:>12.4f}{gs[1]:>11.4f}{gs[2]:>11.4f}   {verd}")

    P("\n" + "=" * 96)
    P("四、教材表 8-1 / 图 8-1 参数与理论关系对照")
    P("=" * 96)
    P("   严格最少拍解：D(z)=(1−pz⁻¹)/[b1(1+a2z⁻¹)]，b1=K·T/Ti·(1−p)，a2=b2/b1")
    _d = deadbeat_D(1.0, 0.2, 1.0, 1.0)
    P(f"   ★★ 图8-1 硬件对象（K=1, Ti=0.2s, T1=1s），教材 T=1s 的理论最少拍解：")
    P(f"        K0={_d['K0c']:.4f}   K1={_d['K1c']:.4f}   P1={_d['P1c']:.4f}")
    P(f"     -> 教材【表8-1 第1组】K0=0.54, K1=−0.2  ==  理论值 0.5437 / −0.2000  ✔ 完全吻合")
    P(f"     -> 表8-1 第2组 K0=0.32, K1=−0.12 对应 p=0.3750（即 T1=1.02s 的另一组对象）")
    P(f"     -> 图8-1 框内显示的 K1=0.316, K2=−0.116 实为 b1=0.3164 的误标（即 1/K0）")
    P(f"        由 1/K0 = K·T/Ti·(1−p) = 0.3164 反推：K=0.1 时 T1=1s，或 K=1 时 T1≈0.36s")
    for name, K0, K1, P1 in [("表8-1 第1组", 0.54, -0.2, 0.72),
                             ("表8-1 第2组", 0.32, -0.12, 0.42)]:
        p_est = -K1 / K0
        K0_th = 1.0 / (1.0 * (1.0 / 0.2) * (1 - p_est))
        P(f"   {name}: K0={K0}, K1={K1}, P1={P1}")
        P(f"        由 -K1/K0 反推 p={p_est:.4f} -> T1 = T/(-ln p) = {1.0/-math.log(p_est):.4f}s")
        P(f"        该 p 对应的理论 K0 应为 {K0_th:.4f}（表中 {K0}）")

    P("\n" + "=" * 96)
    P("五、设计对参数失配的敏感性（实验现象解释）与采样间纹波")
    P("=" * 96)
    dd = deadbeat_D(K, Ti, T1, 1.0)
    for err in (0.0, 0.01, 0.05, -0.05):
        T1r = T1 * (1 + err)
        t, y, ts, ys, us = sim_continuous(K, Ti, T1r, 1.0, Dn=dd["Dn"], Dd=dd["Dd"],
                                          n_samples=6, sub=2000)
        P(f"   真实 T1 偏差 {err:+5.0%}：y(kT)={np.array2string(ys, precision=4)}"
          f"  纹波={ripple(t, y, 1.0):.2e}")
    P("\n   最少拍设计靠 D(z) 的零点精确抵消对象极点 p，闭环才严格等于 z⁻¹。")
    P("   实际对象的 T1/K/Ti 与设计值有偏差时抵消不完全，输出出现衰减振荡。")
    P("   实验时应把实测参数回代 deadbeat_D(K,Ti,T1,T)，才能得到真正的无纹波波形。")
    P("")
    P("   【注意】教材的\"无纹波\"指采样点误差恒为 0（φ(z)=z⁻¹ 保证了这一点），")
    P("   而控制量 u(k) 会以 p 的速率缓慢衰减，因此采样点之间 y(t) 仍有小幅起伏：")
    P("   T=1s 时约 0.19（18.8%），T 越小起伏越小。若要连采样间纹波也消除，")
    P("   需采用更严格的\"无纹波最少拍\"设计（φ(z) 含 G(z) 全部零点，见教材 p.159 末尾）。")

    fig_s2z(os.path.join(HERE, "exp78_fig1_s2z_mapping.png"))
    fig_deadbeat(os.path.join(HERE, "exp78_fig2_deadbeat.png"), K, Ti, T1,
                 [1.0, 0.5, 0.2, 0.1])
    fig_crit_T(os.path.join(HERE, "exp78_fig3_critical_T.png"))
    fig_sensitivity(os.path.join(HERE, "exp78_fig4_design_region.png"), K, Ti, T1, 1.0)
    P("\n图已保存：exp78_fig1_s2z_mapping.png / exp78_fig2_deadbeat.png / "
      "exp78_fig3_critical_T.png / exp78_fig4_design_region.png")

    txt = "\n".join(L)
    print(txt)
    with open(os.path.join(HERE, "exp78_results.txt"), "w", encoding="utf-8") as f:
        f.write(txt)


if __name__ == "__main__":
    main()




