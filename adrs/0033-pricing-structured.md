# ADR-0033 — `pricing` becomes structured: a numeric core with the prose preserved

`decided: 2026-08-26` · status: **accepted**

## Decision

The `pricing` transcription field stops being a string and becomes a mapping:

```yaml
pricing:
  input: 5                 # USD per MTok
  output: 25
  currency: USD
  regime: flat             # flat | context-tiered | time-of-day | variant-priced | route-dependent
  note: "…"                # required unless regime is flat
```

**The base-rate rule** — the thing that makes the numbers comparable, and therefore the
load-bearing part of this decision: `input`/`output` are the list rate for a **small,
standard, non-batch, uncached request on the vendor's first-party USD surface, for the
model this report is about**. Sol's `$5/$30`, not its Terra/Luna siblings. DeepSeek's peak
rate. Qwen's smallest tier. Grok's and Gemini's sub-200k tier. Kimi's USD list, not the
separate CNY one.

`regime` names why the base is not the whole story and carries **one** value even where two
apply — `gpt-5-6-sol` is both context-tiered and variant-priced; the second regime lives in
`note` rather than making `regime` list-valued, because a matrix column sorts on one thing.

`value_type` gains a tenth token, **`structured`**, extending ADR-0032's vocabulary (not
superseding it): a mapping whose sub-schema its own entry's definition states.

## Why

`comparisons/models.md` renders `pricing` raw, so the pricing column of a *comparison*
matrix was a paragraph per row — unsortable, unchartable, uncomparable at a glance.

A plain number was the obvious fix and is wrong: **only 4 of 11 model reports have a flat
rate.** The rest carry context tiers with two different semantics (Grok's ≥200k re-rates
the *whole* request; Sol's >272k input is 2x in / 1.5x out), time-of-day pricing (DeepSeek
halves off-peak on stated UTC windows, effective 2026-08-16 16:00), variant-priced families
inside one report, route and currency dependence (Kimi's USD and CNY lists are "two price
lists, not one converted"), and a retired promo that August ledgers still depend on
(Sonnet's cancelled September increase). A single number would have deleted all of it.

So the core is extracted, the prose is kept verbatim, and `regime` marks the gap between
them. Every one of the 11 `note` values was verified byte-identical to the string it
replaced — a dated claim that changes wording during a mechanical migration is the failure
mode this migration was most exposed to.

## The first cell-value check

ADR-0032 closed by naming its own follow-on: types were declarative, and validating actual
*cells* was deferred. `check_pricing()` in `scripts/build-tool-index.py` is the first
instance — it reads report frontmatter, not the registry, and exits non-zero on a
non-mapping value, a non-positive or non-numeric `input`/`output`, a missing `currency`, an
unknown `regime`, or a missing `note` on a non-flat regime. It runs under both a plain run
and `--check`: a malformed price must not render, because it renders as something that
*looks* like a number.

Verified by three negative tests, each restored afterwards: unknown regime → exit 1 naming
the five legal values; missing note on `context-tiered` → exit 1; `input: "$2"` → exit 1.

## What was deliberately not done

`prompt_caching` and `batch_discount` stay `free-text`. Their content resists a numeric
core — read/write multipliers against several TTLs, storage fees per MTok-hour,
minimum-token thresholds, "Unsupported for this model", peak/off-peak cache rates, batch
APIs that exclude the very model the report is about — and the repo already split them into
their own keys deliberately (`gemini-3-1-pro`'s old pricing string says so: "batch and
caching moved to their own keys"). Several rows would carry a null core and lean entirely
on prose, which is what `free-text` already means.

One rendering consequence accepted rather than papered over: on flat rows the note repeats
the numbers ("**$1 / $5** per MTok — $1 / $5 per MTok (verified 2026-08-17)"). Trimming a
dated claim inside a renderer is worse than mild repetition, so the note stays verbatim.

## Boundary

No decoder: `pricing` keeps its id, its home, and its meaning; only its shape changed.
Material dated on or before 2026-08-26 quotes pricing as a single string — that string is
now the `note`, unchanged. `tools/1-models/_template-model-report.md` carries the new shape
with the base-rate rule inline, so the next model report starts correct.
