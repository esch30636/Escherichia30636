# -*- coding: utf-8 -*-
"""Check which conda envs on legion have OCR libs, and GPU paddle status."""
import subprocess, sys, glob, os

candidates = []
anaconda = r"D:\Applications\Anaconda3"
for p in glob.glob(anaconda + r"\envs\*"):
    candidates.append(os.path.join(p, "python.exe"))
candidates.append(os.path.join(anaconda, "python.exe"))

for py in candidates:
    env = py.replace(anaconda, "").strip("\\") or "base"
    for mod in ["paddleocr", "easyocr", "pytesseract", "paddle", "rapidocr_onnxruntime", "cnocr"]:
        r = subprocess.run([py, "-c", f"import {mod}"], capture_output=True)
        if r.returncode == 0:
            print(f"[{env}] HAS {mod}")
