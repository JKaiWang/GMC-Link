# Experiment Commands — 12D / single-α ship (2026-08-10)

Every command here is reproducible as written. Run inside tmux; single GPU —
never two train/cache jobs at once. All logs → `logs/12d/`.

Context: ρ (code name `snr`, slot 12) removed from the motion feature
(13D→12D); fusion simplified to `s_final = s_host + α·s_gmc` with the
detection gate frozen at the native value 0.0 for all three hosts, so
**α=0 reproduces each reproduced-native baseline exactly**. s_gmc = raw
cosine ∈ [−1,+1] (cache builders emit raw cos unconditionally now).

Reference numbers (pre-change, for α=0 verification):
| host | published | reproduced native (α=0 target) |
|---|---|---|
| iKUN (cascade+simcalib) | 44.564 | 44.224 |
| FlexHook V1 | 53.824 | 53.110 |
| FlexHook V2 | 42.526 | 42.526 |

```bash
mkdir -p logs/12d
```

## Phase 0 — sanity: α=0 must reproduce native (CPU, ~5 min)

Uses any existing cache file for the suffix (values are ×0 at α=0). Run with
the first new-trained seed's caches once Phase 2 is done, or point GMC_SUFFIX
at an old 13D rawcos cache purely for the α=0 check.

```bash
GMC_SUFFIX=_sharedweight_seed0_rawcos python run_ikun_linear_additive.py --alpha 0 \
    2>&1 | tee logs/12d/sanity_alpha0_ikun.log          # expect pooled = 44.224
GMC_SUFFIX=_sharedweight_seed0_rawcos python run_flexhook_phase5_gmc_sweep.py --alpha 0 \
    2>&1 | tee logs/12d/sanity_alpha0_fhv1.log          # expect pooled = 53.110
GMC_SUFFIX=_sharedweight_seed0_rawcos python run_flexhook_v2_raw_sweep.py --alpha 0 \
    2>&1 | tee logs/12d/sanity_alpha0_fhv2.log          # expect pooled = 42.526
```

## Phase 1 — retrain 12D aligner (ship arch, seeds 0–4; ~3 min each)

Seeds 0–2 = main tables (n=3). Seeds 3–4 only needed for the n=5 ablation.

```bash
for s in 0 1 2 3 4; do
  python -m gmc_link.train --split v1 --stage 1 \
      --architecture shared_weight --seed $s \
      --save-path gmc_link_weights_v1train_sw12d_seed${s}.pth \
      2>&1 | tee logs/12d/train_sw12d_seed${s}.log
done
```

## Phase 2 — build GMC caches (3 hosts × seeds 0–2; ~20–30 min per host-seed)

Raw cosine is the only output mode (no GMC_RAW_COS needed anymore).

```bash
for s in 0 1 2; do
  W=gmc_link_weights_v1train_sw12d_seed${s}.pth
  SFX=_sw12d_seed${s}
  GMC_WEIGHTS=$W GMC_SUFFIX=$SFX python run_build_gmc_cache.py \
      2>&1 | tee logs/12d/cache_ikun_seed${s}.log
  GMC_WEIGHTS=$W GMC_SUFFIX=$SFX python run_build_gmc_cache_flexhook.py \
      2>&1 | tee logs/12d/cache_fhv1_seed${s}.log
  GMC_WEIGHTS=$W GMC_SUFFIX=$SFX python run_build_gmc_cache_flexhook_v2_raw.py \
      2>&1 | tee logs/12d/cache_fhv2_seed${s}.log
done
```

## Phase 3 — α sweep (eval-only, CPU TrackEval; ~1 min per point)

Grids: iKUN host score ∈ [0,1] → fine grid; FlexHook logits ∈ [−10,+10] → ×10 grid.

```bash
python run_alpha_sweep.py --arch ikun  --alphas 0,0.1,0.2,0.3,0.5,0.7,1.0 \
    2>&1 | tee logs/12d/sweep_ikun.log
python run_alpha_sweep.py --arch fh_v1 --alphas 0,1,2,3,5,7,10 \
    2>&1 | tee logs/12d/sweep_fhv1.log
python run_alpha_sweep.py --arch fh_v2 --alphas 0,1,2,3,5,7,10 \
    2>&1 | tee logs/12d/sweep_fhv2.log
```

Outputs: `results/alpha_sweep_{ikun,fh_v1,fh_v2}.{csv,json}` (per-seed rows +
mean±std per α; pooled / MOVING / STATIC / APPEARANCE).

## Phase 4 — LOSO α selection (per arch)

For each fold: leave one sequence out, sweep α on the remaining seqs, pick the
pooled-best α; final α* = median over folds; report full-test numbers at α*.
`GMC_EVAL_SEQS` restricts the eval to the fold's sequences.

```bash
# V1 hosts (3 folds). Repeat per arch: ikun, fh_v1.
for HOLD in 0005 0011 0013; do
  INFOLD=$(echo "0005,0011,0013" | tr ',' '\n' | grep -v $HOLD | paste -sd,)
  GMC_EVAL_SEQS=$INFOLD python run_alpha_sweep.py --arch ikun \
      --alphas 0,0.1,0.2,0.3,0.5,0.7,1.0 \
      --out-dir results/loso_ikun_hold${HOLD} \
      2>&1 | tee logs/12d/loso_ikun_hold${HOLD}.log
done
# fh_v2: 4 folds over 0005,0011,0013,0019 with --alphas 0,1,2,3,5,7,10

# C-lite (extra defense, zero cost): report fh_v2 at the α* selected on V1
# (scaled grid) — 0019 and the V2 paraphrases never participated in selection.
```

## Phase 5 — ablation (iKUN, MOVING-class HOTA, n=5, per-config retrain)

Rows: native (α=0, free) / full 12D / −ego (GMC_RAWVEL=1) / −multiscale
(GMC_GAPS=5,5,5). The old −ρ row is obsolete: full model IS the no-ρ model.
Env guard must be set for BOTH train and cache build of that config.

```bash
for CFG in full noego nomulti; do
  case $CFG in
    full)    ENV="" ;;
    noego)   ENV="GMC_RAWVEL=1" ;;
    nomulti) ENV="GMC_GAPS=5,5,5" ;;
  esac
  for s in 0 1 2 3 4; do
    W=gmc_link_weights_v1train_sw12d_${CFG}_seed${s}.pth
    SFX=_sw12d_${CFG}_seed${s}
    env $ENV python -m gmc_link.train --split v1 --stage 1 \
        --architecture shared_weight --seed $s --save-path $W \
        2>&1 | tee logs/12d/abl_train_${CFG}_seed${s}.log
    env $ENV GMC_WEIGHTS=$W GMC_SUFFIX=$SFX python run_build_gmc_cache.py \
        2>&1 | tee logs/12d/abl_cache_${CFG}_seed${s}.log
    GMC_SUFFIX=$SFX OUT_SUFFIX=$SFX python run_ikun_linear_additive.py \
        --alpha ALPHA_STAR_IKUN \
        2>&1 | tee logs/12d/abl_eval_${CFG}_seed${s}.log
  done
done
# ALPHA_STAR_IKUN = the LOSO-selected α from Phase 4 (fill in before running).
# "full" seeds 0-2 reuse Phase 1/2 weights+caches — skip retrain, just eval seeds 3-4 extra.
```

## Phase 6 — final numbers at α*

Main tables = Phase 3 sweep rows at α* (n=3 mean±std, already in the CSVs).
Provenance tuple per number: (arch, n=3 seeds 0-2, _sw12d_seed{N},
gt_template_old [iKUN] / FlexHook gt_template [FH], pooled|per-class,
α=α*, gate 0.0, raw cos).

## Invalidated by this change (do not reuse)

- All 13D aligner checkpoints: `*sharedweight_seed*.pth`, legacy `mlp`, FiLM
- All 13D caches: `iKUN/motion_13d_cache*/`, `gmc_link/gmc_scores_*` without `_sw12d`
- Old recipe hyperparams (α/sc/thr × class × arch) — deleted from scripts
