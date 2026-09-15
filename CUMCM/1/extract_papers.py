# -*- coding: utf-8 -*-
"""Extract text from all CUMCM excellent papers into per-page text files + a metadata summary."""
import fitz
import os
import re
import json

SRC = r"D:\CUMCM\优秀论文\优秀论文"
OUT = r"D:\CUMCM\1\paper_texts"
META_OUT = r"D:\CUMCM\1\paper_meta.json"

os.makedirs(OUT, exist_ok=True)

meta = {}
for root, dirs, files in os.walk(SRC):
    for f in sorted(files):
        if not f.lower().endswith(".pdf"):
            continue
        path = os.path.join(root, f)
        rel = os.path.relpath(path, SRC)
        doc = fitz.open(path)
        pages_text = []
        all_text = []
        for i, page in enumerate(doc):
            t = page.get_text("text")
            pages_text.append(t)
            all_text.append(t)
        full = "\n".join(all_text)
        # figure/table captions
        fig_caps = re.findall(r"图\s*\d+[^\n]{0,60}", full)
        tab_caps = re.findall(r"表\s*\d+[^\n]{0,60}", full)
        # references section
        refs = []
        ref_match = re.search(r"(参考文献|References)\s*\n", full)
        ref_sec = ""
        if ref_match:
            ref_sec = full[ref_match.end():ref_match.end() + 3000]
        # count citation markers like [1], [2,3]
        cites = re.findall(r"\[\d+(?:\s*[,，\-–—]\s*\d+)*\]", full)
        # page count
        npages = len(doc)
        meta[rel] = {
            "pages": npages,
            "fig_captions": fig_caps,
            "table_captions": tab_caps,
            "n_fig_caps": len(fig_caps),
            "n_table_caps": len(tab_caps),
            "ref_section_head": ref_sec[:2000],
            "n_cite_markers": len(cites),
            "n_chars": len(full),
        }
        # write per-page text
        out_path = os.path.join(OUT, rel.replace("\\", "__").replace("/", "__") + ".txt")
        with open(out_path, "w", encoding="utf-8") as fp:
            for i, t in enumerate(pages_text):
                fp.write(f"\n===== PAGE {i+1} =====\n")
                fp.write(t)
        doc.close()
        print(f"{rel}: {npages} pages, {len(fig_caps)} fig caps, {len(tab_caps)} tab caps, {len(cites)} cite markers")

with open(META_OUT, "w", encoding="utf-8") as fp:
    json.dump(meta, fp, ensure_ascii=False, indent=2)
print("DONE ->", META_OUT)
