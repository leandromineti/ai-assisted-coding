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
pricing:
  input: 2          # USD per MTok — base list rate (see the registry's rule)
  output: 12
  currency: USD
  regime: context-tiered
  note: "$2 / $12 per MTok for prompts ≤200k tokens; $4 / $18 above 200k (verified 2026-08-17; batch and caching moved to their own keys)"
knowledge_cutoff: "not stated for 3.1 Pro — the DeepMind model card was read 2026-08-26 (Gemini-3-1-Pro-Model-Card.pdf, published February 2026, 9 pp) and contains no cutoff sentence at all: its Known Limitations section says 'For more information about the known limitations for Gemini 3.1 Pro, see the Gemini 3 Pro model card.' THAT card (Gemini-3-Pro-Model-Card.pdf, Last Updated May 2026) states 'The knowledge cutoff date for Gemini 3 Pro was January 2025' — scoped by name to Gemini 3 Pro, which the same card lists as a DIFFERENT model from 3.1 Pro ('each subsequent model in the Gemini 3 Pro family is based on Gemini 3 Pro (see each model card for individual model details)'). Recorded as the family parent's figure, NOT adopted for 3.1 Pro — same discipline as the Grok 4.5/4.6 retraction. Model page still has no cutoff row, only 'Latest update: February 2026'"
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

## The category-1 axes

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | · |
| Long-horizon coherence | · |
| Usable context (vs advertised) | 1,048,576-token input limit, 65,536 output, from the model page (resolved 2026-08-17 — the 2026-07-31 check found no window on the overview page; the per-model page carries it). Usable-vs-advertised unprobed |
| Cost per completed task | Tiered pricing doubles input cost above 200k prompt tokens — long-context work is priced super-linearly, which directly taxes the "whole monorepo in context" use case the model is marketed for |
| Release mode & access routes (1b) | API-only (Gemini API + Vertex); free tier exists on Flash lines, not Pro |

## Role in this repo's work

None. Appears in the category-2 shelf only through Gemini CLI (whose Antigravity
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
- ~~Knowledge cutoff is still unverified; the DeepMind model card is the likely primary
  source.~~ **Checked 2026-08-26 — the card exists and is silent.**
  [`Gemini-3-1-Pro-Model-Card.pdf`](https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-1-Pro-Model-Card.pdf)
  (published February 2026, 9 pp) contains no occurrence of "knowledge" or "cutoff":
  four of its sections — Known Limitations, Acceptable Usage, Evaluation Approach,
  Safety Policies — are one line each, delegating to
  [`Gemini-3-Pro-Model-Card.pdf`](https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf)
  (Last Updated May 2026), whose Known Limitations reads *"The knowledge cutoff date
  for Gemini 3 Pro was January 2025."*

  **That figure is not adopted here**, and the reason is a distinction the parent card
  draws itself: *"Gemini 3 Pro is not a modification or a fine-tune of a prior model.
  Each subsequent model in the Gemini 3 Pro family is based on Gemini 3 Pro (see each
  model card for individual model details)"* — with Gemini 3.1 Pro named in that
  family list, carrying its own card. So the delegation makes January 2025 *arguable*
  for 3.1 Pro and vendor-stated for neither. The repo already paid for this exact
  inference once: the Grok 4.5 cutoff was retracted 2026-08-17 after the recorded
  "Feb 1, 2026" turned out to be documented for Grok 4.6.

  What would settle it: a first-party page naming 3.1 Pro and a cutoff in the same
  sentence. The card's own landing page —
  [`deepmind.google/models/model-cards/gemini-3-1-pro/`](https://deepmind.google/models/model-cards/gemini-3-1-pro/)
  — and whatever Google publishes at GA (still Preview at six months, per `released`)
  are the two candidates left.
