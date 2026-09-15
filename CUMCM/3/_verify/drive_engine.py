"""Drive the candidates' OWN engine (A3-codex(1) copy) with different ambient-tail
conventions. Any difference is attributable to the convention alone."""
import sys, json, time, numpy as np
sys.path.insert(0, r'D:/CUMCM/3/_verify/rt/engcode')
sys.path.insert(0, r'D:/CUMCM/3/_verify/rt/engcode/drying_common')
from drying_common.engine import solve

RUNS = [('base',400), ('nom',400), ('plateau',400), ('base',1600)]
out = {}
for v, n in RUNS:
    root = f'D:/CUMCM/3/_verify/rt/{v}'
    name = f'q3_n{n}'
    t0 = time.time()
    try:
        p = solve(root, 3, name, n=n, recompute=True)
        d = json.loads(p.with_suffix('.json').read_text())
        key = f'{v}_n{n}'
        out[key] = dict(tail=d['tail'], crossing_s=d['crossing_s'], minute_s=d['minute_s'],
                        crossing_h=d['crossing_s']/3600 if d['crossing_s'] else None,
                        secs=time.time()-t0)
        print('RESULT', key, json.dumps(out[key]), flush=True)
    except Exception as e:
        print('FAIL', v, n, type(e).__name__, e, flush=True)
json.dump(out, open(r'D:/CUMCM/3/_verify/engine_conventions.json','w'), indent=2)
print('ALLDONE', flush=True)
