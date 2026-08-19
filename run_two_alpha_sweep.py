"""Two-alpha keyword-routed LOSO campaign driver (Track C1 / A32, FH ext A35).
Pre-reg: docs/PREREG_TWO_ALPHA_ROAD_2026_08_16.md (ikun)
         docs/PREREG_TWO_ALPHA_FH_2026_08_18.md  (fh_v1, fh_v2)

Per arm: (1) integrity gates — alpha=0 must reproduce the native baseline
exactly, and the diagonal am=aa=α* must be bit-exact vs the single-α run at α*
with the SAME caches and SAME eval list; (2) LOSO fold sweep over the 2D grid
(pooled only); (3) componentwise-median selection with per-axis censoring;
(4) full-test at the selected point (n=3). Full-test is NOT run at every cell.

Usage:
    python run_two_alpha_sweep.py --arch fh_v1 \
        --suffix-template _sw12d_groad_seed{seed}_warm11 \
        --am 3,5,7,10,15 --aa 0.5,1,2,3,5 --jobs 6 \
        --out-dir results/two_alpha_road_fh_v1
"""
import argparse, itertools, json, os, statistics, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

REPO = "/home/seanachan/GMC-Link"
FOLDS3 = {"hold0005": "0011,0013", "hold0011": "0005,0013", "hold0013": "0005,0011"}
FOLDS4 = {"hold0005": "0011,0013,0019", "hold0011": "0005,0013,0019",
          "hold0013": "0005,0011,0019", "hold0019": "0005,0011,0013"}
ARCH = {
    "ikun": dict(runner="run_ikun_linear_additive.py",
                 out_root="hota_eval_ikun_linear_additive",
                 folds=FOLDS3, diag=0.5, native=44.224, out_extra=""),
    # out_extra isolates official-150 trees from the A27 158-expr trees
    "fh_v1": dict(runner="run_flexhook_phase5_gmc_sweep.py",
                  out_root="hota_eval_flexhook_phase5_gmc",
                  folds=FOLDS3, diag=7.0, native=53.824, out_extra="_off150",
                  needs_official=True),
    "fh_v2": dict(runner="run_flexhook_v2_raw_sweep.py",
                  out_root="hota_eval_flexhook_v2_raw_gmc",
                  folds=FOLDS4, diag=5.0, native=42.526, out_extra=""),
}


def run_cell(cfg, seed, cli, tag, suffix_template, eval_seqs=None):
    suffix = suffix_template.format(seed=seed)
    env = dict(os.environ, GMC_SUFFIX=suffix, OUT_SUFFIX=suffix + cfg["out_extra"])
    if eval_seqs:
        env["GMC_EVAL_SEQS"] = eval_seqs
        tag += "_seqs" + "-".join(eval_seqs.split(","))
    else:
        env.pop("GMC_EVAL_SEQS", None)
    result_path = os.path.join(REPO, cfg["out_root"] + suffix + cfg["out_extra"],
                               tag, "result.json")
    if not os.path.exists(result_path):
        proc = subprocess.run([sys.executable, os.path.join(REPO, cfg["runner"])] + cli,
                              env=env, cwd=REPO, capture_output=True, text=True)
        if proc.returncode != 0 or not os.path.exists(result_path):
            sys.stderr.write(f"FAIL {tag} seed={seed} seqs={eval_seqs}\n"
                             f"{proc.stderr[-800:]}\n")
            return None
    return json.load(open(result_path))


def run_two(cfg, seed, am, aa, st, eval_seqs=None):
    return run_cell(cfg, seed, ["--alpha-mot", str(am), "--alpha-app", str(aa)],
                    f"am{am}_aa{aa}", st, eval_seqs)


def run_single(cfg, seed, a, st, eval_seqs=None):
    return run_cell(cfg, seed, ["--alpha", str(a)], f"alpha{a}", st, eval_seqs)


def single_alpha_loso(cfg, args, ALPHAS, seeds, st):
    """A37: single-α LOSO for a host that has a full-test sweep but no folds.
    Same selection rule as the two-α campaign, one axis. Pre-reg:
    docs/PREREG_FH_ROAD_SINGLE_ALPHA_2026_08_19.md
    """
    if not args.skip_integrity:
        a0 = run_single(cfg, seeds[0], 0.0, st)
        if a0 is None or abs(a0["pooled"] - cfg["native"]) > 5e-4:
            print(f"NATIVE GATE FAIL: alpha=0 pooled={a0 and a0['pooled']} "
                  f"expected {cfg['native']}")
            sys.exit(1)
        print(f"native gate OK: alpha=0 pooled == {a0['pooled']}", flush=True)

    cells = [(f, infold, a, s) for f, infold in cfg["folds"].items()
             for a in ALPHAS for s in seeds]

    def worker(c):
        fname, infold, a, s = c
        r = run_single(cfg, s, a, st, eval_seqs=infold)
        print(f"{fname} alpha={a} seed={s} {'done' if r else 'FAIL'}", flush=True)
        return (fname, a, s, r)

    rows = []
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        for fname, a, s, r in ex.map(worker, cells):
            if r:
                rows.append(dict(fold=fname, alpha=a, seed=s, pooled=r["pooled"]))

    argmaxes = {}
    for fname in cfg["folds"]:
        best, best_a = -1, None
        for a in ALPHAS:
            vals = [r["pooled"] for r in rows if r["fold"] == fname and r["alpha"] == a]
            if vals and statistics.mean(vals) > best:
                best, best_a = statistics.mean(vals), a
        argmaxes[fname] = dict(alpha=best_a, pooled=round(best, 3))

    unc = [argmaxes[f]["alpha"] for f in cfg["folds"]
           if argmaxes[f]["alpha"] != max(ALPHAS)]
    if len(unc) < 2:
        alpha_star = None  # axis unresolved per pre-reg -> host keeps the sim chain
    else:
        m = statistics.median(sorted(unc))
        alpha_star = m if m in ALPHAS else max(v for v in ALPHAS if v < m)

    out = {"arch": args.arch, "mode": "single_alpha_loso", "suffix_template": st,
           "grid": ALPHAS, "native_ref": cfg["native"],
           "official_seqmap": os.environ.get("FH_OFFICIAL_SEQMAP"),
           "fold_argmaxes": argmaxes, "alpha_star": alpha_star, "fold_rows": rows}

    if alpha_star is not None:
        full = [r for r in (run_single(cfg, s, alpha_star, st) for s in seeds) if r]
        agg = {}
        for m_ in ("pooled", "moving", "static", "appearance"):
            vals = [r[m_] for r in full if r.get(m_) is not None]
            agg[f"{m_}_mean"] = round(statistics.mean(vals), 3) if vals else None
            agg[f"{m_}_std"] = round(statistics.stdev(vals), 3) if len(vals) > 1 else 0.0
        out["full_test_at_star"] = {"per_seed": full, "aggregate": agg}
        print("FULL-TEST @", alpha_star, agg, flush=True)
    else:
        print("AXIS UNRESOLVED -> host keeps the similarity chain (pre-reg)", flush=True)

    json.dump(out, open(os.path.join(args.out_dir, "single_alpha_campaign.json"), "w"),
              indent=1)
    print("SINGLE_ALPHA_DONE", flush=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--arch", required=True, choices=sorted(ARCH))
    p.add_argument("--suffix-template", required=True)
    p.add_argument("--alphas", help="single-alpha LOSO mode (A37): comma list; "
                                    "mutually exclusive with --am/--aa")
    p.add_argument("--am")
    p.add_argument("--aa")
    p.add_argument("--seeds", default="0,1,2")
    p.add_argument("--jobs", type=int, default=1)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--skip-integrity", action="store_true")
    args = p.parse_args()
    cfg = ARCH[args.arch]
    single = args.alphas is not None
    if single == bool(args.am or args.aa):
        p.error("use either --alphas (single-α) or --am AND --aa (two-α)")
    if not single and not (args.am and args.aa):
        p.error("--am and --aa must both be given")
    AM = [float(x) for x in (args.alphas if single else args.am).split(",")]
    AA = [float(x) for x in args.aa.split(",")] if not single else []
    seeds = [int(s) for s in args.seeds.split(",")]
    st = args.suffix_template
    os.makedirs(args.out_dir, exist_ok=True)

    if cfg.get("needs_official") and not os.environ.get("FH_OFFICIAL_SEQMAP"):
        sys.exit("fh_v1 requires FH_OFFICIAL_SEQMAP (official 150-expr protocol, A31)")

    if single:
        return single_alpha_loso(cfg, args, AM, seeds, st)

    # (1) integrity gates — halt condition: no alpha>0 data may be read on fail
    if not args.skip_integrity:
        s0 = seeds[0]
        a0 = run_single(cfg, s0, 0.0, st)
        if a0 is None or abs(a0["pooled"] - cfg["native"]) > 5e-4:
            print(f"NATIVE GATE FAIL: alpha=0 pooled={a0 and a0['pooled']} "
                  f"expected {cfg['native']}")
            sys.exit(1)
        print(f"native gate OK: alpha=0 pooled == {a0['pooled']}", flush=True)
        ref = run_single(cfg, s0, cfg["diag"], st)
        diag = run_two(cfg, s0, cfg["diag"], cfg["diag"], st)
        if ref is None or diag is None or abs(diag["pooled"] - ref["pooled"]) > 1e-9:
            print(f"DIAGONAL GATE FAIL diag={diag and diag['pooled']} "
                  f"ref={ref and ref['pooled']}")
            sys.exit(1)
        print(f"integrity OK: diagonal {cfg['diag']}/{cfg['diag']} == "
              f"alpha{cfg['diag']} == {ref['pooled']}", flush=True)

    # (2) LOSO fold sweep, pooled only
    cells = [(fname, infold, am, aa, s)
             for fname, infold in cfg["folds"].items()
             for am, aa in itertools.product(AM, AA)
             for s in seeds]

    def worker(c):
        fname, infold, am, aa, s = c
        r = run_two(cfg, s, am, aa, st, eval_seqs=infold)
        print(f"{fname} am={am} aa={aa} seed={s} {'done' if r else 'FAIL'}", flush=True)
        return (fname, am, aa, s, r)

    fold_rows = []
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        for fname, am, aa, s, r in ex.map(worker, cells):
            if r:
                fold_rows.append(dict(fold=fname, am=am, aa=aa, seed=s,
                                      pooled=r["pooled"]))

    # (3) selection: per-fold argmax of mean pooled -> componentwise median
    argmaxes = {}
    for fname in cfg["folds"]:
        best, best_cell = -1, None
        for am, aa in itertools.product(AM, AA):
            vals = [r["pooled"] for r in fold_rows
                    if r["fold"] == fname and r["am"] == am and r["aa"] == aa]
            if vals and statistics.mean(vals) > best:
                best, best_cell = statistics.mean(vals), (am, aa)
        argmaxes[fname] = dict(cell=best_cell, pooled=round(best, 3))

    def sel(axis_vals, idx, gridmax):
        unc = [argmaxes[f]["cell"][idx] for f in cfg["folds"]
               if argmaxes[f]["cell"][idx] != gridmax]
        if len(unc) < 2:
            return None  # axis unresolved per pre-reg
        m = statistics.median(sorted(unc))
        # median between grid points -> lower grid point (pre-reg)
        return m if m in axis_vals else max(v for v in axis_vals if v < m)
    am_star = sel(AM, 0, max(AM))
    aa_star = sel(AA, 1, max(AA))

    out = {"arch": args.arch, "suffix_template": st, "grid_am": AM, "grid_aa": AA,
           "native_ref": cfg["native"], "diag_alpha": cfg["diag"],
           "official_seqmap": os.environ.get("FH_OFFICIAL_SEQMAP"),
           "fold_argmaxes": argmaxes, "am_star": am_star, "aa_star": aa_star,
           "fold_rows": fold_rows}
    # (4) full-test at selected point
    if am_star is not None and aa_star is not None:
        full = [run_two(cfg, s, am_star, aa_star, st) for s in seeds]
        full = [r for r in full if r]
        agg = {}
        for m in ("pooled", "moving", "static", "appearance"):
            vals = [r[m] for r in full if r.get(m) is not None]
            agg[f"{m}_mean"] = round(statistics.mean(vals), 3) if vals else None
            agg[f"{m}_std"] = round(statistics.stdev(vals), 3) if len(vals) > 1 else 0.0
        out["full_test_at_star"] = {"per_seed": full, "aggregate": agg}
        print("FULL-TEST @", (am_star, aa_star), agg, flush=True)
    else:
        print("AXIS UNRESOLVED:", "am" if am_star is None else "",
              "aa" if aa_star is None else "", flush=True)

    json.dump(out, open(os.path.join(args.out_dir, "two_alpha_campaign.json"), "w"),
              indent=1)
    print("TWO_ALPHA_DONE", flush=True)


if __name__ == "__main__":
    main()
