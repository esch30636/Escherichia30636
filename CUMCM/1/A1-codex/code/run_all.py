"""Reproduce math, workbook and checks. --recompute refreshes numerical caches."""
import os,subprocess,sys,argparse
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--recompute',action='store_true')
    p.add_argument('--math-only',action='store_true',help='Skip JS workbook authoring')
    a=p.parse_args()
    root=Path(__file__).resolve().parents[1];code=root/'code'
    dep=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies'
    bundled=dep/'python/python.exe'
    reader=str(bundled) if bundled.exists() else sys.executable
    env=os.environ.copy();env['PYTHONIOENCODING']='utf-8'
    if a.recompute:env['A1_RECOMPUTE']='1'
    def run(args):subprocess.run(list(map(str,args)),check=True,cwd=root,env=env)
    run([reader,code/'extract_inputs.py'])
    for script in ['convergence.py','refine.py','benchmarks.py','innovation.py','sensitivity.py','final_refinement.py','produce.py']:
        run([sys.executable,code/script])
    if not a.math_only:
        node=dep/'node/bin/node.exe'
        if not node.exists():raise RuntimeError('Set up a Node runtime with @oai/artifact-tool; see README.')
        link=code/'node_modules'
        if not link.exists():
            # A fixed local junction for Node package lookup; no dependency copies or edits.
            script="New-Item -ItemType Junction -Path '"+str(link).replace("'","''")+"' -Target '"+str(dep/'node/node_modules').replace("'","''")+"' | Out-Null"
            run(['powershell','-NoProfile','-Command',script])
        run([node,code/'build_workbook.mjs'])
        run([reader,code/'check_workbook.py'])
        run([sys.executable,code/'verify.py'])
    print('Completed. Outputs:',root)

if __name__=='__main__':main()
