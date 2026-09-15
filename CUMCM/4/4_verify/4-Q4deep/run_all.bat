@echo off
cd /d D:\CUMCM\A\04
set OPENBLAS_NUM_THREADS=1
set PY=D:\Applications\Anaconda3\envs\cumcm_a\python.exe
if exist done.txt del done.txt
%PY% a4_sweep.py final --nproc 2   > log_final.txt 2>&1
%PY% a4_sweep.py conv  --nproc 4   > log_conv.txt  2>&1
%PY% a4_sweep.py scen  --nproc 6   > log_scen.txt  2>&1
%PY% a4_sweep.py latent --nproc 4  > log_latent.txt 2>&1
%PY% a4_output.py                   > log_output.txt 2>&1
echo ALL DONE %date% %time% > done.txt
