"""Question 3 entry point, delegates to the shared material-coordinate engine."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
COMMON_CODE=ROOT.parents[1]/'A3/A3-codex/code'
if str(COMMON_CODE) not in sys.path:sys.path.insert(0,str(COMMON_CODE))
from drying_common.engine import solve as shared_solve,cli

def solve(name,**kwargs):return shared_solve(ROOT,3,name,**kwargs)

if __name__=='__main__':cli(ROOT,3)
