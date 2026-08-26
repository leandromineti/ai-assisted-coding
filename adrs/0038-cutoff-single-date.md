# ADR-0038 — One cutoff date: the limit on training data

`decided: 2026-08-26` · status: **accepted**

## Decision

`knowledge_cutoff` keeps its mapping shape but carries **one date, not two**:

```yaml
knowledge_cutoff:
  date: 2025-07             # the limit date on training data — the outer bound
  basis: vendor-stated      # vendor-stated | inherited | not-stated | retracted
  note: "…"                 # required; carries any finer vendor figure
```

The `training_data` sub-key is gone and `knowledge` is renamed `date`, because the field
now has one meaning: **the outer bound of what the model was trained on**. Where a vendor
publishes a finer figure — Anthropic ships `reliableKnowledgeCutoff` beside
`trainingDataCutoff`, defining it as the date through which knowledge is *most extensive* —
the outer bound is what the field carries and the finer figure goes in `note`.

This supersedes ADR-0037's two-date clause, decided hours earlier the same day. Everything
else in 0037 stands: the mapping, `basis`, the null-when-not-stated constraint, and the
cell-value check.

## Why

Owner decision. Two dates in one cell asked every reader to know which one a comparison
meant, and only one vendor of eleven populated the second — so the column bought
ambiguity for nine rows and precision for one. A single well-defined bound sorts cleanly
and means the same thing in every row; the vendor's own finer distinction survives where
distinctions belong, in dated prose next to the source that made it.

## The one value that changed

**`claude-haiku-4-5`: 2025-02 → 2025-07.** It is the lineup's only model where the two
figures differ, and under the new definition the training-data limit is the one recorded.
Its note now says so explicitly — *"recorded here as the training-data limit (2025-07); the
vendor's finer 'reliable knowledge cutoff' is 2025-02"* — so a reader comparing against
yesterday's matrix sees a definition change, not a silent correction.

Every other row is unchanged: three Anthropic models publish both figures identically, and
the remaining seven publish at most one.

## Boundary

No decoder for paths; the field keeps its id and home. What is period: material dated
**2026-08-26 before this commit** may show `knowledge:` / `training_data:` sub-keys and
Haiku at 2025-02 under the earlier definition — ADR-0037 records that shape, and the two
ADRs read together are the decoder.

`check_cutoff` was narrowed to the single `date` key, keeping its constraints: format
`YYYY-MM(-DD)`, null exactly when `basis` is `not-stated` or `retracted`, `note` required.
