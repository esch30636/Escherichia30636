# -*- coding: utf-8 -*-
"""Server-side audit driver.

(1) Method C : cell-vertex conservative FV convergence (independent discretization)
(2) Dirichlet-surface variant: pin C(R,t) = C_air(t) to test the A3-ds hypothesis
    that eliminating the convective surface resistance reproduces ~53 h.
(3) Method D : 2D axisymmetric (r,z) to size the axial end-cap effect.
"""
import sys, time
import numpy as np
from scipy.integrate import solve_ivp

from indep_solver import (R0, L0, T0, C0, HCONV, HM, CTARGET,
                          props, Dfun, harm, chamber)
import verify2


def log(*a):
    print(*a, flush=True)


def dirichlet_run(N=400, t_end=300000.0):
    """Surface moisture node slaved to C_air -> convective resistance removed."""
    m = verify2.CV(N)
    base = verify2.CV.rhs

    def rhs(t, y):
        d = np.array(base(m, t, y))
        _, Ca = chamber(t)
        d[1::2][-1] = 1e6 * (Ca - y[1::2][-1])
        return d

    return solve_ivp(rhs, (0.0, t_end), m.y0(), method='BDF',
                     rtol=1e-8, atol=1e-10, events=m.ev)


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if which in ('c', 'all'):
        log('=== Method C: cell-vertex conservative FV (1st order at surface) ===')
        seq = []
        for N in (400, 800, 1600, 3200):
            t0 = time.time()
            m = verify2.CV(N)
            s = m.solve(t_end=300000.0)
            t = s.t_events[0][0]
            seq.append((N, t))
            log(f'  N={N:5d}  t* = {t:12.3f} s = {t/3600:9.5f} h  ({time.time()-t0:.0f}s)')
        log('  -- successive differences / observed order / Richardson --')
        for k in range(1, len(seq)):
            N1, t1 = seq[k - 1]
            N2, t2 = seq[k]
            d2, d1 = seq[k][1] - seq[k - 1][1], None
            log(f'   {N1}->{N2}: dt = {t2-t1:+.3f} s')
        # Richardson with p=1 (first-order boundary closure): t_inf = 2*t(2N) - t(N)
        for k in range(1, len(seq)):
            N1, t1 = seq[k - 1]
            N2, t2 = seq[k]
            log(f'   Richardson p=1 ({N1},{N2}) -> {2*t2-t1:.3f} s = {(2*t2-t1)/3600:.5f} h')
    if which in ('d', 'all'):
        log('=== Dirichlet-surface variant (C_s pinned to C_air) ===')
        for N in (200, 400):
            t0 = time.time()
            s = dirichlet_run(N)
            if len(s.t_events[0]):
                t = s.t_events[0][0]
                log(f'  N={N:5d}  t* = {t:12.3f} s = {t/3600:9.5f} h '
                    f'= {t/86400:.4f} d  ({time.time()-t0:.0f}s)')
            else:
                log(f'  N={N:5d}  no crossing (status {s.status}) ({time.time()-t0:.0f}s)')
    if which in ('2d', 'all'):
        log('=== Method D: 2D axisymmetric (r,z) ===')
        for (Nr, Nz) in ((40, 125), (60, 188), (80, 250)):
            t0 = time.time()
            m = verify2.FV2D(Nr, Nz)
            s = m.solve(t_end=300000.0)
            if len(s.t_events[0]):
                t = s.t_events[0][0]
                log(f'  Nr={Nr:3d} Nz={Nz:4d}  t* = {t:12.3f} s = {t/3600:9.5f} h '
                    f'= {t/86400:.5f} d  ({time.time()-t0:.0f}s)')
            else:
                log(f'  Nr={Nr:3d} Nz={Nz:4d}  NO CROSSING status={s.status} '
                    f'{s.message} ({time.time()-t0:.0f}s)')
