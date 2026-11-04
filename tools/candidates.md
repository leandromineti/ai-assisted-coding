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
| ZCode (`Z.ai` / Zhipu) | — *(closed, no repo)* | Added 2026-08-26, sighted at [zcode.z.ai](https://zcode.z.ai/en) (v3.9.2). Z.ai's **"Official Harness for GLM-5.3"** — a proprietary desktop + CLI agent for macOS/Windows/Linux, installers only, no source. Deep GLM-5.3 integration with GLM-5.3-Flash "built in for multimodal tasks"; no other model provider documented, so it is the most *closed* vendor-native harness sighted — Claude Code at least drives one vendor's models under a general-purpose design. Named features: **Goals** (long-running tasks with continuous planning and verification), skills, command palette, bot control "from WeChat, Feishu, or Telegram" (hermes-agent's messaging-surface shape, second instance), and MCP support that "supports 20+ agent tools, **including ZCode, Claude Code, and more**" — i.e. it also reaches *over* other harnesses, the orca orchestrator shape from the row below, appearing here inside a vendor-native product. Sold on subscription tiers (Lite $12.60 / Pro $56 / Max $117.60 per month), which resolves what the GLM Coding Plan is: Z.ai sells its models into other people's harnesses **and** ships its own. Why not yet: **closed — no clone, no source to trace**, so a report would be observation-only like [claude-code](2-harnesses/claude-code.md), and that grade is worth spending only when the product anchors a claim. It already anchors one: it is the eighth of eight model makers to ship a harness, recorded in `tool-taxonomy.md` § Maker span |
| kimi-code (`MoonshotAI`) | 7.1k *(2026-08-26)* | Added 2026-08-26. Moonshot AI's terminal coding agent (`kimi`), TypeScript, MIT, created 2026-05-22, pushed the day it was added. Cleanly category 2 on the README's own account: its own loop ("choose the next step based on the feedback it receives"), tool execution, MCP with a conversational `/mcp-config`, built-in `coder`/`explore`/`plan` subagents in isolated contexts, lifecycle hooks that "gate risky tool calls", and a skills/MCP **marketplace** that surfaces each install's trust level. Vendor-native but not locked — Kimi models out of the box, "other compatible providers" configurable. Two things make it worth more than a routine tenth harness. **(1) It corrects a claim this repo made the same day.** § Maker span said Moonshot had no harness; it had shipped one three months earlier and nobody looked — see the correction there. **(2) Distribution is the read.** Single-binary install via `curl \| bash`, "no Node.js required", from a TypeScript codebase — every other TypeScript harness tracked here ships as an npm package, and codex's Rust bet was argued as a *security* choice. A TS harness compiling to a binary tests whether that bet was ever about the language. Also the fourth tracked **ACP** speaker (after gemini-cli, hermes-agent, dsh) — that is now convergence worth a standards-scoreboard row, not a per-tool curiosity. Why not yet: twelve harnesses are tracked and the queue ahead is real — hermes-agent's unread reasoning path and [issue #41](https://github.com/leandromineti/ai-assisted-coding/issues/41) (qwen-code's divergence study, cited here when the row was written, was DONE on 2026-08-27 and its ledger row promoted away); at 7.1k stars it is also the smallest category-2 candidate sighted, so the sighting is dated and left to ripen |
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

## Category 5 — memory

*(Section added 2026-11-04 with its first row. The 2026-08-18 memory arc ingested
every tool it sighted straight into [`5-memory/`](5-memory/README.md), so the category
had no candidate stage until now.)*

| Candidate | Stars | Why not (yet) |
|---|---|---|
| supermemory (`supermemoryai`) | 31.5k *(2026-11-04, GitHub API `stargazers_count`)* | Added 2026-11-04. A "memory and context engine": LLM fact extraction, user profiles (static + dynamic), hybrid RAG+memory search, contradiction resolution and date-based forgetting, behind one API — hosted, or a self-host binary (`supermemory-server`, `server-v0.0.9` released 2026-10-12). Repo MIT, TypeScript, created 2024-02-27, pushed the day it was added. Sold on benchmarks ("#1 on every major AI memory benchmark") — the second tool in the category sold that way, after [mem0](5-memory/mem0.md), whose deep-dive found the shipped write path ≠ the paper. **The openness question decides the read.** The vendor's own self-hosting doc (`apps/docs/self-hosting/local-vs-enterprise.mdx`, read 2026-11-04 via the contents API) says the self-host binary's "server source is not in the public repository", and the binary is free up to a 10,000-document "lite license" limit. The MIT repo holds the clients: the MCP server (`apps/mcp`), web app, SDK/framework wrappers, docs. The harness plugins live in separate repos with no machine-readable license (API `license: null`, 2026-11-04): claude-supermemory 2.8k, opencode-supermemory 1.7k, codex-supermemory 0.06k. So capture and recall are open-source code and consolidation is a closed binary — mem0's OSS-boundary question, now drawn as a clean code/binary line. **Already present at a tracked pin.** [hermes-agent](2-harnesses/hermes-agent.md) at `f97608f178` ships `plugins/memory/supermemory/` (per-turn capture into one document per session per 4-hour window; hosted or self-host `base_url`) — one of 7 provider directories by `git ls-tree --name-only f97608f178 plugins/memory/` (dirs only), two of them tracked category-5 tools (mem0, openviking). Here the integration is installed from the harness side: hermes-agent ships the provider, rather than supermemory shipping a plugin. MemOS's in-repo `evaluation/` also commits a Supermemory client, as a competitor to benchmark against ([memos](5-memory/memos.md) § Benchmarks). **Pre-read predictions** (a report must score these): (1) a deep-dive traces **at most 2 of 3** components (capture, recall) from source — true if consolidation stays docs-route; false if the engine source is published. (2) `injection_trust_boundary` **✗** in the Claude Code plugin — true if recalled memories enter context unfenced; false if they are wrapped as untrusted data. (3) **No native-memory displacement** — true if the plugin leaves CLAUDE.md/auto-memory writes alone; false if it blocks or redirects them the way mem0's does (conclusion 8). (4) `memory_import` **breaks the category's 4-for-4** — true if neither docs nor the open code ships an importer from a rival store or harness-native memory (connectors import *documents*, which don't count); false if one exists. Why not yet: the read worth doing is the capture/recall half through the Claude Code plugin and `apps/mcp`, across three repos with an unlicensed plugin. The engine half caps at docs-route, which is the same grade as a closed product |

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
