"""Read-only numerical/workbook checks; writes a compact verification report."""
import json
from pathlib import Path
import numpy as np
import openpyxl
from PIL import Image
from a4_output import SCENARIOS, LATENT, load
from a4_run import Q4Solver, chamber_tail
import a4_model as M

ROOT = Path(__file__).resolve().parent
names = ['q4_tight800','q4_t50_tight800','q4_t50_tight1600',
         'conv_graded400','conv_graded800','conv_graded1600',
         'conv_uniform400','conv_uniform800','q3_x800','q3_x1600','scen3_t50']
names += ['scen_'+s for s,_ in SCENARIOS]
names += [n for n,_ in LATENT if n!='scen_final']
names += ['q3_lat_surf_dry0_t50','q4_lat_surf_dry0_t50','q4_fixed_props_control']
report = {'cases': [], 'workbooks': [], 'figures': []}
for name in names:
    z,m = load(name)
    ts, ys, fs = z['time_s'], z['states'], z['field']
    assert np.all(np.diff(ts)>0) and ts[0]==0
    expected = np.arange(0, m['minute_s']+1e-6, m['sample_dt'])
    if expected[-1] < m['minute_s']-1e-6:
        expected = np.r_[expected, m['minute_s']]
    np.testing.assert_allclose(ts, expected, rtol=0, atol=1e-6)
    assert np.isfinite(ys).all() and np.isfinite(fs).all()
    assert m['crossing_s'] < m['minute_s'] <= m['crossing_s']+60
    assert fs[-1,:,1].max()<.15
    assert np.max(np.diff(ys[:,1::2],axis=1))<=1e-10
    s=Q4Solver(n=m['n'], mesh=m['mesh'], scenario=m['scenario'],
               latent=m['latent'], appx=m['appx'], radius_mode=m['radius_mode'])
    assert s.make_event()(ts[-1],ys[-1])<0
    for i in [0,1,len(ts)//2,len(ts)-1]:
        R=float(s.R_of(ts[i]))
        rho=s.rho_d0 if not m['latent'] or m['latent']['rho']=='dry0' else 1.
        surf=M.boundary(ys[i,-2],ys[i,-1],*s.air(ts[i]),s.half,R,
                        M.HCONV,M.HM,s.df,s.lmode,rho*(M.R0/R)**2,s.lv,s.appx)
        np.testing.assert_allclose(fs[i,-1],surf[:2],rtol=0,atol=1e-11)
    six=np.r_[np.arange(21600.,ts[-1],21600.),ts[-1]]/3600
    np.testing.assert_allclose(z['table6_times'],six,rtol=0,atol=1e-10)
    idx=[np.argmin(abs(ts-t*3600)) for t in six]
    np.testing.assert_allclose(z['table6_field'],s.sample(ys[idx],ts[idx],np.array([0.,.5,1.])),rtol=0,atol=1e-11)
    report['cases'].append({'name':name,'samples':len(ts),'status':'PASS'})
assert len(names)==25

for name,filename in [('q4_tight800','result4.xlsx'),('q4_t50_tight800','result4_50度设定值.xlsx')]:
    z,m=load(name)
    wb=openpyxl.load_workbook(ROOT/filename,read_only=True,data_only=True)
    ws=wb.active
    rows=list(ws.values)
    expected=np.column_stack([z['time_s'][1:], np.round(z['field'][1:,:,1],4)])
    actual=np.array(rows[1:],dtype=float)
    assert actual.shape==expected.shape
    assert np.array_equal(actual,expected), f'Workbook differs: {filename}'
    assert z['field'][-2,:,1].max()>=.15 and z['field'][-1,:,1].max()<.15
    report['workbooks'].append({'name':filename,'rows':len(actual),
          'numeric_cells':actual.size,'mismatches':int(np.count_nonzero(actual!=expected))})
    wb.close()

for path in sorted((ROOT.parent/'04-pic').glob('fig*.png')):
    with Image.open(path) as im:
        assert min(im.size)>1000
        dpi=im.info.get('dpi',(0,0))
        assert min(dpi)>299
        report['figures'].append({'name':path.name,'size':im.size,'dpi':dpi})
assert len(report['figures'])==6
with Image.open(ROOT.parent/'04-pic/fig01_drying.png') as a, Image.open(ROOT.parent/'04-pic/fig02_drying_t50.png') as b:
    # Exclude the title and the radius panel: verify the actual curve pixels differ.
    aa,bb=np.array(a),np.array(b)
    h,w=aa.shape[:2]
    assert np.any(aa[int(h*.25):int(h*.80),int(w*.12):int(w*.43)] !=
                  bb[int(h*.25):int(h*.80),int(w*.12):int(w*.43)])

s=Q4Solver(n=3,scenario='smooth11')
assert np.array_equal(s.T_ch[-1:],np.array([chamber_tail('smooth11')[0]]))
assert s.T_ch[-1] > 45   # no zero-padding endpoint collapse
for rho in ['dry','bulk']:
    try:
        Q4Solver(n=3,latent={'mode':'surf','rho':rho})
    except ValueError:
        pass
    else:
        raise AssertionError('Deprecated density accepted')
table=np.loadtxt(ROOT/'table6.csv',delimiter=',',skiprows=1)
z,_=load('q4_tight800')
np.testing.assert_allclose(table,np.round(np.column_stack([z['table6_times'],z['table6_field'][:,:,1]]),4),rtol=0,atol=0)
report['status']='PASS'
report['limitations']=['Screenshotted Q1/Q2 temperatures not independently recomputed.',
                      'Numerical checks do not validate physical density or phase-change closure.']
(ROOT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':report['status'],'cases':len(names),'workbooks':report['workbooks'],
                  'figures':len(report['figures'])},ensure_ascii=False,indent=2))
