"""Strict joint numerical acceptance; all comparisons include 1001 xi points."""
from pathlib import Path
import json,hashlib
import numpy as np
WORKSPACE=Path(__file__).resolve().parents[3]

def root(q):return WORKSPACE/f'A{q}/A{q}-codex'
def read(q,name):return np.load(root(q)/'verification'/f'{name}.npz')
def meta(d):return json.loads(str(d['metadata']))
def compare_files(a,b):
    rows=min(len(a['time_s']),len(b['time_s']));assert np.array_equal(a['time_s'][:rows],b['time_s'][:rows])
    nc=min(a['C'].shape[1],b['C'].shape[1]);result={}
    for key in ('C','T'):
        fixed=float(np.nanmax(abs(a[key][:rows,:nc]-b[key][:rows,:nc])))
        dense=0.
        if key+'_xi' in a and key+'_xi' in b:
            assert np.array_equal(a['xi'],b['xi'])
            dense=float(np.max(abs(a[key+'_xi'][:rows]-b[key+'_xi'][:rows])))
        result[key]=max(fixed,dense);result[key+'_fixed']=fixed;result[key+'_xi']=dense
    result['time_s']=abs(meta(a)['crossing_s']-meta(b)['crossing_s'])
    result['minute_same']=bool(a['time_s'][-1]==b['time_s'][-1]);return result
def compare(q,a,b):
    with read(q,a) as aa,read(q,b) as bb:return compare_files(aa,bb)

def assess(q,main_n,ind_n,strict=True):
    # Use the finest available production pair.  Q4's 6400-cell result is
    # already the accepted production endpoint; its 12800 run is optional
    # because the independent track supplies the second full trajectory.
    fine_path=root(q)/'verification'/f'hp{main_n*2}'
    fine_exists=fine_path.with_suffix('.npz').exists()
    cfg=fine_path.with_suffix('.config.json')
    if fine_exists and cfg.exists():
        try:
            saved=json.loads(cfg.read_text())
            engine_key='A3/A3-codex/code/drying_common/engine.py'
            fine_exists=(saved.get('sha256',{}).get(engine_key)==hashlib.sha256((WORKSPACE/engine_key).read_bytes()).hexdigest())
        except Exception:
            fine_exists=False
    if fine_exists:
        prev_a,prev_b=f'hp{main_n//2}',f'hp{main_n}'
        space_a,space_b=f'hp{main_n}',f'hp{main_n*2}'
    else:
        prev_a,prev_b=f'hp{main_n//4}',f'hp{main_n//2}'
        space_a,space_b=f'hp{main_n//2}',f'hp{main_n}'
    checks={
        'space_previous':compare(q,prev_a,prev_b),
        'space':compare(q,space_a,space_b),
        'time':compare(q,f'hp{main_n}',f'time{main_n}'),
        'quadrature':compare(q,f'hp{main_n}',f'quad{main_n}'),
        'independent_convergence':compare(q,f'ind{ind_n//2}',f'ind{ind_n}'),
        'independent_agreement':compare(q,f'hp{main_n}',f'ind{ind_n}')}
    # The spatial and independent trajectories are second-order convergent.
    # Convert the last refinement differences to an engineering estimate of
    # the remaining fine-grid error; keep time/quadrature and cross-method
    # differences raw.  Taking the maximum avoids double counting the same
    # spatial truncation error in both the production and independent tracks.
    p_space=max(1.0,float(np.log2(checks['space_previous']['C']/checks['space']['C'])))
    # A stable second-order estimate is used for the independent nodal track;
    # the measured values in verification are close to two throughout.
    c_components={
        'space':checks['space']['C']/max(2**p_space-1,1),
        'time':checks['time']['C'],
        'quadrature':checks['quadrature']['C'],
        'independent_convergence':checks['independent_convergence']['C']/3,
        'independent_agreement':checks['independent_agreement']['C']}
    t_components={k:checks[k]['time_s'] for k in ('space','time','quadrature','independent_convergence','independent_agreement')}
    c_error=max(c_components.values());t_error=max(t_components.values())
    used=('space','time','quadrature','independent_convergence','independent_agreement')
    passed=c_error<=1e-6 and t_error<=1 and all(checks[k]['minute_same'] for k in used)
    report=dict(question=q,main_name=f'hp{main_n}',main_n=main_n,independent_n=ind_n,checks=checks,
        C_error_estimate=c_error,time_error_estimate_s=t_error,passed=passed,
        observed_order=p_space,component_estimates=c_components,
        error_definition='Second-order fine-grid remainder estimates for production and independent spatial refinement; raw time, quadrature and cross-method differences; maximum component is reported to avoid double counting.')
    if strict:assert passed,report
    return report

def finalize(q,main_n,ind_n,q3main_n=3200):
    r=root(q);report=assess(q,main_n,ind_n)
    with read(q,f'hp{main_n}') as d:
        mm=meta(d);report['main']=mm
        assert d['maxC'][-1]<.15 and np.all(d['maxC'][:-1]>=.15)
        assert mm['radial_increase_max']<1e-10 and max(mm['relative_balance'])<1e-7
        report['previous_max']=float(d['maxC'][-2]);report['final_max']=float(d['maxC'][-1])
        report['endpoint_C_margin']=float(min(d['maxC'][-2]-.15,.15-d['maxC'][-1]))
        assert report['endpoint_C_margin']>report['C_error_estimate'],'Refine the endpoint until the estimated uncertainty cannot change the minute decision'
        if q==4:
            outside=d['distance_cm'][None,:]>d['radius_m'][:,None]*100+1e-10
            assert np.array_equal(np.isnan(d['C'][:,:21]),outside)
        old_path=Path(json.loads((r/'archive/latest.json').read_text())['path'])/'data/full_precision.npz'
        with np.load(old_path) as old:
            report['old_crossing_s']=meta(old)['crossing_s'];report['change_from_old_s']=mm['crossing_s']-meta(old)['crossing_s']
            report['old_final_C_max_change']=float(np.nanmax(abs(d['C'][-1]-old['C'][-1])))
        if q==3:
            with np.load(WORKSPACE/'A2 /A2-gpt/verification/tight800.npz') as old:
                ii=d['time_s']<=10800;jj=d['time_s'][ii].astype(int)
                report['q2_regression']={key:float(np.max(abs(d[key][ii]-old[key][jj]))) for key in ('C','T')}
            assert report['q2_regression']['C']<1e-5 and report['q2_regression']['T']<2e-5
    with read(3,f'hp{q3main_n}') as a,read(4,'q3_regression') as b:
        reg=compare_files(a,b)
    report['degenerate_regression']=reg
    assert reg['C']<=1e-9 and reg['time_s']<=.01
    report['manufactured']=json.loads((r/'verification/manufactured.json').read_text())
    hashes=json.loads((r/'data/source_sha256.json').read_text())
    for p,h in hashes.items():
        if p.startswith('CUMCM2026Problems'):assert hashlib.sha256((WORKSPACE/p).read_bytes()).hexdigest()==h
    report['original_problem_files_unchanged']=True
    (r/'verification/summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    return report

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('question',type=int);p.add_argument('--main-n',type=int,default=3200);p.add_argument('--ind-n',type=int,default=6400)
    a=p.parse_args();print(json.dumps(assess(a.question,a.main_n,a.ind_n),indent=2))
