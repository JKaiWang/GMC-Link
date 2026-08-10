# Model Dispatch Rules

Written 2026-07-05. Facts verified that day against live tool schemas and
official docs. Re-verify with `/model`, `/effort`, or the claude-api skill
before hardcoding values anywhere else.

## Verified facts (2026-07-05)

- Agent tool `model` values: `haiku` | `sonnet` | `opus` | `fable`.
  `fable` existed only in the 2026-07-05 window — assume unavailable.
  If a dispatch with `model: fable` errors, use `opus`.
- The Agent tool call has NO effort parameter. Effort is settable:
  - in `.claude/agents/*.md` frontmatter: `effort: low|medium|high|xhigh|max`
    (frontmatter also supports `model`, `tools`, `maxTurns`, `skills`, ...)
    — source: code.claude.com/docs/en/sub-agents
  - in Workflow scripts: `agent(prompt, {effort: ...})`, same five values
  - for the whole session: `/effort <level>`
    — source: code.claude.com/docs/en/model-config
- API model IDs (harness env 2026-07-05): `claude-sonnet-5`,
  `claude-opus-4-8`, `claude-haiku-4-5-20251001`, `claude-fable-5`.
- Safety-routed requests (Fable → Opus fallback) COUNT toward the same usage
  window (support.claude.com article 15363606 — high confidence, fetched via
  search extract, not line-verified; spot-check on the usage dashboard).
- Built-in subagent types worth using: `Explore` (read-only search),
  `general-purpose`, `Plan`, `claude-code-guide` (Claude Code/API questions).
  The authoritative list is the system-reminder at session start — it changes.

## Rule 0 — the commander does not do grunt work

The main conversation is the expensive context. It holds decisions, not data.
Delegate when the task is any of:

| Trigger | Dispatch |
|---|---|
| Need >2 files read to answer one question | Explore, model haiku |
| Repo-wide scan / "where is X used" | Explore, model haiku |
| Web/docs research | general-purpose, model sonnet |
| Batch mechanical edits (>3 similar changes) | general-purpose, model sonnet |
| Run eval/training and summarize the log | general-purpose, model sonnet |
| Verify another agent's output | fresh agent, model per §Verification |
| Design/plan with tradeoffs | Plan or general-purpose, model opus |

Main thread may directly: read ≤2 files, run one-off short commands, make
small targeted edits it will verify itself via tests. Everything else goes out.

## The 3-element task spec (every dispatch includes all three)

1. **Goal + why** — 1–2 lines. What the result is FOR changes what "good" means.
2. **Acceptance criteria** — checkable, not vibes: "returns file:line for every
   hit", "script exits 0 and prints HOTA for 3 seeds", "cites source URL".
3. **Report format** — what comes back, max length, where artifacts get saved.

Fill-in skeletons per task type: `.claude/rules/templates.md`.

## Report contract (what subagents return)

- Conclusions + `file:line` references. Never raw file dumps or full logs.
- Long output (logs, generated docs, data) → save to a file (scratchpad for
  temporary, repo path for deliverables), return the path + a ≤10-line summary.
- Findings must separate OBSERVED (with evidence) from INFERRED (say so).
- "Not found" is a valid result — report it with the search terms tried,
  never pad with guesses.

## Escalation / de-escalation ladder

- haiku fails or returns garbage once → rerun on sonnet. Don't debug haiku.
- sonnet fails the SAME subtask twice → escalate to opus, attaching the full
  failure trail: what was tried, exact error output, current hypothesis.
  Escalation without the trail wastes the stronger model.
- opus cracks the pattern → downshift: turn the solution into a mechanical
  recipe and batch-apply it on sonnet/haiku.
- Hard cap: 2 retry rounds per task across all models. Still failing →
  stop, write down the blocker, report to the user. Never loop.

## Verification — never self-verify

The agent that produced work never certifies it. After any nontrivial product:

| Product | Verification |
|---|---|
| File written/edited | Fresh haiku agent reads it back: exists, complete, matches spec |
| Code change | Run the test or the actual command; report exit status + decisive lines |
| Eval number | Provenance tuple present (judgment.md §5); re-derivable from a saved log |
| Risky judgment (recipe change, paper claim) | Second opinion from a fresh opus agent, or 3 independent answers + pick best |

## Project-specific dispatch constraints

- **Single GPU.** Never run two training/eval jobs concurrently — serialize all
  GPU dispatches (memory: project_autoresearch_motionrep_loop). Subagents must
  be told this explicitly when their task involves the GPU.
- Long GPU runs: launch with `run_in_background`, monitor via the task
  notification, don't poll with sleep loops.
- Independent non-GPU dispatches: send in ONE message so they run in parallel.
- ARS plugin commands already pin models in frontmatter (opus for
  review/full pipeline, sonnet for mechanical modes) — that split is the
  precedent: judgment → opus, mechanics → sonnet.
