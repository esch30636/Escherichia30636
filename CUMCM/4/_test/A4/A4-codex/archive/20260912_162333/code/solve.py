"""Coupled moving-radius solver with actual flux quadrature and cache hashes."""
from pathlib import Path
import argparse,hashlib,json,time
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator
from core import mesh,sparsity,kernel,sample,center,boundary
ROOT=Path(__file__).resolve().parents[1]

class Inputs:
    def __init__(self,shrink=True,interp='linear',scenario='base'):
        self.env=np.loadtxt(ROOT/'data/ambient.csv',delimiter=',',skiprows=1)
        self.rad=np.loadtxt(ROOT/'data/radius.csv',delimiter=',',skiprows=1)
        self.shrink=shrink;self.interp=interp;self.scenario=scenario
        self.pchip=PchipInterpolator(self.rad[:,0],self.rad[:,1]*.01)
    def air(self,t):
        a=np.array([np.interp(t,self.env[:,0],self.env[:,i]) for i in (1,2)])
        if t>self.env[-1,0]:
            if self.scenario=='temp_low': a[0]-=1
            if self.scenario=='temp_high': a[0]+=1
            if self.scenario=='humid_low': a[1]*=.9
            if self.scenario=='humid_high': a[1]*=1.1
        return a
    def radius(self,t):
        if not self.shrink: return .02,0.
        t=float(t)
        if t>=self.rad[-1,0]: return float(self.rad[-1,1]*.01),0.
        if self.interp=='pchip': return float(self.pchip(t)),float(self.pchip.derivative()(t))
        j=np.clip(np.searchsorted(self.rad[:,0],t,side='right')-1,0,len(self.rad)-2)
        dt=self.rad[j+1,0]-self.rad[j,0];s=(self.rad[j+1,1]-self.rad[j,1])*.01/dt
        return self.rad[j,1]*.01+s*(t-self.rad[j,0]),s

def solve(name,n=800,rtol=1e-11,method='BDF',shrink=True,appendix=4,interp='linear',scenario='base',recompute=False):
    config=dict(n=n,rtol=rtol,method=method,shrink=shrink,appendix=appendix,interp=interp,scenario=scenario)
    config['sha256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ('code/core.py','code/solve.py','data/ambient.csv','data/radius.csv')}
    out=ROOT/'verification'/f'{name}.npz'; cp=out.with_suffix('.config.json')
    if not recompute and out.exists() and cp.exists() and json.loads(cp.read_text())==config:
        print('cached '+name,flush=True);return out
    start=time.perf_counter();inp=Inputs(shrink,interp,scenario)
    x,v,g,half=mesh(n);sp=sparsity(n)
    def rhs(t,y): return kernel(y,x,v,g,half,inp.radius(t)[0],*inp.air(t),appendix)[0]
    def event(t,y):
        r,_=inp.radius(t);ts,cs,_,_=boundary(y[-2],y[-1],*inp.air(t),r*half,appendix)
        return max(center(y[1::2],x),np.max(y[1::2]),cs)-.15
    event.direction=-1
    knots=np.unique(np.r_[inp.env[:,0],inp.rad[:,0]])
    intervals=list(zip(knots[:-1],knots[1:]))
    y=np.tile([28.,2.55],n); times=[0.]; states=[y.copy()];crossing=None
    integrals=np.zeros(4);identities=np.zeros(2);stats={'steps':0,'nfev':0}
    for left,right in intervals:
        sol=solve_ivp(rhs,(left,right),y,method=method,jac_sparsity=sp,rtol=rtol,
          atol=np.tile([rtol*.1,rtol*.01],n),max_step=10. if left<14400 else 300.,dense_output=True,events=event)
        if not sol.success: raise RuntimeError(sol.message)
        stats['steps']+=len(sol.t)-1;stats['nfev']+=sol.nfev
        if len(sol.t_events[0]) and crossing is None: crossing=float(sol.t_events[0][0])
        end=right if crossing is None else min(right,(np.floor(crossing/60)+1)*60)
        tt=np.arange(left+60,end+.0001,60); times.extend(tt);states.extend(sol.sol(tt).T)
        kk=np.unique(np.r_[sol.t[sol.t<end],end]);mids=(kk[1:]+kk[:-1])/2;width=np.diff(kk)/2
        for z,w in ((-.7745966692414834,5/9),(0.,8/9),(.7745966692414834,5/9)):
            tq=mids+z*width;yy=sol.sol(tq)
            for j,t in enumerate(tq):
                r,rd=inp.radius(t); dy,qt,qc,co,en=kernel(yy[:,j],x,v,g,half,r,*inp.air(t),appendix)
                integrals+=w*width[j]*np.array([qc/r**2,qt,co,2*rd/r*en])
                if appendix==4: caps=(760+90*yy[1::2,j])*(1850+2150*yy[1::2,j]/(1+yy[1::2,j]))
                else: caps=(650+128*yy[1::2,j])*(1450+2736*yy[1::2,j]/(1+yy[1::2,j]))
                identities=np.maximum(identities,[abs(v@dy[1::2]+qc/r**2),abs(r**2*(v*caps)@dy[0::2]+qt)])
        y=sol.sol(end)
        if crossing is not None: break
        if right>=knots[-1]:
            if right>=30*86400: raise RuntimeError('No crossing in 30 days; model/input reassessment required')
            intervals.append((right,right+86400))
    tt=np.array(times);ys=np.array(states);radii=np.array([inp.radius(t)[0] for t in tt]);xi=np.linspace(0,1,101)
    fixed=np.arange(21)*.001; output=[];norm=[]
    for t,y,r in zip(tt,ys,radii):
        output.append(sample(y,x,half,r,*inp.air(t),appendix,np.r_[fixed/r,1.]))
        norm.append(sample(y,x,half,r,*inp.air(t),appendix,xi))
    output=np.array(output);norm=np.array(norm)
    output[0,:,0]=28.;output[0,:,1]=2.55;norm[0,:,0]=28.;norm[0,:,1]=2.55
    maxima=np.maximum(ys[:,1::2].max(axis=1),np.nanmax(output[:,:,1],axis=1))
    assert np.isfinite(ys).all() and ys[:,1::2].min()>0
    assert maxima[-1]<.15 and maxima[-2]>=.15
    r=radii[-1];en=kernel(ys[-1],x,v,g,half,r,*inp.air(tt[-1]),appendix)[4]
    en0=kernel(ys[0],x,v,g,half,.02,*inp.air(0),appendix)[4]
    bal=np.array([v@ys[-1,1::2]-v.sum()*2.55+integrals[0],en-en0+integrals[1]-integrals[2]-integrals[3]])
    meta=dict(name=name,**config,crossing_s=crossing,minute_s=float(tt[-1]),seconds=time.perf_counter()-start,
      integrals=integrals.tolist(),balance=bal.tolist(),relative_balance=[abs(bal[0])/(v.sum()*2.55),abs(bal[1])/en0],
      identity_abs=identities.tolist(),radial_increase_max=float(np.diff(ys[:,1::2],axis=1).max()),
      radius_extended=bool(tt[-1]>knots[-1]),**stats)
    np.savez_compressed(out,time_s=tt,radius_m=radii,distance_cm=fixed*100,T=output[:,:,0],C=output[:,:,1],
      xi=xi,T_xi=norm[:,:,0],C_xi=norm[:,:,1],maxC=maxima,means=ys[:,1::2]@v/v.sum(),
      final_cells=ys[-1],x=x,v=v,metadata=json.dumps(meta))
    cp.write_text(json.dumps(config,indent=2));out.with_suffix('.json').write_text(json.dumps(meta,indent=2))
    print(json.dumps({k:meta[k] for k in ('name','crossing_s','minute_s','seconds','relative_balance')}),flush=True)
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',default='tight800');p.add_argument('--n',type=int,default=800)
    p.add_argument('--rtol',type=float,default=1e-11);p.add_argument('--method',default='BDF',choices=['BDF','Radau'])
    p.add_argument('--fixed',action='store_true');p.add_argument('--appendix',type=int,default=4,choices=[3,4])
    p.add_argument('--interp',default='linear',choices=['linear','pchip']);p.add_argument('--scenario',default='base')
    p.add_argument('--recompute',action='store_true');a=vars(p.parse_args());a['shrink']=not a.pop('fixed');solve(**a)
