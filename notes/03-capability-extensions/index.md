# Layer 3 — Capability extensions

`checked: 2026-07-28`

What the agent can **see and touch**. The layer test is independent distribution: authored,
versioned, and installed separately from any harness. See
[`../../taxonomy.md`](../../taxonomy.md).

## Kinds

| Kind | What it does | Portability |
|------|--------------|-------------|
| **MCP servers** | Expose external systems (filesystems, APIs, databases, browsers, SaaS) as tools over the Model Context Protocol. | High — one server works across Claude Code, Codex, Cursor, Copilot, Gemini CLI, OpenCode, Devin. |
| **Skills** | Packaged instructions loaded on demand for a class of task. | Currently Claude-Code-shaped; portable in principle, not yet in practice. |
| **Hooks** | Deterministic code the harness runs at lifecycle points (pre/post tool use, session start/stop). Not model-mediated — the harness executes them, so they *always* fire. | Harness-specific. |
| **Subagent definitions** | Named agents with their own prompt, tools, and model, spawned for isolated work. | Harness-specific format; the pattern is universal. |
| **Rules files** | `CLAUDE.md`, `AGENTS.md`, `.cursorrules` — standing instructions injected into context. | `AGENTS.md` is converging into a cross-harness convention. |

## Why this is a layer and not a pile of harness features

An MCP server is built once and consumed by every major harness. Nothing about it belongs
to a particular agent loop. The same is *aspirationally* true of skills and rules files —
tracking how far that aspiration gets is one of the more interesting things to watch here.

The counter-argument worth holding: hooks and subagent definitions are harness-specific
today, so this layer is only partly portable. If skills and rules converge on standards the
way MCP did, the layer solidifies; if they don't, part of it collapses back into layer 2.

## The distinction that matters

- **Layer 3 governs reach** — what the agent can access.
- **Layer 4 governs process** — what it does with that access.

A tool that adds a database connection is layer 3. A tool that says "write the spec before
you touch the database" is layer 4.

## Open questions

- Does MCP's portability actually hold up, or do servers quietly depend on one harness's
  tool-calling quirks?
- Hooks are the only deterministic escape hatch in an otherwise probabilistic system.
  How much of a workflow *should* be moved into them?
- Rules files are the cheapest context intervention and the least measured. What's the
  actual marginal value of a longer `CLAUDE.md`? (Candidate first experiment — see
  [`../cross-cutting/index.md`](../cross-cutting/index.md).)
