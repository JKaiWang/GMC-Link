#!/bin/bash
# Phase 4: LOSO alpha selection. Per fold: leave one seq out, sweep alpha on
# the rest (n=3 seeds). alpha* = median of per-fold pooled-best alphas.
set -euo pipefail
cd /home/seanachan/GMC-Link
L=logs/12d

IKUN_ALPHAS=0,0.1,0.2,0.3,0.5,0.7,1.0
FH_ALPHAS=0,1,2,3,5,7,10

for HOLD in 0005 0011 0013; do
  INFOLD=$(echo "0005,0011,0013" | tr ',' '\n' | grep -v $HOLD | paste -sd,)
  GMC_EVAL_SEQS=$INFOLD python run_alpha_sweep.py --arch ikun \
      --alphas $IKUN_ALPHAS --out-dir results/loso_ikun_hold${HOLD} \
      > $L/loso_ikun_hold${HOLD}.log 2>&1
  echo "loso ikun hold=$HOLD done"
  GMC_EVAL_SEQS=$INFOLD python run_alpha_sweep.py --arch fh_v1 \
      --alphas $FH_ALPHAS --out-dir results/loso_fh_v1_hold${HOLD} \
      > $L/loso_fhv1_hold${HOLD}.log 2>&1
  echo "loso fh_v1 hold=$HOLD done"
done

for HOLD in 0005 0011 0013 0019; do
  INFOLD=$(echo "0005,0011,0013,0019" | tr ',' '\n' | grep -v $HOLD | paste -sd,)
  GMC_EVAL_SEQS=$INFOLD python run_alpha_sweep.py --arch fh_v2 \
      --alphas $FH_ALPHAS --out-dir results/loso_fh_v2_hold${HOLD} \
      > $L/loso_fhv2_hold${HOLD}.log 2>&1
  echo "loso fh_v2 hold=$HOLD done"
done

echo "=== PHASE 4 LOSO COMPLETE ==="
for d in results/loso_*; do
  echo "--- $d ---"
  cat $d/alpha_sweep_*.csv 2>/dev/null | head -9
done
