"""Track C2 driver: TTC (theta, w) LOSO campaign on iKUN sim caches.
Pre-reg: docs/PREREG_TTC_CALIBRATION_2026_08_16.md
Integrity first (w=0 == plain alpha0.5), then fold sweep, componentwise-median
selection, full-test at star."""
import argparse, itertools, json, os, statistics, subprocess, sys

REPO = "/home/seanachan/GMC-Link"
FOLDS = {"hold0005": "0011,0013", "hold0011": "0005,0013", "hold0013": "0005,0011"}


def run_one(seed, theta, w, suffix_template, eval_seqs=None):
    suffix = suffix_template.format(seed=seed)
    env = dict(os.environ, GMC_SUFFIX=suffix, OUT_SUFFIX=suffix)
    if eval_seqs:
        env["GMC_EVAL_SEQS"] = eval_seqs
    else:
        env.pop("GMC_EVAL_SEQS", None)
    tag = f"th{theta}_w{w}"
    if eval_seqs:
        tag += "_seqs" + "-".join(eval_seqs.split(","))
    result_path = os.path.join(REPO, "hota_eval_ikun_ttc" + suffix, tag, "result.json")
    if not os.path.exists(result_path):
        proc = subprocess.run(
            [sys.executable, os.path.join(REPO, "run_ikun_ttc.py"),
             "--theta", str(theta), "--w", str(w)], env=env, cwd=REPO)
        if proc.returncode != 0 or not os.path.exists(result_path):
            sys.stderr.write(f"FAIL seed={seed} th={theta} w={w} seqs={eval_seqs}\n")
            return None
    return json.load(open(result_path))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--suffix-template", default="_sw12d_seed{seed}_nomema_sim_warm11")
    p.add_argument("--thetas", default="0.5,0.6,0.7,0.8")
    p.add_argument("--ws", default="0.5,1.0")
    p.add_argument("--seeds", default="0,1,2")
    p.add_argument("--out-dir", default="results/ttc_sim")
    args = p.parse_args()
    TH = [float(x) for x in args.thetas.split(",")]
    W = [float(x) for x in args.ws.split(",")]
    seeds = [int(s) for s in args.seeds.split(",")]
    os.makedirs(args.out_dir, exist_ok=True)

    # integrity: w=0 == plain alpha0.5 (seed0)
    ref = json.load(open(os.path.join(
        REPO, "hota_eval_ikun_linear_additive" + args.suffix_template.format(seed=seeds[0]),
        "alpha0.5", "result.json")))
    chk = run_one(seeds[0], 0.5, 0.0, args.suffix_template)
    if chk is None or abs(chk["pooled"] - ref["pooled"]) > 1e-9:
        print(f"INTEGRITY FAIL w=0 {chk and chk['pooled']} != ship {ref['pooled']}")
        sys.exit(1)
    print(f"integrity OK: w=0 == ship alpha0.5 == {ref['pooled']}", flush=True)

    fold_rows = []
    for fname, infold in FOLDS.items():
        for th, w in itertools.product(TH, W):
            for s in seeds:
                r = run_one(s, th, w, args.suffix_template, eval_seqs=infold)
                if r:
                    fold_rows.append(dict(fold=fname, theta=th, w=w, seed=s,
                                          pooled=r["pooled"]))
            print(f"{fname} th={th} w={w} done", flush=True)

    argmaxes = {}
    for fname in FOLDS:
        best, cell = -1, None
        for th, w in itertools.product(TH, W):
            vals = [r["pooled"] for r in fold_rows
                    if r["fold"] == fname and r["theta"] == th and r["w"] == w]
            if vals and statistics.mean(vals) > best:
                best, cell = statistics.mean(vals), (th, w)
        argmaxes[fname] = dict(cell=cell, pooled=round(best, 3))

    def sel(axis_vals, idx):
        gmin, gmax = min(axis_vals), max(axis_vals)
        unc = [argmaxes[f]["cell"][idx] for f in FOLDS
               if argmaxes[f]["cell"][idx] not in (gmax,)]
        if len(unc) < 2:
            return None
        m = statistics.median(sorted(unc))
        return m if m in axis_vals else max(v for v in axis_vals if v < m)

    th_star, w_star = sel(TH, 0), sel(W, 1)
    out = {"grid_theta": TH, "grid_w": W, "fold_argmaxes": argmaxes,
           "theta_star": th_star, "w_star": w_star, "fold_rows": fold_rows,
           "ship_baseline": {"pooled": 44.656, "pooled_std": 0.078,
                             "moving": 30.045, "moving_std": 0.091}}
    if th_star is not None and w_star is not None:
        full = [r for r in (run_one(s, th_star, w_star, args.suffix_template)
                            for s in seeds) if r]
        agg = {}
        for m in ("pooled", "moving", "static", "appearance"):
            vals = [r[m] for r in full if r.get(m) is not None]
            agg[f"{m}_mean"] = round(statistics.mean(vals), 3) if vals else None
            agg[f"{m}_std"] = round(statistics.stdev(vals), 3) if len(vals) > 1 else 0.0
        out["full_test_at_star"] = {"per_seed": full, "aggregate": agg}
        print("FULL-TEST @", (th_star, w_star), agg, flush=True)
    else:
        print("AXIS UNRESOLVED", flush=True)
    json.dump(out, open(os.path.join(args.out_dir, "ttc_campaign.json"), "w"), indent=1)
    print("TTC_DONE", flush=True)


if __name__ == "__main__":
    main()
