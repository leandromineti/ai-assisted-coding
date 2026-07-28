# Layer 3 — Capability extensions

`checked: 2026-07-28`

What the agent can **see and touch**. The layer test is independent distribution: authored,
versioned, and installed separately from any harness. See
[`../../taxonomy.md`](../../taxonomy.md).

This index covers the **installable things**. The specifications they implement — MCP the
protocol, the `AGENTS.md` convention — are not layer entries; they live in
[`../standards/`](../standards/index.md).

## Kinds

| Kind | What it does | Portability |
|------|--------------|-------------|
| **MCP servers** | Expose external systems (filesystems, APIs, databases, browsers, SaaS) as tools over the Model Context Protocol. | High — one server works across Claude Code, Codex, Cursor, Copilot, Gemini CLI, OpenCode, Devin. |
| **Skills** | Packaged instructions loaded on demand for a class of task. | Currently Claude-Code-shaped; portable in principle, not yet in practice. |
| **Hooks** | Deterministic code the harness runs at lifecycle points (pre/post tool use, session start/stop). Not model-mediated — the harness executes them, so they *always* fire. | Harness-specific. |
| **Subagent definitions** | Named agents with their own prompt, tools, and model, spawned for isolated work. | Harness-specific format; the pattern is universal. |
| **Rules files** | `CLAUDE.md`, `AGENTS.md`, `.cursorrules` — standing instructions injected into context. | Convention-level only — see [standards](../standards/index.md). |

## Why this is a layer and not a pile of harness features

An MCP server is built once and consumed by every major harness. Nothing about it belongs
to a particular agent loop. The same is *aspirationally* true of skills and rules files.

The counter-argument worth holding: hooks and subagent definitions are harness-specific
today, so this layer is only partly portable — arguably it's "MCP plus a pile of vendor
features" wearing a layer's clothes. Whether that resolves depends on standards adoption,
which is tracked in [`../standards/`](../standards/index.md) rather than here.

## The distinction that matters

- **Layer 3 governs reach** — what the agent can access.
- **Layer 4 governs process** — what it does with that access.

A tool that adds a database connection is layer 3. A tool that says "write the spec before
you touch the database" is layer 4.

## Open questions

*Questions about the specifications themselves live in
[`../standards/`](../standards/index.md). These are about the installable artifacts.*

- Hooks are the only deterministic escape hatch in an otherwise probabilistic system —
  the harness executes them, so they always fire. How much of a workflow *should* be moved
  into them, and what's lost when you do?
- Subagent definitions isolate context, but each spawn pays a cold-start cost in tokens and
  re-derived understanding. When does isolation actually beat a single longer context?
- Skills load on demand rather than up front. Does just-in-time loading measurably beat a
  fat rules file, or does it just move the same tokens around?
- Is there a real difference between a skill and a well-written section of a rules file,
  other than *when* it enters the context?
