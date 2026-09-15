"""Independent nodal finite volume implementation (no production operator imports).

State nodes include r=0 and the actual surface. Boundary nodes have finite half
control volumes; Robin exchange directly supplies the outer flux. No algebraic
surface extrapolation from the production method is used. Five-point quadrature.
"""
import numpy as np
from numba import njit
from scipy.sparse import diags
Z,W=np.polynomial.legendre.leggauss(5);Z=(Z+1)/2;W=W/2

def mesh(n):
    x=1-(1-np.linspace(0,1,n+1))**1.5
    f=np.r_[0.,(x[1:]+x[:-1])/2,1.]
    return x,np.diff(f*f)/2,f[1:-1]/np.diff(x),0.

def sparsity(n):
    # Interleaved T/C: block tridiagonal, conservatively filled bandwidth 3.
    return diags([np.ones(2*n-abs(k)) for k in range(-3,4)],range(-3,4),format='csc')

@njit(cache=True)
def coefficients(t,c,appendix):
    if appendix==3:
        a=(650+128*c)*(1450+2736*c/(1+c))
        ap=128*(1450+2736*c/(1+c))+(650+128*c)*2736/(1+c)**2
        return a,.21+.38*c/(1+c),.0024*np.exp(-.45/c-3850/(t+273.15)),ap
    a=(760+90*c)*(1850+2150*c/(1+c))
    ap=90*(1850+2150*c/(1+c))+(760+90*c)*2150/(1+c)**2
    return a,.12+.20*c/(1+c),.00042*np.exp(-.30/c-3850/(t+273.15)),ap

@njit(cache=True)
def kernel(y,x,v,g,half,R,ta,ca,appendix,h=25.,hm=8e-7,order=5):
    n=len(x); qt=np.zeros(n+1);qc=np.zeros(n+1)
    for i in range(n-1):
        k=0.;d=0.
        for j in range(5):
            t=y[2*i]+Z[j]*(y[2*i+2]-y[2*i]);c=y[2*i+1]+Z[j]*(y[2*i+3]-y[2*i+1])
            _,kk,dd,_=coefficients(t,c,appendix);k+=W[j]*kk;d+=W[j]*dd
        qt[i+1]=g[i]*k*(y[2*i]-y[2*i+2]);qc[i+1]=g[i]*d*(y[2*i+1]-y[2*i+3])
    qt[-1]=R*h*(y[-2]-ta);qc[-1]=R*hm*(y[-1]-ca)
    dy=np.empty_like(y);corr=0.;en=0.
    for i in range(n):
        a,_,_,ap=coefficients(y[2*i],y[2*i+1],appendix)
        dy[2*i]=(qt[i]-qt[i+1])/(R*R*v[i]*a)
        dy[2*i+1]=(qc[i]-qc[i+1])/(R*R*v[i])
        corr+=R*R*v[i]*ap*y[2*i]*dy[2*i+1]
        en+=R*R*v[i]*a*y[2*i]
    return dy,qt[-1],qc[-1],corr,en

@njit(cache=True)
def sample(y,x,half,R,ta,ca,appendix,targets,order=5):
    out=np.empty((len(targets),2))
    for j in range(len(targets)):
        z=targets[j]
        if z>1+1e-12 or z<0:out[j,:]=np.nan;continue
        if z<=0:out[j,:]=y[:2];continue
        if z>=1-1e-12:out[j,:]=y[-2:];continue
        i=min(max(np.searchsorted(x,z)-1,1),len(x)-2)
        a,b,c=x[i-1],x[i],x[i+1]
        for k in range(2):
            out[j,k]=(z-b)*(z-c)/(a-b)/(a-c)*y[2*(i-1)+k]+(z-a)*(z-c)/(b-a)/(b-c)*y[2*i+k]+(z-a)*(z-b)/(c-a)/(c-b)*y[2*(i+1)+k]
    return out

@njit(cache=True)
def sample_batch(ys,x,half,rs,airs,appendix,targets,order):
    out=np.empty((ys.shape[1],len(targets),2))
    for i in range(ys.shape[1]):out[i]=sample(ys[:,i],x,half,rs[i],airs[i,0],airs[i,1],appendix,targets)
    return out
