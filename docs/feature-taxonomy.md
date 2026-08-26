# The feature taxonomy

`created: 2026-08-18` · decision record: [ADR-0010](../adrs/0010-two-taxonomies.md)

This repo carries **two taxonomies**. The [tool taxonomy](tool-taxonomy.md) classifies
what a tool *is* (the categories, plus types like category 6's `type` and category 4's
poles). This file is the **feature taxonomy**: every characteristic we assess on tools,
defined **once**, with an applicability map saying which categories it can occur in. The
generator (`scripts/build-tool-index.py`) reads the YAML block below as its single
source of truth for valid frontmatter keys — the per-category (and per-type) matrices in
[`comparisons/features.md`](../comparisons/features.md) and its cross-category table
are derived from here plus report frontmatter. **Do not add a key anywhere else.**

The YAML block below is machine-read and renders on GitHub as a raw code block — for
*reading* the registry, use the generated
[`comparisons/feature-registry.md`](../comparisons/feature-registry.md) (added
2026-08-26), which re-renders it as linked tables. Same rule-3 relationship as every
matrix: this file is the editable source, that one is derived.

Conventions:

- A feature is a **presence-claim** verified in source or docs (omitted = not checked,
  `false` = checked and absent) — the same discipline as everywhere in this repo.
  Whether a present feature *pays* is a mechanism question (see each category's index).
- New keys follow **issue #2's two-verified-instances rule**: a key enters the
  registry only after the characteristic is verified in at least two tools.
- `block` names the frontmatter block that carries the key (`harness_features` for
  category 2 — renamed from the original bare `features` 2026-08-21, ADR-0018,
  `workflow_features` for category 4, `memory_features` for category-5 `type: memory` reports
  — ADR-0013, `model_features` for category 1 — ADR-0014, `environment_features` for
  category 3 — ADR-0017). `applies_to` lists tool-taxonomy categories; per-type blocks
  additionally scope by the report's `type`.
- The `environment_features` block's cells carry a grammar the other four blocks
  don't: evidence-grade suffixes inside the cell value, a `family:specific` colon tag
  on three of its eight keys, and lists that mean conjunction only — see
  [ADR-0017](../adrs/0017-environment-features-block.md) for the full grammar.
- **What belongs where** (the placement test, recorded 2026-08-19): a fact with an
  external ground truth we transcribe (stars, license, context window, pricing) is a
  **top-level frontmatter field** — mechanically collected, dated, and at most
  *rendered* into matrices as a column, never duplicated as a key. A capability we
  **assessed by reading**, comparable across tools under one definition, is a
  **registry key** and a cell (omitted = not checked, `false` = checked-absent — both
  claims). A finding, mechanism, or single-instance differentiator stays in **body
  prose** until issue #2's second instance lands. The load-bearing boundary is
  transcription vs assessment: the first drifts when the world changes, the second
  only when someone reads again. *Since 2026-08-26 the transcription half is
  enumerated too* — the `transcription_fields:` list in the YAML block below — so the
  whole assessment surface renders in one place and the generator can refuse an id
  that appears in both lists. An extension within ADR-0010's design, not a revision:
  the registry of assessed keys remains `features:`, and the enumeration adds no keys.
- `kind_link` records the **demand↔supply correspondence**: a harness feature (demand
  side) whose supply side is an installable artifact: the `memory` kind supplies from
  category 5 (Memory), every other kind from category 6 (Extensions) — the ADR-0020
  split. This is the bleed —
  quantified in the generated cross-category table.
- **`value_type` says what shape a cell's value takes** (added 2026-08-26, ADR-0032),
  on every entry in both lists and rendered as the registry's Type column. Nine values,
  and they are the repo's own vocabulary rather than generic types, because two
  distinctions were already load-bearing in prose and a generic set would erase them:
  `closed-enum` (one value from a closed set) is not `open-descriptive` (an open
  vocabulary with a required `family:specific` shape — the ADR-0017 distinction), and
  `graded` is ADR-0011's *ordered* enforcement scale, not merely an enum. The rest:
  `presence` (✓/✗), `list`, `free-text`, `string`, `number`, `date`, and `structured`.
  **`value_type` types the FACT, not the envelope** (ADR-0039): `structured` means
  SEVERAL facts share one cell (`pricing` carries input *and* output), never "this value
  has provenance" — every value here has provenance, and it lives where it always has, in
  the `#` comment beside the key and the report body. The one thing a comment cannot do is
  reach a generated matrix: `safe_load` drops comments, so a field whose *rendered* cell
  must carry prose — an absence needing its search scope, a qualifier that changes what a
  number means — writes that prose into the value and sets **`renders_note: true`**. Two
  fields qualify today (`pricing`, `knowledge_cutoff`) and the test is deliberately narrow:
  `context_window`, `stars`, and `released` all have caveats worth recording and none that
  the matrix must show, so they stay plain types with comments. A key that is
  scalar but accepts a list of named instances where naming them is informative
  (`rules_files`, `memory_store`) keeps its scalar type and says so in its definition —
  list-ness is a property of an instance, not a second type. Unknown values are a
  generator **error**, the same treatment `block` and `verification` already get.
- "Vocabulary" remains the mechanism phrase for this closed key list; the *concept* is
  the feature taxonomy (naming settled 2026-08-18, ADR-0010).

The registry itself lives in **[`feature-taxonomy.yaml`](feature-taxonomy.yaml)** — a real
YAML file since 2026-08-26 ([ADR-0036](../adrs/0036-feature-taxonomy-yaml-split.md)),
paired with this prose the way [`tool-taxonomy.yaml`](tool-taxonomy.yaml) is paired with
[`tool-taxonomy.md`](tool-taxonomy.md). Add or change a key there and re-run
`python3 scripts/build-tool-index.py`; the readable rendering is
[`comparisons/feature-registry.md`](../comparisons/feature-registry.md).
