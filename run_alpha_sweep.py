"""Alpha sweep driver: evaluate s_final = s_host + alpha * s_gmc at multiple
alphas on fixed trained GMC caches (no retraining), aggregate to CSV/JSON.

Per (arch, seed, alpha): subprocess the arch eval script with GMC_SUFFIX /
OUT_SUFFIX set for that seed, then read the result.json it writes.
Runs are serial (TrackEval is CPU-bound; keeps output readable).

Output:
    results/alpha_sweep_{arch}.csv   aggregated mean/std per alpha
    results/alpha_sweep_{arch}.json  per-seed rows + aggregates + provenance

Usage:
    python run_alpha_sweep.py --arch ikun  --alphas 0,0.1,0.2,0.3,0.5,0.7,1.0
    python run_alpha_sweep.py --arch fh_v1 --alphas 0,1,2,3,5,7,10
    python run_alpha_sweep.py --arch fh_v2 --alphas 0,1,2,3,5,7,10
    python run_alpha_sweep.py --arch ikun --alphas 0,0.3 --seeds 0 --dry-run
"""
import argparse, csv, json, os, statistics, subprocess, sys

REPO = "/home/seanachan/GMC-Link"

ARCHS = {
    "ikun": {
        "script": "run_ikun_linear_additive.py",
        "out_root": "hota_eval_ikun_linear_additive",
    },
    "fh_v1": {
        "script": "run_flexhook_phase5_gmc_sweep.py",
        "out_root": "hota_eval_flexhook_phase5_gmc",
    },
    "fh_v2": {
        "script": "run_flexhook_v2_raw_sweep.py",
        "out_root": "hota_eval_flexhook_v2_raw_gmc",
    },
}
METRICS = ("pooled", "moving", "static", "appearance")


def run_one(arch, seed, alpha, suffix_template, dry_run):
    cfg = ARCHS[arch]
    suffix = suffix_template.format(seed=seed)
    env = dict(os.environ, GMC_SUFFIX=suffix, OUT_SUFFIX=suffix)
    cmd = [sys.executable, os.path.join(REPO, cfg["script"]), "--alpha", str(alpha)]
    result_path = os.path.join(
        REPO, cfg["out_root"] + suffix, f"alpha{alpha}", "result.json")
    if dry_run:
        print(f"DRY  GMC_SUFFIX={suffix} {' '.join(cmd)}  →  {result_path}")
        return None
    print(f"RUN  {arch} seed={seed} alpha={alpha}", flush=True)
    proc = subprocess.run(cmd, env=env, cwd=REPO)
    if proc.returncode != 0 or not os.path.exists(result_path):
        sys.stderr.write(f"FAIL {arch} seed={seed} alpha={alpha} "
                         f"rc={proc.returncode} ({result_path} missing)\n")
        return None
    row = json.load(open(result_path))
    row["seed"] = seed
    return row


def aggregate(rows, alphas):
    agg = []
    for alpha in alphas:
        sub = [r for r in rows if r["alpha"] == alpha]
        if not sub:
            continue
        entry = {"alpha": alpha, "n_seeds": len(sub)}
        for m in METRICS:
            vals = [r[m] for r in sub if r.get(m) is not None]
            entry[f"{m}_mean"] = round(statistics.mean(vals), 3) if vals else None
            entry[f"{m}_std"] = (round(statistics.stdev(vals), 3)
                                 if len(vals) > 1 else 0.0 if vals else None)
        agg.append(entry)
    return agg


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--arch", required=True, choices=sorted(ARCHS))
    p.add_argument("--alphas", required=True,
                   help="comma list, e.g. 0,0.1,0.2,0.3,0.5,0.7,1.0")
    p.add_argument("--seeds", default="0,1,2", help="comma list, default 0,1,2")
    p.add_argument("--suffix-template", default="_sw12d_seed{seed}",
                   help="GMC_SUFFIX per seed (default: _sw12d_seed{seed})")
    p.add_argument("--out-dir", default=os.path.join(REPO, "results"))
    p.add_argument("--dry-run", action="store_true",
                   help="print planned commands, run nothing")
    args = p.parse_args()

    alphas = [float(a) for a in args.alphas.split(",")]
    seeds = [int(s) for s in args.seeds.split(",")]

    rows = []
    for alpha in alphas:          # alpha-outer: early alphas complete first
        for seed in seeds:
            row = run_one(args.arch, seed, alpha, args.suffix_template, args.dry_run)
            if row is not None:
                rows.append(row)
    if args.dry_run:
        return

    agg = aggregate(rows, alphas)
    os.makedirs(args.out_dir, exist_ok=True)
    base = os.path.join(args.out_dir, f"alpha_sweep_{args.arch}")

    with open(base + ".csv", "w", newline="") as f:
        cols = ["alpha", "n_seeds"] + [f"{m}_{s}" for m in METRICS for s in ("mean", "std")]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(agg)

    with open(base + ".json", "w") as f:
        json.dump({
            "arch": args.arch,
            "suffix_template": args.suffix_template,
            "seeds": seeds,
            "fusion": "s_final = s_host + alpha * s_gmc (raw cos), gate 0.0",
            "per_seed": rows,
            "aggregate": agg,
        }, f, indent=2)

    print(f"\n=== alpha sweep summary: {args.arch} (n={len(seeds)} seeds) ===")
    print(f"{'alpha':>6} {'pooled':>14} {'MOVING':>14} {'STATIC':>14} {'APPEAR':>14}")
    for e in agg:
        cells = []
        for m in METRICS:
            mu, sd = e[f"{m}_mean"], e[f"{m}_std"]
            cells.append(f"{mu:.3f}±{sd:.3f}" if mu is not None else "None")
        print(f"{e['alpha']:>6} " + " ".join(f"{c:>14}" for c in cells))
    print(f"\nCSV  → {base}.csv\nJSON → {base}.json")


if __name__ == "__main__":
    main()
