# ADR-0002 — Extensions demoted from rung to cross-layer bucket

`decided: 2026-07-30` · `recorded: 2026-08-19 (backfill — text extracted verbatim from
taxonomy.md §3 as of commit fd9f189)` · status: **accepted** (numbering of the bucket
later changed by [ADR-0007](0007-renumber-core-triad-first.md))

## Decision

The extensions category ("layer 3" under the numbering of the time) is a **cross-layer
bucket, not a rung**: the core stack is models, harnesses, and workflow frameworks,
plus execution environments (kept on its own surviving falsifier); the former layer 3
becomes the cross-layer bucket.

## Record (extracted from taxonomy.md, as written)

> **Revision executed — "three core layers + bucket" (recorded and gated 2026-07-30 am;
> trigger (a) fired same day at the ECC deep-dive).** The challenge, raised after the
> hermes/codex deep-dives: layer 3's *mechanisms* were always layer-2 features (every
> harness ships its own MCP client, skills loader, hooks runtime), and the deep-dives
> showed the *write path* absorbed too (autonomous learning loops author the
> memory/skill artifacts — README conclusion 8). Trigger (a) required the ECC read to
> find **no process spine** (confirmed: opt-in catalog, orchestration outsourced to an
> external runtime) **and portability reducing to file conventions** (confirmed for the
> portable bundle: copy-with-adaptation into per-harness convention dirs; even its
> background observer daemon is installed as files and launched through each harness's
> own hook system).
>
> *Countervailing evidence, recorded at execution rather than buried:* the same read
> showed the artifact ecosystem is product-grade — ECC is a 236k-star business built
> entirely on independently distributed capability artifacts, and its instinct
> import/export design points at a *new* exchangeable artifact class. If instinct-like
> formats standardize across vendors (the ~2027-01 standards re-check remains
> scheduled), the bucket may deserve re-promotion to a layer — the door swings both
> ways, and that re-check is now the recorded trigger for the reverse revision.

The reasoning that survives from the layer era: the *runtimes* (MCP clients, skills
loaders, hook engines) were always harness features, the *write paths* are being
absorbed into the harness (README conclusion 8), and what remains genuinely
independent is **artifacts distributed on file conventions** — content plus specs,
which is a bucket's shape, not a rung's.

## Consequences

The bucket kept its number as a storage key at the time ("renumbering would break
every dated cross-reference in the repo for zero information gain") — a rule later
formalized in [ADR-0004](0004-core-triad-reframing.md) and superseded by
[ADR-0007](0007-renumber-core-triad-first.md). The re-promotion trigger (instinct-like
formats standardizing, ~2027-01 re-check) remains live in the taxonomy.
