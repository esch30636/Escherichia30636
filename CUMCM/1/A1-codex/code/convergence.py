"""Run spatial and temporal refinements; report differences over ALL 37,800 points."""
import json
import numpy as np
from solver import save_run, ROOT

def difference(a,b):
    return {k:float(np.max(np.abs(a[k][1:]-b[k][1:]))) for k in ['T','C']}

def main():
    rows=[]
    old=None
    for n in [50,100,200,400,800,1600]:
        x=save_run(f'space_{n}',n=n,dt=.05,budget=0.)
        row={'study':'space','N':n,'dt':.05,'seconds':float(x['seconds'])}
        if old is not None: row.update(difference(x,old))
        rows.append(row);old=x
        print(row,flush=True)
    old=None
    for dt in [.2,.1,.05,.025]:
        x=save_run(f'time_{dt}',n=400,dt=dt,budget=0.)
        row={'study':'time','N':400,'dt':dt,'seconds':float(x['seconds'])}
        if old is not None: row.update(difference(x,old))
        rows.append(row);old=x
        print(row,flush=True)
    (ROOT/'verification/convergence.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')

if __name__=='__main__':main()
