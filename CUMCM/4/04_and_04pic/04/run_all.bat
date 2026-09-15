@echo off
setlocal
cd /d "%~dp0"
set OPENBLAS_NUM_THREADS=1
set OMP_NUM_THREADS=1
set PYTHONIOENCODING=utf-8
if not defined A4_PYTHON set "A4_PYTHON=python"
"%A4_PYTHON%" a4_sweep.py audit --nproc 4
if errorlevel 1 exit /b 1
"%A4_PYTHON%" a4_output.py --plots-only
if errorlevel 1 exit /b 1
"%A4_PYTHON%" a4_verify.py
if errorlevel 1 exit /b 1
echo Audit rebuild and verification completed.
endlocal
