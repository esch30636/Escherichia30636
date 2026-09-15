import numpy as np, json, sys
sys.path.insert(0,"code")
from mol_solver import MOL
env=np.loadtxt(r"E:\HUST\国赛\A1-codex\data\ambient.csv",delimiter=",",skiprows=1)
Lv=2.45e6; h=25.0
m0=MOL(400,False,env); h0,_=m0.run(end=1800)
Ts0, Tc0 = h0[-1,-1], h0[-1,0]
Ta1800=float(np.interp(1800.,env[:,0],env[:,1]))
J=1.49e-6
dT=Ts0-Ta1800
out=dict(no_latent=dict(Ts=Ts0,Tc=Tc0,Ta=Ta1800,dTsurf=dT))
for Lv_ in [2.45e6]:
    hf=1.0-Lv_*J/(h*abs(dT))
    m=MOL(400,False,env,h_factor=hf); h,_=m.run(end=1800)
    out[f"latent_Lv{Lv_:.2e}"]=dict(h_factor=hf,latent_W_m2=Lv_*J,Ts=h[-1,-1],Tc=h[-1,0],
                                   dTs=h[-1,-1]-Ts0,dTc=h[-1,0]-Tc0)
    print(json.dumps(out,indent=2))
json.dump(out,open("verification/latent_heat.json","w"),indent=2)
