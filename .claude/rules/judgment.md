# Judgment Rubrics

Written 2026-07-05. High-level judgment converted into checklists a
Sonnet-level session can execute. Every rubric: rule → checklist → one real
positive and one real negative example from this project's history.

## §1 When to escalate the model

Escalate when the FAILURE MODE is reasoning, not information.

Checklist — escalate only if ALL true:
- [ ] The task spec had all 3 elements (goal, acceptance, format) — if not,
      fix the spec first, same model.
- [ ] The needed inputs were available to the agent — if not, supply them,
      same model.
- [ ] Two attempts failed the same way for different-looking reasons, or the
      agent's output is internally inconsistent.

DO escalate: a sonnet agent twice writes a sweep script whose numbers don't
reproduce, with plausible-looking code both times → opus with both diffs and
both logs attached.
DON'T escalate: an Explore agent finds nothing because the search term was
`gt_templates` (wrong name) → fix the query, rerun same model. Model was
never the problem.

## §2 When it is actually done ("done" for experiments)

An experimental claim is DONE only when all six hold:
- [ ] n ≥ 3 seeds, mean ± std reported
- [ ] Δ vs BOTH baselines: B2 anchor (sw+simple) AND current ship
- [ ] Pooled HOTA AND per-class (STATIC/MOVING) — pooled alone hides
      catastrophes (cascade incident: MOVING=1.55 while STATIC=47.23)
- [ ] Provenance tuple attached (§5)
- [ ] Braking-separation canary ≥ +0.35 (memory: project_braking_canary)
- [ ] Memory file written (positive OR negative result — negatives are the
      project's main asset)

Anything less is "preliminary" and must be labeled so in every mention.

DONE example: ship adoption 2026-05-21 — n=3, both baselines, pooled+per-class,
LOSO defense, memory files. That is the bar.
NOT-DONE example: sw CLIP early-concat looked POS on a single seed; at n=3 it
was NEG on all hosts (project_sw_clip_earlyconcat_flat_2026_05_25). A
single-seed +Δ is a hypothesis, not a result.

For code (non-experiment) tasks, DONE = acceptance criteria met + the check
actually ran (test or real command) + output shown. "Should work" is not done.

## §3 When to stop and ask the user

Ask BEFORE acting when the action is on this list. Otherwise don't ask — act
and report (asking for permission on reversible in-scope work wastes a turn).

Stop-and-ask list:
- Changing locked ship recipes / hyperparams (docs/SHIP.md table)
- Changing any number or claim in paper/
- Deleting or overwriting weights, caches, dataset files, gt_template dirs
- git push, opening PRs/issues, anything leaving the machine
- Adding a dependency
- Editing CLAUDE.md or .claude/rules/* (maintenance.md tiers)
- Starting anything estimated > ~2 GPU-hours that wasn't requested
- A result that would OVERTURN a canonical memory entry (verify protocol
  landmines first — CLAUDE.md Landmines — then present evidence, don't
  silently rewrite memory)

RIGHT to ask: DDETR data unavailable after 3 attempts → reported blocker
instead of substituting a different detector silently (which would have
invalidated the paper comparison).
WRONG to ask: "May I write a scratch script to parse this log?" — reversible,
in scope, scratchpad exists. Just do it.

## §4 Wrong-direction signals (switch path, don't retry harder)

Any ONE of these means STOP the current lever, write the memory file, move on:

- Same lever family HOTA-NEG twice → family closed.
  Example done right: Case 2 variants 1a→1d, each NEG, family closed after 1d
  ship-stack test — no fifth variant.
- You are tuning hyperparameters to rescue a NEG result → stop. Ship recipes
  came from principled sweeps; rescue-tuning has never flipped a verdict here
  (variant B std-matching stayed catastrophic at every setting).
- Diagnostic/proxy green but HOTA red → trust HOTA, kill it. The FH ego pixel
  diagnostic passed its gate and was later HOTA-killed
  (project_fh_ego_pixel_diagnostic_2026_06_02). AUC never adjudicates
  (feedback_never_kill_at_auc): skip AUC gates entirely, go straight to HOTA.
- Result wildly contradicts an established memory number → suspect YOUR
  protocol first (wrong gt_template, missing GMC_RAW_COS, wrong suffix),
  not the memory.
- Two escalations + 2 retry rounds burned → blocker report to user.

## §5 Quality floor — how to verify the floor

Every reported metric carries the provenance tuple:
`(arch, n seeds, GMC_SUFFIX, gt convention, pooled|macro, recipe args)`
No tuple → the number does not enter a table, a commit message, or the paper.

PASS example: "iKUN 44.634 ± 0.066, n=3 (seeds 0/1/2),
_sharedweight_seed{N}_rawcos, gt_template_old, 3-seq pooled, α=1.0/sc=0.9/
thr=0.17 + appear α=1.0/sc=0.30/thr=0.10".
FAIL example: "our method gets 44.6" — no n, no convention, label "our
method" (user's hard rule: tables never say "ours"/"baseline").

Floor checks by artifact type:
- Table/doc: labels name exact recipes; numbers match memory canon; if a
  number differs from memory, that's a finding to surface, not silently edit.
- Code: the smallest runnable check exists and ran (one assert-style script
  or test — see ponytail rules); trivial one-liners exempt.
- Any file produced by an agent: read back by a DIFFERENT fresh agent
  (dispatch.md §Verification).
- Claims about the harness/models: only from live schema, /model, /effort, or
  official docs — with date. Unverifiable → write "UNCONFIRMED", never guess.

## §6 Honest-limits clause

Decomposition + verification + multi-sample judging recover execution quality
on smaller models. They do NOT recover taste on open-ended judgment (research
direction, paper framing, what reviewers will care about). When such a
question appears: (a) check the survey + LETTER for prior Fable-level
direction, (b) if still open, present options to the user with tradeoffs —
do not fake confidence. Say plainly: "this is a taste call above my grade."
