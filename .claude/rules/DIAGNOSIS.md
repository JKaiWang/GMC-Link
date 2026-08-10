# Harness Diagnosis — top 3 leaks (written 2026-07-05 by Fable 5)

Read this when deciding what to optimize about the workflow itself.
Each item: evidence → concrete fix a Sonnet-level session can execute today.

## Leak 1 — Always-loaded context bloat (biggest, paid every session)

Evidence (measured 2026-07-05):
- ~200 deferred MCP tool names load at session start: Canva, Figma, Gmail,
  Google Calendar/Drive, Notion, Vercel, Playwright. This is an offline ML
  research repo — none of these are ever used here.
- ~80 skill descriptions load at start; the vercel plugin alone contributes ~30.
- MEMORY.md index was 141 lines (auto-loaded), MEMORY_ARCHIVE.md only 27 —
  archiving has lagged far behind accumulation (145 memory files).
- Old CLAUDE.md was 185 lines, all always-loaded.

Fix (in priority order):
1. USER ACTION (session cannot do this itself): disconnect unused claude.ai
   connectors (Canva, Figma, Gmail, Calendar, Drive, Notion) and disable the
   vercel plugin for this machine/project. Keep: ARS, si, caveman, ponytail,
   autoresearch-agent, github, zotero. Ask the user once; if declined, drop it.
2. Keep MEMORY.md ≤ 120 lines. When over: move superseded/closed-family entries
   (e.g. Case-2 1a–1d = 5 lines → 1 rollup line) into MEMORY_ARCHIVE.md.
   Procedure: .claude/rules/maintenance.md §4.
3. Keep CLAUDE.md ≤ 150 lines, index-only. Long content → docs/, referenced on
   demand. (Done 2026-07-05; hold the line.)

## Leak 2 — Main thread doing grunt work

Evidence: session histories show whole-file reads of RESEARCH_NOTES.md (579
lines) and multi-hundred-line eval logs pasted into the main conversation.
Context fills → auto-summarization → earlier decisions get lossy → rework.
This is a double leak: tokens AND correctness.

Fix: follow .claude/rules/dispatch.md. Hard rules:
- Main thread reads ≤ 2 files directly per question; more → delegate to an
  Explore agent (model: haiku) that returns conclusions + file:line only.
- Never paste raw logs into the conversation. Runner saves to a file, reports
  path + exit status + the 1–3 decisive lines.
- Batch mechanical edits go to a sonnet agent with the templates in
  .claude/rules/templates.md.

## Leak 3 — Eval-protocol landmines → silently wrong numbers → wasted reruns

Evidence (all real incidents from memory):
- gt_template vs gt_template_old confusion cost weeks and produced a misleading
  "closed ~10-point HOTA gap" note (−6.4 HOTA from convention mismatch).
- Forgetting GMC_RAW_COS=1 silently changes every score (no error raised).
- Single-seed results overturned at n=3 (sw CLIP early-concat looked POS,
  died at n=3). AUC-gate verdicts overturned at HOTA three separate times.
- Retrying levers that memory already falsified (~40 closed levers).

Fix:
- Before ANY eval run: walk the 7-item Landmines list in CLAUDE.md. It is a
  checklist, not prose.
- Every reported number carries the provenance tuple:
  (arch, n seeds, GMC_SUFFIX, gt convention, pooled|macro, recipe).
  A number without the tuple is not reportable — this is the quality floor in
  .claude/rules/judgment.md §5.
- Before proposing an experiment: check docs/CLOSED_LEVERS.md, then
  `grep -ril "<lever keyword>" /home/seanachan/.claude/projects/-home-seanachan-GMC-Link/memory/`.

## Not measured (honest note)

No token telemetry was available in-session; the ranking above is from
structural evidence (what loads, what history shows), not metered usage.
If the user wants hard numbers: check the usage dashboard at claude.ai
settings. Safety-routing to Opus: CONFIRMED it counts toward the same usage
window (support.claude.com article 15363606, checked 2026-07-05 via search
extract — high confidence, not line-verified).
