"""Q2 coupled radial FV model. Celsius states; kelvin only in Arrhenius law.

No imports from A1. Run with a Python environment containing numpy/scipy/numba.
Face coefficients are three-point Gauss averages along a linear (T,C) path.
"""
from pathlib import Path
import argparse, json, time
import numpy as np
from numba import njit
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator
from scipy.sparse import lil_matrix

ROOT = Path(__file__).resolve().parents[1]
R = .02

@njit(cache=True)
def properties(t, c, q1, df):
    if q1:
        return 820.*2600., .36, df*7e-9*np.exp(-.89/c), 0.
    rho = 650.+128.*c
    cp = 1450.+2736.*c/(1.+c)
    cap = rho*cp
    capprime = 128.*cp + rho*2736./(1.+c)**2
    return cap, .21+.38*c/(1.+c), df*.0024*np.exp(-.45/c-3850./(t+273.15)), capprime

@njit(cache=True)
def face(t1,c1,t2,c2,q1,df):
    k,d=0.,0.
    for z,w in ((.1127016653792583,5./18),(.5,4./9),(.8872983346207417,5./18)):
        _,ki,di,_=properties(t1+z*(t2-t1),c1+z*(c2-c1),q1,df)
        k+=w*ki; d+=w*di
    return k,d

@njit(cache=True)
def boundary(t,c,ta,ca,half,q1,h,hm,df):
    # Outer cell half-width is tiny on graded meshes. Coupled fixed point is
    # contractive here; its residual is explicitly checked, never just assumed.
    ts,cs=t,c
    for it in range(60):
        k,d=face(t,c,ts,cs,q1,df)
        tn=(k*t+h*half*ta)/(k+h*half)
        cn=(d*c+hm*half*ca)/(d+hm*half)
        err=max(abs(tn-ts),abs(cn-cs))
        ts,cs=tn,cn
        if err<2e-13:
            return ts,cs,h*(ts-ta),hm*(cs-ca)
    raise ValueError('Surface iteration failed')

@njit(cache=True)
def kernel(y,x,v,g,half,ta,ca,q1,h,hm,df):
    n=len(x); out=np.empty(2*n)
    qt,qc=0.,0.
    correction=0.
    for i in range(n):
        ti,ci=y[2*i],y[2*i+1]
        cap,_,_,ap=properties(ti,ci,q1,df)
        if i<n-1:
            k,d=face(ti,ci,y[2*i+2],y[2*i+3],q1,df)
            nt=g[i]*k*(ti-y[2*i+2])
            nc=g[i]*d*(ci-y[2*i+3])
        else:
            _,_,jT,jC=boundary(ti,ci,ta,ca,half,q1,h,hm,df)
            nt=R*jT; nc=R*jC
        out[2*i]=(qt-nt)/(v[i]*cap)
        out[2*i+1]=(qc-nc)/v[i]
        correction+=v[i]*ap*ti*out[2*i+1]
        qt,qc=nt,nc
    return out,qt,qc,correction

def mesh(n):
    faces=R*(1-(1-np.linspace(0,1,n+1))**2)
    x=(faces[1:]+faces[:-1])/2
    v=(faces[1:]**2-faces[:-1]**2)/2
    g=faces[1:-1]/np.diff(x)
    return x,v,g,R-x[-1]

def sparsity(n):
    a=lil_matrix((2*n,2*n),dtype=int)
    for i in range(n):
        a[2*i:2*i+2,2*max(0,i-1):2*min(n,i+2)]=1
    return a.tocsr()

def sample(y,x,half,ta,ca,q1,h,hm,df):
    t,c=y[0::2],y[1::2]
    ans=np.empty((21,2))
    ans[0]=[(x[1]**2*a[0]-x[0]**2*a[1])/(x[1]**2-x[0]**2) for a in (t,c)]
    for j in range(1,20):
        z=j*.001; i=np.clip(np.searchsorted(x,z)-1,1,len(x)-2)
        xx=x[i-1:i+2]
        weights=np.array([(z-xx[1])*(z-xx[2])/((xx[0]-xx[1])*(xx[0]-xx[2])),
                          (z-xx[0])*(z-xx[2])/((xx[1]-xx[0])*(xx[1]-xx[2])),
                          (z-xx[0])*(z-xx[1])/((xx[2]-xx[0])*(xx[2]-xx[1]))])
        ans[j]=[weights@a[i-1:i+2] for a in (t,c)]
    ts,cs,_,_=boundary(t[-1],c[-1],ta,ca,half,q1,h,hm,df)
    ans[-1]=[ts,cs]
    return ans

@njit(cache=True)
def sample_many(ys,x,half,airs,q1,h,hm,df):
    m=ys.shape[1]; out=np.empty((m,21,2))
    for it in range(m):
        for field in range(2):
            a=ys[field::2,it]
            out[it,0,field]=(x[1]**2*a[0]-x[0]**2*a[1])/(x[1]**2-x[0]**2)
            for j in range(1,20):
                z=j*.001; i=min(max(np.searchsorted(x,z)-1,1),len(x)-2)
                aa,b,c=x[i-1],x[i],x[i+1]
                out[it,j,field]=((z-b)*(z-c)/((aa-b)*(aa-c))*a[i-1]
                    +(z-aa)*(z-c)/((b-aa)*(b-c))*a[i]
                    +(z-aa)*(z-b)/((c-aa)*(c-b))*a[i+1])
        ts,cs,_,_=boundary(ys[-2,it],ys[-1,it],airs[it,0],airs[it,1],half,q1,h,hm,df)
        out[it,20,0]=ts; out[it,20,1]=cs
    return out

def solve(n=400,end=10800,rtol=1e-9,method='BDF',q1=False,hfactor=1.,hmfactor=1.,dfactor=1.,interp='linear',audit=True):
    start=time.perf_counter()
    env=np.loadtxt(ROOT/'data/ambient.csv',delimiter=',',skiprows=1)
    if end>env[-1,0]: raise ValueError('No environment extrapolation is permitted')
    if interp=='pchip':
        p=PchipInterpolator(env[:,0],env[:,1:],axis=0)
        air=lambda ts: p(ts)
    else:
        air=lambda ts: np.stack([np.interp(ts,env[:,0],env[:,i]) for i in (1,2)],axis=-1)
    x,v,g,half=mesh(n); h=25*hfactor; hm=8e-7*hmfactor
    y=np.tile([28.,2.55],n)
    result=np.empty((end+1,21,2)); result[0,:,0]=28.; result[0,:,1]=2.55
    means=np.empty((end+1,2)); means[0]=[28.,2.55]
    def rhs(t,yy):
        a=air(t)
        return kernel(yy,x,v,g,half,a[0],a[1],q1,h,hm,dfactor)[0]
    sp=sparsity(n)
    qtint=qcint=corrint=0.; balances=[]
    cap0=properties(28.,2.55,q1,dfactor)[0]
    e0=v.sum()*cap0*28.; m0=v.sum()*2.55
    count={'nfev':0,'njev':0,'nlu':0,'steps':0}
    # Restart at each measured knot: avoids crossing a derivative discontinuity.
    for left in range(0,end,60):
        right=min(left+60,end)
        sol=solve_ivp(rhs,(left,right),y,method=method,rtol=rtol,
                      atol=np.tile([rtol*.1,rtol*.01],n),jac_sparsity=sp,
                      max_step=10.,dense_output=True)
        if not sol.success: raise RuntimeError(sol.message)
        for key in ('nfev','njev','nlu'): count[key]+=getattr(sol,key)
        count['steps']+=len(sol.t)-1
        ts=np.arange(left+1,right+1); ys=sol.sol(ts)
        if not np.isfinite(ys).all() or np.min(ys[1::2])<=0: raise ValueError('Invalid state; no clipping applied')
        result[ts]=sample_many(ys,x,half,air(ts),q1,h,hm,dfactor)
        means[ts,0]=(v@ys[0::2])/v.sum(); means[ts,1]=(v@ys[1::2])/v.sum()
        if audit:
            # Independent time quadrature on the accepted dense trajectory.
            mids=(sol.t[1:]+sol.t[:-1])/2; widths=(sol.t[1:]-sol.t[:-1])/2
            for z,w in ((-.7745966692414834,5/9),(0.,8/9),(.7745966692414834,5/9)):
                tq=mids+z*widths; yq=sol.sol(tq); aq=air(tq)
                for j in range(len(tq)):
                    _,qt,qc,co=kernel(yq[:,j],x,v,g,half,aq[j,0],aq[j,1],q1,h,hm,dfactor)
                    qtint+=w*widths[j]*qt; qcint+=w*widths[j]*qc; corrint+=w*widths[j]*co
        y=sol.y[:,-1]
        if audit:
            cap=np.array([properties(y[2*i],y[2*i+1],q1,dfactor)[0] for i in range(n)])
            energy=v@(cap*y[0::2]); mass=v@y[1::2]
            balances.append([right,mass-m0+qcint,energy-e0+qtint-corrint,qtint,qcint,corrint])
    metadata=dict(n=n,end=end,rtol=rtol,method=method,q1=q1,hfactor=hfactor,hmfactor=hmfactor,
                  dfactor=dfactor,interp=interp,audit=audit,seconds=time.perf_counter()-start,**count)
    return dict(time_s=np.arange(end+1),radius_cm=np.arange(21)/10,T=result[:,:,0],C=result[:,:,1],
                means=means,x_m=x,volumes=v,final_cells=y,balances=np.array(balances),metadata=json.dumps(metadata))

def run(name,**kwargs):
    p=ROOT/'verification'/f'{name}.npz'
    if p.exists():
        print('Cached:',name,flush=True); return
    z=solve(**kwargs); np.savez_compressed(p,**z)
    print(name,z['metadata'], 'end center/surface',z['T'][-1,[0,-1]],z['C'][-1,[0,-1]],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--name',default='base400');p.add_argument('--n',type=int,default=400)
    p.add_argument('--rtol',type=float,default=1e-9);p.add_argument('--method',default='BDF');p.add_argument('--end',type=int,default=10800)
    a=p.parse_args();run(a.name,n=a.n,rtol=a.rtol,method=a.method,end=a.end)
