"""FPS profile (recreated 2026-08-16; original lost — memory project_paper_fps_fix).
Per-frame wall-time on a real sequence for: ORB global-chain step, road-chain
step, 12D feature compute + aligner forward (via GMCLinkManager.process_frame).
Reports ms/frame breakdown + end-to-end FPS for sim and road chains.

Usage: GMC_MODEL=similarity python profile_inference.py [--seq 0011] [--n 200]
Writes results/fps_profile.json.
"""
import argparse, json, os, time
import cv2
import numpy as np
import torch

REPO = "/home/seanachan/GMC-Link"
IMG_DIR = os.path.join(REPO, "refer-kitti", "KITTI", "training", "image_02")


class _Trk:
    def __init__(self, tid, cx, cy, w, h):
        self.id = tid
        self.centroid = (cx, cy)
        self.bbox = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


def load_tracks(seq):
    from run_ikun_linear_additive import merged_ns
    return merged_ns(seq)


def profile(mode, seq, n, weights):
    # mode: "sim" (global similarity chain) or "road" (GMC_GROUND_MODE=road)
    os.environ["GMC_MODEL"] = "similarity"
    os.environ["GMC_MOTION_EMA"] = "0"
    if mode == "road":
        os.environ["GMC_GROUND_MODE"] = "road"
    else:
        os.environ.pop("GMC_GROUND_MODE", None)
    import importlib
    import gmc_link.manager as M
    importlib.reload(M)
    mgr = M.GMCLinkManager(weights_path=weights)
    ns = load_tracks(seq)
    lang = torch.zeros(384)
    frames = sorted(f for f in os.listdir(os.path.join(IMG_DIR, seq))
                    if f.endswith(".png"))[:n]
    t_total, t_frames = 0.0, 0
    t0_all = time.perf_counter()
    for fname in frames:
        fid = int(fname.split(".")[0])
        img = cv2.imread(os.path.join(IMG_DIR, seq, fname))
        dets = ns.get(fid, [])
        tracks = [_Trk(oid, x + w / 2, y + h / 2, w, h) for oid, x, y, w, h in dets]
        boxes = np.array([t.bbox for t in tracks]) if tracks else None
        t0 = time.perf_counter()
        mgr.process_frame(img, tracks, lang, detections=boxes)
        t_total += time.perf_counter() - t0
        t_frames += 1
    wall = time.perf_counter() - t0_all
    return {
        "mode": mode, "seq": seq, "frames": t_frames,
        "ms_per_frame_process": round(1000 * t_total / t_frames, 2),
        "fps_process_only": round(t_frames / t_total, 1),
        "ms_per_frame_incl_io": round(1000 * wall / t_frames, 2),
        "fps_incl_io": round(t_frames / wall, 1),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seq", default="0011")
    p.add_argument("--n", type=int, default=200)
    p.add_argument("--weights", default="gmc_link_weights_v1train_sw12d_seed0.pth")
    args = p.parse_args()
    out = [profile(m, args.seq, args.n, args.weights) for m in ("sim", "road")]
    for r in out:
        print(r, flush=True)
    os.makedirs(os.path.join(REPO, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(REPO, "results", "fps_profile.json"), "w"), indent=1)
    print("FPS_PROFILE_DONE")


if __name__ == "__main__":
    main()
