# IMPROVEMENT_PLAN_2026_08_13 — full-pipeline audit → ranked plan

Source: 7-component audit + adversarial verification vs `docs/CLOSED_LEVERS.md` + memory
(2026-08-13, 13 agents; raw findings: job workflow wf_ade2a8bf-96b journal).
Every candidate below survived a kill-attempt against the 31-lever graveyard.

## 1. Diagnosis — why the 12D single-α ship underperforms

1. **Single α is a measured Pareto compromise, but the old recipe's extra gain was
   partly tuned-on-test.** Per-class optima diverge (iKUN: APPEAR peaks α=0.2 at 46.511,
   MOVING still rising at α=1.0 → 31.093; FH V1 MOVING rising to α=10; `results/alpha_sweep_*.csv`).
   The 18-param recipe earned +0.410/+0.416/+0.281 vs single-α +0.288/+0.047/+0.158 —
   BUT honest LOSO refit of the per-axis form gave iKUN pooled 44.316 < single-α 44.512
   (`project_loso_calibration_transfer_2026_07_04`). Single-α is the honest baseline;
   the recoverable gap is smaller than the raw recipe numbers suggest.
2. **Host-deficit inverse law caps FH.** GMC fills ~17%/6%/1% of iKUN/FH-V1/FH-V2's
   motion deficit (`project_gmc_contribution_vs_host_motion_deficit_2026_05_26`).
   FH V1 gain +0.047±0.022 is barely 2σ. iKUN is the only host with real headroom.
3. **The audit found real, unfalsified defects** (none previously documented):
   - **Ship training has NO False-Negative Masking** despite CLAUDE.md claiming
     "InfoNCE + FNM": default `AlignmentLoss.forward` ignores `sentence_ids`
     (`losses.py:34-60`); at B=256 with 6 group labels ~30% of in-batch negatives are
     same-group false negatives (~78/255 per anchor; ~117 for "moving").
   - **Inference-only MotionBuffer EMA (α=0.3)** on the 8 velocity dims
     (`manager.py:373`) — training features are raw (`dataset.py`). The one prior
     measurement of removing it was POSITIVE for iKUN (pool +0.071..+0.100, MOVING
     +0.75..1.02, FH flat; commit b00d232 / `project_noema_validation_2026_05_19`),
     reverted without adoption, never tested on the 12D ship.
   - **25.1% of eval track-frames are warmup** (long gap undefined; 5.5% all-zero
     velocity = "stationary"-coded) fused at full α — on FH the GMC term also sits
     inside the detection gate.
   - **V2 per-class grouping is label-space-broken**: classifier runs on paraphrased
     expr_id slugs, cache scores canonical raw_sentence; 108/862 exprs disagree; the
     V2 "MOVING" row is 38% canonical-APPEARANCE. The paper-toxic "V2 MOVING negative"
     row is confounded by this AND localizes to seq 0019 (hold-0019 fold: MOVING RISES
     with α, `results/loso_fh_v2_hold0019/`).
   - **LOSO clobber is ACTIVE on disk right now**: `hota_eval_flexhook_v2_raw_gmc_sw12d_seed*/alpha*/result.json`
     currently hold 3-seq fold outputs (pooled 51.006), not full-test — the exact
     landmine of `project_loso_outsuffix_clobber_landmine_2026_08_11`.
   - **iKUN LOSO fragile**: fold argmaxes {0.2, 1.0-censored-at-grid-boundary, 0.5};
     fold-chosen α=1.0 is full-test −0.444; grid step 0.2 leaves the peak unresolved.
   - Keyword router has 15 stems (docs claim ~38); 14/126 V1 direction exprs
     (counter/same/horizon-direction) route to APPEARANCE.
   - 7/916 frame transitions emit wild homographies (max 5592px corner displacement)
     poisoning ~4.3% of (frame,gap) ego slots via cumulative composition.

## 2. DO-NOW (this month, ranked; 1–2 are prerequisites for everything)

| # | Item | Verdict | Cost | Gate |
|---|---|---|---|---|
| 1 | Eval-protocol hardening | OPEN | ~1 h | assertions pass |
| 2 | V2 canonical regrouping audit | OPEN | <1 h CPU | report both groupings |
| 3 | Warmup validity mask (cache post-filter) | OPEN | ~1 h + sweeps | pooled ≥ ship |
| 4 | Remove inference-only MotionBuffer EMA | OPEN | ~1–2 d GPU | pooled ≥ ship, iKUN MOVING ≥ 30.222 |
| 5 | Group-level FNM in stage-1 InfoNCE | OPEN | ~1 GPU-d | pooled ≥ ship on ≥2/3 archs |

**2.1 Eval-protocol hardening (fold-scoped paths + fatal missing-cache).**
Fold-encode run dirs when `GMC_EVAL_SEQS` set (`run_ikun_linear_additive.py:171`,
`run_flexhook_phase5_gmc_sweep.py:188`, `run_flexhook_v2_raw_sweep.py:191` + sweep
driver); make missing GMC cache fatal in FH scripts at α>0 (currently WARN→silent
native, vs iKUN crash). Verify: sha256 of full-test result.json unchanged after a fold
run; bogus `GMC_SUFFIX` exits nonzero; α=0 → 44.224 exactly. Then **regenerate the
clobbered V2 full-test predicts** (α=0, α=5, seeds 0-2). Protects the pending paper
rerun. No HOTA change by design.

**2.2 V2 canonical regrouping audit.** Re-run TrackEval per-class grouping on existing
predicts with classification by `raw_sentence` (V1 keyword list) instead of paraphrase
slug; optional 4th DIRECTION row for the 66 diluting exprs. Adjudicates whether "V2
MOVING negative" is a grouping artifact vs the host-deficit inverse law. Expect
null-to-attenuation; either way fixes paper narrative + V1/V2 comparability. (Depends
on 2.1's regenerated predicts.)

**2.3 Warmup validity mask.** ~50-line script deletes cache entries with contiguous
track history T ≤ 10 (= max(FRAME_GAPS), not a tuned hyperparam); consumers already
default missing → 0.0 = host-native. Suffix `_warm11`, rerun `run_alpha_sweep.py` all
archs, LOSO α*, n=3. Gate: pooled ≥ ship/arch; report FH V2 MOVING Δ vs 48.018.
Caveat logged: warmup cx/cy/w/h do carry appearance signal — effect may be small;
cheap test adjudicates.

**2.4 Remove inference-only MotionBuffer EMA.** Env `GMC_MOTION_EMA=0` bypass at
`manager.py:372-375` (small code change needed — flag doesn't exist yet); rebuild
caches 3 archs × 3 seeds (suffix `_nomema`), resweep, LOSO. Moves inference TOWARD
training distribution; prior direct measurement POSITIVE (iKUN), and deletes a stateful
component (simplicity-aligned). If 2.3 and 2.4 both pass independently, run the
combined arm before any ship decision.

**2.5 Group-level FNM.** ~10-line `AlignmentLoss.forward` change: mask off-diagonal
same-group logits to −inf both CE directions (`train.py:113` already passes expr_ids).
Retrain sw12d seeds 0-2, rebuild caches, resweep. The untested cell is precisely: pure
masking (no β-mining), group labels, HOTA-adjudicated — prior "FNM negligible" was
82-class sentence-level (~3 collisions), AUC-only, reverted not falsified. Either
outcome: fixes the CLAUDE.md doc mismatch or permanently closes FNM-at-HOTA.

## 3. LATER (ranked)

1. **CLIP-L/14 spatial rerank port onto 12D ship (iKUN-only)** — verifier's strongest
   candidate; ~+0.7 expected (spatial arm alone, held-out; NOT the +1.03 stack number —
   that included Path-B lidar ego). CLIP caches exist on disk
   (`rerank_clipL14_neuralsort_*_cache.json`); rerank code must be resurrected from git
   (commits 2091c84/5e56abb/6044422); use converged expr subset. Gate: pooled−σ >
   44.512+0.104, per-class veto. Scope call: appearance mechanism, likely OUT of the
   GMC-module paper — position as iKUN-stack bonus or next paper.
2. **iKUN grid + LOSO repair** — dense mid-grid {0.35..0.65} + extend {1.25,1.5,2.0}
   to un-censor fold hold0011; pre-register median-of-uncensored-argmax rule BEFORE
   reading results; pass UNION alpha list to avoid clobbering sweep CSV. ~1 d CPU.
   Mostly paper hardening; plausible +0.05–0.10.
3. **Two-α keyword-routed fusion (α_mot, α_app)** — PARTIAL. The genuine 1-vs-18 middle
   ground, but: LOSO prior says pooled recovery unlikely (44.316 precedent); sell as
   MOVING-anomaly-removal / per-class-tradeoff measurement with non-inferiority pooled
   gate; NO V2 3-α arm (recipe-split family falsified); **needs professor sign-off** —
   reverses the 3-day-old simplification.
4. **Degenerate-H sanity gate** (reject |h31|,|h32|>1e-3 or corner-disp>150px → reuse
   last-good-H; instrument must confirm fires on exactly the 7 flagged + count fallback
   firings). iKUN-only gate: MOVING > 30.222, pooled ≥ 44.512−0.104. MAGSAC arm
   strictly secondary.
5. **Direction-keyword router fix** — step-1 per-expr sign test on the 14 exprs first;
   reporting fix unconditionally (docs claim ~38 stems, actual 15/25; publish both
   routings side-by-side). HOTA effect conditional on item 3. Note: same-direction cars
   have near-zero residual (ego frame) — expect counter-POS/same-ambiguous split.
6. **Single-gap non-inferiority** — reuse EXISTING `sw12d_nomulti` seed weights (iKUN
   arm already run: MOVING 29.398 n=5 vs full 29.947, ~1σ deficit — that's the prior);
   spend only on FH cache builds + sweeps; decision rides on pooled parity incl. FH V2
   keeping +0.158. Only then true-8D.
7. **Hygiene riders**: per-seq ego-H cache shared across expressions (+`cv2.setRNGSeed`;
   determinism + build speed, HOTA-neutral by verification); advance ego state on
   detection-empty frames (correctness rider, seq-0013-only effect, pre-commit that
   null HOTA = success); V2 raw_sentence gap-fill (193/862 exprs silently fall back to
   paraphrase text — canonicalize via shared label id; APPEAR/STATIC-scoped, small).

## 4. DO-NOT (brushed against, killed)

- Positive-evidence clamp `max(gmc,0)` — WEAK; twice-closed family
  (`project_signal_decomp_native_vetoes_gmc`, `project_hota_direct_fusion_gate_c`);
  amputates within-frame discrimination on the negative half. At most the 1-h
  no-TrackEval deletion/addition count; do not pre-book the sweep.
- Per-expression mean-centering as a ship change — threshold-family, Gate C closed it;
  transductive test-time statistic (reviewer smell). Keep ONLY as a frozen-α*
  mean-only diagnostic arm (9-18 TrackEval runs) to decompose ship gain into
  threshold-shift vs discrimination — paper value either way.
- V2 3-α arm (α_moving=0) — falsified recipe-split family; reads as "module disabled
  where it looked bad".
- V2 canonical-text cache A/B — already ran and already the ship (`_raw` = raw_sentence;
  `project_flexhook_v2_raw_positive`); as proposed it's a half-day no-op.
- Anything in `docs/CLOSED_LEVERS.md` §fusion-forms / CLIP-sites / motion-rep /
  tracker-substitutes.

## 5. Strategy note (paper)

The ICASSP v2 story ("gain inversely proportional to host native motion ability") is
defensible but currently carries: (a) the confounded V2 MOVING row — items 2.1+2.2 fix
or honestly explain it for <2 h of CPU; (b) an attackable α* selection — LATER-2
hardens it; (c) numbers pending rerun — do NOT rerun before item 2.1 lands, the V2
result dirs are clobbered on disk right now. The module-side gains left (2.3/2.4/2.5)
are each plausibly +0.1–1.0 MOVING on iKUN and are train/eval-consistency fixes, i.e.
they strengthen the "clean module" story without adding hyperparameters. The
biggest-prize lever (CLIP rerank +0.7 iKUN) is real but off-story for this paper.
FH-side tuning has near-zero expected value (inverse law); do not spend GPU there
except as confirmation arms.
