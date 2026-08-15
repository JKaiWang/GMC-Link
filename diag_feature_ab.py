"""Detector A/B for ego-motion homography quality (ORB vs AKAZE vs BRISK vs SIFT).

Same pipeline (BFMatcher + Lowe 0.7 + RANSAC 5px homography), only the
detector/descriptor changes (GMC_FEAT). Replays all consecutive-frame
transitions on the iKUN eval seqs with real NeuralSORT masks. CPU-only
screen — the winner (if any) still needs the full HOTA protocol; this only
measures homography-side quality:
  wild-H tail (corner disp > 150px), disp percentiles, median bg_residual
  (inlier warp error = H accuracy proxy), keypoint/match counts, ms/frame.
"""
import os
import sys
import time

import cv2
import numpy as np

sys.path.insert(0, "/home/seanachan/GMC-Link")
from gmc_link.utils import warp_points
from run_ikun_linear_additive import merged_ns

IMG = "/home/seanachan/GMC-Link/refer-kitti/KITTI/training/image_02/{seq}/{fid:06d}.png"
SEQS = ["0005", "0011", "0013"]
DETECTORS = ["orb", "akaze", "brisk", "sift"]

# preload frames + masks once
transitions = []
for seq in SEQS:
    ns = merged_ns(seq)
    fids = sorted(ns.keys())
    for i in range(len(fids) - 1):
        p0, p1 = IMG.format(seq=seq, fid=fids[i]), IMG.format(seq=seq, fid=fids[i + 1])
        if os.path.exists(p0) and os.path.exists(p1):
            boxes = [(x, y, x + w, y + h) for _, x, y, w, h in ns[fids[i]]]
            transitions.append((seq, fids[i], p0, p1, boxes))
print(f"{len(transitions)} transitions")

for det in DETECTORS:
    os.environ["GMC_FEAT"] = det
    import importlib

    from gmc_link import core
    importlib.reload(core)
    eng = core.ORBHomographyEngine()
    disps, residuals, ninliers, times = [], [], [], []
    wild = 0
    for seq, f0, p0, p1, boxes in transitions:
        img0, img1 = cv2.imread(p0), cv2.imread(p1)
        t0 = time.perf_counter()
        H, bg_res = eng.estimate_homography(img0, img1, prev_bboxes=boxes)
        times.append((time.perf_counter() - t0) * 1000)
        h, w = img0.shape[:2]
        corners = np.array([[0, 0], [w, 0], [0, h], [w, h]], dtype=np.float32)
        d = float(np.linalg.norm(warp_points(corners, H) - corners, axis=1).max())
        disps.append(d)
        residuals.append(float(np.linalg.norm(bg_res)))
        if d > 150.0:
            wild += 1
    disps, residuals, times = map(np.array, (disps, residuals, times))
    print(f"{det:>6}: wild(>150px)={wild:>2}  disp p50={np.percentile(disps,50):5.1f} "
          f"p95={np.percentile(disps,95):5.1f} p99={np.percentile(disps,99):6.1f} max={disps.max():7.1f}  "
          f"bg_residual p50={np.percentile(residuals,50):.3f}px  "
          f"ms/frame p50={np.percentile(times,50):5.1f} p95={np.percentile(times,95):6.1f}",
          flush=True)
