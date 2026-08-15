"""Instrument the GMC_HGATE degenerate-H gate (audit A9 / task S1-C1).

Replays every consecutive-frame transition on the iKUN eval seqs with real
NeuralSORT foreground masks, computes H (no gate), and reports which
transitions the gate WOULD reject. Pass criterion: rejects only the wild
tail (~7/916 measured in the audit; legit ego p95 = 50-99px vs 150px bound),
zero fallback firings.
"""
import os, sys
import numpy as np, cv2
sys.path.insert(0, "/home/seanachan/GMC-Link")
from gmc_link.core import ORBHomographyEngine
from gmc_link.utils import warp_points
from run_ikun_linear_additive import merged_ns

IMG = "/home/seanachan/GMC-Link/refer-kitti/KITTI/training/image_02/{seq}/{fid:06d}.png"
SEQS = ["0005", "0011", "0013"]

eng = ORBHomographyEngine()
total = rejects = 0
disps = []
for seq in SEQS:
    ns = merged_ns(seq)
    fids = sorted(ns.keys())
    seq_rej = 0
    for i in range(len(fids) - 1):
        f0, f1 = fids[i], fids[i + 1]
        p0, p1 = IMG.format(seq=seq, fid=f0), IMG.format(seq=seq, fid=f1)
        if not (os.path.exists(p0) and os.path.exists(p1)):
            continue
        img0, img1 = cv2.imread(p0), cv2.imread(p1)
        boxes = [(x, y, x + w, y + h) for _, x, y, w, h in ns[f0]]
        H, _ = eng.estimate_homography(img0, img1, prev_bboxes=boxes)
        total += 1
        h, w = img0.shape[:2]
        corners = np.array([[0, 0], [w, 0], [0, h], [w, h]], dtype=np.float32)
        d = float(np.linalg.norm(warp_points(corners, H) - corners, axis=1).max())
        disps.append(d)
        if eng._h_is_degenerate(H, img0.shape):
            rejects += 1
            seq_rej += 1
            print(f"REJECT {seq} {f0}->{f1}: corner_disp={d:.0f}px "
                  f"|h31|={abs(H[2,0]):.2e} |h32|={abs(H[2,1]):.2e}")
    print(f"{seq}: rejects={seq_rej}")

disps = np.array(disps)
print(f"\ntotal={total} rejects={rejects} ({rejects/total:.2%})")
print(f"disp p50={np.percentile(disps,50):.0f} p95={np.percentile(disps,95):.0f} "
      f"p99={np.percentile(disps,99):.0f} max={disps.max():.0f}px")
print(f"fallback firings during replay: {eng.fallback_reuses} (want 0)")
