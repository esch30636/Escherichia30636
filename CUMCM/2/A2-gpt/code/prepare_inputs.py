"""Read-only extraction of supplied workbooks; reproducibility manifest."""
from pathlib import Path
import csv,json,hashlib,shutil
from openpyxl import load_workbook
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT.parents[1]
for d in ('data','figures','verification','references'):(ROOT/d).mkdir(parents=True,exist_ok=True)
source=WORK/'CUMCM2026Problems/A题'
w=load_workbook(source/'附件/附件1.xlsx',read_only=True,data_only=True)
rows=list(w.worksheets[0].values);w.close()
assert rows[0]==('时间','温度','水分浓度') and len(rows)==242
assert rows[1][0]==0 and rows[-1][0]==14400
with (ROOT/'data/ambient.csv').open('w',newline='') as f:
    cw=csv.writer(f);cw.writerow(['time_s','air_T_C','air_C_kgkg']);cw.writerows(rows[1:])
files=[source/'A题.pdf',source/'附件/附件1.xlsx',source/'附件/附件3/result2.xlsx',
       WORK/'A1/A1-codex/data/full_precision.npz']
manifest={str(p.relative_to(WORK)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(ROOT/'data/source_sha256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
shutil.copyfile(files[2],ROOT/'data/result2_template.xlsx')
shutil.copyfile(files[3],ROOT/'data/a1_reference.npz')
print('Inputs extracted; source manifest saved.')
