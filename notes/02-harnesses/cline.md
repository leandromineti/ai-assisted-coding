---
name: cline
layer: 2
surfaces: [ide, terminal]   # started as a VS Code extension; the tree carries apps/cli/
execution: local
vendor: Cline
url: https://github.com/cline/cline
license: Apache-2.0
open_source: true
stack: [TypeScript, React]
version: nightly-main-20260728125218-dc175c73a8dd
commit: dc175c73a
read_at: 2026-07-28
depth: stub
---

# Cline

Open-source IDE-embedded harness, originally a VS Code extension, bring-your-own-model.

## The distinguishing bet

_TODO_ — nominally that the harness should be **model-agnostic**, against the vendor-native
harnesses (Claude Code, Codex, Gemini CLI) betting that tight model coupling wins.

## Main features

_TODO_

## Stack & repo shape

TypeScript with React — 1977 `.ts` and 597 `.tsx` across 3429 tracked files. Notably no
longer just an extension: the tree carries `apps/cli/`, `apps/cline-hub/`, an `sdk/`, and
`evals/`. It ships **three separate `ARCHITECTURE.md` files** (`sdk/`, `evals/`, and a
desktop sidecar), which is more architectural self-documentation than anything else in the
set.

6667 commits since 2024-07-05.

## Architecture

_TODO — source unread. Start from `sdk/ARCHITECTURE.md`, which is the rare case of a repo
explaining itself._

## Bleed

_TODO_ — supports MCP (layer 3). The `evals/` directory is a cross-cutting verification
concern living inside a layer-2 product, which is worth documenting.

## Cost model

Open source; metered inference against whichever provider you configure.

## Surprises

_Source unread — but a harness shipping its own `evals/` suite is already notable given how
under-served verification is across the field._

## Open questions

- What does `evals/` actually measure, and could that method be borrowed for this repo's
  own verification problem?
- An extension that grew a CLI, an SDK, a hub, and a desktop sidecar — is that convergence
  on a platform, or scope creep?
