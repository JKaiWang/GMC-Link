"""Welch t-statistics for the n=5 ablation (A34 arms) — record A38.

Reads results/ablation_n5_hedge.json (arms A-full/A-noego/A-nomulti = Option A sim
chain @0.5; B-full/B-noego/B-nomulti = Option B road chain @(0.7,0.1); per_seed =
5 dicts {pooled, moving, static, appearance, seed}). For each arm, full vs each
ablation, each metric: Welch t (positive = full > ablated), Welch-Satterthwaite
df, two-sided p. Writes results/ablation_n5_welch.json and prints the table.

Rebuilt 2026-08-25: the #29 comment cited this file + JSON as A38, but neither
was on the tree. Expected B-arm set from that comment: t 11.8/6.2 (MOVING
-ego/-multi), 11.7/6.7 (pooled); p in {1.75e-5, 9.81e-6, 1.84e-3, 1.76e-3}.

Run: /home/seanachan/miniconda/bin/python diagnostics/welch_ablation_n5.py
"""
import json
import os

import numpy as np
from scipy import stats

REPO = "/home/seanachan/GMC-Link"
SRC = os.path.join(REPO, "results", "ablation_n5_hedge.json")
OUT = os.path.join(REPO, "results", "ablation_n5_welch.json")
METRICS = ["pooled", "moving", "static", "appearance"]


def welch(a, b):
    r = stats.ttest_ind(a, b, equal_var=False)
    return {"t": round(float(r.statistic), 3), "df": round(float(r.df), 2),
            "p": float(r.pvalue), "delta": round(float(np.mean(b) - np.mean(a)), 3),
            "full_mean": round(float(np.mean(a)), 3), "full_std": round(float(np.std(a, ddof=1)), 3),
            "abl_mean": round(float(np.mean(b)), 3), "abl_std": round(float(np.std(b, ddof=1)), 3), "n": len(a)}


def main():
    d = json.load(open(SRC))
    out = {"source": SRC, "protocol": d.get("protocol"), "test": "Welch two-sided, scipy.stats.ttest_ind(equal_var=False)",
           "arms": {}}
    for arm in ("A", "B"):
        full = d[f"{arm}-full"]["per_seed"]
        for abl in ("noego", "nomulti"):
            rows = d[f"{arm}-{abl}"]["per_seed"]
            key = f"{arm}-full_vs_{arm}-{abl}"
            out["arms"][key] = {}
            for m in METRICS:
                a = [r[m] for r in full]
                b = [r[m] for r in rows]
                if any(v is None for v in a + b):
                    continue
                out["arms"][key][m] = welch(a, b)
    json.dump(out, open(OUT, "w"), indent=1)
    print(f"{'comparison':<22}{'metric':<12}{'full':>9}{'ablated':>9}{'delta':>8}{'t':>7}{'df':>6}{'p':>10}")
    for key, ms in out["arms"].items():
        for m, w in ms.items():
            print(f"{key:<22}{m:<12}{w['full_mean']:>9.3f}{w['abl_mean']:>9.3f}{w['delta']:>+8.3f}"
                  f"{w['t']:>7.1f}{w['df']:>6.1f}{w['p']:>10.2e}")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
