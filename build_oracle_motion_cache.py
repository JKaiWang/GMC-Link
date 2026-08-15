"""GT-feature oracle cache builder (motion utility test, RESEARCH_NOTES A21).

For each NS detection (fid, tid), find the GT track via center-distance
matching, compute the SHIP-convention 12D from the GT trajectory (similarity
ego chain, gaps 2/5/10, warm11 T>=11 abstention), score with the CURRENT
sw12d aligner -> cache JSON consumable by run_ikun_linear_additive.py.

Answers: if oracle-feature HOTA ~= ship, the motion module is at its practical
ceiling (feature noise is not the residual bottleneck); if >>, tracker-noise
robustness is the remaining lever.

Usage: GMC_MODEL=similarity python build_oracle_motion_cache.py [seed]
Writes gmc_link/gmc_scores_v1_{seq}_sw12d_seed{S}_gtoracle_cache.json
"""
import glob, json, os, sys
from collections import defaultdict

import numpy as np
import cv2
import torch

sys.path.insert(0, "/home/seanachan/GMC-Link")
os.environ.setdefault("GMC_MODEL", "similarity")
from gmc_link.core import ORBHomographyEngine
from gmc_link.utils import warp_points
from gmc_link.demo_inference import load_neuralsort_tracks
from run_ikun_linear_additive import merged_ns

REPO = "/home/seanachan/GMC-Link"
IMG_DIR = os.path.join(REPO, "refer-kitti", "KITTI", "training", "image_02")
LBL_DIR = os.path.join(REPO, "refer-kitti", "KITTI", "labels_with_ids", "image_02")
EXPR_DIR = os.path.join(REPO, "refer-kitti", "expression")
SEQS = ["0005", "0011", "0013"]
GAPS = [2, 5, 10]
VSCALE = 100.0
TMIN = 11  # warm11 abstention on GT history


def load_gt(seq, W, H):
    tracks = defaultdict(dict)
    for f in glob.glob(os.path.join(LBL_DIR, seq, "*.txt")):
        fid = int(os.path.splitext(os.path.basename(f))[0])
        for line in open(f):
            p = line.split()
            tracks[int(p[1])][fid] = (float(p[2]) * W, float(p[3]) * H,
                                      float(p[4]) * W, float(p[5]) * H)
    return tracks


def sim_chains(seq, gt, n_frames):
    eng = ORBHomographyEngine()
    boxes = defaultdict(list)
    for tid, tr in gt.items():
        for fid, (cx, cy, w, h) in tr.items():
            boxes[fid].append((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
    steps = {}
    prev = None
    for fid in range(n_frames):
        img = cv2.imread(os.path.join(IMG_DIR, seq, f"{fid:06d}.png"),
                         cv2.IMREAD_GRAYSCALE)
        if img is None:
            prev = None
            continue
        if prev is not None:
            pf, pi = prev
            Hs, _ = eng.estimate_homography(pi, img, boxes.get(pf) or None)
            steps[pf] = Hs
        prev = (fid, img)
    return steps


def compose(steps, a, b):
    H = np.eye(3, dtype=np.float32)
    for f in range(a, b):
        Hs = steps.get(f)
        if Hs is None:
            return None
        H = Hs @ H
    return H


def gt12d(tr, steps, fid, W, H):
    """Ship-convention 12D from GT trajectory at fid; None if warmup (T<TMIN)."""
    hist = 0
    f = fid
    while f in tr and hist < TMIN:
        hist += 1
        f -= 1
    if hist < TMIN:
        return None
    vs = []
    for g in GAPS:
        if fid - g not in tr:
            return None
        Hc = compose(steps, fid - g, fid)
        if Hc is None:
            return None
        c0 = np.array(tr[fid - g][:2], np.float32)
        c1 = np.array(tr[fid][:2], np.float32)
        ego = warp_points(c0[None], Hc)[0] - c0
        r = (c1 - c0) - ego
        vs.extend([r[0] / W * VSCALE, r[1] / H * VSCALE])
    cx, cy, w, h = tr[fid]
    w5, h5 = tr[fid - 5][2], tr[fid - 5][3]
    return np.array(vs + [(w - w5) / W * VSCALE, (h - h5) / H * VSCALE,
                          cx / W, cy / H, w / W, h / H], np.float32)


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    from gmc_link.manager import GMCLinkManager
    from gmc_link.text_utils import TextEncoder
    mgr = GMCLinkManager(
        weights_path=f"gmc_link_weights_v1train_sw12d_seed{seed}.pth")
    aligner = mgr.aligner
    aligner.eval()
    tenc = TextEncoder(device="cpu")

    for seq in SEQS:
        img0 = cv2.imread(os.path.join(IMG_DIR, seq, "000000.png"))
        Hh, Ww = img0.shape[:2]
        gt = load_gt(seq, Ww, Hh)
        n_frames = 1 + max(max(tr) for tr in gt.values())
        steps = sim_chains(seq, gt, n_frames)
        ns = merged_ns(seq)
        # NS (fid, tid) -> GT tid via per-frame center distance + majority vote
        from collections import Counter
        votes = defaultdict(Counter)
        for fid, dets in ns.items():
            for tid, x, y, w, h in dets:
                c = (x + w / 2, y + h / 2)
                best, bd = None, max(18.0, 0.8 * max(w, h))
                for gtid, tr in gt.items():
                    if fid not in tr:
                        continue
                    gc = tr[fid]
                    d = ((c[0] - gc[0]) ** 2 + (c[1] - gc[1]) ** 2) ** 0.5
                    if d < bd:
                        best, bd = gtid, d
                if best is not None:
                    votes[tid][best] += 1
        ns2gt = {t: c.most_common(1)[0][0] for t, c in votes.items()
                 if c and c.most_common(1)[0][1] >= 5}
        print(f"{seq}: NS->GT mapped {len(ns2gt)} tracks", flush=True)

        # motion embeddings per (fid, ns_tid) from GT trajectories
        keys, vecs = [], []
        for fid, dets in ns.items():
            for tid, *_ in dets:
                gtid = ns2gt.get(tid)
                if gtid is None:
                    continue
                v = gt12d(gt[gtid], steps, fid, Ww, Hh)
                if v is not None:
                    keys.append((fid, tid))
                    vecs.append(v)
        M = torch.tensor(np.stack(vecs))
        exprs = sorted(f[:-5] for f in os.listdir(os.path.join(EXPR_DIR, seq))
                       if f.endswith(".json"))
        sents = [json.load(open(os.path.join(EXPR_DIR, seq, e + ".json")))["sentence"]
                 for e in exprs]
        with torch.no_grad():
            t_raw = tenc.encode(sents, convert_to_tensor=True)
            m_emb, t_embs = aligner.encode(M, t_raw)
        S = (m_emb @ t_embs.T).numpy()  # (N, E)
        cache = {}
        for ei, expr in enumerate(exprs):
            d = {}
            for ki, (fid, tid) in enumerate(keys):
                d.setdefault(str(fid), {})[str(tid)] = float(S[ki, ei])
            cache[expr] = d
        out = os.path.join(REPO, "gmc_link",
                           f"gmc_scores_v1_{seq}_sw12d_seed{seed}_gtoracle_cache.json")
        json.dump(cache, open(out, "w"))
        print(f"{seq}: wrote {len(keys)} scored (fid,tid) x {len(exprs)} exprs -> {out}",
              flush=True)


if __name__ == "__main__":
    main()
