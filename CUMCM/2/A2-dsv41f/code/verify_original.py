"""Use the ORIGINAL A2-gpt solver module to evaluate its own state, with no
re-implementation in the loop."""
from pathlib import Path
import sys
import numpy as np

A2 = Path(r"E:\HUST\国赛\A2\A2-gpt")
sys.path.insert(0, str(A2 / "code"))
import solver as S                      # the reviewed module itself

z = np.load(A2 / "verification/tight800.npz")
y = z["final_cells"]; x = z["x_m"]; n = x.size
_, v, g, half = S.mesh(n)
env = np.loadtxt(A2 / "data/ambient.csv", delimiter=",", skiprows=1)
ta, ca = env[env[:, 0] == 10800, 1:][0]

rhs, qt, qc, corr = S.kernel(y, x, v, g, half, ta, ca, False, 25.0, 8e-7, 1.0)
ts, cs, jT, jC = S.boundary(y[-2], y[-1], ta, ca, half, False, 25.0, 8e-7, 1.0)
kf, df = S.face(y[-2], y[-1], ts, cs, False, 1.0)

print("ORIGINAL MODULE results")
print(f"  boundary: Ts={ts!r} Cs={cs!r} q={jT!r} j={jC!r}")
print(f"  face coeffs: k={kf!r} D={df!r}")
print(f"  kernel returns qt={qt!r} qc={qc!r}")
print(f"  rhs last cell: dC/dt={rhs[-1]!r}  dT/dt={rhs[-2]!r}")
print()
print("manual reconstruction with the ORIGINAL mesh arrays")
print(f"  v[-1]={v[-1]!r}  half={half!r}  R-x[-1]={0.02 - x[-1]!r}")
print(f"  D*(C_N-Cs)/half = {df * (y[-1] - cs) / half!r}")
print(f"  hm*(Cs-Ca)      = {8e-7 * (cs - ca)!r}")
print(f"  k*(T_N-Ts)/half = {kf * (y[-2] - ts) / half!r}")
print(f"  h*(Ts-Ta)       = {25.0 * (ts - ta)!r}")
print(f"  Ts formula      = {(kf * y[-2] + 25.0 * half * ta) / (kf + 25.0 * half)!r}")
print()
print("conclusion test: does the ORIGINAL code's Ts satisfy k(T_N-Ts)/half = h(Ts-Ta)?")
lhs = kf * (y[-2] - ts) / half
rhs_ = 25.0 * (ts - ta)
print(f"  lhs={lhs!r}  rhs={rhs_!r}  |diff|={abs(lhs - rhs_)!r}")
print()
print("and for moisture: D(C_N-Cs)/half vs hm(Cs-Ca)")
print(f"  lhs={df * (y[-1] - cs) / half!r}  rhs={8e-7 * (cs - ca)!r}")
