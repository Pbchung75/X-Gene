"""Paired DT-RF comparison over 12 datasets (k_min = 4), two-sided Wilcoxon signed-rank test,
zero differences discarded (scipy default), Holm correction over the 9 tests.
Data: table4_per_dataset.csv (Supplementary Table S1).  Run:  py paired_tests.py"""
import pandas as pd
from scipy.stats import wilcoxon

d = pd.read_csv("table4_per_dataset.csv")
rows = []
for s in ["mRMR-50", "mRMR-75", "Boruta"]:
    x = d[d.selector == s]
    for key, name in [("cov", "Coverage"), ("fidp", "Active-rule fidelity"), ("conf", "Confidence (all rules)")]:
        rf, dt = x[f"rf_{key}"], x[f"dt_{key}"]
        res = wilcoxon(rf, dt, alternative="two-sided")
        rows.append(dict(selector=s, measure=name, n_pairs=len(x), n_nonzero=int((rf != dt).sum()),
                         rf_gt_dt=int((rf > dt).sum()), rf_lt_dt=int((rf < dt).sum()),
                         mean_dt=dt.mean(), mean_rf=rf.mean(), W=res.statistic, p=res.pvalue))
r = pd.DataFrame(rows).sort_values("p").reset_index(drop=True)
m = len(r)
adj, prev = [], 0.0
for i, p in enumerate(r.p):                      # Holm step-down
    prev = max(prev, min(1.0, (m - i) * p)); adj.append(prev)
r["p_holm"] = adj
r = r.sort_values(["selector", "measure"])
pd.set_option("display.width", 200)
print(r.round(4).to_string(index=False))
r.round(6).to_csv("paired_tests_results.csv", index=False)
