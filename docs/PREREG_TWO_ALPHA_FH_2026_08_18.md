# Pre-registration: FlexHook two-α × road-chain LOSO (A35) + FPS clean re-measure (A36)

Date: 2026-08-17 (runbook dated 08-18). Committed BEFORE any α>0 data is read.

## Motivation

iKUN adopted road × two-α (A32: pooled 44.847±0.107, t=2.50 over single-α ship;
sim×two-α control flat +0.016 → gain is the road×routing combination).
FlexHook V1/V2 are still sim + single-α (54.011 @α=7 official-150 / 42.658 @α=5).
Paper method must be measured consistently on all three hosts.

## Configuration

- Main arm: road-chain caches `_sw12d_groad_seed{0,1,2}_warm11` × keyword-routed two-α.
- Control arm (run only if main arm passes threshold): sim caches
  `_sw12d_seed{N}_nomema_warm11` × two-α (mirrors A32's sim control).
- FH V1 runs under the host's official 150-expression protocol
  (`FH_OFFICIAL_SEQMAP=~/FlexHook/seqmaps/kitti-1.txt`, A31), filtered at
  generation time; output trees isolated with `_off150` suffix so A27 158-expr
  trees are never clobbered. FH V2 list already official (862 = 862).

## Routing (frozen)

Router classifies the **canonical expression text** — V1: the `sentence` field;
V2: `raw_sentence` (fallback `sentence`) — with the V1 keyword lists in iKUN
order (= `run_v2_canonical_regroup.py` A30). Slug classification is void for
the method (A30); the slug-tuned `classify()` remains only for legacy per-class
rows. α_mot applies to MOVING+STATIC-classified expressions, α_app to
APPEARANCE. α_mot == α_app degenerates to single-α bit-exact.

Locked route counts: V1 official-150 = 25 MOVING / 12 STATIC / 113 APPEARANCE;
V2 = 136 / 93 / 633.

## Grids

- FH V1: α_mot ∈ {3,5,7,10,15} × α_app ∈ {0.5,1,2,3,5}; folds hold0005/0011/0013 (3).
- FH V2: α_mot ∈ {2,3,5,7,10} × α_app ∈ {0.5,1,2,3,5}; folds hold0005/0011/0013/0019 (4).
- Seeds 0,1,2. Fold evals record pooled only (selection uses pooled only, as A32).

## Integrity gates (halt conditions — on fail: stop, diagnose, read NO α>0 data)

1. α=0 must reproduce the published natives exactly: FH V1 (official list)
   **53.824**; FH V2 **42.526** (tolerance 5e-4; validates the generation-time
   official filter against A31's rescore result).
2. Diagonal α_mot=α_aa=α* must be **bit-exact** vs the single-α run at α* with
   the SAME caches and SAME eval list (V1: single-α refs regenerated under the
   official list inside `_off150` trees; V2: existing groad trees). This is the
   code-correctness gate for the new routing path; it is routing-independent.
   Note: the ship numbers 54.011/42.658 are sim-chain values and are the
   *adoption thresholds* below, not the diagonal reference.

## Selection rule (identical to A32)

LOSO per-fold pooled argmax → componentwise median. An axis whose fold-argmax
sits at that axis's grid max is censored for that fold. Fewer than 2 uncensored
folds on an axis → axis unresolved (`null`); median between grid points → lower
grid point.

## Adoption thresholds (pre-registered)

Full-test pooled must exceed the current single-α ship + 2σ:

| Host | current single-α ship | threshold |
|---|---|---|
| FH V1 (official 150) | 54.011 ± 0.025 (α=7) | **> 54.061** |
| FH V2 | 42.658 ± 0.030 (α=5) | **> 42.718** |

## If below threshold (frozen wording, no post-hoc choice)

Report that LOSO selected the diagonal / missed the threshold; the paper's
FlexHook rows stay single-α; the method section states "per-host LOSO selects
α_mot = α_app on FlexHook, degenerating to a single α." Honest and
method-consistent.

## A36: FPS clean re-measure

3 reps of `GMC_MODEL=similarity python profile_inference.py --seq 0011 --n 500`
on an otherwise idle machine, BEFORE the sweeps launch. Report the median of 3;
keep both `fps_process_only` and `fps_incl_io`; overwrite
`results/fps_profile.json`. Gate: dispersion across reps < 5%, else re-measure.
Replaces the under-load values (sim 48.0 / road 35.3) and the stale paper 68 FPS.
