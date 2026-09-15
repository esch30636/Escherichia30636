# -*- coding: utf-8 -*-
"""Build compact digests of OCR'd papers for analysis: abstract, section headers,
figure/table captions, citation contexts, references, sensitivity/evaluation sections."""
import os, re, json, glob

SRC = r"D:\CUMCM\1\paper_texts_ocr"
OUT = r"D:\CUMCM\1\digests"
os.makedirs(OUT, exist_ok=True)

meta = json.load(open(os.path.join(SRC, "_meta.json"), encoding="utf-8")) if os.path.exists(os.path.join(SRC, "_meta.json")) else {}

HEADER_PATS = [
    r"^\s*([一二三四五六七八九十]+、[^\n]{0,40})$",
    r"^\s*(\d+(?:\.\d+){0,2}\s*[^\n]{2,35})$",
    r"^\s*(模型假设|符号说明|模型建立|模型求解|灵敏度分析|模型检验|误差分析|模型评价|模型推广|模型的评价|参考文献|附录)[^\n]{0,30}$",
]
SECTION_KW = ["问题", "模型", "分析", "假设", "符号", "建立", "求解", "结果", "灵敏度",
              "检验", "误差", "评价", "推广", "参考文献", "附录", "总结", "结论", "摘要",
              "关键词", "背景", "准备", "数据", "策略", "方案", "概述", "引言", "讨论"]
CITE_RE = re.compile(r"\[\s*\d+(?:\s*[,，\-–—~～]\s*\d+)*\s*\]")

def ref_section(full):
    m = re.search(r"(参考文献)\s*\n", full)
    if not m:
        return ""
    return full[m.end():m.end() + 2500]

def sens_section(full):
    m = re.search(r"(灵敏度分析|模型检验|误差分析)[^\n]*\n", full)
    if not m:
        return ""
    return full[m.start():m.start() + 3500]

def eval_section(full):
    m = re.search(r"(模型评价|模型的评价|优缺点)[^\n]*\n", full)
    if not m:
        return ""
    return full[m.start():m.start() + 2500]

for f in sorted(glob.glob(os.path.join(SRC, "*.txt"))):
    base = os.path.basename(f)
    text = open(f, encoding="utf-8").read()
    # abstract: from 摘要 to 关键词
    am = re.search(r"摘要\s*\n", text)
    km = re.search(r"关键词[^\n]*", text)
    abstract = ""
    if am and km:
        abstract = text[am.end():km.start()]
    # section headers
    headers = []
    for line in text.split("\n"):
        line = line.strip()
        if 2 <= len(line) <= 42:
            for pat in HEADER_PATS:
                if re.match(pat, line) and any(k in line for k in SECTION_KW):
                    headers.append(line)
                    break
    # dedupe consecutive
    seen = []
    for h in headers:
        if not seen or seen[-1] != h:
            seen.append(h)
    # citation contexts: first 25 unique lines containing markers
    cite_lines = []
    for line in text.split("\n"):
        if CITE_RE.search(line):
            cite_lines.append(line.strip()[:80])
            if len(cite_lines) >= 25:
                break
    m = meta.get(base.replace(".txt", ""), {})
    d = {
        "论文": base,
        "统计": {"图标题": m.get("n_fig"), "表标题": m.get("n_tab"), "引用标记": m.get("n_cites"), "总字数": m.get("n_chars")},
        "摘要": abstract[:3200],
        "关键词": km.group(0) if km else "",
        "章节结构": seen,
        "图表标题": (m.get("fig_captions", [])[:25] + ["..."] + m.get("table_captions", [])[:15]),
        "引用上下文示例": cite_lines,
        "参考文献": ref_section(text)[:2500],
        "灵敏度/检验节选": sens_section(text)[:3500],
        "模型评价节选": eval_section(text)[:2500],
    }
    out = os.path.join(OUT, base + ".digest.md")
    with open(out, "w", encoding="utf-8") as fp:
        json.dump(d, fp, ensure_ascii=False, indent=1)
    print("digest:", base, "| headers:", len(seen), "| cite lines:", len(cite_lines))
