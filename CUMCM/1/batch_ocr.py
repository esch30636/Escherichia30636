# -*- coding: utf-8 -*-
"""Batch OCR all CUMCM papers on legion GPU. Resumable: skips papers already done.
Output: per-paper .txt (page markers) + meta.json (fig/table captions, citations, page count).
Priority order: cover A-E x multiple years first (priority list below), then the rest.
"""
import ssl
if hasattr(ssl.SSLContext, "_load_windows_store_certs"):
    ssl.SSLContext._load_windows_store_certs = lambda self, storename, purpose: None
import os, re, json, sys, time, glob
import fitz
from paddleocr import PaddleOCR

SRC = r"D:\CUMCM\_shared\papers\all"
OUT = r"D:\CUMCM\_shared\papers\ocr_out"
META = os.path.join(OUT, "_meta.json")

os.makedirs(OUT, exist_ok=True)

# priority order: representative spread across problem types and years
PRIORITY = [
    "2023国赛A题_A0127_优秀论文.pdf", "2023国赛B题_B226_优秀论文.pdf", "2023国赛C题_C050_优秀论文.pdf",
    "2023国赛D题_D039_优秀论文.pdf", "2023国赛E题_E032_优秀论文.pdf",
    "2024国赛A题_A016_优秀论文.pdf", "2024国赛B题_B159_优秀论文.pdf", "2024国赛C题_C038_优秀论文.pdf",
    "2024国赛D题_D033_优秀论文.pdf", "2024国赛E题_E010_优秀论文.pdf",
    "2025国赛A题_A196_优秀论文.pdf", "2025国赛B题_B060_优秀论文.pdf", "2025国赛C题_C023_优秀论文.pdf",
    "2025国赛D题_D037_优秀论文.pdf", "2025国赛E题_E030_优秀论文.pdf",
]

pdfs = []
for root, dirs, files in os.walk(SRC):
    for f in files:
        if f.lower().endswith(".pdf"):
            pdfs.append(os.path.join(root, f))
pdfs.sort(key=lambda p: PRIORITY.index(os.path.basename(p)) if os.path.basename(p) in PRIORITY else 999)

meta = {}
if os.path.exists(META):
    meta = json.load(open(META, encoding="utf-8"))

ocr = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)
t0 = time.time()
n_done = 0
for path in pdfs:
    base = os.path.basename(path)
    out_txt = os.path.join(OUT, base + ".txt")
    if os.path.exists(out_txt) and os.path.getsize(out_txt) > 1000:
        n_done += 1
        continue
    try:
        doc = fitz.open(path)
        pages_text = []
        for i in range(len(doc)):
            page = doc[i]
            pix = page.get_pixmap(dpi=180)
            png = os.path.join(OUT, f"_tmp_p{i}.png")
            pix.save(png)
            res = ocr.ocr(png, cls=True)
            lines = []
            if res:
                for block in res:
                    if block:
                        for item in block:
                            lines.append(item[1][0])
            pages_text.append("\n".join(lines))
            os.remove(png)
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
        el = (time.time() - t0) / n_done
        print(f"[{time.strftime('%H:%M:%S')}] done {base} ({n_done}/{len(pdfs)}, {el:.1f}s/paper, eta {(len(pdfs)-n_done)*el/60:.0f}min)", flush=True)
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] FAIL {base}: {e}", flush=True)
        meta[base] = {"error": str(e)}
        json.dump(meta, open(META, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ALL DONE", flush=True)
