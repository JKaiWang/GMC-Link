# Maintenance Protocol

Written 2026-07-05. Who may edit what, where lessons go, when to compress.

## §1 Edit-permission tiers

| Tier | Files | Rule |
|---|---|---|
| FREE | scratchpad, logs, RESEARCH_NOTES.md (append), memory files, docs/*.md prose/typo fixes ONLY — never recipe values, numbers, or commands in docs/SHIP.md (those are PROPOSE/ASK-FIRST below) | Edit without asking. Backup rule (§2) still applies to rewrites. |
| PROPOSE | CLAUDE.md, .claude/rules/*.md, docs/SHIP.md recipe table, MEMORY.md restructure | Draft the change, show diff to user, apply on OK. Exception: single-line additions to CLAUDE.md Landmines/Routing that don't break the 150-line cap may go in directly — report after. |
| ASK-FIRST | paper/*, locked recipes' values, anything in .gitignore'd data/weights, settings*.json, git push | Never touch without explicit user instruction in THIS session. |

## §2 Backup rule

Before REWRITING any existing tracked file:
`cp FILE FILE.bak-$(date +%Y%m%d)` (append-only edits exempt).
Backups are not committed; delete backups older than the last user-confirmed
good state when housekeeping.

## §3 Lesson write-back (where learned things go)

- Experiment result (POS or NEG) → memory file, existing format (frontmatter:
  name/description/type) + one MEMORY.md index line. NEG results always —
  they are the veto list's fuel. Also add/adjust the docs/CLOSED_LEVERS.md row.
- Protocol landmine discovered (silently-wrong-number class) → memory file +
  propose a one-line addition to CLAUDE.md Landmines (PROPOSE tier).
- Harness/model fact learned → update .claude/rules/dispatch.md "Verified
  facts" with date + source (PROPOSE tier).
- User feedback/correction → feedback-type memory file with **Why** and
  **How to apply** lines. Never rely on remembering it.

## §4 Compression triggers (check when touching each file)

| File | Trigger | Action |
|---|---|---|
| CLAUDE.md | > 150 lines | Move content to docs/, keep index line |
| MEMORY.md | > 120 lines | Roll superseded/closed-family lines into MEMORY_ARCHIVE.md (e.g. 5 Case-2 lines → 1 rollup) |
| .claude/rules/*.md | > 200 lines each | Split examples into a docs/ appendix |
| docs/*.md | > 300 lines | Split by topic |
| settings.local.json permissions | one-off junk entries (dead task paths, old PIDs) | Propose cleanup list to user (ASK-FIRST tier) |

## §5 Consistency rules

- Numbers: memory canon > docs/ > prose in old logs. On conflict, memory wins;
  surface the conflict to the user rather than silently editing either side.
- Routing integrity: if you move/rename any file referenced by CLAUDE.md's
  routing table or @import line, update CLAUDE.md in the same change and
  read-back both.
- Institution files (.claude/rules/*, CLAUDE.md, docs/ index pages) are
  written in full sentences — caveman/ponytail compression applies to
  conversation, NOT to these files; ambiguity here multiplies across sessions.

## §6 Periodic review (cheap, monthly or at phase change)

Dispatch one sonnet agent with review template (templates.md §5) over
CLAUDE.md + .claude/rules/*: stale facts, broken paths, rules contradicting
current phase. Present findings to user. Phase changes (experiments→paper→
submission) are when institutions rot fastest.
