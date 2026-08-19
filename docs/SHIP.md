# SHIP.md — canonical results, locked recipes, exact commands

> **SUPERSEDED 2026-08-19.** The current shipped configuration is **Option B** (road-plane ego chain on all three host settings; iKUN two-α 0.7/0.1, FlexHook single α). See `CLAUDE.md` → Current ship, `docs/SHIP_DECISION_2026_08_16.md`, and RESEARCH_NOTES §10 A22–A36. Everything below is kept for provenance and is NOT the current recipe.

Extracted from CLAUDE.md 2026-07-05 (source of truth alongside memory
`project_ship_adoption_sw_recipe_noema_2026_05_21`). If this file and a memory
file disagree, memory wins — flag the conflict to the user.

## Key result (2026-05-21 ship)

3-arch cross-validation, n=3 multi-seed, 3-seq pooled HOTA on V1 (V2 = 4-seq
pooled). Shared-weight (sw) aligner + per-arch linear additive fusion
(raw cos, no EMA):

| Arch | Ship (n=3) | vs paper | B2 anchor (sw + simple fusion) |
|---|---|---|---|
| iKUN | 44.634 ± 0.066 | +0.070 (paper 44.564) | 44.272 |
| FlexHook V1 | 53.526 ± 0.087 | paper-gap structural | 53.121 |
| FlexHook V2 | 42.807 ± 0.038 | +0.281 (paper 42.526) | 42.532 |

Paper-beat 2/3. Historical +8.4% F1 result (learned MLP fusion head) is NOT
ship — it crashed HOTA (−3.79 pooled). Defense against "tuned on test":
LOSO calibration check, memory `project_loso_calibration_transfer_2026_07_04`
(iKUN MOVING ~88% survives out-of-fold).

## Locked recipes (do NOT retune without user approval)

Formula per arch per axis: `final = model_logit + α · (sc · raw_cos + thr)`

| Arch | Motion axis | Appearance axis |
|---|---|---|
| iKUN | α=1.0, sc=0.9, thr=+0.17 | α=1.0, sc=0.30, thr=+0.10 |
| FH V1 | α=0.65, sc=10, thr=+3.0 | α=1.0, sc=3.5, thr=+0.9 |
| FH V2 | α=0.4, sc=10, thr=+1.3 | α=1.0, sc=3.5, thr=+1.2 |

Why sc_appear is 7–11× smaller than sc_motion: GMC is a motion signal and is
noise on appearance expressions ("black cars"); hand-tuned damping suppresses
it. Auto-deriving sc via std-matching was falsified (variant B, NEG all 3
archs). Axis chosen per expression by ~38 motion keywords (moving, turning,
parking, ...).

## Training (ship aligner)

```bash
# shared_weight aligner (ship arch), seeds 0/1/2
for s in 0 1 2; do
  python -m gmc_link.train --split v1 --stage 1 \
      --architecture shared_weight --seed $s \
      --save-path gmc_link_weights_v1train_sharedweight_seed${s}.pth
done

# legacy mlp arch (code default; pre-2026-05-21 ship)
python -m gmc_link.train --split v1 --stage 1 --architecture mlp
```

## Build GMC caches (per arch, per seed)

Raw cosine, no EMA — GMC_RAW_COS=1 is REQUIRED, omitting it silently changes
scores.

```bash
GMC_WEIGHTS=gmc_link_weights_v1train_sharedweight_seed0.pth \
GMC_SUFFIX=_sharedweight_seed0_rawcos GMC_RAW_COS=1 \
    python run_build_gmc_cache.py 0005            # iKUN
GMC_WEIGHTS=... GMC_SUFFIX=... GMC_RAW_COS=1 \
    python run_build_gmc_cache_flexhook.py 0005   # FH V1
GMC_WEIGHTS=... GMC_SUFFIX=... GMC_RAW_COS=1 \
    python run_build_gmc_cache_flexhook_v2_raw.py 0005  # FH V2
```

## Ship HOTA eval (n=3 seeds, locked recipes)

```bash
GMC_SUFFIX=_sharedweight_seed${N}_rawcos GMC_RAW_COS=1 \
    python run_ikun_linear_additive.py \
        --alpha 1.0 --gmc_scale 0.9  --thr 0.17 \
        --alpha_appear 1.0 --gmc_scale_appear 0.30 --thr_appear 0.10

GMC_SUFFIX=_sharedweight_seed${N}_rawcos GMC_RAW_COS=1 \
    python run_flexhook_phase5_gmc_sweep.py \
        --alpha 0.65 --gmc_scale 10.0 --thr 3.0 \
        --alpha_appear 1.0 --gmc_scale_appear 3.5 --thr_appear 0.9

GMC_SUFFIX=_sharedweight_seed${N}_rawcos GMC_RAW_COS=1 \
    python run_flexhook_v2_raw_sweep.py \
        --alpha 0.4 --gmc_scale 10.0 --thr 1.3 \
        --alpha_appear 1.0 --gmc_scale_appear 3.5 --thr_appear 1.2
```

## Ablations

NOTE (2026-07-05): the old CLAUDE.md cited `run_ablation_study.py` and
`run_ablation_proper.sh`, but neither exists in the repo anymore — do not try
to run them. Canonical ablation result stands in memory:
MOVING-class ablation (n=5, 2026-07-04): module +8.83; ego −1.77 p=0.006
SIGNIFICANT; multiscale/snr within noise
(`project_ablation_moving_hota_n3_2026_06_24`). To rerun ablations, ask the
user which script replaced them (results archive: video/ablation/ABLATION_RESULTS.md).

## Reporting requirements (user's hard rules)

- Every number: exact recipe + n + std. Table labels never "ours"/"baseline".
- Always Δ vs BOTH baselines: B2 anchor AND ship.
- Report pooled AND per-class (STATIC/MOVING); pooled hides catastrophes
  (cascade MOVING=1.55 vs STATIC=47.23 incident).
- Braking-separation canary: ship keeps ≥ +0.35, below = regression.
