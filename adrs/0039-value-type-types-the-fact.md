# ADR-0039 — `value_type` types the fact, not the envelope

`decided: 2026-08-26` · status: **accepted**

## Decision

`knowledge_cutoff` is typed **`date`**, not `structured`. Its cell is still written as a
mapping (`date` + `basis` + `note`) and the data is unchanged — what changes is what the
registry claims about it.

Two rules, both narrowing:

1. **`structured` means SEVERAL facts share one cell**, and nothing else. `pricing`
   qualifies (input *and* output, neither derivable from the other). A single fact wearing
   extra keys does not.
2. **A cell writes prose into its value only when the *generated matrix* must carry that
   prose**, and says so with **`renders_note: true`**. Two fields qualify today.

## Why

Raised by the owner as a labelling complaint — why does the registry say `structured` when
the fact is a date? — and then sharpened into the argument that settles it: *every* feature
statement has a basis, so if provenance justified wrapping, every one of the 67 entries
would become `structured` and the Type column would carry no information at all.

That is correct, and it exposes the real reason the two wrapped fields are wrapped. It is
not provenance. **This repo already has a provenance system that lives outside the value** —
the `#` comment beside the key (`turn_end_gates: engine  # session/turn.rs, confirmed at
the branch site`), the report's `checked:` date, `depth:`, and the omitted-vs-`false`
convention. Rebuilding that inside every cell would duplicate it 67 times.

The one thing a comment cannot do is reach a generated view: `yaml.safe_load` drops
comments before any matrix is rendered. `knowledge_cutoff` has **five of eleven models with
no date at all**, and a matrix cell reading `—` with no explanation is precisely the
not-checked-vs-checked-absent ambiguity this repo works hardest against. `pricing` has
`regime`, without which `$2 / $6` misstates Grok's price above 200k tokens. Both notes are
in the value for a *rendering* reason, and that reason generalizes to almost nothing else:
`context_window`, `stars`, `released`, and `version` all carry caveats worth recording and
none the matrix must show.

## Consequences

The Type column now reads `` `date` + note `` and `` `structured` + note ``, so a reader
sees what sorts and that prose travels with it. The `VALUE_TYPES` comment in
`build-tool-index.py` and the vocabulary bullet in `feature-taxonomy.md` both carry the
narrowed meaning and the wrapper test, so the next structured-looking field meets the rule
before it is minted.

No data changed: the eleven `knowledge_cutoff` mappings and their notes are untouched, and
`check_cutoff` still enforces the same constraints. ADR-0033's `structured` token and
ADR-0037/0038's cell shape stand; this narrows what the token *claims*.

Deliberately not done, and now clearly separable: moving `PRICING_REGIMES` and
`CUTOFF_BASIS` out of Python into the registry (ADR-0032's deferred permitted-values half).
That is a sub-schema question, not a typing one, and this decision does not depend on it.
