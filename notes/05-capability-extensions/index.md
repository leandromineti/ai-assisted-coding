# 5 — Extensions & protocols (cross-layer bucket)

> Renamed from "Portable artifacts" 2026-08-17: portability is not an intrinsic
> property of an extension but a status the ecosystem confers by adoption — unevenly
> across the kinds below (see the Standards scoreboard and the dated rename note in
> [`../../taxonomy.md`](../../taxonomy.md) §3).

`checked: 2026-07-30`

What the agent can **see and touch**, as distributable content. **A bucket, not a layer,
since the 2026-07-30 taxonomy revision** (three core layers; trigger fired at the ECC
deep-dive — see the executed-revision note in [`../../taxonomy.md`](../../taxonomy.md)).
The membership test is unchanged: independent distribution — authored, versioned, and
installed separately from any harness. The "3" is a storage key.

This index covers the **installable things**. The specifications they implement — MCP the
protocol, the `AGENTS.md` convention — are not layer entries; they live in
[`../standards/`](../cross-cutting/standards.md).

## Kinds

| Kind | What it does | Portability |
|------|--------------|-------------|
| **MCP servers** | Expose external systems (filesystems, APIs, databases, browsers, SaaS) as tools over the Model Context Protocol. | High — one server works across Claude Code, Codex, Cursor, Copilot, Gemini CLI, OpenCode, Devin. |
| **Skills** | Packaged instructions loaded on demand for a class of task. | Converging (2026-07-28): `SKILL.md` consumed by ≥4 harnesses per spec-kit's integration registry — convention-level, like rules files. See [standards](../cross-cutting/standards.md). |
| **Hooks** | Deterministic code the harness runs at lifecycle points (pre/post tool use, session start/stop). Not model-mediated — the harness executes them, so they *always* fire. | Harness-specific. |
| **Subagent definitions** | Named agents with their own prompt, tools, and model, spawned for isolated work. | Harness-specific format; the pattern is universal. |
| **Rules files** | `CLAUDE.md`, `AGENTS.md`, `.cursorrules` — standing instructions injected into context. | Convention-level only — see [standards](../cross-cutting/standards.md). |

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
