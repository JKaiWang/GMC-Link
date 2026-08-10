# SPINE_ANALYSIS.md — Narrative-Spine Deep-Dive (argument_builder_agent)

ARS deep-dive on ONE question: **what narrative spine makes this paper strongest given its ACTUAL
evidence?** Adversarial, not flattering. Paper: *Resolving Motion-Referring Expressions in
Moving-Camera Videos via Global Motion Compensation*, MMAsia 2026 Regular (6pg+2ref, sigconf,
double-blind). Builds on the VERIFIED situation in PLAN.md / ARGUMENT.md — does not re-derive it.

---

## 0. The fixed constraints every spine must obey

These are settled (PLAN §NOVELTY POSITIONING, ARGUMENT §5/§9). A spine that violates any is dead on
arrival:

- **Novelty = an intersection**, not a primitive. NOT "first motion+language" (VMRMOT, arXiv
  2511.17681, already fuses motion descriptors + language on Refer-KITTI at 53.00 HOTA, ego-naive).
  NOT "first ego-comp" (UCMCTrack / BoT-SORT do CMC in plain MOT, language-blind). The defensible
  claim is the *unoccupied intersection*: explicit ego-motion compensation brought into
  language-referred RMOT, as a decision-level plug-in.
- **iKUN +0.070 vs ±0.066 ≈ 1σ.** "Beat" is reviewer-lethal as a standalone pooled claim (R1).
- **Deficit "law" rests on n=3 hosts.** "∝"/"law"/"scaling" = hasty generalization (R2). Survives
  only as "monotone-inverse across three hosts + two predicted cross-host negatives."
- **No SOTA.** 48.84 needs the DDETR tracker (data refused 3×); detector-bound, evidenced <40 on all
  public substitutes. Tracker-orthogonal scope is honest but is NOT a headline.
- **Aligner is representation-bound (26 NEG levers).** It is explicitly NOT a contribution. Any spine
  that leans on the aligner is fatal (P5).

So every spine is a re-ordering of the SAME four assets: **(A) mechanism/ego-comp decisiveness**
(rawvel ΔΔ=+34.93, 7.17× pixel ratio), **(B) the ego-comp × language intersection** (vs VMRMOT foil),
**(C) the inverse-deficit characterization** (20/+8.6, 43/+2.1, 48/+0.2 + 2 predicted negatives),
**(D) the cross-arch 2/3-host result** (n=3, std-bounded). The question is which becomes the spine and
which become ribs.

---

## 1. Spine scores

Rubric: argument strength (Compelling 90-100 / Strong 70-89 / Adequate 50-69 / Weak <50);
MMAsia-reviewer survivability; honesty (overclaim risk under the thin evidence); writeability at 6pg.
8 weak-argument indicators applied (circular, authority, hasty-generalization, false-dichotomy,
corr≠cause, single-context, undefined-term, counter-stronger).

| Spine | Strength | Score | Reviewer survivability | Honesty | Writeability 6pg | Verdict |
|-------|----------|-------|------------------------|---------|------------------|---------|
| **1. Single diagnosis-spine** ("motion-language RMOT silently fails under camera motion, VMRMOT included; ego-comp is the decisive fix") | **Strong** | **80** | **High** — one falsifiable claim, one decisive ablation, one named foil. Hardest single thing to refute. | **High** — leads with the strongest-evidenced asset (A); demotes the two thin numbers to supporting. No overclaim. | **High** — one thesis, clean 4-para arc, RW funnels to it, every table serves it. | **RECOMMENDED** |
| **2. 3-angle stack** (diagnosis + intersection + deficit co-equal headliners) | **Adequate** | **62** | **Medium-low** — three headliners = three independent attack surfaces; reviewer picks the weakest (deficit n=3) and frames the whole paper by it. Dilutes. | **Medium** — co-equal billing of the n=3 deficit *as a headline* invites the hasty-generalization read. | **Low** — 6pg cannot give three theses their own evidentiary spine; each gets ~1/3 the room and none lands. | Reject as spine |
| **3. Deficit-led** ("gain inverse to native motion ability") | **Adequate** | **58** | **Low** — leads with the single weakest-supported asset (n=3, flag #3). A sharp reviewer's first sentence: "a law from three points." Keystone exposed as the front door. | **Low-medium** — foregrounding n=3 as THE claim is the exact overclaim ARGUMENT R2 warns against. | **Medium** — writeable, but the lead needs constant hedging that bleeds confidence. | Reject as spine |
| **4. Intersection-led** ("we occupy the unfilled ego-comp × language intersection") | **Adequate→Strong** | **66** | **Medium** — bulletproof on novelty, but "we fill a gap" is a *positioning* claim, not a *result* claim; reviewers ask "so what does filling it buy?" and you're back to the thin numbers with no mechanism shield up front. | **High** — the intersection claim is verified and honest. | **Medium-high** — clean to write, but the Intro spends its punch on taxonomy before showing the failure is real. | Strong #2; fold into Spine 1 |

### Per-spine reasoning (adversarial)

**Spine 1 — Single diagnosis-spine.** Leads with asset A, the *only* asset rated Strong-or-better on
its own evidence (SA1 = 84). The thesis is a falsifiable mechanism that *was* falsification-tested
(rawvel collapse). It survives every weak-argument check: not circular (mechanism and HOTA metric are
independent), no authority appeal, no hasty generalization *in the lead* (the n=3 deficit is demoted to
a supporting "why the gain is class-concentrated" rib), no false dichotomy. Single-context (Refer-KITTI
only) and undefined-term flags remain but are Limitations-section items, not spine flaws. Crucially it
*absorbs* B, C, D as supporting evidence without giving any of them headline exposure: VMRMOT becomes
the foil that proves the failure is current and not strawman (B as motivation); the deficit decomp
becomes the mechanism's *signature* — "the fix helps exactly the hosts the mechanism predicts are most
contaminated" (C as corroboration, not standalone law); the 2/3 result is "the fix transfers across
architectures" (D as breadth, with iKUN routed through per-class MOVING). This is the anti-fragile
configuration ARGUMENT §4 identified: the diagnosis is the spine, and the two weak numbers ride in as
*predictions of the diagnosis*, never as standalone claims.

**Spine 2 — 3-angle stack.** The instinct ("we have three good angles, show all three big") is the
classic 6pg trap. Three co-equal headliners means the Intro must establish three theses, the RW must
motivate three gaps, and the Experiments must give each its own evidentiary spine — in ~4050 words. Each
gets starved. Worse, reviewer survivability is set by the *weakest* headliner, not the average: a stack
invites "I'll evaluate the deficit law" and the n=3 flag now characterizes the whole submission. Stacking
here *dilutes* (see §2). Score 62: each angle is individually fine, but as co-equals they compete for the
same scarce evidence-room and hand the reviewer the choice of attack.

**Spine 3 — Deficit-led.** The deficit decomp (C / SA2) is the paper's *most interesting* idea and its
*least-supported* one simultaneously. Leading with it puts the keystone at the front door where it is
maximally exposed. ARGUMENT §5 scores SA2 at 68 *only in rescoped form*; as a lead it must be stated
strongly to carry a paper, and the strong statement ("∝ 1/native") is precisely the hasty
generalization. You cannot lead with a claim you must immediately hedge. The deficit is a brilliant
*payoff*, not a brilliant *premise* — it lands hardest when set up by the mechanism (A) and discharged
in Results. Leading with it spends the surprise and exposes the n=3.

**Spine 4 — Intersection-led.** Bulletproof and honest, and it is the right *novelty* framing — but a
positioning claim makes a weak *spine*. "We occupy an unfilled intersection" answers "is this new?" but
not "is the problem real / does the fix work?" — and the second question is where the strong evidence
(A) lives. An intersection-led Intro spends its first half on a 2×2 taxonomy (motion×language present in
VMRMOT, ego×MOT present in UCMCTrack, ego×language=us) before showing a single failure. Reviewers reward
a demonstrated pain over a well-drawn map. The intersection is essential — but as the *gap statement in
para 2*, not the spine. It is the strongest #2 and folds cleanly into Spine 1.

---

## 2. Does layering 3 angles ADD or DILUTE?

**Verdict: layering as CO-EQUAL HEADLINERS dilutes. Layering as SPINE + SUPPORTING RIBS adds.**

The distinction is billing, not inclusion. All four assets (A/B/C/D) belong in the paper — the question
is whether three of them get *headline* billing.

**Why co-equal stacking dilutes (Spine 2):**
1. **Evidence-room is conserved.** 6pg / ~4050 words is fixed. Three headliners means each thesis gets
   ~1/3 of the Intro's commitment, ~1/3 of the Experiments' adjudication. The mechanism ablation (the
   strongest asset) would share Table 3's real estate with a deficit table and an intersection
   taxonomy — none reaches the depth that makes it decisive.
2. **Survivability is min(), not mean().** A reviewer evaluates the paper by its *weakest* foregrounded
   claim. Stack the n=3 deficit as a headliner and you have volunteered it as the thing to grade. Spine 1
   demotes it so the attack surface is the Strong-84 mechanism instead.
3. **No unifying through-line.** Three co-equal claims read as three small contributions, not one
   coherent thesis. MMAsia Regular rewards a paper that says one thing well.

**Why spine+ribs adds (Spine 1):**
- The diagnosis (A) is a *narrative magnet*: the intersection (B) becomes "and no one has done this
  because they never modeled the camera," the deficit (C) becomes "and here's the fingerprint that it's
  really the camera," the result (D) becomes "and it transfers." Each rib *strengthens* the spine
  instead of competing with it.
- The two thin numbers (iKUN pooled, FH gains) enter as *consequences of the diagnosis* — the deficit
  decomp explains why iKUN's pooled gain is small (motion class is a minority → pool dilution) and why
  FH's gains are small (near native motion ceiling). This is the anti-fragility ARGUMENT §4 names:
  ribs that turn the weak numbers into predicted evidence. That only works when the diagnosis is the
  spine they hang from.

**One nuance:** the intersection (B) is novelty-load-bearing and must NOT be merely a rib buried in RW —
it has to appear as the explicit *gap statement* (Intro para 2 + RW block 3). So Spine 1 is really
"diagnosis-spine with the intersection as its named gap." That is one thesis with a sharp positioning
clause, not two headliners.

---

## 3. RECOMMENDED SPINE: Single Diagnosis-Spine (with intersection as the named gap)

> **"Motion-language RMOT silently fails under camera ego-motion — VMRMOT included — because hosts read
> motion from raw bbox displacement that the moving camera contaminates. A plug-and-play decision-level
> ego-compensation module is the decisive fix, and it transfers across architectures, helping exactly
> the hosts the mechanism predicts are most contaminated."**

### 3.1 Four-paragraph Intro arc

**Para 1 — Pain, as a concrete mechanism (lead with asset A).**
RMOT must resolve motion-class referring expressions ("moving / turning / parked cars"). State the
mechanism plainly and falsifiably: hosts infer motion from raw bounding-box pixel displacement; under a
moving camera that displacement is dominated by the *camera's* motion, not the object's. Concrete image
the reviewer cannot unsee: a parked car displaces in pixels because the camera moves, so "moving car"
matches the parked car and misses the real mover. End with the stakes — this is a *systematic*,
*mechanistic* failure, not a tuning artifact. (No numbers yet; numbers are the payoff.)

**Para 2 — Gap = the named intersection (fold asset B in here).**
The failure persists even in the newest motion-aware RMOT: VMRMOT fuses explicit motion descriptors
(speed/direction trends) with language, but its descriptors are *camera-naive* — under ego-motion a
parked car carries a nonzero "speed trend." Symmetrically, plain-MOT compensates ego-motion (BoT-SORT,
UCMCTrack) but is *language-blind*. So the intersection — *ego-compensated motion fused with language* —
is unoccupied. This is the precise, verified novelty: not "first motion+language," not "first ego-comp,"
but first to bring explicit ego-motion compensation into language-referred RMOT. (This is where the 2×2
positioning earns its place — as a one-sentence gap, not a section.)

**Para 3 — Approach + the decisive-evidence promise.**
A plug-and-play, decision-level module: composed cumulative homography (Stage 1–2) → multi-scale
residual velocity (raw − ego) → lean two-tower motion-language alignment → additive score-level fusion.
No host retraining, no detector swap — a small per-host scalar calibration (NOT a learned head;
std-matching auto-derivation was falsified). Forward-reference the decisive evidence: an ablation that
replaces residual with raw velocity collapses the motion class (ΔΔ=+34.93 on the MOVING class) —
removing only the ego term destroys essentially all motion-class signal, proving ego-compensation is
*the* decisive component. One clause on the qualitative payoff (Fig 2: camera-moving frames where the
baseline scores a parked car "moving" and the module recovers).

**Para 4 — Contributions + scope guard.**
The three bullets (§3.2), then the scope guard: gains are reported *at a fixed tracker*, orthogonal to
detector quality; leaderboard-top (48.84) needs a different detector (DDETR, data unavailable; public
substitutes <40), which is out of scope by evidence, not by dodge. State the domain scope (Refer-KITTI)
plainly here so it is owned, not extracted by a reviewer.

### 3.2 The 3 contribution bullets this spine implies

- **C1 — A decision-level ego-motion-compensation plug-in for RMOT.** Composed cumulative homography +
  multi-scale residual velocity + motion-language alignment + additive fusion; no host retraining, no
  detector swap, a small per-host scalar calibration (std-matching auto-derivation was NEG — the
  calibration is irreducible, not arbitrary). *This is the intersection (B), instantiated.*
- **C2 — Ego-compensation is the decisive component, isolated by ablation.** Rawvel-collapse (ΔΔ=+34.93,
  MOVING class) + 7.17× ego-pixel ratio establish *necessity and magnitude*; decision-level is the robust
  injection site (feature-level −21.7% F1, reproduced by 5 feature/early-concat HOTA/AUC negatives).
  *This is the mechanism (A), the spine's load-bearing evidence.*
- **C3 — Cross-architecture characterization: the plug-in fills the host's motion deficit.** Across three
  RMOT hosts (n=3 multi-seed) the MOVING gain is *monotone-inverse* to native motion ability
  (iKUN 20/+8.6, FH-V1 43/+2.1, FH-V2 48/+0.2) and correctly *predicts two cross-host negatives*
  (FH-V2 plug-in −0.047, architectural ego −0.091). At a fixed tracker the module improves all three
  hosts over their GMC-equipped baseline and exceeds the published number on two. *This is the deficit (C)
  + result (D), discharged as the mechanism's signature — never as a standalone "law."*

### 3.3 Lead vs supporting evidence under this spine

| Evidence | Role | Why |
|----------|------|-----|
| Rawvel-collapse ablation ΔΔ=+34.93 (MOVING class) | **LEAD** | The decisive-component proof; the spine's keystone. Strongest-evidenced asset (SA1=84). |
| 7.17× ego-pixel ratio diagnostic | **LEAD-support** | Independent magnitude check on the mechanism. |
| Decision-level vs feature-level (−21.7% F1 + 5 NEG) | **LEAD-support** | Justifies the injection-site design; the "only viable site" claim, softened. |
| VMRMOT foil (53.00, ego-naive) | **Motivation (lead-adjacent)** | Proves the failure is *current* and not a strawman; names the intersection. Comparison point only, NOT a beat (different host pipeline). |
| Inverse-deficit decomp (20/+8.6 · 43/+2.1 · 48/+0.2) | **SUPPORTING** | The mechanism's *fingerprint* + the explainer for both thin numbers. Headlined would expose n=3; supporting, it is anti-fragile. |
| Two predicted cross-host negatives | **SUPPORTING** | Converts the n=3 correlation into a risky-prediction-that-held — the honest strength of C3. |
| Table 1 main HOTA (iKUN 44.634 / FH-V1 53.526 / FH-V2 42.807, n=3) | **SUPPORTING** | "Transfers across architectures." iKUN framed *matches + per-class lift*; clean beat = FH-V2 +0.281. |
| Per-class 9/9 pool-POS, MOVING Δ up to +4.562 | **SUPPORTING (carries iKUN)** | The load-bearing iKUN evidence, routed through the deficit, NOT the ±0.066 pooled tenth. |
| Tracker-orthogonal / 48.84 detector-bound | **SCOPE (Limitations)** | Bounds the claim honestly; evidenced, not asserted. Never a headline. |
| Appearance re-ranker → 45.612 (+1.032) | **OFF-THESIS BANK (one line + supplement)** | Best iKUN number, but orthogonal to ego-comp; do not let it blur the spine. |

---

## 4. Stress-test of the recommendation

**Single biggest vulnerability: the magnitude gap between the LEAD evidence and the HEADLINE result.**
The spine's decisive proof is ΔΔ=+34.93 — but that is an *internal, class-isolated, AUC/macro-adjacent*
ablation metric. The actual shipped pooled HOTA gains are tenths (iKUN +0.070 ≈ noise; FH-V2 +0.281).
A sharp MMAsia reviewer writes: *"Your mechanism may be decisive in isolation, but the end-to-end pooled
gain is within noise on your showcase host — so is the mechanism decisive or merely real-but-marginal?"*
This is the one counter ARGUMENT rates at near-parity (P1/P2), and it sits exactly on the seam between
the spine's strength and the paper's weak numbers.

**Honest mitigation (three moves, all wording/foregrounding, zero new experiments):**
1. **Mechanically separate the two scales in-text and never conflate them.** State explicitly: ego-comp
   is decisive *for the motion class*; the pooled gain is small *because the motion class is a minority of
   expressions* (~17–27% MOVING share) and pooled HOTA aggregates trajectory IDs across the appearance
   majority — pool dilution is a *mechanical* property (`project_pool_per_expr_disagreement_explained`),
   not weak evidence. The reviewer's "decisive or marginal?" dissolves: decisive on the class, diluted at
   pool, by arithmetic.
2. **Report per-class MOVING HOTA as the primary adjudication in Table 3, pooled as secondary.** The
   +4.562 iKUN-MOVING (7/9 per-class POS, sig at α=0.01) is the number the spine actually predicts. Lead
   the adjudication there; show pooled to prove no regression elsewhere.
3. **Route iKUN through the deficit, never the pooled tenth (R1).** "iKUN *matches* its published pooled
   HOTA while substantially improving the motion class" — true, defensible, and *predicted* by the
   deficit decomp (iKUN = motion-blind → biggest class gain, smallest pool gain). The mechanism, the
   deficit, and the thin pooled number become one self-consistent story.

**Residual risk after mitigation:** a reviewer who rejects per-class HOTA as the primary metric and
insists on pooled-only will still see ~1σ on iKUN. Mitigation: FH-V2 +0.281 is a clean pooled beat
*outside* seed noise, and all three hosts beat their *GMC-equipped* baseline (B2) at pool — so the pooled
story does not rest on iKUN alone. The spine survives a pooled-purist, just less impressively.

---

## 5. Honest content verdict for MMAsia Regular

**Verdict: BORDERLINE (lean-positive under Spine 1, with owed items closed).**

The content is genuinely *publishable*: a falsifiable, ablation-tested mechanism (the rare paper that
*disproves itself if wrong*); a verified, timely novelty (the ego×language intersection, with VMRMOT as
a Nov'25 concurrent foil that makes it current); cross-architecture validation with multi-seed; and an
unusually honest deficit characterization that *predicts its own negatives*. That is a real systems
contribution, not a δ-HOTA paper. Under the diagnosis-spine it reads as one coherent, defensible claim.

It is **not accept-likely** because the headline numbers are thin (no SOTA, iKUN ≈ noise at pool, FH-V1
under its own paper) and the deficit "law" rests on n=3 — so a hostile reviewer has live ammunition even
after rescoping. It is **not weak** because the mechanism evidence is strong, the novelty is bulletproof,
and the spine routes the weak numbers into predicted-evidence rather than exposed claims. It lands at
**borderline, tipping positive** if the spine is executed and the OWED items land — MMAsia Regular
accepts well-argued systems papers with honest scope; it rejects papers that overclaim.

### The 2–3 OWED items that move it most (highest leverage first)

1. **Table 2 deficit deltas at n=3 (FH-V1/V2 currently single-seed, seed0 — D18 integrity).** This is
   the spine's signature evidence (C3). Single-seed deltas on the *novelty keystone* is the single most
   attackable integrity item; n=3 or an explicit footnoted seed count is mandatory. Highest leverage:
   it is the difference between the deficit reading as "characterization with predictive power" vs
   "anecdote on three hosts measured once." **Lab work, cannot fabricate.**
2. **Per-class MOVING HOTA foregrounded in Table 3 + the simple `{host}+GMC` column in Table 1.** The
   per-class metric is what makes the mechanism's decisiveness survive the "pooled is noise" counter
   (§4). The `+GMC` simple-fusion column (recipe-vs-any-GMC control, gap-check #11) pre-empts "is it the
   recipe or just any motion signal?" — without it, SA3/SA4 are exposed. Both are re-runs of existing
   harness, no new method.
3. **Runtime/FPS for ORB+RANSAC+homography composition + dataset-stats line.** Multimedia venue expects
   a cost number for a "plug-and-play real-time-ish" claim; absence reads as hiding overhead. The
   dataset-stats line (#videos/#frames/#expr + class shares ~10/17/73%) is what makes the pool-dilution
   argument (§4 mitigation) quantitative rather than asserted. Both are cheap; both close a reviewer
   reflex.

**Blocking but clerical (not content): cite keys.** FlexHook key resolved (`97QR8XC4`); still owe
HOTA/TrackEval, KITTI, SBERT, CLIP, ORB, RANSAC, InfoNCE, YOLOv8 (PLAN §Ch2 top-up). Desk-reject risk if
left unresolved — but these are bibliography mechanics, not evidence gaps.

### One-line bottom line
Run the **single diagnosis-spine** (mechanism-led, intersection as the named gap, deficit + 2/3-result
as supporting ribs); it is the only configuration where the strong asset leads and the thin numbers ride
in as *predictions* of the thesis. Content is **borderline-tipping-positive** for MMAsia Regular — the
deficit n=3 re-run, per-class MOVING foregrounding, and runtime line are the three items that most move
it from borderline toward accept.
