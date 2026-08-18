# Architecture decision records

`created: 2026-08-19`

One dated, immutable record per structural decision about this repo's taxonomy and
organization. The living documents ([`taxonomy.md`](../taxonomy.md),
[`design-principles.md`](../design-principles.md), the notes indexes) always speak the
**current** state with no inline history; how the current state was reached — and what
it superseded — lives here. When a dated document elsewhere (an experiment log, a
conclusion's original wording, git history, an old GitHub URL) seems to contradict the
living docs, the ADR trail is the decoder.

**Rules:**

- An ADR is written when a structural decision is made, and **never edited after
  acceptance** — except to set `superseded-by` when a later ADR overturns it.
- Each carries `decided:` (when the decision was made) and, for the initial backfill,
  `recorded: 2026-08-19 (backfill)` — ADRs 0001–0006 were extracted from revision
  records previously embedded in `taxonomy.md`; the extracted text is preserved
  as written, under its original date.
- Live falsifiers and re-check triggers stay in the living documents; ADRs record the
  narrative and evidence of the decision.
- This index table is hand-kept — a deliberate, documented exception to methodology
  rule 3: it is append-only and one line per ADR, the lowest-drift shape a hand-kept
  list can have.

| ADR | Decided | Decision | Status |
|---|---|---|---|
| [0001](0001-five-layer-taxonomy.md) | 2026-07-28 | Five-layer taxonomy: models, harnesses, extensions, frameworks, environments | superseded by 0007 (numbering) |
| [0002](0002-extensions-demoted-to-bucket.md) | 2026-07-30 | Extensions demoted from rung to cross-layer bucket | accepted |
| [0003](0003-environments-stay-a-rung.md) | 2026-08-16 | Execution environments stay a rung (adjudicated, reversed same day by E2B evidence) | accepted |
| [0004](0004-core-triad-reframing.md) | 2026-08-17 | Core-triad reframing; numbers kept as storage keys | storage-keys rule superseded by 0007 |
| [0005](0005-rename-to-extensions.md) | 2026-08-17 | Rename "portable artifacts" → "Extensions" | accepted |
| [0006](0006-layer-2-program.md) | 2026-08-18 | Framework code-outcome A/Bs stop; the layer-2 program | accepted |
| [0007](0007-renumber-core-triad-first.md) | 2026-08-19 | Renumber: core triad 1–3, frameworks 4, extensions 5 | accepted |
