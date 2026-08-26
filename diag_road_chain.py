"""Four open questions on the SHIP road-plane ego chain, answered in one replay.

Replays every adjacent frame pair on the 4 eval seqs and the 15 V1 train seqs.
Eval seqs 0005/0011/0013 use real NeuralSORT foreground masks (inference
condition, manager.py:294-296). 0019 has no NeuralSORT output in this repo and
the train seqs are fitted WITHOUT masks -- exactly what training does
(dataset.py:1057 passes no boxes). The mask condition is recorded per row.

Pre-registered readings (decide before looking):

Q1  wild-H tail of the 8-DOF road fit. Never instrumented -- diag_hgate_instrument
    covers the global path only, and A13 measured 8/916 wild on 8-DOF there.
    AMENDED after the 8-pair smoke (2026-08-25): the GMC_HGATE bounds
    (|h31|,|h32| > 1e-3, corner disp > 150 px) are calibrated for the GLOBAL fit,
    whose dominant plane is far away. A road-plane homography under forward
    motion physically carries h32 ~ v/(f*d) (f~720 px, camera height d~1.65 m,
    ~1 m/frame -> ~1e-3), and the smoke showed h32 = -1.1e-3 on every 0005 pair
    and -4e-4 on 0011, i.e. the bound would flag ordinary driving. The HGATE
    counts are kept as a descriptive column only. The referee for "wild" is
    threshold-free and photometric: warp I_{t-1} by H, take the mean |diff| to
    I_t over the road band minus boxes, and compare with identity (no warp) and
    with the similarity-chain H (the previous ship's global 4-DOF fit).
      wild_photo  := road residual > identity residual  (the fit made alignment worse)
      road_beats_sim := road residual < sim residual    (per pair; fraction reported)
    0 wild_photo -> the paper may state no degenerate fit over N pairs.
    road_beats_sim is the estimator-level version of the A25/A29 mechanism claim.

Q2  road_band = 0.5 prior (never swept). Refit at band in {0.3,0.4,0.5,0.6,0.7};
    record corners / tracked / inliers / inlier residual, and the max displacement
    between H_band and H_0.5 on the lower-half grid.
    AMENDED after smoke: grid disagreement scales with speed (0005 at 17.6 m/s
    gives 150-250 px between bands), so the px thresholds below are not usable
    as written. Reading = per-band photometric residual on ONE fixed region
    (band 0.5 minus boxes) -- the band whose H aligns the road best wins, and
    0.5 is justified iff its residual is at or within noise of the minimum.
    Original px rule kept for the record:
    p95(disagreement of 0.4 and 0.6 vs 0.5) < 1 px -> prior is not load-bearing at
        the estimator level; a HOTA sweep is not warranted.
    > 3 px -> HOTA sweep warranted.

Q3  ORB on the SAME road band. "Asphalt is too low-texture for ORB" is a design
    argument so far. ORB(1500) on prev with band-minus-boxes mask, BFMatcher knn2
    + Lowe 0.7 (core.py pipeline), RANSAC 5 px. Reading = fraction of pairs whose
    good-match count is < 12 (the road fit's own minimum), inlier counts and
    inlier residual vs LK, and the ORB-H photometric residual on the band.
    (Smoke already showed ORB does NOT starve on the lower half: good p50 ~176.)

Q4  fallback rate on the 15 training seqs (only the 4 eval seqs were measured:
    results/road_fallback_rate.json = 2065/2065). Reading = count of None.

Also recorded per pair: oxts forward speed (m/s) for physical sanity of the
displacement column.

Self-check: at band 0.5 the inline fit must agree with
ORBHomographyEngine.estimate_road_homography (same OpenCV calls). RANSAC draws
fresh random samples per call, so exact equality is not expected; < 0.5 px
grid disagreement is.

Output: results/road_diag/road_chain_diag[_<tag>].json (per-seq aggregates +
per-pair rows) and a printed summary.
Run:  /home/seanachan/miniconda/envs/RMOT/bin/python diag_road_chain.py \
          [--seqs eval|train|all] [--limit N] [--tag smoke]
"""
import argparse
import json
import os
import sys
import time

import cv2
import numpy as np

REPO = "/home/seanachan/GMC-Link"
sys.path.insert(0, REPO)
os.environ.setdefault("GMC_MODEL", "similarity")       # sim-chain engine = previous ship
from gmc_link.core import ORBHomographyEngine          # noqa: E402
from gmc_link.utils import warp_points                 # noqa: E402
from run_ikun_linear_additive import merged_ns         # noqa: E402

IMG_DIR = REPO + "/refer-kitti/KITTI/training/image_02/{seq}"
EVAL_SEQS = ["0005", "0011", "0013", "0019"]
TRAIN_SEQS = ["0001", "0002", "0003", "0004", "0006", "0007", "0008", "0009",  # = train.V1_TRAIN_SEQS
              "0010", "0012", "0014", "0015", "0016", "0018", "0020"]
NS_SEQS = {"0005", "0011", "0013"}
BANDS = [0.3, 0.4, 0.5, 0.6, 0.7]
MIN_PTS = 12            # core.py road fit minimum
WILD_DISP = 150.0       # GMC_HGATE bounds
WILD_PERSP = 1e-3
OXTS = "/home/seanachan/data/kitti_tracking/training/oxts/{seq}.txt"


def band_mask(h, w, band, boxes):
    m = np.zeros((h, w), dtype=np.uint8)
    m[int(h * band):, :] = 255
    for x1, y1, x2, y2 in boxes:
        x1, y1 = max(0, int(x1)), max(0, int(y1))
        x2, y2 = min(w, int(x2)), min(h, int(y2))
        if x2 > x1 and y2 > y1:
            m[y1:y2, x1:x2] = 0
    return m


def road_fit(pg, cg, mask):
    """Inline copy of core.estimate_road_homography with the counts exposed."""
    out = {"H": None, "corners": 0, "tracked": 0, "inliers": 0, "res": None}
    pts = cv2.goodFeaturesToTrack(pg, maxCorners=600, qualityLevel=0.01, minDistance=7, mask=mask)
    if pts is None:
        return out
    out["corners"] = len(pts)
    if len(pts) < MIN_PTS:
        return out
    nxt, st, _ = cv2.calcOpticalFlowPyrLK(pg, cg, pts, None, winSize=(21, 21), maxLevel=3)
    ok = st.ravel() == 1
    out["tracked"] = int(ok.sum())
    if ok.sum() < MIN_PTS:
        return out
    H, inl = cv2.findHomography(pts[ok], nxt[ok], cv2.RANSAC, 3.0)
    if H is None:
        return out
    inl = inl.ravel().astype(bool)
    src, dst = pts[ok].reshape(-1, 2)[inl], nxt[ok].reshape(-1, 2)[inl]
    out["H"] = H.astype(np.float32)
    out["inliers"] = int(inl.sum())
    out["res"] = float(np.median(np.linalg.norm(warp_points(src, out["H"]) - dst, axis=1))) if inl.sum() else None
    out["src"] = src
    return out


ORB = cv2.ORB_create(1500)
BF = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)


def orb_fit(pg, cg, mask):
    """core.estimate_homography's ORB pipeline restricted to the road band mask.
    Fits the same matches at RANSAC 5 px (core) and 3 px (the road fit's threshold)
    so the ORB-vs-LK comparison is not confounded by the threshold (E4a)."""
    base = {"kp": 0, "good": 0, "inliers": 0, "fail": True, "res": None, "H": None, "src": None}
    out = dict(base)
    out["r3"] = dict(base)
    kp1, d1 = ORB.detectAndCompute(pg, mask=mask)
    kp2, d2 = ORB.detectAndCompute(cg, None)
    out["kp"] = 0 if d1 is None else len(kp1)
    if d1 is None or d2 is None or len(kp1) < 4 or len(kp2) < 4:
        return out
    good = []
    for pair in BF.knnMatch(d1, d2, k=2):
        if len(pair) == 2 and pair[0].distance < 0.7 * pair[1].distance:
            good.append(pair[0])
        elif len(pair) == 1:
            good.append(pair[0])
    out["good"] = out["r3"]["good"] = len(good)
    if len(good) < 4:
        return out
    src = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    for key, thr in (("5", 5.0), ("3", 3.0)):
        tgt = out if key == "5" else out["r3"]
        H, inl = cv2.findHomography(src, dst, cv2.RANSAC, thr)
        if H is None:
            continue
        inl = inl.ravel().astype(bool)
        tgt["inliers"], tgt["fail"], tgt["H"] = int(inl.sum()), False, H.astype(np.float32)
        s_, d_ = src.reshape(-1, 2)[inl], dst.reshape(-1, 2)[inl]
        tgt["src"] = s_
        tgt["res"] = float(np.median(np.linalg.norm(warp_points(s_, tgt["H"]) - d_, axis=1))) if inl.sum() else None
    return out


def spatial(pts, h, w):
    """Where the inliers are: fraction in the central road corridor, normalized y quantiles."""
    if pts is None or len(pts) == 0:
        return None
    x, y = pts[:, 0], pts[:, 1]
    return {"central": round(float(np.mean(np.abs(x - w / 2) < 0.25 * w)), 3),
            "y_p25": round(float(np.percentile(y, 25) / h), 3), "y_p50": round(float(np.percentile(y, 50) / h), 3),
            "y_p75": round(float(np.percentile(y, 75) / h), 3), "n": int(len(pts))}


def photo_res(pg, cg, H, region):
    """Mean |warp(prev by H) - curr| over region (uint8 mask), valid pixels only."""
    h, w = pg.shape
    if H is None:
        return None
    warped = cv2.warpPerspective(pg, H, (w, h))
    valid = cv2.warpPerspective(np.full((h, w), 255, np.uint8), H, (w, h)) > 0
    m = (region > 0) & valid
    if m.sum() < 1000:
        return None
    return float(np.abs(warped[m].astype(np.float32) - cg[m].astype(np.float32)).mean())


def lower_grid(h, w):
    xs, ys = np.linspace(0.1 * w, 0.9 * w, 5), np.linspace(0.55 * h, 0.95 * h, 3)
    return np.array([[x, y] for y in ys for x in xs], dtype=np.float32)


def max_disp(Ha, Hb, g):
    return float(np.linalg.norm(warp_points(g, Ha) - warp_points(g, Hb), axis=1).max())


def pct(a, q):
    return None if len(a) == 0 else float(np.percentile(a, q))


def summarize(rows):
    """Per-seq / total aggregates. Only rows whose eng fit succeeded enter the H stats."""
    okrows = [r for r in rows if not r["fallback"]]
    disp = np.array([r["disp"] for r in okrows])
    sc = np.array([r["selfcheck"] for r in okrows if r["selfcheck"] is not None])
    pr = [r["photo"] for r in okrows if r["photo"]["road"] is not None and r["photo"]["ident"] is not None]
    prs = [p for p in pr if p["sim"] is not None]
    out = {
        "pairs": len(rows), "fallback": sum(r["fallback"] for r in rows),
        "hgate_flag": sum(r["wild"] for r in okrows),
        "wild_photo": sum(p["road"] > p["ident"] for p in pr),
        "wild_photo_pairs": [(r["seq"], r["f0"], round(r["photo"]["road"], 1), round(r["photo"]["ident"], 1))
                             for r in okrows if r["photo"]["road"] is not None and r["photo"]["ident"] is not None
                             and r["photo"]["road"] > r["photo"]["ident"]],
        "road_beats_sim": sum(p["road"] < p["sim"] for p in prs), "n_sim": len(prs),
        "photo_p50": {"ident": pct([p["ident"] for p in pr], 50), "road": pct([p["road"] for p in pr], 50),
                      "sim": pct([p["sim"] for p in prs], 50),
                      "orb_band": pct([p["orb"] for p in pr if p["orb"] is not None], 50)},
        "road_vs_sim_grid_px": {"p50": pct([r["road_vs_sim"] for r in okrows if r["road_vs_sim"] is not None], 50),
                                "p95": pct([r["road_vs_sim"] for r in okrows if r["road_vs_sim"] is not None], 95)},
        "speed_mps_p50": pct([r["vf"] for r in rows if r["vf"] is not None], 50),
        "disp_px": {"p50": pct(disp, 50), "p95": pct(disp, 95), "p99": pct(disp, 99),
                    "max": float(disp.max()) if len(disp) else None},
        "selfcheck_px": {"p95": pct(sc, 95), "max": float(sc.max()) if len(sc) else None},
        "bands": {}, "orb": {},
    }
    for b in BANDS:
        k = str(b)
        bs = [r["bands"][k] for r in rows]
        okb = [x for x in bs if x["H_ok"]]
        d05 = np.array([x["dis_vs_05"] for x in okb if x["dis_vs_05"] is not None])
        out["bands"][k] = {
            "fail": sum(not x["H_ok"] for x in bs),
            "corners_p50": pct([x["corners"] for x in bs], 50),
            "tracked_p50": pct([x["tracked"] for x in bs], 50),
            "inliers_p50": pct([x["inliers"] for x in okb], 50),
            "res_p50": pct([x["res"] for x in okb if x["res"] is not None], 50),
            "photo_p50": pct([x["photo"] for x in okb if x["photo"] is not None], 50),
            "photo_near_p50": pct([x.get("photo_near") for x in okb if x.get("photo_near") is not None], 50),
            "dis_vs_05_px": {"p50": pct(d05, 50), "p95": pct(d05, 95),
                             "max": float(d05.max()) if len(d05) else None},
        }
    ob = [r["orb"] for r in rows]
    out["orb"] = {
        "kp_p50": pct([x["kp"] for x in ob], 50), "good_p50": pct([x["good"] for x in ob], 50),
        "inliers_p50": pct([x["inliers"] for x in ob if not x["fail"]], 50),
        "frac_good_lt_12": float(np.mean([x["good"] < MIN_PTS for x in ob])),
        "fail": sum(x["fail"] for x in ob),
        "res_p50": pct([x["res"] for x in ob if x["res"] is not None], 50),
        "vs_lk05_grid_px": {"p50": pct([x["vs_lk05"] for x in ob if x["vs_lk05"] is not None], 50),
                            "p95": pct([x["vs_lk05"] for x in ob if x["vs_lk05"] is not None], 95)},
    }
    out["lk_inliers_p50_band05"] = out["bands"]["0.5"]["inliers_p50"]
    o3 = [r["orb3"] for r in rows if r.get("orb3")]
    out["orb3"] = {"inliers_p50": pct([x["inliers"] for x in o3 if not x["fail"]], 50),
                   "res_p50": pct([x["res"] for x in o3 if x["res"] is not None], 50),
                   "photo_p50": pct([x["photo"] for x in o3 if x["photo"] is not None], 50),
                   "fail": sum(x["fail"] for x in o3),
                   "vs_lk05_grid_px": {"p50": pct([x["vs_lk05"] for x in o3 if x["vs_lk05"] is not None], 50),
                                       "p95": pct([x["vs_lk05"] for x in o3 if x["vs_lk05"] is not None], 95)}}
    sp = [r["spatial"] for r in rows if r.get("spatial")]
    out["spatial"] = {k: {"central_p50": pct([x[k]["central"] for x in sp if x.get(k)], 50),
                          "y_p50_p50": pct([x[k]["y_p50"] for x in sp if x.get(k)], 50)}
                      for k in ("orb5", "orb3", "lk")}
    nm = [r["nomask"] for r in rows if r.get("nomask")]
    nmp = [(r["nomask"]["photo"], r["photo"]["road"]) for r in rows
           if r.get("nomask") and r["nomask"]["photo"] is not None and r["photo"]["road"] is not None]
    out["nomask"] = {"n": len(nm),
                     "vs_masked_grid_px": {"p50": pct([x["vs_masked"] for x in nm if x["vs_masked"] is not None], 50),
                                           "p95": pct([x["vs_masked"] for x in nm if x["vs_masked"] is not None], 95)},
                     "photo_p50_masked": pct([m for _, m in nmp], 50), "photo_p50_nomask": pct([n for n, _ in nmp], 50),
                     "nomask_worse_by_gt1": sum(n - m > 1 for n, m in nmp), "masked_worse_by_gt1": sum(m - n > 1 for n, m in nmp)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seqs", default="all", choices=["eval", "train", "all"])
    ap.add_argument("--limit", type=int, default=0, help="first N pairs per seq (smoke)")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    seqs = {"eval": EVAL_SEQS, "train": TRAIN_SEQS, "all": EVAL_SEQS + TRAIN_SEQS}[a.seqs]

    eng = ORBHomographyEngine()
    rows, t_fit = [], []
    for seq in seqs:
        d = IMG_DIR.format(seq=seq)
        fids = sorted(int(f[:-4]) for f in os.listdir(d) if f.endswith(".png"))
        ns = merged_ns(seq) if seq in NS_SEQS else None
        vf = {}
        if os.path.exists(OXTS.format(seq=seq)):
            vf = {i: float(l.split()[8]) for i, l in enumerate(open(OXTS.format(seq=seq)))}
        pairs = [(f0, f1) for f0, f1 in zip(fids, fids[1:]) if f1 == f0 + 1]
        if a.limit:
            pairs = pairs[:a.limit]
        for f0, f1 in pairs:
            pg = cv2.imread(f"{d}/{f0:06d}.png", cv2.IMREAD_GRAYSCALE)
            cg = cv2.imread(f"{d}/{f1:06d}.png", cv2.IMREAD_GRAYSCALE)
            h, w = pg.shape
            g = lower_grid(h, w)
            boxes = [(x, y, x + bw, y + bh) for _, x, y, bw, bh in ns[f0]] if ns and f0 in ns else []
            t0 = time.perf_counter()
            H_eng = eng.estimate_road_homography(pg, cg, boxes)          # what ship does
            t_fit.append((time.perf_counter() - t0) * 1000)
            H_sim, _ = eng.estimate_homography(pg, cg, prev_bboxes=boxes)   # previous ship (4-DOF similarity)
            fits = {b: road_fit(pg, cg, band_mask(h, w, b, boxes)) for b in BANDS}
            H05 = fits[0.5]["H"]
            region = band_mask(h, w, 0.5, boxes)
            near = band_mask(h, w, 0.7, boxes)      # inside every band's sampling region
            orb = orb_fit(pg, cg, region)
            orb3 = orb.pop("r3")
            for o in (orb, orb3):
                o["vs_lk05"] = round(max_disp(o["H"], H05, g), 3) if o["H"] is not None and H05 is not None else None
                o["photo"] = photo_res(pg, cg, o["H"], region)
            spat = {"orb5": spatial(orb["src"], h, w), "orb3": spatial(orb3["src"], h, w),
                    "lk": spatial(fits[0.5]["src"], h, w)}
            # E4b: train-side fit passes NO boxes (dataset.py:1057); quantify vs the masked fit
            nomask = None
            if boxes:
                nm = road_fit(pg, cg, band_mask(h, w, 0.5, []))
                nomask = {"inliers": nm["inliers"], "res": None if nm["res"] is None else round(nm["res"], 3),
                          "photo": photo_res(pg, cg, nm["H"], region),
                          "vs_masked": round(max_disp(nm["H"], H05, g), 3) if nm["H"] is not None and H05 is not None else None}
            photo = {"ident": photo_res(pg, cg, np.eye(3, dtype=np.float32), region),
                     "road": photo_res(pg, cg, H_eng, region), "sim": photo_res(pg, cg, H_sim, region),
                     "orb": orb["photo"]}
            for o in (orb, orb3):
                o.pop("H"); o.pop("src")
            row = {"seq": seq, "f0": f0, "mask": "ns" if ns else "none", "n_boxes": len(boxes),
                   "fallback": H_eng is None, "wild": False, "disp": None, "h31": None, "h32": None,
                   "selfcheck": None, "bands": {}, "orb": orb, "orb3": orb3, "spatial": spat, "nomask": nomask,
                   "photo": photo, "vf": vf.get(f0),
                   "road_vs_sim": max_disp(H_eng, H_sim, g) if H_eng is not None else None}
            if H_eng is not None:
                row["disp"] = max_disp(H_eng, np.eye(3, dtype=np.float32), g)
                row["h31"], row["h32"] = float(H_eng[2, 0]), float(H_eng[2, 1])
                row["wild"] = (abs(row["h31"]) > WILD_PERSP or abs(row["h32"]) > WILD_PERSP
                               or row["disp"] > WILD_DISP)
                if H05 is not None:
                    row["selfcheck"] = max_disp(H_eng, H05, g)
            for b in BANDS:
                f = fits[b]
                f.pop("src", None)
                row["bands"][str(b)] = {
                    "photo": photo_res(pg, cg, f["H"], region),
                    "photo_near": photo_res(pg, cg, f["H"], near),
                    "H_ok": f["H"] is not None, "corners": f["corners"], "tracked": f["tracked"],
                    "inliers": f["inliers"], "res": None if f["res"] is None else round(f["res"], 3),
                    "dis_vs_05": (round(max_disp(f["H"], H05, g), 3)
                                  if f["H"] is not None and H05 is not None else None)}
            rows.append(row)
        s = summarize([r for r in rows if r["seq"] == seq])
        pp = s["photo_p50"]
        print(f"{seq} mask={'ns' if ns else 'none'} pairs={s['pairs']} fallback={s['fallback']} "
              f"wild_photo={s['wild_photo']} hgate={s['hgate_flag']} road>sim {s['road_beats_sim']}/{s['n_sim']} "
              f"photo I/road/sim/orb={pp['ident']:.1f}/{pp['road']:.1f}/{pp['sim']:.1f}/{pp['orb_band']:.1f} "
              f"v={s['speed_mps_p50']:.1f}m/s disp p95={s['disp_px']['p95']:.0f} selfcheck max={s['selfcheck_px']['max']:.2f} "
              f"| band0.4/0.6 vs 0.5 p95={s['bands']['0.4']['dis_vs_05_px']['p95']:.2f}/"
              f"{s['bands']['0.6']['dis_vs_05_px']['p95']:.2f}px "
              f"| ORB good p50={s['orb']['good_p50']:.0f} <12:{s['orb']['frac_good_lt_12']:.1%} "
              f"vs LK inl p50={s['lk_inliers_p50_band05']:.0f}", flush=True)

    per_seq = {seq: summarize([r for r in rows if r["seq"] == seq]) for seq in seqs}
    total = summarize(rows)
    total["eval"] = summarize([r for r in rows if r["seq"] in EVAL_SEQS]) if any(r["seq"] in EVAL_SEQS for r in rows) else None
    total["train"] = summarize([r for r in rows if r["seq"] in TRAIN_SEQS]) if any(r["seq"] in TRAIN_SEQS for r in rows) else None
    total["road_fit_ms_p50"] = pct(t_fit, 50)
    out = {"protocol": __doc__, "bands": BANDS, "per_seq": per_seq, "total": total, "rows": rows}
    os.makedirs(f"{REPO}/results/road_diag", exist_ok=True)
    path = f"{REPO}/results/road_diag/road_chain_diag{('_' + a.tag) if a.tag else ''}.json"
    json.dump(out, open(path, "w"), indent=1, default=float)
    pp = total["photo_p50"]
    print(f"\nTOTAL pairs={total['pairs']} fallback={total['fallback']} wild_photo={total['wild_photo']} "
          f"hgate_flag={total['hgate_flag']} road_beats_sim={total['road_beats_sim']}/{total['n_sim']} "
          f"photo p50 I/road/sim/orb={pp['ident']:.2f}/{pp['road']:.2f}/{pp['sim']:.2f}/{pp['orb_band']:.2f} "
          f"road-vs-sim grid p50/p95={total['road_vs_sim_grid_px']['p50']:.1f}/{total['road_vs_sim_grid_px']['p95']:.1f}px "
          f"disp p99={total['disp_px']['p99']:.1f} max={total['disp_px']['max']:.1f}px "
          f"selfcheck p95={total['selfcheck_px']['p95']:.2f}px road_fit {total['road_fit_ms_p50']:.1f}ms")
    for b in BANDS:
        bb = total["bands"][str(b)]
        print(f"  band {b}: fail={bb['fail']} corners={bb['corners_p50']:.0f} tracked={bb['tracked_p50']:.0f} "
              f"inliers={bb['inliers_p50']:.0f} res={bb['res_p50']:.3f}px photo={bb['photo_p50']:.2f} near={bb['photo_near_p50']:.2f} "
              f"vs0.5 p50/p95/max={bb['dis_vs_05_px']['p50']:.2f}/{bb['dis_vs_05_px']['p95']:.2f}/{bb['dis_vs_05_px']['max']:.1f}px")
    o = total["orb"]
    print(f"  ORB@band0.5: kp={o['kp_p50']:.0f} good={o['good_p50']:.0f} inliers={o['inliers_p50']:.0f} "
          f"res={o['res_p50']:.3f}px good<12 on {o['frac_good_lt_12']:.1%} of pairs, fail={o['fail']}  "
          f"(LK inliers p50={total['lk_inliers_p50_band05']:.0f}) ORB-vs-LK grid p50/p95={o['vs_lk05_grid_px']['p50']:.1f}/{o['vs_lk05_grid_px']['p95']:.1f}px")
    o3, sp, nm = total["orb3"], total["spatial"], total["nomask"]
    print(f"  ORB@3px:     inliers={o3['inliers_p50']:.0f} res={o3['res_p50']:.3f}px photo={o3['photo_p50']:.2f} fail={o3['fail']} "
          f"ORB3-vs-LK grid p50/p95={o3['vs_lk05_grid_px']['p50']:.1f}/{o3['vs_lk05_grid_px']['p95']:.1f}px")
    print("  inlier location (central corridor frac / y_p50 of image): "
          + " ".join(f"{k}={sp[k]['central_p50']:.2f}/{sp[k]['y_p50_p50']:.2f}" for k in ("orb5", "orb3", "lk")))
    if nm["n"]:
        print(f"  E4b no-mask fit (n={nm['n']} masked pairs): vs masked grid p50/p95={nm['vs_masked_grid_px']['p50']:.1f}/"
              f"{nm['vs_masked_grid_px']['p95']:.1f}px photo masked/nomask={nm['photo_p50_masked']:.2f}/{nm['photo_p50_nomask']:.2f} "
              f"nomask worse>1: {nm['nomask_worse_by_gt1']}  masked worse>1: {nm['masked_worse_by_gt1']}")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
