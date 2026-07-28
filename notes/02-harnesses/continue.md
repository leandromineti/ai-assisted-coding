---
name: continue
layer: 2
sublayer: ide
vendor: Continue
url: https://github.com/continuedev/continue
license: Apache-2.0
open_source: true
stack: [TypeScript, React]
version: v1.3.40-vscode-11-g5522c6f44
commit: 5522c6f44
read_at: 2026-07-28
depth: stub
---

# Continue

Open-source IDE-embedded harness for VS Code and JetBrains, bring-your-own-model.

## The distinguishing bet

_TODO_ — nominally **portability across IDEs**, which no other tool in the set attempts.
Cline is VS-Code-shaped; Continue maintains a JetBrains extension alongside it, which forces
a genuine core/host separation.

## Main features

_TODO_

## Stack & repo shape

TypeScript with React — 1429 `.ts`, 345 `.tsx` across 3058 tracked files. The tree splits
`extensions/vscode/` from `extensions/intellij/` over a shared core, plus a `binary/` package
with per-platform builds (darwin/linux, arm64/x64), implying a compiled sidecar process that
both IDEs talk to.

**21569 commits since 2023-05-23** — the most commits and second-oldest project in the set.

## Architecture

_TODO — source unread. The core/host boundary is the interesting part: it's the only place
in this set where a harness had to abstract its own UI._

## Bleed

_TODO_ — supports MCP (layer 3). The `binary/` sidecar is arguably a layer-5 concern
(process isolation) solved incidentally.

## Cost model

Open source; metered inference against whichever provider you configure.

## Surprises

_Source unread._

## Open questions

- What exactly lives in the shared core vs. the per-IDE extension? That boundary is the
  clearest available evidence of what a harness *is*, minus its UI.
- Why a compiled binary sidecar rather than running in-process?
- 21.5k commits and it's still a layer-2 tool — where did that volume go?
