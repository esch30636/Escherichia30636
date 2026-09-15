"""Material-coordinate radial finite volumes, adapted from A3-codex.

Coordinates x and v are dimensionless xi and integral xi dxi. R is ALWAYS
passed in metres. Dry-basis C is advected with the solid, not a volume density.
"""
import numpy as np
from numba import njit
from scipy.sparse import lil_matrix
Z3,W3=np.polynomial.legendre.leggauss(3);Z3=(Z3+1)/2;W3=W3/2
Z5,W5=np.polynomial.legendre.leggauss(5);Z5=(Z5+1)/2;W5=W5/2

@njit(cache=True)
def properties(t,c,appendix=4):
    if c<=0 or t<=-273.15: raise ValueError('Nonphysical state; no clipping')
    if appendix==3:
        rho=650+128*c; cp=1450+2736*c/(1+c)
        return rho*cp,.21+.38*c/(1+c),.0024*np.exp(-.45/c-3850/(t+273.15)),128*cp+rho*2736/(1+c)**2
    rho=760+90*c; cp=1850+2150*c/(1+c)
    return rho*cp,.12+.20*c/(1+c),.00042*np.exp(-.30/c-3850/(t+273.15)),90*cp+rho*2150/(1+c)**2

@njit(cache=True)
def face(t1,c1,t2,c2,appendix,order=3):
    k,d=0.,0.
    for j in range(order):
        z=Z3[j] if order==3 else Z5[j]; w=W3[j] if order==3 else W5[j]
        _,ki,di,_=properties(t1+z*(t2-t1),c1+z*(c2-c1),appendix)
        k+=w*ki; d+=w*di
    return k,d

@njit(cache=True)
def boundary(t,c,ta,ca,half,appendix,h=25.,hm=8e-7,order=3):
    ts,cs=t,c
    for it in range(80):
        k,d=face(t,c,ts,cs,appendix,order)
        tn=(k*t+h*half*ta)/(k+h*half)
        cn=(d*c+hm*half*ca)/(d+hm*half)
        err=max(abs(tn-ts),abs(cn-cs)); ts,cs=tn,cn
        if err<2e-13: return ts,cs,h*(ts-ta),hm*(cs-ca)
    raise ValueError('Surface nonlinear solve failed')

def mesh(n):
    f=1-(1-np.linspace(0,1,n+1))**2
    x=(f[1:]+f[:-1])/2; v=(f[1:]**2-f[:-1]**2)/2
    return x,v,f[1:-1]/np.diff(x),1-x[-1]

def sparsity(n):
    a=lil_matrix((2*n,2*n),dtype=int)
    for i in range(n): a[2*i:2*i+2,2*max(0,i-1):2*min(n,i+2)]=1
    return a.tocsr()

@njit(cache=True)
def kernel(y,x,v,g,half,R,ta,ca,appendix,h=25.,hm=8e-7,order=3):
    n=len(x); out=np.empty_like(y); qt,qc=0.,0.; corr=0.; energy=0.
    for i in range(n):
        ti,ci=y[2*i],y[2*i+1]; cap,_,_,ap=properties(ti,ci,appendix)
        if i<n-1:
            k,d=face(ti,ci,y[2*i+2],y[2*i+3],appendix,order)
            nt=g[i]*k*(ti-y[2*i+2]); nc=g[i]*d*(ci-y[2*i+3])
        else:
            _,_,jt,jc=boundary(ti,ci,ta,ca,R*half,appendix,h,hm,order)
            nt=R*jt; nc=R*jc
        out[2*i]=(qt-nt)/(R*R*v[i]*cap)
        out[2*i+1]=(qc-nc)/(R*R*v[i])
        corr+=R*R*v[i]*ap*ti*out[2*i+1]
        energy+=R*R*v[i]*cap*ti
        qt,qc=nt,nc
    return out,qt,qc,corr,energy

@njit(cache=True)
def center(a,x):
    return (x[1]**2*a[0]-x[0]**2*a[1])/(x[1]**2-x[0]**2)

@njit(cache=True)
def sample(y,x,half,R,ta,ca,appendix,targets,order=3):
    ts,cs,_,_=boundary(y[-2],y[-1],ta,ca,R*half,appendix,order=order)
    xx=np.empty(len(x)+2);xx[0]=0.;xx[1:-1]=x;xx[-1]=1.
    ans=np.empty((len(targets),2))
    for k in range(2):
        a=np.empty(len(xx));a[0]=center(y[k::2],x);a[1:-1]=y[k::2];a[-1]=ts if k==0 else cs
        for j in range(len(targets)):
            z=targets[j]
            if z>1+1e-12 or z<0: ans[j,k]=np.nan;continue
            if z>=1-1e-12: ans[j,k]=a[-1];continue
            if z==0: ans[j,k]=a[0];continue
            i=min(max(np.searchsorted(xx,z)-1,1),len(xx)-2)
            aa,b,c=xx[i-1],xx[i],xx[i+1]
            ans[j,k]=((z-b)*(z-c)/((aa-b)*(aa-c))*a[i-1]
              +(z-aa)*(z-c)/((b-aa)*(b-c))*a[i]
              +(z-aa)*(z-b)/((c-aa)*(c-b))*a[i+1])
    return ans

@njit(cache=True)
def sample_batch(ys,x,half,rs,airs,appendix,targets,order):
    out=np.empty((ys.shape[1],len(targets),2))
    for i in range(ys.shape[1]): out[i]=sample(ys[:,i],x,half,rs[i],airs[i,0],airs[i,1],appendix,targets,order)
    return out
