"""Diagnose where the independent solve and A2-gpt differ in space and time."""
from pathlib import Path
import json, sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
A2 = ROOT.parent / "A2-gpt"


def interp_to(x, y2, r_target):
    t = y2[:, 0]; c = y2[:, 1]; n = x.size
    out = np.empty((r_target.size, 2))
    for j, z in enumerate(r_target):
        if z <= x[0]:
            zz = np.array([-x[1], x[0], x[1]]); dd = np.array([t[1], t[0], t[1]])
            dc = np.array([c[1], c[0], c[1]])
        elif z >= x[-1]:
            i = n - 2; zz = x[i - 1:i + 2]; dd = t[i - 1:i + 2]; dc = c[i - 1:i + 2]
        else:
            i = int(np.clip(np.searchsorted(x, z), 1, n - 2))
            zz = x[i - 1:i + 2]; dd = t[i - 1:i + 2]; dc = c[i - 1:i + 2]
        w = np.array([(z - zz[1]) * (z - zz[2]) / ((zz[0] - zz[1]) * (zz[0] - zz[2])),
                      (z - zz[0]) * (z - zz[2]) / ((zz[1] - zz[0]) * (zz[1] - zz[2])),
                      (z - zz[0]) * (z - zz[1]) / ((zz[2] - zz[0]) * (zz[2] - zz[1]))])
        out[j] = [w @ dd, w @ dc]
    return out


ref = np.load(A2 / "data/full_precision.npz")
r = ref["radius_cm"] / 100.0
for p in sys.argv[1:]:
    z = np.load(p)
    x = z["x"]; meta = json.loads(str(z["meta"]))
    snaps = sorted(int(k[1:]) for k in z.files if k.startswith("y"))
    print(f"\n=== {Path(p).name}  n={meta['n']} p={meta['p']} ===")
    for tt in snaps:
        y = z[f"y{tt}"]
        got = interp_to(x, np.column_stack([y[0::2], y[1::2]]), r)
        dT = got[:, 0] - ref["T"][tt]
        dC = got[:, 1] - ref["C"][tt]
        jT = int(np.argmax(np.abs(dT))); jC = int(np.argmax(np.abs(dC)))
        print(f" t={tt:6d}  maxdT {np.abs(dT).max():.3e} @ r={r[jT]*100:.1f}cm"
              f"   maxdC {np.abs(dC).max():.3e} @ r={r[jC]*100:.1f}cm"
              f"   rmsdT {np.sqrt((dT**2).mean()):.2e} rmsdC {np.sqrt((dC**2).mean()):.2e}")
    # spatial error profile at the last snapshot
    y = z[f"y{snaps[-1]}"]
    got = interp_to(x, np.column_stack([y[0::2], y[1::2]]), r)
    print(" final dC per radius:", np.array2string(got[:, 1] - ref["C"][snaps[-1]],
                                                   precision=2, floatmode="fixed", max_line_width=200))
    print(" final dT per radius:", np.array2string(got[:, 0] - ref["T"][snaps[-1]],
                                                   precision=2, floatmode="fixed", max_line_width=200))
