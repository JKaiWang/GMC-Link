# GMC-Link Paper — Drafting Hub

Living doc for the MM Asia 2026 submission. Single source of truth for venue facts, decisions, status, evidence map. Update as we go.

---

## Venue

**ACM Multimedia Asia 2026 (MMAsia '26)**

| Item | Value | Source / confidence |
|------|-------|---------------------|
| Conference | ~December 2026, location TBD | 2026 host still being bid; MMAsia 2025=Malaysia Dec 9–12, 2024=Auckland Dec → December pattern firm |
| **Track** | **Regular Paper** | locked 2026-06-24 |
| **Submission deadline** | **est. late July 2026** | MMAsia 2025 Regular/Short = Jul 25; Demo/BNI/Doctoral = Aug 30; 2026 site not live — CONFIRM when posted |
| Format | ACM `acmart`, `sigconf`, double-column | `sample-sigconf.tex` |
| **Page limit** | **6 pages** text+figures, **+2** references | Regular track, carries across editions |
| Review | **Double-blind** (anonymous) | no self-id, no repo name, no "our prior work", no ship dates |
| Supplementary | allowed | overflow ablations land here |

ACTION OWED: re-check official MMAsia 2026 CFP once host site announced (page limit / deadline / template version could shift). Watch acmmmasia.org.

---

## Status

- [x] Venue confirmed (MMAsia 2026)
- [x] Mode chosen: **plan-first** (Socratic outline + evidence map before drafting)
- [x] **Lead thesis chosen** (see below)
- [ ] Section skeleton locked ← NEXT (/ars-plan)
- [ ] Evidence map (claim → result) complete
- [ ] acmart `sigconf` repo scaffolded (anonymized)
- [ ] Draft §-by-§
- [ ] Self-review pass (ars-reviewer)
- [ ] Anonymization audit
- [ ] Citations / refs

---

## Thesis (LOCKED 2026-06-24)

**Working title:** Resolving Motion-Referring Expressions in Moving-Camera Videos via Global Motion Compensation

**One-sentence argument:** A plug-and-play decision-level module that compensates camera ego-motion through composed cumulative homographies, recovering the *motion class* of referring expressions that camera-naive RMOT hosts systematically miss.

**Scope discipline:**
- Frame general ("moving-camera videos"); experiments state dataset = Refer-KITTI (driving) explicitly → dodges "only tested driving" hit.
- "Compensation" (not composition) — connects to known GMC term (BoT-SORT, video coding). Differentiator: theirs = single-frame GMC for IoU gating; ours = **composed multi-frame homographies + multi-scale residual velocity + motion-language alignment, fused at decision level**.
- Paper scoped to **motion class**. Appearance spatial re-ranker → **supplement** (iKUN-only, deficit-conditional, keeps main paper focused).
- Core empirical hook = motion-deficit decomp (gain inverse to host native motion ability).

## Key results (from CLAUDE.md + project memory, anonymized-safe)

**Headline (ship 2026-05-21):** Sw aligner + per-arch linear additive fusion, raw cos, no EMA. 3-arch cross-validation, n=3 multi-seed, pooled HOTA.

| Host arch | HOTA (n=3) | vs paper baseline |
|-----------|-----------|-------------------|
| iKUN | 44.634 ± 0.066 | **+0.070** (beat) |
| FlexHook V1 | 53.526 ± 0.087 | gap structural |
| FlexHook V2 | 42.807 ± 0.038 | **+0.281** (beat) |

→ paper-beat **2/3**.

**Candidate lead story (motion-deficit):** GMC's MOVING-class gain is monotonic-inverse to host native motion ability — iKUN +8.6 / FH-V1 +2.1 / FH-V2 +0.2 (native MOVING 20/43/48). Plug-in fills the host's motion deficit; helps motion-blind hosts most.

**Supporting levers (POS):**
- Ego-comp decisive: FiLM rawvel ablation collapses (ΔΔ=+34.93)
- Multi-scale temporal velocity = dominant ablation gain (+0.047 separation)
- Spatial-gate appearance re-ranker (iKUN-only): stack 45.612 (+1.032 vs ship)
- Decision-level only: feature-level injection = −21.7% F1 (NEG, motivates design)

**Honest limits:** FH-V1 paper-gap structural; 48.84 SOTA needs DDETR tracker (data unavailable); ceiling representation-bound (8+ aligner levers exhausted).

---

## Decisions log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-06-24 | Target MMAsia 2026 | user pick |
| 2026-06-24 | Plan-first mode | 6pg tight → selection is the hard problem, not prose |
| 2026-06-24 | Thesis = motion-referring-exprs via GMC | task+method framed; auto-scopes to motion class |
| 2026-06-24 | "compensation" not "composition" | links known GMC term; novelty in the guts |
| 2026-06-24 | "moving-camera videos" scope word | broader than driving, MMAsia-fit, evidence stays KITTI |
| 2026-06-24 | Appearance re-ranker → supplement | keep 6pg main focused on motion |
| 2026-06-24 | Track = Regular Paper (6pg+2) | finished+validated work; decomp needs the room; Short would cut the novelty |

---

## Files

- `README.md` — this hub
- _(coming)_ `outline.md` — locked section skeleton + evidence map
- _(coming)_ `latex/` — acmart sigconf source
- _(coming)_ `figures/`
