"""Track C2: confidence-gated temporal calibration (TTC) on iKUN fused scores.
Pre-reg: docs/PREREG_TTC_CALIBRATION_2026_08_16.md
Single eval: --theta --w (+ env GMC_SUFFIX/OUT_SUFFIX/GMC_EVAL_SEQS as usual).
w=0 reproduces the plain alpha=0.5 ship run exactly."""
import argparse, json, math, os, shutil, sys
sys.path.insert(0, "/home/seanachan/GMC-Link")
sys.path.insert(0, "/home/seanachan/iKUN")
from run_ikun_linear_additive import (
    CASCADE_FULL, DATA_ROOT, FRAMES, GT_TEMPLATE, TEST_SEQS, TEXT_FEAT_JSON,
    compute_simcalib_bias, load_ikun_scores, merged_ns, run_te)

REPO = "/home/seanachan/GMC-Link"
ALPHA = 0.5  # candidate ship alpha (fixed; pre-reg)
GMC_CACHE_TPL = os.path.join(
    REPO, "gmc_link", "gmc_scores_v1_{seq}" + os.environ.get("GMC_SUFFIX", "") + "_cache.json")
OUT_ROOT = os.path.join(
    REPO, "hota_eval_ikun_ttc" + os.environ.get("OUT_SUFFIX", ""))

sigmoid = lambda x: 1.0 / (1.0 + math.exp(-x))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--theta", type=float, required=True)
    p.add_argument("--w", type=float, required=True)
    args = p.parse_args()

    text_feat = json.load(open(TEXT_FEAT_JSON))
    gmc_caches = {s: json.load(open(GMC_CACHE_TPL.format(seq=s))) for s in TEST_SEQS}

    tag = f"th{args.theta}_w{args.w}"
    if os.environ.get("GMC_EVAL_SEQS"):
        tag += "_seqs" + "-".join(TEST_SEQS)
    run_dir = os.path.join(OUT_ROOT, tag)
    res_dir = os.path.join(run_dir, "results")
    if os.path.exists(res_dir):
        shutil.rmtree(res_dir)
    os.makedirs(res_dir, exist_ok=True)
    seqmap_lines = []

    for seq in TEST_SEQS:
        ns = merged_ns(seq)
        expr_dir = os.path.join(DATA_ROOT, "expression", seq)
        exprs = sorted(f.replace(".json", "") for f in os.listdir(expr_dir)
                       if f.endswith(".json"))
        bias = compute_simcalib_bias(text_feat, exprs)
        gmc_seq = gmc_caches.get(seq, {})
        min_f, max_f = FRAMES[seq]

        for expr in exprs:
            outd = os.path.join(res_dir, seq, expr)
            os.makedirs(outd, exist_ok=True)
            gt_src = os.path.join(GT_TEMPLATE, seq, expr, "gt.txt")
            gt_dst = os.path.join(outd, "gt.txt")
            if os.path.exists(gt_src):
                shutil.copy2(gt_src, gt_dst)
            else:
                open(gt_dst, "w").close()
            seqmap_lines.append(f"{seq}+{expr}")

            ikun_scores = load_ikun_scores(CASCADE_FULL, seq, expr)
            b = bias.get(expr, 0.0)
            per_expr_gmc = gmc_seq.get(expr, {})

            # fused scores per (fid, oid), temporal order
            per_frame = []  # (fid, [(oid, x, y, w, h, fused)])
            for fid in sorted(ns.keys()):
                if not (min_f < fid < max_f):
                    continue
                dets = []
                for oid, x, y, w_, h in ns[fid]:
                    cs = ikun_scores.get(fid, {}).get(oid)
                    if cs is None:
                        continue
                    gmc = float(per_expr_gmc.get(str(fid), {}).get(str(oid), 0.0))
                    dets.append((oid, x, y, w_, h, cs + b + ALPHA * gmc))
                per_frame.append((fid, dets))

            # confidence-gated memory + positive-residual calibration (online)
            mem = {}  # oid -> stored score
            rows = []
            for fid, dets in per_frame:
                for oid, x, y, w_, h, r in dets:
                    m = mem.get(oid)
                    r_hat = r + args.w * max(m - r, 0.0) if m is not None else r
                    if sigmoid(r) >= args.theta:
                        mem[oid] = r
                    if r_hat > 0.0:
                        rows.append((fid, oid, x, y, w_, h))
            with open(os.path.join(outd, "predict.txt"), "w") as f:
                for fid, oid, x, y, w_, h in rows:
                    f.write(f"{fid},{oid},{x:.2f},{y:.2f},{w_:.2f},{h:.2f},1,1,1\n")

    sm = os.path.join(run_dir, "seqmap.txt")
    open(sm, "w").write("\n".join(seqmap_lines) + "\n")
    result = {
        "arch": "ikun_ttc", "alpha": ALPHA, "theta": args.theta, "w": args.w,
        "gmc_suffix": os.environ.get("GMC_SUFFIX", ""), "eval_seqs": TEST_SEQS,
        "pooled": run_te(sm, res_dir),
        "moving": run_te(sm, res_dir, class_filter="MOVING"),
        "static": run_te(sm, res_dir, class_filter="STATIC"),
        "appearance": run_te(sm, res_dir, class_filter="APPEARANCE"),
    }
    with open(os.path.join(run_dir, "result.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"  th={args.theta} w={args.w}  pooled={result['pooled']} "
          f"MOV={result['moving']}", flush=True)


if __name__ == "__main__":
    main()
