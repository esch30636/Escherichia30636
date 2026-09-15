"""Run the coordinated A3/A4 calculation and delivery workflow."""
from pathlib import Path
import sys,os
ROOT=Path(__file__).resolve().parents[1]
COMMON_CODE=ROOT.parents[1]/'A3/A3-codex/code'
if str(COMMON_CODE) not in sys.path:sys.path.insert(0,str(COMMON_CODE))
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'verification/mpl-cache'))
from joint_pipeline import main
if __name__=="__main__":main()
