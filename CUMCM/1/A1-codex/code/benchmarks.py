"""Independent analytic/sparse-ODE checks. Does not call the FV flux routine."""
import json,time,os
import numpy as np
from scipy.special import j0,j1,expi
from scipy.optimize import brentq
from scipy.integrate import solve_ivp
from scipy.sparse import diags
from solver import ROOT,R,RHO,CP,K,H,HM,T0,C0,integrate


def modes(biot,n=180):
    f=lambda z:z*j1(z)-biot*j0(z)
    scan=np.linspace(1e-9,(n+1)*np.pi,12*n+20)
    vals=f(scan)
    roots=[brentq(f,a,b,xtol=1e-14) for a,b,fa,fb in zip(scan[:-1],scan[1:],vals[:-1],vals[1:]) if fa*fb<0][:n]
    z=np.array(roots)
    assert len(z)==n
    coeff=2*j1(z)/(z*(j0(z)**2+j1(z)**2))
    return z,coeff


def analytic_constant(alpha,biot,initial,air,times,nmodes=180):
    z,a=modes(biot,nmodes)
    basis=a[:,None]*j0(z[:,None]*np.linspace(0,1,21))
    return air+(initial-air)*(np.exp(-np.asarray(times)[:,None]*alpha/R**2*z**2)@basis)


def exact_heat(nmodes=180):
    env=np.loadtxt(ROOT/'data/ambient.csv',delimiter=',',skiprows=1)
    z,a=modes(H*R/K,nmodes)
    rate=K/(RHO*CP*R**2)*z**2
    basis=a[:,None]*j0(z[:,None]*np.linspace(0,1,21))
    states=np.zeros(len(z));history=[np.full(21,T0)]
    for t in range(1,1801):
        i=min((t-1)//60,len(env)-2)
        slope=(env[i+1,1]-env[i,1])/60
        states=states*np.exp(-rate)+slope*(-np.expm1(-rate))/rate
        air=env[i,1]+slope*(t-env[i,0])
        history.append(air-states@basis)
    return np.array(history)


def harmonic_reference(n=200,power=2.,rtol=2e-10,atol=2e-12,method='harmonic'):
    """Independent method-of-lines: harmonic D at faces, BDF via SciPy sparse FD Jacobian.
    Same PDE; conventional frozen-last-cell D for half-cell Robin closure.
    All derivatives and geometry below are independently assembled.
    """
    edges=1-(1-np.linspace(0,1,n+1))**power
    x=(edges[1:]+edges[:-1])/2
    v=(edges[1:]**2-edges[:-1]**2)/2
    env=np.loadtxt(ROOT/'data/ambient.csv',delimiter=',',skiprows=1)
    stencil=diags([np.ones(n-1),np.ones(n),np.ones(n-1)],[-1,0,1],format='csc')
    def potential(c):
        return 7e-9/R**2*(c*np.exp(-.89/c)+.89*expi(-.89/c))
    def boundary(c,air):
        d=7e-9/R**2*np.exp(-.89/c)
        half=1-x[-1]
        cs=(d*c+half*(HM/R)*air)/(d+half*(HM/R))
        if method=='kirchhoff':
            for _ in range(8):
                f=potential(c)-potential(cs)-half*(HM/R)*(cs-air)
                delta=f/(7e-9/R**2*np.exp(-.89/cs)+half*(HM/R))
                cs+=delta
                if abs(delta)<2e-13:break
        return cs
    def rhs(t,c):
        d=7e-9/R**2*np.exp(-.89/c)
        df=2*d[:-1]*d[1:]/(d[:-1]+d[1:])
        q=np.zeros(n+1)
        q[1:-1]=edges[1:-1]*df*(c[:-1]-c[1:])/np.diff(x)
        if method=='kirchhoff':
            q[1:-1]=edges[1:-1]*(potential(c[:-1])-potential(c[1:]))/np.diff(x)
        air=np.interp(t,env[:,0],env[:,2])
        q[-1]=(HM/R)*(boundary(c[-1],air)-air)
        return (q[:-1]-q[1:])/v
    state=np.full(n,C0)
    hist=[np.full(21,C0)]
    start=time.perf_counter()
    from scipy.interpolate import make_interp_spline
    for left in range(0,1800,60):
        out=solve_ivp(rhs,[left,left+60],state,method='BDF',rtol=rtol,atol=atol,
                      t_eval=np.arange(left+1,left+61),jac_sparsity=stencil)
        assert out.success,out.message
        assert np.all(np.isfinite(out.y)), 'Non-finite independent reference'
        state=out.y[:,-1]
        for t,c in zip(out.t,out.y.T):
            values=make_interp_spline(x,c,k=2)(np.linspace(0,1,21))
            values[0]=(x[1]**2*c[0]-x[0]**2*c[1])/(x[1]**2-x[0]**2)
            air=np.interp(t,env[:,0],env[:,2])
            values[-1]=boundary(c[-1],air)
            hist.append(values)
    return np.array(hist),time.perf_counter()-start


def end_effect(dt=.5,nmodes=220):
    """Finite cylinder with BOTH flat ends convecting; compare midplane to radial model.
    Product step response + Duhamel integral with composite midpoint quadrature.
    Return temperature excess at midplane (finite - infinite cylinder).
    """
    alpha=K/(RHO*CP);halfL=.125
    z,a=modes(H*R/K,nmodes)
    bz=H*halfL/K
    mu=np.array([brentq(lambda u:u*np.tan(u)-bz,k*np.pi+1e-10,k*np.pi+np.pi/2-1e-10) for k in range(nmodes)])
    b=4*np.sin(mu)/(2*mu+np.sin(2*mu))
    lags=(np.arange(int(1800/dt))+.5)*dt
    sz=np.exp(-lags[:,None]*(alpha/halfL**2)*mu**2)@b
    sr=np.exp(-lags[:,None]*(alpha/R**2)*z**2)@(a[:,None]*j0(z[:,None]*np.linspace(0,1,21)))
    kernel=sr*(1-sz[:,None])
    env=np.loadtxt(ROOT/'data/ambient.csv',delimiter=',',skiprows=1)
    slopes=np.repeat(np.diff(env[:31,1])/60,int(60/dt))
    # discrete causal convolution of input slope with step-response difference
    from scipy.signal import fftconvolve
    arr=np.stack([fftconvolve(slopes,kernel[:,j])[:len(lags)]*dt for j in range(21)],axis=1)
    return arr[int(1/dt)-1::int(1/dt)]


def main():
    exact=exact_heat(); np.save(ROOT/'verification/heat_exact.npy',exact)
    checks={'heat_series_180_vs_360':float(np.max(np.abs(exact-exact_heat(360))))}
    times=np.arange(1801)
    for label,alpha,biot,initial,air,scale,beta in [
        ('heat',K/(RHO*CP),H*R/K,T0,50.,K/(RHO*CP*R**2),H/(RHO*CP*R)),
        ('moisture',7e-9*np.exp(-.89/C0),HM*R/(7e-9*np.exp(-.89/C0)),C0,.02,
         7e-9*np.exp(-.89/C0)/R**2,HM/R)]:
        coeff=np.zeros((4,1));coeff[3,0]=air
        num=integrate(800,1800,1.,1e-4,np.array([0.,1800.]),coeff,initial,scale,beta,False,2.)
        ref=analytic_constant(alpha,biot,initial,air,times[1:])
        checks[label+'_constant_max_abs_error']=float(np.max(np.abs(num[0][1:]-ref)))
        checks[label+'_constant_balance_max']=float(np.max(np.abs(num[2])))
        print(label,checks,flush=True)
    for n in [100,200,400,800]:
        path=ROOT/'verification'/f'harmonic_{n}.npz'
        if not path.exists() or os.environ.get('A1_RECOMPUTE')=='1':
            arr,sec=harmonic_reference(n)
            np.savez_compressed(path,C=arr,seconds=sec)
            print('harmonic',n,sec,arr[-1,[0,-1]],flush=True)
    effects=end_effect(.5,220)
    fine=end_effect(.25,320)
    np.save(ROOT/'verification/end_effect.npy',fine)
    checks['end_effect_max_C']=float(np.max(np.abs(fine)))
    checks['end_effect_refinement_difference_C']=float(np.max(np.abs(effects-fine)))
    checks['end_effect_final_center_C']=float(fine[-1,0])
    (ROOT/'verification/benchmarks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
    print(checks,flush=True)

if __name__=='__main__':main()
