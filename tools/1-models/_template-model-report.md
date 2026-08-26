---
name: <model-slug>
category: 1
maker: <who trains it>
url: <primary docs / model card URL — the page the facts below were verified against>
license: proprietary            # or the weights license (Apache-2.0, MIT, Kimi K3's modified MIT…)
access: <open-weights | closed-source>   # open-weights only once the weights are actually published; `open-source` is reserved for a model whose TRAINING SOURCE is public (none read yet). Terms live in `license:` above
model_id: <exact API model ID / HF repo id>
release_mode: api-only          # api-only | open-weights | both
released: "<lifecycle: date + stage in the vendor's OWN vocabulary — 'GA YYYY-MM-DD, no preview stage' / 'Preview since YYYY-MM-DD, no GA date' / 'weights YYYY-MM-DD, first-party API YYYY-MM-DD'. Stages don't align across vendors, so the stage word is part of the fact (replaced ga_date 2026-08-17)>"
context_window: <tokens>
max_output: <tokens>
pricing:                 # structured since ADR-0033 — numbers comparable, prose preserved
  input: <n>             # USD per MTok, BASE rate: a small, standard, non-batch, uncached
  output: <n>            # request on the vendor's first-party USD surface, for THIS model
  currency: USD
  regime: <flat | context-tiered | time-of-day | variant-priced | route-dependent>
  # Everything the two numbers can't hold — tiers and their boundaries, off-peak windows,
  # sibling variants, non-USD lists, retired promos — goes here, dated. Required unless
  # regime is `flat`.
  note: "<$in / $out per MTok, with any time-limited or tiered pricing dated>"
knowledge_cutoff: <vendor-stated>
# API-feature keys (2026-08-17) — set ONLY when verified against `url`-linked vendor
# docs on the `checked` date; omitted = not checked (models matrix renders ·).
model_features:   # nested per ADR-0014 (2026-08-19)
  # The three reasoning keys are typed (ADR-0040, 2026-08-26). Repo voice says
  # "reasoning"; the vendor's own word (thinking.type, budget_tokens, "K3 always
  # thinks") is quoted verbatim in the body, never translated.
  reasoning: <true | false — generates reasoning tokens at all; true even if always-on>
  reasoning_type: <always-on | default-on | opt-in | none — TOGGLEABILITY, not who sizes it>
  # The depth dial, `family:specific`. The family says who sizes the reasoning:
  # `levels:<set>@<default>` (model spends against a level) | `budget:<unit>`
  # (caller allocates up front) | `none`. The default after `@` is required.
  reasoning_effort: <levels:low/high/max@high | budget:tokens | none>
  prompt_caching: "<write/read economics + TTLs, in the vendor's own terms>"
  batch_discount: "<async batch pricing, if offered>"
checked: <YYYY-MM-DD — the date every spec above was verified against `url`>
depth: <stub | survey>
---

# <Model>

> **The category-1 depth mapping** (documented once here; the shared vocabulary is reused so
> the generated index stays comparable): **stub** = specs verified against the vendor
> page, model not used · **survey** = used on real work in this repo's orbit, with the
> evidence named. *Corrected 2026-08-17:* a third grade (deep-dive = "this repo's
> experiments produced measured data") predated methodology rule 1a and contradicted
> it — closure caps a report at `survey`; measured behavior is OBSERVED-grade
> evidence and goes in the axis cells, not the depth field.
>
> Every spec in the frontmatter carries the `checked` date and must come from `url`,
> not from memory (methodology rule 1). Prices and context windows drift; a model
> report with a stale `checked` is a rumor.

## What it is

One paragraph. The vendor's positioning in one clause, then what it's actually for in
this repo's terms.

## The category-1 axes (taxonomy §1)

Judged on the five axes the taxonomy names — fill only what there's evidence for,
mark the rest `·` (not-yet-checked):

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | |
| Long-horizon coherence | |
| Usable context (vs advertised) | |
| Cost per completed task | |
| Release mode & access routes (1b) | |

## Role in this repo's work

Where this model actually appears in the study: experiments that pinned it, machine
rules that route to it, harness defaults that ship it. This section is the *evidence*
for a `survey`/`deep-dive` rating — if it's empty, the rating is `stub`.

## Surprises

What contradicted expectations. Empty + `stub` is honest; empty + `survey` means you
used it and learned nothing, which is worth saying explicitly.

## Open questions

-
