# -*- coding: utf-8 -*-
"""Q4 deep-solve batch: grid convergence, chamber-convention hunt, latent
variants, Q3 cross-check. Multiprocessing; one JSON+NPZ per case in out/.
"""
import sys, io, os, json, time, traceback
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
import numpy as np
import multiprocessing as mp
import a4_run
from a4_run import solve_case

OUT = a4_run.OUT


def task(spec):
    name = spec.pop('name')
    t0 = time.perf_counter()
    try:
        res = solve_case(name, save=True, **spec)
        return (name, 'OK', time.perf_counter() - t0,
                res.get('crossing_h'), res.get('minute_h'))
    except Exception as e:
        traceback.print_exc()
        return (name, 'FAIL', time.perf_counter() - t0, str(e)[:200], None)


def main(which, nproc=8):
    specs = []
    if which == 'conv':
        for n, mesh in [(400, 'graded'), (800, 'graded'), (1600, 'graded'),
                        (400, 'uniform'), (800, 'uniform')]:
            specs.append(dict(name=f'conv_{mesh}{n}', n=n, mesh=mesh,
                              tmax_h=70.0, sample_dt=3600.0))
        specs.append(dict(name='q3_x800', n=800, appx=3, tmax_h=80.0, sample_dt=3600.0))
        specs.append(dict(name='q3_x1600', n=1600, appx=3, tmax_h=80.0, sample_dt=3600.0))
    elif which == 'scen':
        for sc in ['final', 'stage_mean', 'last2h_mean', 'last_hour_mean', 't50',
                   't50c05', 'last_hour_meanT_finalC', 'finalT_meanc', 'smooth11']:
            specs.append(dict(name=f'scen_{sc}', n=400, scenario=sc,
                              tmax_h=80.0, sample_dt=3600.0))
            specs.append(dict(name=f'scen3_{sc}', n=400, scenario=sc, appx=3,
                              tmax_h=90.0, sample_dt=3600.0))
    elif which == 'latent':
        for mode in ['vol', 'surf']:
            for rho in ['dry0', 'dry', 'bulk', 'unit']:
                specs.append(dict(name=f'lat_{mode}_{rho}', n=400,
                                  latent={'mode': mode, 'rho': rho, 'lv': 2.383e6},
                                  tmax_h=1200.0, sample_dt=3600.0, max_step=600.0))
    elif which == 'final':
        specs.append(dict(name='q4_tight800', n=800, tmax_h=70.0, sample_dt=60.0))
        specs.append(dict(name='q4_tight1600', n=1600, tmax_h=70.0, sample_dt=3600.0))
    else:
        raise ValueError(which)
    print(f'[{which}] {len(specs)} cases on {nproc} workers', flush=True)
    with mp.Pool(nproc) as pool:
        for name, st, dt, ch, mh in pool.imap_unordered(task, specs):
            print(f'{name}: {st} {dt:.0f}s  crossing={ch} h minute={mh} h', flush=True)


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('which', choices=['conv', 'scen', 'latent', 'final'])
    p.add_argument('--nproc', type=int, default=8)
    a = p.parse_args()
    main(a.which, a.nproc)
