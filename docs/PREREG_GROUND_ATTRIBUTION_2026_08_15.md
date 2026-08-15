# PRE-REGISTRATION — ground-arm attribution split (2×2 factorial)

Registered 2026-08-15 (session tmp; user to commit), BEFORE any arm result exists.
User signed off 2026-08-15: attribution = top priority.

## Question

Ground-full arm (A23 draft) gained MOVING +0.665 (t≈3.6) with mechanism unproven
(A21 killed the screening story). GMC_GROUND=1 changes TWO feature-definition
factors at once. Which carries the gain?

- Factor P (warp point): bbox BOTTOM-CENTER (ground-contact) vs centroid
- Factor R (ego chain): road-plane homography chain (LK road band, global-H
  fallback) vs global similarity chain

## Design — 2×2, diagonals already measured

| arm | point | chain | status |
|---|---|---|---|
| sim baseline | centroid | global-sim | measured: 44.656±0.078 / MOV 30.045±0.091 @0.5 |
| G1 "point" | bottom | global-sim | NEW |
| G2 "road" | centroid | road | NEW |
| ground full | bottom | road | measured: 44.591±0.043 / MOV 30.710±0.305 @0.5; MOV@1.0 32.684 |

Each new arm = ONE definition change applied END-TO-END (train + cache build),
same as all prior arms. n=3 seeds, α ∈ {0,0.1,0.2,0.3,0.5,0.7,1.0}, warm11,
GMC_MOTION_EMA=0 at build, GMC_MODEL=similarity at build. α=0 ≡ 44.224 exactly.

Train envs: G1 = GMC_GROUND_MODE=point, defaults otherwise (mirrors sim-ship
training: direct global ego). G2 = GMC_GROUND_MODE=road + GMC_MODEL=similarity
(road-chain fallback estimator parity with ground-full).
Acknowledged confound: train-side chain composition co-varies with factor R
(road chain is composed per-frame by construction; sim-ship training ego is
direct) — inherent to end-to-end arms, note in ledger.

Implementation: new env `GMC_GROUND_MODE ∈ {point, road, full}` splitting the
coupled GMC_GROUND flag (manager.py + dataset.py; cache key gains ground_mode).
Regression guard: GMC_GROUND=1 behavior must remain byte-identical (spot-check
one cache entry vs existing ground cache before arms run).

Suffixes: `_sw12d_gpoint_seed{s}_warm11` → `results/ground_point/`;
`_sw12d_groad_seed{s}_warm11` → `results/ground_road/`.

## Interpretation rule (pre-registered)

Primary metric: MOVING@0.5 Δ vs sim baseline (Welch, n=3). Secondary: MOV@1.0,
pooled non-inferiority (−2σ gate vs 44.656), STATIC cost.

- Attribute the mechanism to the factor whose single arm recovers ≥50% of the
  full-arm MOVING gain (+0.665) AND is significant (t>2); other arm ≈ 0.
- Both arms recover ≥50% or additivity violated
  (|G1Δ + G2Δ − fullΔ| > 2·pooled-σ): declare INTERACTION — mechanism = joint,
  paper narrative must say so.
- Neither arm recovers ≥50%: attribution FAILED — full-arm gain suspect
  (seed luck / train-domain artifact); flag to user, consider n=5 on full arm.
- No ship adoption from this campaign; ledger + user+professor decision after.

## Queue

After LOSO grid repair (running): G1 → G2 → cego-oracle (re-queued, its own
pre-reg unchanged). No other GPU/CPU work on this line without user say-so.
