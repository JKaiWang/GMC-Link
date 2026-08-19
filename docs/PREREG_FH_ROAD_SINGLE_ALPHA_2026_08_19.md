# Pre-registration: FlexHook road-chain single-α LOSO (A37)

Committed BEFORE any fold data is generated. Date 2026-08-19.

## Motivation

Option B was locked 2026-08-19, and with it the decision to run **all three host settings on
the road-plane ego chain** so the paper describes one estimator. iKUN's α is already
LOSO-selected on that chain (A32). FlexHook's is not: the road-chain full-test α sweep exists
(A27/A31) but **no single-α fold runs exist for FlexHook on the road chain at all** — verified
by enumeration, every `alpha*_seqs*` directory in the repo belongs to the similarity chain.
Selecting α by reading the full-test sweep would be test-set tuning.

## Configuration

- Caches `_sw12d_groad_seed{0,1,2}_warm11` (road chain, warm11 mask, no motion EMA, raw cosine).
- FH V1 under the host's official 150-expression protocol (`FH_OFFICIAL_SEQMAP`, `_off150`
  output trees so official-list runs never mix with the 158-expression trees). Folds
  hold0005 / hold0011 / hold0013.
- FH V2, 862 expressions, folds hold0005 / hold0011 / hold0013 / hold0019.
- Grid α ∈ {0, 1, 2, 3, 5, 7, 10} — identical to the A27 sweep grid. Seeds 0, 1, 2.
- Fold runs record pooled HOTA only (selection uses pooled, as in A32/A35).

## Integrity gates (halt conditions)

α = 0 must reproduce the published natives exactly, in both the fold and full-test paths:
FH V1 (official list) **53.824**, FH V2 **42.526** (tolerance 5e-4). On failure: stop,
diagnose, read no α > 0 result.

## Selection rule

Per-fold pooled argmax → median over uncensored folds. A fold whose argmax sits at the grid
maximum (α = 10) is censored. Fewer than 2 uncensored folds → axis unresolved.
Median between grid points → the lower grid point.

## Frozen commitments (decided before seeing any fold number)

1. Report the full-test numbers at the LOSO-selected α **even if that α is not the argmax of
   the already-known full-test sweep**. The full-test grid was measured in A27/A31; this
   registration exists to select honestly, not to confirm a maximum.
2. If a host's axis is unresolved, that host **keeps the global similarity chain** and the
   paper states that the ego estimator is selected per host. No grid extension, no re-selection.
3. The full-test values must be the ones already on record
   (`results/fh_v1_official/fh_v1_official.json` groad arm; `results/ground_road_fh_v2/`).
   If a re-run disagrees with those, that is a defect to investigate, not a new number to adopt.

## Expected outcome (recorded for calibration, not a target)

The road-chain full-test peaks are V1 53.981 ± 0.043 @ α=5 (53.980 @ 7) and V2
42.625 ± 0.032 @ α=5, so folds are expected to select in the 3–7 range with low censoring
risk. Adopting the road chain costs about −0.03 on both FlexHook settings relative to the
similarity-chain values (V1 54.011, V2 42.658); both stay above native and above published.

## Tooling

`run_two_alpha_sweep.py` gains a single-α mode (`--alphas`), reusing its existing per-arch fold
definitions, `_off150` output isolation, integrity gate, and thread pool. `run_alpha_sweep.py`
is NOT used: it hard-codes `OUT_SUFFIX` to `GMC_SUFFIX`, so official-list fold results would be
written into the 158-expression trees.
