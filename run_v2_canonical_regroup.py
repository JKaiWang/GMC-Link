"""V2 per-class HOTA regrouping audit (audit A4, DO-NOW 2 in docs/IMPROVEMENT_PLAN_2026_08_13.md).

The shipped V2 per-class rows classify the PARAPHRASED expr_id slug with a
V2-expanded keyword list, while the GMC cache scores the canonical raw_sentence
— 108/862 expressions disagree; the "MOVING" row is 38% canonical-APPEARANCE.
This script re-runs ONLY the TrackEval class grouping on existing predict dirs,
classifying each expression by its canonical text with the V1 keyword lists.
Predicts are untouched; no GPU; no fusion change.

Rows: MOVING / STATIC / APPEARANCE (canonical) + DIRECTION (slug-MOVING but
canonical-APPEARANCE — the 66 diluting expressions isolated).

Usage:
    python run_v2_canonical_regroup.py                 # alphas 0,5; seeds 0,1,2
    python run_v2_canonical_regroup.py --alphas 0,5 --seeds 0,1,2
alpha=0 reads seed0's run dir only (no GMC term => identical across seeds).
"""
import argparse
import json
import os
import statistics
import subprocess
import sys

REPO       = "/home/seanachan/GMC-Link"
DATA_ROOT  = "/home/seanachan/data/Dataset/refer-kitti-v2"
OUT_TPL    = os.path.join(REPO, "hota_eval_flexhook_v2_raw_gmc_sw12d_seed{seed}", "alpha{alpha}")
TRACKEVAL  = "/home/seanachan/TempRMOT/TrackEval/scripts/run_mot_challenge.py"

# Canonical rows: shared A43 classifier (gmc_link/moving_kw.py = the router).
sys.path.insert(0, REPO)
from gmc_link.moving_kw import classify as classify_canonical  # noqa: E402

# Pre-A43 V1 lists, kept ONLY for the legacy slug DIRECTION row below.
MOTION_KW = ["moving","walking","running","turning","faster","slower","braking",
             "parking","parked","stopped","stop","stand","static","stationary","accelerat"]
STATIC_KW = ["parking","parked","stopped","stop","stand","static","stationary"]

# V2-expanded slug lists (= run_flexhook_v2_raw_sweep.py; its classify order)
SLUG_MOTION_KW = MOTION_KW + ["transit","traveling","headed","going","passing","drive",
                              "driving","circulating","in-motion","in-the-process-of-moving"]
SLUG_STATIC_KW = STATIC_KW + ["left-on","abandoned","left-behind"]


def classify_slug(expr_id):
    e = expr_id.lower()
    if any(k in e for k in SLUG_STATIC_KW): return "STATIC"
    if any(k in e for k in SLUG_MOTION_KW): return "MOVING"
    return "APPEARANCE"


def canonical_text(seq, expr_id):
    with open(os.path.join(DATA_ROOT, "expression", seq, expr_id + ".json")) as fh:
        d = json.load(fh)
    return d.get("raw_sentence") or d.get("sentence", "")


def trackeval_hota(seqmap_path, results_dir):
    sp = os.path.join(results_dir, "pedestrian_summary.txt")
    if os.path.exists(sp): os.remove(sp)
    cmd = [sys.executable, TRACKEVAL, "--METRICS", "HOTA",
           "--SEQMAP_FILE", os.path.abspath(seqmap_path),
           "--SKIP_SPLIT_FOL", "True",
           "--GT_FOLDER", os.path.abspath(results_dir),
           "--TRACKERS_FOLDER", os.path.abspath(results_dir),
           "--GT_LOC_FORMAT", "{gt_folder}/{video_id}/{expression_id}/gt.txt",
           "--TRACKERS_TO_EVAL", os.path.abspath(results_dir),
           "--USE_PARALLEL", "False", "--PLOT_CURVES", "False", "--PRINT_CONFIG", "False"]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(TRACKEVAL))
    if not os.path.exists(sp):
        sys.stderr.write(f"TrackEval FAIL rc={proc.returncode}\n{proc.stderr[-1500:]}\n")
        return None
    return float(open(sp).read().splitlines()[1].split()[0])


def regroup_one(run_dir):
    """Return {row_name: HOTA} for canonical MOVING/STATIC/APPEARANCE + DIRECTION."""
    res_dir = os.path.join(run_dir, "results")
    sm_all = os.path.join(run_dir, "seqmap.txt")
    lines = [l for l in open(sm_all).read().splitlines() if l]
    rows = {}
    groups = {"MOVING": [], "STATIC": [], "APPEARANCE": [], "DIRECTION": []}
    for l in lines:
        seq, expr_id = l.split("+", 1)
        canon = classify_canonical(canonical_text(seq, expr_id))
        groups[canon].append(l)
        if canon == "APPEARANCE" and classify_slug(expr_id) == "MOVING":
            groups["DIRECTION"].append(l)
    for name, sel in groups.items():
        if not sel:
            rows[name] = None
            continue
        sm = os.path.join(run_dir, f"seqmap_CANON_{name}.txt")
        open(sm, "w").write("\n".join(sel) + "\n")
        rows[name] = trackeval_hota(sm, res_dir)
        rows[name + "_n"] = len(sel)
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--alphas", default="0,5")
    p.add_argument("--seeds", default="0,1,2")
    p.add_argument("--suffix", default="",
                   help="run-dir suffix after seed, e.g. _nomema_warm11 (candidate ship)")
    p.add_argument("--tree", default="hota_eval_flexhook_v2_raw_gmc_sw12d_seed{seed}",
                   help="run-dir template before --suffix; the road-chain ship needs "
                        "hota_eval_flexhook_v2_raw_gmc_sw12d_groad_seed{seed} (A37)")
    p.add_argument("--out", default=os.path.join(REPO, "results", "v2_canonical_regroup.json"))
    args = p.parse_args()
    global OUT_TPL
    OUT_TPL = os.path.join(REPO, args.tree + args.suffix, "alpha{alpha}")
    alphas = [float(a) for a in args.alphas.split(",")]
    seeds = [int(s) for s in args.seeds.split(",")]

    out = {"canonical_lists": "V1 (iKUN order)", "runs": []}
    for alpha in alphas:
        use_seeds = [seeds[0]] if alpha == 0 else seeds  # a=0: no GMC term, seed-invariant
        for seed in use_seeds:
            run_dir = OUT_TPL.format(seed=seed, alpha=alpha)
            if not os.path.isdir(os.path.join(run_dir, "results")):
                sys.stderr.write(f"SKIP missing {run_dir}\n"); continue
            print(f"regroup alpha={alpha} seed={seed} ...", flush=True)
            rows = regroup_one(run_dir)
            # sanity: run dir must be full-test (4 seqs), not a LOSO fold
            rj = json.load(open(os.path.join(run_dir, "result.json")))
            rows.update(alpha=alpha, seed=seed,
                        slug_result=rj, full_test=len(rj.get("eval_seqs", [1]*4)) == 4)
            out["runs"].append(rows)
            print("  " + "  ".join(f"{k}={rows[k]}" for k in
                  ("MOVING", "STATIC", "APPEARANCE", "DIRECTION")), flush=True)

    # aggregate: canonical delta (alpha!=0 mean vs alpha=0) per row
    base = next((r for r in out["runs"] if r["alpha"] == 0), None)
    for alpha in [a for a in alphas if a != 0]:
        sub = [r for r in out["runs"] if r["alpha"] == alpha]
        if not sub or base is None: continue
        print(f"\n=== canonical grouping: alpha={alpha} (n={len(sub)}) vs alpha=0 ===")
        for name in ("MOVING", "STATIC", "APPEARANCE", "DIRECTION"):
            vals = [r[name] for r in sub if r[name] is not None]
            if not vals or base[name] is None: continue
            mu = statistics.mean(vals)
            sd = statistics.stdev(vals) if len(vals) > 1 else 0.0
            print(f"  {name:<11} n_expr={base[name + '_n']:<4} "
                  f"a{alpha}={mu:.3f}±{sd:.3f}  a0={base[name]:.3f}  Δ={mu - base[name]:+.3f}")

    out_path = args.out
    json.dump(out, open(out_path, "w"), indent=2)
    print(f"\nJSON → {out_path}")


if __name__ == "__main__":
    main()
