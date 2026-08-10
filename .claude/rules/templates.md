# Delegation Prompt Templates

Written 2026-07-05. Copy the skeleton, fill every {blank}, delete unused
optional lines. Every template has the 3 elements: goal+why, acceptance
criteria, report format (dispatch.md). Suggested model per type; escalation
ladder in dispatch.md applies.

## 1. SEARCH (agent: Explore, model: haiku)

```
GOAL: Find {what} in {scope/dirs}. Needed because {decision this feeds}.
KNOWN: {1-3 facts the agent can't cheaply discover: naming conventions,
  likely dirs, e.g. "eval scripts are top-level run_*.py, not in gmc_link/"}
ACCEPTANCE:
- Every hit cited as file:line with a 1-line description.
- If nothing found: say "NOT FOUND", list every search term/glob tried.
REPORT: ≤15 lines, list form. No file content dumps.
```

## 2. IMPLEMENT (agent: general-purpose, model: sonnet)

```
GOAL: {change} in {files}. Motivation: {why / what breaks without it}.
CONSTRAINTS: match surrounding code style; no new dependencies; do not touch
  {protected files, e.g. locked recipe args, gt_template dirs}.
ACCEPTANCE:
- {observable behavior, e.g. "python {script} {args} exits 0 and prints X"}
- Run the check yourself and include exit status + decisive output line.
- No unrelated diffs.
REPORT: files changed as path:line-range + 1 line each; the check command and
  its output; anything you were unsure about, flagged OBSERVED vs INFERRED.
```

## 3. REFACTOR (agent: general-purpose, model: sonnet)

```
GOAL: Refactor {what} to {shape}. Why: {duplication/cost/risk}.
INVARIANT: zero behavior change.
ACCEPTANCE:
- {test command or golden check} passes BEFORE and AFTER — run both, show both.
- If no test exists: write the smallest assert-style check first, get it green
  on the old code, then refactor against it.
- Public interfaces unchanged unless listed here: {exceptions}.
REPORT: before/after check outputs; files as path:line-range; LOC delta.
```

## 4. RESEARCH (web/docs) (agent: general-purpose, model: sonnet)

```
GOAL: Answer {question}. This feeds {decision}.
SOURCES: prefer {official docs / arXiv / venue pages}; every claim needs a URL
  + publication date. Use claude-code-guide agent instead if the question is
  about Claude Code/API itself.
ACCEPTANCE:
- Each claim labeled VERIFIED (direct source) / REPORTED (secondary) /
  UNCONFIRMED. Never present UNCONFIRMED as fact.
- Conflicting sources reported as conflict, with both citations.
REPORT: ≤25 lines. Answer first, then per-claim citations. Long notes → save
  to {path}, return path.
```

## 5. REVIEW (agent: general-purpose, model: opus; adversarial)

```
GOAL: Adversarially review {artifact} against {spec/rubric}. Your job is to
  find what's WRONG — assume the author is competent but rushed.
CHECK AT MINIMUM: {list, e.g. contradictions between files; wrong
  paths/commands (verify each referenced path exists via ls); numbers vs
  docs/SHIP.md and memory; statements a weak model would misread}.
ACCEPTANCE:
- Every finding: location (file:line), what's wrong, concrete fix.
- Rank by severity. Try to refute your own findings once before reporting;
  drop what doesn't survive.
- Zero findings is acceptable ONLY with a list of what was checked.
REPORT: ranked findings list. No restating what's fine beyond the checked-list.
```

## 6. EXPERIMENT / EVAL (this repo's specialty)
(agent: general-purpose, model: sonnet; GPU jobs SERIALIZED — dispatch.md)

```
GOAL: Measure {lever/config} on {arch(s)}. Hypothesis: {expected effect + why}.
PRECHECK (do these BEFORE any GPU time, abort + report if any fails):
- Lever not in docs/CLOSED_LEVERS.md and not NEG in memory
  (grep -ril "{keyword}" /home/seanachan/.claude/projects/-home-seanachan-GMC-Link/memory/)
- Walk CLAUDE.md Landmines: gt_template_old? GMC_RAW_COS=1? correct GMC_SUFFIX?
PROTOCOL: seeds {0,1,2}; commands from docs/SHIP.md with {deltas}; ONE GPU job
  at a time; save each log to {log_dir}/{name}_seed{N}.log.
ACCEPTANCE (= judgment.md §2):
- n=3 mean±std; Δ vs B2 anchor AND ship; pooled AND per-class HOTA;
  braking canary ≥ +0.35; provenance tuple on every number.
REPORT: one table (exact recipe labels, never "ours"); verdict
  POS/NEG/NEUTRAL vs both baselines; log paths. Draft memory-file text for the
  result (positive or negative) — main thread reviews before saving.
```

## Dispatch call shape (reference)

Agent tool: `subagent_type` + `model` (haiku|sonnet|opus) + `prompt` = filled
template. Parallel independent dispatches → one message, multiple tool calls.
GPU tasks → never parallel. Long runs → run_in_background: true.
