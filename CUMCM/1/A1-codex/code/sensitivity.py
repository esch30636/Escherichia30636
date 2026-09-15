"""Deterministic scenario analysis. +/-5% is a chosen perturbation, not measured uncertainty."""
import json
import numpy as np
from solver import ROOT,save_run

def main():
    base=save_run('sensitivity_base',n=400,dt=.025,budget=0.,power=2.)
    rows=[]
    cases=[('PCHIP',{'interpolation':'pchip'})]
    for key in ['h_factor','hm_factor','d_factor']:
        for factor in [.95,1.05]:cases.append((f'{key}_{factor}',{key:factor}))
    # Equilibrium-proxy sensitivity assessed with hm and D only; no invented sorption parameters.
    for name,args in cases:
        res=save_run('sensitivity_'+name,n=400,dt=.025,budget=0.,power=2.,**args)
        row={'case':name}
        for k in ['T','C']:
            row[k+'_max_abs_difference']=float(np.max(np.abs(res[k][1:]-base[k][1:])))
            row[k+'_center_1800_change']=float(res[k][-1,0]-base[k][-1,0])
            row[k+'_surface_1800_change']=float(res[k][-1,-1]-base[k][-1,-1])
        rows.append(row)
        print(row,flush=True)
    (ROOT/'verification/sensitivity.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')

if __name__=='__main__':main()
