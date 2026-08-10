# Core Protocol (always loaded via CLAUDE.md @import — keep ≤ 130 lines)

Compressed essentials. Full versions: dispatch.md, judgment.md, templates.md,
maintenance.md in this directory. On any ambiguity, the full file wins.

## 1. Commander rule

Main conversation = decisions only. Delegate via Agent tool: repo scans,
>2-file reads, web research, batch edits, log parsing, verification.
Subagents return conclusions + file:line; long artifacts go to files, the
path comes back. Never paste raw logs/dumps into the main conversation.

## 2. Model choice (verified 2026-07-05; re-check /model before trusting)

| Task | Agent `model` |
|---|---|
| Search, file inventory, read-back verification | haiku (Explore agent) |
| Implement, batch edits, run evals, log summarize | sonnet |
| Design, hard debugging, adversarial review | opus |

`fable` only existed 2026-07-05 — assume unavailable. Agent tool has no
effort param; effort lives in .claude/agents frontmatter, Workflow agent()
opts, or session `/effort` (low|medium|high|xhigh|max).

## 3. Every dispatch has 3 elements

(1) goal + why, (2) checkable acceptance criteria, (3) report format + where
to save artifacts. Skeletons: templates.md — search / implement / refactor /
research / review / experiment.

## 4. Escalation ladder

haiku fails once → sonnet. sonnet fails same subtask twice → opus WITH full
failure trail (attempts, exact errors, hypothesis). Solved on opus →
downshift to sonnet/haiku for batch application. Max 2 retry rounds per task
total, then stop and report the blocker to the user. Never loop.

## 5. Verify ≠ self-verify

Producer never certifies own work. File → fresh haiku read-back. Code → run
the test/command, show exit status + decisive line. Risky judgment (recipe,
paper claim) → fresh opus second opinion or 3-sample judge.

## 6. Done (experiments) means ALL of

n≥3 seeds + std · Δ vs BOTH baselines (B2 anchor AND ship) · pooled AND
per-class HOTA · braking canary ≥ +0.35 · provenance tuple
(arch, n, GMC_SUFFIX, gt convention, pooled|macro, recipe) · memory file
written. Less than that = label "preliminary" everywhere it's mentioned.

## 7. Stop and ask the user before

Changing locked recipes · changing paper numbers/claims · deleting
weights/caches/data/gt_template dirs · git push or anything public · new
dependency · editing CLAUDE.md or .claude/rules/* (tiers: maintenance.md) ·
unrequested jobs > ~2 GPU-hours. Otherwise act and report — don't ask
permission for reversible in-scope work.

## 8. Wrong-direction signals → switch path, write memory, move on

Same lever family HOTA-NEG twice → closed. Tuning hyperparams to rescue a
NEG → stop. Proxy/diagnostic green but HOTA red → HOTA wins, kill it (skip
AUC gates entirely). New number contradicts memory canon → suspect your
protocol first (gt_template? GMC_RAW_COS? suffix?), not the memory.

## 9. Operational constants

Single GPU: never two training/eval jobs at once; long runs in background.
Independent non-GPU dispatches: one message, parallel calls.
Numbers conflict: memory canon > docs > old logs; surface, don't silently fix.
Institution files are written in full sentences (no caveman compression).
