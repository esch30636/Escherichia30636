"""Rank the delivered result3.xlsx against the N=6400 converged reference
(same ambient convention), on the 4-decimal values that are actually delivered."""
import numpy as np, openpyxl, json

ref = np.load(r'D:/CUMCM/3/_verify/rt/base/verification/q3_ref6400.npz', allow_pickle=True)
rt  = ref['time_s']; rC = ref['C']
print('ref time_s: %d pts, %.0f..%.0f' % (len(rt), rt[0], rt[-1]), 'C shape', rC.shape)
assert np.allclose(rt, np.r_[np.arange(0, 205861, 60)], atol=1e-9), 'time grid unexpected'

paths = {
 '03_and_03pic        ': "03_and_03pic/03/result3.xlsx",
 '03_and_03pic_audit  ': "03_and_03pic_audit/03/result3.xlsx",
 'A3-codex            ': "A3-codex/A3-codex/result3.xlsx",
 'A3-codex(1)         ': "A3-codex(1)/result3.xlsx",
}
tot = 0; res = {}
for lab, p in paths.items():
    wb = openpyxl.load_workbook(p, read_only=True, data_only=True); ws = wb[wb.sheetnames[0]]
    rows = list(ws.iter_rows(values_only=True)); wb.close()
    hdr = [h for h in rows[0][1:] if isinstance(h, (int, float))]
    assert len(hdr) == 21, (lab, len(hdr))
    tv = np.array([r[0] for r in rows[1:]], float)
    deliv = np.array([[r[j+1] for j in range(21)] for r in rows[1:]], float)
    idx = np.searchsorted(rt, tv); assert np.allclose(rt[idx], tv)
    refv = rC[idx]
    bad = (np.round(deliv, 4) != np.round(refv, 4))
    n = bad.size; tot = n
    worst = int(bad.sum(axis=0)[:1].sum()) if False else None
    res[lab] = dict(cells=int(n), bad=int(bad.sum()), pct=100*bad.sum()/n,
                    per_radius=[int(x) for x in bad.sum(axis=0)],
                    maxdiff=float(np.abs(deliv-refv).max()))
    print('%s  %6d/%6d cells off in 4th decimal = %6.3f%%   max|Δ|=%.2e' % (lab, bad.sum(), n, 100*bad.sum()/n, np.abs(deliv-refv).max()))
    print('      per-radius-col bad counts (0..2.0cm):', [int(x) for x in bad.sum(axis=0)])
json.dump(res, open(r'D:/CUMCM/3/_verify/cellcmp.json','w'), indent=2)
