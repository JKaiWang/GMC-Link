# CLAUDE.md

File guide Claude Code (claude.ai/code) working repo.

## Project Overview

GMC-Link = plug-and-play module **Referring Multi-Object Tracking (RMOT)**. Bridge object motion (geometry) + natural language (semantics). Input video + description like "moving cars", score which tracked objects match by physical motion reasoning, not visual appearance.

**Current ship (2026-08-10 simplification, numbers pending rerun)**: ρ/snr removed
(13D→12D), fusion collapsed to `s_final = s_host + α·s_gmc` (single α per arch, all
expressions, gate frozen at native 0.0 so α=0 ≡ reproduced native). α* selected via
LOSO from the α sweep. Full protocol: `EXPERIMENT_COMMANDS.md`. Results land in
`results/alpha_sweep_*.{csv,json}`.

**Historical (2026-05-21 recipe ship, 13D + per-class recipes — superseded)**:
iKUN 44.634 ± 0.066 / FH V1 53.526 ± 0.087 / FH V2 42.807 ± 0.038 (n=3, paper-beat 2/3).
Reproduced natives: iKUN 44.224, FH V1 53.110, FH V2 42.526.

## Common Commands

### Training (Ship Aligner)

```bash
# Train shared_weight 12D aligner (ship arch, seeds 0/1/2; +3/4 for n=5 ablation)
for s in 0 1 2; do
  python -m gmc_link.train --split v1 --stage 1 \
      --architecture shared_weight --seed $s \
      --save-path gmc_link_weights_v1train_sw12d_seed${s}.pth
done

# Legacy mlp arch (default; was prior ship arch until 2026-05-21)
python -m gmc_link.train --split v1 --stage 1 --architecture mlp

# Legacy F1-optimized fusion head (NOT ship; crashes HOTA — see project memory)
python gmc_link/fusion_head.py --collect / --train / --eval
```

### Ship Evaluation (Single-α Additive Fusion)

```bash
# Build GMC caches per-arch per-seed (raw cosine is the only output mode)
GMC_WEIGHTS=gmc_link_weights_v1train_sw12d_seed0.pth GMC_SUFFIX=_sw12d_seed0 \
    python run_build_gmc_cache.py                    # iKUN
GMC_WEIGHTS=... GMC_SUFFIX=... python run_build_gmc_cache_flexhook.py         # FH V1
GMC_WEIGHTS=... GMC_SUFFIX=... python run_build_gmc_cache_flexhook_v2_raw.py  # FH V2

# Single eval at one α (gate frozen at 0.0; α=0 ≡ reproduced native)
GMC_SUFFIX=_sw12d_seed0 python run_ikun_linear_additive.py --alpha 0.3

# α sweep across seeds → results/alpha_sweep_{arch}.{csv,json}
python run_alpha_sweep.py --arch ikun  --alphas 0,0.1,0.2,0.3,0.5,0.7,1.0
python run_alpha_sweep.py --arch fh_v1 --alphas 0,1,2,3,5,7,10
python run_alpha_sweep.py --arch fh_v2 --alphas 0,1,2,3,5,7,10
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

**Stage 1 — Ego-Motion Compensation** (`gmc_link/core.py`):
- `ORBHomographyEngine` extracts ORB features, matches BFMatcher (Hamming, Lowe's ratio=0.7), RANSAC homography estimate
- Foreground mask prevent tracking object features instead static background
- Output: 3×3 homography matrix map prev frame → current frame

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
- Train symmetric InfoNCE loss + False-Negative Masking (`gmc_link/losses.py`)
- Language embeddings: SentenceTransformer (all-MiniLM-L6-v2, 384D) via `gmc_link/text_utils.py`

**Stage 4 — Single-α Additive Fusion** (`run_ikun_linear_additive.py`, `run_flexhook_phase5_gmc_sweep.py`, `run_flexhook_v2_raw_sweep.py`):
- Ship formula: `s_final = s_host + α · s_gmc` for ALL expressions (no class branching); detection gate frozen at native 0.0, so α=0 ≡ reproduced native baseline
- One free hyperparam per arch (α), selected by LOSO from the α sweep (`run_alpha_sweep.py`)
- Motion-keyword classifier retained ONLY for per-class HOTA grouping (MOVING/STATIC/APPEARANCE)
- Historical per-class recipe fusion (18 hyperparams) superseded 2026-08-10; recipes in git history
- Legacy `gmc_link/fusion_head.py`: F1-optimized MLP — NOT ship, crashes HOTA (−3.79)

### Data Flow

```
Video Frames
    ↓
ORBHomographyEngine → frame-to-frame H matrices
    ↓
GMCLinkManager → compose cumulative H, warp original coords, compute multi-scale residual velocity
    ↓
12D motion vector [res_dx×3scales, res_dy×3scales, dw, dh, cx, cy, w, h]
    ↓
MotionLanguageAligner (shared_weight) ←── TextEncoder("moving cars") → 384D embedding
    ↓
raw cosine ∈ [−1, +1]   (no sigmoid, no EMA)
    ↓
Single-α additive fusion: s_final = s_host + α · raw_cos   (gate 0.0)
    ↓
HOTA-eval (TrackEval per-arch consumer: iKUN / FH V1 / FH V2)
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
- Ship fusion (2026-08-10): one α per arch, α* from LOSO sweep (pending); gate 0.0. Old locked recipes superseded (git history).
- Legacy Fusion Head arch (NOT ship): 3→32→16→1 sigmoid output

### Project Layout Notes

- Paper: `2027_ICASSP/gmc.tex` is the LIVE working file (v2, 12D/single-α — edit this one). `2027_ICASSP/submission_mainv3/mainv3.tex` is the frozen Aug-5 v1 submission snapshot (13D + ρ) — never edit, comparison only.
- `gmc_link/` — installable package (core library)
- `run_*.py` — top-level experiment/eval scripts (not in package)
- `build/` — stale `setuptools` build artifacts; do not edit
- Weight files (`*.pth`) + data files (`*.npz`) gitignored

## Data Paths

- Refer-KITTI dataset: `/home/seanachan/data/Dataset/refer-kitti-v2` (also symlinked `refer-kitti/` + `Refer-KITTI/`)
- Full annotation JSON: `Refer-KITTI_labels.json`
- iKUN precomputed scores: `iKUN/`
- NeuralSORT track detections: `NeuralSORT/`
- **GT template — TWO conventions, must pick right one (corrected 2026-04-30):**
  - `gt_template_old/` = **paper-iKUN-canonical**. Frame numbering aligns with NeuralSORT tracker `predict.txt`. Reproduces paper README 44.56 HOTA at 44.224 (cascade+simcalib YOLOv8-NS, 3-seq pooled). USE for any iKUN-paper comparison.
  - `gt_template/` = 2026-04-16 TransRMOT-convention regeneration. Frame numbering off-by-one vs NeuralSORT tracker. Using it drops HOTA ~6.4 due to gt-prediction misalignment (NOT a free eval improvement). Use only if pairing with TransRMOT-style tracker outputs.
  - Earlier note "fix closed ~10-point HOTA gap" was misleading — conflated the two label spaces. NeuralSORT tracker lives in `gt_template_old`'s convention.

## Important Design Decisions

- **ORB over optical flow**: ORB+Homography beat Farneback + RAFT on KITTI planar scenes; better outlier rejection via RANSAC
- **Decision-level fusion only**: Feature-level injection (motion into CLIP) caused catastrophic regression (−21.7% F1); always fuse at decision level
- **False-Negative Masking**: Multiple train samples share same expression; FNM prevent same-sentence pairs penalized as negatives
- **Cumulative homography**: Store original coords, warp once with composed H — more numerically stable than iterative per-frame warp
- **Multi-scale temporal velocity**: Three frame gaps (2, 5, 10) capture short/mid/long motion patterns; dominant ablation gain (+0.047 separation)
- **ρ/SNR feature REMOVED (2026-08-10)**: ablation showed no HOTA cost; professor-directed simplification → 12D
- **Motion keyword detection**: ~38 motion keywords (moving, turning, parking, etc.) determine class for per-axis fusion in linear additive ship
- **Not for temporal trackers**: GMC-Link designed for spatially-ignorant vision-language frameworks (e.g., TransRMOT, iKUN). Cascading onto trackers with native temporal memory (e.g., TempRMOT) cause structural regression from redundant temporal constraints
- **Per-class GMC-relevance damping (2026-05-21)**: ship recipe sc_a (appear axis) is 7-11× smaller than sc_m (motion axis) per arch. GMC = motion signal is NOISE on appearance exprs ("black cars"). Hand-tuned damping suppresses this. Auto-deriving via std-matching falsified (variant B, all 3 archs NEG, see `project_variant_b_std_matching_negative_2026_05_21`).
- **Learned fusion heads = NEG**: F1-optimized MLP fusion head (`fusion_head.py`) crashes HOTA (−3.79 pool). Residual additive MLP on iKUN NEG. Hand-tuned linear additive strictly safer.

## Experiment Log

Detailed experiment history (Exp 1–24+) in `RESEARCH_NOTES.md`, including ablations, loss comparisons, arch decisions with exact metric values.