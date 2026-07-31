---
name: <model-slug>
layer: 1
vendor: <who trains it>
url: <primary docs / model card URL — the page the facts below were verified against>
license: proprietary            # or the weights license (Apache-2.0, MIT, Kimi K3's modified MIT…)
open_source: false              # true only for released weights
model_id: <exact API model ID / HF repo id>
release_mode: api-only          # api-only | open-weights | both
ga_date: <YYYY-MM-DD if disclosed>
context_window: <tokens>
max_output: <tokens>
pricing: "<$in / $out per MTok, with any time-limited pricing dated>"
knowledge_cutoff: <vendor-stated>
checked: <YYYY-MM-DD — the date every spec above was verified against `url`>
depth: <stub | survey | deep-dive>
---

# <Model>

> **Layer-1 depth mapping** (documented once here; the shared vocabulary is reused so
> the generated index stays comparable): **stub** = specs verified against the vendor
> page, model not used · **survey** = used on real work in this repo's orbit, with the
> evidence named · **deep-dive** = this repo's own experiments produced *measured* data
> on it (rig runs, preregistered A/Bs). Closed weights have no source to trace, so the
> tool template's "loop traced" bar is replaced by "measured here" — same honesty
> gradient, different instrument.
>
> Every spec in the frontmatter carries the `checked` date and must come from `url`,
> not from memory (methodology rule 1). Prices and context windows drift; a model
> report with a stale `checked` is a rumor.

## What it is

One paragraph. The vendor's positioning in one clause, then what it's actually for in
this repo's terms.

## The layer-1 axes (taxonomy §1)

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
