# 5 — Extensions & protocols (cross-layer bucket)

> Renamed from "Portable artifacts" 2026-08-17: portability is not an intrinsic
> property of an extension but a status the ecosystem confers by adoption — unevenly
> across the kinds below (see the Standards scoreboard and the dated rename note in
> [`../../taxonomy.md`](../../taxonomy.md) §3).

`checked: 2026-08-18`

What the agent can **see and touch**, as distributable content. **A bucket, not a layer,
since the 2026-07-30 taxonomy revision** (three core layers; trigger fired at the ECC
deep-dive — see the executed-revision note in [`../../taxonomy.md`](../../taxonomy.md)).
The membership test is unchanged: independent distribution — authored, versioned, and
installed separately from any harness. The "3" is a storage key.

This index covers the **installable things**. The specifications they implement — MCP the
protocol, the `AGENTS.md` convention — are not layer entries; they live in
[`../standards/`](../cross-cutting/standards.md).

## Kinds

Reports in this bucket carry a `kind:` frontmatter key from this table's vocabulary
(`mcp-server · skill · hook · subagent-def · rules-file · config-pack · memory`) —
added 2026-08-18 so the bucket can be sliced by kind as it grows.

| Kind | What it does | Portability |
|------|--------------|-------------|
| **MCP servers** | Expose external systems (filesystems, APIs, databases, browsers, SaaS) as tools over the Model Context Protocol. | High — one server works across Claude Code, Codex, Cursor, Copilot, Gemini CLI, OpenCode, Devin. |
| **Skills** | Packaged instructions loaded on demand for a class of task. | Converging (2026-07-28): `SKILL.md` consumed by ≥4 harnesses per spec-kit's integration registry — convention-level, like rules files. See [standards](../cross-cutting/standards.md). |
| **Hooks** | Deterministic code the harness runs at lifecycle points (pre/post tool use, session start/stop). Not model-mediated — the harness executes them, so they *always* fire. | Harness-specific. |
| **Subagent definitions** | Named agents with their own prompt, tools, and model, spawned for isolated work. | Harness-specific format; the pattern is universal. |
| **Rules files** | `CLAUDE.md`, `AGENTS.md`, `.cursorrules` — standing instructions injected into context. | Convention-level only — see [standards](../cross-cutting/standards.md). |
| **Config packs** | Curated bundles of the other kinds at scale (skills + agents + rules + hooks), installed as a set. | Rides on the file conventions of what it bundles — ECC's ~13 install targets are the measured case. |
| **Memory** | Persistent cross-session state fed by hooks/MCP and injected back at session start — the agent↔time edge as an installable product. *(Kind added 2026-08-18; seeds below.)* | Seven seeds, 2026-08-18, spanning two recurring shapes — harness-facing (ai-memory via MCP + hooks; memos and everos via per-harness plugins) and SDK/API-facing (mem0, cognee, memori, memmachine) — with three distinct technical wagers (markdown wiki, knowledge graph, action capture) and an "OS" branding convergence. Portability claims untested here. |

## Why this is a layer and not a pile of harness features

An MCP server is built once and consumed by every major harness. Nothing about it belongs
to a particular agent loop. The same is *aspirationally* true of skills and rules files.

The counter-argument worth holding: hooks and subagent definitions are harness-specific
today, so this layer is only partly portable — arguably it's "MCP plus a pile of vendor
features" wearing a layer's clothes. Whether that resolves depends on standards adoption,
which is tracked in [`../standards/`](../cross-cutting/standards.md) rather than here.

## Reports

| Tool | Depth | One-line |
|---|---|---|
| [**ECC** (everything-claude-code)](ecc.md) | deep-dive (2026-07-30) | 236k stars in ~6.5 months; reclassified here from provisional layer 4 — a config pack at scale (281 skills, 67 agents, rules, enforcement hooks) plus the set's only *harness-independent* autonomous learning loop (hook-observed "instincts", traced in source). Solo-author; commercial ring (Pro, GitHub App); `ecc2` Rust control plane growing toward layer 2. |
| [**ai-memory**](ai-memory.md) | deep-dive (2026-08-18) | Cross-harness memory as one Rust daemon: hook capture (closed 10-kind vocabulary) → rule-based session pages in a git-versioned markdown wiki → heuristic handoff injected at next session start, any harness. Zero-LLM default path; with a provider, a **source-verified background learning loop** auto-approves its own wiki edits (`_rules/`, `procedures/`) — second harness-independent instance after ECC. Surprise: the continuity baton is first + last prompt + tool names, no LLM; the rich memory is pull-only via 18 MCP tools. |
| [**mem0**](mem0.md) | stub (2026-08-18) | "The memory layer for personalized AI" — YC-backed managed platform + OSS SDK (Python/TS) that LLM-extracts memories from conversations and retrieves them per-user; publishes its own benchmark results (LoCoMo, LongMemEval). Reaches coding harnesses via integrations and ships itself partly as a `SKILL.md` skill. The SDK-facing shape of the memory kind. |
| [**cognee**](cognee.md) | survey (2026-08-18) | The kind's incumbent (2023-08, 30.1k stars) and its knowledge-graph pole — at the price of a tripartite graph+vector+relational consistency surface. Membership verdict: the SDK sits in the bucket **via its shims**, and the shims are where the coding-agent product lives (agent-scoped datasets, session/permanent split, agent-invoked `improve` consolidation, coding-rule extraction). No autonomous loop in-repo (`learning_loop: false`); the marketplace plugin automates capture but runs in API mode, where rule extraction is explicitly skipped. ai-memory's opposition dossier spot-checked: both structural claims corroborated (LiteLLM/Instructor churn guard; the Ladybug fork's costs written into pyproject). |
| [**memori**](memori.md) | stub (2026-08-18) | "Memory from what agents do, not just what they say" — Rust core with Python/Node bindings, BYODB or cloud, 16.1k stars in ~13 months. Action-capture framing, embeddable-engine shape. |
| [**everos**](everos.md) | stub (2026-08-18) | EverMind's "Ever OS": durable writes + retrieval, Claude Code plugin shipped in-repo. Youngest seed (first commit 2026-06-05; 12.1k stars in ~10 weeks, on only 88 commits — read its numbers with that ratio in mind). |
| [**memos**](memos.md) | survey (2026-08-18) | Two products in one repo: the Python research OS (MemCube, paper lineage) and — what harnesses actually install — a standalone TS core ("Reflect2Evolve V7") behind OpenClaw/DSH/hermes adapters. **Learning loop verified: background**, an event-driven cascade (trace capture → reward backprop → policy induction → world models → skill crystallization) — the kind's formal ceiling: memory as a scored, evolving policy database that *mints skills*, not prose. Third harness-independent instance; issue #13's trigger still unfired. |
| [**memmachine**](memmachine.md) | stub (2026-08-18) | "The open-source memory layer for AI agents" — plain store-and-retrieve SDK (Python), OpenClaw/Strands integrations. The kind's commodity baseline. |

## The distinction that matters

- **Layer 5 governs reach** — what the agent can access.
- **Layer 4 governs process** — what it does with that access.

A tool that adds a database connection is layer 5. A tool that says "write the spec before
you touch the database" is layer 4. ECC is the case that proved the distinction cuts
cleanly even at 236k stars: enormous reach, deliberately no prescribed process — see the
verdict section of [`ecc.md`](ecc.md).

## Open questions

*Questions about the specifications themselves live in
[`../standards/`](../cross-cutting/standards.md). These are about the installable artifacts.*

- Hooks are the only deterministic escape hatch in an otherwise probabilistic system —
  the harness executes them, so they always fire. How much of a workflow *should* be moved
  into them, and what's lost when you do?
- Subagent definitions isolate context, but each spawn pays a cold-start cost in tokens and
  re-derived understanding. When does isolation actually beat a single longer context?
- Skills load on demand rather than up front. Does just-in-time loading measurably beat a
  fat rules file, or does it just move the same tokens around?
- Is there a real difference between a skill and a well-written section of a rules file,
  other than *when* it enters the context?
- **Memory (added 2026-08-18):** harnesses ship native memory loops (conclusion 8's
  absorption story — hermes on-by-default, codex built-but-off), yet independent memory
  extensions are growing fast anyway (ai-memory: 2.6k stars in 3 months). What does the
  extension buy that the native loop doesn't — cross-harness continuity is the obvious
  candidate bet — and does conclusion 8 predict its absorption next?
- The memory-authorship open decision (design-principles, "What the field visibly does
  not agree on") gains a fourth position: agent-written **and independently stored**
  (ai-memory's wiki, mem0's store) vs the three harness-side positions already recorded.
- Issue #13's `learning_loop` promotion trigger: **ai-memory verified in source
  (2026-08-18)** as the second harness-independent autonomous loop after ECC — mechanism
  `background` (server-side scheduler, default-on with a provider, auto-approving). The
  promotion trigger itself still hasn't fired: `background` now has four instances,
  `in-loop` and `manual` still one each.
