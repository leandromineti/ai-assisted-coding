# ai-assisted-coding

A personal sandbox for understanding the AI-assisted-coding tooling landscape — from
first-hand trial rather than from marketing pages.

This is a learning repo. The deliverable is notes and conclusions, not a product.

## Start here

**[`taxonomy.md`](taxonomy.md)** — the shared vocabulary. Five stack layers plus
cross-cutting concerns, with a boundary rule for the many tools that straddle them.
Everything else in the repo declares which layer it belongs to.

| Layer | Index | Examples |
|-------|-------|----------|
| 1 · Models | [`notes/01-models/`](notes/01-models/index.md) | Opus 5, Fable 5, Grok 4.5, Kimi K3 |
| 2 · Harnesses | [`notes/02-harnesses/`](notes/02-harnesses/index.md) | Claude Code, OpenCode, Codex CLI, Cursor |
| 3 · Capability extensions | [`notes/03-capability-extensions/`](notes/03-capability-extensions/index.md) | MCP servers, skills, hooks, rules files |
| 4 · Workflow frameworks | [`notes/04-workflow-frameworks/`](notes/04-workflow-frameworks/index.md) | GSD, spec-kit |
| 5 · Execution environments | [`notes/05-execution-environments/`](notes/05-execution-environments/index.md) | worktrees, devcontainers, E2B |
| ✕ Cross-cutting | [`notes/cross-cutting/`](notes/cross-cutting/index.md) | context engineering, verification, cost |
| ✕ Standards | [`notes/standards/`](notes/standards/index.md) | MCP, `AGENTS.md` convention |

## Layout

| Path | Holds |
|------|-------|
| `taxonomy.md` | The layer definitions and boundary rule — the canonical reference |
| `notes/` | One index per layer, plus one file per tool, written while using it |
| `upstream/` | Cloned open-source sources to read — **gitignored**, see [`upstream/README.md`](upstream/README.md) |
| `experiments/` | Small self-contained trials — ideally the *same* task, different tools |
| `comparisons/` | Side-by-side matrices distilled from the notes and experiments |
| `scripts/` | `sync-upstream.sh` (clone/update), `repo-facts.sh` (verified frontmatter facts), `build-tool-index.py` (regenerate the index) |

**[`comparisons/tools.md`](comparisons/tools.md)** is the flat cross-layer index of every
tool with a report, and **[`comparisons/features.md`](comparisons/features.md)** the
harness feature matrix — both generated from the reports' frontmatter, never hand-edited,
so they can't drift from them. In the matrix, `·` means *not yet checked*, which is
deliberately distinct from ✗ *verified absent*.

One report per tool, following
[`notes/_template-tool-report.md`](notes/_template-tool-report.md). Its **"distinguishing
bet"** field is the one that matters — what does this tool believe that its competitors
don't? — and **`depth`** is the honesty marker: `stub` (facts collected, source unread),
`survey` (used or skimmed), `deep-dive` (agent loop and context assembly actually traced).

The point of reusing one task across `experiments/` is to make comparisons honest instead
of impressionistic — though see the open question in
[`notes/cross-cutting/`](notes/cross-cutting/index.md) about whether a clean A/B is
possible here at all.

## Conventions

- Every claim about a tool carries a `checked: YYYY-MM-DD` date. This field moves fast and
  notes go stale quietly.
- Anything not confirmed against a primary source is marked `unverified` rather than
  asserted.
- A tool that hasn't actually been used gets an **empty** "my take" section. The blankness
  is the honest state.

## Conclusions

_(Kept here as they firm up — the running answer to "what did I actually learn?")_
