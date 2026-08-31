---
name: gemini-3-1-pro
category: 1
maker: Google
url: https://ai.google.dev/gemini-api/docs/models
license: proprietary
access: closed-source
model_id: gemini-3.1-pro (Preview)
release_date:
  date: 2026-02-19
  stage: Preview
  note: "API changelog: 'Released Gemini 3.1 Pro Preview'; no GA date or plan stated anywhere as of 2026-08-17 — six months in Preview and counting"
context_window: 1048576   # input token limit on the model page (verified 2026-08-17; resolves the 2026-07-31 gap)
max_output: 65536
pricing:
  input: 2          # USD per MTok — base list rate (see the registry's rule)
  output: 12
  currency: USD
  regime: context-tiered
  note: "$2 / $12 per MTok for prompts ≤200k tokens; $4 / $18 above 200k (verified 2026-08-17; batch and caching moved to their own keys)"
knowledge_cutoff:
  date: 2025-01          # the limit date on training data
  basis: inherited
  note: "January 2025 — inherited by explicit vendor delegation, read 2026-08-26 from both DeepMind model cards. Gemini-3-1-Pro-Model-Card.pdf (published February 2026) states no cutoff of its own, but its Model Data section reads 'Training Dataset: Gemini 3.1 Pro is based on Gemini 3 Pro. For more information about the training dataset for Gemini 3.1 Pro, see the Gemini 3 Pro model card' — and Gemini-3-Pro-Model-Card.pdf (Last Updated May 2026) states 'The knowledge cutoff date for Gemini 3 Pro was January 2025'. A cutoff is a property of the training dataset, and the vendor delegates 3.1 Pro's dataset to that card, so the figure carries. Caveat: the parent card separates pre- from post-training data and a cutoff describes the pre-training half, so a later post-training refresh would not surface here. Model page still has no cutoff row, only 'Latest update: February 2026'"
model_features:   # nested per ADR-0014 (2026-08-19); reasoning keys split per ADR-0040
  reasoning: true
  reasoning_type: always-on    # "thinking by default", cannot be fully disabled — OBSERVED 2026-08-31 (issue #42 probe): thoughtsTokenCount 87 on a three-word prompt, no thinking config sent
  reasoning_effort: "levels:low/medium/high@high"   # thinking_level IS the dial; legacy thinking_budget is mutually exclusive with it
  prompt_caching: "implicit on by default (4096-tok min) + explicit cache objects; cached input $0.20 (≤200k) / $0.40 (>200k) per MTok = 0.1x, storage $4.50 per MTok-hour, TTL settable, default 1h"
  batch_discount: "50% in+out at both size tiers ($1 / $6 ≤200k, $2 / $9 above); batch caching priced same as standard"
  fast_mode: true    # "Priority" service tier on the first-party pricing page: $3.60/$21.60 ≤200k, $7.20/$32.40 above (~1.8x standard); Flex is the slower-for-cheaper inverse (verified 2026-08-27); the tier is RESPONSE-OBSERVABLE — usageMetadata carries `serviceTier: "standard"` on a plain request (observed 2026-08-31), so a Priority purchase would be verifiable from the same field
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

## Reasoning surface

What the three reasoning cells rest on, verified 2026-08-17 (carried verbatim from the
free-text `thinking`/`effort_control` cells those keys replaced, ADR-0040): *"dynamic
('thinking by default'), cannot be fully disabled; `thinking_level` caps depth; legacy
`thinking_budget` mutually exclusive with it"* and *"`thinking_level`: low/medium/high,
default high — IS the effort surface, no separate param; 'minimal' exists only on Flash
lines."*

Google is the one vendor whose *dial* is thinking-named while everyone else's is
reasoning-named — and it carries both dial shapes at once, the level enum superseding a
legacy token budget that cannot be combined with it.

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
  source.~~ **Resolved 2026-08-26: January 2025, inherited.**
  [`Gemini-3-1-Pro-Model-Card.pdf`](https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-1-Pro-Model-Card.pdf)
  (published February 2026, 9 pp) contains no occurrence of "knowledge" or "cutoff" —
  it is a thin card that delegates most sections to
  [`Gemini-3-Pro-Model-Card.pdf`](https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf)
  (Last Updated May 2026), whose Known Limitations reads *"The knowledge cutoff date
  for Gemini 3 Pro was January 2025."*

  **The figure carries**, on a delegation of the underlying fact rather than of a
  section: the 3.1 card's Model Data section reads *"Training Dataset: Gemini 3.1 Pro
  is based on Gemini 3 Pro. For more information about the training dataset for
  Gemini 3.1 Pro, see the Gemini 3 Pro model card"* — the same "is based on" formula
  it uses for Training Data Processing, Hardware, and Software. A cutoff is a property
  of the training dataset; the vendor sends that dataset question to the parent card;
  the parent card answers January 2025.

  **The distinction worth keeping** (this was first recorded the other way on
  2026-08-26 and corrected the same day): a card delegating a *section* that happens to
  contain a model-scoped figure does not transfer that figure — which is why the Grok
  4.5 cutoff was retracted on 2026-08-17, with nothing linking 4.5's data to the 4.6
  page the number came from. A card delegating *the fact's own subject* does. Read the
  delegation, not the section heading.

  Both cards now have notes in the library —
  [`2026-gemini-3-1-pro`](../../references/cards/2026-gemini-3-1-pro.md) and
  [`2026-gemini-3-pro`](../../references/cards/2026-gemini-3-pro.md) — each carrying its
  quoted passages and the archive snapshot they can be re-checked against, since a card is
  rewritten in place (ADR-0034).

  Residual caveat: the parent card separates pre-training from post-training data and a
  cutoff describes the pre-training half, so a later post-training refresh would not
  surface here. A first-party page naming 3.1 Pro and a cutoff in one sentence would
  still be better evidence —
  [`deepmind.google/models/model-cards/gemini-3-1-pro/`](https://deepmind.google/models/model-cards/gemini-3-1-pro/)
  and whatever Google publishes at GA (still Preview at six months, per `release_date`).
