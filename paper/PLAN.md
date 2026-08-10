# Chapter Plan + INSIGHT Collection — MMAsia 2026 Regular Paper

Plan-mode output (Socratic). Accumulates per-chapter summaries + extracted INSIGHTs. Feeds `full`/`outline` drafting later. Anonymized (double-blind).

**Title:** Resolving Motion-Referring Expressions in Moving-Camera Videos via Global Motion Compensation
**Thesis:** A plug-and-play decision-level module compensates camera ego-motion via composed cumulative homographies, recovering the motion class of referring expressions that camera-naive RMOT hosts systematically miss.
**Venue:** MMAsia 2026 Regular Paper, acmart sigconf, 6pg+2ref, double-blind.

---

## DRAFT STATUS — 2026-06-24 (full first draft complete)

All 5 sections + abstract drafted via ARS generator→evaluator→revise workflows, inserted into `paper/latex/main.tex`, compiles clean (`latexmk -pdf`, EXIT=0, 0 undefined, **6 pages**, 12 cites resolve). Gates per section: writing-quality (0 AI-tells, em-dash ≤2/pg), spine discipline (0 "beat"/"law" across paper), number integrity (Experiments verified vs sources), technical accuracy (Method eqs/recipe vs code).

**Owed before submission:**
- ✅ D18 n=3 deficit re-run DONE 2026-06-24: Table 2 filled with authoritative n=3 — native 20.25/43.98/48.02, gains +9.22±0.88 / +0.91±0.79 / +0.43±0.17. Monotone-inverse confirmed; FH-V1 honestly dropped +2.1→+0.91 (seed-1 ~0). Main-results +4.562→+9.22 reconciled (consistent native-vs-ship baseline; 9/9 per-class deltas POS verified).
- 🔄 Ablation MOVING-HOTA RUNNING (grid `bhahc2hwb`): env-guarded −ego/−multiscale/−snr (GMC_RAWVEL/GMC_GAPS/GMC_NO_SNR added to manager.py+dataset.py, cache-key ablation-aware, defaults=ship). FULL row known (29.47). Fills `tab:ablation` on completion.
- 🎨 Figures: Fig 1 pipeline, Fig 2 qualitative — placeholders compile.
- ✅ Citation-compliance DOI pass DONE 2026-06-24: all 12 verified (DOIs, full authors, venues); UCMCTrack→AAAI'24 inproceedings, SBERT→full venue; FlexHook="Accepted CVPR 2026" (upgrade when proceedings post); 4 benign empty-address warnings remain (camera-ready polish).
- ✅ Overfull hboxes FIXED (microtype + tabcolsep 4pt + C2 reword); residual 1.34pt vbox is benign.
- 📏 Length: 6pg at limit (with placeholder figures) → re-check once real Fig 1/2 land.
- 📋 Mandatory ACM statements (AI-disclosure, ethics, data-availability) — camera-ready.

## INSIGHTS (running)

- `[INSIGHT: thesis]` plug-in, decision-level, ego-motion compensation via composed cumulative homography; recovers motion-class exprs.
- `[INSIGHT: intro_opener]` MECHANISM-failure lead: hosts read motion from raw bbox displacement; under camera ego-motion that displacement is the camera's → "moving car" matches parked, misses moving. Falsifiable; proven by rawvel-collapse ablation (ΔΔ=+34.93).
- `[INSIGHT: core_novelty]` Inverse-deficit: plug-in gain ∝ 1/(host native motion ability). iKUN +8.6 / FH-V1 +2.1 / FH-V2 +0.2 MOVING (native MOVING 20/43/48). Stated as Intro contribution bullet, paid off in Results.
- `[INSIGHT: scope_guard]` Tracker-orthogonal. 48.84 SOTA out of scope (needs DDETR tracker; data unavailable). Contribution = motion reasoning at fixed tracker, not leaderboard top.

---

## NARRATIVE SPINE — LOCKED 2026-06-24 (two ARS agents converged)

**SINGLE DIAGNOSIS-SPINE** (architect 80/Strong; reviewer = only un-killable framing). NOT a 3-angle stack (both agents: dilutes/dominated).
- Spine: motion-language RMOT silently fails under camera ego-motion (VMRMOT included) → hosts read motion from camera-contaminated bbox displacement → decision-level ego-comp is the decisive fix → transfers across architectures.
- Deficit (C) = demoted to *explanatory support* (NOT a law). Intersection (A) = one-line Related-Work positioning.
- **METRIC DISCIPLINE (load-bearing):** thesis metric = **per-class MOVING HOTA**, not pooled tenths, not the ΔΔ proxy. NEVER write "beat" on iKUN (1σ) or "∝/law" on the deficit — each is a desk-reject grenade. iKUN framed as "matches paper pooled + lifts motion class."
- Content verdict: borderline→**Weak Accept at MMAsia Regular** (fatal at top-tier). Science sound; risk = framing discipline in final prose.
- Top-3 fixes: (1) strip beat/law + per-class MOVING as thesis metric [free]; (2) simple-`+GMC` control col + D18 n=3 deficit re-run [lab]; (3) rawvel ablation reported in HOTA-per-class not ΔΔ [cheap].
- Detail: `paper/SPINE_ANALYSIS.md`, `paper/REVIEW_SIMULATION.md`.

## NOVELTY POSITIONING — verified 2026-06-24 (CENTRAL CLAIM)

**Defensible claim = an INTERSECTION, not a primitive.** Verified against literature:
- ❌ "first motion+language in RMOT" — FALSE. **VMRMOT** (Lv et al., arXiv 2511.17681, Nov'25) already fuses motion descriptors (position/direction/distance-trend/speed-trend) → NL → MLLM, on Refer-KITTI (53.00 HOTA) + V2 (35.21). End-to-end.
- ❌ "first ego-motion compensation" — FALSE. UCMCTrack (AAAI'24, 2312.08952), BoT-SORT, GMC all do CMC/ego-comp in plain MOT — but language-blind.
- ✅ **"first to bring EXPLICIT ego-motion compensation into language-referred RMOT, as a plug-in"** — BULLETPROOF. VMRMOT fuses motion+language but its descriptors are RAW (ego-naive); plain-MOT CMC compensates ego but has no language. Unoccupied intersection = ego-compensated motion × language.

**WEDGE vs VMRMOT (strongest differentiator):** their speed/direction descriptors are camera-contaminated; under ego-motion a parked car has nonzero "speed trend." We compensate before fusing. Use VMRMOT as the foil that motivates ego-comp.

**New must-cites:** VMRMOT `[2511.17681]` (concurrent motion-language, ego-naive — position against; comparison point 53.00 vs our FH-V1+GMC 53.526), UCMCTrack `[2312.08952]` (ego-comp in MOT, language-blind).

**Related Work reshaped around the intersection (3 blocks, bold-inline-lead):**
1. RMOT & motion-language fusion (TransRMOT, iKUN, FlexHook, VMRMOT, TempRMOT) → model object motion but ego-naive.
2. Camera/ego-motion compensation in tracking (GMC/BoT-SORT, UCMCTrack, ORB/RANSAC) → compensate ego but language-blind.
3. The gap: no work crosses both → our decision-level plug-in fills it. (TempRMOT carve-out folds into block 1 or 3.)

---

## ARS REVIEW FINDINGS (2026-06-24) — structure_architect + argument_builder

Full detail: `paper/OUTLINE.md` (word alloc + gap-check) + `paper/ARGUMENT.md` (CER + strength + rescopes).
Composite argument strength = **Strong (74)** AFTER R1+R2; reviewer-lethal before.

**🔴 Critical — wording only (do before drafting):**
- R1: iKUN +0.070 is ~1σ. Reframe → "matches paper pooled + lifts motion class." Reserve "beat" for FH-V2. *(applied: Ch1, Ch4)*
- R2: deficit "∝ law" from n=3 → "monotone-inverse, validated by 2 predicted cross-host negatives." *(applied: Ch1, Ch4)*
- C15: "plug-and-play" → "no retrain/no detector swap + small per-host scalar calibration." *(applied: Ch1)*

**🔴 Integrity:**
- D18: Table 2 FH-V1/V2 deltas single-seed → re-run n=3 or footnote. *(flagged in Ch4)*

**🟠 Experiments OWED (need re-runs / data — USER lab work):**
- Simple-`{host}+GMC` fusion column in Table 1 (recipe-vs-any-GMC control). STILL OWED (needs eval re-run).
- Failure panel in Fig 2 (turning-verb / coverage ceiling — material in memory). STILL OWED.
- ΔΔ=+34.93 caption: define relative-to-what + metric + split + seeds. (Replace ΔΔ proxy w/ per-class MOVING HOTA per spine decision.)

**✅ D3 RESOLVED 2026-06-24 (workflow w3lyzn7zc measured/computed — NONE experiment-owed):**
- **Runtime (trivial fill):** Stage-1 ego ~13–15 ms/frame (~68–78 FPS); full pipeline ~16–18 ms/frame (~57–61 FPS); CPU, opencv 4.13, ORB=~80% cost. KITTI=10fps → ~6–8× real-time on CPU, no GPU. Publish via ~15-line harness, n≥3 ±std. Wrap point: `core.py` estimate_homography / `manager.py` process_frame. (Don't time run_build_gmc_cache.py — recomputes per-expr.)
- **Router accuracy (cheap fill):** ship router = `run_ikun_linear_additive.py:60-69`, **15 keywords (NOT 38 — CLAUDE.md wrong)**. Prototype V1 N=158: acc 0.772 (dir=motion) / **0.911 (dir→appear, ship intent)**. Disagreements definitional: 22 FN=direction exprs (excluded by design), 14 FP=walking-ped. Report both GT defs; 30-min hand-audit of ~36 disagreements → gold. Defuses gap-check #14.
- **Dataset stats (trivial, COMPUTED):** V1 test 3 seqs/1010 frames/158 exprs → APPEAR 119 (75.3%)/STATIC 12 (7.6%)/MOVING **27 (17.1%)**. V2 test 4 seqs/1469 frames/862 exprs → APPEAR 639 (74.1%)/STATIC 101 (11.7%)/MOVING 122 (14.2%). **LOAD-BEARING: MOVING=17% minority quantifies why pooled HOTA dilutes — the pool-marginal defense. Cite in spine.** Per-seq breakdowns in workflow output.

**✅ D2 RESOLVED 2026-06-24 (state both as bounded-failure-modes):**
- Planar: single homography (core.py:82) exact only for planar/pure-rotation; driving=planar-dominated, deliberate choice (beat Farneback+RAFT); residual parallax absorbed by RANSAC+aligner; ablation proves it holds. Scope, not weakness.
- Circularity: mask seeded from host boxes (core.py:46-56) → wrong box leaks object features; bounded by RANSAC outlier reject (:82) + identity fallback (:59-60,72,84) + bg_residual confidence (:88-95). Degrades gracefully. Quote the mitigations = rigor.

**🟡 Code corrections surfaced (cleanup, non-blocking):**
- CLAUDE.md "~38 motion keywords" → actually 15.
- "77% APPEAR" (frame-weighted) ≠ 75.3% (expression-count) — cite right denominator.
- dataset.py:1721 imports non-existent gmc_link/expr_class.py (dead ImportError path).

**🟠 Citations OWED (blocking — desk-reject risk):**
- Resolve FlexHook key (`N2NKLUN9`) — quantitative baseline cited to unresolved key = bad.
- Cite HOTA/TrackEval, KITTI, SentenceTransformer/all-MiniLM-L6-v2, CLIP.

**🟡 Scope/limits to state explicitly:**
- Planar-scene homography assumption (parallax).
- Foreground mask uses host's own boxes (circularity if tracker wrong).
- Operational defs: "native motion ability," "structural gap," "motion class."
- Domain scope: all results Refer-KITTI only.
- C2 "first analysis" → "we characterize" unless lit-check confirms novelty.

---

## Ch 1 — Introduction (~0.75 pg, ~700 w)  [SUMMARY LOCKED + ARS-revised]

**Goal:** reader feels the motion-class failure is real + mechanistic, and that a plug-in fix exists.

Para flow:
1. **Pain (mechanism).** RMOT task; motion-class expressions ("moving/turning/parked cars"); hosts infer motion from raw bbox displacement; camera ego-motion contaminates it → systematic mismatch. Concrete: parked car displaces in pixels because camera moves.
2. **Gap.** Existing RMOT hosts are camera-naive (no ego model). Prior global-motion-compensation in tracking (BoT-SORT-style) is single-frame, IoU-gating only, never fused with language. No one compensates ego-motion for motion-language alignment.
3. **Approach (1 para).** Plug-and-play decision-level module: composed cumulative homography → multi-scale residual velocity → motion-language contrastive alignment → additive fusion. No host retrain, no detector swap.
4. **Contributions + scope guard.**

**Contribution bullets:** *(post-ARS-review wording — R1/R2/C15 applied)*
- C1: Decision-level ego-motion-compensation module (composed homography + multi-scale residual velocity + motion-language alignment); **no host retraining, no detector swap — a small per-host scalar calibration** (NOT a learned head; std-matching auto-derivation was NEG). Avoid bare "plug-and-play" overclaim.
- C2: Cross-architecture study on 3 RMOT hosts (n=3 multi-seed). Plug-in gain is **monotone-inverse to host native motion ability across our three hosts, validated by two predicted cross-host negatives** (FH-V2 −0.047/−0.091). Phrase as characterization, NOT a "∝ law."
- C3: Ablations isolating ego-compensation as the decisive component (rawvel collapse, MOVING-class) and decision-level fusion as the viable injection site (feature-level −21.7% F1, + 5 prior NEG fusion sites).
- Result framing (R1): iKUN **matches** paper pooled HOTA (44.634 vs 44.564, within ±0.066) **while lifting the motion class** (MOVING Δ up to +4.562, 7/9 per-class sig); clean paper-beat = **FH-V2 +0.281**. Do NOT lead with iKUN "+0.070 beat" (≈1σ).
- Scope guard: gains at fixed tracker; orthogonal to detector quality (48.84 SOTA needs a different tracker, out of scope — evidence it's detector-bound, not a dodge).

---

## SOCRATIC CHAPTER SUMMARIES — ch1–3 (socratic_mentor formal pass, 2026-06-24)

### Chapter Summary: Introduction
- **Commitment gate** (hardest part to write well): not overclaiming iKUN +0.070 → resolved by R1.
- Q1 Problem urgency: motion-class referring exprs fail — hosts read motion from raw bbox displacement contaminated by camera ego-motion ("moving car" matches parked, misses movers).
- Q2 Gap: no RMOT host models ego-motion; prior GMC (BoT-SORT) is single-frame IoU-gating, never language-fused.
- Q3 RQ: can a plug-in decision-level ego-motion-compensation module recover the motion class camera-naive hosts miss, *across architectures*?
- Q4 Timeliness: RMOT matured on appearance (TransRMOT'23, iKUN'24); motion class is now the bottleneck.
- Q5 Reading motivation: monotone-inverse deficit — module helps motion-blind hosts most; tracker-orthogonal.
- **Convergence:** C1 ✓ C2 ✓ C3 ✓ C4 ✓ (owns FH-V1 gap + SOTA scope) → CONVERGED.
- **Risk:** leading with the ~1σ iKUN beat (R1 fixes). `[INSIGHT: intro_summary]` mechanism-pain + inverse-deficit hook, parity-not-beat framing.

### Chapter Summary: Related Work
- **Commitment gate** (coverage 1-10): ~7; thin leg = motion-for-grounding (uncited, gap-check #19).
- Q1 What to review: RMOT methods; global-motion-compensation in tracking; motion representation for grounding.
- Q2 Relationships: evolutionary RMOT appearance lineage + GMC borrowed from MOT but never language-fused = the bridge we build.
- Q3 Biggest gap: ego-motion modeling absent in RMOT; GMC never fused with language.
- Q4 Positioning: intersection — first to bring composed *multi-frame* GMC into motion-language alignment.
- Q5 Disagree-with: implicit assumption that temporal trackers (TempRMOT) subsume motion reasoning → carve out (native memory ≠ ego-comp; cascading regresses Δ−3.8..−5.4).
- **Convergence:** C1 ✓ C2 ✓ C3 ⚠ (cite keys TODO: HOTA, KITTI, CLIP, FlexHook) C4 ✓ → CONVERGED-with-caveat (citations owed).
- **Risk:** citing FlexHook baseline to unresolved key (blocking). `[INSIGHT: related_summary]` gap-funnel, TempRMOT carve-out turns landmine into scoped design.

### Chapter Summary: Method
- **Commitment gate** (first reviewer criticism of method): "18-param hand-tuned recipe undercuts plug-and-play" → C15 reframe.
- Q1 Method: ORB-homography ego-comp → composed cumulative H → multi-scale residual velocity 13D → two-tower contrastive alignment → decision-level additive fusion.
- Q2 Justification: ORB+RANSAC > optical flow on planar KITTI (outlier rejection); decision-level > feature-level (−21.7% F1); composed multi-frame > single-frame GMC.
- Q3 Data: Refer-KITTI V1/V2, paper-canonical splits; sufficient.
- Q4 Quality assurance: n=3 multi-seed; `gt_template_old` canonical convention; reproduce paper 44.564.
- Q5 Limitation: planar-scene homography (parallax); foreground mask depends on host boxes (circularity); aligner representation-bound. Handle: state as scope; ego-comp ablation proves value regardless.
- **Convergence:** C1 ✓ C2 ✓ C3 ✓ C4 ✓ → CONVERGED.
- **Risk:** plug-and-play overclaim (C15); runtime unreported (#5); router accuracy unreported (#14). `[INSIGHT: method_summary]` ego-comp+composition is the differentiator; aligner deliberately lean.

---

## Ch 2 — Related Work (~0.75 pg)  [STRUCTURE LOCKED — cite keys TODO via Zotero]

Structure = gap-funnel, each mini-para ends at the hole we fill.

- **(a) RMOT methods.** TransRMOT `[key?]` (Refer-KITTI origin), iKUN `[key?]`, FlexHook `[key?]`, TempRMOT `[key?]`. → all infer motion from raw bbox geometry; none model camera ego-motion. **TempRMOT carve-out**: hosts with native temporal memory are out of scope (GMC redundant there → structural regression Δ−3.8..−5.4); GMC targets spatially-naive hosts.
- **(b) Global motion compensation in tracking.** BoT-SORT GMC `[key?]`, ECC / ORB-homography lineage `[key?]`. → used for IoU-gating, single-frame, never fused with language.
- **(c) Motion representation for language grounding.** appearance-dominated grounding `[key?]`. → motion-class expressions under-served.

### Resolved cite keys (Zotero, verified 2026-06-24)
- TransRMOT / Refer-KITTI origin — Wu et al., CVPR'23 — `DT2U6YGG`
- iKUN — Du et al., CVPR'24 — `5WW4YXMU`
- BoT-SORT (GMC module) — Aharon et al., arXiv'22 — `JXF98FKT`
- HOTA metric — Luiten et al., IJCV'21 — `TRC3SSJA`
- **FlexHook** — Li, Du, Yin, Zhao, Su, arXiv 2503.07516 (2025-11) — `97QR8XC4`. Two-stage RBT (C-Hook + PCD); host arch V1/V2 = Refer-KITTI/v2. BLOCKER CLEARED.
- Other RMOT in-library (for breadth): COAL `DCE7BWEQ`, CGATracker `DSQBCUBU`, Bootstrapping-RMOT `VZ7IRQDL`, HFF-Tracker `5ZUJK2TE`

### Resolved via search (2026-06-24)
- **TempRMOT method + Refer-KITTI-v2 dataset** = arXiv 2406.05039 (Zhang/Wu/Han) = Zotero `VZ7IRQDL` (already in library; was labeled "Bootstrapping-RMOT"). One key covers both. Relabel in ledger.
- **NeuralSORT** base tracker (YOLOv8 detector) → cite iKUN `5WW4YXMU` for the tracker pipeline + add YOLOv8.

### BIBLIOGRAPHY TOP-UP (must-add — all canonical; Zotero auto-fetches metadata on add)
- KITTI — Geiger et al., CVPR'12 — base dataset
- CLIP — Radford et al., ICML'21 — encoder + appearance re-ranker
- SBERT — Reimers & Gurevych, EMNLP'19 — language encoder (NOT in library)
- ORB — Rublee et al., ICCV'11 — Stage-1 feature detector
- RANSAC — Fischler & Bolles, CACM'81 (or Hartley-Zisserman MVG) — homography estimation
- InfoNCE — van den Oord et al., arXiv'18 (CPC) — contrastive loss
- YOLOv8 — Jocher et al. / Ultralytics'23 — detector behind NeuralSORT

### CONDITIONAL
- Motion-for-grounding leg-3 — only if leg kept (lean: CUT); if kept → 1–2 cites via mini-search.
- **Empirical RW benchmark (2 reliable fetches):**
  - 2403.10830 (homography+moving-cam MOT, 10–11pg/65refs): RW 3 subsecs incl standalone "Camera Motion Compensation" (validates leg-2), ~1,100w, 20–25% of Method+Exp.
  - 2505.20680 (CLIP continual-learning, 82refs, long-format): RW 3 subsecs, ~1,200w, 12% of total.
  - **REAL MMAsia exemplar (measured from PDF):** Jiao/Cao/Wang IT-Prompt, MMAsia'24, ACM sigconf 8pg (6+2ref), 60 refs. §2 Related Work = **~850 words, 3 thematic blocks, ~30 cites, NO subsections/figures, bold-inline-lead style** (`\textbf{Theme:}`). RW ≈ 16% of body; Method+Exp dominate (~60%).
  - **REVISED LOCK (evidence updated):** 3 compact thematic blocks (~280w each, ~850w total) IS within 6pg MMAsia norm — use **bold-inline-lead paragraphs, not `\subsection`**. So our RW can run 3 legs. Budget: bump RW 600→~830w (pull ~230w from Method 1,450→~1,250). Open question now = WHAT the 3rd leg is (motion-grounding vs splitting GMC into ego-comp + MOT-trackers vs motion-rep-in-RMOT) — pick the most load-bearing, not necessarily motion-grounding.

Loose PDFs (8GXC8KGE/MTJYITW9/BD2V3DBP/UGGUK7SS) NOT ground through — must-add list is canonical regardless; user adds clean items faster than IDing unnamed PDFs.

### FlexHook provenance — RESOLVED 2026-06-24
Published by others → cite freely, no anonymity issue. Key = loose PDF `N2NKLUN9` (resolve metadata at draft time).
## Ch 3 — Method (~1.75 pg)  [LOCKED]

**Fig 1 = pipeline** (frames → ORB homography → compose cumulative H → residual velocity 13D → two-tower alignment → additive fusion → HOTA).

Strategic: aligner is NOT the contribution (representation-bound ceiling, 8+ arch levers NEG). Budget → ego-comp + residual velocity + fusion; alignment stays lean.

**Stage 1 — Ego-motion compensation.** ORB features; BFMatcher (Hamming, Lowe ratio 0.7); RANSAC homography; foreground mask to avoid locking onto object features. Output: frame→frame 3×3 H.

**Stage 2 — Cumulative composition + residual velocity.** *(Eq 1)* H[t−k→t] = H[t−1→t]·…·H[t−k→t−k+1]. Store original (never-warped) centroids; warp once with composed H (numerically stabler than iterative). *(Eq 2)* residual velocity = raw velocity − ego velocity at gaps {2,5,10}; normalize v_norm=(v_pix/img_dims)×100. **13D vector** = [res_dx×3, res_dy×3, dw, dh, cx, cy, w, h, snr]. Multi-scale = dominant ablation gain (+0.047 sep); snr = variance reducer. Full 13D breakdown → supplement.

**Stage 3 — Motion-language alignment (LEAN).** Two-tower shared_weight: per-modality Linear adapter (motion 13→256, lang 384→256) → shared MLP 256→512→512→256 → LN → L2. Lang = SentenceTransformer all-MiniLM-L6-v2 (384D). Train symmetric InfoNCE (τ=0.07) + False-Negative Masking. Inference: raw cosine (no sigmoid, no EMA).

**Stage 4 — Decision-level additive fusion.** *(Eq 3)* final = model_logit + α·(sc·raw_cos + thr), per-arch, per-axis (motion + appearance). Per-class GMC-relevance damping: sc_a ≪ sc_m (GMC=motion signal is noise on appearance exprs). **Compact 3-arch recipe table** (motion/appear α,sc,thr); full 18-param grid → supplement. Decision-level only: feature-level injection = −21.7% F1 (motivates the design).

**Equations shown:** Eq1 cumulative composition, Eq2 residual velocity, Eq3 additive fusion.
## Ch 4 — Experiments (~2 pg)  [LOCKED — working defaults A2+B2+qual fig, override OK]

**Protocol para.** Refer-KITTI V1 (3-seq pooled) + V2 (4-seq pooled); HOTA via TrackEval; n=3 multi-seed (±std). State `gt_template_old` = paper-canonical (NeuralSORT-aligned) convention; reproduce paper iKUN 44.564. Two baselines per host: `{host}` and `{host}+GMC` (raw cos).

**Table 1 — main HOTA.** 3 hosts × {native, +GMC ship} × HOTA (n=3 ± std) + Δ-vs-paper. iKUN 44.634, FH-V1 53.526, FH-V2 42.807. **Framing (R1):** iKUN *matches* paper (44.634 vs 44.564, within ±0.066) — present as parity + motion-class lift, NOT a beat. Clean beat = FH-V2 +0.281. FH-V1 = footnote: residual to its *own* published number; GMC still lifts it over B2 (53.121→53.526). **ADD `{host}+GMC` simple-fusion column** (gap-check #11) → answers "recipe vs any GMC."

**Table 2 — motion-deficit decomp** (the novelty; table not figure — 3 hosts too thin for scatter). Rows: host | native MOVING ability (= host MOVING HOTA w/o GMC) | GMC MOVING gain. iKUN 20/+8.6 · FH-V1 43/+2.1 · FH-V2 48/+0.2. Text: monotone-inverse across the 3 hosts; FH-V1's small gain *predicted by* its small deficit (turns the weak number into evidence). **⚠ INTEGRITY (D18): FH-V1/V2 deltas are single-seed (seed0) — RE-RUN n=3 or footnote seed count before publish.**

**Table 3 — ablation (mechanism).** Rows: full / −ego (raw velocity) / −multiscale (single gap) / −snr. Report MOVING-class metric (pooled hides motion catastrophe). Rawvel collapse (ΔΔ=+34.93) = decisive-component proof.

**Fig 2 — qualitative recovery.** Frame(s) where camera moves: baseline scores parked car as "moving" / misses real mover; GMC recovers. Multimedia-venue payoff.

**Appearance extension (A2).** One sentence in main: orthogonal CLIP-L/14 spatial re-ranker stacks on iKUN → 45.612 (+1.032), first iKUN pooled >45.5; full method → supplement. Framed off-thesis but banks best number.

**Supplement:** full 18-param recipe grid, per-class 9/9 pool-POS table, 13D breakdown, appearance re-ranker method, V2 protocol notes.

## Ch 5 — Conclusion + Limitations (~0.5 pg)  [DRAFT]

- Restate: plug-in ego-motion compensation recovers motion-class exprs; gain inverse to host motion deficit; beats baselines 2/3 at fixed tracker.
- **Limitations (honest):** FH-V1 paper-gap structural; SOTA 48.84 needs a stronger tracker (DDETR, data unavailable) — our gain is tracker-orthogonal, not leaderboard-top; aligner ceiling representation-bound (motion-class extraction from 2D kinematics is the bound, not fusion); out of scope = hosts with native temporal memory (TempRMOT).
- Future: richer motion representation (oracle gap shows +5 pooled reachable via stronger motion classifier, no new tracker).
- Mandatory: Data Availability, Ethics, AI-disclosure, limitations (per ARS IRON rule).
