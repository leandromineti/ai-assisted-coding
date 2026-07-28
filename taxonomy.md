# A taxonomy of AI-assisted-coding tooling

`checked: 2026-07-28`

The point of this document is a **shared vocabulary**. Without one, "Claude Code vs. GSD
vs. Opus 5" is a category error — three things that aren't the same kind of thing at all.
Every note and comparison in this repo declares which layer its subject occupies, so that
comparisons stay like-for-like.

## The stack

### 1. Models

The weights themselves. The foundation everything else sits on.

Judged for *this* field on: tool-call fidelity, long-horizon coherence (staying on task
across hundreds of steps — the property that separates an agentic model from a good chat
model), usable context, cost per **completed task** rather than per token, and release
mode (API-only vs. open weights).

#### 1b. Model access

How you actually reach the weights: first-party APIs, aggregators/routers, cloud
marketplaces, and local runtimes. A sub-layer rather than a peer layer, but it earns
mention because it silently explains a lot of "why did it get worse" — prompt-caching
support, quantization, rate limits, and context truncation all differ by route while the
model name stays the same.

### 2. Harnesses

The program that runs the agent loop. Concretely: **loop + context assembly + permission
model + UI**.

Sub-divided by surface, because the affordances genuinely differ:

- **Terminal** — Claude Code, Codex CLI, OpenCode, Aider, Grok Build
- **IDE-embedded** — Cursor, Windsurf, Cline, Continue, Copilot
- **Async / cloud** — Devin, Jules, cloud Codex, Claude Code on web

As of mid-2026 this is the most contested layer, and the consensus reason is worth
recording: the frontier models have converged enough that the harness now decides most of
the day-to-day experience.

### 3. Capability extensions

What the agent can **see and touch**. MCP servers, tools, skills, hooks, subagent
definitions, and rules files (`CLAUDE.md`, `AGENTS.md`).

The layer test is **independent distribution**: an MCP server is authored, versioned, and
installed separately from any harness, and the same one works across Claude Code, Codex,
Cursor, Copilot, Gemini CLI, OpenCode, and Devin. That portability is what makes this a
layer rather than a bag of harness features.

Distinct from layer 4: capability extensions govern **what the agent can reach**;
workflow frameworks govern **what process it follows**.

### 4. Workflow frameworks

An encoded **methodology** — spec-first, phased planning, on-disk artifacts, review gates
— that rides on top of a harness.

The analogy: if the harness is the runtime, this is the framework. Node is to Next.js as
Claude Code is to GSD.

The layer test is **harness portability by design**: both GSD and spec-kit target many
harnesses from one definition. A tool that only makes sense inside one harness's loop is
probably that harness's feature, not a framework.

### 5. Execution environments

Where the agent's code actually runs, and what it can damage: git worktrees,
devcontainers, Docker, remote sandboxes (E2B, Modal, Cloudflare Sandbox SDK), cloud VMs.

Easy to overlook until it bites. Isolation that hides the files the agent needs is a
layer-5 problem routinely misread as a layer-2 bug — the worktree/gitignore trap written
up in [`notes/05-execution-environments/`](notes/05-execution-environments/index.md) is
the case that convinced me this layer is real.

## Cross-cutting concerns

These are **not layers**. They appear at several layers at once, and forcing them onto the
ladder distorts them. Each gets a note of its own.

- **Context engineering** — lives in the harness (layer 2), the rules files (layer 3), and
  the workflow framework (layer 4) simultaneously. Probably the highest-leverage topic in
  the repo.
- **Verification & evaluation** — tests, CI gates, review bots, agent-run observability,
  benchmarks. The least-explored area of the field, and the one that decides whether any
  of the rest is actually working.
- **Cost & economics** — per-token price is the least interesting form of this. Cost per
  completed task, cost of a failed run, and cost of review time all matter more.

## Standards

The stress test below surfaced a category that isn't a layer at all: **standards**. MCP,
the `AGENTS.md` convention, and the emerging agent-permission conventions are
specifications, not installable things. A standard is recorded here, once, and referenced
from the layers that implement it — never given a layer entry of its own.

- **MCP (Model Context Protocol)** — the protocol is a standard; the *servers* that speak
  it are layer 3.
- **`AGENTS.md` / `CLAUDE.md`** — rules-file conventions; the files are layer 3 artifacts.
- **Agent-permission conventions** — emerging; nothing confirmed as a named standard.

Written up in [`notes/standards/`](notes/standards/index.md), which also tracks the
question this category exists to answer: whether skills and hooks standardize the way MCP
did, or stay vendor features — which decides whether layer 3 is a real layer.

## The boundary rule

**The layers are analytic, not physical.** Real products bundle across them constantly:

- Claude Code ships skills and hooks (layer 3) and plan mode (layer 4) inside the harness.
- GSD is distributed *as* Claude Code skills, but also ships `gsd-pi`, its own CLI — so it
  reaches down into layer 2.
- Devin bundles its own sandbox (layer 5) with its harness (layer 2).

So every entry records a **primary layer** plus an explicit **bleed** note. The bleed is
signal, not noise: it's how you watch layers consolidate. The clearest current example is
xAI/SpaceX's $60B acquisition of Anysphere (Cursor), announced 2026-06-16 — a layer-1
vendor buying a layer-2 product, then training Grok 4.5 on that harness's session data.
Vertical integration across layers 1 and 2 is the live structural story of 2026.

## Stress test

Five deliberately hard cases, classified. If a new case has no defensible home, the
taxonomy needs revision — not the case.

| Case | Verdict | Reasoning |
|------|---------|-----------|
| **Cursor's agent mode** | Layer 2, IDE-embedded | The IDE is the UI; the agent loop underneath is a harness. "IDE feature" describes the surface, not the kind. Now bleeds into layer 1 via xAI ownership. |
| **Claude Code Skills** | Layer 3, bundled in layer 2 | Independently authored, versioned, and portable in principle — that's the layer-3 test. Shipping inside a harness is distribution, not identity. |
| **Devin** | Layer 2, bundles layer 5 | A harness that happens to ship its own sandbox. You can't adopt one without the other, but bundling ≠ layer identity. |
| **Aider** | Layer 2, opinionated | It *has* a methodology (commit per change, repo map), but you can't install that methodology on top of a different harness. Not portable → harness with strong defaults, not a framework. |
| **MCP itself** | Not a layer — a standard | Forced the "Standards" section above. The protocol is a spec; its servers are layer 3. |

## Deliberate exclusions

- **Agent SDKs** (Claude Agent SDK, LangGraph, Mastra, PydanticAI) — a different consumer:
  you're *building* an agent rather than *using* one. Excluded for now, not dismissed;
  revisit if the repo's scope widens.
- **Human practices** — task decomposition, when to restart context, review discipline.
  Real and important, but they're techniques rather than tooling; they belong in
  `notes/cross-cutting/`.

## Layer indexes

| Layer | Index |
|-------|-------|
| 1 · Models | [`notes/01-models/index.md`](notes/01-models/index.md) |
| 2 · Harnesses | [`notes/02-harnesses/index.md`](notes/02-harnesses/index.md) |
| 3 · Capability extensions | [`notes/03-capability-extensions/index.md`](notes/03-capability-extensions/index.md) |
| 4 · Workflow frameworks | [`notes/04-workflow-frameworks/index.md`](notes/04-workflow-frameworks/index.md) |
| 5 · Execution environments | [`notes/05-execution-environments/index.md`](notes/05-execution-environments/index.md) |
| ✕ Cross-cutting | [`notes/cross-cutting/index.md`](notes/cross-cutting/index.md) |
| ✕ Standards | [`notes/standards/index.md`](notes/standards/index.md) |

Per-tool entries use [`notes/_template.md`](notes/_template.md).
