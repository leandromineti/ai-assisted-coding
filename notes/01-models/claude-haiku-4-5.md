---
name: claude-haiku-4-5
layer: 1
vendor: Anthropic
url: https://platform.claude.com/docs/en/about-claude/models/overview
license: proprietary
open_source: false
model_id: claude-haiku-4-5-20251001
release_mode: api-only
context_window: 200000
max_output: 64000
pricing: "$1 / $5 per MTok (verified 2026-07-31)"
knowledge_cutoff: "Feb 2025 (reliable); training data Jul 2025"
checked: 2026-07-31
depth: stub
---

# Claude Haiku 4.5

Anthropic's small/fast tier: "the fastest model with near-frontier intelligence." The
only current Claude model still on a dated model ID (`-20251001`), the only one at
200k context, and the only one with legacy extended thinking instead of adaptive
thinking — a generation seam running visibly through the lineup.

## The layer-1 axes

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | · |
| Long-horizon coherence | · (its designed role — short mechanical subagent work — mostly sidesteps the axis) |
| Usable context (vs advertised) | 200k advertised; unprobed |
| Cost per completed task | 1/5 of Sonnet per token; the interesting question is retry rate — a cheap model that needs two attempts isn't 5× cheaper (cross-cutting cost note) |
| Release mode & access routes (1b) | API-only; four cloud routes |

## Role in this repo's work

None pinned. Notably, the tools *studied* here use it where this repo doesn't: **ECC's
instinct pipeline runs its background analysis on Haiku**
([`../03-capability-extensions/ecc.md`](../03-capability-extensions/ecc.md)), and
hermes routes auxiliary/compression work to cheap models of this class. The small tier's
real niche in mid-2026 practice appears to be *background cognition inside other
tools* — continuous, low-stakes, volume-priced — rather than interactive work.

## Surprises

1. **Feb 2025 knowledge cutoff** — seventeen months stale by now, in a lineup whose
   workhorse knows May 2026. For the background-cognition role that mostly doesn't
   matter; for anything touching current tooling it quietly does.

## Open questions

- The `learning_loop` machinery this repo now tracks (hermes, codex, ECC) all needs an
  always-on cheap model. Is the small tier's economics the actual enabler of the
  autonomous-memory pattern — i.e., is conclusion 8's absorption story downstream of
  Haiku-class pricing?
