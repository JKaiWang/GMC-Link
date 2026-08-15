# T-probe: representation diagnosis (pre-registered 2026-08-15)

Adapted from external feedback with three corrections. Question chain:
history 有沒有資訊 → 需要多長 → 是什麼資訊 → 才決定 architecture.
Pure diagnostic — no changes to the shipping system; NOT gated on HOTA.

## Corrections vs the original proposal (why this differs)

1. **Ship 12D is not instantaneous** (it embeds gap-2/5/10 velocities = 10 frames
   of built-in history). The T-sweep therefore runs on a truly-instantaneous 8D
   feature; ship-12D is a separate control arm (its T=1 ≈ built-in-history probe).
2. **Identical sample set across all T**: samples = (track, frame) with contiguous
   GT history ≥ 16 and future ≥ 5. T=32 dropped (median KITTI segment 24-30
   frames would bias the sample set); T ∈ {1, 2, 4, 8, 16}.
3. **Two label sources** (circularity guard): kinematic labels are computed from
   the same GT kinematics the features encode — high accuracy there ≠ task
   relevance. Expression-derived labels (track ∈ GT of keyword-matched V1
   expressions) are the task-relevant primary; kinematic labels remain as the
   information-existence check. Kinematic "moving" is additionally
   parallax-contaminated (A14: static-object image residual up to ~7px/frame on
   0005) — noted, reported, not hidden.
4. **Mean-pool is permutation-invariant, so the original plan's shuffle test
   would trivially show zero effect.** Two readouts per T: mean-pool
   (order-free) and flatten (order-aware); the shuffle test applies to flatten.

## Fixed conditions

- Data: Refer-KITTI V1 TRAIN seqs only (15). Probe-test seqs (held out, fixed):
  0001, 0006, 0010, 0016 (every 4th of the sorted list). Probe-train: other 11.
- Trajectories: GT (labels_with_ids), pixel coords. Tracker-trajectory arm = later.
- Ego: composed per-frame similarity chain (ORB1500, GT-box masked), same
  convention as ship inference.
- Features per frame:
  - `inst8`: [res_dx1, res_dy1, dw1, dh1, cx/W, cy/H, w/W, h/H] (gap-1 residual,
    ×100 velocity scale) — the T-sweep arm.
  - `ship12`: ship 12D (gap 2/5/10 residuals + box state) — control arm.
- Probe: sklearn LogisticRegression (class_weight=balanced, StandardScaler),
  seed 0. Metrics: macro-F1 (primary), AUROC. No MLP in round 1.
- Tasks × label sources:
  - Expression labels (primary): moving vs parked/static; turning; braking;
    counter-direction (each binary: keyword-group tracks vs
    contrast/complement; ambiguous excluded).
  - Kinematic labels (secondary): moving (win-5 mean residual speed > 0.8
    px/frame), direction (sign of res_dx), turning (|Δθ| win-8 > 4°/frame among
    moving), braking (speed drop > 30% over win-8 among moving),
    counter-direction (cos(θ_i − θ_neighbors) < 0, ≥1 moving neighbor).
    Thresholds fixed here BEFORE running; recorded in script.
- Shuffle test: T=16 flatten, fixed per-sample permutation (seed 0).
- Future probe (secondary): Ridge regression, flatten T → displacement of bbox
  center over +5 frames; ADE in px.

## Decision rules (pre-registered)

- Task where flatten-T=16 ≫ T=1 (≥ +0.10 macro-F1) → temporal information
  exists that instantaneous features lack → temporal-encoder direction reopens
  FOR THAT SEMANTIC (with the 2026-06-11 convergent-kill caveat: monetizing it
  needs a different alignment objective, since transformer-at-HOTA was flat).
- T=1 already high (≥ 0.9 of T=16) → that semantic does not need history.
- ordered ≫ shuffled (≥ +0.05 macro-F1) → ordering itself carries information
  (supports recurrent/attention encoders over pooling).
- ship12 T=1 ≈ inst8 T=8..16 → built-in multi-scale already captures it;
  ship12 T=1 ≪ inst8 T=16 → the 12D compression loses history information.
- Expression-label probes ≪ kinematic-label probes on the same task →
  label-domain gap (kinematics separable but task semantics not) — that itself
  is a finding (language/annotation side, not representation side).

Outputs: `results/tprobe/tprobe_results.json` + printed tables.
Runtime: CPU only, ~1-2 h (ego chains ~10 min, probes minutes).
