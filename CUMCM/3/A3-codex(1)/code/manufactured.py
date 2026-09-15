"""Fixed/moving manufactured solutions plus insulated homogeneous shrinkage."""
from pathlib import Path
import json
import numpy as np
from scipy.integrate import solve_ivp
from drying_common import core,independent
ROOT=Path(__file__).resolve().parents[1]

def exact(x,t):return 35+3*np.sin(t/3000)+4*x*x,1+.1*np.sin(t/2000)-.2*x*x
def geometry(t,moving):return .02*(1-.1*t/3600) if moving else .02
def local(T,C):
    a=(650+128*C)*(1450+2736*C/(1+C));k=.21+.38*C/(1+C)
    D=.0024*np.exp(-.45/C-3850/(T+273.15))
    return a,k,D
def test(n,moving,backend):
    op=core if backend=='production' else independent
    x,v,g,half=op.mesh(n);nn=len(x);T,C=exact(x,0);initial=np.column_stack((T,C)).ravel()
    def rhs(t,y):
        R=geometry(t,moving);Te,Ce=exact(x,t);cap,k,D=local(Te,Ce)
        ts,cs=exact(1.,t);_,ks,ds=local(ts,cs)
        ta=ts+ks*8/(R*25);ca=cs+ds*(-.4)/(R*8e-7)
        dy=op.kernel(y,x,v,g,half,R,ta,ca,3)[0]
        dt=.001*np.cos(t/3000);dc=.00005*np.cos(t/2000)
        divT=(16*k+4*.38/(1+Ce)**2*(-.2)*4*x*x)/R**2
        divC=(-.8*D+4*(-.2)*x*x*(D*.45/Ce**2*(-.2)+D*3850/(Te+273.15)**2*4))/R**2
        dy[0::2]+=dt-divT/cap;dy[1::2]+=dc-divC
        return dy
    sol=solve_ivp(rhs,(0,3600),initial,method='BDF' if backend=='production' else 'Radau',
        jac_sparsity=op.sparsity(nn),rtol=1e-11,atol=1e-12,max_step=30.)
    assert sol.success
    T,C=exact(x,3600)
    return dict(n=n,T=float(np.max(abs(sol.y[0::2,-1]-T))),C=float(np.max(abs(sol.y[1::2,-1]-C))))

def main():
    records={}
    for backend in ('production','independent'):
        for moving in (False,True):
            key=backend+('_moving' if moving else '_fixed');rows=[test(n,moving,backend) for n in (40,80,160)]
            rows[-1]['observed_T_order']=float(np.log2(rows[-2]['T']/rows[-1]['T']))
            rows[-1]['observed_C_order']=float(np.log2(rows[-2]['C']/rows[-1]['C']))
            assert rows[-1]['observed_T_order']>1.7 and rows[-1]['observed_C_order']>1.7,(key,rows)
            records[key]=rows
        op=core if backend=='production' else independent;x,v,g,half=op.mesh(80);y=np.tile([28.,2.55],len(x))
        def rhs(t,state):return op.kernel(state,x,v,g,half,geometry(t,True),28.,2.55,4,0.,0.)[0]
        sol=solve_ivp(rhs,(0,3600),y,method='BDF',jac_sparsity=op.sparsity(len(x)),rtol=1e-11,atol=1e-12)
        assert sol.success
        error=float(np.max(abs(sol.y-y[:,None])));assert error<1e-12
        records[backend+'_uniform_no_exchange']=error
    for q in (3,4):
        dest=ROOT.parents[1]/f'A{q}/A{q}-codex/verification/manufactured.json'
        dest.write_text(json.dumps(records,indent=2))
    print(json.dumps(records,indent=2))
if __name__=='__main__':main()
