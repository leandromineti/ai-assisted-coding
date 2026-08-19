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
| **Memory** | Persistent cross-session state fed by hooks/MCP and injected back at session start — the agent↔time edge as an installable product. *(Kind added 2026-08-18; seeds below.)* | Seven seeds, four read (2026-08-18 arc: ai-memory deep-dive; memos, cognee, mem0 surveys). Four distinct wagers verified — markdown wiki (ai-memory), RL policy database that mints skills (memos), knowledge graph over a tripartite store (cognee), LLM-extraction platform sold on benchmarks (mem0) — and four consolidation postures: background cron, per-turn event cascade, agent-invoked, hook-capture-to-platform. Zero shared formats (scoreboard row); each vendor pays the harness-fragmentation cost separately, in code. The SDK-facing shape earns membership only via its shims, and the shims are where the coding-agent behavior lives — up to and including mem0's plugin *blocking the harness's native memory writes* (the displacement finding, conclusion 8). *(2026-08-19: the comparison is now structured — 11-key `memory_features` registry block + [generated matrix](../../comparisons/features.md#memory-extensions-layer-5-kind-memory), ADR-0013.)* |

## The memory matrix — first cut (2026-08-19)

The reading arc's prose comparison became a registry block
([ADR-0013](../../adrs/0013-memory-features-block.md)): 11 keys, generated
[matrix](../../comparisons/features.md#memory-extensions-layer-5-kind-memory), cells
set only on the four read tools. What the first cut shows:

- **Where the kind agrees** (4/4 among read tools): typed memory tiers; and 3/4 on
  hybrid retrieval fusion, decay lifecycles, and shipping a harness installer — the
  engineering table stakes have converged even though formats haven't.
- **Where it splits** — the identity axes: store wager (`files-git` / `vector` /
  `rows+vector` / `graph+vector+rows`, no two alike), capture path (hook / adapter /
  agent-invoked), recall injection (auto / pull-only / both), and the trust boundary
  (2✓, one explicit open question, one unchecked — the security axis is the least
  converged, and memory injection is a prompt-injection vector).
- **The asymmetry worth flagging**: every axis above has 2–4 verified instances, but
  the kind's *headline* bet — cross-harness continuity as a working mechanism — has
  exactly **one** (ai-memory's baton, and it is thin: first + last prompt + tool
  names, no LLM). The category's sales pitch rests on its least-instantiated feature.
  The [rig question](#open-questions) (capture a session, switch harness, measure what
  the second agent actually knows) is what would test it.

Single-instance bets stay out of the vocabulary by the two-instance rule but are the
differentiators to watch: zero-LLM default (ai-memory), git-versioned store
(ai-memory), native-memory displacement (mem0), competitor import (mem0), skill
crystallization (memos), provenance audit (ai-memory).

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
| [**mem0**](mem0.md) | survey (2026-08-18) | The kind's commercial pole (YC-backed platform + OSS SDK). Shipped write path ≠ the 553-citation paper: V3 is ADD-only extraction with linking, the paper's ADD/UPDATE/DELETE/NOOP phase is retired. In-repo plugin installs hook capture into six harnesses with a **background learning loop** (Stop-hook capture, `infer=True`) — fourth verified instance — plus the kind's most aggressive move: a PreToolUse gate that **blocks the harness's native MEMORY.md writes** and redirects to mem0's tool. Displacement, not just colonization. Vendor paper graded separately ([2025-mem0](../../refs/2025-mem0.md)): its own full-context baseline beats the memory system on quality. |
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
- **Memory (added 2026-08-18; arc verdict same day):** what the extension buys over the
  native loop is confirmed as cross-harness continuity — the one thing a single harness
  cannot absorb — and the mechanism is real in source (ai-memory: one server,
  per-harness injection envelopes). Two qualifications keep it open: the *automatic*
  continuity floor is thin (ai-memory's baton is first + last prompt + tool names; the
  rich memory is pull-only), and absorption runs both ways — memos installs into hermes
  alongside hermes' own loop (conclusion 8's counter-current). The falsifiable residue
  is a rig question: capture a session, switch harness, measure what the second agent
  actually knows.
- ~~The memory-authorship fourth position~~ — resolved into design-principles
  (2026-08-18): independent storage *stacks* authorships rather than picking one; the
  sharpened question is who approves writes, not who makes them.
- Issue #13's `learning_loop` promotion trigger: **ai-memory verified in source
  (2026-08-18)** as the second harness-independent autonomous loop after ECC — mechanism
  `background` (server-side scheduler, default-on with a provider, auto-approving). The
  promotion trigger itself still hasn't fired: `background` now has four instances,
  `in-loop` and `manual` still one each.
