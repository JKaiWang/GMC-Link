"""T-probe round 4: (a) turning x ego-YAW stratification done RIGHT (oxts yaw
rate, not image-plane rotation) on the image-arm samples; (b) oracle-feature
component ablation (position / velocity / heading / delta-heading / full).

Answers: is image-plane turning info destroyed by ego rotation (Hypothesis B
mechanism), and WHICH physical quantity carries the world-frame turning info.

Run: python diagnostics/tprobe4_strat_components.py
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, "/home/seanachan/GMC-Link")
REPO = "/home/seanachan/GMC-Link"
OUT_DIR = os.path.join(REPO, "results", "tprobe")
OXTS_DIR = "/home/seanachan/data/kitti_tracking/training/oxts"
PROBE_TEST_SEQS = {"0001", "0006", "0010", "0016"}
TMAX = 16

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.preprocessing import StandardScaler


def run(X, y, tr, te):
    if len(te) < 30 or len(set(y[tr])) < 2 or len(set(y[te])) < 2:
        return None
    sc = StandardScaler().fit(X[tr])
    clf = LogisticRegression(max_iter=2000, class_weight="balanced",
                             random_state=0).fit(sc.transform(X[tr]), y[tr])
    return round(float(f1_score(y[te], clf.predict(sc.transform(X[te])),
                                average="macro")), 4)


def yaw_rates():
    yr = {}
    for f in os.listdir(OXTS_DIR):
        seq = f[:-4]
        yaws = [float(l.split()[5]) for l in open(os.path.join(OXTS_DIR, f))]
        d = np.abs(np.degrees(np.diff(np.unwrap(yaws))))
        yr[seq] = np.concatenate([[0.0], d])
    return yr


def part_a():
    samples = list(np.load(os.path.join(OUT_DIR, "samples2.npy"),
                           allow_pickle=True))
    yr = yaw_rates()
    win_yaw = []
    for s in samples:
        rates = yr.get(s["seq"])
        fid = s["fid"]
        idx = [max(0, min(len(rates) - 1, fid - k)) for k in range(TMAX)]
        win_yaw.append(float(np.mean([rates[i] for i in idx])))
    win_yaw = np.array(win_yaw)

    tr_idx = [i for i, s in enumerate(samples) if s["seq"] not in PROBE_TEST_SEQS]
    te_idx = [i for i, s in enumerate(samples) if s["seq"] in PROBE_TEST_SEQS]
    y = np.array([s["e_turning"] for s in samples]).astype(int)
    out = {}
    for arm in ("raw", "gmc", "gnd"):
        Xf = np.stack([s["X"][arm] for s in samples]).reshape(len(samples), -1)
        te_yaw = win_yaw[te_idx]
        qs = np.percentile(te_yaw, [33, 66])
        row = {"tercile_bounds_degpf": [round(float(q), 4) for q in qs]}
        for name, lo, hi in (("stable", -1, qs[0]), ("mid", qs[0], qs[1]),
                             ("rotating", qs[1], 1e9)):
            te_s = [i for i in te_idx if lo < win_yaw[i] <= hi]
            row[name] = {"f1": run(Xf, y, tr_idx, te_s),
                         "n": len(te_s), "pos": int(y[te_s].sum())}
        out[arm] = row
        print("A turning x ego-yaw", arm, json.dumps(row), flush=True)
    return out


def part_b():
    # rebuild oracle samples via tprobe3 extraction (center-distance mapping)
    import diagnostics.tprobe3_oracle as t3
    samples = t3.extract()
    tr_idx = [i for i, s in enumerate(samples) if s["seq"] not in PROBE_TEST_SEQS]
    te_idx = [i for i, s in enumerate(samples) if s["seq"] in PROBE_TEST_SEQS]
    X = np.stack([s["X"] for s in samples])  # (N, 16, 11)
    # cols: 0 X/30, 1 Z/30, 2 vX, 3 vZ, 4 sin(roty), 5 cos(roty),
    #       6 sin(world), 7 cos(world), 8 droty, 9 d(world), 10 deyaw
    GROUPS = {
        "position_XZ": [0, 1],
        "velocity_vXvZ": [2, 3],
        "heading_roty": [4, 5],
        "heading_world": [6, 7],
        "dheading": [8, 9, 10],
        "full": list(range(11)),
    }
    out = {}
    for task in ("turning", "counter", "moving_vs_static"):
        if task == "moving_vs_static":
            m = np.array([(s["e_moving"] != s["e_static"]) and
                          (s["e_moving"] or s["e_static"]) for s in samples])
            y = np.array([s["e_moving"] for s in samples]).astype(int)
        else:
            y = np.array([s["e_" + task] for s in samples]).astype(int)
            m = np.ones(len(samples), bool)
        tr = [i for i in tr_idx if m[i]]
        te = [i for i in te_idx if m[i]]
        row = {}
        for g, cols in GROUPS.items():
            Xg = X[:, :, cols].reshape(len(samples), -1)
            row[g] = run(Xg, y, tr, te)
        out[task] = row
        print("B components", task, json.dumps(row), flush=True)
    return out


if __name__ == "__main__":
    results = {"A_turning_by_ego_yaw": part_a(), "B_oracle_components": part_b()}
    with open(os.path.join(OUT_DIR, "tprobe4_results.json"), "w") as f:
        json.dump(results, f, indent=2)
    print(f"saved -> {OUT_DIR}/tprobe4_results.json")
