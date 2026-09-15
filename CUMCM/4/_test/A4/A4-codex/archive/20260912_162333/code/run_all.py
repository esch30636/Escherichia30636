"""Reproducible entry point. Only writes inside A4-codex."""
from pathlib import Path
import os,sys,subprocess,argparse
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--recompute',action='store_true');p.add_argument('--math-only',action='store_true');a=p.parse_args()
 os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'verification/mpl_cache'))
 def run(script,*args):subprocess.run([sys.executable,str(ROOT/'code'/script),*args],check=True,cwd=ROOT)
 run('prepare_inputs.py');run('run_cases.py',*(['--recompute'] if a.recompute else []));run('verify.py');run('produce.py')
 if not a.math_only:
  deps=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies'
  node=Path(os.environ.get('A4_NODE',str(deps/'node/bin/node')))
  modules=Path(os.environ.get('A4_NODE_MODULES',str(deps/'node/node_modules')))
  link=ROOT/'code/node_modules'
  if not link.exists():link.symlink_to(modules,target_is_directory=True)
  subprocess.run([str(node),str(ROOT/'code/build_workbook.mjs')],check=True,cwd=ROOT)
  run('check_workbook.py')
if __name__=='__main__':main()
