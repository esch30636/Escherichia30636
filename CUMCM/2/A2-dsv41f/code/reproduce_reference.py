"""Run the reviewed solver module for the FULL 10800 s and compare its own final
state with the state stored in verification/tight800.npz."""
from pathlib import Path
import sys
import numpy as np
from scipy.integrate import solve_ivp

sys.path.insert(0, str(Path(__file__).resolve().parent))
A2 = Path(__file__).resolve().parents[2] / "A2-gpt"
sys.path.insert(0, str(A2 / "code"))
import solver as S

env = np.loadtxt(A2 / "data/ambient.csv", delimiter=",", skiprows=1)
air = lambda ts: np.stack([np.interp(ts, env[:, 0], env[:, i]) for i in (1, 2)], axis=-1)

n = 800
x, v, g, half = S.mesh(n)
y = np.tile([28.0, 2.55], n)
sp = S.sparsity(n)


def rhs(t, yy):
    a = air(t)
    return S.kernel(yy, x, v, g, half, a[0], a[1], False, 25.0, 8e-7, 1.0)[0]


steps = 0
for left in range(0, 10800, 60):
    right = left + 60
    sol = solve_ivp(rhs, (left, right), y, method="BDF", rtol=1e-11,
                    atol=np.tile([1e-12, 1e-13], n), jac_sparsity=sp,
                    max_step=10.0, dense_output=True)
    assert sol.success
    steps += len(sol.t) - 1
    y = sol.y[:, -1]

z = np.load(A2 / "verification/tight800.npz")
yd = z["final_cells"]
print(f"recomputed steps = {steps}")
print(f"{'index':>6} {'recomputed':>18} {'delivered':>18} {'diff':>12}")
for i in (-1, -2, -3, -4, -5, 0, 1):
    print(f"{i:6d} {y[i]:18.12f} {yd[i]:18.12f} {y[i] - yd[i]:12.3e}")
print()
ta, ca = float(air(10800.0)[0]), float(air(10800.0)[1])
for tag, yy in (("recomputed", y), ("delivered ", yd)):
    ts, cs, q, j = S.boundary(yy[-2], yy[-1], ta, ca, half, False, 25.0, 8e-7, 1.0)
    kf, df = S.face(yy[-2], yy[-1], ts, cs, False, 1.0)
    bal = (kf * yy[-2] + 25.0 * half * ta) / (kf + 25.0 * half)
    print(f"\n{tag}: node T={yy[-2]:.9f}  boundary Ts={ts:.9f}  balance Ts={bal:.9f}"
          f"  |diff|={abs(ts - bal):.3e}")
    print(f"           k(T_N-Ts)/half={kf * (yy[-2] - ts) / half:.6e}"
          f"   h(Ts-Ta)={25.0 * (ts - ta):.6e}")
print(f"\nmax |recomputed - delivered| over all internal cells = "
      f"{np.max(np.abs(y - yd)):.6e}")
