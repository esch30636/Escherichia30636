import json
from solver import save_run,ROOT
from convergence import difference

rows=[]
old=None
for n in [50,100,200,400,800,1600]:
    x=save_run(f'graded_{n}',n=n,dt=.05,budget=0.,power=2.)
    row={'study':'graded','N':n,'dt':.05,'seconds':float(x['seconds'])}
    if old is not None:row.update(difference(x,old))
    rows.append(row);old=x
    print(row,flush=True)
(ROOT/'verification/graded_convergence.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
for b in [2e-4,1e-4,5e-5]:
    x=save_run(f'adaptive_{b}',n=800,dt=1.,budget=b,power=2.)
