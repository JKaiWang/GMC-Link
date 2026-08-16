"""Two-alpha keyword-routed LOSO campaign driver (Track C1).
Pre-reg: docs/PREREG_TWO_ALPHA_ROAD_2026_08_16.md

Per arm: (1) diagonal integrity check (am=aa=0.5 must reproduce single-alpha
alpha0.5 exactly, seed0); (2) LOSO fold sweep over the 2D grid (pooled only);
(3) componentwise-median selection with per-axis censoring; (4) full-test at
the selected point (n=3). Full-test is NOT run at every cell (cost).

Usage:
    python run_two_alpha_sweep.py --suffix-template _sw12d_groad_seed{seed}_warm11 \
        --am 0.3,0.5,0.7,1.0,1.5,2.0 --aa 0.1,0.2,0.35,0.5,0.7 \
        --out-dir results/two_alpha_road
"""
import argparse, itertools, json, os, statistics, subprocess, sys

REPO = "/home/seanachan/GMC-Link"
OUT_ROOT = "hota_eval_ikun_linear_additive"
FOLDS = {"hold0005": "0011,0013", "hold0011": "0005,0013", "hold0013": "0005,0011"}


def run_one(seed, am, aa, suffix_template, eval_seqs=None):
    suffix = suffix_template.format(seed=seed)
    env = dict(os.environ, GMC_SUFFIX=suffix, OUT_SUFFIX=suffix)
    if eval_seqs:
        env["GMC_EVAL_SEQS"] = eval_seqs
    else:
        env.pop("GMC_EVAL_SEQS", None)
    tag = f"am{am}_aa{aa}"
    if eval_seqs:
        tag += "_seqs" + "-".join(eval_seqs.split(","))
    result_path = os.path.join(REPO, OUT_ROOT + suffix, tag, "result.json")
    if not os.path.exists(result_path):
        cmd = [sys.executable, os.path.join(REPO, "run_ikun_linear_additive.py"),
               "--alpha-mot", str(am), "--alpha-app", str(aa)]
        proc = subprocess.run(cmd, env=env, cwd=REPO)
        if proc.returncode != 0 or not os.path.exists(result_path):
            sys.stderr.write(f"FAIL seed={seed} am={am} aa={aa} seqs={eval_seqs}\n")
            return None
    return json.load(open(result_path))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--suffix-template", required=True)
    p.add_argument("--am", required=True)
    p.add_argument("--aa", required=True)
    p.add_argument("--seeds", default="0,1,2")
    p.add_argument("--out-dir", required=True)
    p.add_argument("--skip-integrity", action="store_true")
    args = p.parse_args()
    AM = [float(x) for x in args.am.split(",")]
    AA = [float(x) for x in args.aa.split(",")]
    seeds = [int(s) for s in args.seeds.split(",")]
    os.makedirs(args.out_dir, exist_ok=True)

    # (1) diagonal integrity: am=aa=0.5 == single-alpha 0.5 (seed0)
    if not args.skip_integrity:
        diag = run_one(seeds[0], 0.5, 0.5, args.suffix_template)
        ref_path = os.path.join(
            REPO, OUT_ROOT + args.suffix_template.format(seed=seeds[0]),
            "alpha0.5", "result.json")
        ref = json.load(open(ref_path))
        if diag is None or abs(diag["pooled"] - ref["pooled"]) > 1e-9:
            print(f"INTEGRITY FAIL diag={diag and diag['pooled']} ref={ref['pooled']}")
            sys.exit(1)
        print(f"integrity OK: diagonal 0.5/0.5 == alpha0.5 == {ref['pooled']}", flush=True)

    # (2) LOSO fold sweep, pooled only
    fold_rows = []
    for fname, infold in FOLDS.items():
        for am, aa in itertools.product(AM, AA):
            for s in seeds:
                r = run_one(s, am, aa, args.suffix_template, eval_seqs=infold)
                if r:
                    fold_rows.append(dict(fold=fname, am=am, aa=aa, seed=s,
                                          pooled=r["pooled"]))
            print(f"{fname} am={am} aa={aa} done", flush=True)

    # (3) selection: per-fold argmax of mean pooled -> componentwise median
    argmaxes = {}
    for fname in FOLDS:
        best, best_cell = -1, None
        for am, aa in itertools.product(AM, AA):
            vals = [r["pooled"] for r in fold_rows
                    if r["fold"] == fname and r["am"] == am and r["aa"] == aa]
            if vals and statistics.mean(vals) > best:
                best, best_cell = statistics.mean(vals), (am, aa)
        argmaxes[fname] = dict(cell=best_cell, pooled=round(best, 3))
    def sel(axis_vals, idx, gridmax):
        unc = [argmaxes[f]["cell"][idx] for f in FOLDS
               if argmaxes[f]["cell"][idx] != gridmax]
        if len(unc) < 2:
            return None  # axis unresolved per pre-reg
        m = statistics.median(sorted(unc))
        # median between grid points -> lower grid point (pre-reg)
        return m if m in axis_vals else max(v for v in axis_vals if v < m)
    am_star = sel(AM, 0, max(AM))
    aa_star = sel(AA, 1, max(AA))

    out = {"suffix_template": args.suffix_template, "grid_am": AM, "grid_aa": AA,
           "fold_argmaxes": argmaxes, "am_star": am_star, "aa_star": aa_star,
           "fold_rows": fold_rows}
    # (4) full-test at selected point
    if am_star is not None and aa_star is not None:
        full = [run_one(s, am_star, aa_star, args.suffix_template) for s in seeds]
        full = [r for r in full if r]
        agg = {}
        for m in ("pooled", "moving", "static", "appearance"):
            vals = [r[m] for r in full if r.get(m) is not None]
            agg[f"{m}_mean"] = round(statistics.mean(vals), 3) if vals else None
            agg[f"{m}_std"] = round(statistics.stdev(vals), 3) if len(vals) > 1 else 0.0
        out["full_test_at_star"] = {"per_seed": full, "aggregate": agg}
        print("FULL-TEST @", (am_star, aa_star), agg, flush=True)
    else:
        print("AXIS UNRESOLVED:", "am" if am_star is None else "", "aa" if aa_star is None else "", flush=True)

    json.dump(out, open(os.path.join(args.out_dir, "two_alpha_campaign.json"), "w"), indent=1)
    print("TWO_ALPHA_DONE", flush=True)


if __name__ == "__main__":
    main()
