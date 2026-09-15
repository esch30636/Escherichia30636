import sys, json, time
sys.path.insert(0, r'D:/CUMCM/3/_verify/rt/engcode')
from drying_common.engine import solve
RUNS=[('plateau',1600,'base'),('base',400,'mean'),('nom',1600,'base')]
out={}
for v,n,sc in RUNS:
    t0=time.time()
    try:
        p=solve(f'D:/CUMCM/3/_verify/rt/{v}',3,f'q3_{sc}_n{n}',n=n,recompute=True,scenario=sc)
        d=json.loads(p.with_suffix('.json').read_text())
        k=f'{v}_{sc}_n{n}'
        out[k]=dict(tail=d['tail'],crossing_s=d['crossing_s'],minute_s=d['minute_s'],
                    crossing_h=d['crossing_s']/3600,secs=time.time()-t0)
        print('RESULT',k,json.dumps(out[k]),flush=True)
    except Exception as e: print('FAIL',v,n,sc,type(e).__name__,e,flush=True)
json.dump(out,open(r'D:/CUMCM/3/_verify/engine_conventions2.json','w'),indent=2)
print('ALLDONE',flush=True)
