"""iKUN cascade+simcalib + single-alpha additive GMC fusion on 3-seq POOLED HOTA.

Fusion (2026-08-10 simplification, all expressions, no class branching):

    fused = cs + b + alpha * gmc        # gmc = raw cosine in [-1, +1]
    keep iff fused > 0.0                # native baseline gate (frozen)

alpha=0 reproduces the native cascade+simcalib baseline exactly (44.224 local,
paper-pure 44.564). GMC caches contain raw cosine (builders emit raw cos unconditionally).

The motion-keyword classifier below is used ONLY for per-class HOTA grouping
(MOVING/STATIC/APPEARANCE rows), never in the fusion path.

Usage:
    GMC_SUFFIX=_sw12d_seed0 python run_ikun_linear_additive.py --alpha 0.3
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, "/home/seanachan/GMC-Link")
sys.path.insert(0, "/home/seanachan/iKUN")

from utils import expression_conversion as ikun_expression_conversion

from gmc_link.demo_inference import load_ikun_scores, load_neuralsort_tracks

# V1 defaults; override via env for V2 (iKUN-V2 cross-split eval).
DATA_ROOT      = os.environ.get("IKUN_DATA_ROOT", "/home/seanachan/GMC-Link/refer-kitti")
TRACK_DIR      = "/home/seanachan/GMC-Link/NeuralSORT"
GT_TEMPLATE    = os.environ.get("IKUN_GT_TEMPLATE", "/home/seanachan/data/Dataset/refer-kitti/gt_template_old")
TEXT_FEAT_JSON = os.environ.get("IKUN_TEXT_FEAT_JSON", "/home/seanachan/GMC-Link/iKUN/text_feat_bboxNum_v1.json")
CASCADE_FULL   = os.environ.get("IKUN_CASCADE_JSON", "/home/seanachan/GMC-Link/iKUN/ikun_results_v1_cascade_full.json")
_GMC_SUFFIX = os.environ.get("GMC_SUFFIX", "")  # e.g. "_seed0"
_GMC_CACHE_VER = os.environ.get("GMC_CACHE_VER", "v1")  # v1|v2 cache filename tag
GMC_CACHE_TPL  = "/home/seanachan/GMC-Link/gmc_link/gmc_scores_" + _GMC_CACHE_VER + "_{seq}" + _GMC_SUFFIX + "_cache.json"
TRACKEVAL      = "/home/seanachan/TempRMOT/TrackEval/scripts/run_mot_challenge.py"
_OUT_SUFFIX = os.environ.get("OUT_SUFFIX", "")  # e.g. "_seed0"
OUT_ROOT       = os.environ.get("IKUN_OUT_ROOT", "/home/seanachan/GMC-Link/hota_eval_ikun_linear_additive" + _OUT_SUFFIX)

TEST_SEQS = os.environ.get("GMC_EVAL_SEQS", "0005,0011,0013").split(",")  # LOSO folds override
FRAMES = {"0005": (0, 296), "0011": (0, 372), "0013": (0, 339)}
SIM_A, SIM_B, SIM_TAU = 8.0, -0.1, 100.0

MOTION_KW = ["moving","walking","running","turning","faster","slower","braking",
             "parking","parked","stopped","stop","stand","static","stationary","accelerat"]
STATIC_KW = ["parking","parked","stopped","stop","stand","static","stationary"]


def is_motion(e): return any(k in e.lower() for k in MOTION_KW)
def classify(e):
    if not is_motion(e): return "APPEARANCE"
    if any(k in e.lower() for k in STATIC_KW): return "STATIC"
    return "MOVING"


def compute_simcalib_bias(text_feat, exprs):
    train_dict, test_dict = text_feat["train"], text_feat["test"]
    keys = list(train_dict.keys())
    FEATS = np.array([train_dict[k]["feature"] for k in keys])
    PROBS = np.array([train_dict[k]["probability"] for k in keys])
    bias = {}
    for expr in exprs:
        en = ikun_expression_conversion(expr)
        target = test_dict if en in test_dict else train_dict
        if en not in target: bias[expr] = 0.0; continue
        feat = np.array(target[en]["feature"])[None, :]
        sim = (feat @ FEATS.T)[0]
        sim = (sim - sim.min()) / (sim.max() - sim.min() + 1e-12)
        w = np.exp(SIM_TAU * sim); w = w / w.sum()
        prob = float((w * PROBS).sum())
        bias[expr] = SIM_A * prob + SIM_B
    return bias


def merged_ns(seq):
    car = load_neuralsort_tracks(os.path.join(TRACK_DIR, seq, "car", "predict.txt"))
    ped = load_neuralsort_tracks(os.path.join(TRACK_DIR, seq, "pedestrian", "predict.txt"))
    max_car = 0
    for fid, dets in car.items():
        for oid, *_ in dets: max_car = max(max_car, oid)
    ns = defaultdict(list)
    for fid, dets in car.items(): ns[fid].extend(dets)
    for fid, dets in ped.items():
        ns[fid].extend([(oid+max_car, x, y, w, h) for oid, x, y, w, h in dets])
    return ns


def gen_predicts(text_feat, gmc_caches, alpha, run_dir, alpha_app=None):
    # alpha_app None → single-α (ship). Else two-α keyword routing (Track C1
    # pre-reg): α_mot(=alpha) for MOVING/STATIC-classified exprs, α_app for
    # APPEARANCE. Router = classify(); am==aa reproduces single-α exactly.
    res_dir = os.path.join(run_dir, "results")
    if os.path.exists(res_dir): shutil.rmtree(res_dir)
    os.makedirs(res_dir, exist_ok=True)
    seqmap_lines = []

    for seq in TEST_SEQS:
        ns = merged_ns(seq)
        expr_dir = os.path.join(DATA_ROOT, "expression", seq)
        exprs = sorted(f.replace(".json","") for f in os.listdir(expr_dir) if f.endswith(".json"))
        bias = compute_simcalib_bias(text_feat, exprs)
        gmc_seq = gmc_caches.get(seq, {})
        min_f, max_f = FRAMES[seq]

        for expr in exprs:
            outd = os.path.join(res_dir, seq, expr); os.makedirs(outd, exist_ok=True)
            gt_src = os.path.join(GT_TEMPLATE, seq, expr, "gt.txt")
            gt_dst = os.path.join(outd, "gt.txt")
            if os.path.exists(gt_src): shutil.copy2(gt_src, gt_dst)
            else: open(gt_dst, "w").close()
            open(os.path.join(outd, "predict.txt"), "w").close()
            seqmap_lines.append(f"{seq}+{expr}")

            ikun_scores = load_ikun_scores(CASCADE_FULL, seq, expr)
            b = bias.get(expr, 0.0)
            per_expr_gmc = gmc_seq.get(expr, {})
            a_expr = alpha if alpha_app is None else (
                alpha if classify(expr) != "APPEARANCE" else alpha_app)

            rows = []
            for fid, dets in ns.items():
                if not (min_f < fid < max_f): continue
                for oid, x, y, w, h in dets:
                    cs = ikun_scores.get(fid, {}).get(oid)
                    if cs is None: continue
                    gmc = float(per_expr_gmc.get(str(fid), {}).get(str(oid), 0.0))
                    fused = cs + b + a_expr * gmc
                    if fused > 0.0:
                        rows.append((fid, oid, x, y, w, h))

            with open(os.path.join(outd, "predict.txt"), "w") as f:
                for fid, oid, x, y, w, h in rows:
                    f.write(f"{fid},{oid},{x:.2f},{y:.2f},{w:.2f},{h:.2f},1,1,1\n")

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
        if not lines: return None
        open(sm, "w").write("\n".join(lines) + "\n")
    sp = os.path.join(results_dir, "pedestrian_summary.txt")
    if os.path.exists(sp): os.remove(sp)
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
    args = p.parse_args()
    two_a = args.alpha_mot is not None or args.alpha_app is not None
    if two_a and (args.alpha_mot is None or args.alpha_app is None or args.alpha is not None):
        p.error("use either --alpha alone, or --alpha-mot AND --alpha-app")
    if not two_a and args.alpha is None:
        p.error("--alpha required")

    print("Loading text_feat + GMC caches...", flush=True)
    text_feat = json.load(open(TEXT_FEAT_JSON))
    gmc_caches = {s: json.load(open(GMC_CACHE_TPL.format(seq=s))) for s in TEST_SEQS}

    tag = (f"am{args.alpha_mot}_aa{args.alpha_app}" if two_a
           else f"alpha{args.alpha}")
    if os.environ.get("GMC_EVAL_SEQS"):
        # fold-scoped output dir: LOSO runs must never clobber full-test result.json
        tag += "_seqs" + "-".join(TEST_SEQS)
    run_dir = os.path.join(OUT_ROOT, tag)
    os.makedirs(run_dir, exist_ok=True)
    print(f"\n=== {tag}: fused = cs + b + alpha(expr) * gmc, gate 0.0 ===", flush=True)
    res_dir, sm = gen_predicts(
        text_feat, gmc_caches,
        args.alpha_mot if two_a else args.alpha, run_dir,
        alpha_app=args.alpha_app if two_a else None)
    result = {
        "arch": "ikun",
        "alpha": args.alpha,
        "alpha_mot": args.alpha_mot,
        "alpha_app": args.alpha_app,
        "gmc_suffix": _GMC_SUFFIX,
        "eval_seqs": TEST_SEQS,
        "pooled": run_te(sm, res_dir),
        "moving": run_te(sm, res_dir, class_filter="MOVING"),
        "static": run_te(sm, res_dir, class_filter="STATIC"),
        "appearance": run_te(sm, res_dir, class_filter="APPEARANCE"),
    }
    with open(os.path.join(run_dir, "result.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"  pooled={result['pooled']}  MOVING={result['moving']}  "
          f"STATIC={result['static']}  APPEAR={result['appearance']}", flush=True)
    print(f"  result.json → {run_dir}")
    print("\nReference: paper-pure 44.564 | reproduced native (alpha=0) 44.224")


if __name__ == "__main__":
    main()
