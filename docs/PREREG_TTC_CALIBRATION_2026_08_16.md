# PRE-REGISTRATION — confidence-gated temporal calibration of fused scores (Track C2)

Registered 2026-08-16 before any number exists. User authorized. Inspired by
C²RMOT (anonymous ACM submission, ~/Downloads/8_C_2_RMOT_Language_Guided_Com.pdf):
inference-only, per-track referring-memory + positive-residual calibration.
CLOSED_LEVERS check: NOT ScoreBuffer EMA (unconditional smoothing, removed
2026-08-10) — this is confidence-GATED memory with positive-only residual;
NOT in Gate C's search space (per-frame fusion forms; no cross-frame memory).

## Mechanism (adapted, minimal)

Per (expression, track), frames in temporal order, fused ship score
r_t = cs + b + α·gmc with α=0.5 (candidate ship, sim caches):
- memory update (confidence gate): if σ(r_t) ≥ θ_update → m ← r_t
- calibration (positive residual only): r̂_t = r_t + w·max(m − r_t, 0)
  (no memory yet → r̂_t = r_t). Decision threshold unchanged (r̂ > 0).
Omitted vs C²RMOT: embedding winner-gate/competition (no per-instance
embeddings in our caches) — this is the memory+residual core only; noted as
a weaker variant in any writeup.

## Hyperparameters & LOSO

- Grid: θ_update ∈ {0.5, 0.6, 0.7, 0.8} × w ∈ {0.5, 1.0} (8 cells).
- LOSO: 3 folds, per-fold pooled argmax → componentwise median (censoring at
  grid edges per axis, ≥2 censored ⇒ axis unresolved).
- Full-test at (θ\*, w\*), n=3 seeds (sim caches `_sw12d_seed{s}_nomema_sim_warm11`).

## Integrity & baselines

- w=0 must reproduce ship α=0.5 numbers exactly (calibration off) — verified
  on seed0 before the campaign.
- Baseline: candidate ship 44.656±0.078 @0.5 / MOV 30.045±0.091.
- Gate: REGRESSION iff pooled Δ<0 with Welch t>2; SUCCESS claim requires
  pooled > 44.656 + 2σ; anything between = recorded, no adoption claim.
- Prior context: C²RMOT reports +1.0~1.6 on query-based hosts (TempRMOT line);
  our host is two-stage with per-frame scores — transfer unknown, that is the
  question.

## Outputs

`results/ttc_sim/ttc_campaign.json`; ledger row on completion. No adoption
without user+professor.
