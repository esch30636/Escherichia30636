"""All declared accuracy, mechanism and sensitivity cases."""
import argparse
from solve import solve
CASES=[
 ('base400',dict(n=400,rtol=1e-10)),
 ('base800',dict(n=800,rtol=1e-10)),
 ('tight800',dict(n=800,rtol=1e-11)),
 ('fine1600',dict(n=1600,rtol=1e-11)),
 ('radau400',dict(n=400,rtol=1e-10,method='Radau')),
 ('q3_regression800',dict(n=800,rtol=1e-11,shrink=False,appendix=3)),
 ('fixed4_800',dict(n=800,rtol=1e-11,shrink=False)),
 ('s_pchip',dict(n=400,rtol=1e-10,interp='pchip')),
 *[(f's_{s}',dict(n=400,rtol=1e-10,scenario=s)) for s in ('temp_low','temp_high','humid_low','humid_high')]]
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--recompute',action='store_true');a=p.parse_args()
 for name,kw in CASES: solve(name,**kw,recompute=a.recompute)
