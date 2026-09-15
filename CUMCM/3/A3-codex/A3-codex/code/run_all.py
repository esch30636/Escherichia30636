"""Reproduce calculations, evidence, figures, report and workbook.

Usage: python code/run_all.py [--recompute] [--math-only]
Existing results are reused only when their recorded solver/core/input hash matches.
"""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'verification'/'mpl-cache'))
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
from solve import solve

def fingerprint():
    h=hashlib.sha256()
    for p in [ROOT/'code/core.py',ROOT/'code/solve.py',ROOT/'data/ambient.csv']: h.update(p.read_bytes())
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--recompute',action='store_true');p.add_argument('--math-only',action='store_true')
    a=p.parse_args();stamp=fingerprint()
    jobs=[('base400',dict(n=400)),('base800',dict(n=800)),('tight800',dict(n=800,rtol=1e-11)),
          ('fine1600',dict(n=1600,rtol=1e-11)),('radau400',dict(n=400,method='Radau'))]
    jobs += [('s_'+s,dict(n=400,scenario=s)) for s in ['mean','temp_low','temp_high','humid_low','humid_high']]
    for name,kw in jobs:
        config=ROOT/'verification'/f'{name}.stamp.json'
        valid=config.exists() and json.loads(config.read_text())==dict(hash=stamp,kwargs=kw)
        if a.recompute or not valid or not (ROOT/'verification'/f'{name}.npz').exists():
            solve(name,**kw);config.write_text(json.dumps(dict(hash=stamp,kwargs=kw)))
        else: print('Reusing',name,flush=True)
    subprocess.run([sys.executable,str(ROOT/'code/produce.py')],check=True)
    if not a.math_only:
        deps=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies'
        node=Path(os.environ.get('A3_NODE',str(deps/'node/bin/node')))
        modules=Path(os.environ.get('A3_NODE_MODULES',str(deps/'node/node_modules')))
        link=ROOT/'code/node_modules'
        if not link.exists(): link.symlink_to(modules,target_is_directory=True)
        subprocess.run([str(node),str(ROOT/'code/build_workbook.mjs')],check=True)
        subprocess.run([sys.executable,str(ROOT/'code/check_workbook.py')],check=True)

if __name__=='__main__': main()
