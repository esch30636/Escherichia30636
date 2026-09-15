"""One production engine for both questions; independent spatial backend optional."""
from pathlib import Path
import argparse,hashlib,json,time
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator
from . import core,independent
COMMON=Path(__file__).resolve().parent
WORKSPACE=COMMON.parents[3]

class Inputs:
    def __init__(self,root,shrink,interp,scenario):
        self.env=np.loadtxt(root/'data/ambient.csv',delimiter=',',skiprows=1)
        self.rad=np.loadtxt(root/'data/radius.csv',delimiter=',',skiprows=1)
        self.shrink=shrink;self.interp=interp;self.scenario=scenario
        self.pchip=PchipInterpolator(self.rad[:,0],self.rad[:,1]*.01)
        self.tail=self.env[-1,1:].copy()
        if scenario=='mean':self.tail=np.trapezoid(self.env[-61:,1:],self.env[-61:,0],axis=0)/3600
        if scenario=='temp_low':self.tail[0]-=1
        if scenario=='temp_high':self.tail[0]+=1
        if scenario=='humid_low':self.tail[1]*=.9
        if scenario=='humid_high':self.tail[1]*=1.1
    def air(self,t):
        a=np.asarray(t);v=np.stack([np.interp(a,self.env[:,0],self.env[:,i]) for i in (1,2)],axis=-1)
        return np.where((a>14400)[...,None],self.tail,v)
    def radius(self,t):
        if not self.shrink:return .02,0.
        if t>=self.rad[-1,0]:return self.rad[-1,1]*.01,0.
        if self.interp=='pchip':return float(self.pchip(t)),float(self.pchip.derivative()(t))
        j=np.clip(np.searchsorted(self.rad[:,0],t,side='right')-1,0,len(self.rad)-2)
        slope=(self.rad[j+1,1]-self.rad[j,1])*.01/(self.rad[j+1,0]-self.rad[j,0])
        return self.rad[j,1]*.01+slope*(t-self.rad[j,0]),slope

def fingerprint(root):
    paths=list(COMMON.glob('*.py'))+[root/'data/ambient.csv',root/'data/radius.csv']
    return {str(p.relative_to(WORKSPACE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

def solve(root,question,name,n=1600,rtol=1e-11,method='BDF',shrink=None,appendix=None,
          interp='linear',scenario='base',recompute=False,order=3,max_step=300.,backend='production'):
    root=Path(root).resolve();shrink=(question==4) if shrink is None else shrink;appendix=question if appendix is None else appendix
    assert n>=4 and appendix in (3,4) and order in (3,5) and max_step>0
    assert scenario in ('base','mean','temp_low','temp_high','humid_low','humid_high')
    assert backend in ('production','independent')
    if backend=='independent':method='Radau';order=5
    config=dict(question=question,n=n,rtol=rtol,method=method,shrink=shrink,appendix=appendix,
        interp=interp,scenario=scenario,order=order,max_step=max_step,backend=backend,sha256=fingerprint(root))
    out=root/'verification'/f'{name}.npz';cp=out.with_suffix('.config.json')
    if not recompute and out.exists() and cp.exists() and json.loads(cp.read_text())==config:
        print('cached',question,name,flush=True);return out
    start=time.perf_counter();inp=Inputs(root,shrink,interp,scenario);op=core if backend=='production' else independent
    x,v,g,half=op.mesh(n);nn=len(x);sp=op.sparsity(nn)
    def rhs(t,y):return op.kernel(y,x,v,g,half,inp.radius(t)[0],*inp.air(t),appendix,order=order)[0]
    def event(t,y):
        if backend=='independent':return y[1::2].max()-.15
        R=inp.radius(t)[0];cs=core.boundary(y[-2],y[-1],*inp.air(t),R*half,appendix,order=order)[1]
        return max(core.center(y[1::2],x),y[1::2].max(),cs)-.15
    event.direction=-1
    knots=np.unique(np.r_[inp.env[:,0],inp.rad[:,0]])
    intervals=list(zip(knots[:-1],knots[1:]));y=np.tile([28.,2.55],nn);crossing=None
    initial=y.copy();xi=np.linspace(0,1,1001);fixed=np.arange(21)*.001
    times=[np.array([0.])];radii=[np.array([.02])];norm=[np.tile([28.,2.55],(1,1001,1))]
    output=[np.tile([28.,2.55],(1,22,1))];maxima=[np.array([2.55])];means=[np.array([2.55])]
    integrals=np.zeros(4);identities=np.zeros(2);stats={'steps':0,'nfev':0};radial=0.;minC=2.55;maxC=2.55
    en0=op.kernel(y,x,v,g,half,.02,*inp.air(0),appendix,order=order)[4]
    print('start',question,name,n,backend,flush=True)
    for left,right in intervals:
        sol=solve_ivp(rhs,(left,right),y,method=method,jac_sparsity=sp,rtol=rtol,
            atol=np.tile([rtol*.1,rtol*.01],nn),max_step=min(10.,max_step) if left<14400 else max_step,
            dense_output=True,events=event,
            # The graded mesh leaves a very thin outer half-cell.  At high N
            # its diffusive time scale is below 1e-10 s; forcing a smaller
            # first implicit step prevents the Newton predictor from
            # visiting negative C while retaining the un-clipped physical
            # constitutive law.
            first_step=1e-14 if left==0 and backend=='production' and n>=6400 else None)
        if not sol.success:raise RuntimeError(sol.message)
        stats['steps']+=len(sol.t)-1;stats['nfev']+=sol.nfev
        if len(sol.t_events[0]) and crossing is None:crossing=float(sol.t_events[0][0])
        end=right if crossing is None else min(right,(np.floor(crossing/60)+1)*60)
        tt=np.arange(left+60,end+.0001,60);yy=sol.sol(tt);rs=np.array([inp.radius(t)[0] for t in tt]);aa=inp.air(tt)
        if len(tt):
            if not np.isfinite(yy).all() or yy[1::2].min()<=0:raise RuntimeError('Nonphysical state; never clipped')
            radial=max(radial,float(np.diff(yy[1::2],axis=0).max()));minC=min(minC,float(yy[1::2].min()));maxC=max(maxC,float(yy[1::2].max()))
            ns=op.sample_batch(yy,x,half,rs,aa,appendix,xi,order)
            actual=np.array([op.sample(yy[:,j],x,half,R,*aa[j],appendix,np.r_[fixed/R,1.],order) for j,R in enumerate(rs)])
            times.append(tt);radii.append(rs);norm.append(ns);output.append(actual)
            maxima.append(np.maximum(np.max(yy[1::2],axis=0),np.maximum(np.nanmax(actual[:,:,1],axis=1),ns[:,:,1].max(axis=1))))
            means.append(v@yy[1::2]/v.sum())
        kk=np.unique(np.r_[sol.t[sol.t<end],end]);mids=(kk[1:]+kk[:-1])/2;width=np.diff(kk)/2
        for z,w in ((-.7745966692414834,5/9),(0.,8/9),(.7745966692414834,5/9)):
            tq=mids+z*width;yq=sol.sol(tq)
            for j,t in enumerate(tq):
                R,rd=inp.radius(t);dy,qt,qc,co,en=op.kernel(yq[:,j],x,v,g,half,R,*inp.air(t),appendix,order=order)
                integrals+=w*width[j]*np.array([qc/R**2,qt,co,2*rd/R*en])
                c=yq[1::2,j]
                caps=(650+128*c)*(1450+2736*c/(1+c)) if appendix==3 else (760+90*c)*(1850+2150*c/(1+c))
                identities=np.maximum(identities,[abs(v@dy[1::2]+qc/R**2),abs(R**2*(v*caps)@dy[0::2]+qt)])
        y=sol.sol(end)
        if crossing is not None:break
        if right>=knots[-1]:
            if right>=30*86400:raise RuntimeError('No crossing in 30 days')
            intervals.append((right,right+86400))
    tt=np.concatenate(times);rs=np.concatenate(radii);ns=np.concatenate(norm);actual=np.concatenate(output)
    mx=np.concatenate(maxima);avg=np.concatenate(means)
    assert mx[-1]<.15 and np.all(mx[:-1]>=.15)
    R=rs[-1];en=op.kernel(y,x,v,g,half,R,*inp.air(tt[-1]),appendix,order=order)[4]
    bal=[float(v@y[1::2]-v.sum()*2.55+integrals[0]),float(en-en0+integrals[1]-integrals[2]-integrals[3])]
    meta=dict(name=name,**config,crossing_s=crossing,minute_s=float(tt[-1]),seconds=time.perf_counter()-start,
        integrals=integrals.tolist(),balance=bal,relative_balance=[abs(bal[0])/(v.sum()*2.55),abs(bal[1])/en0],
        identity_abs=identities.tolist(),radial_increase_max=radial,minimum=minC,maximum=maxC,
        radius_extended=bool(shrink and tt[-1]>inp.rad[-1,0]),tail=inp.tail.tolist(),**stats)
    cols=21 if question==3 else 22
    np.savez_compressed(out,time_s=tt,radius_m=rs,distance_cm=fixed*100,radius_cm=fixed*100,
        T=actual[:,:,:][...,0][:,:cols],C=actual[...,1][:,:cols],xi=xi,T_xi=ns[:,:,0],C_xi=ns[:,:,1],
        maxC=mx,means=avg,final_cells=y,x=x*.02 if question==3 else x,v=v*.02**2 if question==3 else v,
        xi_cells=x,v_xi=v,metadata=json.dumps(meta))
    cp.write_text(json.dumps(config,indent=2));out.with_suffix('.json').write_text(json.dumps(meta,indent=2))
    print('done',question,name,meta['crossing_s'],meta['seconds'],flush=True);return out

def cli(root,question):
    p=argparse.ArgumentParser();p.add_argument('--name',default='main');p.add_argument('--n',type=int,default=1600)
    p.add_argument('--rtol',type=float,default=1e-11);p.add_argument('--method',default='BDF',choices=['BDF','Radau'])
    p.add_argument('--fixed',action='store_true');p.add_argument('--appendix',type=int,choices=[3,4]);p.add_argument('--order',type=int,default=3,choices=[3,5])
    p.add_argument('--interp',default='linear',choices=['linear','pchip']);p.add_argument('--scenario',default='base')
    p.add_argument('--backend',default='production',choices=['production','independent']);p.add_argument('--max-step',type=float,default=300.)
    p.add_argument('--recompute',action='store_true');a=vars(p.parse_args());a['shrink']=False if a.pop('fixed') else question==4
    solve(root,question,**a)
