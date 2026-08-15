"""T-probe round 2: coordinate-frame comparison (docs/TPROBE_PLAN.md addendum).

Four representation arms, same probe protocol as round 1:
  raw    — image-plane gap-1 velocity, NO ego compensation ("Image" arm;
           round-1 never measured this — round-1 inst8 was already compensated)
  gmc    — global-similarity-compensated residual (round-1 arm, re-extracted)
  ground — bbox bottom-center residual via road-plane LK chain ("World-ish" arm)
  rel    — gmc velocity minus per-frame median neighbor gmc velocity (relational)

Plus per-sample mean |ego rotation| over the window (from the similarity step
transforms) for the turning x ego-rotation stratification.

Run:  GMC_MODEL=similarity python diagnostics/tprobe2.py [--probe-only]
"""
import argparse, glob, json, os, sys
from collections import defaultdict

import numpy as np
import cv2

sys.path.insert(0, "/home/seanachan/GMC-Link")
os.environ.setdefault("GMC_MODEL", "similarity")
from gmc_link.core import ORBHomographyEngine
from gmc_link.utils import warp_points

REPO = "/home/seanachan/GMC-Link"
DATA = os.path.join(REPO, "refer-kitti")
IMG_DIR = os.path.join(DATA, "KITTI", "training", "image_02")
LBL_DIR = os.path.join(DATA, "KITTI", "labels_with_ids", "image_02")
EXPR_DIR = os.path.join(DATA, "expression")
OUT_DIR = os.path.join(REPO, "results", "tprobe")

TRAIN_SEQS = ["0001", "0002", "0003", "0004", "0006", "0007", "0008", "0009",
              "0010", "0012", "0014", "0015", "0016", "0018", "0020"]
PROBE_TEST_SEQS = {"0001", "0006", "0010", "0016"}
TMAX = 16
VSCALE = 100.0

KW = {
    "moving": ("moving", "in motion"),
    "static": ("parking", "parked", "stopped", "stationary", "static"),
    "turning": ("turning",),
    "counter": ("counter direction",),
}


def load_gt_tracks(seq, W, H):
    tracks = defaultdict(dict)
    for f in glob.glob(os.path.join(LBL_DIR, seq, "*.txt")):
        fid = int(os.path.splitext(os.path.basename(f))[0])
        for line in open(f):
            p = line.split()
            if len(p) < 6:
                continue
            tid = int(p[1])
            tracks[tid][fid] = (float(p[2]) * W, float(p[3]) * H,
                                float(p[4]) * W, float(p[5]) * H)
    return tracks


def expression_track_labels(seq):
    groups = defaultdict(set)
    for p in glob.glob(os.path.join(EXPR_DIR, seq, "*.json")):
        d = json.load(open(p))
        sent = (d.get("sentence") or "").lower()
        tids = set()
        for _, ids in (d.get("label") or {}).items():
            tids.update(int(i) for i in ids)
        for g, kws in KW.items():
            if any(k in sent for k in kws):
                for t in tids:
                    groups[t].add(g)
    return groups


def chains(seq, tracks, n_frames):
    """Per-frame global-similarity step H + road-plane step H + ego rotation."""
    eng = ORBHomographyEngine()
    boxes = defaultdict(list)
    for tid, tr in tracks.items():
        for fid, (cx, cy, w, h) in tr.items():
            boxes[fid].append((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
    g_steps, r_steps, rot = {}, {}, {}
    prev = None
    for fid in range(n_frames):
        img = cv2.imread(os.path.join(IMG_DIR, seq, f"{fid:06d}.png"))
        if img is None:
            prev = None
            continue
        if prev is not None:
            pf, pi = prev
            Hg, _ = eng.estimate_homography(pi, img, boxes.get(pf) or None)
            Hr = eng.estimate_road_homography(pi, img, boxes.get(pf) or None)
            g_steps[pf] = Hg
            r_steps[pf] = Hr if Hr is not None else Hg
            rot[pf] = float(np.degrees(np.arctan2(Hg[1, 0], Hg[0, 0])))
        prev = (fid, img)
    return g_steps, r_steps, rot


def res_gap1(tr, steps, fid, W, H, bottom=False):
    if fid - 1 not in tr or fid not in tr:
        return None
    Hs = steps.get(fid - 1)
    if Hs is None:
        return None
    def pt(f):
        cx, cy, w, h = tr[f]
        return np.array([cx, cy + h / 2.0] if bottom else [cx, cy], np.float32)
    c0, c1 = pt(fid - 1), pt(fid)
    ego = warp_points(c0[None], Hs)[0] - c0
    r = (c1 - c0) - ego
    return np.array([r[0] / W * VSCALE, r[1] / H * VSCALE], np.float32)


def raw_gap1(tr, fid, W, H):
    if fid - 1 not in tr or fid not in tr:
        return None
    c0 = np.array(tr[fid - 1][:2], np.float32)
    c1 = np.array(tr[fid][:2], np.float32)
    r = c1 - c0
    return np.array([r[0] / W * VSCALE, r[1] / H * VSCALE], np.float32)


def extract_seq(seq):
    img0 = cv2.imread(os.path.join(IMG_DIR, seq, "000000.png"))
    Hh, Ww = img0.shape[:2]
    tracks = load_gt_tracks(seq, Ww, Hh)
    n_frames = 1 + max(max(tr) for tr in tracks.values())
    g_steps, r_steps, rot = chains(seq, tracks, n_frames)
    egroups = expression_track_labels(seq)

    feats = {a: defaultdict(dict) for a in ("raw", "gmc", "gnd")}
    for tid, tr in tracks.items():
        for fid in sorted(tr):
            box = tr[fid]
            state = [box[0] / Ww, box[1] / Hh, box[2] / Ww, box[3] / Hh]
            dwh = None
            if fid - 1 in tr:
                dwh = [(box[2] - tr[fid - 1][2]) / Ww * VSCALE,
                       (box[3] - tr[fid - 1][3]) / Hh * VSCALE]
            for arm, fn in (("raw", lambda: raw_gap1(tr, fid, Ww, Hh)),
                            ("gmc", lambda: res_gap1(tr, g_steps, fid, Ww, Hh)),
                            ("gnd", lambda: res_gap1(tr, r_steps, fid, Ww, Hh, bottom=True))):
                v = fn()
                if v is not None and dwh is not None:
                    feats[arm][tid][fid] = np.array(
                        list(v) + dwh + state, np.float32)

    frame_v = defaultdict(dict)
    for tid, d in feats["gmc"].items():
        for fid, f in d.items():
            frame_v[fid][tid] = f[:2]

    samples = []
    for tid, tr in tracks.items():
        for fid in sorted(tr):
            hist = [fid - k for k in range(TMAX - 1, -1, -1)]
            if not all(all(f in feats[a].get(tid, {}) for f in hist)
                       for a in ("raw", "gmc", "gnd")):
                continue
            X = {a: np.stack([feats[a][tid][f] for f in hist])
                 for a in ("raw", "gmc", "gnd")}
            # relational arm: gmc velocities minus per-frame median neighbor
            rel = X["gmc"].copy()
            for i, f in enumerate(hist):
                nb = [v for t2, v in frame_v.get(f, {}).items() if t2 != tid]
                if nb:
                    rel[i, :2] = rel[i, :2] - np.median(nb, axis=0)
            X["rel"] = rel
            ego_rot = float(np.mean([abs(rot.get(f - 1, 0.0)) for f in hist]))
            eg = egroups.get(tid, set())
            samples.append(dict(
                seq=seq, tid=tid, fid=fid, X=X, ego_rot=ego_rot,
                e_moving="moving" in eg, e_static="static" in eg,
                e_turning="turning" in eg, e_counter="counter" in eg))
    return samples


def probe_all(samples):
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import f1_score

    tr_idx = [i for i, s in enumerate(samples) if s["seq"] not in PROBE_TEST_SEQS]
    te_idx = [i for i, s in enumerate(samples) if s["seq"] in PROBE_TEST_SEQS]

    def labels(task):
        if task == "moving_vs_static":
            m = np.array([(s["e_moving"] != s["e_static"]) and
                          (s["e_moving"] or s["e_static"]) for s in samples])
            y = np.array([s["e_moving"] for s in samples])
        else:
            y = np.array([s["e_" + task] for s in samples])
            m = np.ones(len(samples), bool)
        return y.astype(int), m

    def run(X, y, tr, te):
        if len(set(y[tr])) < 2 or len(set(y[te])) < 2 or len(te) < 30:
            return None
        sc = StandardScaler().fit(X[tr])
        clf = LogisticRegression(max_iter=2000, class_weight="balanced",
                                 random_state=0).fit(sc.transform(X[tr]), y[tr])
        return round(float(f1_score(y[te], clf.predict(sc.transform(X[te])),
                                    average="macro")), 4)

    arms = ("raw", "gmc", "gnd", "rel")
    Xf = {a: np.stack([s["X"][a] for s in samples]).reshape(len(samples), -1)
          for a in arms}
    results = {}
    for task in ("moving_vs_static", "turning", "counter"):
        y, m = labels(task)
        tr = [i for i in tr_idx if m[i]]
        te = [i for i in te_idx if m[i]]
        results[task] = {a: run(Xf[a], y, tr, te) for a in arms}
        print(task, json.dumps(results[task]), flush=True)

    # turning x ego-rotation stratification (quartiles over the valid test set)
    y, m = labels("turning")
    rotv = np.array([s["ego_rot"] for s in samples])
    qs = np.percentile(rotv[te_idx], [25, 50, 75])
    strat = {}
    for name, lo, hi in (("q1_stable", -1, qs[0]), ("q2", qs[0], qs[1]),
                         ("q3", qs[1], qs[2]), ("q4_rotating", qs[2], 1e9)):
        te_s = [i for i in te_idx if m[i] and lo < rotv[i] <= hi]
        tr_s = [i for i in tr_idx if m[i]]
        strat[name] = {a: run(Xf[a], y, tr_s, te_s) for a in ("gmc", "gnd")}
    results["turning_by_ego_rotation"] = {
        "quartile_bounds_deg": [round(float(q), 4) for q in qs], **strat}
    print("turning_by_ego_rotation", json.dumps(results["turning_by_ego_rotation"]),
          flush=True)

    with open(os.path.join(OUT_DIR, "tprobe2_results.json"), "w") as f:
        json.dump(results, f, indent=2)
    print(f"saved -> {OUT_DIR}/tprobe2_results.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe-only", action="store_true")
    args = ap.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, "samples2.npy")
    if args.probe_only:
        samples = list(np.load(path, allow_pickle=True))
    else:
        samples = []
        for seq in TRAIN_SEQS:
            s = extract_seq(seq)
            print(f"{seq}: {len(s)} samples", flush=True)
            samples.extend(s)
        np.save(path, np.array(samples, dtype=object), allow_pickle=True)
    probe_all(samples)


if __name__ == "__main__":
    main()
