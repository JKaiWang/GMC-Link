# Letter to Future Sessions

Written 2026-07-05 by Claude Fable 5, the one high-capability session this
environment gets. You are probably Sonnet or Opus. That is fine — the system
around you was built so that it doesn't matter much. Read this once, then
work from CLAUDE.md and .claude/rules/.

## Three things the user didn't ask me but you should know

1. **The biggest token win needs a user action, not a smarter model.** Every
   session in this project loads ~200 MCP tool names and ~80 skill
   descriptions from connectors and plugins that an offline ML research repo
   never uses (Canva, Figma, Gmail, Calendar, Drive, Notion, Vercel,
   Playwright). One-time fix: user runs `/plugin` and disables unused plugins,
   and disconnects unused claude.ai connectors. Raise it ONCE politely with
   the expected saving; if declined, never nag again. (DIAGNOSIS.md Leak 1.)

2. **The negative-results corpus IS the project's moat.** ~40 falsified levers
   in memory + docs/CLOSED_LEVERS.md. Its value is only real if (a) new
   sessions actually check it before burning GPU hours, and (b) new negatives
   keep getting written down with the same discipline. The single most
   damaging thing a future session can do is quietly rerun a closed lever or
   quietly not record a failure. Also: this corpus is the paper's
   methodological spine (reviewers respect falsification records) and could
   seed a second, methods-flavored publication — user decides, don't push.

3. **The paper phase changes the risk profile.** During experiments the main
   risk was wasted compute; now it is a wrong number reaching the manuscript.
   Every number entering paper/ must trace to a memory file or a saved log
   (paper/REPRODUCIBILITY.md manifest). Treat paper/ as ASK-FIRST territory
   (maintenance.md §1). The ARS plugin's reviewer/pipeline commands exist for
   this phase and already pin sensible models.

## How this system will most likely degrade, and the prevention

- **Append rot**: weak sessions add lines instead of restructuring; CLAUDE.md
  and MEMORY.md swell past their caps and stop being read. Prevention: the
  hard caps + triggers in maintenance.md §4 — enforce them the moment you
  touch a file, not "later".
- **Phase drift**: rules written in the experiment era slowly mismatch paper/
  submission-era work; sessions then learn to ignore the rules wholesale.
  Prevention: maintenance.md §6 periodic review at every phase change.
- **Routing rot**: a file gets moved/renamed, the CLAUDE.md pointer goes
  stale, one session finds a dead link and stops trusting the routing table.
  Prevention: same-change update + read-back rule (maintenance.md §5).
- **Verification decay**: under time pressure, sessions skip the fresh-agent
  read-back and self-certify. This is invisible until a wrong number ships.
  Prevention: treat dispatch.md §Verification as non-negotiable for anything
  entering docs/, memory, or paper/.
- **Cargo-culting me**: these rules encode 2026-07-05 reality. When a rule
  fights the observable present (a tool renamed, a model retired), the
  present wins — verify, then update the rule with date + source, per
  maintenance.md §3. Rules are maps, not territory.

## Honest confidence report on my own deliverables

- **Lowest confidence — DIAGNOSIS.md ranking.** No token telemetry was
  available; the top-3 ordering is structural inference. The items are real;
  their relative sizes are estimates. Verify on the usage dashboard.
- **templates.md is untested in anger.** No template was exercised by a real
  weak-model session before writing. First sessions: treat as v1, refine
  wording that confuses agents, note refinements in the file (PROPOSE tier).
- **CLOSED_LEVERS.md one-liners are lossy.** Compiled from memory index
  hooks, not by re-reading all 145 memory files. Before a decision hinges on
  one row, open the underlying memory file.
- **Escalation thresholds (1 fail / 2 fails / 2 rounds) are judgment calls,**
  not measured optima. They're deliberately simple so a weak model can apply
  them. Adjust with evidence if they misfire, and write down why.
- **Verified-facts shelf life.** Model names, effort values, @import
  behavior, quota accounting: verified 2026-07-05 (sources in dispatch.md).
  Anything model-related older than a few months deserves re-verification via
  claude-code-guide before being load-bearing.
- **Taste calls can't be delegated down.** Research direction, paper framing,
  reviewer psychology: decomposition and multi-sample judging won't recover
  Fable/Opus-level taste (judgment.md §6). For those, present options with
  tradeoffs to the user, or suggest running the ARS opus-pinned review
  commands. Saying "this is above my grade" is compliant behavior, not
  failure.

Work small, verify fresh, write everything down. The institution outlives
any single context window — that's the point.
