# CLAUDE.md

File guide Claude Code (claude.ai/code) working repo.

## Project Overview

GMC-Link = plug-and-play module **Referring Multi-Object Tracking (RMOT)**. Bridge object motion (geometry) + natural language (semantics). Input video + description like "moving cars", score which tracked objects match by physical motion reasoning, not visual appearance.

**CURRENT SHIP — Option B, locked 2026-08-19** (user decision, no professor sign-off
required; decision record `docs/SHIP_DECISION_2026_08_16.md`). All three host settings
share one ego chain: **road-plane homography** (`GMC_GROUND_MODE=road`) + warm11 validity
mask + no motion EMA + raw cosine + additive fusion at gate 0.0 (α=0 ≡ native exact).
Aligner weights `gmc_link_weights_v1train_sw12d_groad_seed{N}.pth`, caches
`_sw12d_groad_seed{N}_warm11`.

| Host | Fusion | pooled HOTA | native |
|---|---|---|---|
| iKUN | two-α, α_mot=1.0 / α_app=0.1 (LOSO re-run under the A43 router; was 0.7/0.1 under the pre-A43 router, A32/A42) | **45.304 ± 0.115** (MOVING 37.139 ± 0.923, A43 class) | 44.543 |
| FlexHook V1 (official 150-expr protocol, A31) | single α\*=7 (LOSO, A37) | **53.980 ± 0.059** (MOVING 48.330 ± 0.189, A43 class) | 53.824 |
| FlexHook V2 | single α\*=5 (LOSO, A37) | **42.625 ± 0.032** (canonical MOVING +0.694, t=27, A43 class) | 42.526 |

Two-α routes on the canonical expression text (α_mot for MOVING/STATIC, α_app for
APPEARANCE); per-host LOSO selects α_mot=α_app on both FlexHook settings, so they
degenerate to a single α (A35, measured on the road chain). FPS (CPU, process-only, same
session, A41): road **149.3** (6.7 ms/frame) / global 63.9. Never compare FPS across sessions —
A36's 31.8 / 42.8 were machine-state-specific.

**Expression classes (A43, 2026-08-29)**: ONE shared keyword classifier `gmc_link/moving_kw.py`
(MOVING: moving, in motion, driving, walking, running, jogging, crossing, riding, travelling/traveling,
braking, brake, accelerat, decelerat, slowing down, speeding up, approaching, overtaking, receding;
STATIC: parking, parked, stopped, stop, stand, static, stationary; else APPEARANCE) drives BOTH the
α router and the per-class HOTA rows. `turning`/`faster`/direction exprs are APPEARANCE by design.
V1 official-150: MOVING 21 / STATIC 12 / APPEAR 117; V2 canonical 111 / 93 / 658. iKUN ship trees are
`hota_eval_ikun_linear_additive_sw12d_*_mkw/am1.0_aa0.1` (re-run under the A43 router; `am0.7_aa0.1` there = same router, old α; vs the pre-A43
trees only the two `0011+*-faster-than-ours` predict.txt differ — `turning-*` have no iKUN host scores)
— read `result_off150_mkw.json`; summaries in `results/moving_kw/` (canonical iKUN: `ikun_official150_mkw_am1.0.json`; LOSO: `loso_two_alpha_mkw.json`; A44 sub-metrics / α sweep / single-α n=5: `submetrics.json`, `alpha_sweep_mkw.json`, `single_alpha_0.35_n5.json`). FlexHook needs no re-run (α_mot=α_app).

**Historical ships (superseded, kept for provenance)**: 2026-08-10 12D single-α on the
global similarity chain (iKUN 44.656 @0.5 / FH V1 54.011 @7 / FH V2 42.658 @5 — this was
"Option A"); 2026-05-21 13D per-class recipe ship (iKUN 44.634 / FH V1 53.526 / FH V2
42.807, 18 hyperparams). Reproduced natives: iKUN 44.543 on the official 150-expr list (A42, 2026-08-29; 44.224 on
the old 158-list every pre-A42 iKUN number used), FH V1 53.824 (official list) / 53.110
(old 158-expr list), FH V2 42.526.

**Protocol (A42): all V1 numbers use the official 150-expression test seqmap**
(`seqmaps/refer_kitti_v1_test_official_150.txt` = TransRMOT `seqmap.txt` = FlexHook
`kitti-1.txt`; iKUN's own `utils.py` drops the same 8). `run_ikun_linear_additive.py` still
enumerates all 158 JSONs in `expression/{seq}`, so its `result.json` is the 158-list number and
is NOT paper-comparable. After any iKUN run, rescore TrackEval-only: filter the run dir's
`seqmap.txt` to the official list (and per class via `classify()`), rerun
`TrackEval/scripts/run_mot_challenge.py --METRICS HOTA --SEQMAP_FILE <filtered>` with the same
GT/tracker folder arguments `run_te()` uses, and record that number (A42 did this for all 485
dirs → `result_off150.json` per dir, summary `results/official150/ikun_official150.json`; the
one-off rescore/aggregate scripts are kept local, not in git). A43 trees: same rescore with
`--out-name result_off150_mkw.json` → `results/moving_kw/ikun_official150_mkw.json`.

## Common Commands

### Training (Ship Aligner)

```bash
# Train ship aligner: shared_weight 12D on the ROAD chain (seeds 0/1/2; +3/4 for n=5)
# Train-time ground mode must match inference — road caches need road-trained weights.
for s in 0 1 2; do
  GMC_GROUND_MODE=road python -m gmc_link.train --split v1 --stage 1 \
      --architecture shared_weight --seed $s \
      --save-path gmc_link_weights_v1train_sw12d_groad_seed${s}.pth
done

# Legacy mlp arch (default; was prior ship arch until 2026-05-21)
python -m gmc_link.train --split v1 --stage 1 --architecture mlp

# Legacy F1-optimized fusion head (NOT ship; crashes HOTA — see project memory)
python gmc_link/fusion_head.py --collect / --train / --eval
```

### Ship Evaluation (Option B: road chain + additive fusion)

```bash
# Build GMC caches per-arch per-seed on the road chain (raw cosine is the only mode)
GMC_GROUND_MODE=road GMC_MOTION_EMA=0 \
    GMC_WEIGHTS=gmc_link_weights_v1train_sw12d_groad_seed0.pth \
    GMC_SUFFIX=_sw12d_groad_seed0_warm11 \
    python run_build_gmc_cache.py                    # iKUN
GMC_GROUND_MODE=road ... python run_build_gmc_cache_flexhook.py         # FH V1
GMC_GROUND_MODE=road ... python run_build_gmc_cache_flexhook_v2_raw.py  # FH V2

# iKUN ship eval: two-α keyword routing (α=0 ≡ reproduced native). result.json is on the
# 158-list — paper numbers need the official-150 TrackEval rescore (see Protocol note, A42)
GMC_SUFFIX=_sw12d_groad_seed0_warm11 OUT_SUFFIX=_sw12d_groad_seed0_warm11_mkw \
    python run_ikun_linear_additive.py --alpha-mot 1.0 --alpha-app 0.1   # _mkw = A43 router; α re-selected by LOSO (A43)

# FlexHook ship eval: single α. V1 needs the host's official 150-expr seqmap (A31);
# OUT_SUFFIX must carry _off150 so official-list runs never mix with 158-list trees.
FH_OFFICIAL_SEQMAP=$HOME/FlexHook/seqmaps/kitti-1.txt \
    GMC_SUFFIX=_sw12d_groad_seed0_warm11 OUT_SUFFIX=_sw12d_groad_seed0_warm11_off150 \
    python run_flexhook_phase5_gmc_sweep.py --alpha 7

# LOSO α selection (fold runs; never read a fold result.json as a full-test number)
python run_two_alpha_sweep.py --arch ikun --am ... --aa ...   # two-α, 2D grid
```

### Ablation Studies

Old `run_ablation_study.py` / `run_ablation_proper.sh` are deleted. Ablations run
via env guards (train + cache build both): `GMC_RAWVEL=1` (−ego),
`GMC_GAPS=5,5,5` (−multiscale). The −ρ row is obsolete (full model IS no-ρ).
Full n=5 iKUN MOVING-HOTA protocol: `EXPERIMENT_COMMANDS.md` Phase 5.

### Package Installation

```bash
pip install -e .
# Dependencies: torch, torchvision, numpy, opencv-python, sentence-transformers, tqdm, scipy
```

## Architecture

### Pipeline Stages

**Stage 1 — Ego-Motion Compensation** (`gmc_link/core.py`) — TWO parallel chains:
- **Road-plane chain (SHIP, `GMC_GROUND_MODE=road`)**, `estimate_road_homography` (core.py:54-94):
  Shi-Tomasi corners (`goodFeaturesToTrack`, maxCorners=600, qualityLevel=0.01) + pyramidal
  Lucas-Kanade flow (winSize 21, maxLevel 3) on the lower half of the frame (road_band=0.5)
  minus detection boxes; `findHomography(..., RANSAC, 3.0)`. NOT ORB — not because ORB
  starves on asphalt (A39: it finds 188 good matches p50 in the band) but because its
  keypoints sit near the horizon, off the road plane, so its H aligns the road no better
  than the global fit. Returns None below 12 tracked points (never happened: 0/7,690, A39).
- **Global chain (fallback + legacy ship)**: `ORBHomographyEngine` — ORB 1500 features,
  BFMatcher (Hamming, Lowe 0.7), RANSAC 5.0px. In road mode it is estimated LAZILY — only
  when the road fit returns None (A41, 2026-08-25; never observed: 0/7,690 pairs) — so the
  ship pays for one estimator per frame; the global cumulative buffer is not maintained in
  road mode. Cache equivalence verified (0011 seed0: 183,872 entries, max |Δ| 0.00).
- Foreground mask prevents fitting to tracked objects instead of static background
- Output: 3×3 homography mapping prev frame → current frame (one per chain)

**Stage 2 — Cumulative Homography & Velocity** (`gmc_link/manager.py`):
- `GMCLinkManager` store *original* (never-warped) centroid coords in history deques
- Hold cumulative composed homographies: H[t-k→t] = H[t-1→t] @ ... @ H[t-k→t-k+1]
- Compute **multi-scale residual velocity** at three temporal gaps (2, 5, 10 frames) catch different motion patterns
- Residual velocity = raw velocity − ego velocity, isolate true object movement
- EMA smoothing: `MotionBuffer` (α=0.3) + `ScoreBuffer` (α=0.4) in `utils.py`
- Output **12D motion vector**: `[res_dx_s, res_dy_s, res_dx_m, res_dy_m, res_dx_l, res_dy_l, dw, dh, cx, cy, w, h]` (ρ/snr slot removed 2026-08-10)

**Stage 3 — Motion-Language Alignment** (`gmc_link/alignment.py`):
- `MotionLanguageAligner`: ship = `shared_weight` arch (2026-05-21 ship adoption). Per-modality Linear adapter (motion 12→256, lang 384→256) → shared 2-hidden MLP (256→512→512→256) → LN → L2-norm. Symmetric two-tower, shared nonlinear core. Trained `--architecture shared_weight`.
- Legacy `mlp` arch is code default (`--architecture mlp`): independent dual-MLP per modality (motion 12→256→512→256, lang 384→256→512→256) → L2-norm. Asymmetric per-modality projectors. Prior ship arch until 2026-05-21.
- Inference (ship): raw cosine (no sigmoid, no EMA) — cache builders emit raw cos unconditionally (GMC_RAW_COS env removed 2026-08-10).
- Legacy inference (mlp ship era): sigmoid + EMA smoothing.
- Train symmetric InfoNCE loss (`gmc_link/losses.py`). NOTE (audit 2026-08-13): ship stage-1 path has NO False-Negative Masking — default `AlignmentLoss` ignores `sentence_ids`; FNM-capable `HardNegativeInfoNCE` is blocked for stage 1 (see RESEARCH_NOTES §10 A1)
- Language embeddings: SentenceTransformer (all-MiniLM-L6-v2, 384D) via `gmc_link/text_utils.py`

**Stage 4 — Additive Fusion with class-conditional α** (`run_ikun_linear_additive.py`, `run_flexhook_phase5_gmc_sweep.py`, `run_flexhook_v2_raw_sweep.py`):
- Ship formula: `s_final = s_host + α(expr) · s_gmc`; detection gate frozen at native 0.0, so α=0 ≡ reproduced native baseline
- `α(expr) = α_mot` when the keyword classifier labels the canonical expression text MOVING or
  STATIC, `α_app` when APPEARANCE. α_mot = α_app is bit-exact single-α.
- iKUN: two-α (1.0 / 0.1) selected by LOSO under the A43 router (was 0.7 / 0.1, A32). **FlexHook V1/V2: per-host LOSO selects
  α_mot = α_app, so both degenerate to a single α** (A35 — the α_app axis is unresolved on
  both, and out-of-grid probes confirm the optimum is interior, not truncated).
- Keyword classifier = shared `gmc_link/moving_kw.py` (A43); ALSO used for per-class HOTA grouping (MOVING/STATIC/APPEARANCE);
  for V2 grouping use canonical `raw_sentence`, never the paraphrased slug (A30)
- Historical per-class recipe fusion (18 hyperparams) superseded 2026-08-10; recipes in git history
- Legacy `gmc_link/fusion_head.py`: F1-optimized MLP — NOT ship, crashes HOTA (−3.79)

### Data Flow

```
Video Frames
    ↓
Road-plane chain (Shi-Tomasi + LK on road band)  →  H_road   [SHIP]
ORBHomographyEngine (global)                     →  H_global [fallback when road fit fails]
    ↓
GMCLinkManager → compose cumulative H, warp original coords, compute multi-scale residual velocity
    ↓
12D motion vector [res_dx×3scales, res_dy×3scales, dw, dh, cx, cy, w, h]
    ↓
MotionLanguageAligner (shared_weight) ←── TextEncoder("moving cars") → 384D embedding
    ↓
raw cosine ∈ [−1, +1]   (no sigmoid, no EMA)
    ↓
Additive fusion: s_final = s_host + α(expr) · raw_cos   (gate 0.0)
    iKUN: α_mot 0.7 / α_app 0.1  |  FlexHook: single α (routing degenerates, A35)
    ↓
HOTA-eval (TrackEval per-arch consumer: iKUN / FH V1 official-150 / FH V2)
```

### Training Data Pipeline (`gmc_link/dataset.py`)

- Load Refer-KITTI V2 expressions + ground-truth centroid tracks
- Multi-scale frame gaps `[2, 5, 10]` match `GMCLinkManager.FRAME_GAPS`
- Apply synthetic positional jitter (±2px) for robustness
- Normalize velocity: `v_norm = (v_pixel / img_dims) × 100` (resolution-invariant)
- Generate positive (motion_vector, language_embedding) pairs for InfoNCE train

### Key Constants

- `VELOCITY_SCALE = 100` (`utils.py`) — multiplier normalized velocities so MLP inputs ~1.0 magnitude
- `FRAME_GAPS = [2, 5, 10]` (`manager.py`) — must match between `GMCLinkManager` + `dataset.py`
- InfoNCE temperature: `0.07` (`losses.py`)
- EMA alphas: `MotionBuffer(α=0.3)`, `ScoreBuffer(α=0.4)` — score-side EMA/sigmoid removed from ship path 2026-08-10
- Embedding dims (ship `shared_weight`): motion/lang 12D/384D → 256D (Linear adapter) → shared trunk 256→512→512→256. Legacy `mlp`: motion 12D → 256D → 512D → 256D, language 384D → 256D → 512D → 256D.
- Ship fusion (Option B, locked 2026-08-19): road chain + `s_host + α(expr)·s_gmc`, gate 0.0.
  α from LOSO: iKUN (α_mot 1.0, α_app 0.1; A43 router); FlexHook V1 α=7, FlexHook V2 α=5 (A37).
  Road homography RANSAC threshold is **3.0px** (global path is 5.0px); the road fit succeeds
  on 7,690/7,690 adjacent frame pairs across all 19 train+eval seqs (A39), so the lazy ORB
  fallback never fires. Old recipes superseded.
- Legacy Fusion Head arch (NOT ship): 3→32→16→1 sigmoid output

### Project Layout Notes

- Paper: **`2027_ICASSP/gmc_v3.tex` is the LIVE working file** (since 2026-08-29, A43 numbers —
  edit this one). Pending corrections tracked in issues #23 (numeric/factual) and #24
  (narrative). Paper prose is USER-LED: never edit the .tex autonomously; wait for the user to
  say "開始寫" and write collaboratively. Superseded: `2027_ICASSP/gmc_v2.tex` (as committed at 148b6be, the last paper-2026-08-26-round revision; A42 and A43 live only in v3 — new experiment rounds fork a new vN, never edit a frozen one), `2027_ICASSP/gmc_v1.tex`
  (paper-2026-08-22 release), `2027_ICASSP/gmc.tex`, and `paper/latex/mainv3.tex` (frozen
  Aug-5 submission) — comparison only, never edit.
- `gmc_link/` — installable package (core library)
- `run_*.py` — top-level experiment/eval scripts (not in package)
- `build/` — stale `setuptools` build artifacts; do not edit
- Weight files (`*.pth`) + data files (`*.npz`) gitignored

## Data Paths

- Refer-KITTI dataset: `/home/seanachan/data/Dataset/refer-kitti` (V1, 818 expressions / 18 seqs; symlinked `refer-kitti/` + `Refer-KITTI/`). The V2 paraphrase set is a separate directory `/home/seanachan/data/Dataset/refer-kitti-v2` (9,778 expressions), used only by `--split v2`
- Full annotation JSON: `Refer-KITTI_labels.json`
- iKUN precomputed scores: `iKUN/`
- NeuralSORT track detections: `NeuralSORT/`
- **GT template — TWO conventions, must pick right one (corrected 2026-04-30):**
  - `gt_template_old/` = **paper-iKUN-canonical**. Frame numbering aligns with NeuralSORT tracker `predict.txt`. Reproduces paper README 44.56 HOTA at 44.543 on the official 150-expr seqmap (44.224 on the 158-list, A42; cascade+simcalib YOLOv8-NS, 3-seq pooled). USE for any iKUN-paper comparison.
  - `gt_template/` = 2026-04-16 TransRMOT-convention regeneration. Frame numbering off-by-one vs NeuralSORT tracker. Using it drops HOTA ~6.4 due to gt-prediction misalignment (NOT a free eval improvement). Use only if pairing with TransRMOT-style tracker outputs.
  - Earlier note "fix closed ~10-point HOTA gap" was misleading — conflated the two label spaces. NeuralSORT tracker lives in `gt_template_old`'s convention.

## Important Design Decisions

- **ORB over optical flow**: ORB+Homography beat Farneback + RAFT on KITTI planar scenes; better outlier rejection via RANSAC
- **Decision-level fusion only**: Feature-level injection (motion into CLIP) caused catastrophic regression (−21.7% F1); always fuse at decision level
- **False-Negative Masking**: intended design (prevent same-sentence pairs penalized as negatives) but NOT ACTIVE in ship stage-1 training (audit 2026-08-13, RESEARCH_NOTES §10 A1); ~30% of in-batch negatives are same-group false negatives at B=256
- **Cumulative homography**: Store original coords, warp once with composed H — more numerically stable than iterative per-frame warp
- **Multi-scale temporal velocity**: Three frame gaps (2, 5, 10) capture short/mid/long motion patterns; dominant ablation gain (+0.047 separation)
- **ρ/SNR feature REMOVED (2026-08-10)**: ablation showed no HOTA cost; professor-directed simplification → 12D
- **Motion keyword detection (A43, 2026-08-29)**: one shared list in `gmc_link/moving_kw.py` (19 MOVING stems + 7 STATIC) both routes α and groups per-class HOTA; every eval script imports it (pre-A43 per-script copies — 15 stems iKUN / 25 V2-slug — live in git history; `run_flexhook_v2_raw_sweep.py` keeps its slug `classify()` for legacy rows only). Direction/turning/faster exprs are APPEARANCE by design → α_app.
- **Not for temporal trackers**: GMC-Link designed for spatially-ignorant vision-language frameworks (e.g., TransRMOT, iKUN). Cascading onto trackers with native temporal memory (e.g., TempRMOT) cause structural regression from redundant temporal constraints
- **Per-class GMC-relevance damping (2026-05-21)**: ship recipe sc_a (appear axis) is 7-11× smaller than sc_m (motion axis) per arch. GMC = motion signal is NOISE on appearance exprs ("black cars"). Hand-tuned damping suppresses this. Auto-deriving via std-matching falsified (variant B, all 3 archs NEG, see `project_variant_b_std_matching_negative_2026_05_21`).
- **Learned fusion heads = NEG**: F1-optimized MLP fusion head (`fusion_head.py`) crashes HOTA (−3.79 pool). Residual additive MLP on iKUN NEG. Hand-tuned linear additive strictly safer.

## Experiment Log

Detailed experiment history (Exp 1–24+) in `RESEARCH_NOTES.md`, including ablations, loss comparisons, arch decisions with exact metric values.