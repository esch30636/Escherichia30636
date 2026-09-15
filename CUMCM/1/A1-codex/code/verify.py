"""Meaningful scientific regressions and delivery consistency checks."""
import json,hashlib,re
import numpy as np
from solver import ROOT,integrate,make_grid,surface,R,K,RHO,CP,H,HM

def main():
    checks={}
    for nonlinear,initial,air,beta,label in [(True,2.55,2.55,HM/R,'moisture_equilibrium'),
        (False,28.,28.,H/(RHO*CP*R),'heat_equilibrium'),
        (True,2.55,.02,0.,'insulated_moisture'),(False,28.,50.,0.,'insulated_heat')]:
        coeff=np.zeros((4,1));coeff[3,0]=air
        scale=7e-9/R**2 if nonlinear else K/(RHO*CP*R**2)
        out=integrate(50,10,1.,0.,np.array([0.,10.]),coeff,initial,scale,beta,nonlinear,2.)
        err=float(np.max(np.abs(out[0]-initial)))
        assert err<1e-10
        checks[label+'_max_error']=err
    s=json.loads((ROOT/'verification/summary.json').read_text(encoding='utf-8'))
    assert s['all_numeric_checks_passed']
    w=json.loads((ROOT/'verification/workbook_check.json').read_text(encoding='utf-8'))
    assert w['all_passed']
    data=np.load(ROOT/'data/full_precision.npz')
    payload=json.loads((ROOT/'data/workbook_values.json').read_text(encoding='utf-8'))
    for label,key in [('温度','T_C'),('水分浓度','C_kgkg')]:
        assert np.array_equal(np.round(data[key][1:],4),np.array(payload[label]))
    report=(ROOT/'建模报告.md').read_text(encoding='utf-8')
    for name in re.findall(r'!\[[^\]]*\]\(([^)]+)\)',report):assert (ROOT/name).is_file()
    assert '@TABLE' not in report and 'NaN' not in report.replace('NaN、无穷、负含水率','')
    # Verify all 70 report table entries against the original full-precision arrays.
    times=[100,300,600,900,1200,1500,1800]
    for label,key in [('表1','T_C'),('表2','C_kgkg')]:
        part=report.split('### '+label+'：')[1]
        rows=re.findall(r'^\| (\d+) \| ([^\n]+)$',part,re.M)[:7]
        assert len(rows)==7
        for (time,values),t in zip(rows,times):
            assert int(time)==t
            actual=[x.strip() for x in values.rstrip('|').split('|')]
            assert actual==[f'{v:.4f}' for v in data[key][t,[0,5,10,15,20]]]
    checks['report_table_entries_checked']=70
    checks['workbook_values_checked']=75600
    source=ROOT.parent/'CUMCM2026Problems/A题'
    hashes=json.loads((ROOT/'data/source_sha256.json').read_text(encoding='utf-8'))
    for rel,digest in hashes.items():assert hashlib.sha256((source/rel).read_bytes()).hexdigest()==digest
    checks['source_files_unchanged']=True
    checks['all_passed']=True
    (ROOT/'verification/final_checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
    print(json.dumps(checks,indent=2))

if __name__=='__main__':main()
