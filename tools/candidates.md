# Candidates ledger

`created: 2026-08-18` · decision records:
[ADR-0009](../adrs/0009-candidates-ledger.md),
[ADR-0031](../adrs/0031-candidates-ledger-is-a-backlog.md)

A **candidate** is the first step of the engagement ladder — **candidate → stub → survey → deep-dive** — and the only step that lives outside a tool report. A candidate
has been *sighted and assessed, not ingested*: no clone in `upstream/`, no pinned
commit, no report file. The row itself is the claim, which sets the conventions:

- **Stars are hand-typed here, always with a date.** This is a deliberate, narrow
  exception to "never hand-type stars" — that rule governs reports, where
  `repo-facts.sh` exists to do it mechanically. A candidate has no clone to run it
  against.
- **This file is a backlog, not a history.** Everything here is open work: sighted,
  assessed, not ingested. **Promotion removes the row** — the report supersedes it, and
  the complete list of everything that *has* been ingested is the generated
  [`comparisons/tools.md`](../comparisons/tools.md) (ADR-0031, 2026-08-26; ADR-0009
  originally annotated rows in place). Anything in a row that is still load-bearing
  after the read — a licensing finding, a pre-read prediction the report will score —
  belongs in the report before the row goes; removed rows stay in git history.
  Refusal reasoning stays for tools we **declined**, which is what it is for.
- **Hand-kept by design** — a documented exception to methodology rule 3, same class
  as the ADR index table: these rows are primary dated observations (miniature
  decision records), not derived summaries of content that lives elsewhere.

## Category 2 — harnesses

| Candidate | Stars | Why not (yet) |
|---|---|---|
| qwen-code (`QwenLM`) | 27.2k *(2026-08-18)* | Added 2026-08-18. Alibaba's terminal coding agent — cleanly category 2: own agent loop, tool execution, MCP, subagents, memory, multi-protocol model client (OpenAI/Anthropic/Gemini/Qwen APIs + Ollama/vLLM). A **gemini-cli descendant**: based on Gemini CLI v0.8.2 per its own acknowledgment, stopped syncing at Qwen Code v0.1, independent since — which makes the interesting read a *divergence study* against [gemini-cli](2-harnesses/gemini-cli.md) at its pin (what a year of independent, Qwen-optimized evolution did to the same architecture). Platform breadth (IDE plugins, desktop, daemon, IM bots) is surface around the harness, not a category ambiguity. Why not yet: nine harnesses already tracked; the divergence question needs a paired gemini-cli re-read to be worth anything. **2026-08-25: precondition met — gemini-cli [deep-dived](2-harnesses/gemini-cli.md) at HEAD.** The divergence is likely large and asymmetric: the policy engine, hooks system, skills, and subagents all postdate the v0.8.2-era fork point, so the study would mostly measure what qwen-code *didn't* inherit — worth knowing before spending the read |
| kimi-code (`MoonshotAI`) | 7.1k *(2026-08-26)* | Added 2026-08-26. Moonshot AI's terminal coding agent (`kimi`), TypeScript, MIT, created 2026-05-22, pushed the day it was added. Cleanly category 2 on the README's own account: its own loop ("choose the next step based on the feedback it receives"), tool execution, MCP with a conversational `/mcp-config`, built-in `coder`/`explore`/`plan` subagents in isolated contexts, lifecycle hooks that "gate risky tool calls", and a skills/MCP **marketplace** that surfaces each install's trust level. Vendor-native but not locked — Kimi models out of the box, "other compatible providers" configurable. Two things make it worth more than a routine tenth harness. **(1) It corrects a claim this repo made the same day.** § Vendor span said Moonshot had no harness; it had shipped one three months earlier and nobody looked — see the correction there. **(2) Distribution is the read.** Single-binary install via `curl \| bash`, "no Node.js required", from a TypeScript codebase — every other TypeScript harness tracked here ships as an npm package, and codex's Rust bet was argued as a *security* choice. A TS harness compiling to a binary tests whether that bet was ever about the language. Also the fourth tracked **ACP** speaker (after gemini-cli, hermes-agent, dsh) — that is now convergence worth a standards-scoreboard row, not a per-tool curiosity. Why not yet: ten harnesses are tracked and the queue ahead is real (qwen-code's divergence study, hermes-agent's unread reasoning path, [issue #41](https://github.com/leandromineti/ai-assisted-coding/issues/41)); at 7.1k stars it is also the smallest category-2 candidate sighted, so the sighting is dated and left to ripen |
| orca (`stablyai`) | 50.0k *(2026-08-20)* | Added 2026-08-20. YC-backed desktop/mobile/VPS "ADE" (TypeScript, MIT, created 2026-03 — ~50k stars in five months) that runs a fleet of *other* harnesses — Codex, Claude Code, OpenCode, Pi — side by side, each agent in its own git worktree, with SSH remote worktrees, diff-annotation review, an embedded browser ("design mode"), GitHub/Linear integration, a mobile companion for steering agents, and its own automation CLI. **Not a harness by the strict test** — no agent loop, context assembly, or permission model of its own; the loops belong to the hosted CLIs. First sighted instance of the **orchestrator-above-harnesses shape**: the interaction surface sits above category 2, and the load-bearing mechanics are category-3 bleed (worktree-per-agent Δcwd multiplication — the parallelism axis — plus SSH host multiplication). Filed under category 2 as the least-wrong primary: it competes at the surface the taxonomy says now decides the day-to-day experience. Recorded as a strain, same discipline as the resident-agent note in `tool-taxonomy.md` §2 — a second sighted product of this shape triggers the vocabulary question (does the orchestrator deserve its own name?), not this first one. Why not yet: the read worth doing is narrow and category-3-shaped — does its worktree-per-agent bootstrap survive the worktree/gitignore trap (the category's founding scar), and what do its SSH worktrees inject? — a targeted probe pass at most, and the category-3 queue (the three v2.0 coverage reads) is ahead of it |

## Category 4 — workflow frameworks

*(Table relocated 2026-08-18 from the category-4 index, text preserved. Original heading:
"Considered, not added (2026-07-28)" — the first eight rows are from that web +
GitHub-API sweep, stars as of 2026-07-28; later rows are dated inline.)*

| Candidate | Stars | Why not (yet) |
|---|---|---|
| claude-task-master (`eyaltoledano`) | 28k | Quiet since 2026-04; MCP-server-shaped (category-6 bleed dominant) |
| SuperClaude_Framework | 24k | Single-harness (Claude Code only) — fails the category-4 portability test; useful as the boundary counterexample |
| wshobson/agents | 38k | Multi-harness plugin *marketplace* — category-6 distribution, no methodology |
| agent-os (`buildermethods`) | 5k | Too small, quieting since 2026-05 |
| microsoft/amplifier | 3k | Too small; watchlist |
| Kiro (AWS), Tessl | — | Closed products — observation-only if ever added; no clone possible |

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
