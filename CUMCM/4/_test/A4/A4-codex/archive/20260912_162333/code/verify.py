"""Numerical comparisons plus independent NumPy/Brent operator checks."""
from pathlib import Path
import json,hashlib,platform
import numpy as np
import scipy,numba
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from core import mesh,kernel,sparsity
from solve import Inputs
ROOT=Path(__file__).resolve().parents[1]
def read(n):return np.load(ROOT/'verification'/f'{n}.npz')
def meta(d):return json.loads(str(d['metadata']))
def compare(a,b):
 a,b=read(a),read(b);n=min(len(a['time_s']),len(b['time_s']))
 assert np.array_equal(a['time_s'][:n],b['time_s'][:n])
 return dict(C=float(max(np.nanmax(abs(a['C'][:n]-b['C'][:n])),np.max(abs(a['C_xi'][:n]-b['C_xi'][:n])))),
 T=float(max(np.nanmax(abs(a['T'][:n]-b['T'][:n])),np.max(abs(a['T_xi'][:n]-b['T_xi'][:n])))),
 crossing_s=abs(meta(a)['crossing_s']-meta(b)['crossing_s']))

def independent(y,R,ta,ca):
 # No calls to the production property, face or boundary functions.
 n=len(y)//2;f=1-(1-np.linspace(0,1,n+1))**2;x=(f[1:]+f[:-1])/2;v=np.diff(f*f)/2
 t=y[0::2];c=y[1::2]
 def coeff(t1,c1,t2,c2):
  z=np.array([.5-np.sqrt(15)/10,.5,.5+np.sqrt(15)/10]);w=np.array([5,8,5])/18
  cc=np.asarray(c1)[...,None]+z*(np.asarray(c2)-c1)[...,None]
  tt=np.asarray(t1)[...,None]+z*(np.asarray(t2)-t1)[...,None]
  return (.12+.20*cc/(1+cc))@w,(.00042*np.exp(-.30/cc-3850/(tt+273.15)))@w
 delta=R*(1-x[-1])
 def surfT(cs):
  def eq(ts):return coeff(t[-1],c[-1],ts,cs)[0]*(t[-1]-ts)-25*delta*(ts-ta)
  if t[-1]==ta:return ta
  return brentq(eq,min(t[-1],ta),max(t[-1],ta),xtol=1e-13)
 def eqc(cs):return coeff(t[-1],c[-1],surfT(cs),cs)[1]*(c[-1]-cs)-8e-7*delta*(cs-ca)
 cs=brentq(eqc,min(c[-1],ca),max(c[-1],ca),xtol=1e-14);ts=surfT(cs)
 k,d=coeff(t[:-1],c[:-1],t[1:],c[1:]);g=f[1:-1]/np.diff(x)
 qt=np.r_[0,g*k*(t[:-1]-t[1:]),R*25*(ts-ta)]
 qc=np.r_[0,g*d*(c[:-1]-c[1:]),R*8e-7*(cs-ca)]
 cap=(760+90*c)*(1850+2150*c/(1+c));dy=np.empty_like(y)
 dy[0::2]=-np.diff(qt)/(R*R*v*cap);dy[1::2]=-np.diff(qc)/(R*R*v)
 return dy

def main():
 pairs={'400_to_800':('base400','base800'),'800_to_1600':('tight800','fine1600'),
  'tolerance':('base800','tight800'),'BDF_vs_Radau':('base400','radau400')}
 checks={k:compare(*v) for k,v in pairs.items()}
 error=sum(checks[k]['C'] for k in ('800_to_1600','tolerance','BDF_vs_Radau'))
 assert error<2e-5,(error,'refine mesh')
 main=read('tight800');mm=meta(main)
 for name in ('base400','base800','tight800','fine1600','radau400','q3_regression800','fixed4_800',
              's_pchip','s_temp_low','s_temp_high','s_humid_low','s_humid_high'):
  d=read(name);m=meta(d)
  assert m['radial_increase_max']<1e-10
  assert max(m['relative_balance'])<2e-7
  assert d['maxC'][-1]<.15 and np.all(d['maxC'][:-1]>=.15)
  assert np.allclose(np.diff(d['time_s']),60)
  mask=d['distance_cm'][None,:]>d['radius_m'][:,None]*100+1e-10
  assert np.array_equal(np.isnan(d['C'][:,:21]),mask)
  assert np.array_equal(np.isnan(d['T'][:,:21]),mask)
 old=np.load(ROOT.parents[1]/'A3/A3-codex/data/full_precision.npz');reg=read('q3_regression800')
 assert np.array_equal(old['time_s'],reg['time_s'])
 regression={k:float(np.max(abs(old[k]-reg[k][:,:21]))) for k in ('T','C')}
 regression['crossing_s']=abs(meta(reg)['crossing_s']-meta(old)['crossing_s'])
 assert regression['C']<2e-7 and regression['T']<2e-7 and regression['crossing_s']<.1
 # Uniform, insulated drying material must retain the same dry-basis C while R changes.
 x,v,g,half=mesh(80);inp=Inputs();initial=np.tile([28.,2.55],80)
 def rhs(t,y):return kernel(y,x,v,g,half,inp.radius(t)[0],28.,2.55,4,0.,0.)[0]
 sol=solve_ivp(rhs,(0,259200),initial,method='BDF',jac_sparsity=sparsity(80),rtol=1e-10,atol=1e-12,max_step=1800)
 uniform=float(np.max(abs(sol.y-initial[:,None])));assert sol.success and uniform<1e-10
 independent_checks=[]
 for y,r,ta,ca in [(main['final_cells'],float(main['radius_m'][-1]),*inp.air(main['time_s'][-1])),
  (np.column_stack((40+8*main['x']**2,.5-.25*main['x']**2)).ravel(),.015,50.,.05)]:
  xx,vv,gg,hh=mesh(len(y)//2);actual=kernel(y,xx,vv,gg,hh,r,ta,ca,4)[0];expected=independent(y,r,ta,ca)
  delta=float(np.max(abs(expected-actual)));scale=float(np.max(abs(expected)))
  independent_checks.append(dict(max_abs=delta,relative=delta/max(scale,1e-30)))
  assert np.allclose(actual,expected,rtol=2e-6,atol=2e-8)
 hashes=json.loads((ROOT/'data/source_sha256.json').read_text())
 assert all(hashlib.sha256((ROOT.parents[1]/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
 sensitivity=[]
 for name in ('s_pchip','s_temp_low','s_temp_high','s_humid_low','s_humid_high'):
  m=meta(read(name));sensitivity.append(dict(name=name,h=m['crossing_s']/3600,delta_h=(m['crossing_s']-meta(read('base400'))['crossing_s'])/3600))
 summary=dict(comparisons=checks,C_error_estimate=error,observed_order=float(np.log2(checks['400_to_800']['C']/checks['800_to_1600']['C'])),
  regression=regression,uniform_insulated_max_error=uniform,independent_operator=independent_checks,
  sensitivity=sensitivity,main=mm,source_hashes_unchanged=True,
  versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,numba=numba.__version__))
 (ROOT/'verification/summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
