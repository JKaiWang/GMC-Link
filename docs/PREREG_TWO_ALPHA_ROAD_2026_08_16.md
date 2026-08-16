# PRE-REGISTRATION — two-α keyword-routed fusion × road caches (Track C1)

Registered 2026-08-16 before any 2D-grid number exists. User authorized
(professor-gate waived by user 2026-08-16). LATER-3 lineage; prior warning
acknowledged: per-axis LOSO refit precedent 44.316 < single-α 44.512 (old
recipe form) — outcome recorded either way.

## Motivation

A25/A27/A28/A29: road arm has real, distributed MOVING headroom
(+1.5~3.1 at fixed α; signal repair on 0011) that single-α LOSO cannot select
(per-seq α spread). Two-α is per-CLASS routing (not per-seq) — LOSO-able with
3 folds — and per-class optima diverge measurably (APPEAR peaks α≈0.2-0.35,
MOVING/STATIC ≥0.5). The untested 1-vs-18 middle ground.

## Fusion + routing rule

s_final = s_host + α(expr)·s_gmc, gate 0.0, where
α(expr) = **α_mot** if `classify(expr)` ∈ {MOVING, STATIC} else **α_app**
(APPEARANCE). Router = existing keyword `classify()` in
`run_ikun_linear_additive.py` (string match, no learned component).
α_mot = α_app = a must reproduce the single-α run at a EXACTLY
(diagonal integrity check, verified before the campaign at a=0.5 on seed0).

## Arms & grids (n=3 seeds each; iKUN only)

- **Primary: road caches** `_sw12d_groad_seed{s}_warm11` — full grid
  α_mot ∈ {0.3, 0.5, 0.7, 1.0, 1.5, 2.0} × α_app ∈ {0.1, 0.2, 0.35, 0.5, 0.7}
  (30 cells).
- **Control: sim caches** `_sw12d_seed{s}_nomema_sim_warm11` — coarse grid
  α_mot ∈ {0.5, 1.0, 1.5} × α_app ∈ {0.2, 0.35, 0.5} (9 cells) — answers
  "is two-α itself the unlock, or the road×two-α combination".

## LOSO selection (pre-registered)

- 3 folds (hold 0005/0011/0013); per-fold argmax of in-fold pooled over the
  2D grid; (α_mot\*, α_app\*) = component-wise median over folds.
- Censoring per axis: a fold's component is censored iff it sits at that
  axis's grid max (2.0 / 0.7). Median over uncensored components per axis;
  if ≥2 folds censored on an axis → that axis unresolved, campaign reports
  "peak unresolved" for it (no cherry-pick).
- Full-test at (α_mot\*, α_app\*), n=3, pooled + per-class.

## Gates & baselines (fixed now)

- Baseline: candidate ship single-α 44.656±0.078 @0.5 (sim arm LOSO-honest).
- SUCCESS: full-test pooled at road-(α_mot\*, α_app\*) ≥ 44.656 − 2σ AND
  MOVING > 30.045; upgrade ship recommendation only if pooled > 44.656 + 2σ
  (report either way, user+professor still own adoption).
- α_mot=α_app diagonal cells double as single-α replication (integrity).
- α=0 ≡ 44.224 exact (fold and full-test).

## Outputs

`results/two_alpha_road/` (full-test grid + LOSO folds + summary),
`results/two_alpha_sim/` (control). Ledger row on completion.
