"""Warmup validity mask (audit A3, DO-NOW 3 in docs/IMPROVEMENT_PLAN_2026_08_13.md).

Deletes GMC cache entries whose contiguous track history T <= max(FRAME_GAPS)=10,
i.e. exactly where the long-gap residual-velocity feature is undefined (and the
early frames are zero-padded "stationary"-coded garbage). All three fusion
consumers default missing entries to gmc=0.0, so filtered entries fuse as
s_final = s_host — GMC abstains where its features are undefined. Zero new
hyperparameters; threshold fixed by the feature definition.

Manager bookkeeping is replayed from the cache's own (fid, oid) grid: motion
vectors are expression-independent, so the union grid over expressions equals
the processed-frame/track presence; a track absent in one processed frame is
deleted by the manager (dead-track deletion), which resets T.

Usage:
    python filter_warmup_cache.py --seeds 0,1,2          # all archs
    python filter_warmup_cache.py --archs ikun --seeds 0
Writes gmc_scores_*_{suffix}_warm11_cache.json next to the inputs.
"""
import argparse
import json
import os

GMC_DIR = "/home/seanachan/GMC-Link/gmc_link"
T_MIN = 11  # keep iff contiguous history T >= T_MIN (> max FRAME_GAPS = 10)

ARCHS = {
    "ikun":  ("gmc_scores_v1_{seq}{sfx}_cache.json",              ["0005", "0011", "0013"]),
    "fh_v1": ("gmc_scores_flexhook_v1_{seq}{sfx}_cache.json",     ["0005", "0011", "0013"]),
    "fh_v2": ("gmc_scores_flexhook_v2_raw_{seq}{sfx}_cache.json", ["0005", "0011", "0013", "0019"]),
}


def filter_cache(path_in, path_out):
    cache = json.load(open(path_in))
    # union (fid, oid) grid across expressions
    fids = sorted({int(f) for expr in cache.values() for f in expr}, key=int)
    present = {f: set() for f in fids}
    for expr in cache.values():
        for f, oids in expr.items():
            present[int(f)].update(oids.keys())
    # replay manager history: +1 while present in consecutive processed frames,
    # reset on absence (dead-track deletion)
    T = {}
    valid = set()  # (fid, oid) with T >= T_MIN
    for f in fids:
        oids = present[f]
        T = {o: T.get(o, 0) + 1 for o in oids}  # absent oids dropped = reset
        valid.update((f, o) for o in oids if T[o] >= T_MIN)
    kept, dropped = 0, 0
    out = {}
    for expr, frames in cache.items():
        oe = {}
        for f, oids in frames.items():
            fo = {o: s for o, s in oids.items() if (int(f), o) in valid}
            if fo:
                oe[f] = fo
            kept += len(fo)
            dropped += len(oids) - len(fo)
        out[expr] = oe
    json.dump(out, open(path_out, "w"))
    return kept, dropped


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--archs", default="ikun,fh_v1,fh_v2")
    p.add_argument("--seeds", default="0,1,2")
    p.add_argument("--in-suffix", default="_sw12d_seed{seed}")
    args = p.parse_args()

    for arch in args.archs.split(","):
        tpl, seqs = ARCHS[arch]
        for seed in args.seeds.split(","):
            sfx = args.in_suffix.format(seed=seed)
            for seq in seqs:
                pin = os.path.join(GMC_DIR, tpl.format(seq=seq, sfx=sfx))
                pout = os.path.join(GMC_DIR, tpl.format(seq=seq, sfx=sfx + "_warm11"))
                kept, dropped = filter_cache(pin, pout)
                tot = kept + dropped
                print(f"{arch} seed{seed} {seq}: kept {kept}/{tot} "
                      f"({dropped / tot:.1%} warmup dropped) -> {os.path.basename(pout)}")


if __name__ == "__main__":
    main()
