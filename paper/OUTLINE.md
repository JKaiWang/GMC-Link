# Paper Outline — MMAsia 2026 Regular Paper (Phase 2 Deliverable)

**Title (working):** Resolving Motion-Referring Expressions in Moving-Camera Videos via Global Motion Compensation
**Venue:** ACM Multimedia Asia 2026, Regular Paper, acmart `sigconf`, 6 pages + 2 ref, double-blind.
**Target length:** ≈ 5,200 words (2-col sigconf; figures/tables eat space — budget conservative).
**Deliverable owner:** structure_architect_agent (ARS Phase 2).

---

## 1. Structure Pattern

**Selected pattern: Conference (problem→approach→evidence).**

Mapping to the locked 5-chapter plan in `paper/PLAN.md`:

| Conference slot | Paper section | PLAN.md chapter |
|---|---|---|
| Hook + gap + contributions | §1 Introduction | Ch 1 |
| Positioning / gap-funnel | §2 Related Work | Ch 2 |
| Approach | §3 Method | Ch 3 |
| Evidence | §4 Experiments | Ch 4 |
| Close + limits | §5 Conclusion & Limitations | Ch 5 |

**Why this pattern (validity argument).** The contribution is a *systems/mechanism* claim — a plug-in module that fixes a named, falsifiable failure mode (camera ego-motion contaminating raw-bbox motion reading). The Conference pattern front-loads the mechanism and back-loads cross-architecture evidence, which is exactly the Intro→Results payoff structure the plan demands (motion-deficit law stated as a contribution bullet in §1, discharged in Table 2). A survey or thesis-style "background-heavy" pattern would over-spend the 6-page budget on context; a method-first pattern without an explicit gap-funnel Related Work would weaken the "no one compensates ego-motion for motion-language alignment" novelty claim. Conference pattern satisfies all six quality gates within budget.

---

## 2. Overview

Six-page mechanism paper. The reader should leave §1 convinced the motion-class failure is **real and mechanistic** (camera motion is misread as object motion) and that a **plug-and-play, decision-level** fix exists with no host retraining. §2 funnels three literature strands (RMOT hosts, GMC-in-tracking, motion-for-grounding) each to the hole we fill. §3 (the largest section) details the four-stage pipeline with three equations and Fig 1, keeping the aligner deliberately lean because it is **not** the contribution (representation-bound ceiling). §4 carries the evidence: Table 1 (main HOTA, 3 hosts × n=3), Table 2 (the novelty — motion-deficit inverse law), Table 3 (mechanism ablation: rawvel collapse), and Fig 2 (qualitative recovery). §5 restates the inverse-deficit story, draws honest limits (FH-V1 structural gap, tracker-orthogonality, representation-bound ceiling, temporal-tracker carve-out), and points to richer motion representation as the future lever (oracle shows +5 pooled reachable without a new tracker). The appearance re-ranker (45.612, +1.032) appears as one off-thesis sentence banking the best number, with full method in supplement.

---

## 3. Detailed Outline

> Heading depth: Level 1 (§), Level 2 (§.x), Level 3 (§.x.y, core sections §3–§4 only). Max depth = 3 ≤ 5 (gate pass). Every lowest heading carries ≥150 words of planned content + a Purpose statement.

---

### §1 Introduction  (Level 1)  — target 700 w

**Purpose:** Make the motion-class failure feel real and mechanistic, establish that no prior work compensates ego-motion for motion-language alignment, and state the three contributions + scope guard so the reader knows what is and is not claimed.

*(No Level-3 split; four planned paragraphs as one Level-1 block. Planned content ≥150 w below.)*

**Planned content.** Open on the RMOT task: given a video and a referring expression like "moving cars" or "the car that is turning", a tracker must score which trajectories match. Para 1 (Pain/mechanism): hosts infer motion from *raw bounding-box displacement*; under camera ego-motion that displacement is dominated by the camera's own motion, so a parked car "moves" in pixels and a truly moving car can be masked — a systematic, falsifiable mismatch, concretely illustrated (parked car displaces in pixels because the camera pans). Para 2 (Gap): existing RMOT hosts (TransRMOT, iKUN, FlexHook) are camera-naive; prior global-motion-compensation in tracking (BoT-SORT-style) is single-frame and IoU-gating only, never fused with language. Para 3 (Approach): a plug-and-play decision-level module — composed cumulative homography → multi-scale residual velocity → motion-language contrastive alignment → additive fusion — with no host retrain and no detector swap. Para 4: contributions C1/C2/C3 (verbatim from plan) + scope-guard sentence (gains at fixed tracker; 48.84 SOTA out of scope, needs a different tracker). End by forward-pointing to the motion-deficit inverse law as the headline finding. Place a one-line teaser of Fig 1 ("our four-stage pipeline, Fig 1").

**Evidence used:** DT2U6YGG (TransRMOT/Refer-KITTI), 5WW4YXMU (iKUN), JXF98FKT (BoT-SORT GMC), [FlexHook key TODO], rawvel-collapse ΔΔ=+34.93 (forward ref), feature-level −21.7% F1 (forward ref), motion-deficit deltas iKUN +8.6 / FH-V1 +2.1 / FH-V2 +0.2 (forward ref).

**→ Transition to §2:** Last sentence of §1 ("…no prior system compensates ego-motion for the purpose of motion-language alignment") motivates a structured walk through the three literature strands that each leave this hole open.

---

### §2 Related Work  (Level 1)  — target 600 w

**Purpose:** Position the work in a gap-funnel: three mini-paragraphs, each ending at the specific hole this paper fills, plus the TempRMOT carve-out that bounds scope.

#### §2.1 RMOT methods and motion reading  (Level 2)  — 240 w
**Purpose:** Survey the RMOT host family and show all infer motion from raw bbox geometry without an ego model; carve out temporal-memory hosts.
**Planned content.** TransRMOT (Refer-KITTI origin, end-to-end transformer RMOT), iKUN (insertable knowledge-unification module over a frozen tracker), FlexHook (host we adopt as a second/third architecture), TempRMOT (temporal-memory RMOT). Funnel point: every one of these reads motion from raw bounding-box displacement or attention over raw boxes; none models camera ego-motion explicitly. **TempRMOT carve-out:** hosts with native temporal memory are *out of scope* because the module's residual-velocity signal is redundant against their internal temporal state, producing structural regression (Δ −3.8 to −5.4 observed on cascaded TempRMOT); the module targets spatially-naive hosts. This sets up the cross-architecture host selection (iKUN, FlexHook-V1/V2) used in §4 and pre-empts the "why not the strongest tracker" reviewer question. Keep absolute-HOTA leaderboard comparison out — that is the scope guard, discharged in §5.
**Evidence:** DT2U6YGG, 5WW4YXMU, [FlexHook key TODO], [TempRMOT key TODO]. Optional breadth: COAL DCE7BWEQ, CGATracker DSQBCUBU, Bootstrapping-RMOT VZ7IRQDL (cite only if space).

#### §2.2 Global motion compensation in tracking  (Level 2)  — 200 w
**Purpose:** Show GMC exists in tracking but is decoupled from language.
**Planned content.** BoT-SORT introduces a camera-motion-compensation (GMC) step (ECC/ORB-homography family) to correct Kalman predictions before IoU association. ORB-homography and ECC alignment lineage for frame-to-frame registration. Funnel point: in all prior uses, GMC corrects a *geometric association gate* (IoU) within a single tracker step — it is single-frame, never composed cumulatively across temporal gaps, and never fused with a language signal. No prior work compensates ego-motion to produce a *motion descriptor that is aligned against a referring expression*. This is precisely the gap our Stage 1–2 (composed cumulative homography + multi-scale residual velocity) and Stage 3 (motion-language alignment) fill. Distinguish our cumulative composition (warp original coords once with composed H) from per-frame iterative warping used in association GMC, foreshadowing the numerical-stability design decision in §3.2.
**Evidence:** JXF98FKT (BoT-SORT GMC), [ECC/ORB-homography key TODO].

#### §2.3 Motion representation for language grounding  (Level 2)  — 160 w
**Purpose:** Show grounding literature is appearance-dominated, leaving motion-class expressions under-served.
**Planned content.** Vision-language grounding and referring-segmentation/tracking pipelines (CLIP-based scorers, appearance-keyed matching) are dominated by *appearance* features; motion enters, if at all, as raw trajectory deltas without ego correction. Funnel point: motion-class referring expressions ("moving", "turning", "braking", "parked") are systematically under-served because the descriptor they hinge on (true object velocity) is corrupted by camera motion and is a small fraction of typical referring-expression benchmarks. This motivates a dedicated, ego-compensated motion channel fused at decision level. Tie directly to the per-class decomposition in §4 (MOVING is 10% of GT yet carries the largest GMC gain). Close the funnel: the three holes — no ego model in hosts, GMC never language-fused, grounding appearance-biased — are jointly closed by the proposed module.
**Evidence:** [CLIP key TODO], DT2U6YGG (Refer-KITTI expression distribution).

**→ Transition to §3:** Closing sentence of §2.3 ("we close all three gaps with a single decision-level module") hands directly to the four-stage method, with Fig 1 as the visual anchor.

---

### §3 Method  (Level 1)  — target 1,450 w

**Purpose:** Specify the four-stage pipeline precisely enough to reproduce, with three equations and Fig 1, while keeping Stage 3 (alignment) deliberately lean because the aligner is not the contribution.

**Fig 1 placement:** top of §3 (pipeline: frames → ORB homography → compose cumulative H → 13D residual velocity → two-tower alignment → additive fusion → HOTA). Referenced in the opening sentence of §3.

#### §3.1 Stage 1 — Ego-motion compensation  (Level 2)  — 250 w
**Purpose:** Estimate frame-to-frame homography robustly from background, not object, features.
**Planned content.** ORB feature extraction per frame; BFMatcher with Hamming distance and Lowe's ratio test (0.7); RANSAC homography estimation. A foreground mask (derived from current tracker boxes) excludes object regions so the homography locks onto static background, not moving objects — without it the estimated camera motion would absorb object motion and cancel the very signal we want. Output: a 3×3 homography H mapping previous frame → current frame. Justify ORB+homography over optical flow (Farneback/RAFT): on KITTI's near-planar driving scenes, ORB+RANSAC gives better outlier rejection and is cheaper; report the design decision and forward-reference the −ego ablation (§4.3) that proves the component is decisive (rawvel collapse). Note the planar-scene assumption explicitly as a scope condition (homography is exact for planar/rotational camera motion; KITTI driving scenes approximate this).
**Evidence:** JXF98FKT (GMC lineage), [ORB/ECC key TODO], rawvel-collapse ΔΔ=+34.93 (forward ref to §4.3).

#### §3.2 Stage 2 — Cumulative composition and residual velocity  (Level 2)  — 420 w
**Purpose:** Compose homographies across temporal gaps and isolate true object motion as a 13D descriptor.

##### §3.2.1 Cumulative homography (Eq 1)  (Level 3)  — 180 w
**Purpose:** Define the composed transform and justify warp-once-with-composed-H.
**Planned content.** Eq 1: H[t−k→t] = H[t−1→t]·H[t−2→t−1]·…·H[t−k→t−k+1]. The manager stores *original* (never-warped) centroid coordinates in history deques and warps once with the composed homography, rather than iteratively re-warping each frame; this is numerically more stable (one matrix multiply per query vs accumulated per-frame interpolation error). Contrast with single-frame association GMC (§2.2). State the frame-gap set used for composition {2, 5, 10}. Explain that warping the original centroid forward through H[t−k→t] yields where a *static* point at time t−k would appear at time t, so subtracting it from the observed centroid isolates motion the camera cannot explain. Keep the matrix-composition direction explicit to avoid the off-by-one ambiguity that plagued the GT conventions (cite the protocol note in §4.1).
**Evidence:** internal (Eq 1); design-decision "cumulative homography" from CLAUDE.md.

##### §3.2.2 Multi-scale residual velocity and the 13D vector (Eq 2)  (Level 3)  — 240 w
**Purpose:** Define residual velocity, multi-scale gaps, normalization, and the 13D feature.
**Planned content.** Eq 2: residual velocity = raw velocity − ego velocity, computed at gaps {2, 5, 10} (short/mid/long temporal scale). Ego velocity = displacement of the H-warped original centroid; raw velocity = displacement of the observed centroid. Normalize: v_norm = (v_pixel / img_dims) × 100 (resolution-invariant; VELOCITY_SCALE=100 keeps adapter inputs ≈1.0 magnitude). The **13D motion vector** = [res_dx×3 scales, res_dy×3 scales, dw, dh, cx, cy, w, h, snr]. Multi-scale is the dominant ablation gain (+0.047 separation; §4.3). SNR (signal-to-noise ratio of residual velocity) does not raise mean separation but cuts variance (±0.010→±0.007) — a variance reducer, framed honestly as a stabilizer not a separator. Full per-dimension breakdown deferred to supplement. Note bbox-state dims (w,h,cx,cy,dw,dh) carry appearance-correlated signal, which is why the appearance fusion axis (§3.4) is non-trivial. FRAME_GAPS must match between manager and training dataset.
**Evidence:** multiscale +0.047 sep, snr variance ±0.010→±0.007, 13D layout (CLAUDE.md), Eq 2.

#### §3.3 Stage 3 — Motion-language alignment (lean)  (Level 2)  — 230 w
**Purpose:** Map 13D motion and 384D language into a shared space via a deliberately small two-tower aligner; argue brevity is principled, not lazy.
**Planned content.** Two-tower `shared_weight` architecture: per-modality Linear adapter (motion 13→256, language 384→256) feeds a *shared* MLP trunk 256→512→512→256 → LayerNorm → L2-normalize. Language embeddings from SentenceTransformer all-MiniLM-L6-v2 (384D). Trained with symmetric InfoNCE (τ=0.07) plus False-Negative Masking (multiple training samples share an expression; FNM prevents same-sentence pairs being penalized as negatives). Inference uses **raw cosine** — no sigmoid, no EMA — which the fusion stage consumes directly. Critically, state that the aligner is *not* the contribution: an extensive arch/loss/encoder search (8+ levers) hit a representation-bound ceiling, so we spend the page budget on ego-compensation and fusion and keep the aligner minimal. This pre-empts "why such a simple aligner" by framing it as an evidence-backed scope decision (full negative-lever record in supplement).
**Evidence:** [CLIP/SentenceTransformer key TODO], InfoNCE τ=0.07 + FNM (CLAUDE.md), representation-bound ceiling (memory: exp34 series — cite as supplement).

#### §3.4 Stage 4 — Decision-level additive fusion (Eq 3)  (Level 2)  — 300 w
**Purpose:** Define the per-arch, per-axis additive fusion rule and justify decision-level over feature-level.

##### §3.4.1 Additive rule and per-class damping  (Level 3)  — 180 w
**Purpose:** State Eq 3 and the motion/appearance axis split with GMC-relevance damping.
**Planned content.** Eq 3: final = model_logit + α·(sc·raw_cos + thr), applied per architecture and per axis (motion vs appearance), where the axis is selected by ~38 motion keywords (moving, turning, parking, braking, …) detecting whether an expression is a motion-class or appearance-class query. Per-class GMC-relevance damping: the appearance-axis score-scale sc_a is 7–11× smaller than the motion-axis sc_m, because GMC is a motion signal and is *noise* on appearance expressions ("black cars"). The per-arch recipe also absorbs score-scale calibration (iKUN logits ≈[0,1] vs FlexHook ≈[−10,+10]). Present the compact 3-arch recipe table inline (motion/appear α, sc, thr per host); the full 18-parameter grid goes to supplement. Note that auto-deriving the recipe via std-matching was falsified (NEG, all 3 archs) — hand-tuned damping is the shipped choice, stated honestly.
**Evidence:** ship recipes (CLAUDE.md): iKUN motion α1.0/sc0.9/thr0.17 + appear α1.0/sc0.30/thr0.10; FH-V1 motion α0.65/sc10/thr3 + appear α1.0/sc3.5/thr0.9; FH-V2 motion α0.4/sc10/thr1.3 + appear α1.0/sc3.5/thr1.2. Eq 3.

##### §3.4.2 Why decision-level, not feature-level  (Level 3)  — 160 w
**Purpose:** Justify the injection site with the feature-level regression.
**Planned content.** Motivate decision-level fusion empirically: injecting motion features into the host's visual/text feature stream (feature-level) caused catastrophic regression (−21.7% F1). Decision-level fusion keeps the host's learned representation intact and adds an orthogonal, interpretable scalar at the logit. This also makes the module truly plug-and-play (no host weights touched) and architecture-portable (only a per-host scalar recipe differs), which is exactly what enables the cross-architecture validation in §4. Contrast with learned fusion heads: an F1-optimized MLP gate crashed pooled HOTA (−3.79), and a residual additive MLP on iKUN also regressed; the hand-tuned linear additive rule is strictly safer and is the shipped fusion. Frame the simplicity as a *defended* design point, not a missing experiment.
**Evidence:** feature-level −21.7% F1; learned-fusion-head −3.79 pool (CLAUDE.md / memory).

**→ Transition to §4:** Final sentence of §3.4 ("…we now measure this module across three hosts under a fixed-tracker protocol") hands to the experimental protocol.

---

### §4 Experiments  (Level 1)  — target 1,500 w

**Purpose:** Establish the protocol, then carry four pieces of evidence: main HOTA (Table 1), the motion-deficit inverse law (Table 2, the novelty), the mechanism ablation (Table 3), and qualitative recovery (Fig 2).

#### §4.1 Protocol, datasets, and baselines  (Level 2)  — 320 w
**Purpose:** Pin down dataset, metric, seeds, GT convention, and the two-baseline-per-host comparison so every later number is interpretable.
**Planned content.** Datasets: Refer-KITTI V1 (3-seq pooled test) and V2 (4-seq pooled). Add an explicit dataset-statistics line: #videos/#frames/#expressions and the motion-class share (MOVING ≈10%, STATIC ≈17%, APPEARANCE ≈73% of GT objects) — this directly motivates the per-class reporting in Tables 2–3. Metric: HOTA via TrackEval, 3-seq (V1) / 4-seq (V2) **pooled**, reported as mean ± std over **n=3** seeds. GT convention: `gt_template_old` is paper-canonical (NeuralSORT-aligned frame numbering); we reproduce paper iKUN 44.564 to validate the harness, and flag that the alternative convention drops HOTA ~6.4 via off-by-one misalignment (a protocol caveat, not a free gain). Two baselines per host: `{host}` (native) and `{host}+GMC` (raw cosine, simple fusion) — so every Δ is reported against *both* a no-module and a naive-module anchor. State hardware/runtime budget for ego-motion estimation (one-time cache build) here or note it as a complexity line.
**Evidence:** DT2U6YGG (Refer-KITTI V1/V2), gt_template_old paper-canonical + 44.564 repro, per-class GT shares (memory signal-decomp), n=3 protocol (CLAUDE.md).

#### §4.2 Main results: cross-architecture HOTA (Table 1)  (Level 2)  — 360 w
**Purpose:** Show the module holds across three architectures and beats published baselines on 2/3.
**Planned content.** Table 1: 3 hosts × {native baseline, +GMC ship} × HOTA (n=3 ± std) with Δ-vs-paper. Numbers: iKUN 44.634 ± 0.066 (+0.070 vs paper 44.564); FlexHook-V1 53.526 ± 0.087 (paper-gap structural); FlexHook-V2 42.807 ± 0.038 (+0.281 vs paper 42.526). Beat 2/3. Narrate: the module is additive on every host but the *magnitude* varies — set up Table 2. FlexHook-V1 paper-gap handled in a footnote as structural/host-specific (the host's strong native base already captures most motion; our additive scalar cannot overtake an internal-pipeline difference), explicitly NOT hidden. Emphasize n=3 ± std (tight stds support significance) and the fixed-tracker, same-detector protocol so the comparison is apples-to-apples. One off-thesis sentence here or in §4.5: an orthogonal CLIP-L/14 spatial re-ranker stacks on iKUN to 45.612 (+1.032), the first iKUN pooled >45.5 — full method in supplement, banked as best number but framed as outside the motion thesis.
**Evidence:** Table 1 numbers (CLAUDE.md ship), 5WW4YXMU (iKUN paper 44.564), [FlexHook key TODO] (paper 42.526), appearance stack 45.612 (+1.032, supp).

#### §4.3 The motion-deficit inverse law (Table 2)  (Level 2)  — 360 w
**Purpose:** Deliver the core novelty — plug-in gain is inverse to host native motion ability — as a defensible quantitative law.

##### §4.3.1 The inverse pattern  (Level 3)  — 200 w
**Purpose:** Present Table 2 and state the monotonic relationship.
**Planned content.** Table 2 (table, not figure — only 3 hosts, scatter too thin): rows host | native MOVING ability | GMC MOVING gain. iKUN native 20.25 / +8.6; FH-V1 native 43.34 / +2.1; FH-V2 native 48.37 / +0.2. Native MOVING 20→43→48 maps monotonically to GMC MOVING gain +8.6→+2.1→+0.2. State the law: the plug-in fills the host's *motion deficit* — it helps motion-blind hosts most (iKUN is pure-appearance, motion-blind; the module is the carrier of motion signal there) and adds little to motion-strong hosts (FH-V2 already reads motion from raw-bbox displacement). Pre-empt the natural misreading ("FlexHook benefits more because it scores higher"): FlexHook's high absolute HOTA is its strong native base, not the module. Report the deficit-fill fraction (iKUN ~17%, FH-V1 ~6%, FH-V2 ~1% of oracle−native).
**Evidence:** memory project_gmc_contribution_vs_host_motion_deficit (native/gain table), CLAUDE.md deficit deltas.

##### §4.3.2 Why pooled HOTA understates it  (Level 3)  — 160 w
**Purpose:** Explain the pooled-vs-per-class gap so reviewers don't read small pooled Δ as a weak result.
**Planned content.** MOVING is only ~10% of GT, so a large MOVING-class gain (iKUN +8.6) dilutes to a small pooled Δ (+0.71). Report both pooled and per-class so the contribution is visible. This is why Table 2 reports the MOVING-class metric, not pooled — pooled aggregates trajectory IDs cross-expression and hides the motion catastrophe. Note the additive-fusion veto mechanism honestly: a confidently-negative native logit can veto a correct GMC score on the hardest motion expressions (e.g., braking), and this veto is load-bearing (removing it floods false positives and hurts pooled DetA/AssA). State that the residual MOVING headroom is a *classification* gap (oracle MOVING recall/precision 20.5/26→69/80), not a coverage gap — motivating §5's future direction.
**Evidence:** memory signal-decomp (pooled +0.71, veto, oracle 50.71), per-class shares.

#### §4.4 Mechanism ablation (Table 3)  (Level 2)  — 300 w
**Purpose:** Prove ego-compensation is the decisive component and multi-scale/SNR contribute as claimed.
**Planned content.** Table 3 rows: full / −ego (raw velocity, no ego subtraction) / −multiscale (single gap) / −snr. Report a MOVING-class metric (pooled hides the motion catastrophe). Headline: removing ego compensation collapses performance — the rawvel ablation moves the metric by ΔΔ=+34.93, the single decisive-component proof that the homography step, not just "having a motion feature", is what works. −multiscale costs +0.047 separation (second-largest lever). −snr leaves mean separation flat but raises variance (±0.007→±0.010), confirming it as a stabilizer. Tie each ablation row back to the §3 stage it removes (−ego ↔ §3.1–3.2, −multiscale ↔ §3.2.2, −snr ↔ §3.2.2). Add (or flag as supplement) the feature-level vs decision-level contrast (−21.7% F1) as an injection-site ablation, so the design decision is table-backed not just asserted. State clearly which metric (MOVING-class separation or MOVING HOTA) each ΔΔ refers to, on which split/seed count.
**Evidence:** rawvel ΔΔ=+34.93, multiscale +0.047, snr variance, feature-level −21.7% F1 (CLAUDE.md).

#### §4.5 Qualitative recovery (Fig 2)  (Level 2)  — 160 w
**Purpose:** Give the multimedia-venue visual payoff — show a recovered case where the camera moves.
**Planned content.** Fig 2: frame(s) from a sequence where the camera is moving. Baseline panel: the host scores a *parked* car as "moving" (its pixels shifted due to camera pan) and/or misses a truly moving car (its real motion canceled by ego motion in raw displacement). GMC panel: residual velocity correctly separates the two, recovering the right trajectory for "moving cars". Caption ties the visual to Eq 2 (residual = raw − ego) and to the Table 2 MOVING gain. Choose a case from iKUN (showcase host, biggest clean gain). This is the section a multimedia reviewer remembers; keep it tight (one figure, ~160 w) but make the before/after unambiguous. If space allows, add a failure case (turning-verb expression the module cannot recover) to pre-empt cherry-pick criticism — see gap-check.
**Evidence:** Fig 2 (qualitative); ties to Eq 2 and §4.3.

**→ Transition to §5:** Final sentence of §4.5 ("…the module recovers motion-class cases the host structurally misses, but a residual classification gap remains") hands to the conclusion and its limitations.

---

### §5 Conclusion & Limitations  (Level 1)  — target 450 w

**Purpose:** Restate the contribution and inverse-deficit finding, draw honest limits, point to the future lever, and discharge mandatory ACM sections.

#### §5.1 Summary and limitations  (Level 2)  — 300 w
**Purpose:** Restate thesis + state every honest limit.
**Planned content.** Restate: a plug-in, decision-level ego-motion-compensation module recovers motion-class referring expressions that camera-naive hosts systematically miss; the gain is inverse to host native motion ability (motion-deficit law); beats published baselines on 2/3 hosts at a fixed tracker. Limitations (honest, per ARS IRON rule): (1) FlexHook-V1 paper-gap is structural/host-specific. (2) Leaderboard SOTA 48.84 needs a stronger tracker (DDETR; tracker output unavailable) — our gain is tracker-*orthogonal*, not leaderboard-top, by design. (3) The aligner ceiling is representation-bound: extracting motion class from 2D kinematics is the bound, not the fusion — 8+ aligner levers were falsified. (4) Out of scope: hosts with native temporal memory (TempRMOT), where the module is redundant and regresses. (5) Planar-scene homography assumption (KITTI driving); non-planar/severe-parallax scenes are untested. State the assumption explicitly.
**Evidence:** FH-V1 gap, 48.84/DDETR unavailable, representation-bound ceiling, TempRMOT carve-out (CLAUDE.md / memory).

#### §5.2 Future work and mandatory statements  (Level 2)  — 150 w
**Purpose:** Point to the open lever and place required ACM/double-blind statements.
**Planned content.** Future: a richer motion representation/classifier — oracle analysis shows +5 pooled is reachable via a stronger motion classifier with **no new tracker** (ship→oracle_motion 44.58→50.71), so the headroom is modeling, not coverage. Candidate directions: depth-augmented residual velocity, trajectory/temporal motion features, HOTA-aware (not F1-aware) learned fusion. Mandatory statements: Data Availability (Refer-KITTI public; code/recipes to be released), Ethics (driving video, no personal-identity claims; pedestrian boxes used only as tracker targets), AI-usage disclosure (venue-specific), and an explicit Limitations pointer. Double-blind: no author/affiliation/repo-identifying content; anonymize any released-artifact URL until camera-ready.
**Evidence:** oracle +5 reachable (memory signal-decomp), depth-aug iKUN-POS lead (memory), mandatory-section IRON rule.

---

## 4. Evidence Map (source → section)

### Verified citation keys

| Source (verified key) | Assigned section(s) | Role |
|---|---|---|
| TransRMOT / Refer-KITTI — `DT2U6YGG` (CVPR'23) | §1, §2.1, §2.3, §4.1 | RMOT origin, dataset, expression distribution |
| iKUN — `5WW4YXMU` (CVPR'24) | §1, §2.1, §4.2 | host #1, paper baseline 44.564 |
| BoT-SORT GMC — `JXF98FKT` (arXiv'22) | §1, §2.2, §3.1 | GMC-in-tracking lineage, ORB/ECC |
| COAL — `DCE7BWEQ` | §2.1 (optional breadth) | RMOT breadth |
| CGATracker — `DSQBCUBU` | §2.1 (optional breadth) | RMOT breadth |
| Bootstrapping-RMOT — `VZ7IRQDL` | §2.1 (optional breadth) | RMOT breadth |
| Rethinking-2stage — `97QR8XC4` | §2.1 (optional breadth) | RMOT breadth |
| HFF-Tracker — `5ZUJK2TE` | §2.1 (optional breadth) | RMOT breadth |

### [key TODO] gaps — MUST resolve before submission

| Source (no verified key) | Needed in section(s) | Why blocking |
|---|---|---|
| **FlexHook** [key TODO — loose PDF `N2NKLUN9`] | §1, §2.1, §3 (host), §4.2 (paper 42.526) | Host #2/#3; a *quantitative baseline* (42.526) is cited — must have a real reference. |
| **TempRMOT** [key TODO] | §2.1 (carve-out), §5.1 | Scope-bounding claim (Δ−3.8..−5.4) needs the cited system. |
| **CLIP** [key TODO] | §2.3, §3.3 (text/encoder context), §4.2 (re-ranker, supp) | Encoder + appearance re-ranker provenance. |
| **ECC / ORB-homography** [key TODO] | §2.2, §3.1 | GMC lineage beyond BoT-SORT; ORB original. |
| **SentenceTransformer / all-MiniLM-L6-v2** [key TODO] | §3.3 | Language encoder; needs a citation. |
| **HOTA / TrackEval** [key TODO] | §4.1 | Metric definition must be cited. |
| **KITTI** (base dataset) [key TODO] | §4.1 | Refer-KITTI builds on KITTI; cite base. |

### Internal evidence (no external cite; our own results) → section

| Result/number | Section |
|---|---|
| Ship HOTA iKUN 44.634±0.066 / FH-V1 53.526±0.087 / FH-V2 42.807±0.038 | §4.2 (Table 1) |
| Motion-deficit: iKUN 20/+8.6, FH-V1 43/+2.1, FH-V2 48/+0.2 | §4.3 (Table 2) |
| Rawvel collapse ΔΔ=+34.93; multiscale +0.047; snr variance ±0.007→±0.010 | §4.4 (Table 3) |
| Feature-level −21.7% F1 | §3.4.2, §4.4 |
| Appearance stack 45.612 (+1.032) | §4.2/§4.5 + supplement |
| 18-param recipe grid, 9/9 per-class pool-POS, 13D breakdown, re-ranker method, V2 notes | Supplement |
| Oracle +5 reachable (50.71) | §4.3.2, §5.2 |

---

## 5. Word Count Summary

Target ≈ 5,200 w. Tolerance ±5% → [4,940 — 5,460].

| Section | Planned words |
|---|---|
| §1 Introduction | 700 |
| §2 Related Work (2.1 240 + 2.2 200 + 2.3 160) | 600 |
| §3 Method (3.1 250 + 3.2 420 + 3.3 230 + 3.4 300 + 50 connective) | 1,450 |
| §4 Experiments (4.1 320 + 4.2 360 + 4.3 360 + 4.4 300 + 4.5 160) | 1,500 |
| §5 Conclusion & Limitations (5.1 300 + 5.2 150) | 450 |
| Abstract (≈150) + figure/table captions (≈350, 5 floats) | 500 |
| **Total** | **5,200** |

Sum = 5,200 w = exactly 100% of target (within ±5% gate). Body prose (§1–§5) = 4,700 w; abstract + captions = 500 w. Float budget: Fig 1 (§3), Fig 2 (§4.5), Table 1 (§4.2), Table 2 (§4.3), Table 3 (§4.4) + inline 3-arch recipe table (§3.4.1, counted in §3 prose). Note: sigconf 2-col reduces effective text per page when 5 floats are placed; if floats overflow 6 pages, cut §2.1 optional-breadth citations and trim §4.5 to 140 w first (lowest-risk reductions).

---

## 6. Quality-Gate Self-Check

| Gate | Status | Note |
|---|---|---|
| Structure pattern valid | PASS | Conference pattern, justified §1 |
| 100% sections have Purpose | PASS | Every L1/L2/L3 heading has a Purpose line |
| Word sum within ±5% | PASS | 5,200 / 5,200 (0% deviation) |
| Every cited source → ≥1 section | PASS | All verified keys mapped; [key TODO] gaps listed explicitly |
| Every adjacent section pair has transition logic | PASS | §1→2, §2→3, §3→4, §4→5 all specified; intra-section funnel handoffs noted |
| ≤5 heading levels | PASS | Max depth = 3 (L3 only in §3, §4) |
| Every lowest heading ≥150 w planned content | PASS | All L2/L3 leaf headings carry ≥150 w |

---

## 7. GAP-CHECK (adversarial — most important deliverable)

Ordered roughly by severity for a top-venue (MMAsia regular) submission.

**A. Blocking — citations / reproducibility**
1. **FlexHook has no verified cite key, yet you cite its paper number (42.526) as a baseline.** Citing a *quantitative* baseline to a [key TODO] is a desk-reject risk. Resolve `N2NKLUN9` metadata before draft. Same for the FlexHook paper 42.526 value — confirm it is published, not internal.
2. **Metric (HOTA/TrackEval) and base dataset (KITTI) are uncited.** A reviewer expects HOTA defined-by-citation and KITTI credited. Both currently [key TODO].
3. **Language encoder (all-MiniLM-L6-v2 / SentenceTransformer) and CLIP are uncited.** Methods that name a pretrained model must cite it.
4. **No reproducibility/availability statement of substance.** "Code to be released" is weak under double-blind; commit to an anonymized artifact at submission (anonymous repo / supplementary zip). State seeds (0/1/2), exact recipe table, and the `gt_template_old` convention as a repro requirement — the off-by-one GT ambiguity is a known footgun and must be documented or reviewers will fail to reproduce 44.564.

**B. Missing/weak experimental content**
5. **No complexity/runtime/throughput numbers.** ORB+RANSAC per frame + homography composition has a cost; a multimedia venue will ask FPS / per-sequence latency / cache-build time. Currently absent everywhere. Add one line in §4.1 or a small column.
6. **Dataset-statistics line is implied but not written.** #videos, #frames, #expressions, and the MOVING/STATIC/APPEARANCE class shares (10/17/73%) must appear explicitly in §4.1 — they are load-bearing for interpreting every per-class Δ.
7. **n=3 is thin for significance claims.** iKUN +0.070 vs paper is *smaller than one std* on the paper side (you only have ±0.066 on your own number; the paper number has no std). The "+0.070 beats paper" claim is fragile. Either (a) reframe as "matches paper within noise + recovers MOVING class", or (b) add a significance test (the memory mentions 9/9 per-class pool-POS with p-values — surface that, it is your strongest defense). Do **not** lead with the fragile +0.070.
8. **FlexHook-V1 is a *loss* (paper-gap) presented in the main table.** A reviewer will read 3 hosts, one of which the module fails to beat, and discount the "2/3" framing. The footnote must give a *mechanistic* reason (host's strong native motion base; additive scalar can't overtake an internal pipeline diff) — and ideally Table 2 should be positioned to *explain* the FH-V1 loss (smallest deficit to fill), turning the weakness into evidence for the inverse law.
9. **No failure-case analysis in the qualitative figure.** Showing only recovery cases invites cherry-pick criticism. Add a failure example (e.g., turning-verb expressions the module provably cannot recover; the veto/coverage ceiling) — the memory has this material (turning-verbs unrecoverable, ~19% tracker coverage ceiling). A top venue rewards an honest failure panel.
10. **Ablation table lacks a "−ego but keep motion feature" vs "no motion at all" distinction clarity.** ΔΔ=+34.93 needs an explicit baseline anchor: ΔΔ *relative to what*, on which metric (MOVING separation? MOVING HOTA?), which split, which seed count. As written it could read as a unit-less magic number. Define it precisely in the caption.
11. **Two-baseline-per-host promise vs Table 1 columns.** §4.1 promises `{host}` and `{host}+GMC` (raw cos, simple) anchors, but Table 1 as drafted shows {native, ship}. Make the *simple-GMC* baseline explicit in Table 1 (or a sub-row) so the Δ-vs-naive-module is visible, not just Δ-vs-native and Δ-vs-paper — otherwise the "is the recipe doing the work, or just any GMC?" question is unanswered in the main paper.

**C. Unstated assumptions / scope**
12. **Planar-scene homography assumption is never stated as a limitation in the method.** Homography is exact only for planar scenes or pure-rotation cameras; KITTI driving approximates this. A reviewer with parallax expertise will flag it. Add to §3.1 and §5.1 (now scheduled, but must actually be written).
13. **Foreground mask depends on the host's own boxes — circularity risk.** The ego-motion estimate excludes object regions using tracker boxes; if the tracker is wrong, the mask is wrong. Note this dependency and its robustness (RANSAC tolerance) — otherwise it is an unexamined assumption.
14. **Motion-keyword routing (~38 keywords) is a hand-built classifier on the critical path.** Its coverage/error rate is unreported. What fraction of expressions route correctly? A misrouted expression gets the wrong axis/damping. Report routing accuracy or acknowledge it as a limitation; a learned router is an obvious reviewer suggestion to pre-empt.
15. **Per-arch hand-tuned 18-param recipe undercuts "plug-and-play".** The strongest reviewer attack: "plug-and-play" but every host needs a hand-tuned 6-param recipe. The std-matching auto-derivation was NEG — say so, and reframe "plug-and-play" honestly as "no host *retraining* / no detector swap; a small per-host scalar calibration is required." Do not overclaim zero-tuning.

**D. Contribution-vs-evidence backing**
16. **C2's "first analysis showing inverse-deficit" — is "first" defensible?** "First" claims invite a single counterexample to sink them. Soften to "we characterize" unless a literature check confirms novelty of the inverse-deficit framing.
17. **Appearance re-ranker (45.612, +1.032) is the best number but off-thesis.** Banking it in one sentence is fine, but a reviewer may ask why the headline isn't 45.612. Pre-empt: it is orthogonal (appearance, not motion), iKUN-only, and does not generalize cross-host (FH-V2 NEG) — state the non-generalization so it is clearly a bonus, not the contribution.
18. **Motion-deficit deltas for FH-V1/V2 were seed0 single-seed in the source memory; iKUN was n=3.** The memory explicitly flags "re-run n=3 before publishing the exact deltas." If Table 2's +2.1/+0.2 are still single-seed, either re-run n=3 or footnote the seed count — publishing a single-seed delta in the novelty table is a data-integrity risk.

**E. Smaller**
19. No related-work citation for the appearance-grounding/CLIP claim in §2.3 beyond [key TODO] — the funnel's third leg is currently uncited.
20. Float budget is tight: 2 figures + 3 tables + inline recipe table on 6 sigconf pages. Have a concrete cut-list (already noted: §2.1 breadth cites, §4.5 trim) and consider merging Table 2+Table 3 visually if space fails.
21. Abstract is allocated 150 w but not outlined — ensure it states the mechanism, the inverse-deficit finding, and 2/3 result without overclaiming +0.070.
