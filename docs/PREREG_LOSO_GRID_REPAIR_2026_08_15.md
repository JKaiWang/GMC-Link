# PRE-REGISTRATION — iKUN LOSO grid repair (A7 / IMPROVEMENT_PLAN LATER-2)

Registered 2026-08-15 (session tmp; user to commit — repo writes blocked in this
background session). Written BEFORE any fold result on this arm exists.
Results adjudicated against this file only.

## Motivation (A7)

Prior iKUN LOSO (nomema_warm11 arm) fold argmaxes = {0.2, 1.0-censored-at-grid-boundary,
0.5}: grid step 0.2 leaves the peak unresolved and fold-hold0011's argmax sits on the
grid edge. Additionally the candidate ship (similarity arm) never had its own LOSO —
α*=0.5 was carried over. This campaign is BOTH the grid repair and the missing
sim-arm LOSO.

## Arm

- iKUN only. Caches `_sw12d_seed{seed}_nomema_sim_warm11` (candidate ship:
  similarity 4-DOF ego + no MotionBuffer EMA + warm11 mask), seeds 0,1,2.
- Fusion `s_final = s_host + α·s_gmc`, gate 0.0. α=0 must equal 44.224 exactly
  (integrity check, every fold and full-test).

## Grid (UNION — single canonical list, passed whole to avoid CSV clobber)

0, 0.1, 0.2, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 1.0, 1.25, 1.5, 2.0

(dense mid-grid 0.35–0.65 at step 0.05; extension 1.25/1.5/2.0 to un-censor hold0011)

## Protocol

- 3 folds: hold one of {0005, 0011, 0013}; tune on the other two
  (`GMC_EVAL_SEQS=<infold>`); per-fold argmax = α maximizing in-fold pooled mean (n=3).
- Full-test sweep at the same UNION grid → `results/model_sim/alpha_sweep_ikun.*`
  (supersedes the 7-point sweep with a 16-point superset).
- Fold outputs: `results/model_sim/loso_ikun_hold{0005,0011,0013}/`.
- Runner: `run_loso_grid_repair.sh` (this dir), queued behind the ground arm;
  logs `logs/12d/gridrepair_*.log`.

## Selection rule (pre-registered — no post-hoc alternatives)

- α* = **median of per-fold pooled-argmaxes over UNCENSORED folds**.
  A fold is censored iff its argmax lands on the grid maximum (2.0).
- If ≥2 folds censored: campaign result = "peak unresolved, grid extension needed" —
  do NOT pick an α* from this run.
- Even-count median falling between grid points: take the lower grid point
  (conservative, toward native).

## Report + gates

- Report full-test pooled AND per-class (MOVING/STATIC/APPEAR) at α*, n=3 mean±std;
  Δ vs current pick α=0.5 (44.656±0.078 / MOV 30.045±0.091) and vs native 44.224.
- This is protocol hardening: outcome recorded in RESEARCH_NOTES §10 either way
  (expected band: −0.05..+0.10 pooled). NO ship adoption from this run —
  user+professor sign-off required regardless of outcome.
- Baselines untouched: FH V1/V2 out of scope (inverse law, near-zero EV).
