"""Consolidate every verified number quoted in the review report into one file.

Run: python code/make_summary.py
Writes: verification/00_审核结论汇总.json
"""
from pathlib import Path
import hashlib, json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
A2 = ROOT.parent / "A2-gpt"
R = 0.02
LV0, LV_SLOPE = 2.501e6, 2.361e3
RHO_D = (650.0 + 128.0 * 2.55) / (1.0 + 2.55)


def load(p):
    raw = Path(p).read_bytes()
    for enc in ("utf-8", "gbk", "cp936", "latin-1"):
        try:
            return json.loads(raw.decode(enc))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    raise ValueError(f"cannot decode {p}")


rep = {"审核对象": "A2/A2-gpt", "审核方": "A2/A2-dsv41f"}

# ---- 1. deliverable format -------------------------------------------------
aud = load(ROOT / "verification/workbook_audit.json")
rep["1_交付格式_通过"] = {
    "工作表名一致": aud["sheetnames"]["match"],
    "时间轴": aud["time_index"],
    "半径轴": {"模板骨架一致(0/0.1/0.2/2)": aud["radius_axis_skeleton_match"],
             "步长恒为0.1": aud["radius_axis_step_uniform"],
             "端点0与2": aud["radius_axis_endpoints_ok"]},
    "与四位小数逐格一致": aud["delivered_vs_fullprecision"],
    "报告表3表4与工作簿最大差": aud["report_tables_max_abs_diff"],
    "场量合理性": aud["field_plausibility"],
}

# ---- 2. reproducibility and self-consistency ------------------------------
rep["2_可复现与自身一致_通过"] = {
    "用原始模块重算10800s": {
        "设置": "N=800, BDF, rtol=1e-11, max_step=10s, 每60s重启（与交付完全相同）",
        "重算步数": 18823, "交付步数": 18820,
        "全场最大差": 7.359802e-11,
        "脚本": "code/reproduce_reference.py",
    },
    "表面节点热平衡": {
        "N200": {"half_m": 2.5e-07, "T_node_C": 35.412955181,
                 "T_surface_C": 35.413040561, "balance_Ts_C": 35.413040561,
                 "残差_W_m2": 7.2e-09},
        "N400": {"half_m": 6.25e-08, "T_node_C": 35.413003865,
                 "T_surface_C": 35.413025210, "balance_Ts_C": 35.413025210,
                 "残差_W_m2": 6.1e-09},
        "脚本": "code/audit_surface_node.py",
        "结论": "表面重构完全自洽",
    },
    "审核方更正记录": ("一度误判表面节点违反自身热平衡（残差 6e6 W/m²），实为审核方推理错误，"
                    "已用原始模块复算更正；相关结论已删除"),
}

# ---- 3. numerical accuracy, independent solver -----------------------------
cmpf = load(ROOT / "verification/independent_comparison.json")
rep["3_数值精度独立复算_通过"] = {
    "交付解自报误差": {"T_C": 4.806094158501158e-06, "C_kgkg": 2.749998253707512e-06},
    "独立解与交付解最大差": {c["id"]: {"max_dT": c["max_dT"], "max_dC": c["max_dC"]}
                             for c in cmpf["comparisons"]},
    "观测阶": "均匀族 100→200 阶≈1；半聚簇族 100→200 阶≈2；两族外推极限与交付解之差 <1e-5",
    "独立复现作者闭合": {"网格": "均匀 N=200", "max_dT_C": 1.74e-06, "max_dC_kgkg": 1.94e-06},
    "结论": ("在已实现的方程与边界闭合下，交付数值解可信；误差估计方法用法正确。"
             "该结论不覆盖下述物理缺失。"),
}

# ---- 4. P0: energy budget --------------------------------------------------
ea = load(ROOT / "verification/energy_audit.json")
rep["4_P0_失水量超出可供能量"] = {
    "核算输入": "仅用交付的 T/C/means 数组与题给 h=25 W/(m2 K)，不含审核方模型",
    "表面环境温差最大_K": ea["surface_ambient_gap_max_K"],
    "3h进入药材的能量_J_per_m": ea["heat_net_into_rod_J_per_m"],
    "其中显热升温_J_per_m": ea["sensible_heat_stored_J_per_m"],
    "留给相变的能量_J_per_m": ea["energy_available_for_latent_net_J_per_m"],
    "交付排出水量_kg_per_m": ea["water_removed_delivered_kg_per_m"],
    "蒸发所需潜热_J_per_m": ea["latent_heat_required_J_per_m"],
    "潜热比可供相变能量": ea["deficit_factor_net"],
    "潜热比进入药材总能量": ea["latent_heat_required_J_per_m"] / ea["heat_net_into_rod_J_per_m"],
    "能量允许的最大失水_kg_per_m": ea["max_water_evaporable_net_kg_per_m"],
    "能量允许的最大平均降湿_kg_per_kg": ea["max_mean_dC_from_energy_net_kg_per_kg"],
    "交付的平均降湿_kg_per_kg": ea["mean_dC_delivered_kg_per_kg"],
    "原因": "表面热边界只有 -k dT/dr|R = h(Ts-Ta)，缺蒸发潜热汇 L_v*j",
    "脚本": "code/audit_energy.py",
}

# ---- 5. P1: moisture BC dimension -----------------------------------------
cc = load(ROOT / "verification/conservation_check.json")
rep["5_P1_水分边界量纲"] = {
    "rho_d_kg_m3": cc["rho_d_kg_m3"],
    "体积平均失水_kg_per_m": cc["volume_mean_loss_kg_per_m"],
    "代码通量公式积分_kg_per_m": cc["coded_flux_integral_kg_per_m"],
    "比值": cc["ratio_volume_over_coded"],
    "补rho_d后比值": cc["ratio_volume_over_corrected"],
    "释义": ("比值恰为 rho_d：离散格式排出的水量等于带 rho_d 的正确公式，"
             "而代码写下的 h_m(Cs-Ca) 量纲不成立（m/s 乘 kg/kg）"),
    "气侧上限对照": {"3h积分_kg_per_m": 2.7503516661733227e-05,
                 "与交付失水之比": cc["volume_mean_loss_kg_per_m"] / 2.7503516661733227e-05},
    "脚本": "code/audit_conservation.py",
}

# ---- 6. mesh robustness ----------------------------------------------------
mr = load(ROOT / "verification/mesh_resolution.json")
rep["6_网格鲁棒性"] = {
    "二次聚簇网格最外单元": mr["mesh"],
    "实测": {"n400_rtol1e-9": "最外单元含水率 60 s 内崩到 0.092，此后全场失真",
           "n800_rtol1e-9": "崩到 0.078",
           "n800_rtol1e-11": "稳定，且可被逐位复现（交付设置）"},
    "脚本": "code/diag_mesh.py, code/diag_stability.py",
}

# ---- 7. inputs -------------------------------------------------------------
man = load(A2 / "data/source_sha256.json")
rep["7_输入哈希"] = {p: bool((ROOT.parents[1] / p).exists())
                  and hashlib.sha256((ROOT.parents[1] / p).read_bytes()).hexdigest() == v
                  for p, v in man.items()}

(ROOT / "verification/00_审核结论汇总.json").write_text(
    json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(rep, ensure_ascii=False, indent=2))
