"""T-probe: trajectory-history information diagnosis (docs/TPROBE_PLAN.md).

Stage 1: extract per-(track, frame) samples from GT trajectories on V1 TRAIN
seqs — instantaneous 8D + ship-style 12D features, kinematic + expression
labels, contiguous history >= 16 and future >= 5 (identical sample set for
every T). Stage 2: logistic-regression probes over T in {1,2,4,8,16} with
mean-pool and flatten readouts, shuffle test at T=16, future-displacement
ridge probe.

Run:  GMC_MODEL=similarity python diagnostics/tprobe.py [--extract-only]
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
PROBE_TEST_SEQS = {"0001", "0006", "0010", "0016"}  # every 4th, pre-registered
TMAX, FUT, TS = 16, 5, [1, 2, 4, 8, 16]
VSCALE = 100.0

# Pre-registered kinematic thresholds (px/frame in residual space; deg/frame)
TAU_V, TAU_TURN_DEG, TAU_BRAKE = 0.8, 4.0, 0.30

# Expression keyword groups (V1 canonical sentences)
KW = {
    "moving": ("moving", "in motion"),
    "static": ("parking", "parked", "stopped", "stationary", "static"),
    "turning": ("turning",),
    "braking": ("braking",),
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
            cx, cy, w, h = (float(p[2]) * W, float(p[3]) * H,
                            float(p[4]) * W, float(p[5]) * H)
            tracks[tid][fid] = (cx, cy, w, h)
    return tracks


def expression_track_labels(seq):
    """tid -> set of keyword groups from V1 expressions covering that tid."""
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


def step_chains(seq, tracks, n_frames, W, H):
    """Composed similarity ego chain: returns list H_step[i] = H(frame i -> i+1)."""
    eng = ORBHomographyEngine()
    frames_boxes = defaultdict(list)
    for tid, tr in tracks.items():
        for fid, (cx, cy, w, h) in tr.items():
            frames_boxes[fid].append((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
    steps = {}
    prev = None
    for fid in range(n_frames):
        path = os.path.join(IMG_DIR, seq, f"{fid:06d}.png")
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            prev = None
            continue
        if prev is not None:
            pf, pi = prev
            H_s, _ = eng.estimate_homography(pi, img, frames_boxes.get(pf) or None)
            steps[pf] = H_s
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


def residual(tr, steps, fid, gap, W, H):
    """Residual displacement of centroid over [fid-gap, fid], normalized*100."""
    if fid - gap not in tr or fid not in tr:
        return None
    Hc = compose(steps, fid - gap, fid)
    if Hc is None:
        return None
    c0 = np.array(tr[fid - gap][:2], dtype=np.float32)
    c1 = np.array(tr[fid][:2], dtype=np.float32)
    ego = warp_points(c0[None], Hc)[0] - c0
    raw = c1 - c0
    res = raw - ego
    return np.array([res[0] / W * VSCALE, res[1] / H * VSCALE], dtype=np.float32)


def extract_seq(seq):
    img0 = cv2.imread(os.path.join(IMG_DIR, seq, "000000.png"))
    H_img, W_img = img0.shape[:2]
    tracks = load_gt_tracks(seq, W_img, H_img)
    n_frames = 1 + max(max(tr) for tr in tracks.values())
    steps = step_chains(seq, tracks, n_frames, W_img, H_img)
    egroups = expression_track_labels(seq)

    # per-frame inst8 features per track (need contiguous presence)
    inst8, ship12 = defaultdict(dict), defaultdict(dict)
    for tid, tr in tracks.items():
        for fid in sorted(tr):
            if fid - 1 in tr:
                r1 = residual(tr, steps, fid, 1, W_img, H_img)
                if r1 is None:
                    continue
                _, _, w0, h0 = tr[fid - 1]
                cx, cy, w, h = tr[fid]
                dw1 = (w - w0) / W_img * VSCALE
                dh1 = (h - h0) / H_img * VSCALE
                inst8[tid][fid] = np.array(
                    [r1[0], r1[1], dw1, dh1, cx / W_img, cy / H_img,
                     w / W_img, h / H_img], dtype=np.float32)
            # ship-style 12D (gaps 2/5/10)
            vs = []
            okall = True
            for g in (2, 5, 10):
                r = residual(tr, steps, fid, g, W_img, H_img) if fid - g in tr else None
                if r is None:
                    okall = False
                    break
                vs.extend([r[0], r[1]])
            if okall and fid - 5 in tr:
                cx, cy, w, h = tr[fid]
                w5, h5 = tr[fid - 5][2], tr[fid - 5][3]
                ship12[tid][fid] = np.array(
                    vs + [(w - w5) / W_img * VSCALE, (h - h5) / H_img * VSCALE,
                          cx / W_img, cy / H_img, w / W_img, h / H_img],
                    dtype=np.float32)

    # neighbor mean heading per frame (for kinematic counter-direction)
    frame_vels = defaultdict(dict)
    for tid, feats in inst8.items():
        for fid, f in feats.items():
            frame_vels[fid][tid] = f[:2]

    samples = []
    for tid, tr in tracks.items():
        fids = sorted(tr)
        for fid in fids:
            hist = [fid - k for k in range(TMAX - 1, -1, -1)]
            if not all(f in inst8.get(tid, {}) for f in hist):
                continue
            if fid + FUT not in tr or fid not in ship12.get(tid, {}):
                continue
            X = np.stack([inst8[tid][f] for f in hist])          # (16, 8)
            x12 = ship12[tid][fid]                               # (12,)
            # kinematic labels over recent window
            v_win = X[-5:, :2]
            speed = float(np.linalg.norm(v_win.mean(axis=0)))
            k_moving = speed > TAU_V
            thetas = np.arctan2(X[:, 1], X[:, 0])
            sp = np.linalg.norm(X[:, :2], axis=1)
            mask8 = sp[-8:] > TAU_V
            dth = np.abs(np.diff(np.unwrap(thetas[-8:])))
            k_turning = bool(k_moving and mask8[:-1].all()
                             and np.degrees(dth.mean()) > TAU_TURN_DEG)
            sp_first, sp_last = sp[-8:-4].mean(), sp[-4:].mean()
            k_braking = bool(sp_first > TAU_V and sp_last < sp_first * (1 - TAU_BRAKE))
            k_dir_right = bool(X[-5:, 0].mean() > 0)
            # neighbor heading
            nb = [v for t2, v in frame_vels.get(fid, {}).items()
                  if t2 != tid and np.linalg.norm(v) > TAU_V]
            if nb and speed > TAU_V:
                mean_nb = np.mean(nb, axis=0)
                cosang = float(np.dot(v_win.mean(axis=0), mean_nb) /
                               (np.linalg.norm(v_win.mean(axis=0)) * np.linalg.norm(mean_nb) + 1e-9))
                k_counter = cosang < 0.0
                has_nb = True
            else:
                k_counter, has_nb = False, False
            eg = egroups.get(tid, set())
            samples.append(dict(
                seq=seq, tid=tid, fid=fid,
                X=X, x12=x12,
                fut=np.array(tr[fid + FUT][:2], dtype=np.float32) -
                    np.array(tr[fid][:2], dtype=np.float32),
                k_moving=k_moving, k_turning=k_turning, k_braking=k_braking,
                k_dir_right=k_dir_right, k_counter=k_counter, k_has_nb=has_nb,
                e_moving="moving" in eg, e_static="static" in eg,
                e_turning="turning" in eg, e_braking="braking" in eg,
                e_counter="counter" in eg,
            ))
    return samples


def extract_all():
    os.makedirs(OUT_DIR, exist_ok=True)
    all_s = []
    for seq in TRAIN_SEQS:
        s = extract_seq(seq)
        print(f"{seq}: {len(s)} samples", flush=True)
        all_s.extend(s)
    np.save(os.path.join(OUT_DIR, "samples.npy"), np.array(all_s, dtype=object),
            allow_pickle=True)
    return all_s


def probe_all(samples):
    from sklearn.linear_model import LogisticRegression, Ridge
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import f1_score, roc_auc_score

    rng = np.random.RandomState(0)
    perm16 = rng.permutation(TMAX)
    tr_idx = [i for i, s in enumerate(samples) if s["seq"] not in PROBE_TEST_SEQS]
    te_idx = [i for i, s in enumerate(samples) if s["seq"] in PROBE_TEST_SEQS]

    def get_YM(key):
        """labels + validity mask per task."""
        if key == "e_moving_vs_static":
            m = np.array([s["e_moving"] != s["e_static"] and (s["e_moving"] or s["e_static"])
                          for s in samples])
            y = np.array([s["e_moving"] for s in samples])
        elif key == "k_counter":
            m = np.array([s["k_has_nb"] for s in samples])
            y = np.array([s["k_counter"] for s in samples])
        elif key.startswith("e_"):
            y = np.array([s[key] for s in samples]); m = np.ones(len(samples), bool)
        else:
            y = np.array([s[key] for s in samples]); m = np.ones(len(samples), bool)
        return y.astype(int), m

    def run_probe(X, y, tr, te):
        if len(set(y[tr])) < 2 or len(set(y[te])) < 2:
            return None
        sc = StandardScaler().fit(X[tr])
        clf = LogisticRegression(max_iter=2000, class_weight="balanced",
                                 random_state=0).fit(sc.transform(X[tr]), y[tr])
        p = clf.predict(sc.transform(X[te]))
        pr = clf.predict_proba(sc.transform(X[te]))[:, 1]
        return dict(macro_f1=round(float(f1_score(y[te], p, average="macro")), 4),
                    auroc=round(float(roc_auc_score(y[te], pr)), 4),
                    n_te=int(len(te)), pos_te=int(y[te].sum()))

    Xfull = np.stack([s["X"] for s in samples])            # (N, 16, 8)
    X12 = np.stack([s["x12"] for s in samples])            # (N, 12)
    results = {}
    TASKS = ["e_moving_vs_static", "e_turning", "e_braking", "e_counter",
             "k_moving", "k_turning", "k_braking", "k_dir_right", "k_counter"]
    for task in TASKS:
        y, m = get_YM(task)
        tr = [i for i in tr_idx if m[i]]
        te = [i for i in te_idx if m[i]]
        row = {}
        for T in TS:
            win = Xfull[:, TMAX - T:, :]
            row[f"mean_T{T}"] = run_probe(win.mean(axis=1), y, tr, te)
            row[f"flat_T{T}"] = run_probe(win.reshape(len(samples), -1), y, tr, te)
        shuf = Xfull[:, perm16, :].reshape(len(samples), -1)
        row["flat_T16_shuffled"] = run_probe(shuf, y, tr, te)
        row["ship12_T1"] = run_probe(X12, y, tr, te)
        results[task] = row
        f1s = {k: (v["macro_f1"] if v else None) for k, v in row.items()}
        print(task, json.dumps(f1s), flush=True)

    # future displacement (ADE, px) via Ridge on flatten
    fut = np.stack([s["fut"] for s in samples])
    fr = {}
    for T in TS:
        win = Xfull[:, TMAX - T:, :].reshape(len(samples), -1)
        sc = StandardScaler().fit(win[tr_idx])
        r = Ridge(alpha=1.0).fit(sc.transform(win[tr_idx]), fut[tr_idx])
        pred = r.predict(sc.transform(win[te_idx]))
        fr[f"T{T}"] = round(float(np.linalg.norm(pred - fut[te_idx], axis=1).mean()), 3)
    results["future_ade_px"] = fr
    print("future ADE(px):", json.dumps(fr), flush=True)

    with open(os.path.join(OUT_DIR, "tprobe_results.json"), "w") as f:
        json.dump(results, f, indent=2)
    print(f"saved -> {OUT_DIR}/tprobe_results.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract-only", action="store_true")
    ap.add_argument("--probe-only", action="store_true")
    args = ap.parse_args()
    if args.probe_only:
        samples = list(np.load(os.path.join(OUT_DIR, "samples.npy"),
                               allow_pickle=True))
    else:
        samples = extract_all()
    if not args.extract_only:
        probe_all(samples)


if __name__ == "__main__":
    main()
