# PRE-REGISTRATION — FH V1 official-seqmap re-evaluation (Track A)

Registered 2026-08-16, committed before any re-scored number is read.

## Finding being acted on (2026-08-16 exploration)

The FH V1 "structural reproduction gap" (53.110 vs published 53.824) is an
EVAL-LIST mismatch, not model or pipeline drift:
- Our pipeline already consumes the strongest official config's scores
  (rope-swin-tiny + roberta, `SOTA_ckpts/refer-kitti-best.pth`,
  Temp-NeuralSORT tracks) — verified from `retest-kitti-1/.../config.json`.
- Our α=0 predicts are byte-identical to FlexHook's native outputs (158/158
  predict.txt AND gt.txt).
- Our seqmap enumerates 158 expressions; the official
  `~/FlexHook/seqmaps/kitti-1.txt` has 150. The 8 extras (verified):
  0005 {cars,vehicles}-which-are-braking; 0011 {cars,vehicles}-in-horizon-direction;
  0013 {females,males,men,women}-back-to-the-camera — degenerate GT
  (e.g. gt 12 rows vs pred 244-395).
- Control: V2 seqmap is set-identical to official (862=862) and reproduces
  the shipped 42.526 exactly. The only list-mismatched cell is the only
  "gapped" cell.

## Protocol

- Evaluation list = official 150-expression seqmap (48/62/40 per seq),
  copied verbatim from `~/FlexHook/seqmaps/kitti-1.txt`.
- Re-run TrackEval ONLY (existing predict trees untouched) for:
  - candidate ship arm `hota_eval_flexhook_phase5_gmc_sw12d_seed{0,1,2}_nomema_warm11`,
    all 7 α full-test tags + 21 fold tags (`*_seqs*`),
  - groad arm `..._sw12d_groad_seed{0,1,2}_warm11`, same tags.
- Full-test tags: pooled + MOVING/STATIC/APPEARANCE
  (class filter = `run_flexhook_phase5_gmc_sweep.classify` on the official list).
  Fold tags: pooled only (LOSO selection metric).
- Output: `results/fh_v1_official/` (sweep JSON/CSV per arm + LOSO summary).

## Integrity gate (halt condition)

α=0 pooled on the official list must equal **53.824 ± 0.01** (FlexHook's own
`infer.sh` recorded reproduction; the paper's 53.83 is flagged there as a typo).
If outside tolerance: STOP, investigate residual cause before reading any α>0.

## Selection rule

LOSO α\* = median of per-fold pooled argmaxes over uncensored folds
(censored = argmax at grid max 10), identical to prior FH protocol.

## Interpretation (pre-registered)

- Expected: near-uniform upward level shift (~+0.7) at all α; Δ(GMC − native)
  approximately preserved. Report new native, new ship-α numbers, new Δ, new α\*.
- The old "structural cli-fork gap" conclusions (docs/COMPARISON.md,
  RESEARCH_NOTES §7) become SUPERSEDED — mark, don't delete.
- Paper consequence (number-pack only, no tex edits): FH V1 row becomes
  official-protocol-comparable; reproduction-gap disclaimer replaced by
  "evaluated on the host's official 150-expression protocol".

## Repair rider

Our 2026-05-01 STATIC-filtered run clobbered
`~/FlexHook/retest-kitti-1/refer-kitti-best/results/pedestrian_summary.txt`
(now holds a 12-expression subset run). Restore by re-running TrackEval there
with the full official seqmap. Guard: our eval scripts must never write into
`~/FlexHook` paths.
