"""FlexHook V1 + single-alpha additive GMC fusion on 3-seq POOLED HOTA.

Fusion (2026-08-10 simplification, all expressions, no class branching):

    margin = score[1] - score[0]
    fused  = margin + alpha * gmc       # gmc = raw cosine in [-1, +1]
    keep   = fused > 0.0                # native baseline gate (frozen)

alpha=0 reproduces the reproduced-native FlexHook V1 baseline (53.110).
GMC caches contain raw cosine (builders emit raw cos unconditionally). The keyword
classifier is used ONLY for per-class HOTA grouping, never in fusion.

Usage:
    GMC_SUFFIX=_sw12d_seed0 python run_flexhook_phase5_gmc_sweep.py --alpha 3
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from collections import defaultdict

import numpy as np

FLEXHOOK_RES = "/home/seanachan/FlexHook/retest-kitti-1/refer-kitti-best/results"
RESULT_JSON  = "/home/seanachan/FlexHook/retest-kitti-1/refer-kitti-best/result_0.json"
TRACK_DIR    = "/home/seanachan/FlexHook/FlexHook/tracker_outputs/Temp-NeuralSORT-kitti1"
DATA_ROOT    = "/home/seanachan/GMC-Link/refer-kitti"
GT_TEMPLATE  = "/home/seanachan/FlexHook/datasets/refer-kitti/gt_template"
_GMC_SUFFIX  = os.environ.get("GMC_SUFFIX", "")
GMC_CACHE_TPL= "/home/seanachan/GMC-Link/gmc_link/gmc_scores_flexhook_v1_{seq}" + _GMC_SUFFIX + "_cache.json"
TRACKEVAL    = "/home/seanachan/TempRMOT/TrackEval/scripts/run_mot_challenge.py"
_OUT_SUFFIX  = os.environ.get("OUT_SUFFIX", "")
OUT_ROOT     = "/home/seanachan/GMC-Link/hota_eval_flexhook_phase5_gmc" + _OUT_SUFFIX

TEST_SEQS = os.environ.get("GMC_EVAL_SEQS", "0005,0011,0013").split(",")  # LOSO folds override
FRAMES = {"0005": (0, 296), "0011": (0, 372), "0013": (0, 339)}
MOTION_KW = ["moving", "walking", "running", "turning", "faster", "slower",
             "braking", "parking", "parked", "stopped", "stop", "stand",
             "static", "stationary", "accelerat"]
STATIC_KW = ["parking", "parked", "stopped", "stop", "stand", "static",
             "stationary"]


def is_motion(e): return any(k in e.lower() for k in MOTION_KW)
def is_strict_static(e): return any(k in e.lower() for k in STATIC_KW)
def classify(e):
    el = e.lower()
    if any(k in el for k in STATIC_KW): return "STATIC"
    if any(k in el for k in MOTION_KW): return "MOVING"
    return "APPEARANCE"


def load_tracks(seq):
    car_path = os.path.join(TRACK_DIR, seq, "car", "predict.txt")
    ped_path = os.path.join(TRACK_DIR, seq, "pedestrian", "predict.txt")
    arr_c = np.loadtxt(car_path, delimiter=",") if os.path.getsize(car_path) > 0 else np.empty((0, 10))
    arr_p = np.loadtxt(ped_path, delimiter=",") if os.path.exists(ped_path) and os.path.getsize(ped_path) > 0 else np.empty((0, 10))
    if arr_c.ndim == 1 and arr_c.size: arr_c = arr_c[None, :]
    if arr_p.ndim == 1 and arr_p.size: arr_p = arr_p[None, :]
    if arr_c.size:
        max_obj = arr_c[:, 1].max()
        if arr_p.size:
            arr_p[:, 1] += max_obj
        tracks = np.concatenate([arr_c, arr_p], axis=0) if arr_p.size else arr_c
    else:
        tracks = arr_p
    tracks[:, 0] = tracks[:, 0] - 1
    return tracks


def gen_predicts(cls_dict, tracks_by_seq, gmc_caches, alpha, run_dir):
    res_dir = os.path.join(run_dir, "results")
    if os.path.exists(res_dir): shutil.rmtree(res_dir)
    os.makedirs(res_dir, exist_ok=True)
    seqmap = []

    for seq in TEST_SEQS:
        if seq not in cls_dict: continue
        seq_out = os.path.join(res_dir, seq)
        os.makedirs(seq_out, exist_ok=True)
        expr_dir = os.path.join(DATA_ROOT, "expression", seq)
        exp_files = sorted(f for f in os.listdir(expr_dir) if f.endswith(".json"))
        expr_text_by_id = {}
        for ef in exp_files:
            expr_id = ef.replace(".json", "")
            with open(os.path.join(expr_dir, ef)) as fh:
                expr_text_by_id[expr_id] = json.load(fh)["sentence"]
            outd = os.path.join(seq_out, expr_id)
            os.makedirs(outd, exist_ok=True)
            gt_src = os.path.join(GT_TEMPLATE, seq, expr_id, "gt.txt")
            gt_dst = os.path.join(outd, "gt.txt")
            if os.path.exists(gt_src):
                if os.path.exists(gt_dst) or os.path.islink(gt_dst): os.remove(gt_dst)
                shutil.copy2(gt_src, gt_dst)
            else:
                open(gt_dst, "w").close()
            seqmap.append(f"{seq}+{expr_id}")

        tracks = tracks_by_seq[seq]
        tracks_idx = {}
        for r in tracks:
            k = (int(r[0]), int(r[1]))
            tracks_idx.setdefault(k, r)
        min_f, max_f = FRAMES[seq]
        gmc_seq = gmc_caches.get(seq, {})
        seq_dict = cls_dict[seq]
        pred_buf = defaultdict(list)

        for obj_id, obj_dict in seq_dict.items():
            oid_int = int(obj_id)
            for frame_id, frame_dict in obj_dict.items():
                fid_int = int(frame_id)
                row = tracks_idx.get((fid_int, oid_int))
                if row is None: continue
                bbox = row.copy()
                if not (min_f <= bbox[0] <= max_f): continue
                bbox[0] += 1   # FlexHook predict.txt 1-indexed
                fid_pred = int(bbox[0])
                bbox_str = ",".join(map(str, bbox.tolist()))

                for expr_id, expr_text in expr_text_by_id.items():
                    score = frame_dict.get(expr_text)
                    if score is None: continue
                    margin = float(score[1] - score[0])
                    gmc = float(gmc_seq.get(expr_id, {}).get(str(fid_pred), {}).get(str(oid_int), 0.0))
                    if margin + alpha * gmc > 0.0:
                        pred_buf[expr_id].append(bbox_str)

        for expr_id in expr_text_by_id:
            outd = os.path.join(seq_out, expr_id)
            with open(os.path.join(outd, "predict.txt"), "w") as f:
                lines = pred_buf.get(expr_id, [])
                if lines: f.write("\n".join(lines) + "\n")

    sm_path = os.path.join(run_dir, "seqmap.txt")
    with open(sm_path, "w") as f:
        f.write("\n".join(seqmap) + "\n")
    return res_dir, sm_path


def run_te(seqmap, results_dir, class_filter=None):
    if class_filter is None:
        sm = seqmap
    else:
        sm = os.path.join(os.path.dirname(seqmap), f"seqmap_{class_filter}.txt")
        lines = [l for l in open(seqmap).read().splitlines()
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
           "--USE_PARALLEL", "False", "--PLOT_CURVES", "False",
           "--PRINT_CONFIG", "False"]
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          cwd=os.path.dirname(TRACKEVAL))
    if not os.path.exists(sp):
        sys.stderr.write(f"FAIL ({class_filter}) rc={proc.returncode}\n{proc.stderr[-1500:]}\n")
        return None
    return float(open(sp).read().splitlines()[1].split()[0])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--alpha", type=float, required=True)
    args = p.parse_args()

    print("Loading FlexHook result_0.json (~80MB)...", flush=True)
    with open(RESULT_JSON) as fh:
        cls_dict = json.load(fh)

    print("Loading GMC caches...", flush=True)
    gmc_caches = {}
    for s in TEST_SEQS:
        cp = GMC_CACHE_TPL.format(seq=s)
        if os.path.exists(cp):
            with open(cp) as fh:
                gmc_caches[s] = json.load(fh)
        elif args.alpha != 0:
            # missing cache at alpha>0 would silently evaluate as native (flat
            # sweep labeled as fused) — fail loudly instead, matching iKUN.
            raise FileNotFoundError(
                f"GMC cache missing: {cp} (check GMC_SUFFIX; alpha>0 needs it)")
        else:
            print(f"  WARN: {cp} missing (alpha=0, cache unused)")

    print("Loading tracks...", flush=True)
    tracks_by_seq = {seq: load_tracks(seq) for seq in TEST_SEQS}

    tag = f"alpha{args.alpha}"
    if os.environ.get("GMC_EVAL_SEQS"):
        # fold-scoped output dir: LOSO runs must never clobber full-test result.json
        tag += "_seqs" + "-".join(TEST_SEQS)
    run_dir = os.path.join(OUT_ROOT, tag)
    os.makedirs(run_dir, exist_ok=True)
    print(f"\n=== {tag}: fused = margin + {args.alpha} * gmc, gate 0.0 ===", flush=True)
    res_dir, sm = gen_predicts(cls_dict, tracks_by_seq, gmc_caches, args.alpha, run_dir)
    result = {
        "arch": "fh_v1",
        "alpha": args.alpha,
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
    print("\nReference: published 53.824 | reproduced native (alpha=0) 53.110")


if __name__ == "__main__":
    main()
