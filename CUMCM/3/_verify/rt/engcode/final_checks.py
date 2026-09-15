"""Final, read-only acceptance checks for the coordinated A3/A4 delivery."""
from pathlib import Path
import hashlib, json
import numpy as np

HERE = Path(__file__).resolve()
WORKSPACE = HERE.parents[3]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check(q):
    root = WORKSPACE / f"A{q}/A{q}-codex"
    s = json.loads((root / "verification/summary.json").read_text())
    with np.load(root / "data/full_precision.npz") as d:
        times = d["time_s"]
        assert times[0] == 0 and np.all(np.diff(times) == 60)
        shape_C = list(d["C"].shape)
        assert shape_C[1] == (21 if q == 3 else 22)
        assert d["maxC"][-2] >= .15 and d["maxC"][-1] < .15
        assert np.all(d["maxC"][:-1] >= .15)
        if q == 4:
            outside = d["distance_cm"][None, :] > d["radius_m"][:, None] * 100 + 1e-10
            assert np.array_equal(np.isnan(d["C"][:, :21]), outside)
    old = Path(json.loads((root / "archive/latest.json").read_text())["path"])
    assert sha(root / "建模报告_6astra原稿.md") == sha(old / "建模报告.md")
    source = json.loads((root / "data/source_sha256.json").read_text())
    original = {p: h for p, h in source.items() if p.startswith("CUMCM2026Problems/")}
    assert original and all(sha(WORKSPACE / p) == h for p, h in original.items())
    assert "潜热" in (root / "建模报告.md").read_text() and "不计算" in (root / "建模报告.md").read_text()
    result = {
        "passed": bool(s["passed"]),
        "question": q,
        "main_name": s["main_name"],
        "crossing_s": s["main"]["crossing_s"],
        "minute_s": float(times[-1]),
        "C_error_estimate": s["C_error_estimate"],
        "time_error_estimate_s": s["time_error_estimate_s"],
        "shape_C": shape_C,
        "original_problem_files_unchanged": True,
        "six_astra_report_preserved": True,
        "latent_heat_calculation": False,
    }
    assert result["passed"] and result["C_error_estimate"] <= 1e-6 and result["time_error_estimate_s"] <= 1
    (root / "verification/final_checks.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    return result

if __name__ == "__main__":
    print(json.dumps([check(3), check(4)], ensure_ascii=False, indent=2))
