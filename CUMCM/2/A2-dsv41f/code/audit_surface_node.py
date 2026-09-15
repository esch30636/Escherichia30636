"""DEFINITIVE TEST: is the surface node of the reviewed scheme internally consistent?

The reviewed semi-discrete scheme is
    V_i A_i dT_i/dt = F^T_{i-1/2} - F^T_{i+1/2},   F^T_R = R * h (T_s - T_a)
with T_s reconstructed by the half-cell Robin closure.  With the authored
`boundary()`, the loop computes tn = (k*T + h*half*Ta)/(k + h*half) -- which is
exactly the heat-balance solution -- but returns the ORIGINAL t, not tn.

This script integrates that scheme from scratch (author's module, author's
settings) and compares:
    T_s returned by boundary()        vs
    T_s required by the heat balance  vs
    the node value the scheme actually advances
"""
from pathlib import Path
import sys
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
A2 = Path(__file__).resolve().parents[2] / "A2-gpt"
sys.path.insert(0, str(A2 / "code"))
import solver as S

env = np.loadtxt(A2 / "data/ambient.csv", delimiter=",", skiprows=1)
air = lambda ts: np.stack([np.interp(ts, env[:, 0], env[:, i]) for i in (1, 2)], axis=-1)

for n in (200, 400):
    x, v, g, half = S.mesh(n)
    y = np.tile([28.0, 2.55], n)
    sp = S.sparsity(n)

    def rhs(t, yy):
        a = air(t)
        return S.kernel(yy, x, v, g, half, a[0], a[1], False, 25.0, 8e-7, 1.0)[0]

    from scipy.integrate import solve_ivp
    sol = solve_ivp(rhs, (0.0, 1800.0), y, method="BDF", rtol=1e-11,
                    atol=np.tile([1e-12, 1e-13], n), jac_sparsity=sp,
                    max_step=10.0)
    y = sol.y[:, -1]
    ta, ca = float(air(1800.0)[0]), float(air(1800.0)[1])
    ts, cs, q, j = S.boundary(y[-2], y[-1], ta, ca, half, False, 25.0, 8e-7, 1.0)

    # node value the scheme advanced, mapped to r = R by the same closure
    Tn, Cn = y[-2], y[-1]
    kf, df = S.face(Tn, Cn, ts, cs, False, 1.0)
    q_node = kf * (Tn - ts) / half          # == the R * h(Ts-Ta) the kernel uses
    bal_Ts = (kf * Tn + 25.0 * half * ta) / (kf + 25.0 * half)

    print(f"\n================ n = {n} ================")
    print(f"  half = {half:.4e} m,  k = {kf:.6f} W/(m K),  h*half = {25.0 * half:.4e}")
    print(f"  node T_lastcell            = {Tn:.9f} C")
    print(f"  boundary() RETURNED T_s    = {ts:.9f} C")
    print(f"  heat balance REQUIRES T_s  = {bal_Ts:.9f} C")
    print(f"  discrepancy                = {ts - bal_Ts:+.6e} K")
    print(f"  k*(T_N - T_s)/half [W/m2]  = {q_node:.6e}")
    print(f"  h*(T_s - T_a)      [W/m2]  = {25.0 * (ts - ta):.6e}")
    print(f"  heat-flux mismatch [W/m2]  = {q_node - 25.0 * (ts - ta):.6e}")
    print(f"  ambient T_a                = {ta:.6f} C")
    print(f"  ==> is T_N - T_s ~ (h/k)*half*(T_s-T_a) = "
          f"{25.0 / kf * half * (ts - ta):.3e} K ?  actual {Tn - ts:.3e} K")
    print(f"  surface C: returned {cs:.9f} vs node {Cn:.9f} (diff {cs - Cn:+.3e})")
