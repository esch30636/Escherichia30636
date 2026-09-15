"""Recheck the current high-precision selection (does not rerun solves)."""
from pathlib import Path
import sys,os
ROOT=Path(__file__).resolve().parents[1]
COMMON_CODE=ROOT.parents[1]/'A3/A3-codex/code'
if str(COMMON_CODE) not in sys.path:sys.path.insert(0,str(COMMON_CODE))
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'verification/mpl-cache'))
import json
from joint_verify import assess
if __name__=='__main__':
 s=json.loads((ROOT/'verification/summary.json').read_text())
 print(json.dumps(assess(4,s['main_n'],s['independent_n']),indent=2))
