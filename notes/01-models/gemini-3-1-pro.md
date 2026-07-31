---
name: gemini-3-1-pro
layer: 1
vendor: Google
url: https://ai.google.dev/gemini-api/docs/models
license: proprietary
open_source: false
model_id: gemini-3.1-pro (Preview)
release_mode: api-only
context_window: unverified   # not stated on the pages checked; the 200k pricing-tier boundary implies a window well beyond it, but implying is not verifying
max_output: unverified
pricing: "$2 / $12 per MTok for prompts ≤200k tokens; $4 / $18 above 200k; batch half-price; caching $0.20–$0.40 (verified 2026-07-31)"
knowledge_cutoff: unverified
checked: 2026-07-31
depth: stub
---

# Gemini 3.1 Pro

Google's big-model line for "advanced intelligence, complex problem-solving, and
powerful agentic and vibe coding capabilities" — and, as of this check, still marked
**Preview** while four Flash-line models (3.6 Flash, 3.5 Flash, 3.5 Flash-Lite, 3.1
Flash-Lite) are Stable. The lineup's shape is the finding: Google's *stable* tier is
the fast/cheap line; the flagship Pro trails it in release status.

## The layer-1 axes

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | · |
| Long-horizon coherence | · |
| Usable context (vs advertised) | Advertised window **not found on the checked pages** — a gap worth flagging given the seed inventory called this the "hold the whole monorepo" option. That framing is currently unsourced; the 200k pricing boundary is the only window-related primary fact captured |
| Cost per completed task | Tiered pricing doubles input cost above 200k prompt tokens — long-context work is priced super-linearly, which directly taxes the "whole monorepo in context" use case the model is marketed for |
| Release mode & access routes (1b) | API-only (Gemini API + Vertex); free tier exists on Flash lines, not Pro |

## Role in this repo's work

None. Appears in the layer-2 shelf only through Gemini CLI (whose Antigravity
transition deferred its own read) and the stale Terminal-Bench snapshot.

## Surprises

1. **The flagship is in Preview while the budget line is Stable** — inverted from
   every other vendor in this sweep.
2. **Long-context pricing works against the long-context pitch:** 2× input above
   200k. Every vendor with 1M-class windows now tiers at ~200k (Google, xAI) — the
   marginal price of the marquee feature is the emerging pattern to watch.

## Open questions

- What is the actual advertised context window, from a primary source? (The models
  page omits it; resolve before any long-context claim about this model is repeated.)
- Does "Preview" gate anything material (SLAs, caching, rate limits) for agent use?
