---
name: gsd-core
layer: 4
vendor: Open GSD
url: https://github.com/open-gsd/gsd-core
license: MIT
open_source: true
stack: [Markdown, Node]
version: v1.8.0-102-gd04592de
commit: d04592de
read_at: 2026-07-28
depth: stub
---

# GSD — gsd-core

An *operating loop* for agentic engineering work; its stated enemy is context bloat and
scope drift. Three principles: explicit plans as **structured task graphs**, **clean
execution contexts** per unit of work, and **real verification** producing human-readable
evidence.

Installs into Claude Code, Codex, Gemini CLI, Cursor, Windsurf, and Copilot. Ships
alongside `gsd-pi` (standalone CLI), `gsd-browser` (deterministic Chrome control), and
announced-but-unshipped `gsd-workbench` and `gsd-cloud`.

**Already installed on this machine**, so source claims can be cross-checked against
observed behavior — the only tool in the set where that's possible.

## The distinguishing bet

That agents fail from **context mismanagement**, not insufficient intelligence — so the
leverage is in giving each unit of work a clean, right-sized context and verifying the
result with evidence. Compare spec-kit, which shares the diagnosis but locates the failure
in under-specified intent.

## Main features

_TODO_

## Stack & repo shape

**Majority markdown: 1398 `.md` against 810 `.cjs`** across 2636 tracked files. This is the
single most informative fact in the bootstrap pass — a layer-4 framework is mostly *prose*,
because the methodology is the product and the code is delivery machinery. Runtime is
CommonJS Node (`.cjs` plus 177 `.cts`).

`docs/ARCHITECTURE.md` exists, and is translated into ja-JP, ko-KR, and pt-BR — a
localization investment nothing else in the set makes.

4788 commits since **2025-12-14** — barely seven months old, the youngest project here by
first-commit date, at roughly 680 commits/month.

## Architecture

_TODO — source unread. `docs/ARCHITECTURE.md` is the way in. The interesting question for a
prose-dominant tool is how the markdown is structured, versioned, and targeted at multiple
harnesses._

## Bleed

Reaches **down into layer 2** via `gsd-pi`, its own standalone CLI, and into **layer 3** via
`gsd-browser`. Documented in [`index.md`](index.md) — it's the clearest case in the repo of a
workflow framework growing into the runtime it was meant to sit on top of.

## Cost model

Free and open source (MIT). Inference cost is whatever your harness charges — though the
structured-task-graph approach implies more model calls per unit of work, which is a cost
question worth measuring.

## Surprises

**The markdown-to-code ratio.** 1398 `.md` vs 810 `.cjs` is close to a proof of the layer-4
definition: if the artifact is mostly prose, the thing being distributed really is a
methodology rather than a program. Recorded before reading a line of source.

## Open questions

- How is 1398 markdown files' worth of methodology kept coherent? Is there a schema, or is
  it convention?
- Does the ceremony pay below some task size, and where's that threshold?
- 680 commits/month on a seven-month-old project — what's churning?
- Does `gsd-pi` behave identically to gsd-in-Claude-Code, or does the host harness dominate?
