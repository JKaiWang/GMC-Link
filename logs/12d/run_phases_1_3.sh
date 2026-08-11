#!/bin/bash
# Phases 1-3: retrain 12D (seeds 0-4) -> caches (3 hosts x seeds 0-2) -> alpha sweeps.
# Serial on purpose: single GPU. Logs land beside this script.
set -euo pipefail
cd /home/seanachan/GMC-Link
L=logs/12d

echo "=== PHASE 1: train sw12d seeds 0-4 ==="
for s in 0 1 2 3 4; do
  python -m gmc_link.train --split v1 --stage 1 \
      --architecture shared_weight --seed $s \
      --save-path gmc_link_weights_v1train_sw12d_seed${s}.pth \
      > $L/train_sw12d_seed${s}.log 2>&1
  echo "  seed $s done: $(tail -2 $L/train_sw12d_seed${s}.log | head -1)"
done

echo "=== PHASE 2: caches, 3 hosts x seeds 0-2 ==="
for s in 0 1 2; do
  W=gmc_link_weights_v1train_sw12d_seed${s}.pth
  SFX=_sw12d_seed${s}
  GMC_WEIGHTS=$W GMC_SUFFIX=$SFX python run_build_gmc_cache.py \
      > $L/cache_ikun_seed${s}.log 2>&1
  echo "  ikun seed $s cache done"
  GMC_WEIGHTS=$W GMC_SUFFIX=$SFX python run_build_gmc_cache_flexhook.py \
      > $L/cache_fhv1_seed${s}.log 2>&1
  echo "  fh_v1 seed $s cache done"
  GMC_WEIGHTS=$W GMC_SUFFIX=$SFX python run_build_gmc_cache_flexhook_v2_raw.py \
      > $L/cache_fhv2_seed${s}.log 2>&1
  echo "  fh_v2 seed $s cache done"
done

echo "=== PHASE 3: alpha sweeps ==="
python run_alpha_sweep.py --arch ikun  --alphas 0,0.1,0.2,0.3,0.5,0.7,1.0 \
    > $L/sweep_ikun.log 2>&1
echo "  ikun sweep done"
python run_alpha_sweep.py --arch fh_v1 --alphas 0,1,2,3,5,7,10 \
    > $L/sweep_fhv1.log 2>&1
echo "  fh_v1 sweep done"
python run_alpha_sweep.py --arch fh_v2 --alphas 0,1,2,3,5,7,10 \
    > $L/sweep_fhv2.log 2>&1
echo "  fh_v2 sweep done"

echo "=== PHASES 1-3 COMPLETE ==="
for a in ikun fh_v1 fh_v2; do
  echo "--- $a aggregate ---"
  cat results/alpha_sweep_${a}.csv
done
