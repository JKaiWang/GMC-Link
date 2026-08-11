#!/bin/bash
# Phase 5: iKUN ablation, n=5, MOVING-class HOTA, eval at alpha*=0.5.
# full: seeds 0-2 reuse Phase 1/2 weights+caches (eval rows already in sweep
# JSON at alpha 0.5); train/cache only seeds 3-4, then eval them.
# noego (GMC_RAWVEL=1) / nomulti (GMC_GAPS=5,5,5): full train+cache+eval x5.
set -euo pipefail
cd /home/seanachan/GMC-Link
L=logs/12d
ALPHA=0.5

train_cache_eval () {  # CFG ENVSTR SEED (env applies to train + cache build)
  local CFG=$1 ENVSTR=$2 s=$3
  local W=gmc_link_weights_v1train_sw12d_${CFG}_seed${s}.pth
  local SFX=_sw12d_${CFG}_seed${s}
  env $ENVSTR python -m gmc_link.train --split v1 --stage 1 \
      --architecture shared_weight --seed $s --save-path $W \
      > $L/abl_train_${CFG}_seed${s}.log 2>&1
  env $ENVSTR GMC_WEIGHTS=$W GMC_SUFFIX=$SFX python run_build_gmc_cache.py \
      > $L/abl_cache_${CFG}_seed${s}.log 2>&1
  GMC_SUFFIX=$SFX OUT_SUFFIX=$SFX python run_ikun_linear_additive.py --alpha $ALPHA \
      > $L/abl_eval_${CFG}_seed${s}.log 2>&1
  echo "$CFG seed $s done"
}

# full config, extra seeds 3-4 (plain env)
for s in 3 4; do
  W=gmc_link_weights_v1train_sw12d_seed${s}.pth   # trained in Phase 1 already
  SFX=_sw12d_seed${s}
  GMC_WEIGHTS=$W GMC_SUFFIX=$SFX python run_build_gmc_cache.py \
      > $L/abl_cache_full_seed${s}.log 2>&1
  GMC_SUFFIX=$SFX OUT_SUFFIX=$SFX python run_ikun_linear_additive.py --alpha $ALPHA \
      > $L/abl_eval_full_seed${s}.log 2>&1
  echo "full seed $s done"
done

for s in 0 1 2 3 4; do train_cache_eval noego   "GMC_RAWVEL=1" $s; done
for s in 0 1 2 3 4; do train_cache_eval nomulti "GMC_GAPS=5,5,5" $s; done

echo "=== PHASE 5 COMPLETE ==="
python - << 'EOF'
import json, glob, statistics
def collect(pattern):
    vals = []
    for p in sorted(glob.glob(pattern)):
        r = json.load(open(p))
        vals.append((r["moving"], r["pooled"]))
    return vals
groups = {
    "full":    "hota_eval_ikun_linear_additive_sw12d_seed[0-4]/alpha0.5/result.json",
    "noego":   "hota_eval_ikun_linear_additive_sw12d_noego_seed*/alpha0.5/result.json",
    "nomulti": "hota_eval_ikun_linear_additive_sw12d_nomulti_seed*/alpha0.5/result.json",
}
print(f"{'config':<10} {'n':>2} {'MOVING':>16} {'pooled':>16}")
for name, pat in groups.items():
    vals = collect(pat)
    if not vals: print(f"{name:<10} MISSING"); continue
    mv = [v[0] for v in vals]; pl = [v[1] for v in vals]
    f = lambda xs: f"{statistics.mean(xs):.3f}±{statistics.stdev(xs):.3f}" if len(xs)>1 else f"{xs[0]:.3f}"
    print(f"{name:<10} {len(vals):>2} {f(mv):>16} {f(pl):>16}")
print("native (alpha=0): MOVING 25.531, pooled 44.224")
EOF
