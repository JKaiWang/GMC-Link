# REVIEW_SIMULATION.md — Simulated MMAsia 2026 Regular Reviewer (Adversarial)

**Reviewer persona:** Skeptical-but-fair PC member, RMOT/MOT background, has read iKUN, FlexHook, VMRMOT, BoT-SORT/UCMCTrack. Venue = ACM Multimedia Asia 2026, Regular track, 6pg+2ref, double-blind. I review ~6 papers/cycle; I reject papers whose headline number is noise and whose novelty is a recombination, *unless* the recombination is principled and the analysis teaches me something.

**Paper in one line (as I read it):** A plug-and-play decision-level module that compensates camera ego-motion (composed homographies → multi-scale residual velocity → motion-language contrastive alignment → additive fusion) to recover the motion class of referring expressions that camera-naive RMOT hosts miss. 3 hosts, n=3, Refer-KITTI V1/V2.

I went in trying to kill it. Below is per-framing, then my honest editorial read.

---

## 1. Per-framing kill-shots + ratings

### Framing A — Diagnosis-led ("motion-language RMOT silently fails under ego-motion; ego-comp is the fix")

**Kill-shots I'd write:**
1. **"The diagnosis is half-measured on borrowed instrumentation."** The headline mechanism evidence is rawvel-collapse ΔΔ=+34.93 and a 7.17× static-residual pixel ratio. But ΔΔ=+34.93 is an *internal AUC/macro-adjacent ablation number lifted from the FiLM experiment line*, not a HOTA delta on the shipped pipeline — and the shipped pooled HOTA gain is tenths. A diagnosis paper lives or dies on whether the disease it diagnoses actually costs the system anything measurable end-to-end. Here the disease is dramatic in an isolated metric and nearly invisible in the metric you ship on. That gap is the whole review.
2. **"The 7.17× pixel ratio proves the camera moves, not that hosts mis-rank because of it."** The causal chain "ego-motion contaminates displacement → host mis-ranks motion expressions" is asserted with a pixel measurement and an ablation on *your own* aligner, never on the host's actual ranking behavior. You never show iKUN/FlexHook itself flipping a parked car to "moving" because of camera motion — only that *your* feature collapses without ego-comp. Circular-adjacent: the diagnosis is validated on the cure's substrate.
3. **"If the diagnosis were as decisive as claimed, the fix would move pooled HOTA more than 0.07–0.28."** You pre-empt this with pool-dilution (motion class is a minority), which is fair — but then the *paper's own thesis metric must be per-class MOVING HOTA, and the pooled table becomes a secondary/honesty exhibit*. As currently planned (pooled headline in Table 1), the diagnosis framing undercuts itself.

**Ratings:** Novelty **Borderline** (diagnosis of a known-in-MOT problem, newly localized to RMOT — incremental but real). Rigor **Borderline** (mechanism falsification-tested, but on proxy metric + proxy substrate). Honesty **Accept** (they openly flag the proxy-metric gap in their own notes).

---

### Framing B — 3-angle stack (diagnosis + intersection + deficit, co-equal)

**Kill-shots I'd write:**
1. **"Three half-novel angles do not sum to one whole novelty."** Diagnosis is incremental (MOT knew ego-motion hurts), intersection is a recombination (VMRMOT already does motion+language; GMC/UCMCTrack already do ego-comp), and the deficit law is n=3. Presenting them co-equal invites me to evaluate each on its own — and each, alone, is sub-threshold. A reviewer who can attack on three fronts will, and "but the *combination* is novel" reads as hedging when no single leg holds.
2. **"Co-equal framing hides which claim the evidence actually supports."** Your strongest, cleanest result is the per-class motion-deficit decomposition (SA2). Your weakest is the pooled headline (SA4). Co-equal billing means the abstract has to promise the pooled beat *and* the deficit law *and* the diagnosis, and a skeptical reader checks the pooled beat first, finds iKUN +0.070 ≈ 1σ, and reads the rest in a hostile frame. You are spending your credibility on your weakest leg by giving it equal billing.
3. **"Scope sprawl in 6 pages."** Three co-equal contributions + ablations + appearance re-ranker (45.612) + V1/V2 + cross-host negatives cannot be done justice in 6pg. Either the method is under-described or the analysis is thin. MMAsia Regular reviewers penalize a 6-pager that reads like an 8-pager's abstract.

**Ratings:** Novelty **Weak Reject** (sum-of-incrementals, no load-bearing primitive). Rigor **Borderline**. Honesty **Borderline** (co-equal billing of unequal-strength claims is itself a mild honesty smell).

---

### Framing C — Deficit-led ("fills host motion deficit, inverse to native ability")

**Kill-shots I'd write:**
1. **"n=3 hosts cannot support an inverse law — this is the textbook hasty generalization."** Three ordered points (iKUN 20/+8.6, FH-V1 43/+2.1, FH-V2 48/+0.2) define a monotone sequence trivially; *any* two-feature ranking of 3 items is monotone with probability 1/3 by chance, and with a chosen x-axis it's cherry-pickable. The two "predicted negatives" are both FH-V2 (the same host, near-ceiling) — that is **one** independent out-of-sample host, not two. You are generalizing a functional relationship from effectively 2.x independent data points. I would not let "law," "∝," or even "predicts" through review at face value.
2. **"The deficit framing is unfalsifiable as stated."** If a new host gains a lot → "it had a deficit." If it gains nothing → "it was near ceiling." There is no host outcome that contradicts the characterization, because native-ability is measured post-hoc on the same axis. A characterization that cannot be wrong is not a finding. To make it falsifiable you'd need to *predict* a held-out host's gain from its native ability *before* measuring — which you cannot do with the hosts available.
3. **"Even granting the trend, it makes the contribution sound like 'helps weak baselines,' which is the least interesting possible reading."** "Our module helps the host that was worst at motion" is close to tautological for any motion module. The interesting claim would be that ego-comp specifically (not generic motion signal) fills the deficit — but your Table-1 simple-`+GMC` control is *owed, not run* (your own gap-check #11), so you cannot yet separate "ego-comp fills deficit" from "any motion cue fills deficit."

**Ratings:** Novelty **Borderline-leaning-Accept** *if* honestly rescoped (the deficit *characterization* is the only genuinely new intellectual content). Rigor **Weak Reject** as literally framed (n=3 law + missing control). Honesty **Borderline** (the rescope exists in their notes but the law-phrasing keeps reappearing).

---

### Framing D — Intersection-led ("ego-comp × language, unfilled until now")

**Kill-shots I'd write:**
1. **"VMRMOT (2511.17681) is the paper that should worry you, and it's barely a foil — it's a near-peer."** VMRMOT already fuses motion descriptors (position/direction/speed-trend) with language on Refer-KITTI at 53.00 HOTA, end-to-end. Your wedge is "their descriptors are ego-naive, we compensate first." That is a *single engineering delta on one term of their feature vector*, not a new problem space. A reviewer asks: did you re-implement VMRMOT's descriptors with and without ego-comp to isolate that the compensation — not the rest of your pipeline — is what helps? You did not; you compare against iKUN/FlexHook hosts, not against VMRMOT's descriptor set. The intersection claim is therefore **untested against the one system that occupies the adjacent cell**.
2. **"'First to bring explicit ego-comp into RMOT' is a true-but-thin novelty — the components are all off-the-shelf."** ORB+RANSAC homography (decades old), cumulative composition (standard SfM), InfoNCE two-tower (standard), additive late fusion (standard). The intersection is unoccupied because it is a small, expected combination, not because it is hard. Intersection novelty needs the *crossing* to be non-obvious or to unlock something; here both halves are well-known and the crossing is "apply A before B." Reviewers discount "first to combine X and Y" heavily unless the combination surprises.
3. **"You don't beat VMRMOT (53.00) where it's strongest, and your closest host (FH-V1 53.526) doesn't even beat its own published number — so the intersection claim has no number defending it."** The intersection framing implicitly promises that occupying the new cell yields a payoff. Your best V1 number is within the FlexHook reproduction gap and roughly level with VMRMOT, with no head-to-head. The framing writes a check the results don't cash.

**Ratings:** Novelty **Borderline** (true first, but thin/expected). Rigor **Weak Reject** (no head-to-head with the one true neighbor, VMRMOT). Honesty **Accept** (they correctly identify VMRMOT and refuse the "first motion+language" overclaim — credit for that).

---

## 2. Which framing best survives review

**Framing A (diagnosis-led) as the spine, with the deficit *characterization* (rescoped C, not the "law") as the payoff — i.e., A carrying a demoted C.**

Reasoning:
- **A is the only framing whose central claim I cannot fully kill.** That camera-naive RMOT hosts mis-handle motion-class expressions under ego-motion, and that explicit composed-homography ego-comp is a *clean, mechanistically-motivated, plug-in* remedy, is genuinely useful to the community and is backed by a falsification-tested ablation. Its weakness (proxy metric) is fixable by foregrounding per-class MOVING HOTA — a presentation fix, not a missing experiment.
- **D dies to VMRMOT** the moment a reviewer who knows the field reads it: the intersection is real but thin and untested against its one neighbor. Leading with D invites the lethal "you didn't compare to VMRMOT" comment.
- **C alone dies to n=3** and to unfalsifiability. But as a *secondary* result — "and notably, the gain concentrates in the host with the largest motion deficit, which also explains why our near-ceiling hosts gain little" — it stops being a law and becomes an honest, anti-fragile explanation that absorbs the weak FH numbers. That is exactly the role the authors' own ARGUMENT.md assigns SA2, and it's correct.
- **B (co-equal) is strictly dominated:** it gives equal billing to the weak legs and triples the attack surface.

So: **diagnosis-led, deficit-as-explanatory-keystone, intersection demoted to a one-line positioning claim in Related Work (not the headline).** This is essentially the authors' own rescoped plan (R1+R2) — and to their credit, they already converged on it. My job is to confirm it's the *only* survivable spine, and it is.

---

## 3. Is the marginal headline FATAL or SURVIVABLE? (the decisive question)

**My honest editorial read: SURVIVABLE at MMAsia Regular, FATAL at a top-tier venue (CVPR/ICCV/NeurIPS), conditional on three non-negotiable presentation moves.**

Why survivable *here specifically:*
- **MMAsia Regular is a 6-page venue that rewards a clean idea + honest analysis over a leaderboard win.** It is not a SOTA-or-die venue. A plug-in that improves three hosts over their *own* GMC-equipped baseline, with a mechanistic story and a real ablation, is a publishable systems-analysis contribution at this tier *even without* beating anyone's headline — provided the paper never claims it does.
- **The pooled headline being marginal is only fatal if the paper leans on it.** The fatal version is the one in the current PLAN Table 1 draft: "iKUN +0.070, beat 2/3." A sharp reviewer kills "beat" on sight (1σ), and once they catch one overclaim they re-read everything hostile — that cascade *is* the desk-reject path. The survivable version never says "beat" for iKUN, leads iKUN with the per-class MOVING result, reserves "beats published" for FH-V2 (+0.281, genuinely outside noise), and states the FH-V1 reproduction gap plainly.
- **No-SOTA is well-defended.** The detector-bound argument (public trackers all <40, DDETR data refused 3×, measured ~44.6 ceiling) is *evidenced*, not asserted. I accept "evaluated at fixed tracker" as a legitimate scope boundary. This is not the fatal flaw; the overclaimed headline is.

Why it would be **fatal at a top venue:** there, "matches baseline within noise + one host +0.28 + no SOTA + n=3 deficit characterization + recombined components" is a clear reject — too little forward motion on the metric, novelty too incremental. The honesty that *saves* it at MMAsia (openly marginal, openly scoped) reads as "the authors agree it's incremental" at a venue with a higher bar.

**Verdict on the question:** The marginal headline is a **survivable flaw at MMAsia Regular** *iff* the iKUN "beat" wording is removed and the thesis metric is shifted to per-class MOVING HOTA. It becomes **fatal** the instant the paper claims a pooled beat it cannot support. The flaw is in the framing, not the science — which is the most survivable kind.

---

## 4. Three changes that would most raise my score

Ranked by score impact. I flag which need new lab work vs. pure rewrite.

**Change 1 (REWRITE, zero new experiments) — Strip every "beat"/"∝ law" overclaim; make per-class MOVING HOTA the thesis metric.**
Lead iKUN with MOVING Δ up to +4.562 (7/9 per-class sig at α=0.01), present pooled iKUN as "matches published (44.634 vs 44.564, within ±0.066)," reserve "exceeds published" for FH-V2 only, state FH-V1 as a host reproduction gap (GMC still lifts it 53.121→53.526 over the +GMC anchor). Replace deficit "law/∝" with "monotone-inverse across our three hosts; correctly anticipates the absence of gain on our two near-ceiling FH-V2 conditions." This single change moves the paper from "reviewer catches an overclaim and re-reads hostile" to "authors are scrupulously honest" — the largest available swing, and it costs nothing. **+2 on my scale by itself.**

**Change 2 (NEW EXPERIMENT — partially owed already) — Run the simple-`{host}+GMC` (raw-cos, no recipe) control column in Table 1 across all three hosts, n=3, AND re-run the Table-2 FH-V1/V2 deltas at n=3.**
Two integrity holes in your own notes: (a) gap-check #11 — without the simple-GMC control, you cannot show the *recipe* earns its 18 params over "any GMC," and a reviewer will assume the recipe is overfit; (b) D18 — Table-2 deficit deltas are single-seed (seed0). The entire deficit *characterization* (your keystone, Framing C) rests on single-seed FH numbers. A reviewer who notices "+2.1 / +0.2 are n=1" can dismiss the whole monotone-inverse story as seed noise. These are the two experiments that, if missing, let a hostile reviewer collapse your best result. **+1.5, and removes a desk-reject risk.** *(Flagged: needs lab runs — the +GMC anchors partly exist in memory [gmc_baseline_aligner_sw], but the Table-1 column and n=3 Table-2 must be produced and reported.)*

**Change 3 (NEW EXPERIMENT, harder — flag as stretch) — One ego-comp isolation against a motion-fusing neighbor, ideally a minimal VMRMOT-style descriptor with vs. without ego-comp on one host.**
The deepest unaddressed attack (Framing D kill-shot 1, Framing C kill-shot 3): you never isolate that *ego-compensation specifically* — not generic motion signal — produces the gain. The cheapest credible version: take your own 13D residual-velocity features, ablate ego-comp (you have the rawvel ablation), but report it in **HOTA per-class**, not the ΔΔ proxy, so the isolation lives in the ship metric. The stronger version: a stripped VMRMOT-style speed/direction descriptor, fused into one host, raw vs. ego-compensated. Even the cheap HOTA-per-class version converts SA1 from "proxy-metric mechanism" to "ship-metric mechanism" and pre-empts the VMRMOT comparison demand. **+1, and closes the single most credible methodological objection.** *(Flagged: the cheap version is a re-evaluation of an existing ablation in a different metric; the strong VMRMOT version is genuinely new work and may be out of scope for the deadline.)*

---

## 5. Final recommendation (best-framed version)

**Recommendation: WEAK ACCEPT (borderline-positive) — for the best-framed version (Framing A spine + rescoped-deficit keystone + Change 1 applied), conditional on Change 2.**

- Without Change 1 (overclaim still present): **Weak Reject** — the headline "beat" is a noise claim and the deficit "law" is a hasty generalization; a diligent reviewer kills both and the paper reads as overselling a marginal result.
- With Change 1 only (honest rewrite, no new runs): **Borderline** — honest, clean idea, but the recipe-vs-GMC and single-seed-deficit holes remain exploitable.
- With Change 1 + Change 2: **Weak Accept** — honest, mechanistically grounded, properly controlled plug-in analysis; appropriate contribution for MMAsia Regular.
- With all three: solid **Weak Accept / low Accept** — the VMRMOT/ego-isolation gap is the only remaining soft spot and it's defensible as scoped.

**One-sentence meta-review:**
> A mechanistically-motivated, genuinely plug-and-play ego-motion-compensation module for RMOT whose science is sound and whose authors are admirably honest about a marginal pooled headline and an incremental novelty; it is publishable at MMAsia Regular *if and only if* it leads with the per-class motion-recovery result rather than the within-noise pooled "beat," supplies the missing simple-GMC control, and reports the deficit characterization at n=3 rather than single-seed — fix the framing and the controls, not the experiments, and this clears the bar.

---

### Reviewer's note on the authors' own pre-emption
For the record: the PLAN.md/ARGUMENT.md documents already diagnose nearly every kill-shot above (R1 demote iKUN beat, R2 drop the law, D18 single-seed flag, #11 missing control). That is unusual self-awareness and it raises my confidence the final draft will land on the survivable framing. The remaining risk is *execution discipline* — whether the drafted text actually holds the rescoped line under the temptation to say "beats SOTA-adjacent on FH-V1" or "2/3 paper-beat." Every place the word "beat" attaches to iKUN, or "∝"/"law" attaches to the deficit, is a live grenade. The science survives; the prose must not relapse.
