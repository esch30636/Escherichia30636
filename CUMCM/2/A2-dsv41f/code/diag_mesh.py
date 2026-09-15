"""Diagnose the near-surface resolution problem of the quadratic mesh.

Checks, for the A2-gpt mesh family:
  * surface cell half-width delta for various n
  * surface-cell diffusive time constant delta^2/D
  * companion ODE stiffness ratio
and inspects the delivered solution for near-surface oscillation.
"""
from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
A2 = ROOT.parent / "A2-gpt"
R = 0.02


def mesh(n):
    faces = R * (1 - (1 - np.linspace(0, 1, n + 1)) ** 2)
    x = (faces[1:] + faces[:-1]) / 2
    da = np.diff(faces)
    return x, da


rows = []
for n in (200, 400, 800, 1600):
    x, da = mesh(n)
    d = R - x[-1]
    D0 = 2.4e-3 * np.exp(-0.45 / 2.55) * np.exp(-3850 / 301.15)
    rows.append(dict(n=n, last_cell_width_m=da[-1], half_cell_delta_m=d,
                     tau_surface_s=d * d / D0,
                     interior_cell_width_m=float(np.max(da)),
                     ratio_max_to_min=float(np.max(da) / np.min(da)),
                     cells_within_1mm=int(np.count_nonzero(R - x < 1e-3))))

# delivered solution behaviour near the surface
z = np.load(A2 / "data/full_precision.npz")
C = z["C"]; T = z["T"]
surf_cell = z["final_cells"][1::2]
x_m = z["x_m"]
n_out = C.shape[0]
# first 30 s of the reported surface history (from the sampled output)
head = C[:31, -1]
print("mesh table")
for r in rows:
    print("  n={n:5d}  last_cell={last_cell_width_m:.3e} m  delta={half_cell_delta_m:.3e} m"
          "  tau=delta^2/D={tau_surface_s:.3e} s  ratio={ratio_max_to_min:.3e}"
          "  cells<1mm={cells_within_1mm}".format(**r))

print("\ndelivered surface C, t=0..30 s:", np.array2string(head, precision=4))
print("delivered surface T, t=0..30 s:", np.array2string(T[:31, -1], precision=4))
print("delivered internal outer cells (final):",
      np.array2string(surf_cell[-6:], precision=6))
print("last internal cell centre x =", x_m[-1], " delta =", R - x_m[-1])

# oscillation detector on the delivered surface time series
d2 = np.diff(C[:, -1], 2)              # second difference
sign = np.sign(d2)
flips = np.count_nonzero(np.diff(sign) != 0)
print("\nsurface C second-difference sign flips:", flips, "of", d2.size)
print("surface C monotone decreasing overall:", bool(np.all(np.diff(C[:, -1]) <= 1e-12)),
      " min step:", float(np.min(np.diff(C[:, -1]))), " max step:", float(np.max(np.diff(C[:, -1]))))
amp = []
for j in range(1, 20):
    row = C[:, j * 1] if False else None
# oscillation scan across all radii
rep = {}
for j in range(21):
    y = C[:, j]
    d2 = np.diff(y, 2)
    rep[j] = int(np.count_nonzero(np.diff(np.sign(d2)) != 0))
print("sign flips of 2nd difference per radius 0..2 cm:", rep)

json.dump({"mesh": rows, "sign_flips": rep,
           "surface_head_C": head.tolist(), "surface_head_T": T[:31, -1].tolist()},
          open(ROOT / "verification/mesh_resolution.json", "w", encoding="utf-8"),
          indent=2)
