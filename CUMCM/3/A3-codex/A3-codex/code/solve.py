"""Long-time extension of the audited Q2 core; SI radial coordinates throughout."""
from pathlib import Path
import json,time,argparse
import numpy as np
from scipy.integrate import solve_ivp
from core import mesh,sparsity,kernel,sample_many,properties,boundary,face
ROOT=Path(__file__).resolve().parents[1]

def solve(name,n=800,rtol=1e-10,method='BDF',scenario='base',max_step=300.):
    begin=time.perf_counter()
    env=np.loadtxt(ROOT/'data/ambient.csv',delimiter=',',skiprows=1)
    tail=env[-1,1:].copy()
    if scenario=='mean': tail=np.trapezoid(env[-61:,1:],env[-61:,0],axis=0)/3600
    if scenario=='temp_low': tail[0]-=1
    if scenario=='temp_high': tail[0]+=1
    if scenario=='humid_low': tail[1]*=.9
    if scenario=='humid_high': tail[1]*=1.1
    def air(t):
        t=np.asarray(t)
        a=np.stack([np.interp(t,env[:,0],env[:,i]) for i in (1,2)],axis=-1)
        return np.where((t>14400)[...,None],tail,a)
    x,v,g,half=mesh(n); sp=sparsity(n)
    def rhs(t,y):
        ta,ca=air(t)
        return kernel(y,x,v,g,half,ta,ca,False,25.,8e-7,1.)[0]
    def center(c): return (x[1]**2*c[0]-x[0]**2*c[1])/(x[1]**2-x[0]**2)
    def event(t,y):
        c=y[1::2]; ta,ca=air(t)
        cs=boundary(y[-2],y[-1],ta,ca,half,False,25.,8e-7,1.)[1]
        return max(center(c),np.max(c),cs)-.15
    event.direction=-1
    y=np.tile([28.,2.55],n); times=[0.]; states=[y.copy()]; crossing=None
    integrals=np.zeros(3); max_identity=np.zeros(2); stats={'steps':0,'nfev':0}
    intervals=[(a,a+60) for a in range(0,14400,60)]+[(14400,72*3600)]
    for left,right in intervals:
        sol=solve_ivp(rhs,(left,right),y,method=method,jac_sparsity=sp,
            rtol=rtol,atol=np.tile([rtol*.1,rtol*.01],n),
            max_step=10. if left<14400 else max_step,dense_output=True,events=event)
        if not sol.success: raise RuntimeError(sol.message)
        stats['steps']+=len(sol.t)-1; stats['nfev']+=sol.nfev
        if len(sol.t_events[0]) and crossing is None: crossing=float(sol.t_events[0][0])
        end=right if crossing is None else min(right,(np.floor(crossing/60)+1)*60)
        ts=np.arange(left+60,end+.001,60); ys=sol.sol(ts)
        times.extend(ts); states.extend(ys.T)
        # Integrate the actual boundary flux, never back-fit fluxes to state changes.
        knots=np.unique(np.r_[sol.t[sol.t<end],end]); mids=(knots[1:]+knots[:-1])/2; widths=np.diff(knots)/2
        for z,w in ((-.7745966692414834,5/9),(0.,8/9),(.7745966692414834,5/9)):
            tq=mids+z*widths; yq=sol.sol(tq); aq=air(tq)
            for j in range(len(tq)):
                dy,qt,qc,co=kernel(yq[:,j],x,v,g,half,*aq[j],False,25.,8e-7,1.)
                integrals+=w*widths[j]*np.array([qt,qc,co])
                cq=yq[1::2,j]; caps=(650+128*cq)*(1450+2736*cq/(1+cq))
                max_identity=np.maximum(max_identity,[abs(v@dy[1::2]+qc),abs((v*caps)@dy[0::2]+qt)])
        y=sol.sol(end)
        if crossing is not None: break
        if right>=72*3600:
            if right>=720*3600: raise RuntimeError('No crossing within 30 days; reassess model')
            intervals.append((right,right+24*3600))
    times=np.array(times); states=np.array(states)
    if not np.isfinite(states).all() or np.min(states[:,1::2])<=0: raise RuntimeError('Invalid state; no clipping')
    sampled=sample_many(states.T,x,half,air(times),False,25.,8e-7,1.)
    sampled[0,:,0]=28.;sampled[0,:,1]=2.55
    caps=np.array([properties(y[2*i],y[2*i+1],False,1.)[0] for i in range(n)])
    cap0=properties(28.,2.55,False,1.)[0]
    mass0=v.sum()*2.55; energy0=v.sum()*cap0*28.
    balances=[v@y[1::2]-mass0+integrals[1],v@(caps*y[0::2])-energy0+integrals[0]-integrals[2]]
    allmax=np.maximum(np.max(states[:,1::2],axis=1),np.max(sampled[:,:,1],axis=1))
    radial_violation=float(np.max(np.diff(states[:,1::2],axis=1)))
    meta=dict(name=name,n=n,rtol=rtol,method=method,scenario=scenario,tail=tail.tolist(),
        crossing_s=crossing,minute_s=float(times[-1]),seconds=time.perf_counter()-begin,
        balances=balances,relative_balances=[abs(balances[0])/mass0,abs(balances[1])/energy0],
        integrals=integrals.tolist(),identity_abs=max_identity.tolist(),
        radial_increase_max=radial_violation,minimum=float(states[:,1::2].min()),**stats)
    np.savez_compressed(ROOT/'verification'/f'{name}.npz',time_s=times,radius_cm=np.arange(21)/10,
        T=sampled[:,:,0],C=sampled[:,:,1],maxC=allmax,means=states[:,1::2]@v/v.sum(),
        final_cells=y,x=x,v=v,metadata=json.dumps(meta))
    (ROOT/'verification'/f'{name}.json').write_text(json.dumps(meta,indent=2))
    print(json.dumps(meta),flush=True)
    return meta

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',default='base800');p.add_argument('--n',type=int,default=800)
    p.add_argument('--rtol',type=float,default=1e-10);p.add_argument('--method',default='BDF');p.add_argument('--scenario',default='base')
    a=p.parse_args();solve(**vars(a))
