"""Summarise the self-consistent reference run (uniform mesh, reviewed physics).

This run exists only to show that the reviewed closure is reproduced correctly by
an independent solver.  The physics variants explored during the review are
described in the report text and are not kept as data, because the quadratic
mesh's degenerate surface cell corrupts variant runs at coarse tolerances.

Writes verification/physics_comparison.json
"""
from pathlib import Path
import json, glob
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
A2 = ROOT.parent / "A2-gpt"
OUT = ROOT / "verification/physics_comparison.json"
R = 0.02
r_target = np.arange(21) / 1000.0


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
rep = {"note": ("独立求解器在均匀网格 n=200 上复现 A2-gpt 的水分边界闭合；仅用于确认其数值解"
                "可信，不作为修正方案的数值结论。"),
       "runs": [], "delivered": {
           "T_center": float(ref["T"][-1, 0]), "T_surface": float(ref["T"][-1, -1]),
           "C_center": float(ref["C"][-1, 0]), "C_surface": float(ref["C"][-1, -1]),
           "mean_T": float(ref["means"][-1, 0]), "mean_C": float(ref["means"][-1, 1])}}

for path in sorted(glob.glob(str(ROOT / "verification/uni_*_n200_p1.0.npz"))):
    z = np.load(path)
    meta = json.loads(str(z["meta"]))
    aud = z["audit"]; x = z["x"]; v = z["v"]; y = z["y10800"]
    got = interp_to(x, np.column_stack([y[0::2], y[1::2]]), r_target)
    water = float(np.trapezoid(2 * np.pi * R * aud[:, 2], aud[:, 0]))
    heat_in = float(-np.trapezoid(2 * np.pi * R * aud[:, 1], aud[:, 0]))
    rep["runs"].append(dict(
        id=Path(path).name, physics=meta["physics"], n=meta["n"],
        seconds=meta["seconds"],
        T_surface=float(got[-1, 0]), C_surface=float(got[20, 1]),
        C_at_1cm=float(got[10, 1]),
        mean_C=float((v @ y[1::2]) / v.sum()), mean_T=float((v @ y[0::2]) / v.sum()),
        max_dC_vs_delivered=float(np.max(np.abs(got[:, 1] - ref["C"][-1]))),
        max_dT_vs_delivered=float(np.max(np.abs(got[:, 0] - ref["T"][-1]))),
        water_loss_kg_per_m=water, convective_heat_in_J_per_m=heat_in,
    ))
OUT.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(rep, ensure_ascii=False, indent=2))
