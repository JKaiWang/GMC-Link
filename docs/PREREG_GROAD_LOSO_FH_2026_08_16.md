# PRE-REGISTRATION — ground-road LOSO (iKUN) + FH V1/V2 confirmation arms

Registered 2026-08-15 night (user-ordered), committed BEFORE any result exists.
Follows A25 (road-chain attribution). Weights: existing `_sw12d_groad_seed{0,1,2}`.

## Part 1 — ground-road iKUN LOSO (dense grid, A24 protocol)

- Caches `_sw12d_groad_seed{s}_warm11` (exist). UNION 16-α grid
  {0,0.1,0.2,0.3,0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7,1.0,1.25,1.5,2.0}.
- 3 folds (hold 0005/0011/0013, tune in-fold pooled, n=3) →
  `results/ground_road/loso_ikun_hold*`; full-test union sweep supersedes the
  7-point `results/ground_road/alpha_sweep_ikun.*` with the 16-point superset.
- Selection rule = A24's: α\* = median of per-fold pooled-argmaxes over
  uncensored folds (censored iff argmax = 2.0); ≥2 censored → peak unresolved,
  no α\* from this run. Even-median → lower grid point.
- Report full-test pooled + per-class at α\*, Δ vs sim ship 44.656±0.078 @0.5
  and vs native 44.224. α=0 ≡ 44.224 exactly.

## Part 2 — FH V1/V2 ground-road confirmation

- Motivation: ship consistency — if iKUN adopts the road chain, FH caches carry
  the same mechanism; must not regress (A13 protocol). Prior: FH+ego NEG
  (`project_fh_ego_lean_v2_negative_2026_06_04`), inverse law ⇒ EXPECTED FLAT.
- Build: `run_build_gmc_cache_flexhook.py` (V1) + `run_build_gmc_cache_flexhook_v2_raw.py`
  (V2), env `GMC_GROUND_MODE=road GMC_MODEL=similarity GMC_MOTION_EMA=0`,
  weights `_sw12d_groad_seed{s}`, suffix `_sw12d_groad_seed{s}`; warm11 filter;
  sweeps α ∈ {0,1,2,3,5,7,10} → `results/ground_road_fh_v1/`, `results/ground_road_fh_v2/`.
- Baselines (candidate ship, nomema_warm11 + global homography chain):
  FH V1 53.246±0.008 @5; FH V2 42.658±0.030 @5. Natives at α=0: 53.110 / 42.526
  exactly (integrity check).
- Gate (pre-registered): per arch, at that arch's best α — REGRESSION iff
  pooled Δ < 0 with Welch t > 2 (n=3); otherwise NON-INFERIOR (report Δ ± t).
  Report per-class rows; V2 rows are slug-grouped (canonical regroup deferred —
  run_v2_canonical_regroup.py needs regenerated predicts, separate step if V2
  changes materially).
- Note: baseline chain is homography-global (sim-arm FH caches were never
  built, A13); this comparison is the decision-relevant one — candidate ship
  FH vs road FH.

## Decision scope

No ship adoption from this campaign. Output = complete evidence pack for
user+professor: iKUN road α\* + full-test numbers, FH non-inferiority verdicts.
No further GPU beyond this queue without user say-so.
