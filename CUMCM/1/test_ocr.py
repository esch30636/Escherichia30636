# -*- coding: utf-8 -*-
"""Test OCR on one page of a paper."""
import ssl
if hasattr(ssl.SSLContext, "_load_windows_store_certs"):
    ssl.SSLContext._load_windows_store_certs = lambda self, storename, purpose: None
import fitz, sys
from paddleocr import PaddleOCR

pdf_path = r"D:\CUMCM\_shared\papers\test\2023国赛D题_D039_优秀论文.pdf"
png_path = r"D:\CUMCM\_shared\papers\test\test_page.png"

doc = fitz.open(pdf_path)
page = doc[11]
pix = page.get_pixmap(dpi=200)
pix.save(png_path)
print("saved page 12, size:", pix.width, "x", pix.height)

ocr = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)
res = ocr.ocr(png_path, cls=True)
lines = []
if res:
    for block in res:
        if block:
            for item in block:
                lines.append(item[1][0])
print("\n".join(lines[:40]))
