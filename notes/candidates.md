# Candidates ledger

`created: 2026-08-18` · decision record: [ADR-0009](../adrs/0009-candidates-ledger.md)

A **candidate** is the first rung of the engagement ladder — **candidate → stub →
survey → deep-dive** — and the only rung that lives outside a tool report. A candidate
has been *sighted and assessed, not ingested*: no clone in `upstream/`, no pinned
commit, no report file. The row itself is the claim, which sets the conventions:

- **Stars are hand-typed here, always with a date.** This is a deliberate, narrow
  exception to "never hand-type stars" — that rule governs reports, where
  `repo-facts.sh` exists to do it mechanically. A candidate has no clone to run it
  against.
- **Append-mostly.** Promotion (running the ingest operation) *annotates* the row with
  a dated pointer to the new report — it never deletes it. Refusal reasoning stays so
  it isn't re-derived later.
- **Hand-kept by design** — a documented exception to methodology rule 3, same class
  as the ADR index table: these rows are primary dated observations (miniature
  decision records), not derived summaries of content that lives elsewhere.

## Layer 2 — harnesses

| Candidate | Stars | Why not (yet) |
|---|---|---|
| qwen-code (`QwenLM`) | 27.2k *(2026-08-18)* | Added 2026-08-18. Alibaba's terminal coding agent — cleanly layer 2: own agent loop, tool execution, MCP, subagents, memory, multi-protocol model client (OpenAI/Anthropic/Gemini/Qwen APIs + Ollama/vLLM). A **gemini-cli descendant**: based on Gemini CLI v0.8.2 per its own acknowledgment, stopped syncing at Qwen Code v0.1, independent since — which makes the interesting read a *divergence study* against [gemini-cli](02-harnesses/gemini-cli.md) at its pin (what a year of independent, Qwen-optimized evolution did to the same architecture). Platform breadth (IDE plugins, desktop, daemon, IM bots) is surface around the harness, not a layer ambiguity. Why not yet: nine harnesses already tracked; the divergence question needs a paired gemini-cli re-read to be worth anything |

## Layer 4 — workflow frameworks

*(Table relocated 2026-08-18 from the layer-4 index, text preserved. Original heading:
"Considered, not added (2026-07-28)" — the first eight rows are from that web +
GitHub-API sweep, stars as of 2026-07-28; later rows are dated inline.)*

| Candidate | Stars | Why not (yet) |
|---|---|---|
| BMAD-METHOD (`bmad-code-org`) | 51k | Famous, active — but its predicted profile (role-playing agent teams, process-gates-heavy) is the mechanism column exp-01 measured near zero. First in line if layer-4 scope expands; would make a good ceremony-pole test subject **→ promoted to [stub](04-workflow-frameworks/bmad-method.md) 2026-08-18** |
| hermes-agent (`NousResearch`) | 222k | A layer-2 harness, not a framework (spec-kit installs *into* it). Queued on the layer-2 backlog: [issue #1](https://github.com/leandromineti/ai-assisted-coding/issues/1) *(since ingested: [report](02-harnesses/hermes-agent.md), deep-dive)* |
| claude-task-master (`eyaltoledano`) | 28k | Quiet since 2026-04; MCP-server-shaped (layer-5 bleed dominant) |
| SuperClaude_Framework | 24k | Single-harness (Claude Code only) — fails the layer-4 portability test; useful as the boundary counterexample |
| wshobson/agents | 38k | Multi-harness plugin *marketplace* — layer-5 distribution, no methodology |
| agent-os (`buildermethods`) | 5k | Too small, quieting since 2026-05 |
| microsoft/amplifier | 3k | Too small; watchlist |
| Kiro (AWS), Tessl | — | Closed products — observation-only if ever added; no clone possible |
| Conductor (`gemini-cli-extensions`) | 3.7k *(2026-08-18)* | Added 2026-08-18. Google-org SDD plugin ("measure twice, code once"; Context → Spec & Plan → Implement) installing into Antigravity and Claude Code — passes the portability test on paper and would extend the [SDD set](04-workflow-frameworks/index.md#spec-driven-development-sdd) beyond the trio. Young (created 2025-12-17) and plugin-distributed (layer-5 delivery vehicle, like ECC's hooks). Queue behind BMAD **→ promoted to [stub](04-workflow-frameworks/conductor.md) 2026-08-18** |
| pilot-shell (`maxritter`) | 2.0k *(2026-08-18)* | Added 2026-08-18. Has a real process spine (spec-driven `/prd` → `/spec` with enforced TDD → `/build` judge loops), targets two harnesses (Claude Code primary + Codex) — passes the portability test, barely. Held back by ECC-shaped platform sprawl around the spine (bot, console, semantic search, code graph, own binary — spine-or-catalog needs a source read), youth (2025-10, 2k stars, 95% single-author), and a custom all-rights-reserved EULA (only non-OSI candidate here; check clone/read terms before ingesting) **→ promoted to [stub](04-workflow-frameworks/pilot-shell.md) 2026-08-18; EULA §2(c) permits internal-use reading** |
| spec-kitty (`Priivacy-ai`) | 1.5k *(2026-08-18)* | Added 2026-08-18. SDD, and literally a **spec-kit derivative** — carries spec-kit's commit history and `.specify` constitution layout (the `localden` commits in its log are imported history), then extends the pipeline toward a "governed software factory": work packages in kanban lanes, parallel agents in isolated git worktrees (layer-3 bleed), review/accept/merge gates, per-mission retrospectives, `dispatch` governance records. Genuinely multi-maintainer (two leads, ~8k commits) — rare in this table. Why not yet: derivative of an already-tracked seed, so marginal new mechanism per read-hour vs BMAD; young (2025-10, 1.5k stars). Evidence the SDD family is speciating: spec-kit's intent pipeline + orchestration grafted on **→ promoted to [stub](04-workflow-frameworks/spec-kitty.md) 2026-08-18** |
| haft (`m0n0x41d`) | 1.4k *(2026-08-18)* | Added 2026-08-18. Not SDD — a **decision-governance** pole: typed decision records (frame → compare → decide) with **evidence decay** and parity enforcement, implementing Levenchuk's First Principles Framework; SQLite ledger served over MCP. Strongest portability claim in this table (Claude Code + Codex stable, 8 more adapters experimental). Why not yet: 1.4k stars, created 2025-12, ~100% single-author, and MCP-runtime delivery raises the claude-task-master layer-5 question — is it an encoded methodology or a memory extension? Worth watching regardless: evidence decay is this repo's own `checked:`-dates discipline as a runtime mechanism, and typed decision records ≈ ADRs. MIT in LICENSE (GitHub API reports NOASSERTION) **→ promoted to [stub](04-workflow-frameworks/haft.md) 2026-08-18** |
