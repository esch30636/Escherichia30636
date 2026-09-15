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
            for rho in ['dry0', 'unit']:
                specs.append(dict(name=f'lat_{mode}_{rho}', n=400,
                                  latent={'mode': mode, 'rho': rho, 'lv': 2.383e6},
                                  tmax_h=1200.0, sample_dt=3600.0, max_step=600.0))
    elif which == 'final':
        specs.append(dict(name='q4_tight800', n=800, tmax_h=70.0, sample_dt=60.0))
        specs.append(dict(name='q4_tight1600', n=1600, tmax_h=70.0, sample_dt=3600.0))
    elif which == 'audit':
        for name, n, sc, appx, dt, mesh in [
            ('q4_tight800',800,'final',4,60.,'graded'),
            ('q4_t50_tight800',800,'t50',4,60.,'graded'),
            ('q4_t50_tight1600',1600,'t50',4,3600.,'graded'),
            ('conv_graded400',400,'final',4,3600.,'graded'),
            ('conv_graded800',800,'final',4,3600.,'graded'),
            ('conv_graded1600',1600,'final',4,3600.,'graded'),
            ('conv_uniform400',400,'final',4,3600.,'uniform'),
            ('conv_uniform800',800,'final',4,3600.,'uniform'),
            ('q3_x800',800,'final',3,600.,'graded'),
            ('q3_x1600',1600,'final',3,3600.,'graded'),
            ('scen3_t50',400,'t50',3,3600.,'graded')]:
            specs.append(dict(name=name,n=n,scenario=sc,appx=appx,sample_dt=dt,mesh=mesh))
        for sc in ['final','last_hour_mean','last_hour_meanT_finalC','t50',
                   't50c05','stage_mean','last2h_mean']:
            specs.append(dict(name=f'scen_{sc}',n=400,scenario=sc,sample_dt=3600.))
        for mode in ['surf','vol']:
            for rho in ['dry0','unit']:
                specs.append(dict(name=f'lat_{mode}_{rho}',n=400,sample_dt=3600.,
                                  latent={'mode':mode,'rho':rho,'lv':2.383e6}))
        for appx in [3,4]:
            specs.append(dict(name=f'q{appx}_lat_surf_dry0_t50',n=400,scenario='t50',
                              appx=appx,sample_dt=3600.,
                              latent={'mode':'surf','rho':'dry0','lv':2.383e6}))
        specs.append(dict(name='q4_fixed_props_control',n=400,radius_mode='fixed',
                          sample_dt=3600.,tmax_h=240.))
    else:
        raise ValueError(which)
    print(f'[{which}] {len(specs)} cases on {nproc} workers', flush=True)
    failures = []
    with mp.Pool(nproc) as pool:
        for name, st, dt, ch, mh in pool.imap_unordered(task, specs):
            print(f'{name}: {st} {dt:.0f}s  crossing={ch} h minute={mh} h', flush=True)
            if st != 'OK':
                failures.append(name)
    if failures:
        raise RuntimeError(f'Failed cases: {failures}')


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('which', choices=['conv', 'scen', 'latent', 'final', 'audit'])
    p.add_argument('--nproc', type=int, default=8)
    a = p.parse_args()
    main(a.which, a.nproc)
