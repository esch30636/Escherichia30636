"""Mass-conservation and flux-formula audit of the delivered solution.

The reviewed semi-discrete scheme is
    V_i dC_i/dt = F^C_{i-1/2} - F^C_{i+1/2},   F^C_R = 2 R h_m (C_s - C_a),
so the volume-weighted water loss over 3 h must equal the time integral of the
surface flux.  This script evaluates both from the delivered output and shows
that the coded flux formula is short by exactly the dry-basis density rho_d.

Writes verification/conservation_check.json
"""
from pathlib import Path
import sys, json
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model_ref import R, RHO_D, load_delivered, load_ambient, properties

ROOT = Path(__file__).resolve().parents[1]
rep = {}

z = load_delivered()
T, C, means, t = z["T"], z["C"], z["means"], z["time_s"]
env = load_ambient()
Ta = np.interp(t, env[:, 0], env[:, 1])
Ca = np.interp(t, env[:, 0], env[:, 2])

# --- water removed, from the volumetric mean --------------------------------
loss_vol = RHO_D * (means[0, 1] - means[-1, 1]) * np.pi * R ** 2
# --- water the coded flux formula can account for ---------------------------
j_code = 8e-7 * (C[:, -1] - Ca)
loss_flux = float(np.trapezoid(2 * np.pi * R * j_code, t))
loss_flux_rho = float(np.trapezoid(2 * np.pi * R * RHO_D * j_code, t))

rep["rho_d_kg_m3"] = RHO_D
rep["volume_mean_loss_kg_per_m"] = float(loss_vol)
rep["coded_flux_integral_kg_per_m"] = loss_flux
rep["ratio_volume_over_coded"] = float(loss_vol / loss_flux)
rep["rho_d_corrected_flux_integral_kg_per_m"] = loss_flux_rho
rep["ratio_volume_over_corrected"] = float(loss_vol / loss_flux_rho)
rep["dCbar_dt_final"] = float(np.gradient(means[:, 1], t)[-1])
rep["surface_dCdr_reported_per_m"] = float(np.gradient(C[-1], z["radius_cm"] / 100.0)[-1])
rep["D_at_surface_m2_s"] = float(properties(T[-1, -1], C[-1, -1])[2])
rep["km_relation_gas_side"] = ("j = h_m rho_a (Y_sat(T_s) - Y_a) is the "
                               "dimensionally consistent alternative")
rep["conclusion"] = ("the volumetric water loss equals the surface-flux integral only when the "
                     "flux carries rho_d = 275.04 kg/m3; as coded it is short by exactly rho_d")

(ROOT / "verification/conservation_check.json").write_text(
    json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(rep, ensure_ascii=False, indent=2))
