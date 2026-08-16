# PRE-REGISTRATION — road-arm diagnostics (per-seq decomposition + signal separation)

Registered 2026-08-16, before results. Diagnostics only — NO ship numbers change.
Answers devil's-advocate challenge #1 (scene-overfitting) with data.

## Probe 1 — per-seq HOTA decomposition (new TrackEval runs on EXISTING predicts)

- Arms: sim (`_sw12d_seed{s}_nomema_sim_warm11`) vs groad (`_sw12d_groad_seed{s}_warm11`),
  α ∈ {0.5, 1.0}, seeds 0-2, seqs {0005, 0011, 0013}. Per-seq seqmap subsets of the
  existing alpha-run dirs; metrics pooled + MOVING per seq. No re-scoring.
- Output `results/road_diag/perseq.json`.
- Interpretation (pre-registered): per-seq MOVING Δ(road−sim), n=3 mean.
  CONCENTRATED iff one seq carries >80% of total positive Δ and the others are ≤0
  within 1σ → road narrative downgraded to scene-conditional.
  DISTRIBUTED iff ≥2 seqs positive → narrative holds (mechanism general on this set).

## Probe 2 — cache-level score separation (free, existing caches)

- Per (arm, seed, seq): for MOVING-classified expressions, positives = tids in the
  eval dir's gt.txt per frame, negatives = scored tids not in GT; separation =
  mean(raw_cos[pos]) − mean(raw_cos[neg]).
- Question: does the road chain improve the SIGNAL (separation) and where —
  the honest "why" evidence A25 lacks (A21 showed static residuals are NOT the
  mechanism). Report per-seq separation Δ(road−sim).

## Probe 3 — α-heterogeneity note (free, existing fold JSONs + Probe 1)

- Per-seq α preference from Probe 1 (pooled at 0.5 vs 1.0 per seq) + A24/A27 fold
  argmax patterns (sim {0.2,1.5,0.5} vs road {0.2,2.0c,0.5} — same shape).
  Deliverable: robustness paragraph for the paper — heterogeneity pre-exists on the
  sim arm; road amplifies, does not create it.

No adoption decisions ride on these; they set the STRENGTH of the road analysis
section (mechanism section vs limitation footnote).
