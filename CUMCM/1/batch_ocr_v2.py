# -*- coding: utf-8 -*-
"""Hardened batch OCR: per-page try/except, per-page progress log, 150dpi, no angle cls.
Resumable: skips papers already done. Writes partial results as it goes."""
import ssl
if hasattr(ssl.SSLContext, "_load_windows_store_certs"):
    ssl.SSLContext._load_windows_store_certs = lambda self, storename, purpose: None
import os, re, json, sys, time, glob
import fitz
from paddleocr import PaddleOCR

SRC = r"D:\CUMCM\_shared\papers\all"
OUT = r"D:\CUMCM\_shared\papers\ocr_out"
META = os.path.join(OUT, "_meta.json")
LOG = r"D:\CUMCM\_shared\papers\ocr.log"

os.makedirs(OUT, exist_ok=True)

PRIORITY = [
    "2023国赛A题_A0127_优秀论文.pdf", "2023国赛B题_B226_优秀论文.pdf", "2023国赛C题_C050_优秀论文.pdf",
    "2023国赛D题_D039_优秀论文.pdf", "2023国赛E题_E032_优秀论文.pdf",
    "2024国赛A题_A016_优秀论文.pdf", "2024国赛B题_B159_优秀论文.pdf", "2024国赛C题_C038_优秀论文.pdf",
    "2024国赛D题_D033_优秀论文.pdf", "2024国赛E题_E010_优秀论文.pdf",
    "2025国赛A题_A196_优秀论文.pdf", "2025国赛B题_B060_优秀论文.pdf", "2025国赛C题_C023_优秀论文.pdf",
    "2025国赛D题_D037_优秀论文.pdf", "2025国赛E题_E030_优秀论文.pdf",
]

def log(msg):
    with open(LOG, "a", encoding="utf-8") as fp:
        fp.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    print(msg, flush=True)

pdfs = []
for root, dirs, files in os.walk(SRC):
    for f in files:
        if f.lower().endswith(".pdf"):
            pdfs.append(os.path.join(root, f))
pdfs.sort(key=lambda p: PRIORITY.index(os.path.basename(p)) if os.path.basename(p) in PRIORITY else 999)

meta = json.load(open(META, encoding="utf-8")) if os.path.exists(META) else {}
ocr = PaddleOCR(use_angle_cls=False, lang="ch", show_log=False)

n_done = 0
for path in pdfs:
    base = os.path.basename(path)
    out_txt = os.path.join(OUT, base + ".txt")
    if os.path.exists(out_txt) and os.path.getsize(out_txt) > 1000:
        n_done += 1
        continue
    t_paper = time.time()
    try:
        doc = fitz.open(path)
        npages = len(doc)
        pages_text = []
        for i in range(npages):
            t_page = time.time()
            try:
                pix = doc[i].get_pixmap(dpi=150)
                png = os.path.join(OUT, f"_tmp_{base[:8]}_{i}.png")
                pix.save(png)
                res = ocr.ocr(png, cls=False)
                lines = []
                if res:
                    for block in res:
                        if block:
                            for item in block:
                                lines.append(item[1][0])
                pages_text.append("\n".join(lines))
                if os.path.exists(png):
                    os.remove(png)
            except Exception as e:
                log(f"page-err {base} p{i+1}: {e}")
                pages_text.append("")
            if (i + 1) % 15 == 0:
                log(f"{base} page {i+1}/{npages} ({time.time()-t_page:.1f}s/page)")
        doc.close()
        full = "\n".join(pages_text)
        with open(out_txt, "w", encoding="utf-8") as fp:
            for i, t in enumerate(pages_text):
                fp.write(f"\n===== PAGE {i+1} =====\n{t}\n")
        fig_caps = re.findall(r"图\s*[0-9０-９]{1,2}[^\n]{0,50}", full)
        tab_caps = re.findall(r"表\s*[0-9０-９]{1,2}[^\n]{0,50}", full)
        cites = re.findall(r"\[\d+(?:\s*[,，\-–—]\s*\d+)*\]", full)
        meta[base] = {"fig_captions": fig_caps, "table_captions": tab_caps,
                      "n_fig": len(fig_caps), "n_tab": len(tab_caps), "n_cites": len(cites),
                      "n_chars": len(full)}
        json.dump(meta, open(META, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        n_done += 1
        log(f"done {base} ({n_done}/{len(pdfs)}, {(time.time()-t_paper)/60:.1f}min/paper)")
    except Exception as e:
        log(f"FAIL {base}: {e}")
log("ALL DONE")
