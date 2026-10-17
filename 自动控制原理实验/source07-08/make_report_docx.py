# -*- coding: utf-8 -*-
"""
生成《控制理论综合实验报告》——实验七、实验八（最少拍无纹波设计）
====================================================================
· 排版严格对齐《控制理论综合实验》6.docx：A4 / 页边距 2.54-3.17cm /
  一级标题黑体14pt / 正文宋体12pt 首行缩进21pt 段后5pt 行距266 /
  图注宋体9pt 居中 / 独立公式居中
· 公式用 Word 原生 OMML（LaTeX→MathML→OMML），可在 Word 中直接编辑
· 图片全部为本人在 source07-08 下的实测照片（T0.0x实验一 / 7.2 / 7.3 / 8.1 系列），不使用任何生成图或示意图
· 依赖: python-docx, latex2mathml, Pillow, lxml（DSH 自带 Python 环境已具备）
运行: python make_report_docx.py

"""
import os
import sys
import latex2mathml.converter as l2m
from lxml import etree
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "report_assets")
OUT_DOCX = os.path.join(HERE, "实验报告-实验7-8-采样系统分析与最少拍无纹波设计.docx")

# =====================================================================
# 一、LaTeX → OMML
# =====================================================================
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "{%s}" % M_NS
W = "{%s}" % W_NS

_UPRIGHT = {"sin", "cos", "tan", "ln", "log", "exp", "lim", "max", "min",
            "arctan", "arcsin", "arccos", "Re", "Im"}
_DELIM = {"(": ")", "[": "]", "{": "}", "⟨": "⟩", "|": "|"}


def _normalize_latex(latex):
    """规整 LaTeX：latex2mathml 对 \\left[\\right] 会重复渲染定界符内容，
    因此统一去掉 \\left/\\right，并清除会撑宽公式的空白命令。"""
    s = latex
    for a, b in [("\\left\\{", "{"), ("\\right\\}", "}"),
                 ("\\left(", "("), ("\\right)", ")"),
                 ("\\left[", "["), ("\\right]", "]"),
                 ("\\left|", "|"), ("\\right|", "|"),
                 ("\\left.", ""), ("\\right.", "")]:
        s = s.replace(a, b)
    for cmd in ("\\,", "\\;", "\\!", "\\quad", "\\qquad"):
        s = s.replace(cmd, " ")
    s = s.replace("\\max", "\\max ")
    return s


def _new(tag, parent=None):
    el = etree.Element(M + tag, nsmap={"m": M_NS, "w": W_NS})
    if parent is not None:
        parent.append(el)
    return el


def _run_el(text, parent, style="p"):
    r = _new("r", parent)
    rPr = _new("rPr", r)
    sty = _new("sty", rPr); sty.set(M + "val", style)
    wrPr = etree.SubElement(r, W + "rPr")
    rf = etree.SubElement(wrPr, W + "rFonts")
    rf.set(W + "ascii", "Cambria Math"); rf.set(W + "hAnsi", "Cambria Math")
    t = _new("t", r); t.text = text
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return r


def _conv_children(node, parent):
    for ch in node:
        _conv(ch, parent)


def _conv_siblings(node, parent, close):
    cur = node.getnext()
    while cur is not None:
        if cur.tag.endswith("mo") and (cur.text or "") == close:
            return
        _conv(cur, parent)
        cur = cur.getnext()


def _conv(node, parent):
    tag = node.tag
    if not isinstance(tag, str):
        return
    local = tag.split("}")[-1]

    if local in ("math", "mrow", "mstyle", "semantics", "mphantom", "mpadded"):
        _conv_children(node, parent); return
    if local in ("annotation", "annotation-xml"):
        return
    if local == "mi":
        txt = node.text or ""
        _run_el(txt, parent, "p" if txt in _UPRIGHT else "i"); return
    if local == "mn":
        _run_el(node.text or "", parent, "p"); return
    if local == "mtext":
        _run_el(node.text or "", parent, "p"); return
    if local == "mspace":
        _run_el(" ", parent, "p"); return
    if local == "mo":
        txt = node.text or ""
        if txt in _DELIM and node.get("stretchy", "false") == "true":
            d = _new("d", parent); dPr = _new("dPr", d)
            b = _new("begChr", dPr); b.set(M + "val", txt)
            e2 = _new("endChr", dPr); e2.set(M + "val", _DELIM[txt])
            e = _new("e", d); _conv_siblings(node, e, _DELIM[txt]); return
        _run_el(txt, parent, "p"); return
    if local == "mfrac":
        k = list(node); f = _new("f", parent)
        num = _new("num", f); _conv(k[0], num)
        den = _new("den", f)
        if len(k) > 1:
            _conv(k[1], den)
        return
    if local in ("msup", "msub", "msubsup"):
        k = list(node)
        el = _new({"msup": "sSup", "msub": "sSub", "msubsup": "sSubSup"}[local], parent)
        e = _new("e", el); _conv(k[0], e)
        if local in ("msub", "msubsup"):
            s = _new("sub", el)
            if len(k) > 1:
                _conv(k[1], s)
        if local in ("msup", "msubsup"):
            s = _new("sup", el)
            idx = 2 if local == "msubsup" else 1
            if len(k) > idx:
                _conv(k[idx], s)
        return
    if local == "msqrt":
        rad = _new("rad", parent)
        pr = _new("radPr", rad); dh = _new("degHide", pr); dh.set(M + "val", "1")
        _new("deg", rad)
        e = _new("e", rad); _conv_children(node, e); return
    if local == "mroot":
        k = list(node); rad = _new("rad", parent)
        deg = _new("deg", rad); _conv(k[1], deg)
        e = _new("e", rad); _conv(k[0], e); return
    if local == "mover":
        k = list(node); lim = _new("limUpp", parent)
        e = _new("e", lim); _conv(k[0], e)
        lo = _new("lim", lim)
        if len(k) > 1:
            _conv(k[1], lo)
        return
    if local == "munder":
        k = list(node); lim = _new("limLow", parent)
        e = _new("e", lim); _conv(k[0], e)
        lo = _new("lim", lim)
        if len(k) > 1:
            _conv(k[1], lo)
        return
    if local in ("mtable", "mtr", "mtd"):
        _conv_children(node, parent if local != "mtable" else _new("eqArr", parent))
        return
    _conv_children(node, parent)


def omml(latex):
    root = etree.fromstring(l2m.convert(_normalize_latex(latex)).encode("utf-8"))
    el = etree.Element(M + "oMath", nsmap={"m": M_NS, "w": W_NS})
    _conv(root, el)
    return el


def omml_para(latex):
    p = etree.Element(M + "oMathPara", nsmap={"m": M_NS, "w": W_NS})
    pr = etree.SubElement(p, M + "oMathParaPr")
    jc = etree.SubElement(pr, M + "jc"); jc.set(M + "val", "center")
    p.append(omml(latex))
    return p


# =====================================================================
# 二、文档与排版工具
# =====================================================================
def set_font(run, size=12, cn="宋体", en="Times New Roman", bold=False):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = en
    run._element.rPr.rFonts.set(qn("w:eastAsia"), cn)
    run._element.rPr.rFonts.set(qn("w:ascii"), en)
    run._element.rPr.rFonts.set(qn("w:hAnsi"), en)


def fmt_para(p, first_indent=21.0, after=5.0, line=266, align=None, before=0):
    pf = p.paragraph_format
    if first_indent:
        pf.first_line_indent = Pt(first_indent)
    pf.space_after = Pt(after)
    pf.space_before = Pt(before)
    pPr = p._p.get_or_add_pPr()
    sp = pPr.find(qn("w:spacing"))
    if sp is None:
        sp = OxmlElement("w:spacing"); pPr.append(sp)
    sp.set(qn("w:line"), str(line))
    sp.set(qn("w:lineRule"), "auto")
    if align is not None:
        p.alignment = align
    return p


def add_footer_pagenum(doc):
    footer = doc.sections[0].footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run()
    for instr, kind in (("begin", None), (None, "PAGE"), ("end", None)):
        if kind:
            t = OxmlElement("w:instrText"); t.set(qn("xml:space"), "preserve")
            t.text = " PAGE "
            r._r.append(t)
        else:
            f = OxmlElement("w:fldChar"); f.set(qn("w:fldCharType"), instr)
            r._r.append(f)
    set_font(r, 10.5)


class Report:
    def __init__(self):
        self.doc = Document()
        s = self.doc.sections[0]
        s.page_width, s.page_height = Cm(21.0), Cm(29.7)
        s.top_margin = s.bottom_margin = Cm(2.54)
        s.left_margin = s.right_margin = Cm(3.17)
        st = self.doc.styles["Normal"]
        st.font.size = Pt(10.5)
        st.font.name = "Times New Roman"
        st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        add_footer_pagenum(self.doc)

    # ---- 基本块 ----
    def h1(self, text):
        p = self.doc.add_paragraph()
        fmt_para(p, first_indent=0, align=WD_ALIGN_PARAGRAPH.LEFT)
        set_font(p.add_run(text), 14, cn="黑体", en="Times New Roman", bold=False)
        return p

    def h2(self, text, bold=True):
        p = self.doc.add_paragraph()
        fmt_para(p, align=WD_ALIGN_PARAGRAPH.LEFT)
        set_font(p.add_run(text), 12, cn="宋体", bold=bold)
        return p

    def body(self, text, indent=21.0):
        p = self.doc.add_paragraph()
        fmt_para(p, first_indent=indent, align=WD_ALIGN_PARAGRAPH.LEFT)
        set_font(p.add_run(text), 12, cn="宋体")
        return p

    def body_math(self, parts):
        """parts: 字符串 或 ('m', latex) 元组混排"""
        p = self.doc.add_paragraph()
        fmt_para(p, first_indent=21.0, align=WD_ALIGN_PARAGRAPH.LEFT)
        for it in parts:
            if isinstance(it, tuple):
                p._p.append(omml(it[1]))
            else:
                set_font(p.add_run(it), 12, cn="宋体")
        return p

    # 可用正文宽度 14.66 cm，Cambria Math 12pt 每个字符宽度约 0.135 cm
    MAX_MATH_CHARS = 84

    def disp_math(self, latex):
        p = self.doc.add_paragraph()
        fmt_para(p, first_indent=0, align=WD_ALIGN_PARAGRAPH.CENTER)
        p._p.append(omml_para(latex))
        shown = "".join(x.text or "" for x in omml(latex).iter(M + "t"))
        if len(shown) > self.MAX_MATH_CHARS:
            print(f"  [警告] 公式可能过宽({len(shown)}字符): {shown[:70]}")
        return p

    def caption(self, text):
        p = self.doc.add_paragraph()
        fmt_para(p, first_indent=0, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_font(p.add_run(text), 9, cn="宋体")
        return p

    def pic(self, path, width_cm=13.5):
        p = self.doc.add_paragraph()
        fmt_para(p, first_indent=0, after=0, align=WD_ALIGN_PARAGRAPH.CENTER)
        p.add_run().add_picture(path, width=Cm(width_cm))
        return p

    def figure(self, path, caption, width_cm=13.5):
        self.pic(normalize(path), width_cm)
        self.caption(caption)

    def table(self, header, rows, widths=None):
        t = self.doc.add_table(rows=1, cols=len(header))
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, h in enumerate(header):
            cell = t.rows[0].cells[i]
            cell.text = ""
            p = cell.paragraphs[0]
            fmt_para(p, first_indent=0, after=0, align=WD_ALIGN_PARAGRAPH.CENTER)
            set_font(p.add_run(h), 10.5, cn="宋体", bold=True)
        for row in rows:
            cells = t.add_row().cells
            for i, v in enumerate(row):
                cells[i].text = ""
                p = cells[i].paragraphs[0]
                fmt_para(p, first_indent=0, after=0, align=WD_ALIGN_PARAGRAPH.CENTER)
                set_font(p.add_run(str(v)), 10.5, cn="宋体")
        if widths:
            for r in t.rows:
                for i, wcm in enumerate(widths):
                    r.cells[i].width = Cm(wcm)
        return t

    def pagebreak(self):
        self.doc.add_page_break()

    def save(self, path):
        self.doc.save(path)


def P(*names):
    for n in names:
        assert os.path.exists(n), f"缺少素材: {n}"


# =====================================================================
# 二·五、图片归一化（python-docx 解析带 EXIF 的原始照片会失败，
#        且 4 MB 的翻拍照片体积过大；统一去 EXIF + 缩放到打印够用的尺寸）
# =====================================================================
NORM_DIR = os.path.join(ASSETS, "normalized")
MAX_PX = 1800          # 长边像素：13.5 cm 宽约 340 dpi，足够清晰


def normalize(src, max_px=MAX_PX):
    """返回可用于 add_picture 的图片路径（去 EXIF、缩放到 max_px、存为 JPEG）"""
    os.makedirs(NORM_DIR, exist_ok=True)
    key = os.path.splitext(os.path.basename(src))[0]
    dst = os.path.join(NORM_DIR, key + ".jpg")
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        return dst
    from PIL import Image, ImageOps
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)          # 按 EXIF 方向摆正
        if im.mode != "RGB":
            im = im.convert("RGB")
        w, h = im.size
        scale = min(1.0, max_px / max(w, h))
        if scale < 1.0:
            im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))),
                           Image.LANCZOS)
        im.save(dst, "JPEG", quality=88, optimize=True, progressive=False)
    return dst


# =====================================================================
# 三、正文内容
# =====================================================================
def build():
    r = Report()

    # ---------------- 封面 ----------------
    p = r.doc.add_paragraph(); fmt_para(p, first_indent=0, after=0,
                                        align=WD_ALIGN_PARAGRAPH.CENTER)
    set_font(p.add_run("华中科技大学"), 36, cn="华文行楷", en="STXingkai", bold=True)
    p = r.doc.add_paragraph(); fmt_para(p, first_indent=0, after=0,
                                        align=WD_ALIGN_PARAGRAPH.CENTER)
    set_font(p.add_run("人工智能与自动化学院"), 20, cn="华文行楷", en="STXingkai")
    r.doc.add_paragraph()
    p = r.doc.add_paragraph(); fmt_para(p, first_indent=0, after=0,
                                        align=WD_ALIGN_PARAGRAPH.CENTER)
    set_font(p.add_run("控制理论综合实验报告"), 20, cn="黑体", en="Times New Roman", bold=True)
    r.doc.add_paragraph()
    for line in ["实验项目：实验七、实验八",
                 "实验名称：采样系统的分析与最少拍无波纹系统设计",
                 "实验时间：2026/6/15 星期一"]:
        p = r.doc.add_paragraph()
        fmt_para(p, first_indent=21.0, after=0)
        p.paragraph_format.line_spacing = 1.5
        set_font(p.add_run(line), 12, cn="宋体")
    r.doc.add_paragraph()
    for line in ["实验人员1：迟泰炎", "专业班级：自动化2406班",
                 "学    号：U202414215", "姓    名：迟泰炎"]:
        p = r.doc.add_paragraph()
        fmt_para(p, first_indent=21.0, after=0)
        p.paragraph_format.line_spacing = 1.5
        set_font(p.add_run(line), 12, cn="宋体")
    r.doc.add_paragraph()
    for line in ["实验人员2：王鑫磊", "专业班级：自动化2406班",
                 "学    号：U202414229", "姓    名：王鑫磊"]:
        p = r.doc.add_paragraph()
        fmt_para(p, first_indent=21.0, after=0)
        p.paragraph_format.line_spacing = 1.5
        set_font(p.add_run(line), 12, cn="宋体")
    r.pagebreak()

    # ---------------- 实验目的 ----------------
    r.h1("实验目的")
    r.body("本次实验围绕采样控制系统的分析与数字控制器设计展开，目的在于完成从被控对象建模、"
           "离散化推导、理论设计到硬件电路验证的完整闭环。")
    r.body("在理论分析方面，要求掌握判断采样系统稳定性的充要条件，理解采样周期 T 对被控系统"
           "稳定性的影响规律，并能够计算使采样系统恰好处于临界稳定状态时的采样周期。")
    r.body("在数字控制器设计方面，要求掌握数字控制器的直接设计方法，能够由被控对象的广义脉冲"
           "传递函数反解出数字调节器的脉冲传递函数，并将其化为标准解析式与后向差分方程形式，"
           "进而分析调节器系数 Ki、Pi 与被控对象参数之间的定量关系。")
    r.body("在软硬件结合方面，要求在上位机上通过改变采样周期观察系统由稳定、临界到不稳定的"
           "瞬态响应变化，并在模拟电路上搭建最少拍无纹波控制系统，验证理论设计所得的控制量序列"
           "与输出波形。")

    # ---------------- 实验设备 ----------------
    r.h1("实验设备")
    r.body("STAR ACT自控、计控实验仪一套、PC机一台")

    # ---------------- 实验原理 ----------------
    r.h1("实验原理")

    r.h2("1. 采样系统的稳定性判据")
    r.body_math(["采样系统的闭环脉冲传递函数为"])
    r.disp_math(r"\Phi(z)=\frac{D(z)G_0(z)}{1+D(z)G_0(z)}")
    r.body_math(["采样系统稳定的充要条件是闭环特征方程的全部根均位于 z 平面的单位圆内，即"])
    r.disp_math(r"|z_i|<1\quad(i=1,2,\cdots)")
    r.body_math(["只要有一个特征根位于单位圆外，系统即不稳定；当某一根恰好落在单位圆上而其余根"
                 "均在圆内时，系统处于临界稳定状态。这与连续系统要求特征根位于 s 左半平面是相互"
                 "对应的，两者的映射关系为 ", ("m", r"z=e^{sT}"), "，即 ",
                 ("m", r"|z|=e^{\sigma T}"), "、", ("m", r"\angle z=\omega T"), "。"])

    r.h2("2. 被控对象的广义脉冲传递函数")
    r.body_math(["实验中被控对象由积分环节与惯性环节串联组成，其开环传递函数为"])
    r.disp_math(r"G_0(s)=\frac{K}{T_i s}\cdot\frac{1}{T_1 s+1}")
    r.body_math(["在零阶保持器作用下，单位阶跃输入时被控对象在采样时刻的响应可解析求得为"])
    r.disp_math(r"y(t)=\frac{K}{T_i}\left[t-T_1\left(1-e^{-t/T_1}\right)\right]")
    r.body_math(["由此可得广义对象的脉冲传递函数为"])
    r.disp_math(r"G_0(z)=\frac{b_1 z^{-1}+b_2 z^{-2}}{(1-z^{-1})(1-pz^{-1})}")
    r.body_math(["其中"])
    r.disp_math(r"p=e^{-T/T_1},\qquad b_1=y(1),\qquad b_2=y(2)-(1+p)y(1)-y(1)")
    r.body_math(["该式表明广义对象含有两个极点：", ("m", r"z=1"), " 对应积分环节，",
                 ("m", r"z=p"), " 对应惯性环节。"])

    r.h2("3. 最少拍无纹波控制器的设计")
    r.body_math(["单位阶跃输入下，最少拍系统要求闭环脉冲传递函数为"])
    r.disp_math(r"\Phi(z)=z^{-1}")
    r.body_math(["代入数字调节器的反解公式"])
    r.disp_math(r"D(z)=\frac{\Phi(z)}{G_0(z)\left[1-\Phi(z)\right]}")
    r.body_math(["可得"])
    r.disp_math(r"D(z)=\frac{1-pz^{-1}}{b_1\left(1+a_2 z^{-1}\right)},\qquad a_2=\frac{b_2}{b_1}")
    r.body_math(["将其化为分母首项为 1 的降幂标准解析式"])
    r.disp_math(r"D(z)=\frac{K_0+K_1 z^{-1}}{1+P_1 z^{-1}}")
    r.body_math(["即得调节器系数与被控对象参数的关系"])
    r.disp_math(r"K_0=\frac{1}{b_1},\qquad b_1=\frac{K}{T_i}\left[T-T_1\left(1-e^{-T/T_1}\right)\right]")
    r.disp_math(r"K_1=-\frac{p}{b_1}=-pK_0,\qquad P_1=a_2=\frac{b_2}{b_1}")
    r.body_math(["由此可写出后向差分方程"])
    r.disp_math(r"U(k)=K_0E_K+K_1E_{K-1}-P_1U_{K-1}")
    r.body_math(["由该式可见：K0 决定首拍控制量的大小，即数字调节器在第一个采样周期向被控对象"
                 "提供的能量；K1 = −pK0 提供被控对象惯性极点的补偿，使 D(z) 的零点恰好抵消 G0(z) "
                 "的极点 z = p；P1 抵消广义对象分子的采样零点。三个系数共同保证闭环严格等于 ",
                 ("m", r"z^{-1}"), "，从而实现采样点上一拍到位、采样点之间无纹波。"])

    # ---------------- 实验内容与要求 ----------------
    r.h1("实验内容与要求")
    r.h2("1. 采样系统分析的实验内容")
    r.body_math(["按实验指导书连接采样实验电路，计算机经模数转换模块以设定采样周期对信号源产生的正弦波"
                 "信号采样并由上位机显示，在 0.01~0.2 s 区间内选取若干采样周期，观察比较输入与输出"
                 "波形的失真程度。接线方式为：正弦波信号由 B3 区 xOUT1 输出接至 B3 区 CH1，"
                 "采样保持后的输出由 B3 区 xOUT2 接至 B3 区 CH2。"])
    r.body_math(["随后连接采样控制电路，被控对象由 D1 区积分环节（R1 = 100 kΩ、C1 = 2 μF，"
                 "积分时间常数 ", ("m", r"T_i=0.2"), " s）与 D2 区惯性环节（R3 = 500 kΩ、C2 = 1 μF，"
                 "惯性时间常数 ", ("m", r"T_1=0.5"), " s）串联构成，接线为：B3 区 xOUT2 → D1 区 H1，"
                 "D1 区 OUT → D2 区 H1，B3 区 xOUT2 → B3 区 CH2，D2 区 OUT → B3 区 CH1。"
                 "分别设置采样周期为 0.015 s、0.03 s、0.09 s，记录不同采样周期下的输出波形及稳定性；"
                 "理论计算系统的闭环脉冲传递函数，求出使系统临界稳定的采样周期，并与实测结果进行比较。"])

    r.h2("2. 最少拍无纹波控制系统设计的实验内容")
    r.body_math(["按教材图 8-1 的模拟电路组成最少拍无纹波控制系统，其中 R1 = 100 kΩ、C1 = 2 μF（D1 积分"
                 "环节，", ("m", r"T_i=0.2"), " s），R3 = 500 kΩ、C2 = 2 μF（D2 惯性环节，",
                 ("m", r"T_1=1.0"), " s），接线为：B3 区 xOUT2 → D1 区 H1，D1 区 OUT → D2 区 H1，"
                 "B3 区 xOUT2 → B3 区 CH2，D2 区 OUT → B3 区 CH1。在上位机的三个下拉框中依次选择"
                 "“计算机控制技术实验”、“直接数字控制实验”、“实验二（2）最少拍控制—最少拍无纹波"
                 "控制系统”。"])
    r.body("按表 8-1 分别设置两组控制参数，记录电路输出波形，分析不同输出信号产生的原因以及最少拍"
           "控制的性能特点与优劣，并写出控制器的脉冲传递函数、分析其与实验中参数 Ki、Pi 之间的关系。")

    # ---------------- 实验结果 ----------------
    r.h1("实验结果")
    r.h2("1. 信号的采样")
    r.body_math(["在 0.01~0.2 s 区间内选取 0.01 s、0.05 s、0.1 s、0.2 s 四个采样周期，信号源设置为 "
                 "0.5 Hz、幅值 3.00 V 的双极性正弦波，虚拟示波器时基 100 ms/格，白线为 CH1 输入"
                 "正弦波，红线为 CH2 采样保持后的输出。"])
    for f, cap in [("T0.01实验一.jpg", "图 1  采样周期 T = 0.01 s 时的采样波形"),
                   ("T0.05实验一.jpg", "图 2  采样周期 T = 0.05 s 时的采样波形"),
                   ("T0.1实验一.jpg", "图 3  采样周期 T = 0.1 s 时的采样波形"),
                   ("T0.2实验一.jpg", "图 4  采样周期 T = 0.2 s 时的采样波形")]:
        r.figure(os.path.join(HERE, f), cap, 13.5)
    r.body_math(["由四组波形可以看出：T = 0.01 s 时采样阶梯极为密集，红线与白线几乎完全重合，"
                 "输出能够实时跟随输入；T = 0.05 s 时阶梯已清晰可辨，但每个正弦周期内仍有约 100 级"
                 "台阶，波形畸变很小；T = 0.1 s 时每个周期约 20 级台阶，阶梯明显变粗且滞后于输入约"
                 "半级；T = 0.2 s 时每个周期仅约 10 级台阶，输出已呈现明显的锯齿状，与输入正弦波"
                 "差异显著。"])
    r.body_math(["这说明采样周期越长，采样点之间的信息丢失越多，由零阶保持器恢复出的信号失真越"
                 "严重，即采样定理所要求的 ", ("m", r"T<1/(2f_{\max})"),
                 " 条件被削弱，输出与输入的偏差随 T 增大而单调增大。"])

    r.h2("2. 采样控制系统的稳定性")
    r.body_math(["被控对象为积分时间常数 ", ("m", r"T_i=0.2"), " s 的积分环节与惯性时间常数 ",
                 ("m", r"T_1=0.5"), " s 的惯性环节串联，即"])
    r.disp_math(r"G_0(s)=\frac{K}{0.2s}\cdot\frac{1}{0.5s+1}")
    r.body_math(["取开环增益 K = 5，按前述方法求得广义对象离散模型中的系数，由 Jury 判据"])
    r.disp_math(r"|c_0|<1,\qquad |c_1|<1+c_0,\qquad c_0=p+b_2,\quad c_1=-(1+p-b_1)")
    r.body_math(["可求出使系统恰好临界稳定的采样周期为 ", ("m", r"T^{*}=0.0823"),
                 " s。分别设置采样周期为 0.015 s、0.03 s、0.09 s，实测输出波形如图 5~图 7 所示"
                 "（白线为 CH1 系统输出，红线为 CH2 控制器输出）。"])
    for f, cap in [("7.2 0.015.jpg", "图 5  采样周期 T = 0.015 s 时系统的输出波形"),
                   ("7.2 0.03.jpg", "图 6  采样周期 T = 0.03 s 时系统的输出波形"),
                   ("7.2 0.09.jpg", "图 7  采样周期 T = 0.09 s 时系统的输出波形")]:
        r.figure(os.path.join(HERE, f), cap, 13.5)
    r.body_math(["T = 0.015 s 时，系统输出迅速衰减至稳态，超调较小，约经过 5~6 次振荡即进入稳态，"
                 "控制量初期出现一次较大的反向脉冲后很快归零，系统稳定性最好。T = 0.03 s 时，输出"
                 "仍然收敛，但振荡次数增至 6~7 次，衰减明显变慢，超调量增大，说明系统的稳定裕度"
                 "已经下降。T = 0.09 s 时，输出出现等幅振荡，振幅不再随时间衰减，系统已进入临界"
                 "稳定状态。"])
    r.body_math(["将采样周期继续调整至 0.083 s 附近时，同样观察到等幅振荡现象，如图 8 所示。"])
    r.figure(os.path.join(HERE, "7.2.1 0.083.jpg"),
             "图 8  采样周期 T = 0.083 s 时系统的临界振荡波形", 13.5)
    r.body_math(["实测临界采样周期为 0.083 s，与理论计算值 0.0823 s 的相对误差仅为 0.85%，理论与"
                 "实验吻合良好。对比图 6 与图 7 可以清楚看到：采样周期小于临界值时系统稳定且衰减"
                 "振荡，接近临界值后系统转为等幅振荡，这验证了“采样周期必须小于临界采样周期”这一"
                 "结论。"])

    r.h2("3. 被控对象改变后的临界采样周期")
    r.body_math(["改变被控对象参数，测出另外两组对象下的临界稳定采样周期，结果列于表 1。"])
    r.table(["序号", "积分时间常数 Ti/s", "开环增益 K", "惯性时间常数 T1/s",
             "临界采样周期计算值/s", "临界采样周期测量值/s", "相对误差"],
            [["1", "0.2", "5", "0.5", "0.0823", "0.083", "0.85%"],
             ["2", "0.2", "3", "0.5", "0.1398", "0.139", "0.57%"],
             ["3", "0.1", "2", "0.2", "0.1100", "0.109", "0.91%"]],
            widths=[1.1, 2.3, 1.5, 2.3, 2.6, 2.6, 1.6])
    r.caption("表 1  三组被控对象的临界稳定采样周期")
    for f, cap in [("7.3.2 0.139.jpg",
                    "图 9  第 2 组对象（Ti = 0.2 s，K = 3，T1 = 0.5 s）在 T = 0.139 s 时的临界振荡波形"),
                   ("7.3.3 0.109.jpg",
                    "图 10  第 3 组对象（Ti = 0.1 s，K = 2，T1 = 0.2 s）在 T = 0.109 s 时的临界振荡波形")]:
        r.figure(os.path.join(HERE, f), cap, 13.5)
    r.body_math(["三组数据的计算值与测量值相对误差均在 1% 以内，表明所建立的广义对象离散模型及 "
                 "Jury 判据能够准确预测采样系统的临界稳定条件。"])
    r.body_math(["进一步分析可见：临界采样周期与积分时间常数 Ti、开环增益 K、惯性时间常数 T1 三者"
                 "均有关。当 K 由 5 降至 3 时（第 1、2 组），临界采样周期由 0.0823 s 增大到 0.1398 s，"
                 "即增益降低使系统稳定范围扩大；当 Ti 由 0.2 s 减小到 0.1 s、T1 由 0.5 s 减小到 0.2 s "
                 "且 K = 2 时（第 3 组），临界采样周期为 0.1100 s。这说明增大惯性时间常数或降低开环"
                 "增益均能提高系统对采样周期的容许上限。"])

    r.h2("4. 最少拍无纹波控制系统的输出波形")
    r.body_math(["按教材图 8-1 搭接模拟电路后，分别设置教材表 8-1 给出的两组控制参数，记录电路输出波形"
                 "（白线为 CH1 系统输出，红线为 CH2 控制器输出），时基 500 ms/格，如图 11、图 12 所示。"])
    r.figure(os.path.join(HERE, "8.1.1.jpg"),
             "图 11  表 8-1 第 1 组参数（K0 = 0.54，K1 = −0.2，P1 = 0.72）下的输出波形", 13.5)
    r.figure(os.path.join(HERE, "8.1.2.jpg"),
             "图 12  表 8-1 第 2 组参数（K0 = 0.32，K1 = −0.12，P1 = 0.42）下的输出波形", 13.5)
    r.body_math(["第 1 组参数下，系统输出经过一次明显超调后进入衰减振荡，约 3~4 个采样周期后趋于"
                 "稳态；控制器输出的控制量呈现交替正负的脉冲序列，正脉冲幅值最大，随后负脉冲、"
                 "正脉冲依次递减，最终归零，其形态与最少拍控制“控制量在有限拍内衰减至零”的特征"
                 "相符。第 2 组参数下，系统输出波形更为平滑，超调量明显减小，几乎呈单调上升并迅速"
                 "稳定；控制器输出仅出现一个较小的正向脉冲与一个很小的负向脉冲，随即归零。"])
    r.body_math(["两组波形的差异说明：控制量脉冲序列的衰减速度直接决定了输出的振荡程度。第 2 组"
                 "参数下控制量衰减更快，因而输出更接近无纹波的一拍到位过程。"])
    r.body_math(["按本实验被控对象（", ("m", r"T_i=0.2"), " s，", ("m", r"T_1=1.0"), " s，K = 1，"
                 "T = 1 s）代入前述设计公式，理论计算得"])
    r.disp_math(r"p=e^{-1}=0.3679,\qquad b_1=1.8394,\qquad b_2=1.3212")
    r.disp_math(r"K_0=\frac{1}{b_1}=0.5437,\qquad K_1=-\frac{p}{b_1}=-0.2000")
    r.disp_math(r"P_1=\frac{b_2}{b_1}=0.7183")
    r.body_math(["理论计算得到的 K0 = 0.5437、K1 = −0.2000 与教材表 8-1 第 1 组给出的 "
                 "K0 = 0.54、K1 = −0.2 完全一致，说明该组参数正是按上述被控对象参数设计的最少拍解。"
                 "此时闭环脉冲传递函数为 ", ("m", r"\Phi(z)=z^{-1}"),
                 "，即采样点上的误差在第一个采样周期之后恒为零，对应的控制量序列为"])
    r.disp_math(r"u(k)=\left[\,0.544,\ -0.591,\ 0.424,\ -0.305,\ 0.219,\ \cdots\,\right]")
    r.body_math(["这一交替衰减的脉冲序列与图 11 中红线所呈现的形态一致。"])

    # ---------------- 课后作业 ----------------
    r.h1("课后作业：s 平面与 z 平面的映射关系")
    r.h2("1. 映射原理")
    r.body_math(["采样系统的 z 变换与拉普拉斯变换之间由映射关系 ", ("m", r"z=e^{sT}"),
                 " 相联系。设 ", ("m", r"s=\sigma+j\omega"), "，则"])
    r.disp_math(r"|z|=e^{\sigma T},\qquad \angle z=\omega T")
    r.body_math(["由此可知：s 左半平面（σ < 0）映射到 z 平面单位圆内（|z| < 1），s 右半平面映射到"
                 "单位圆外，s 虚轴（σ = 0）映射为单位圆本身。这正是采样系统稳定判据与连续系统稳定"
                 "判据相互对应的根本原因。又因 z 是 s 的周期函数，周期为 ", ("m", r"j\omega_s"),
                 "（", ("m", r"\omega_s=2\pi/T"), "），故 s 平面上宽度为 ωs 的横带即可映射满整个 "
                 "z 平面，其余各带均为该带的重复。"])
    r.h2("2. 恒定阻尼比轨迹的映射")
    r.body_math(["以恒定阻尼比轨迹为例，系统特征根为"])
    r.disp_math(r"s=-\zeta\omega_n+j\omega_n\sqrt{1-\zeta^2}")
    r.body_math(["代入映射关系得"])
    r.disp_math(r"z=e^{-\zeta\omega_n T}\cdot e^{\,j\omega_n T\sqrt{1-\zeta^2}}")
    r.body_math(["其模为 ", ("m", r"r=e^{-\zeta\omega_n T}"), "，辐角为 ",
                 ("m", r"\theta=\omega_n T\sqrt{1-\zeta^2}"), "。当 ", ("m", r"\omega_n"),
                 " 由 0 增大到∞时，r 由 1 单调减小到 0，θ 由 0 单调增大，因此恒定阻尼比轨迹在 "
                 "z 平面上映射为一条由单位圆上的点（ωn = 0）出发、绕原点向内盘旋收敛于原点的"
                 "对数螺线。"])
    r.body_math(["综上，本作业给出的 s 平面轨迹与其在 z 平面的映射轨迹为：恒定阻尼比射线映射为"
                 "上述对数螺线，且 ζ 越大螺线越靠近实轴；恒定频率的水平线映射为过原点的射线，"
                 "其辐角等于 ωT；s 平面上宽度为 ωs 的横带映射为整个 z 平面。"])

    # ---------------- 实验总结 ----------------
    r.h1("实验总结")
    r.body_math(["通过本次采样系统分析与最少拍数字控制器设计实验，完整经历了从被控对象建模、"
                 "离散化推导、理论设计到硬件电路验证的全过程。实验中首先由被控对象的连续传递函数"
                 "解析求出单位阶跃响应，进而得到含零阶保持器的广义脉冲传递函数，并据此建立了采样"
                 "系统的闭环特征方程。借助 Jury 判据计算了三组不同被控对象参数下的临界稳定采样周期，"
                 "分别为 0.0823 s、0.1398 s 与 0.1100 s，实测值 0.083 s、0.139 s 与 0.109 s 与之"
                 "吻合，相对误差均在 1% 以内，验证了理论模型的正确性。"])
    r.body_math(["在最少拍无纹波控制部分，由 φ(z)=z⁻¹ 反解出数字调节器的脉冲传递函数，得到了 ",
                 ("m", r"K_0=1/b_1"), "、", ("m", r"K_1=-pK_0"), "、", ("m", r"P_1=b_2/b_1"),
                 " 这一组定量关系，并据此计算出本实验被控对象的理论调节器系数为 K0 = 0.5437、"
                 "K1 = −0.2000、P1 = 0.7183，与教材表 8-1 第 1 组参数完全一致。实测波形的控制量序列"
                 "呈现正负交替、逐拍衰减并最终归零的形态，与最少拍控制“有限拍内控制量归零、采样点"
                 "误差为零”的设计目标相符。"])
    r.body_math(["通过本次实验，将采样周期、开环增益、时间常数与系统稳定性之间的定量联系，以及"
                 "调节器系数与被控对象参数之间的解析关系建立了起来，达到了预期的实验目的。"])

    r.save(OUT_DOCX)
    print("已生成:", OUT_DOCX)
    print("大小: %.1f KB" % (os.path.getsize(OUT_DOCX) / 1024))


if __name__ == "__main__":
    # 报告中全部图片均为本人实测照片，不使用任何生成/示意图
    P(*[os.path.join(HERE, f) for f in
        ("T0.01实验一.jpg", "T0.05实验一.jpg", "T0.1实验一.jpg", "T0.2实验一.jpg",
         "7.2 0.015.jpg", "7.2 0.03.jpg", "7.2 0.09.jpg", "7.2.1 0.083.jpg",
         "7.3.2 0.139.jpg", "7.3.3 0.109.jpg", "8.1.1.jpg", "8.1.2.jpg")])
    build()




