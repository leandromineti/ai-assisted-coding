---
name: gemini-3-1-pro
category: 1
vendor: Google
url: https://ai.google.dev/gemini-api/docs/models
license: proprietary
open_source: false
model_id: gemini-3.1-pro (Preview)
release_mode: api-only
released: "Preview since 2026-02-19 (API changelog: 'Released Gemini 3.1 Pro Preview'); no GA date or plan stated anywhere as of 2026-08-17 — six months in Preview and counting"
context_window: 1048576   # input token limit on the model page (verified 2026-08-17; resolves the 2026-07-31 gap)
max_output: 65536
pricing: "$2 / $12 per MTok for prompts ≤200k tokens; $4 / $18 above 200k (verified 2026-08-17; batch and caching moved to their own keys)"
knowledge_cutoff: "unverified — model page has no cutoff row, only 'Latest update: February 2026'; the DeepMind model card may carry it (unchecked, off first-party API docs)"
model_features:   # nested per ADR-0014 (2026-08-19); values unchanged
  thinking: "dynamic ('thinking by default'), cannot be fully disabled; thinking_level caps depth; legacy thinking_budget mutually exclusive with it"
  effort_control: "thinking_level: low/medium/high, default high — IS the effort surface, no separate param; 'minimal' exists only on Flash lines"
  prompt_caching: "implicit on by default (4096-tok min) + explicit cache objects; cached input $0.20 (≤200k) / $0.40 (>200k) per MTok = 0.1x, storage $4.50 per MTok-hour, TTL settable, default 1h"
  batch_discount: "50% in+out at both size tiers ($1 / $6 ≤200k, $2 / $9 above); batch caching priced same as standard"
checked: 2026-08-17
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
| Usable context (vs advertised) | 1,048,576-token input limit, 65,536 output, from the model page (resolved 2026-08-17 — the 2026-07-31 check found no window on the overview page; the per-model page carries it). Usable-vs-advertised unprobed |
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

- ~~What is the actual advertised context window, from a primary source?~~ Resolved
  2026-08-17: 1,048,576 in / 65,536 out on the per-model page (the overview table
  omits it — the gap was real, just one page deep).
- Does "Preview" gate anything material (SLAs, caching, rate limits) for agent use?
- Knowledge cutoff is still unverified: the model page's spec table has no cutoff row
  (only "Latest update: February 2026"). The DeepMind model card is the likely primary
  source; it lives outside the API docs surface this stub was checked against.
