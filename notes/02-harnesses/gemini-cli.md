---
name: gemini-cli
layer: 2
surfaces: [terminal]
execution: local
vendor: Google
url: https://github.com/google-gemini/gemini-cli
license: Apache-2.0
open_source: true
stack: [TypeScript, Node, Ink]
version: v0.49.0-preview.0-49-gbef611950
commit: bef611950
first_commit: 2025-04-15
stars: 106225
stars_at: 2026-07-28
read_at: 2026-07-28   # drift-checked 2026-08-16 (rule 4b) — see the drift-check section; pin deliberately not moved
depth: stub
---

# Gemini CLI

Google's vendor-native terminal harness. Positioned around long context — the "hold the
whole monorepo" option in the mid-2026 comparisons.

Transitioning to **Antigravity CLI**; the individual free tier (1000 requests/day) ended
2026-06-18.

## Drift check — 2026-08-16 (not a re-read; the pin is unchanged)

22 commits / 84 files, and **nothing to falsify** — the honest verdict for a stub, which
asserts almost nothing beyond repo shape. Repo-shape numbers barely moved (`.tsx` 418 →
418, `.ts` 1726 → 1729, tracked 2933 → 2963), so the stack description still holds. One
commit in the drift mentions Antigravity, consistent with the transition noted above but
not evidence about its state.

The `_TODO_` sections are the real status here: a stub can't go stale because it never
claimed anything. That is a reason to be relaxed about stub drift in general — and a
reminder that this report's value is currently the *external* fact (the free tier ending
2026-06-18), which drifts on Google's schedule rather than the repo's and is not checkable
from a clone at all.

## The distinguishing bet

_TODO_ — nominally that a large enough context window makes retrieval strategy irrelevant.
If true, its context assembly should be markedly simpler than its peers'. That's a testable
prediction against the source.

## Main features

_TODO_

## Stack & repo shape

TypeScript on Node ≥20, with **Ink** for the terminal UI — which explains the 418 `.tsx`
files in a CLI: they're React components rendering to a terminal. 1726 `.ts` across 2933
tracked files. Packages split `cli/` from `core/`, plus an `a2a-server/`.

6321 commits since 2025-04-15.

## Architecture

_TODO — source unread._

## Bleed

_TODO_ — supports MCP (layer 5).

## Cost model

Metered via Gemini API. The free individual tier is gone as of 2026-06-18.

## Surprises

_Source unread._

## Open questions

- Does the `cli`/`core` split make the core reusable as a library, or is it organizational?
- What does `a2a-server` do — agent-to-agent coordination?
- Does the long-context bet actually show up as simpler context assembly, or do they still
  do retrieval anyway?
