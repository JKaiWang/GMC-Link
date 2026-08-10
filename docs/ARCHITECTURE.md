# ARCHITECTURE.md — pipeline, data flow, constants, layout

Extracted from CLAUDE.md 2026-07-05.

## Pipeline stages

**Stage 1 — Ego-motion compensation** (`gmc_link/core.py`)
- `ORBHomographyEngine`: ORB features, BFMatcher (Hamming, Lowe ratio 0.7),
  RANSAC homography. Foreground mask prevents tracking object features instead
  of static background. Output: 3×3 homography prev→current frame.

**Stage 2 — Cumulative homography & velocity** (`gmc_link/manager.py`)
- `GMCLinkManager` stores ORIGINAL (never-warped) centroids in history deques;
  composes cumulative homographies H[t−k→t] = H[t−1→t] @ … @ H[t−k→t−k+1].
- Multi-scale residual velocity at frame gaps 2/5/10.
  Residual velocity = raw velocity − ego velocity.
- EMA smoothing: `MotionBuffer` (α=0.3) + `ScoreBuffer` (α=0.4) in `utils.py`.
- Output 13D motion vector:
  `[res_dx_s, res_dy_s, res_dx_m, res_dy_m, res_dx_l, res_dy_l, dw, dh, cx, cy, w, h, snr]`

**Stage 3 — Motion-language alignment** (`gmc_link/alignment.py`)
- `MotionLanguageAligner`. SHIP = `shared_weight` arch (2026-05-21): per-modality
  Linear adapter (motion 13→256, lang 384→256) → shared 2-hidden MLP
  (256→512→512→256) → LN → L2-norm. Train with `--architecture shared_weight`.
- Legacy `mlp` arch is the CODE DEFAULT (`--architecture mlp`): independent
  dual-MLP per modality (13→256→512→256 / 384→256→512→256) → L2-norm.
  Prior ship until 2026-05-21. Don't confuse default with ship.
- Ship inference: raw cosine (no sigmoid, no EMA) via `GMC_RAW_COS=1`;
  `manager.py:587` bypasses cosine_buffer + sigmoid when raw_cos=True.
- Training: symmetric InfoNCE + False-Negative Masking (`gmc_link/losses.py`).
- Language embeddings: SentenceTransformer all-MiniLM-L6-v2, 384D
  (`gmc_link/text_utils.py`).

**Stage 4 — Decision-level linear additive fusion**
(`run_ikun_linear_additive.py`, `run_flexhook_phase5_gmc_sweep.py`,
`run_flexhook_v2_raw_sweep.py`)
- `final = model_logit + α · (sc · raw_cos + thr)` per arch per axis.
- 18 free hyperparams (α/sc/thr × motion+appear × 3 archs). Values + rationale:
  docs/SHIP.md.
- Legacy `gmc_link/fusion_head.py` (F1-optimized MLP 3→32→16→1) is NOT ship —
  crashes HOTA −3.79.

## Data flow

```
Video frames
  → ORBHomographyEngine (frame-to-frame H)
  → GMCLinkManager (cumulative H, warp original coords, multi-scale residual velocity)
  → 13D motion vector
  → MotionLanguageAligner (shared_weight)  ←  TextEncoder("moving cars") 384D
  → raw cosine ∈ [−1, +1]   (GMC_RAW_COS=1)
  → per-arch linear additive fusion
  → HOTA eval (TrackEval consumer per arch: iKUN / FH V1 / FH V2)
```

## Training data pipeline (`gmc_link/dataset.py`)

- Refer-KITTI V2 expressions + GT centroid tracks.
- Frame gaps [2, 5, 10] — MUST match `GMCLinkManager.FRAME_GAPS`.
- Synthetic positional jitter ±2px; velocity normalization
  `v_norm = (v_pixel / img_dims) × 100` (resolution-invariant).
- Positive (motion_vector, language_embedding) pairs for InfoNCE.

## Design rationale (why these choices — don't re-litigate without new data)

- ORB+Homography over optical flow: beat Farneback AND RAFT on KITTI planar
  scenes; better outlier rejection via RANSAC.
- Multi-scale temporal velocity (gaps 2/5/10): dominant ablation gain
  (+0.047 separation).
- SNR feature: no mean-separation gain, but cuts variance ±0.010 → ±0.007
  (stabilizes predictions) — do not drop it for looking "useless" on means.
- Cumulative homography (store original coords, warp once with composed H):
  more numerically stable than iterative per-frame warping.
- False-Negative Masking: many train samples share one expression; FNM stops
  same-sentence pairs being punished as negatives.

## Key constants

- `VELOCITY_SCALE = 100` (`utils.py`)
- `FRAME_GAPS = [2, 5, 10]` (`manager.py`; mirrored in `dataset.py`)
- InfoNCE temperature 0.07 (`losses.py`)
- EMA alphas: MotionBuffer 0.3, ScoreBuffer 0.4, cosine_buffer 0.4
  (ship bypasses cosine_buffer via GMC_RAW_COS=1)
- Dims (ship sw): 13D/384D → 256 adapter → shared 256→512→512→256.
  Legacy mlp: 13→256→512→256 and 384→256→512→256.

## Layout

- `gmc_link/` — installable package (core library)
- `run_*.py` — top-level experiment/eval scripts (not in package)
- `build/` — stale setuptools artifacts, do not edit
- `*.pth` weights + `*.npz` data gitignored
- `paper/` — paper drafts, LaTeX, reproducibility manifest
- Experiment history: `RESEARCH_NOTES.md` (579 lines — delegate reading)
