# -*- coding: utf-8 -*-
"""对 文献库.md 中的全部 DOI 做 Crossref 核验：存在性 + 标题关键词重叠粗判。

用法: python doi_check.py            # 全部 DOI
      python doi_check.py 300 443    # 只查编号区间
输出: _tools/doi_check_report.txt （同时打印摘要）
"""
import re
import sys
import urllib.request
import urllib.error
import json
from concurrent.futures import ThreadPoolExecutor

MD = r'D:\Escherichia30636\CUMCM\cumcm2026\A\文献库.md'
OUT = r'D:\Escherichia30636\CUMCM\cumcm2026\A\_tools\doi_check_report.txt'
UA = {'User-Agent': 'cumcm2026-litcheck/1.0 (mailto:cumcm2026@example.com)'}
STOP = set('the a an of and in for on with to by from at as is are its it their this that '
           'using based study effect effects analysis model modeling modelling during '
           'heat mass transfer drying food materials material new novel via'.split())


def tokens(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9\u4e00-\u9fff ]+', ' ', s)
    return {w for w in s.split() if len(w) > 3 and w not in STOP}


def parse():
    entries = []
    cur = None
    for line in open(MD, encoding='utf-8'):
        m = re.match(r'^\[(\d+)\]\s*(.+)$', line.strip())
        if m:
            cur = {'num': int(m.group(1)), 'body': m.group(2)}
            cur['doi'] = (re.search(r'DOI:\s*([0-9]{2}\.[^\s（]+)', m.group(2)) or [None, None])[1]
            if cur['doi']:
                cur['doi'] = cur['doi'].rstrip('.,;')
            entries.append(cur)
        elif cur and 'DOI:' in line:
            d = re.search(r'DOI:\s*([0-9]{2}\.[^\s（]+)', line)
            if d and not cur['doi']:
                cur['doi'] = d.group(1).rstrip('.,;')
    return [e for e in entries if e['doi']]


CN_PREFIX = ('10.11975', '10.7501', '10.13386', '10.19540', '10.13733', '10.88888',
             '10.14148', '10.16333', '10.13995', '10.13657', '10.16429', '10.13427',
             '10.13922', '10.19554', '10.13335', '10.11841', '10.3976', '10.4268',
             '10.16429', '10.55214')


def doi_resolves(doi):
    """用 doi.org 解析, 判断 DOI 是否真实存在(返回最终 status 或 None)。"""
    try:
        req = urllib.request.Request('https://doi.org/' + doi, headers=UA, method='HEAD')
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status
    except urllib.error.HTTPError as ex:
        return ex.code if ex.code != 404 else None
    except Exception:
        return None


def check(e):
    e = dict(e)
    url = 'https://api.crossref.org/works/' + e['doi']
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=25) as r:
            js = json.loads(r.read().decode('utf-8', 'replace'))
        e['cr_title'] = (js['message'].get('title') or [''])[0]
        e['found'] = True
    except urllib.error.HTTPError as ex:
        e['found'] = False
        e['err'] = 'HTTP %d' % ex.code
        e['cr_title'] = ''
    except Exception as ex:                                    # 网络异常
        e['found'] = False
        e['err'] = type(ex).__name__
        e['cr_title'] = ''
    if not e['found']:
        e['cn'] = e['doi'].startswith(CN_PREFIX)
        e['doi_org'] = doi_resolves(e['doi']) if not e['cn'] else 'skip'
    if e['found']:
        a, b = tokens(e['body'][:200]), tokens(e['cr_title'][:200])
        e['overlap'] = sorted(a & b)
    else:
        e['overlap'] = []
    return e


def main():
    entries = parse()
    lo, hi = 0, 10 ** 9
    if len(sys.argv) == 3:
        lo, hi = int(sys.argv[1]), int(sys.argv[2])
    todo = [e for e in entries if lo <= e['num'] <= hi]
    print('待查 DOI 条数: %d' % len(todo))
    with ThreadPoolExecutor(max_workers=6) as ex:
        res = list(ex.map(check, todo))
    bad_exist = [e for e in res if not e['found']]
    cn_bad = [e for e in bad_exist if e.get('cn')]
    en_bad = [e for e in bad_exist if not e.get('cn')]
    mismatch = [e for e in res if e['found'] and not e['overlap']]
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('DOI 核验报告  共 %d 条\n\n' % len(res))
        f.write('== A1. 中文刊 DOI（Crossref 无记录，属正常，用期刊官网核验）(%d) ==\n' % len(cn_bad))
        for e in cn_bad:
            f.write('[%d] %s\n' % (e['num'], e['doi']))
        f.write('\n== A2. 非中文 DOI 在 Crossref 未找到 (%d) ==\n' % len(en_bad))
        for e in en_bad:
            f.write('[%d] %s  err=%s  doi.org解析=%s\n'
                    % (e['num'], e['doi'], e.get('err', ''), e.get('doi_org')))
        f.write('\n== B. 标题关键词零重叠, 需人工核对 (%d) ==\n' % len(mismatch))
        for e in mismatch:
            f.write('[%d] %s\n      本库: %s\n      Crossref: %s\n'
                    % (e['num'], e['doi'], e['body'][:110], e['cr_title'][:110]))
        f.write('\n== C. 通过 (%d) ==\n' % (len(res) - len(bad_exist) - len(mismatch)))
        for e in res:
            if e['found'] and e['overlap']:
                f.write('[%d] %s | %s\n' % (e['num'], e['doi'], ','.join(e['overlap'][:6])))
    print('未找到: %d 条; 零重叠: %d 条; 通过: %d 条'
          % (len(bad_exist), len(mismatch), len(res) - len(bad_exist) - len(mismatch)))
    for e in bad_exist:
        print('  [未找到] [%d] %s %s' % (e['num'], e['doi'], e.get('err', '')))
    for e in mismatch:
        print('  [零重叠] [%d] %s\n      本库: %s\n      Crossref: %s'
              % (e['num'], e['doi'], e['body'][:100], e['cr_title'][:100]))


if __name__ == '__main__':
    main()
