"""T-probe round 3: ORACLE 3D/world-frame features (experiment 4 of the
coordinate-frame plan). Decisive test: can GROUND-TRUTH 3D motion (KITTI
tracking label_02: camera-frame X,Z + rotation_y; oxts: ego yaw) separate the
turning / moving / counter EXPRESSION labels that image-plane features cannot?

- turning separable here  -> information lives in 3D/world frame; estimator
  direction confirmed (Hypothesis B), road-H approximation was just too weak.
- turning still ~chance   -> label/semantic-level problem; motion
  representation exonerated entirely.

tid mapping: Refer-KITTI labels_with_ids ids != KITTI tracking ids; built per
sequence by per-frame IoU matching (>0.5) + majority vote.

Run: python diagnostics/tprobe3_oracle.py
"""
import glob, json, os, sys
from collections import defaultdict, Counter

import numpy as np
import cv2

sys.path.insert(0, "/home/seanachan/GMC-Link")

REPO = "/home/seanachan/GMC-Link"
DATA = os.path.join(REPO, "refer-kitti")
IMG_DIR = os.path.join(DATA, "KITTI", "training", "image_02")
LBL_DIR = os.path.join(DATA, "KITTI", "labels_with_ids", "image_02")
EXPR_DIR = os.path.join(DATA, "expression")
KT_DIR = "/home/seanachan/data/kitti_tracking/training/label_02"
OXTS_DIR = "/home/seanachan/data/kitti_tracking/training/oxts"
OUT_DIR = os.path.join(REPO, "results", "tprobe")

TRAIN_SEQS = ["0001", "0002", "0003", "0004", "0006", "0007", "0008", "0009",
              "0010", "0012", "0014", "0015", "0016", "0018", "0020"]
PROBE_TEST_SEQS = {"0001", "0006", "0010", "0016"}
TMAX = 16

KW = {
    "moving": ("moving", "in motion"),
    "static": ("parking", "parked", "stopped", "stationary", "static"),
    "turning": ("turning",),
    "counter": ("counter direction",),
}


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


def iou(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    if x2 <= x1 or y2 <= y1:
        return 0.0
    inter = (x2 - x1) * (y2 - y1)
    ar = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ar


def build_seq(seq):
    img0 = cv2.imread(os.path.join(IMG_DIR, seq, "000000.png"))
    H, W = img0.shape[:2]
    # KITTI 3D: frame -> ktid -> (bbox, X, Z, roty)
    k3d = defaultdict(dict)
    for line in open(os.path.join(KT_DIR, f"{seq}.txt")):
        p = line.split()
        if p[2] == "DontCare":
            continue
        k3d[int(p[0])][int(p[1])] = (
            (float(p[6]), float(p[7]), float(p[8]), float(p[9])),
            float(p[13]), float(p[15]), float(p[16]))
    # Refer boxes: frame -> rtid -> bbox
    rbox = defaultdict(dict)
    for f in glob.glob(os.path.join(LBL_DIR, seq, "*.txt")):
        fid = int(os.path.splitext(os.path.basename(f))[0])
        for line in open(f):
            p = line.split()
            cx, cy, w, h = (float(p[2]) * W, float(p[3]) * H,
                            float(p[4]) * W, float(p[5]) * H)
            rbox[fid][int(p[1])] = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    # rtid -> ktid via per-frame CENTER-DISTANCE majority vote (Refer-KITTI
    # boxes are independently re-annotated with a ~11px systematic offset vs
    # KITTI — IoU collapses on small boxes; center distance is robust).
    votes = defaultdict(Counter)
    for fid, rd in rbox.items():
        kd = k3d.get(fid, {})
        for rt, rb in rd.items():
            rc = ((rb[0] + rb[2]) / 2, (rb[1] + rb[3]) / 2)
            rsz = max(rb[2] - rb[0], rb[3] - rb[1])
            best, bd = None, max(18.0, 0.8 * rsz)
            for kt, (kb, *_) in kd.items():
                kc = ((kb[0] + kb[2]) / 2, (kb[1] + kb[3]) / 2)
                d = ((rc[0] - kc[0]) ** 2 + (rc[1] - kc[1]) ** 2) ** 0.5
                if d < bd:
                    best, bd = kt, d
            if best is not None:
                votes[rt][best] += 1
    mapping = {rt: c.most_common(1)[0][0] for rt, c in votes.items()
               if c and c.most_common(1)[0][1] >= 5}
    # ego yaw per frame
    yaw = {}
    op = os.path.join(OXTS_DIR, f"{seq}.txt")
    if os.path.exists(op):
        for i, line in enumerate(open(op)):
            yaw[i] = float(line.split()[5])
    return k3d, mapping, yaw


def extract():
    samples = []
    for seq in TRAIN_SEQS:
        k3d, mapping, yaw = build_seq(seq)
        egroups = expression_track_labels(seq)
        # ktid -> {fid: (X, Z, roty)}
        ktr = defaultdict(dict)
        for fid, d in k3d.items():
            for kt, (_, X, Z, roty) in d.items():
                ktr[kt][fid] = (X, Z, roty)
        n = 0
        for rt, kt in mapping.items():
            tr = ktr.get(kt, {})
            eg = egroups.get(rt, set())
            for fid in sorted(tr):
                hist = [fid - k for k in range(TMAX - 1, -1, -1)]
                if not all(f in tr and f in yaw for f in hist):
                    continue
                rows = []
                for f in hist:
                    X, Z, roty = tr[f]
                    ey = yaw[f]
                    if f - 1 in tr:
                        Xp, Zp, rotyp = tr[f - 1]
                        vX, vZ = X - Xp, Z - Zp
                        droty = np.arctan2(np.sin(roty - rotyp), np.cos(roty - rotyp))
                        deyaw = np.arctan2(np.sin(ey - yaw[f - 1]), np.cos(ey - yaw[f - 1]))
                    else:
                        vX = vZ = droty = deyaw = 0.0
                    world_head = roty + ey
                    rows.append([X / 30.0, Z / 30.0, vX, vZ,
                                 np.sin(roty), np.cos(roty),
                                 np.sin(world_head), np.cos(world_head),
                                 droty * 57.3, (droty + deyaw) * 57.3,
                                 deyaw * 57.3])
                samples.append(dict(
                    seq=seq, X=np.array(rows, np.float32),
                    e_moving="moving" in eg, e_static="static" in eg,
                    e_turning="turning" in eg, e_counter="counter" in eg))
                n += 1
        print(f"{seq}: {n} oracle samples (mapped {len(mapping)} tracks)", flush=True)
    return samples


def probe(samples):
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import f1_score

    tr_idx = [i for i, s in enumerate(samples) if s["seq"] not in PROBE_TEST_SEQS]
    te_idx = [i for i, s in enumerate(samples) if s["seq"] in PROBE_TEST_SEQS]
    Xf = np.stack([s["X"] for s in samples]).reshape(len(samples), -1)

    def labels(task):
        if task == "moving_vs_static":
            m = np.array([(s["e_moving"] != s["e_static"]) and
                          (s["e_moving"] or s["e_static"]) for s in samples])
            y = np.array([s["e_moving"] for s in samples])
        else:
            y = np.array([s["e_" + task] for s in samples])
            m = np.ones(len(samples), bool)
        return y.astype(int), m

    results = {}
    for task in ("moving_vs_static", "turning", "counter"):
        y, m = labels(task)
        tr = [i for i in tr_idx if m[i]]
        te = [i for i in te_idx if m[i]]
        if len(set(y[tr])) < 2 or len(set(y[te])) < 2:
            results[task] = None
            continue
        sc = StandardScaler().fit(Xf[tr])
        clf = LogisticRegression(max_iter=2000, class_weight="balanced",
                                 random_state=0).fit(sc.transform(Xf[tr]), y[tr])
        f1 = float(f1_score(y[te], clf.predict(sc.transform(Xf[te])), average="macro"))
        results[task] = dict(macro_f1=round(f1, 4), n_te=len(te), pos=int(y[te].sum()))
        print(task, results[task], flush=True)

    with open(os.path.join(OUT_DIR, "tprobe3_oracle_results.json"), "w") as f:
        json.dump(results, f, indent=2)
    print(f"saved -> {OUT_DIR}/tprobe3_oracle_results.json")


if __name__ == "__main__":
    probe(extract())
