# Candidates ledger

`created: 2026-08-18` · decision record: [ADR-0009](../adrs/0009-candidates-ledger.md)

A **candidate** is the first step of the engagement ladder — **candidate → stub → survey → deep-dive** — and the only step that lives outside a tool report. A candidate
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

## Category 2 — harnesses

| Candidate | Stars | Why not (yet) |
|---|---|---|
| qwen-code (`QwenLM`) | 27.2k *(2026-08-18)* | Added 2026-08-18. Alibaba's terminal coding agent — cleanly category 2: own agent loop, tool execution, MCP, subagents, memory, multi-protocol model client (OpenAI/Anthropic/Gemini/Qwen APIs + Ollama/vLLM). A **gemini-cli descendant**: based on Gemini CLI v0.8.2 per its own acknowledgment, stopped syncing at Qwen Code v0.1, independent since — which makes the interesting read a *divergence study* against [gemini-cli](2-harnesses/gemini-cli.md) at its pin (what a year of independent, Qwen-optimized evolution did to the same architecture). Platform breadth (IDE plugins, desktop, daemon, IM bots) is surface around the harness, not a category ambiguity. Why not yet: nine harnesses already tracked; the divergence question needs a paired gemini-cli re-read to be worth anything. **2026-08-25: precondition met — gemini-cli [deep-dived](2-harnesses/gemini-cli.md) at HEAD.** The divergence is likely large and asymmetric: the policy engine, hooks system, skills, and subagents all postdate the v0.8.2-era fork point, so the study would mostly measure what qwen-code *didn't* inherit — worth knowing before spending the read |
| orca (`stablyai`) | 50.0k *(2026-08-20)* | Added 2026-08-20. YC-backed desktop/mobile/VPS "ADE" (TypeScript, MIT, created 2026-03 — ~50k stars in five months) that runs a fleet of *other* harnesses — Codex, Claude Code, OpenCode, Pi — side by side, each agent in its own git worktree, with SSH remote worktrees, diff-annotation review, an embedded browser ("design mode"), GitHub/Linear integration, a mobile companion for steering agents, and its own automation CLI. **Not a harness by the strict test** — no agent loop, context assembly, or permission model of its own; the loops belong to the hosted CLIs. First sighted instance of the **orchestrator-above-harnesses shape**: the interaction surface sits above category 2, and the load-bearing mechanics are category-3 bleed (worktree-per-agent Δcwd multiplication — the parallelism axis — plus SSH host multiplication). Filed under category 2 as the least-wrong primary: it competes at the surface the taxonomy says now decides the day-to-day experience. Recorded as a strain, same discipline as the resident-agent note in `tool-taxonomy.md` §2 — a second sighted product of this shape triggers the vocabulary question (does the orchestrator deserve its own name?), not this first one. Why not yet: the read worth doing is narrow and category-3-shaped — does its worktree-per-agent bootstrap survive the worktree/gitignore trap (the category's founding scar), and what do its SSH worktrees inject? — a targeted probe pass at most, and the category-3 queue (the three v2.0 coverage reads) is ahead of it |

## Category 4 — workflow frameworks

*(Table relocated 2026-08-18 from the category-4 index, text preserved. Original heading:
"Considered, not added (2026-07-28)" — the first eight rows are from that web +
GitHub-API sweep, stars as of 2026-07-28; later rows are dated inline.)*

| Candidate | Stars | Why not (yet) |
|---|---|---|
| BMAD-METHOD (`bmad-code-org`) | 51k | Famous, active — but its predicted profile (role-playing agent teams, process-gates-heavy) is the mechanism column exp-01 measured near zero. First in line if category-4 scope expands; would make a good ceremony-pole test subject **→ promoted to [stub](4-workflow-frameworks/bmad-method.md) 2026-08-18, deep-dived same day** (prediction half-falsified: build-first entry, ceremony being shed; half-confirmed: every framework gate prose — enforcement sold separately in bmad-loop) |
| hermes-agent (`NousResearch`) | 222k | A category-2 harness, not a framework (spec-kit installs *into* it). Queued on the category-2 backlog: [issue #1](https://github.com/leandromineti/ai-assisted-coding/issues/1) *(since ingested: [report](2-harnesses/hermes-agent.md), deep-dive)* |
| claude-task-master (`eyaltoledano`) | 28k | Quiet since 2026-04; MCP-server-shaped (category-6 bleed dominant) |
| SuperClaude_Framework | 24k | Single-harness (Claude Code only) — fails the category-4 portability test; useful as the boundary counterexample |
| wshobson/agents | 38k | Multi-harness plugin *marketplace* — category-6 distribution, no methodology |
| agent-os (`buildermethods`) | 5k | Too small, quieting since 2026-05 |
| microsoft/amplifier | 3k | Too small; watchlist |
| Kiro (AWS), Tessl | — | Closed products — observation-only if ever added; no clone possible |
| Conductor (`gemini-cli-extensions`) | 3.7k *(2026-08-18)* | Added 2026-08-18. Google-org SDD plugin ("measure twice, code once"; Context → Spec & Plan → Implement) installing into Antigravity and Claude Code — passes the portability test on paper and would extend the [SDD set](4-workflow-frameworks/README.md#spec-driven-development-sdd) beyond the trio. Young (created 2025-12-17) and plugin-distributed (category-6 delivery vehicle, like ECC's hooks). Queue behind BMAD **→ promoted to [stub](4-workflow-frameworks/conductor.md) 2026-08-18** |
| pilot-shell (`maxritter`) | 2.0k *(2026-08-18)* | Added 2026-08-18. Has a real process spine (spec-driven `/prd` → `/spec` with enforced TDD → `/build` judge loops), targets two harnesses (Claude Code primary + Codex) — passes the portability test, barely. Held back by ECC-shaped platform sprawl around the spine (bot, console, semantic search, code graph, own binary — spine-or-catalog needs a source read), youth (2025-10, 2k stars, 95% single-author), and a custom all-rights-reserved EULA (only non-OSI candidate here; check clone/read terms before ingesting) **→ promoted to [stub](4-workflow-frameworks/pilot-shell.md) 2026-08-18; EULA §2(c) permits internal-use reading** |
| spec-kitty (`Priivacy-ai`) | 1.5k *(2026-08-18)* | Added 2026-08-18. SDD, and literally a **spec-kit derivative** — carries spec-kit's commit history and `.specify` constitution layout (the `localden` commits in its log are imported history), then extends the pipeline toward a "governed software factory": work packages in kanban lanes, parallel agents in isolated git worktrees (category-3 bleed), review/accept/merge gates, per-mission retrospectives, `dispatch` governance records. Genuinely multi-maintainer (two leads, ~8k commits) — rare in this table. Why not yet: derivative of an already-tracked seed, so marginal new mechanism per read-hour vs BMAD; young (2025-10, 1.5k stars). Evidence the SDD family is speciating: spec-kit's intent pipeline + orchestration grafted on **→ promoted to [stub](4-workflow-frameworks/spec-kitty.md) 2026-08-18** |
| haft (`m0n0x41d`) | 1.4k *(2026-08-18)* | Added 2026-08-18. Not SDD — a **decision-governance** pole: typed decision records (frame → compare → decide) with **evidence decay** and parity enforcement, implementing Levenchuk's First Principles Framework; SQLite ledger served over MCP. Strongest portability claim in this table (Claude Code + Codex stable, 8 more adapters experimental). Why not yet: 1.4k stars, created 2025-12, ~100% single-author, and MCP-runtime delivery raises the claude-task-master category-6 question — is it an encoded methodology (4), an extension (6), or a memory tool (5)? Worth watching regardless: evidence decay is this repo's own `checked:`-dates discipline as a runtime mechanism, and typed decision records ≈ ADRs. MIT in LICENSE (GitHub API reports NOASSERTION) **→ promoted to [stub](4-workflow-frameworks/haft.md) 2026-08-18** |

## Category 6 — extensions

*(Section added 2026-08-19 by the balance arc, [issue #30](https://github.com/leandromineti/ai-assisted-coding/issues/30):
web sweep + GitHub-API facts, stars hand-typed per this ledger's convention. Purpose: give
the ~2027-01 standards re-check a sample beyond the 2026-08-18 memory arc —
[ADR-0016](../adrs/0016-extensions-stay-broad.md).)*

| Candidate | Stars | Why not (yet) |
|---|---|---|
| context7 (`upstash`) | 61.0k *(2026-08-19)* | Added 2026-08-19. Docs-injection MCP server — version-pinned library documentation pulled into context on demand; paired with GitHub MCP as the "essential combo" in most 2026 roundups, so arguably the most-installed third-party MCP server in coding use. Vendor-backed (Upstash), MIT, TypeScript. Why not yet: the mcp-server type has one reading slot in the arc and two qualified specimens (this and playwright-mcp); also hosted-service-backed — the server fronts Upstash's API, which re-raises mem0's OSS-boundary question at the type's very first read |
| playwright-mcp (`microsoft`) | 36.3k *(2026-08-19)* | Added 2026-08-19. First-party browser-automation MCP server — the de-facto standard for agent browser control. Apache-2.0, TypeScript. The type's canonical "one server, every harness" specimen, and the cleaner portability read of the two sighted (no hosted backend). Sighted alongside, not rowed: `github/github-mcp-server` (32.4k, Go, vendor-native) and `modelcontextprotocol/servers` (89.7k — the spec org's own reference monorepo, weaker as a *product* read) |
| skills (`anthropics`) | 170.5k *(2026-08-19)* | Added 2026-08-19. Anthropic's official skills collection — a first-party pack for the `SKILL.md` convention that ≥5 harnesses now consume. Why not yet: a first-party pack tests the "vendor features" arm, not the portability arm — the informative read pairs it with a third-party pack (e.g. `glebis/claude-skills`, ~100 skills) to see whether the format travels outside its vendor. License not machine-readable via the API — check before cloning. Context for the eventual read: Snyk's ToxicSkills audit (2026-02) found 36% of community skills carried ≥1 security flaw — the type's quality-floor datum |
| awesome-claude-code-subagents (`VoltAgent`) | 24.5k *(2026-08-19)* | Added 2026-08-19. 100+ installable subagent definitions — the subagent-def type's biggest dedicated pack. Cross-reference: `wshobson/agents` (38.9k) has sat in this ledger's category-4 table since 2026-07-28 with the verdict "category-6 distribution, no methodology" — it is effectively this type's largest sighting already, and a promotion would re-home it here. Why not yet: subagent-def is a harness-specific format (Types table) — the interesting read is whether the format travels at all, which wants the standards scoreboard question sharpened first |
| claude-code-hooks-mastery (`disler`) | 3.9k *(2026-08-19)* | Added 2026-08-19. Best-available hook-pack sighting, and the sighting is itself the finding: **the hook type has no large installable pack** — the biggest dedicated collections found are this (3.9k, educational shape: all 13 lifecycle events implemented as a mastery reference) and `karanb192/claude-code-hooks` (0.5k, a 20-plugin marketplace). Consistent with the scoreboard's "hooks: no sign of movement" row; ECC remains the only tracked at-scale hook *carrier* (as a config-pack). Why not yet: at this size a read moves no conclusion — the row exists to date the absence |
