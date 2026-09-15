"""Read source workbooks; no workbook authoring. Bundled Python compatible."""
from pathlib import Path
import csv, json, hashlib
from openpyxl import load_workbook

root=Path(__file__).resolve().parents[1]
source=root.parent/'CUMCM2026Problems/A题'
w=load_workbook(source/'附件/附件1.xlsx',read_only=True,data_only=True)
rows=list(w.worksheets[0].values)
w.close()
assert rows[0]==('时间','温度','水分浓度')
assert len(rows)==242 and all(len(r)==3 for r in rows)
assert rows[1][0]==0 and rows[-1][0]>=1800
assert all(rows[i+1][0]-rows[i][0]==60 for i in range(1,len(rows)-1))
with (root/'data/ambient.csv').open('w',newline='',encoding='utf-8') as f:
    writer=csv.writer(f); writer.writerow(['time_s','air_T_C','air_C_kgkg']); writer.writerows(rows[1:])
manifest={str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
          [source/'A题.pdf',source/'附件/附件1.xlsx',source/'附件/附件3/result1.xlsx']}
(root/'data/source_sha256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Read 241 environment observations; source hashes saved.')
