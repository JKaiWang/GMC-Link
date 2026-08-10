# ARGUMENT.md — Argument Blueprint + Stress Test

ARS Plan-mode **Step 3 (Argument Stress Test)**. Primary inputs: `paper/PLAN.md`, `CLAUDE.md`, memory index. All numbers traced to those sources; none invented. Paper: *Resolving Motion-Referring Expressions in Moving-Camera Videos via Global Motion Compensation*, MMAsia 2026 Regular.

---

## 1. Central Thesis

> A **plug-and-play, decision-level** module that compensates camera ego-motion via composed cumulative homographies recovers the **motion class** of referring expressions that camera-naive RMOT hosts systematically miss — and the size of the recovery is **inverse to the host's native motion ability**, identifying the module as a *motion-deficit filler* rather than a generic accuracy booster.

Two load-bearing halves:
- **(T1) Mechanism + remedy:** camera ego-motion contaminates raw bbox displacement → "moving" matches parked, misses moving; ego-compensation removes the contamination at decision level.
- **(T2) Characterization:** the gain is conditional (host-deficit-dependent), not universal. This is the paper's intellectual novelty and also its honesty firewall (it *predicts* the small FH gains instead of hiding them).

---

## 2. Sub-Arguments (3-5) with CER Chains

### SA1 — Camera ego-motion is the mechanistic cause of motion-class failure, and ego-compensation is the decisive remedy.
- **Claim:** Hosts read motion from raw bbox pixel displacement; under camera ego-motion that displacement is dominated by the camera's, so motion-class expressions systematically mismatch. Removing the ego component is the single decisive intervention.
- **Evidence:**
  - rawvel-collapse ablation: replacing residual velocity with raw velocity collapses the model, ΔΔ=+34.93 (the ego term carries essentially all the motion-class signal). [`project_film_ego_injection_results`]
  - FH ego-pixel diagnostic: raw static-residual 10.25px → oxts-compensated 1.43px, ratio **7.17×** — direct measurement that uncompensated displacement is ~7× the true residual. [`project_fh_ego_pixel_diagnostic_2026_06_02`]
  - FlexHook (a comparison host) uses raw bbox displacement with no ego model — the differentiator is concrete, not hypothetical. [`project_flexhook_no_ego_compensation`]
- **Reasoning:** A controlled ablation that removes only the ego term and watches the motion class collapse establishes *necessity*; the pixel-ratio diagnostic establishes *magnitude*. Together they license "decisive component," not merely "contributing component."
- **Strength: STRONG (84).** Mechanism is falsifiable and was falsification-tested. Capped below Compelling because ΔΔ=+34.93 is reported as a within-pipeline ablation metric (macro/AUC-adjacent), and the headline HOTA gains are far smaller — the mechanism is decisive *for the motion class in isolation*, which the wording must preserve.

### SA2 — Plug-in gain is inverse to host native motion ability ("fills the motion deficit").
- **Claim:** The plug-in helps motion-blind hosts most; gain is monotone-inverse to native MOVING ability.
- **Evidence:** 3-host MOVING decomposition — iKUN native 20 / GMC +8.6; FH-V1 native 43 / +2.1; FH-V2 native 48 / +0.2. Monotone-inverse across all three. [`project_gmc_contribution_vs_host_motion_deficit_2026_05_26`]. Corroborated independently by the two FH negatives: Path B FH-V2 plug-in −0.047 and Mode-2 architectural ego −0.091 — both near-native-ceiling hosts show no lift, exactly as the law predicts. [`project_pathB_ego_motion_sota_2026_05_27`, `project_fh_ego_lean_v2_negative_2026_06_04`]
- **Reasoning:** Three ordered points + two independent corroborating negatives is a consistent monotone trend, and the negatives are *risky predictions that came true* (the law forbade FH gains; FH gains were absent). That is stronger than a fitted correlation.
- **Strength: ADEQUATE → STRONG (68, conditional on rescope).** As "we observe a monotone-inverse relationship and it predicts our cross-host negatives" it is Strong. As "gain ∝ 1/native ability" (a quantitative law) on **n=3 hosts** it is a hasty generalization (see §5 flag). Rating reflects the honest, rescoped phrasing.

### SA3 — Decision-level fusion is the only viable injection site.
- **Claim:** Motion must be fused at the decision (score) level; feature-level injection regresses.
- **Evidence:** Feature-level injection of motion into the host = −21.7% F1 [CLAUDE.md design decisions]. Reinforced by a wall of feature/early-concat negatives: CLIP 64D concat −0.057, late-concat 0.731, sw CLIP early-concat n=3 NEG all hosts. [`project_exp39_clip_concat_negative`, `project_exp41_late_concat_negative`, `project_sw_clip_earlyconcat_flat_2026_05_25`]. Per-class pooled Δ at decision level: 9/9 POS, 7/9 sig at α=0.01, biggest +4.562 (iKUN MOVING). [`project_per_class_pool_all_positive`]
- **Reasoning:** A clean A/B (same signal, two injection sites, opposite sign) plus broad replication of the feature-level failure across encoders and archs supports the design choice strongly.
- **Strength: STRONG (80).** The −21.7% is one headline number, but it is backed by ~5 independent feature-injection negatives, so it is not a single anecdote. Capped below Compelling because "only viable" is a universal over a finite tested set; "decision-level is the robust site, feature-level reproducibly regresses" is the defensible form.

### SA4 — The module beats published baselines on 2/3 hosts at a fixed tracker, and the wins are real (n=3, std-bounded).
- **Claim:** GMC+host beats published HOTA on iKUN (+0.070) and FH-V2 (+0.281); FH-V1 retains a structural gap.
- **Evidence:** iKUN 44.634 ± 0.066 vs paper 44.564 (+0.070); FH-V2 42.807 vs paper 42.526 (+0.281); FH-V1 53.526 (gap structural, host-specific). All n=3 multi-seed, 3-/4-seq pooled HOTA, `gt_template_old` paper-canonical convention reproducing paper 44.564. [`project_ship_adoption_sw_recipe_noema_2026_05_21`]. Against the `{host}+GMC` raw-cos anchor B2 (iKUN 44.272 / V1 53.121 / V2 42.532) the ship recipe adds further. [`gmc_baseline_aligner_sw_2026_05_21`]
- **Reasoning:** Pooled HOTA in the paper-canonical convention, multi-seed, is the correct adjudication metric (per project methodology: HOTA adjudicates, AUC skipped).
- **Strength: ADEQUATE (60).** FH-V2 +0.281 is comfortably outside its seed noise and is genuinely a beat. **iKUN +0.070 vs ±0.066 is ~1σ — inside-noise and indefensible as a standalone "beat."** The 2/3 framing survives only if iKUN is carried by the per-class motion story (SA2), not by the pooled tenth-of-a-point. See §5 + rescope R1.

### SA5 — The contribution is tracker-orthogonal; not reaching SOTA 48.84 is a legitimate scope boundary, not a failure.
- **Claim:** Gains are reported at a fixed tracker; leaderboard-top needs a different detector/tracker (DDETR) and is out of scope. The plug-in characterization is the contribution.
- **Evidence:** SOTA 48.84 requires the paper's DDETR tracker output, which the original author refused to release 3× [`project_ddetr_data_unavailable`]. Public-tracker substitutes all <40 (ByteTrack 39.0–39.8, BoT-SORT 35.12, DETR-NS 32.4) — the bottleneck is the *detector*, not our module. [`project_path2_ddetr_public_trackers_negative`, `project_phase5g_cascade_detr_negative`]. Pooled ceiling on the available YOLOv8-NS tracker is ~44.6 regardless of method (FiLM macro +0.642 evaporates to +0.053 pooled). [`project_film_pooled_marginal`]
- **Reasoning:** The 48.84–44.6 gap is demonstrably attributable to detector recall, an axis the module does not touch. Scoping it out is supported by the evidence, not asserted to dodge.
- **Strength: STRONG (76).** The scope boundary is *evidenced* (detector-bound, data-unavailable, ceiling measured) rather than declared. The reviewer-facing risk is presentation, not substance.

---

## 3. Counter-Arguments + Rebuttal Strategy (per sub-argument)

| SA | Strongest counter | Rebuttal strategy | Holds? |
|----|-------------------|-------------------|--------|
| SA1 | "ΔΔ=+34.93 is an internal ablation metric; the HOTA gain is tenths. The mechanism may be real but trivial." | Separate the two claims explicitly: ego-comp is *decisive for the motion class in isolation* (ablation + 7.17× pixel ratio); the pooled HOTA gain is small because the motion class is a minority of expressions (pool dilution, mechanically explained in `project_pool_per_expr_disagreement_explained`). Report per-class MOVING HOTA, not just pooled, in Table 3. | Yes — if per-class metric is foregrounded. |
| SA2 | "n=3 hosts is an anecdote, not a law." | Drop "∝"/"law"; state "monotone-inverse across our three hosts, and it correctly predicts two independent cross-host negatives." Frame as a *characterization with predictive power*, not a fitted relationship. | Yes — only in rescoped form (R2). |
| SA3 | "−21.7% F1 is one number; F1 is not your eval metric (you ship on HOTA)." | Cite the ~5 corroborating feature/early-concat HOTA/AUC negatives, not just the F1 figure. The pattern, not the number, carries it. Note F1 here is the *historical* motivating result, replicated in spirit by HOTA negatives. | Yes. |
| SA4 | "iKUN +0.070 is within ±0.066 std — that's noise; you can't claim a beat." | Concede the pooled iKUN beat is marginal; do **not** lead with it. Lead iKUN with the per-class result: MOVING pooled Δ up to +4.562, 7/9 per-class POS sig at α=0.01. The honest pooled claim for iKUN is "matches paper while substantially improving the motion class," with FH-V2 +0.281 as the clean pooled beat. | Partially — needs R1 rescope or it is the paper's weakest seam. |
| SA5 | "'Out of scope' is a dodge for not reaching SOTA." | Show the gap is detector recall (public trackers all <40; ceiling measured at ~44.6). The module is evaluated *at parity of tracker* against each host's own published number — the fair comparison. SOTA needs a different detector, an orthogonal axis. | Yes. |
| Thesis | "Why not just use a temporal tracker (TempRMOT) and skip the bolt-on?" | TempRMOT has native temporal memory; GMC is redundant there and *regresses* it (Stage D all 3 β arms Δ−3.8..−5.4, `project_exp37_stage_d_tracker_class_dichotomy`). The module's value proposition is *precisely* for spatially-naive hosts you cannot or do not want to retrain — the deficit-filler framing makes this a feature, not a limitation. Switching trackers is a different, heavier intervention (retrain, different detector) than a plug-in. | Yes — this is a genuine strength, surface it in Related Work carve-out (already in PLAN Ch2). |

---

## 4. Logical Flow Diagram

```
                         THESIS
         plug-in ego-comp recovers motion-class exprs;
            gain inverse to host motion deficit
                            |
     +----------------------+----------------------+--------------------+
     |                      |                      |                    |
   [SA1]                  [SA3]                  [SA4]                [SA5]
 ego-comp is          decision-level         beats 2/3 at         tracker-
 the decisive          is the only           fixed tracker        orthogonal;
 remedy                viable site           (n=3, std)           48.84 OOS
 (rawvel ΔΔ34.93,     (feat-lvl -21.7%      (iKUN +0.070*,       (detector-
  7.17x px)            +5 NEG concats)        FH-V2 +0.281)        bound <40)
     |                      |                      |                    |
     +----------+-----------+----------+-----------+----------+---------+
                |                      |                      |
                v                      v                      v
            establishes            establishes            bounds the
            MECHANISM              DESIGN                  CLAIM honestly
                |                      |                      |
                +----------------------+----------------------+
                                       |
                                     [SA2]  <-- NOVELTY KEYSTONE
                          gain ~ 1/native motion ability
                    (iKUN 20/+8.6 . FH-V1 43/+2.1 . FH-V2 48/+0.2;
                     predicts FH-V2 plug-in -0.047 & arch -0.091)
                                       |
                                       v
                       UNIFIES: explains why iKUN's pooled
                       beat is tiny (small motion deficit at pool)
                       AND why FH gains are tiny (near native ceiling)
                       --> turns the weakest numbers INTO evidence

  * iKUN +0.070 is ~1sigma at pool; load-bearing support is per-class
    (MOVING Delta up to +4.562, 7/9 sig) routed through SA2, not pooled.
```

Key structural property: **SA2 is the keystone that absorbs the paper's weakest seams.** The two facts a reviewer attacks (iKUN's tiny pooled beat, FH's tiny gains) are exactly what the deficit law *predicts*. The argument is anti-fragile if SA2 is foregrounded and SA4's pooled iKUN number is demoted.

---

## 5. Argument Strength Assessment Table

4-level rubric: Compelling 90-100 / Strong 70-89 / Adequate 50-69 / Weak <50.

| # | Sub-argument | Strength | Score | Primary risk |
|---|--------------|----------|-------|--------------|
| SA1 | Ego-comp is the decisive remedy (mechanism) | Strong | 84 | "decisive" is class-isolated, not pooled — must say so |
| SA2 | Inverse-deficit characterization (novelty keystone) | Adequate→Strong* | 68 | n=3 hosts; "law"/"∝" = hasty generalization |
| SA3 | Decision-level is the only viable injection site | Strong | 80 | "only" universal; F1 metric off-target (backed by HOTA negs) |
| SA4 | Beats published baselines 2/3 at fixed tracker | Adequate | 60 | **iKUN +0.070 ≈ ±0.066 = inside noise** |
| SA5 | Tracker-orthogonal; 48.84 out of scope | Strong | 76 | Reads as a dodge if not evidenced as detector-bound |
| — | **Thesis (composite)** | **Strong** | **74** | Hinges on SA2 carrying SA4's weak seam |

\* SA2 scores Adequate as literally worded ("∝ 1/native"); Strong (≈74) in the rescoped "monotone-inverse, predicts our negatives" form. Reported at 68 to reflect that the rescope is mandatory, not optional.

---

## 6. Weak-Argument Indicator Audit (8 checks)

| # | Indicator | Present? | Where / Verdict |
|---|-----------|----------|-----------------|
| 1 | Circular reasoning | **No** | Mechanism (SA1) and metric (SA4) are independent; ablation isn't assumed by the claim. |
| 2 | Appeal to authority | **No** | Claims rest on own ablations/HOTA, not on citing iKUN/FlexHook as authorities. (Watch: don't justify the recipe by "the paper does it.") |
| 3 | Hasty generalization | **FLAG (SA2)** | "gain ∝ 1/native ability" generalized from **n=3 hosts**. Rescope to "monotone-inverse across our three hosts + predicts 2 cross-host negatives." Do not call it a law. |
| 4 | False dichotomy | **MINOR FLAG (SA3)** | "decision-level is the *only* viable site" is a binary over a finite tested set. Soften to "decision-level is robust; feature-level reproducibly regresses across 5 tested injections." |
| 5 | Correlation ≠ causation | **Watch (SA2)** | The inverse-deficit is correlational across 3 hosts. Mitigated because SA1 supplies the *causal mechanism* (ego-comp fills motion gap) — keep SA1→SA2 link explicit so SA2 is not standalone correlation. |
| 6 | Single-context generalization | **Partial FLAG** | All results on Refer-KITTI (V1+V2) only; one dataset family, autonomous-driving domain. State the domain scope; don't imply generic moving-camera video. (Honest scope, not fatal for a systems paper, but must be named in Limitations.) |
| 7 | Undefined key term | **FLAG** | "motion class," "native motion ability," "structural gap" (FH-V1), and "deficit" must be defined operationally. "Native motion ability" = host MOVING-class HOTA without GMC (20/43/48). "Structural gap" = host-specific FH-V1 deficit vs its own paper number — define or it reads as an excuse. |
| 8 | Counter stronger than argument | **No** (one near-parity) | Only SA4's pooled-iKUN counter ("+0.070 is noise") is at parity with the claim. Neutralized by demoting pooled iKUN and routing iKUN's weight through per-class SA2. No counter is net-stronger. |

**Net:** 3 substantive flags (hasty generalization, undefined terms, single-context) + 2 minor (false dichotomy, correlation watch). All are *fixable by rescoping language*, none require new experiments. The argument structure is sound; the exposure is in word choice.

---

## 7. Adversarial Probe Responses (the six MMAsia-reviewer angles)

**P1 — "Inverse-deficit on 3 hosts: claim or anecdote?"**
Honest phrasing: *"Across our three hosts the plug-in's MOVING gain is monotone-inverse to native motion ability (iKUN 20→+8.6, FH-V1 43→+2.1, FH-V2 48→+0.2), and this relationship correctly predicts two independent cross-host negatives where the law forbade a gain (FH-V2 plug-in −0.047, FH-V2 architectural ego −0.091)."* That is a *characterization with out-of-sample predictive checks*, not a curve fit. **Rebuttal holds (Strong)** — but only without "∝"/"law"/"scaling." 3 points cannot support a functional law; they can support a monotone characterization that made and survived risky predictions.

**P2 — "iKUN +0.070 ± 0.066: within noise. Defensible as a beat?"**
**Concede the pooled point.** It is ~1σ; calling it a "beat" standalone is indefensible and a sharp reviewer will catch it. Defensible claim: iKUN **matches** its published pooled HOTA *while substantially improving the motion class* (MOVING pooled Δ up to +4.562; 7/9 per-class POS sig at α=0.01). The clean pooled beat is FH-V2 (+0.281, outside seed noise). **Rebuttal holds only after rescope R1.** As written in PLAN Table 1 ("+0.070, Beat 2/3") it is Weak.

**P3 — "FH-V1 doesn't beat paper — does 2/3 oversell?"**
"2/3 paper-beat" is defensible *iff* FH-V1's gap is defined and shown host-specific, not method failure: GMC still adds over the FH-V1 `+GMC` anchor (B2 53.121 → ship 53.526), so the module works on FH-V1; the residual to the FH-V1 *paper number* is a host reproduction gap. Better headline: *"improves all three hosts over their GMC-equipped baseline; exceeds the published number on two."* **Rebuttal holds (Adequate-Strong)** if "structural gap" is operationalized (R3); leaving it as an undefined hand-wave is the risk.

**P4 — "48.84 not reached — scope or dodge?"**
Legitimate scope. Evidence the boundary: SOTA needs DDETR tracker output (author refused 3×); every public-tracker substitute lands <40 (ByteTrack 39.0–39.8, BoT-SORT 35.12, DETR-NS 32.4); measured pooled ceiling on the available tracker ~44.6 for *any* method. The gap is detector recall, orthogonal to motion reasoning. We compare **at parity of tracker** to each host's own number — the fair test. **Rebuttal holds (Strong).** Frame as "evaluated at fixed tracker," never "we could reach SOTA but chose not to."

**P5 — "Aligner is representation-bound, 26 NEG levers — doesn't that undercut the contribution?"**
Invert it. The contribution is **not** the aligner; PLAN explicitly keeps Stage 3 lean. The 26 NEG levers are *evidence the easy wins are exhausted* and that the remaining headroom (oracle: ship 44.58 → oracle_motion 50.71 = +6.13, no new tracker, `project_signal_decomp_native_vetoes_gmc_2026_05_26`) is a **motion-representation** problem, which is honest future work, not a hole in the present claim. The present claim is "a simple decision-level ego-comp module recovers motion class" — and simplicity is a stated value (`feedback_simplicity_over_tiny_hota`). **Rebuttal holds (Strong)** — but only if the paper *does not* sell the aligner as novel. If any draft sentence claims aligner novelty, this counter becomes lethal.

**P6 — "Why not a temporal tracker (TempRMOT) instead of bolting on GMC?"**
Direct evidence it backfires: cascading GMC onto TempRMOT (native temporal memory) regresses all 3 β arms (Δ−3.8..−5.4). The module is *for* spatially-naive hosts you will not retrain. Swapping to a temporal tracker is a heavier, different intervention (retrain + often a different detector) and addresses a different host class. The deficit-filler framing (SA2) makes "use it where the host is motion-blind" the precise, principled deployment rule. **Rebuttal holds (Strong)** and converts the objection into a contribution (the carve-out is informative).

---

## 8. Chapter Plan (6 fields per chapter)

### Ch 1 — Introduction (~700 w)
- **Core Argument:** A mechanistic, camera-induced failure (ego-motion contaminates bbox displacement) makes camera-naive hosts misread motion-class expressions; a plug-and-play decision-level ego-comp module fixes it, and the fix is deficit-conditional.
- **Supporting Evidence:** parked-car-displaces-because-camera-moves intuition; rawvel-collapse ΔΔ=+34.93 forward-referenced; contribution bullets C1–C3 + scope guard.
- **Counter-arguments:** "small HOTA gains" / "why not retrain the host."
- **Response:** gains are class-concentrated (pool dilutes); plug-in = no retrain, the whole point; deficit law explains gain size.
- **Argument Strength:** Strong (frames T1+T2 honestly; opener is falsifiable-mechanism, the strongest available hook).
- **Est. Word Count:** ~700.

### Ch 2 — Related Work (~0.75 pg)
- **Core Argument:** No prior work compensates camera ego-motion *for motion-language alignment*; GMC-in-tracking is single-frame IoU-gating, RMOT hosts are camera-naive, and temporal trackers are a different (out-of-scope) class.
- **Supporting Evidence:** TransRMOT/iKUN/FlexHook camera-naive; BoT-SORT GMC = IoU-gating only; TempRMOT carve-out (Stage D Δ−3.8..−5.4).
- **Counter-arguments:** "GMC is a solved tracking primitive" / "temporal trackers already do this."
- **Response:** solved for IoU-gating, never fused with language; temporal trackers regress under GMC → orthogonal niche.
- **Argument Strength:** Strong (gap-funnel; the TempRMOT carve-out pre-empts P6 in-text).
- **Est. Word Count:** ~550.

### Ch 3 — Method (~1.75 pg)
- **Core Argument:** Composed cumulative homography → multi-scale residual velocity (13D) → lean two-tower alignment → decision-level additive fusion is the minimal pipeline that isolates and exploits ego-residual motion.
- **Supporting Evidence:** Eq1 cumulative composition, Eq2 residual velocity, Eq3 additive fusion; multi-scale = dominant ablation gain (+0.047 sep); decision-level vs feature-level −21.7% F1.
- **Counter-arguments:** "aligner is trivial / under-engineered" / "18-param recipe is overfit."
- **Response:** aligner deliberately lean (representation-bound, not the contribution); recipe is per-arch score-scale calibration, with auto-derivation (std-matching) falsified — the 18 params are irreducible, not arbitrary (`project_variant_b_std_matching_negative`).
- **Argument Strength:** Strong (design choices each backed by an A/B; the recipe-overfit counter is the one to pre-empt with the std-match negative).
- **Est. Word Count:** ~1100.

### Ch 4 — Experiments (~2 pg)
- **Core Argument:** At fixed tracker, GMC improves all three hosts over their GMC-equipped baseline, exceeds the published number on two, and the gain magnitude follows the motion-deficit law; ablations pin the cause on ego-comp.
- **Supporting Evidence:** Table 1 (HOTA n=3±std + Δ-paper: iKUN 44.634/+0.070, FH-V1 53.526/gap, FH-V2 42.807/+0.281); Table 2 (deficit decomp 20/+8.6, 43/+2.1, 48/+0.2); Table 3 (ablation, MOVING-class metric, rawvel collapse); Fig 2 qualitative recovery; per-class 9/9 pool-POS (supplement).
- **Counter-arguments:** P2 (iKUN noise), P3 (FH-V1 gap), P1 (n=3 law).
- **Response:** lead iKUN with per-class MOVING (+4.562, 7/9 sig), report pooled as "matches"; FH-V1 gap = host reproduction, GMC still adds over B2; deficit stated as monotone characterization + 2 predicted negatives, not a law.
- **Argument Strength:** Adequate→Strong (the chapter where rescoping is decisive; Table 1's "+0.070 Beat" wording must change or this drops to Adequate).
- **Est. Word Count:** ~1300.

### Ch 5 — Conclusion + Limitations (~0.5 pg)
- **Core Argument:** A simple plug-in recovers motion-class expressions proportional to host deficit; honest about FH-V1 gap, 48.84 scope, representation-bound ceiling, single-dataset domain, and TempRMOT exclusion.
- **Supporting Evidence:** restate T1+T2; oracle headroom +6.13 (motion classifier, no new tracker) as future work; detector-bound SOTA gap; Refer-KITTI-only scope named.
- **Counter-arguments:** P4 (scope dodge), P5 (representation-bound undercut).
- **Response:** scope = evidenced detector boundary; ceiling = honest future direction (motion representation), present claim stands on simplicity + deficit characterization.
- **Argument Strength:** Strong (limitations section is the paper's credibility deposit; pre-empts P4/P5/single-context).
- **Est. Word Count:** ~400.

**Total ≈ 4050 words main text** (excl. figures/tables/refs), consistent with MMAsia 6pg+2ref sigconf budget.

---

## 9. Mandatory Rescoping Recommendations (ranked)

**R1 (critical) — Demote iKUN's pooled "+0.070 beat"; route iKUN's weight through the per-class motion result.**
PLAN Ch4 Table 1 currently reads "iKUN 44.634 (+0.070) … Beat 2/3." +0.070 vs ±0.066 is ~1σ; a reviewer kills "beat" on sight. Reword to: iKUN **matches** published pooled HOTA *while improving the motion class substantially* (MOVING pooled Δ up to +4.562; 7/9 per-class POS, sig at α=0.01). Reserve the word "beat" for FH-V2 (+0.281, outside noise). Keeps "improves 2/3, exceeds published on 1 cleanly + 1 marginally" — defensible. This converts SA4 from Adequate(60) to Strong.

**R2 (critical) — Replace "gain ∝ 1/native ability" / "law" with "monotone-inverse across our three hosts, validated by two predicted cross-host negatives."**
n=3 cannot support a functional/scaling law (hasty-generalization flag #3). The predictive-negative framing is *stronger* anyway: it shows the relationship made risky forecasts (FH-V2 plug-in −0.047, arch −0.091) that held. Do this everywhere the INSIGHT "∝" appears (PLAN core_novelty bullet, C2).

**R3 (important) — Operationally define the load-bearing terms, especially "structural gap" (FH-V1) and "native motion ability."**
Undefined-term flag #7. "Native motion ability" := host MOVING-class HOTA without GMC (the 20/43/48 numbers). "Structural gap" := FH-V1's residual to its *own published number*, shown host-specific (GMC still lifts FH-V1 over its `+GMC` baseline B2 53.121→53.526). Without these definitions, "2/3 beat" and "structural gap" read as excuses; with them, they read as precise scope. Also name the single-dataset scope (Refer-KITTI V1+V2 only) in Limitations to clear flag #6.

---

### One-line bottom line
The argument is **structurally sound (composite Strong, 74)** and *anti-fragile* because the inverse-deficit keystone (SA2) turns the two weakest numbers (iKUN pooled, FH gains) into predicted evidence — **but only after R1+R2 rescoping.** As literally drafted in PLAN (iKUN "+0.070 beat," deficit "∝ law"), the paper exposes two reviewer-lethal seams; both close with wording changes alone, zero new experiments.
