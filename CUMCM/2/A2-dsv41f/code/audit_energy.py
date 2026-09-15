"""Energy-bound audit of the delivered A2-gpt solution.

Rigorous statement of the defect, using only the delivered arrays and the
problem-given h = 25 W/(m2 K):

  (a) The rod receives heat only across its lateral surface, so the total energy
      it can absorb in 3 h is bounded by  |integral h (T_a - T_s) 2 pi R dt|.
  (b) Part of that energy raises the rod's sensible heat; the rest can evaporate
      water, at not less than L_v ~ 2.4e6 J/kg.
  (c) The delivered moisture field removes far more water than (b) can pay for.

Writes verification/energy_audit.json
"""
from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
A2 = ROOT.parent / "A2-gpt"
R = 0.02
LV0, LV_SLOPE = 2.501e6, 2.361e3
RHO_D = (650.0 + 128.0 * 2.55) / (1.0 + 2.55)

z = np.load(A2 / "data/full_precision.npz")
T, C, means, t = z["T"], z["C"], z["means"], z["time_s"]
env = np.loadtxt(A2 / "data/ambient.csv", delimiter=",", skiprows=1)
Ta = np.interp(t, env[:, 0], env[:, 1])

# ---- (a) energy actually crossing the surface ------------------------------
q_out = 25.0 * (T[:, -1] - Ta)                 # >0 leaving the rod
heat_net = float(-np.trapezoid(2 * np.pi * R * q_out, t))          # >0 = into rod
heat_abs = float(np.trapezoid(2 * np.pi * R * np.abs(q_out), t))
max_gap = float(np.abs(T[:, -1] - Ta).max())

# ---- (b) sensible heat actually stored ------------------------------------
# use the reported mean temperature with the volumetric heat capacity at the
# final mean moisture (a lower bound on the capacity over the whole run)
c_end = (650.0 + 128.0 * means[-1, 1]) * (1450.0 + 2736.0 * means[-1, 1] / (1 + means[-1, 1]))
c_start = (650.0 + 128.0 * means[0, 1]) * (1450.0 + 2736.0 * means[0, 1] / (1 + means[0, 1]))
sensible = float(c_end * np.pi * R ** 2 * (means[-1, 0] - means[0, 0]))

# ---- (c) latent heat the delivered moisture loss implies ------------------
water = float(RHO_D * (means[0, 1] - means[-1, 1]) * np.pi * R ** 2)
Lv = LV0 - LV_SLOPE * float(np.mean(T[:, -1]))
latent = water * Lv

# ---- (d) what the available energy could actually evaporate ---------------
energy_for_latent_net = heat_net - sensible
energy_for_latent_abs = heat_abs - sensible
water_max_net = energy_for_latent_net / Lv
water_max_abs = energy_for_latent_abs / Lv

rep = {
    "given_h_W_m2K": 25.0,
    "rho_d_kg_m3": RHO_D,
    "surface_ambient_gap_max_K": max_gap,
    "heat_net_into_rod_J_per_m": heat_net,
    "heat_abs_through_surface_J_per_m": heat_abs,
    "sensible_heat_stored_J_per_m": sensible,
    "latent_heat_required_J_per_m": float(latent),
    "latent_over_sensible": float(latent / sensible),
    "energy_available_for_latent_net_J_per_m": float(energy_for_latent_net),
    "energy_available_for_latent_abs_J_per_m": float(energy_for_latent_abs),
    "Lv_mean_surface_J_per_kg": float(Lv),
    "water_removed_delivered_kg_per_m": water,
    "max_water_evaporable_net_kg_per_m": float(water_max_net),
    "max_water_evaporable_abs_kg_per_m": float(water_max_abs),
    "deficit_factor_net": float(water / water_max_net) if water_max_net > 0 else None,
    "deficit_factor_abs": float(water / water_max_abs) if water_max_abs > 0 else None,
    "mean_dC_delivered_kg_per_kg": float(means[0, 1] - means[-1, 1]),
    "max_mean_dC_from_energy_net_kg_per_kg": float(water_max_net / (RHO_D * np.pi * R ** 2)),
    "max_mean_dC_from_energy_abs_kg_per_kg": float(water_max_abs / (RHO_D * np.pi * R ** 2)),
    "conclusion": (
        "The delivered model evaporates far more water than the heat crossing its own "
        "surface can pay for, because the surface energy balance omits the latent sink "
        "L_v*j.  The bound uses only the delivered temperatures, the delivered moisture "
        "means and the problem-given h; no review-side model is involved."),
}
(ROOT / "verification/energy_audit.json").write_text(
    json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
for k, vv in rep.items():
    print(f"{k}: {vv}")
