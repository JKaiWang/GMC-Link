# PRE-REGISTRATION — n=5 ablations for BOTH ship options + FPS profile (Track D hedge)

Registered 2026-08-16 before any new number exists. Runs while the ship
decision (Option A single-α sim vs Option B road+two-α; Obsidian decision doc)
is with the professor — arms cover both options so no rerun is needed either way.

## Protocol (identical to the 2026-08-11 ablation discipline)

iKUN only, n=5 seeds (0-4), eval at each option's LOSO-selected operating point
(NOT re-tuned): Option A = single α=0.5 on sim-chain caches; Option B =
two-α (0.7, 0.1) on road-chain caches. All builds: GMC_MOTION_EMA=0,
GMC_MODEL=similarity, warm11 filter (T≥11, fixed). α=0 ≡ 44.224 exact.
Primary metric MOVING HOTA, secondary pooled; Welch t (n=5) vs the matching
full arm. Priors (2026-08-11, 12D era): −ego −2.12 MOVING (p=0.006), 
−multiscale −0.55 (marginal).

## Arms

| arm | weights | build env | evals |
|---|---|---|---|
| A-full n=5 completion | sw12d seeds 3,4 (exist) | sim chain | α=0.5 |
| B-full n=5 completion | groad seeds 3,4 (TRAIN: GMC_GROUND_MODE=road) | road chain | (0.7,0.1) + α=0.5 |
| −ego (shared) | noego seeds 0-4 (exist, GMC_RAWVEL=1 trained) | GMC_RAWVEL=1 | α=0.5 AND (0.7,0.1) |
| −multiscale (A) | nomulti seeds 0-4 (exist, GMC_GAPS=5,5,5) | sim chain + GMC_GAPS | α=0.5 |
| −multiscale (B) | same weights | road chain + GMC_GAPS | (0.7,0.1) |

Note: −ego has no ego chain at all, so it is chain-agnostic — one build serves
both options; the two-α eval of it is Option B's −ego row.

## FPS profile (ship-agnostic)

Recreate `profile_inference.py` (missing from repo, memory
`project_paper_fps_fix...`): per-frame wall-time on seq 0011 for (a) ORB
sim-chain step, (b) road-chain step, (c) 12D feature compute, (d) aligner
forward; report ms/frame breakdown + end-to-end FPS for both chains.
Prior profile: ~68 FPS. Output `results/fps_profile.json`.

## Interpretation

Fixed operating points, no tuning → these rows go straight into the paper
number-pack for whichever option the professor selects. Expectation: −ego
significantly negative on MOVING in both options (module's core claim);
−multiscale marginal. Any sign flip vs priors → flag before use.
