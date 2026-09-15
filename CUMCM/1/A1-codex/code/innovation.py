"""Isolate spatial-flux differences with the SAME independently implemented BDF integrator."""
import numpy as np
import os
from benchmarks import harmonic_reference
from solver import ROOT

if __name__=='__main__':
    for n in [100,200,400,800,1600]:
        for method in ['kirchhoff','harmonic']:
            p=ROOT/'verification'/f'bdf_{method}_{n}.npz'
            if p.exists() and os.environ.get('A1_RECOMPUTE')!='1':continue
            arr,sec=harmonic_reference(n=n,method=method)
            np.savez_compressed(p,C=arr,seconds=sec)
            print(method,n,sec,arr[-1,[0,-1]],flush=True)
    arr,sec=harmonic_reference(n=800,method='kirchhoff',rtol=2e-11,atol=2e-13)
    np.savez_compressed(ROOT/'verification/bdf_kirchhoff_800_tight.npz',C=arr,seconds=sec)
    for n in [100,200,400,800,1600]:
        p=ROOT/'verification'/f'bdf_uniform_{n}.npz'
        if p.exists() and os.environ.get('A1_RECOMPUTE')!='1':continue
        arr,sec=harmonic_reference(n=n,method='kirchhoff',power=1.)
        np.savez_compressed(p,C=arr,seconds=sec)
        print('uniform',n,sec,flush=True)
