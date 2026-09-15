import numpy as np, json, sys
sys.path.insert(0,"code")
from mol_solver import MOL, R, RHO, CP, K, H, HM, T0, C0, D0
env=np.loadtxt(r"E:\HUST\国赛\A1-codex\data\ambient.csv",delimiter=",",skiprows=1)
D0_,DECAY=7e-9,0.89
Ca=0.03307
print("closure sensitivity with the model-consistent half-cell relation:")
out={}
for d in [0.0,0.02,0.05,0.10]:
    row={}
    for t,cN,delta in [(900,1.754715,0.000625),(1800,1.510243,0.000625)]:
        dN=D0_*np.exp(-DECAY/cN)
        cs=(dN*cN+delta*HM*(Ca+d))/(dN+delta*HM)
        row[f"t={t}"]=cs
    out[f"C_e=C_a+{d:.2f}"]=row
    print(f"  C_e=C_a+{d:.2f}: t900={row['t=900']:.5f} t1800={row['t=1800']:.5f}")
print()
print("latent-heat scenario (temperature, exact modal reference scale):")
m0=MOL(400,False,env); h0,_=m0.run(end=1800)
print("   no latent heat: T_surface=%.4f T_centre=%.4f"%(h0[-1,-1],h0[-1,0]))
for hf in [0.7,0.5,0.4,0.3]:
    m=MOL(400,False,env,h_factor=hf); h,_=m.run(end=1800)
    print(f"   h_factor={hf}: T_surface={h[-1,-1]:.4f} (dT={h[-1,-1]-h0[-1,-1]:+.4f}) T_centre={h[-1,0]:.4f} (dT={h[-1,0]-h0[-1,0]:+.4f})")
json.dump({"closure":out},open("verification/closure_final.json","w"),indent=2)
