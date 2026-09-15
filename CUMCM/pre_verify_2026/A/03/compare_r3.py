# -*- coding: utf-8 -*-
"""校验 03 文件夹产物与已验证的 out/ 产物逐格一致(在 legion 上运行)。"""
import sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import openpyxl

p1 = r'D:\CUMCM\A\03\result3.xlsx'
p2 = r'D:\CUMCM\A\out\result3.xlsx'
wb1 = openpyxl.load_workbook(p1, read_only=True)
wb2 = openpyxl.load_workbook(p2, read_only=True)
assert wb1.sheetnames == wb2.sheetnames, (wb1.sheetnames, wb2.sheetnames)
for n in wb1.sheetnames:
    ws1, ws2 = wb1[n], wb2[n]
    rows1 = [tuple(r) for r in ws1.iter_rows(values_only=True)]
    rows2 = [tuple(r) for r in ws2.iter_rows(values_only=True)]
    assert len(rows1) == len(rows2), (n, len(rows1), len(rows2))
    assert rows1[0] == rows2[0], ('表头不一致', rows1[0], rows2[0])
    ndiff = 0
    maxd = 0.0
    for a, b in zip(rows1[1:], rows2[1:]):
        if a != b:
            ndiff += 1
            for x, y in zip(a, b):
                if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                    maxd = max(maxd, abs(x - y))
    print(f'[{n}] 数据行 {len(rows1)-1}, 逐格不同行 {ndiff}, 最大数值差 {maxd:g}')

# tables3.json vs tables.json 的表5
d1 = json.load(open(r'D:\CUMCM\A\03\tables3.json', encoding='utf-8'))
d2 = json.load(open(r'D:\CUMCM\A\out\tables.json', encoding='utf-8'))
ref = d2['表5']
assert abs(d1['t_end'] - ref['t_end']) < 1e-6, (d1['t_end'], ref['t_end'])
m = 0.0
for a, b in zip(d1['C'], ref['C']):
    assert len(a) == len(b), (len(a), len(b))
    m = max(m, max(abs(x - y) for x, y in zip(a, b)))
print(f'表5: 烘干时间差 {abs(d1["t_end"]-ref["t_end"]):.3e} s, 水分浓度最大绝对差 {m:.3e}')
print('校验完成: 03 产物与已验证产物一致。')
