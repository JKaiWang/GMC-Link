"""TransRMOT + additive GMC fusion on the official-150 3-seq POOLED HOTA (A46 P5).

Fusion (Option B form, host referring score in place of iKUN's cs+b):

    fused = refer + alpha(expr) * gmc     # gmc = raw cosine in [-1, +1]
    keep iff fused > 0.5                  # native gate, frozen
                                          # (inference.py filter_dt_by_ref_scores
                                          #  uses STRICT >, not >=)

alpha=0 reproduces the native predict.txt tree BYTE-FOR-BYTE: candidates come
from the A46 pre-gate scores.txt dump (%.17g, exact float32 round-trip), rows
with label==0 are gated and written through the same '{frame},{id},{x1},{y1},
{w},{h},1,1,1' format as inference.py write_results (float64 str), in dump
order. Occluded rows (label==1) never reach predict.txt natively and are
skipped here.

Protocol: official 150-expression seqmap, GT = gt_template/ (TransRMOT frame
convention), classes = gmc_link.moving_kw.classify, TrackEval = the te() recipe.

Usage:
    GMC_SUFFIX=_sw12d_groad_seed0_warm11 OUT_SUFFIX=_sw12d_groad_seed0_warm11 \
        python run_transrmot_linear_additive.py --alpha 0.1
    # two-α keyword routing:
    ... python run_transrmot_linear_additive.py --alpha-mot 1.0 --alpha-app 0.1
    # LOSO folds: GMC_EVAL_SEQS=0005,0013 → fold-scoped out dir (_seqs suffix)
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from collections import defaultdict

sys.path.insert(0, "/home/seanachan/GMC-Link")

from gmc_link.moving_kw import classify  # noqa: E402

SCORES_ROOT = os.environ.get(
    "TRANSRMOT_SCORES_ROOT",
    "/home/seanachan/RMOT/exps/off150_scores/results_epoch99")
GT_TEMPLATE = os.environ.get("TRANSRMOT_GT_TEMPLATE",
                             "/home/seanachan/data/Dataset/refer-kitti/gt_template")
OFFICIAL_SEQMAP = os.environ.get(
    "TRANSRMOT_SEQMAP",
    "/home/seanachan/GMC-Link/seqmaps/refer_kitti_v1_test_official_150.txt")
_GMC_SUFFIX = os.environ.get("GMC_SUFFIX", "")
GMC_CACHE_TPL = ("/home/seanachan/GMC-Link/gmc_link/gmc_scores_transrmot_{seq}"
                 + _GMC_SUFFIX + "_cache.json")
TRACKEVAL = "/home/seanachan/TempRMOT/TrackEval/scripts/run_mot_challenge.py"
_OUT_SUFFIX = os.environ.get("OUT_SUFFIX", "")
OUT_ROOT = os.environ.get("TRANSRMOT_OUT_ROOT",
                          "/home/seanachan/GMC-Link/hota_eval_transrmot_linear_additive"
                          + _OUT_SUFFIX)
GATE = 0.5

TEST_SEQS = os.environ.get("GMC_EVAL_SEQS", "0005,0011,0013").split(",")


def official_exprs():
    """seqmap → {seq: [expr, ...]} restricted to TEST_SEQS."""
    per_seq = defaultdict(list)
    for line in open(OFFICIAL_SEQMAP):
        line = line.strip()
        if not line or "+" not in line:
            continue
        seq, expr = line.split("+", 1)
        if seq in TEST_SEQS:
            per_seq[seq].append(expr)
    return per_seq


def gen_predicts(gmc_caches, alpha, run_dir, alpha_app=None):
    res_dir = os.path.join(run_dir, "results")
    if os.path.exists(res_dir):
        shutil.rmtree(res_dir)
    os.makedirs(res_dir, exist_ok=True)
    seqmap_lines = []
    fmt = '{frame},{id},{x1},{y1},{w},{h},1,1,1\n'  # == inference.py write_results

    for seq, exprs in sorted(official_exprs().items()):
        gmc_seq = gmc_caches.get(seq, {})
        for expr in exprs:
            outd = os.path.join(res_dir, seq, expr)
            os.makedirs(outd, exist_ok=True)
            gt_src = os.path.join(GT_TEMPLATE, seq, expr, "gt.txt")
            gt_dst = os.path.join(outd, "gt.txt")
            if os.path.exists(gt_src):
                shutil.copy2(gt_src, gt_dst)
            else:
                open(gt_dst, "w").close()
            seqmap_lines.append(f"{seq}+{expr}")

            per_expr_gmc = gmc_seq.get(expr, {})
            a_expr = alpha if alpha_app is None else (
                alpha if classify(expr) != "APPEARANCE" else alpha_app)

            scores_path = os.path.join(SCORES_ROOT, seq, expr, "scores.txt")
            with open(os.path.join(outd, "predict.txt"), "w") as out:
                if not os.path.exists(scores_path):
                    continue
                for line in open(scores_path):
                    p = line.rstrip("\n").split(",")
                    if len(p) != 9 or p[8] != "0":  # label==0 rows only
                        continue
                    fid, oid = int(p[0]), int(p[1])
                    x1, y1, x2, y2 = float(p[2]), float(p[3]), float(p[4]), float(p[5])
                    refer = float(p[6])
                    gmc = float(per_expr_gmc.get(p[0], {}).get(p[1], 0.0))
                    if refer + a_expr * gmc > GATE:
                        out.write(fmt.format(frame=fid, id=oid, x1=x1, y1=y1,
                                             w=x2 - x1, h=y2 - y1))

    sm = os.path.join(run_dir, "seqmap.txt")
    open(sm, "w").write("\n".join(seqmap_lines) + "\n")
    return res_dir, sm


def run_te(seqmap_path, results_dir, class_filter=None):
    if class_filter is None:
        sm = seqmap_path
    else:
        sm = os.path.join(os.path.dirname(seqmap_path), f"seqmap_{class_filter}.txt")
        lines = [l for l in open(seqmap_path).read().splitlines()
                 if l and classify(l.split("+", 1)[1]) == class_filter]
        if not lines:
            return None
        open(sm, "w").write("\n".join(lines) + "\n")
    sp = os.path.join(results_dir, "pedestrian_summary.txt")
    if os.path.exists(sp):
        os.remove(sp)
    cmd = [sys.executable, TRACKEVAL,
           "--METRICS", "HOTA",
           "--SEQMAP_FILE", os.path.abspath(sm),
           "--SKIP_SPLIT_FOL", "True",
           "--GT_FOLDER", os.path.abspath(results_dir),
           "--TRACKERS_FOLDER", os.path.abspath(results_dir),
           "--GT_LOC_FORMAT", "{gt_folder}/{video_id}/{expression_id}/gt.txt",
           "--TRACKERS_TO_EVAL", os.path.abspath(results_dir),
           "--USE_PARALLEL", "False", "--PLOT_CURVES", "False", "--PRINT_CONFIG", "False"]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(TRACKEVAL))
    if not os.path.exists(sp):
        sys.stderr.write(f"FAIL ({class_filter}) rc={proc.returncode}\n{proc.stderr[-1500:]}\n")
        return None
    return float(open(sp).read().splitlines()[1].split()[0])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--alpha", type=float)
    p.add_argument("--alpha-mot", type=float, help="two-α: MOVING/STATIC exprs")
    p.add_argument("--alpha-app", type=float, help="two-α: APPEARANCE exprs")
    p.add_argument("--pooled-only", action="store_true",
                   help="skip per-class TrackEval (LOSO fold runs)")
    p.add_argument("--sweep-grid", type=str, default=None,
                   help="comma-separated α values; runs the full α_mot × α_app grid "
                        "in one process (caches loaded once), pooled-only per cell")
    args = p.parse_args()
    if args.sweep_grid:
        grid = [float(v) for v in args.sweep_grid.split(",")]
        gmc_caches = {s: json.load(open(GMC_CACHE_TPL.format(seq=s))) for s in TEST_SEQS}
        for am in grid:
            for aa in grid:
                tag = f"am{am}_aa{aa}"
                if os.environ.get("GMC_EVAL_SEQS"):
                    tag += "_seqs" + "-".join(TEST_SEQS)
                run_dir = os.path.join(OUT_ROOT, tag)
                if os.path.exists(os.path.join(run_dir, "result.json")):
                    continue  # resumable
                os.makedirs(run_dir, exist_ok=True)
                res_dir, sm = gen_predicts(gmc_caches, am, run_dir, alpha_app=aa)
                result = {"arch": "transrmot", "alpha": None, "alpha_mot": am,
                          "alpha_app": aa, "gmc_suffix": _GMC_SUFFIX,
                          "eval_seqs": TEST_SEQS, "pooled": run_te(sm, res_dir),
                          "moving": None, "static": None, "appearance": None}
                with open(os.path.join(run_dir, "result.json"), "w") as f:
                    json.dump(result, f, indent=2)
                print(f"  {tag}: pooled={result['pooled']}", flush=True)
        return
    two_a = args.alpha_mot is not None or args.alpha_app is not None
    if two_a and (args.alpha_mot is None or args.alpha_app is None or args.alpha is not None):
        p.error("use either --alpha alone, or --alpha-mot AND --alpha-app")
    if not two_a and args.alpha is None:
        p.error("--alpha required")

    a0 = (args.alpha_mot if two_a else args.alpha) == 0 and (not two_a or args.alpha_app == 0)
    if a0:
        gmc_caches = {s: {} for s in TEST_SEQS}  # α=0 never reads gmc
    else:
        gmc_caches = {s: json.load(open(GMC_CACHE_TPL.format(seq=s))) for s in TEST_SEQS}

    tag = (f"am{args.alpha_mot}_aa{args.alpha_app}" if two_a
           else f"alpha{args.alpha}")
    if os.environ.get("GMC_EVAL_SEQS"):
        # fold-scoped output dir: LOSO runs must never clobber full-test result.json
        tag += "_seqs" + "-".join(TEST_SEQS)
    run_dir = os.path.join(OUT_ROOT, tag)
    os.makedirs(run_dir, exist_ok=True)
    print(f"\n=== {tag}: fused = refer + alpha(expr) * gmc, gate {GATE} (strict >) ===", flush=True)
    res_dir, sm = gen_predicts(
        gmc_caches,
        args.alpha_mot if two_a else args.alpha, run_dir,
        alpha_app=args.alpha_app if two_a else None)
    result = {
        "arch": "transrmot",
        "alpha": args.alpha,
        "alpha_mot": args.alpha_mot,
        "alpha_app": args.alpha_app,
        "gmc_suffix": _GMC_SUFFIX,
        "eval_seqs": TEST_SEQS,
        "pooled": run_te(sm, res_dir),
        "moving": None if args.pooled_only else run_te(sm, res_dir, class_filter="MOVING"),
        "static": None if args.pooled_only else run_te(sm, res_dir, class_filter="STATIC"),
        "appearance": None if args.pooled_only else run_te(sm, res_dir, class_filter="APPEARANCE"),
    }
    with open(os.path.join(run_dir, "result.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"  pooled={result['pooled']}  MOVING={result['moving']}  "
          f"STATIC={result['static']}  APPEAR={result['appearance']}", flush=True)
    print(f"  result.json → {run_dir}")


if __name__ == "__main__":
    main()
