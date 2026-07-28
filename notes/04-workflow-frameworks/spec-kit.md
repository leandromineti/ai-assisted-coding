---
name: spec-kit
layer: 4
sublayer: '-'
vendor: GitHub
url: https://github.com/github/spec-kit
license: MIT
open_source: true
stack: [Python]
version: v0.1.10-1039-g655a3cb
commit: 655a3cb
read_at: 2026-07-28
depth: stub
---

# spec-kit

GitHub's toolkit for **Spec-Driven Development**: specifications are written first and
treated as executable artifacts that generate the implementation, rather than documentation
that merely guides it. Intent before mechanism.

Workflow: `/speckit.constitution` (principles) → `/speckit.specify` (requirements) →
`/speckit.plan` (technical strategy) → `/speckit.tasks` (task list) → `/speckit.implement`.
Optional `/speckit.clarify`, `/speckit.analyze`, `/speckit.checklist`.

30+ agent integrations (`specify integration list`). Install: `uv tool install specify-cli`,
requiring Python 3.11+, git, and `uv`.

## The distinguishing bet

That agents fail from **under-specified intent**, not insufficient intelligence — so the
leverage is in forcing the "what" to be settled before the "how" begins. Compare GSD, which
shares the diagnosis but locates the failure in context management instead. Same disease,
different organ.

## Main features

_TODO_

## Stack & repo shape

Python — 284 `.py` across 521 tracked files, the second-smallest repo here. 135 `.md` files
are the command and template definitions, which is where a layer-4 tool's actual product
lives. Ships `presets/ARCHITECTURE.md` and `workflows/ARCHITECTURE.md`, plus 11 `.sh` and
10 `.ps1` — cross-platform shell scaffolding.

1603 commits since 2025-08-21 — the youngest and smallest history in the set.

## Architecture

_TODO — source unread. For a layer-4 tool the question isn't the agent loop (it has none);
it's how the methodology is encoded and how it targets 30+ harnesses from one definition._

## Bleed

Layer 3 — it installs slash commands and templates into whichever harness you point it at.
The `specify` CLI itself is a thin installer, not a harness.

## Cost model

Free and open source. Inference cost is whatever your harness charges.

## Surprises

_Source unread._

## Open questions

- How does one definition target 30+ harnesses? That mechanism *is* the layer-4 portability
  claim, and it's the most checkable thing in the repo.
- Where's the line between a `/speckit.*` command and an ordinary prompt template?
- Does the constitution step do real work, or is it ceremony that makes users feel invested?
