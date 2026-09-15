"""Quantitative acceptance checks and data export. Does not author XLSX."""
import json,sys,hashlib,platform,shutil
from pathlib import Path
import numpy as np
import scipy,numba
from scipy.integrate import quad
from solver import ROOT,properties,face,boundary,kernel,mesh

def load(name):return np.load(ROOT/'verification'/f'{name}.npz')
def maximum(a,b):return {k:float(np.max(np.abs(a[k]-b[k]))) for k in ('T','C')}
def write(name,data): (ROOT/'verification'/name).write_text(json.dumps(data,ensure_ascii=False,indent=2))

z=load('tight800'); fine=load('tight1600');radau=load('radau800')
coarse=[load(f'base{n}') for n in (200,400,800)]
diffs=[maximum(coarse[i],coarse[i+1]) for i in (0,1)]
spacediff=maximum(z,fine); timediff=maximum(z,coarse[-1]); methods=maximum(z,radau)
order={k:float(np.log2(diffs[0][k]/diffs[1][k])) for k in ('T','C')}
error={k:4/3*spacediff[k]+timediff[k]+methods[k] for k in ('T','C')}
assert all(1.8<p<2.2 for p in order.values()),order
assert all(e<2e-5 for e in error.values()),error
a1=np.load(ROOT/'data/a1_reference.npz'); q1=load('q1_800')
reg={k:float(np.max(np.abs(q1[k]-a1[ak]))) for k,ak in [('T','T_C'),('C','C_kgkg')]}
assert all(e<2e-5 for e in reg.values()),reg
q2_a1={k:float(np.max(abs(z[k][:1801]-a1[ak]))) for k,ak in [('T','T_C'),('C','C_kgkg')]}
b=z['balances'];heat_scale=abs(b[-1,3]);mass_scale=abs(b[-1,4])
balance={'mass_abs':float(max(abs(b[:,1]))),'mass_relative':float(max(abs(b[:,1]))/mass_scale),
         'heat_identity_abs':float(max(abs(b[:,2]))),'heat_identity_relative':float(max(abs(b[:,2]))/heat_scale),
         'note':'Balances omit common 2*pi*length. Heat identity includes the integral of A_prime(C)*T*C_t; it is not total physical energy.'}
assert balance['mass_relative']<1e-7 and balance['heat_identity_relative']<1e-7
np.savetxt(ROOT/'verification/balance.csv',b,delimiter=',',header='time_s,mass_residual,heat_identity_residual,integral_QT,integral_QC,capacity_correction',comments='')

# Unit-level invariants independent of output data.
cap,k,d,ap=properties(28.,2.55,False,1.)
assert np.isclose(cap,(650+128*2.55)*(1450+2736*2.55/3.55),rtol=1e-14)
assert np.isclose(d,.0024*np.exp(-.45/2.55)*np.exp(-3850/301.15),rtol=1e-14)
delta=1e-5
apr=(properties(28.,2.55+delta,False,1.)[0]-properties(28.,2.55-delta,False,1.)[0])/(2*delta)
assert abs(apr/ap-1)<1e-8
x,v,g,half=mesh(200); yy=np.tile([28.,2.55],200)
eq=kernel(yy,x,v,g,half,28.,2.55,False,25.,8e-7,1.)[0]
assert np.max(abs(eq))<1e-8
# Actual final-profile boundary residual and all-face quadrature error.
cells=z['final_cells'];x=z['x_m'];half=.02-x[-1]
env=np.loadtxt(ROOT/'data/ambient.csv',delimiter=',',skiprows=1)
ta,ca=env[env[:,0]==10800,1:][0]
ts,cs,qt,qc=boundary(cells[-2],cells[-1],ta,ca,half,False,25.,8e-7,1.)
kk,dd=face(cells[-2],cells[-1],ts,cs,False,1.)
surf={'heat_residual_W_m2':float(kk*(cells[-2]-ts)/half-qt),
      'moisture_residual_m_s':float(dd*(cells[-1]-cs)/half-qc)}
face_err=[]
for i in range(0,len(x)-1,13):
    t1,c1,t2,c2=cells[2*i:2*i+4]
    kk,dd=face(t1,c1,t2,c2,False,1.)
    truth=quad(lambda s: .0024*np.exp(-.45/(c1+s*(c2-c1))-3850/(t1+s*(t2-t1)+273.15)),0,1,epsabs=1e-20)[0]
    face_err.append(abs(dd/truth-1))
tests={'equilibrium_rhs_max':float(np.max(abs(eq))),'capacity_derivative_relative_error':float(abs(apr/ap-1)),
       'sampled_final_face_quadrature_max_relative_error':float(max(face_err)),**surf}
assert abs(surf['heat_residual_W_m2'])<1e-5 and abs(surf['moisture_residual_m_s'])<1e-12
assert tests['sampled_final_face_quadrature_max_relative_error']<1e-10

sens=[]
for name in ['hfactor_0.95','hfactor_1.05','hmfactor_0.95','hmfactor_1.05','dfactor_0.95','dfactor_1.05','pchip400']:
    zz=load(name); change=maximum(zz,coarse[1]); row={'scenario':name,**{f'max_delta_{k}':val for k,val in change.items()}}
    for k in ('T','C'):
        row[f'final_surface_delta_{k}']=float(zz[k][-1,-1]-coarse[1][k][-1,-1])
        row[f'final_center_delta_{k}']=float(zz[k][-1,0]-coarse[1][k][-1,0])
    sens.append(row)
write('sensitivity.json',sens)

manifest=json.loads((ROOT/'data/source_sha256.json').read_text()); work=ROOT.parents[1]
unchanged=all(hashlib.sha256((work/p).read_bytes()).hexdigest()==v for p,v in manifest.items())
assert unchanged
summary={'environment':{'python':sys.version,'executable':sys.executable,'platform':platform.platform(),
                       'numpy':np.__version__,'scipy':scipy.__version__,'numba':numba.__version__},
         'selected_run':'tight800','settings':json.loads(str(z['metadata'])),
         'space_differences_200_400_800':diffs,'observed_order':order,'space_difference_800_1600':spacediff,
         'time_tightening_difference':timediff,'BDF_Radau_difference':methods,'estimated_errors':error,
         'target':2e-5,'numerical_target_pass':True,'a1_regression':reg,'q2_vs_a1_first1800':q2_a1,
         'balances':balance,'unit_checks':tests,'input_hashes_unchanged':unchanged,
         'range':{k:[float(z[k].min()),float(z[k].max())] for k in ('T','C')},
         'final':{'T_center':float(z['T'][-1,0]),'T_surface':float(z['T'][-1,-1]),
                  'C_center':float(z['C'][-1,0]),'C_surface':float(z['C'][-1,-1]),'volume_mean_T':float(z['means'][-1,0]),'volume_mean_C':float(z['means'][-1,1])}}
write('summary.json',summary)
shutil.copyfile(ROOT/'verification/tight800.npz',ROOT/'data/full_precision.npz')
for key,name in [('T','temperature'),('C','moisture')]:
    np.savetxt(ROOT/f'data/{name}_full_precision.csv',np.column_stack((z['time_s'],z[key])),delimiter=',',fmt='%.15g',
               header='time_s,'+','.join(f'r_{r:.1f}_cm' for r in z['radius_cm']),comments='')
payload={'time_s':z['time_s'][1:].tolist(),'radius_cm':z['radius_cm'].tolist(),
         '温度':np.round(z['T'][1:],4).tolist(),'水分浓度':np.round(z['C'][1:],4).tolist()}
(ROOT/'data/workbook_values.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')))
print(json.dumps(summary,ensure_ascii=False,indent=2))
