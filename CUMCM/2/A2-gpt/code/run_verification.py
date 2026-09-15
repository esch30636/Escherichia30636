"""Reproducible grid/time/method, Q1 regression and sensitivity runs."""
from solver import run
for n in (200,400,800):run(f'base{n}',n=n,rtol=1e-9)
run('tight800',n=800,rtol=1e-11)
run('tight1600',n=1600,rtol=1e-11)
run('radau800',n=800,rtol=1e-11,method='Radau')
run('q1_800',n=800,end=1800,rtol=1e-11,q1=True)
for key in ('hfactor','hmfactor','dfactor'):
    for value in (.95,1.05):run(f'{key}_{value}',n=400,rtol=1e-9,audit=False,**{key:value})
run('pchip400',n=400,rtol=1e-9,interp='pchip',audit=False)
