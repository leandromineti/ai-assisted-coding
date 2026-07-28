---
name: openspec
layer: 4
vendor: Fission AI
url: https://github.com/Fission-AI/OpenSpec
license: MIT
open_source: true
stack: [TypeScript, Node]
version: v1.6.0-88-g1637856
commit: 1637856
first_commit: 2025-08-05
stars: 62948
stars_at: 2026-07-28
read_at: 2026-07-28
depth: stub
---

# OpenSpec

Spec-driven development via **delta specs**: instead of documenting the whole system up
front (spec-kit's full artifact chain), you spec only *the change* — proposal, delta
specification, design, task list — and completed changes archive into a growing
source-of-truth spec that evolves alongside the code. The lean pole of the
"BMAD vs Spec Kit vs OpenSpec" trio that dominates the 2026 SDD conversation.

Targets multiple AI coding assistants ("for AI coding assistants" — integration breadth
unverified, source unread).

## The distinguishing bet

Same diagnosis as spec-kit — agents fail from under-specified intent — but the opposite
unit of specification: **the change, not the system**. Betting that up-front full specs
go stale and that a living spec should *accrete* from merged deltas. Within the layer-4
mechanism vocabulary, predicted profile *(prediction, not yet source-read)*:
intent-capture concentrated, bookkeeping minimal, process gates near zero, empirical
grounding absent.

## Main features

_TODO — source unread._

## Stack & repo shape

TypeScript — 311 `.ts` under 674 `.md` across 1,074 tracked files: majority-markdown
again, consistent with the layer-4 pattern (the methodology is the prose). 715 commits
since 2025-08-05. Visibly **dogfooded**: the repo's own `openspec/changes/` tree carries
live change dirs with `design.md` plus a dated `archive/` — the tool's history is written
in its own format.

## Architecture

_TODO — source unread. The two questions that matter: (1) what is the delta grammar, and
is the merge of archived deltas into the source-of-truth spec deterministic code or LLM
prose? (2) same portability question answered for spec-kit — compile-per-harness or a
shared directory convention?_

## Bleed

_Unverified. The `specify`-equivalent CLI (`openspec` npm package) looks like a thin
layer-3 installer, as with spec-kit — to confirm._

## Cost model

Free and open source (MIT). Cited in 2026 SDD roundups as one of the cheapest frameworks
to run (vs BMAD's heavy multi-agent spend) — consistent with the lean-delta design, but
that's third-party claim, not measurement.

## Surprises

_Source unread._

## Open questions

- Is the delta→source-of-truth merge deterministic or model-executed? That's the same
  "where does the runtime live" question that produced spec-kit's sharpest findings.
- Does the delta model dodge spec-kit's staleness problem or just relocate it (a pile of
  archived deltas is a history, not a spec — who compacts it, and how well)?
- 63k stars vs spec-kit's 124k: substitution or coexistence? Their bets are compatible —
  does anyone run both?
