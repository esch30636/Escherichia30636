import sys, json, time
sys.path.insert(0, r'D:/CUMCM/3/_verify/rt/engcode')
from drying_common.engine import solve
t0=time.time()
p=solve('D:/CUMCM/3/_verify/rt/base',3,'q3_ref6400',n=6400,recompute=True)
d=json.loads(p.with_suffix('.json').read_text())
print('REF6400', d['crossing_s'], d['crossing_s']/3600, d['minute_s'], '%.0fs'%(time.time()-t0), flush=True)
