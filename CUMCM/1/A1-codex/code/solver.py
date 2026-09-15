"""Q1 independent conservative solver. SI units; x=r/R; cell-centred FV.

Time: backward Euler, optionally step doubling (accept two half steps).
Nonlinear flux: integral of D, evaluated with 3-point Gauss quadrature.
No clipping of computed moisture; rejected Newton/time steps fail explicitly.
"""
from pathlib import Path
import json
import os
import time
import numpy as np
from numba import njit
from scipy.interpolate import PchipInterpolator

ROOT = Path(__file__).resolve().parents[1]
R, RHO, CP, K, H, HM = .02, 820., 2600., .36, 25., 8e-7
T0, C0 = 28., 2.55


@njit(cache=True)
def diffusivity(c, scale, nonlinear):
    if nonlinear:
        return scale * np.exp(-.89 / c)
    return scale


@njit(cache=True)
def integral_d(a, b, scale, nonlinear):
    """Integral from b to a. Cancellation-free even for a approximately b."""
    if not nonlinear:
        return scale * (a - b)
    m = .5 * (a + b)
    d = .5 * (a - b)
    z = .7745966692414834 * d
    return d * scale * (5/9*np.exp(-.89/(m-z)) +
                       8/9*np.exp(-.89/m) + 5/9*np.exp(-.89/(m+z)))


@njit(cache=True)
def surface(c, air, dx, scale, beta, nonlinear):
    """Integral_D(c,cs)/half_dx = beta*(cs-air), monotone scalar equation."""
    d = diffusivity(c, scale, nonlinear)
    cs = (d*c + .5*dx*beta*air)/(d + .5*dx*beta)
    if not nonlinear:
        return cs, beta*d/(d + .5*dx*beta)
    lo, hi = min(c, air), max(c, air)
    for _ in range(20):
        f = integral_d(c, cs, scale, nonlinear) - .5*dx*beta*(cs-air)
        ds = diffusivity(cs, scale, nonlinear)
        step = f/(ds+.5*dx*beta)
        if abs(step) < 2e-14:
            return cs, beta*d/(ds+.5*dx*beta)
        if f > 0:
            lo = cs
        else:
            hi = cs
        nxt = cs+step
        cs = nxt if lo < nxt < hi else .5*(lo+hi)
    raise ValueError('Surface root failed')


@njit(cache=True)
def tridiagonal(lower, diag, upper, rhs):
    n = len(diag)
    b, z = diag.copy(), rhs.copy()
    for i in range(1, n):
        fac = lower[i]/b[i-1]
        b[i] -= fac*upper[i-1]
        z[i] -= fac*z[i-1]
    z[-1] /= b[-1]
    for i in range(n-2, -1, -1):
        z[i] = (z[i]-upper[i]*z[i+1])/b[i]
    return z


@njit(cache=True)
def make_grid(n, power):
    faces = 1-(1-np.linspace(0.,1.,n+1))**power
    centers = .5*(faces[1:]+faces[:-1])
    volumes = .5*(faces[1:]**2-faces[:-1]**2)
    g = faces[1:-1]/(centers[1:]-centers[:-1])
    return centers, volumes, g, 1-centers[-1]


@njit(cache=True)
def residual_jac(c, old, dt, air, scale, beta, nonlinear, grid):
    n = len(c)
    centers,v,conductance,half = grid
    d = np.empty(n)
    for i in range(n):
        d[i] = diffusivity(c[i], scale, nonlinear)
    lo, up = np.zeros(n), np.zeros(n)
    diag, res = v.copy(), v*(c-old)
    for i in range(n-1):
        g = conductance[i]
        q = g*integral_d(c[i], c[i+1], scale, nonlinear)
        res[i] += dt*q
        res[i+1] -= dt*q
        diag[i] += dt*g*d[i]
        diag[i+1] += dt*g*d[i+1]
        up[i] = -dt*g*d[i+1]
        lo[i+1] = -dt*g*d[i]
    cs, deriv = surface(c[-1], air, 2*half, scale, beta, nonlinear)
    q = beta*(cs-air)
    res[-1] += dt*q
    diag[-1] += dt*deriv
    return res, lo, diag, up, q


@njit(cache=True)
def be_step(old, dt, air, scale, beta, nonlinear, grid):
    c = old.copy()
    n = len(c)
    vol = grid[1]
    for it in range(14):
        res, lo, diag, up, q = residual_jac(c, old, dt, air, scale, beta, nonlinear, grid)
        # Diagonal scaling measures backward error even on very thin boundary cells.
        err = np.max(np.abs(res)/diag)
        if err < 3e-13:
            return c, q, it
        delta = tridiagonal(lo, diag, up, -res)
        lam = 1.
        for j in range(18):
            trial = c + lam*delta
            if not nonlinear or np.min(trial)>0:
                r2, _, _, _, _ = residual_jac(trial, old, dt, air, scale, beta, nonlinear, grid)
                if np.max(np.abs(r2)/diag) < err or np.max(np.abs(lam*delta)) < 1e-12:
                    break
            lam *= .5
        c = trial
    raise ValueError('Newton did not converge')


@njit(cache=True)
def eval_air(t, times, coeff):
    i = min(max(np.searchsorted(times, t, side='right')-1, 0), len(times)-2)
    z = t-times[i]
    return ((coeff[0,i]*z+coeff[1,i])*z+coeff[2,i])*z+coeff[3,i]


@njit(cache=True)
def sample(c, air, scale, beta, nonlinear, grid):
    n = len(c)
    out = np.empty(21)
    # Point-value cell-centred FV: symmetry-constrained quadratic at r=0.
    centers = grid[0]
    out[0] = (centers[1]**2*c[0]-centers[0]**2*c[1])/(centers[1]**2-centers[0]**2)
    out[-1], _ = surface(c[-1], air, 2*grid[3], scale, beta, nonlinear)
    for j in range(1,20):
        # Local quadratic point reconstruction avoids extra linear interpolation error.
        z = j/20
        i = min(max(np.searchsorted(centers,z)-1, 1), n-2)
        a,b,d = centers[i-1],centers[i],centers[i+1]
        out[j] = (z-b)*(z-d)/((a-b)*(a-d))*c[i-1] + (z-a)*(z-d)/((b-a)*(b-d))*c[i] + (z-a)*(z-b)/((d-a)*(d-b))*c[i+1]
    return out


@njit(cache=True)
def integrate(n, end, dtmax, budget, times, coeff, initial, scale, beta, nonlinear, power=1.):
    """budget>0: local budget proportional to increment of sqrt(t/end).
    This allocates more accuracy budget to the incompatible initial boundary layer.
    This local error budget is diagnostic, NOT a rigorous PDE global error bound.
    budget==0: fixed-step BE for controlled convergence studies.
    """
    c = np.full(n, initial)
    hist = np.empty((end+1,21))
    hist[0] = initial
    grid = make_grid(n,power)
    vol = grid[1]
    m0 = np.sum(vol*c)
    balance = np.zeros(end+1)
    qint = 0.
    qcomp = 0.
    t, h = 0., min(dtmax, .1)
    steps, rejected, iterations = 0, 0, 0
    hmin, hmax, emin, emax = 1e99, 0., initial, initial
    for target in range(1,end+1):
        while t < target-1e-10:
            nxtnode = times[min(np.searchsorted(times,t+1e-9),len(times)-1)]
            h = min(h,dtmax,target-t)
            if nxtnode > t+1e-9:
                h = min(h,nxtnode-t)
            air = eval_air(t+h,times,coeff)
            full, qf, it = be_step(c,h,air,scale,beta,nonlinear,grid)
            iterations += it
            err = 0.
            if budget>0:
                am = eval_air(t+.5*h,times,coeff)
                half, qh, it = be_step(c,.5*h,am,scale,beta,nonlinear,grid)
                fine, q2, it2 = be_step(half,.5*h,air,scale,beta,nonlinear,grid)
                iterations += it+it2
                err = max(np.max(np.abs(fine-full)), np.max(np.abs(
                    sample(fine,air,scale,beta,nonlinear,grid)-sample(full,air,scale,beta,nonlinear,grid))))
                weight = np.sqrt((t+h)/end)-np.sqrt(t/end)
                allowed = max(budget*weight, 5e-13)
                if err>allowed:
                    h *= max(.1,.8*allowed/err)
                    rejected += 1
                    if h<1e-12:
                        raise ValueError('Time step underflow')
                    continue
                c = fine
                dq = .5*h*(qh+q2)
            else:
                c = full
                dq = h*qf
            # Kahan accumulation for boundary exchange.
            y = dq-qcomp
            s = qint+y
            qcomp = (s-qint)-y
            qint = s
            steps += 1
            hmin, hmax = min(hmin,h), max(hmax,h)
            emin, emax = min(emin,np.min(c)), max(emax,np.max(c))
            t += h
            if budget>0:
                h *= min(2.,max(.5,.85*allowed/max(err,1e-30)))
            else:
                h = dtmax
        air = eval_air(float(target),times,coeff)
        hist[target] = sample(c,air,scale,beta,nonlinear,grid)
        balance[target] = np.sum(vol*c)-m0+qint
    return hist, c, balance, np.array([steps,rejected,iterations,hmin,hmax,emin,emax,qint])


def ambient(interpolation='linear'):
    a = np.loadtxt(ROOT/'data/ambient.csv',delimiter=',',skiprows=1)
    times = a[:,0]
    coefficients = []
    for y in a[:,1:].T:
        if interpolation=='pchip':
            c = PchipInterpolator(times,y).c
        else:
            c = np.zeros((4,len(times)-1))
            c[2] = np.diff(y)/np.diff(times)
            c[3] = y[:-1]
        coefficients.append(c)
    return times, coefficients


def solve(n=200, dt=.1, budget=0., interpolation='linear', h_factor=1., hm_factor=1., d_factor=1., end=1800, power=1.):
    times, coeff = ambient(interpolation)
    start=time.perf_counter()
    rt = integrate(n,end,dt,budget,times,coeff[0],T0,K/(RHO*CP*R**2),H*h_factor/(RHO*CP*R),False,power)
    rc = integrate(n,end,dt,budget,times,coeff[1],C0,7e-9*d_factor/R**2,HM*hm_factor/R,True,power)
    return dict(T=rt[0],C=rc[0],Tcells=rt[1],Ccells=rc[1],Tbalance=rt[2],Cbalance=rc[2],
                Tstats=rt[3],Cstats=rc[3],seconds=np.array(time.perf_counter()-start))


def save_run(name, **kw):
    path=ROOT/'verification'/f'{name}.npz'
    meta=ROOT/'verification'/f'{name}.config.json'
    if path.exists() and meta.exists() and json.loads(meta.read_text())==kw and os.environ.get('A1_RECOMPUTE')!='1':
        return dict(np.load(path))
    print('RUN',name,kw,flush=True)
    result=solve(**kw)
    np.savez_compressed(path,**result)
    meta.write_text(json.dumps(kw),encoding='utf-8')
    print('DONE',name,'seconds',float(result['seconds']),'end',result['T'][-1,[0,-1]],result['C'][-1,[0,-1]],flush=True)
    return result


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--n',type=int,default=200)
    p.add_argument('--dt',type=float,default=.1)
    p.add_argument('--budget',type=float,default=0.)
    p.add_argument('--name',default='standalone')
    a=p.parse_args()
    save_run(a.name,n=a.n,dt=a.dt,budget=a.budget)
