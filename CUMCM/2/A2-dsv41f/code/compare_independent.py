"""Compare the independent re-solve with the A2-gpt delivered field.

* loads A2-gpt/data/full_precision.npz  (delivered 800-cell BDF solution)
* loads verification/indep_*.npz        (this pack's Radau solutions)
* interpolates the independent cell-centre values onto the 21 reporting radii
  with local quadratic (or linear at the boundary end) interpolation
* reports max/RMS differences and the implied observed order

Writes verification/independent_comparison.json
"""
from pathlib import Path
import json, sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
A2 = ROOT.parent / "A2-gpt"
OUT = ROOT / "verification/independent_comparison.json"


def load_indep(path):
    z = np.load(path, allow_pickle=False)
    meta = json.loads(str(z["meta"]))
    x = z["x"]
    snaps = {int(k[1:]): z[k] for k in z.files if k.startswith("y")}
    return x, snaps, meta


def interp_to(x, y2, r_target):
    """y2 is (n,2) cell-centre states -> values at r_target (21,)."""
    t = y2[:, 0]; c = y2[:, 1]
    n = x.size
    out = np.empty((r_target.size, 2))
    for j, z in enumerate(r_target):
        if z <= x[0]:                      # centre: even function of r
            zz = np.array([-x[1], x[0], x[1]])
            dd = np.array([t[1], t[0], t[1]])
            dc = np.array([c[1], c[0], c[1]])
        elif z >= x[-1]:
            i = n - 2
            zz = x[i - 1:i + 2]
            dd = t[i - 1:i + 2]; dc = c[i - 1:i + 2]
        else:
            i = int(np.clip(np.searchsorted(x, z), 1, n - 2))
            zz = x[i - 1:i + 2]
            dd = t[i - 1:i + 2]; dc = c[i - 1:i + 2]
        w = np.array([(z - zz[1]) * (z - zz[2]) / ((zz[0] - zz[1]) * (zz[0] - zz[2])),
                      (z - zz[0]) * (z - zz[2]) / ((zz[1] - zz[0]) * (zz[1] - zz[2])),
                      (z - zz[0]) * (z - zz[1]) / ((zz[2] - zz[0]) * (zz[2] - zz[1]))])
        out[j] = [w @ dd, w @ dc]
    return out


def main(paths):
    ref = np.load(A2 / "data/full_precision.npz")
    r_target = ref["radius_cm"] / 100.0
    times = [int(k) for k in ref.files if k.startswith("y")] if False else None
    report = {"reference": {"n": 800, "rtol": 1e-11, "method": "BDF"},
              "comparisons": [], "orders": []}
    series = {}
    for p in paths:
        x, snaps, meta = load_indep(p)
        diffs = []
        for tt, y in sorted(snaps.items()):
            ref_T = ref["T"][tt] if tt <= ref["T"].shape[0] - 1 else None
            ref_C = ref["C"][tt] if tt <= ref["C"].shape[0] - 1 else None
            got = interp_to(x, np.column_stack([y[0::2], y[1::2]]), r_target)
            diffs.append([tt, float(np.max(np.abs(got[:, 0] - ref_T))),
                          float(np.max(np.abs(got[:, 1] - ref_C)))])
        key = f"n{meta['n']}_p{meta['p']}"
        series[key] = dict(meta=meta, diffs=diffs)
        report["comparisons"].append({
            "id": key, "n": meta["n"], "p": meta["p"], "rtol": meta["rtol"],
            "method": meta["method"], "steps": meta["steps"],
            "seconds": round(meta["seconds"], 2), "min_C": meta["mass_check"],
            "max_dT": max(d[1] for d in diffs),
            "max_dC": max(d[2] for d in diffs),
            "dT_final": diffs[-1][1], "dC_final": diffs[-1][2],
        })
    # observed order between uniform meshes, if at least two are present
    uni = sorted([c for c in report["comparisons"] if c["p"] == 1.0],
                 key=lambda c: c["n"])
    for a, b in zip(uni, uni[1:]):
        if b["max_dT"] > 0 and a["max_dT"] > 0:
            report["orders"].append({
                "pair": [a["id"], b["id"]],
                "order_T": float(np.log(a["max_dT"] / b["max_dT"]) / np.log(b["n"] / a["n"])),
                "order_C": float(np.log(a["max_dC"] / b["max_dC"]) / np.log(b["n"] / a["n"])),
            })
    report["series"] = series
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("comparisons", "orders")},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(sys.argv[1:])
