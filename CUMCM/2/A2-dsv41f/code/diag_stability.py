"""Stress test of the reviewed discretisation's own robustness.

Uses the ORIGINAL A2-gpt solver module (no re-implementation) and asks whether
the quadratic-graded mesh stays stable when the time-step cap or tolerance is
loosened.  The delivered result was produced with rtol=1e-11 and max_step=10 s.

Run: python code/diag_stability.py [n] [end] [rtol] [max_step]
"""
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
A2 = Path(__file__).resolve().parents[2] / "A2-gpt"
sys.path.insert(0, str(A2 / "code"))
import solver as S                       # the reviewed module itself

env = np.loadtxt(A2 / "data/ambient.csv", delimiter=",", skiprows=1)


def run_case(n=400, end=600, rtol=1e-9, max_step=10.0, block=60):
    from scipy.integrate import solve_ivp
    x, v, g, half = S.mesh(n)
    air = lambda ts: np.stack([np.interp(ts, env[:, 0], env[:, i]) for i in (1, 2)], axis=-1)
    y = np.tile([28.0, 2.55], n)
    sp = S.sparsity(n)
    rows = []

    def rhs(t, yy):
        a = air(t)
        return S.kernel(yy, x, v, g, half, a[0], a[1], False, 25.0, 8e-7, 1.0)[0]

    for left in range(0, end, block):
        right = min(left + block, end)
        sol = solve_ivp(rhs, (left, right), y, method="BDF", rtol=rtol,
                        atol=np.tile([rtol * .1, rtol * .01], n),
                        jac_sparsity=sp, max_step=max_step, dense_output=True)
        y = sol.y[:, -1]
        rows.append((right, float(y[-2]), float(y[-1]), float(y[1::2].min()),
                     len(sol.t) - 1, int(sol.nfev)))
    return x, half, rows


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 600
    rtol = float(sys.argv[3]) if len(sys.argv) > 3 else 1e-9
    ms = float(sys.argv[4]) if len(sys.argv) > 4 else 10.0
    x, half, rows = run_case(n=n, end=end, rtol=rtol, max_step=ms)
    print(f"n={n} end={end} rtol={rtol} max_step={ms} half={half:.3e}")
    print(f"{'t':>7} {'T_lastcell':>12} {'C_lastcell':>12} {'minC':>12} "
          f"{'steps':>7} {'nfev':>8}")
    for right, tlast, clast, mn, st, nf in rows:
        print(f"{right:7d} {tlast:12.6f} {clast:12.6f} {mn:12.6f} {st:7d} {nf:8d}")
