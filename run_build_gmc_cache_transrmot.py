"""Build GMC caches on TransRMOT candidate streams (A46 P4).

Track source: the A46 pre-gate score dump, one scores.txt per (seq, expression)
under SCORES_ROOT (exps/off150_scores/results_epoch99/{seq}/{expr}/scores.txt),
rows: frame,id,x1,y1,x2,y2,refer,det,label (full %.17g precision).

Unlike iKUN/FlexHook, TransRMOT's candidate set is expression-conditioned (the
track queries see the sentence), so each expression gets its own track stream
and its own manager history — the warm-11 abstention mask is applied INLINE per
expression here. filter_warmup_cache.py's union-grid replay assumes an
expression-independent stream and must NOT be used on these caches.

Ship settings (Option B), same as the other hosts:
    GMC_GROUND_MODE=road GMC_MOTION_EMA=0 \
    GMC_WEIGHTS=gmc_link_weights_v1train_sw12d_groad_seed{N}.pth \
    GMC_SUFFIX=_sw12d_groad_seed{N}_warm11 \
        python run_build_gmc_cache_transrmot.py 0005 0011 0013

Output: gmc_link/gmc_scores_transrmot_{seq}{GMC_SUFFIX}_cache.json
        {expr_slug: {frame: {oid: raw_cos}}}, warm-11 already applied.
"""
import json
import os
import sys
from collections import defaultdict

import cv2
import numpy as np
import torch
from tqdm import tqdm

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from gmc_link.demo_inference import DummyTrack
from gmc_link.manager import GMCLinkManager
from gmc_link.text_utils import TextEncoder

SCORES_ROOT = os.environ.get(
    "TRANSRMOT_SCORES_ROOT",
    "/home/seanachan/RMOT/exps/off150_scores/results_epoch99")
FRAME_DIR   = os.environ.get("GMC_FRAME_DIR", "/home/seanachan/data/Dataset/refer-kitti/KITTI/training/image_02")
GMC_WEIGHTS = os.environ.get("GMC_WEIGHTS", "gmc_link_weights_v1train_sw12d_groad_seed0.pth")
GMC_SUFFIX  = os.environ.get("GMC_SUFFIX", "_sw12d_groad_seed0_warm11")
DEVICE      = "cuda" if torch.cuda.is_available() else "cpu"
T_MIN       = 11  # warm-up abstention: keep iff contiguous history >= 11 (> max FRAME_GAPS)


def load_stream(scores_path):
    """scores.txt -> {frame_id: [(oid, x, y, w, h), ...]} (xywh)."""
    stream = defaultdict(list)
    with open(scores_path) as f:
        for line in f:
            p = line.strip().split(",")
            if len(p) != 9:
                continue
            fid, oid = int(p[0]), int(p[1])
            x1, y1, x2, y2 = float(p[2]), float(p[3]), float(p[4]), float(p[5])
            stream[fid].append((oid, x1, y1, x2 - x1, y2 - y1))
    return stream


def build(seq):
    cache_path = f"gmc_link/gmc_scores_transrmot_{seq}{GMC_SUFFIX}_cache.json"
    if os.path.exists(cache_path):
        print(f"[gmc] cache exists → {cache_path}, skip")
        return
    seq_root = os.path.join(SCORES_ROOT, seq)
    expressions = sorted(d for d in os.listdir(seq_root)
                         if os.path.isfile(os.path.join(seq_root, d, "scores.txt")))
    print(f"[gmc] {seq}: {len(expressions)} exprs → {cache_path}")

    encoder = TextEncoder(model_name="all-MiniLM-L6-v2", device=DEVICE)
    seq_frame_dir = os.path.join(FRAME_DIR, seq)
    frame_files = sorted(f for f in os.listdir(seq_frame_dir) if f.endswith((".png", ".jpg")))
    total_frames = len(frame_files)

    cache = {}
    for expression in tqdm(expressions, desc=f"gmc-transrmot-{seq}"):
        stream = load_stream(os.path.join(seq_root, expression, "scores.txt"))
        text_emb = encoder.encode(expression.replace("-", " ")).to(DEVICE)
        linker = GMCLinkManager(weights_path=GMC_WEIGHTS, device=DEVICE)
        per_expr = {}
        T = {}  # warm-up replay: consecutive presence in processed frames
        for f0 in range(total_frames):
            f1 = f0 + 1
            dets = stream.get(f1, [])
            if not dets:
                continue
            frame_img = cv2.imread(os.path.join(seq_frame_dir, frame_files[f0]))
            if frame_img is None:
                continue
            active = [DummyTrack(oid, x, y, w, h) for oid, x, y, w, h in dets]
            det_arr = np.array([[x, y, x + w, y + h] for _, x, y, w, h in dets])
            scores, _, _ = linker.process_frame(
                frame_img, active, text_emb, detections=det_arr,
                raw_cos=True, seq=seq, frame_id=f1)
            oids = {oid for oid, *_ in dets}
            T = {o: T.get(o, 0) + 1 for o in oids}  # absent oids dropped = reset
            for oid, g in scores.items():
                if T.get(int(oid), 0) >= T_MIN:
                    per_expr.setdefault(str(f1), {})[str(oid)] = float(g)
        cache[expression] = per_expr

    kept = sum(len(o) for e in cache.values() for o in e.values())
    json.dump(cache, open(cache_path, "w"))
    print(f"[gmc] cached → {cache_path}  entries={kept}")


if __name__ == "__main__":
    seqs = sys.argv[1:] if len(sys.argv) > 1 else ["0005", "0011", "0013"]
    for s in seqs:
        build(s)
