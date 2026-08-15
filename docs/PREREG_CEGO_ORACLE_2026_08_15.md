# PRE-REGISTRATION — matched-retrain oracle (A22 domain-shift objection test)

Registered 2026-08-15 (session tmp; user to commit), BEFORE any result exists.

## Challenge being adjudicated

User challenge: A22 (GT-feature oracle 44.549 ≈ ship 44.656) is inference
substitution — the aligner was trained with direct-estimate ego, oracle caches
use the composed similarity chain. If the aligner is "overfit to its training
noise", the oracle underestimates the true feature-quality ceiling and the
motion-line-closed verdict is unsafe.

Fact established first: training ALREADY uses GT centroid tracks
(`dataset.py` labels_with_ids) — the only train/oracle domain gaps are the ego
chain (direct vs composed-similarity) and ±2px jitter augmentation.

## Arm

- Existing cego weights `gmc_link_weights_v1train_sw12d_cego_seed{0,1,2}.pth`
  (A15: trained with GMC_TRAIN_COMPOSED_EGO=1 + GMC_MODEL=similarity — i.e.
  ego-domain-MATCHED to the oracle chain). No retraining.
- Oracle caches rebuilt with those weights: `build_oracle_motion_cache_cego.py`
  (sed variant of `build_oracle_motion_cache.py`, session tmp; only weight path
  + cache suffix changed), suffix `_sw12d_seed{seed}_cego_gtoracle`.
- Sweep α ∈ {0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0}, n=3 → `results/cego_gtoracle/`.
- α=0 must equal 44.224 exactly.

## Baselines (fixed now)

- Candidate ship (sim arm): 44.656±0.078 @0.5, MOVING 30.045±0.091.
- Inference-substitution oracle (A22): 44.549±0.052 @0.5, MOVING@1.0 32.264±0.835.
- cego on REAL NS caches (A15): 44.453±0.045 @0.3 (NEG) — cego aligner is not
  secretly stronger; this cell isolates eval-side domain match only.

## Interpretation rule (pre-registered)

- Peak pooled ≤ ship + 2σ (≈ 44.81): domain-shift objection FALSIFIED —
  A22 verdict sealed; record as ledger row, motion line stays closed.
- Peak pooled > ship + 2σ: A22 verdict REOPENED — feature-quality ceiling was
  underestimated; flag to user BEFORE any further conclusion; tracker-noise /
  clean-feature levers return to the live list.
- Either way: no ship change from this run (diagnostic only).
