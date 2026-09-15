"""Read original inputs without modifying them; record provenance."""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
import openpyxl
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT.parents[1]
def main():
    for name in ('data','verification','figures'): (ROOT/name).mkdir(exist_ok=True)
    sources=['CUMCM2026Problems/A题/A题.pdf','CUMCM2026Problems/A题/附件/附件1.xlsx',
      'CUMCM2026Problems/A题/附件/附件2.xlsx','CUMCM2026Problems/A题/附件/附件3/result4.xlsx',
      'A3/A3-codex/code/core.py','A3/A3-codex/code/solve.py',
      'A3/A3-codex/data/full_precision.npz','A2 /A2-gpt/code/solver.py',
      'A1/A1-codex/建模报告.md']
    hashes={s:hashlib.sha256((WORK/s).read_bytes()).hexdigest() for s in sources}
    for name,src,header in [('ambient','附件1.xlsx','time_s,T_C,C_air_kgkg'),('radius','附件2.xlsx','time_s,radius_cm')]:
        w=openpyxl.load_workbook(WORK/'CUMCM2026Problems/A题/附件'/src,read_only=True,data_only=True)
        a=np.asarray(list(w.active.values)[1:],float); w.close()
        assert np.all(np.diff(a[:,0])>0) and np.isfinite(a).all()
        if name=='radius': assert a[0,1]==2 and np.all(np.diff(a[:,1])<=0)
        np.savetxt(ROOT/'data'/f'{name}.csv',a,delimiter=',',header=header,comments='',fmt='%.17g')
    shutil.copyfile(WORK/sources[3],ROOT/'data/result4_template.xlsx')
    (ROOT/'data/source_sha256.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
