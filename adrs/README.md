# Architecture decision records

`created: 2026-08-18`

One dated, immutable record per structural decision about this repo's taxonomy and
organization. The living documents ([`tool-taxonomy.md`](../docs/tool-taxonomy.md),
[`design-principles.md`](../docs/design-principles.md), the notes indexes) always speak the
**current** state with no inline history; how the current state was reached — and what
it superseded — lives here. When a dated document elsewhere (an experiment log, a
conclusion's original wording, git history, an old GitHub URL) seems to contradict the
living docs, the ADR trail is the decoder.

**The standing decoders** (relocated here from the tool taxonomy's lead-in, 2026-08-22,
[ADR-0022](0022-refs-repo-voice-sweepable.md)): anything dated before **2026-08-18**
(git history, old URLs, experiment logs) uses the pre-renumbering scheme —
[ADR-0007](0007-renumber-core-triad-first.md) carries the mapping. Anything dated
before **2026-08-22** says "category 5" for both memory and the extensions bucket —
[ADR-0020](0020-memory-category-extensions-renumbered.md) carries that decoder
(memory → 5, everything else → 6). Anything dated before **2026-08-26** cites report
paths as `notes/0N-<name>/…` — [ADR-0024](0024-notes-to-tools-single-digit.md)
carries that mapping (`notes/` → `tools/`, `0N-` → `N-`), and the cross-cutting
notes cited at either old home live in `docs/` since the same day: `…/cross-cutting/<file>`
→ `docs/<file>` ([ADR-0025](0025-cross-cutting-becomes-docs.md)). Anything dated **on or
before 2026-08-26** also cites the constitution at root — `taxonomy.md`,
`methodology.md`, `design-principles.md`, `taxonomy.yaml` all map to `docs/<file>`,
unrenamed ([ADR-0026](0026-constitution-into-docs.md)) — and cites the hand-kept front
doors as `index.md`: `docs/index.md` and `tools/N-<name>/index.md` map to `README.md` in
the same directory ([ADR-0027](0027-index-front-doors-become-readme.md)); generated
`references/index.md` is unaffected. It also cites the numbered conclusions as living in
`README.md` — they moved to `docs/conclusions.md` the same day, **numbers unchanged**, so
"conclusion N" still resolves ([ADR-0028](0028-conclusions-out-of-readme.md)). Finally, it
calls the tool taxonomy `taxonomy.md` / `taxonomy.yaml`, at either home: both gained a
`tool-` prefix on 2026-08-26 to pair with `feature-taxonomy.md`, so they are
`docs/tool-taxonomy.md` and `docs/tool-taxonomy.yaml`
([ADR-0030](0030-tool-taxonomy-prefix.md)). And it cites source notes as `refs/<key>.md`:
the library was renamed and split the same day, so those map to
`references/papers/<key>.md` — bare `refs/` to `references/`
([ADR-0034](0034-references-papers-and-cards.md)). Anything dated before **2026-08-26**
also names the category-1 reasoning cells `thinking:` and `effort_control:`:
[ADR-0040](0040-reasoning-replaces-thinking.md) carries that decoder — `thinking` split
into `reasoning` (does it reason at all) **and** `reasoning_type` (toggleability), while
`effort_control` became `reasoning_effort` in `family:specific` form. Not a pure rename in
either direction, so an old cell's prose does not map onto one new cell; each report's
**§ Reasoning surface** carries the original wording with its check date.

**Rules:**

- An ADR is written when a structural decision is made, and **never edited after
  acceptance** — except to set `superseded-by` when a later ADR overturns it.
- Each carries `decided:` (when the decision was made) and, for the initial backfill,
  `recorded: 2026-08-18 (backfill)` — ADRs 0001–0006 were extracted from revision
  records previously embedded in the tool taxonomy; the extracted text is preserved
  as written, under its original date.
- Live falsifiers and re-check triggers stay in the living documents; ADRs record the
  narrative and evidence of the decision.
- **Dating correction (2026-08-18):** the session that wrote ADRs 0007–0008, the
  backfill stamps, and the memory-kind seeds ran with a clock one day ahead and
  stamped everything `2026-08-19`; all its work was actually committed 2026-08-18 UTC
  (verified against git timestamps and an external clock). The wrong date was swept
  to 2026-08-18 across the repo the same day — a mechanical correction of a clock
  error, not a decision revision. ADR-0007's decoder boundary was reworded to name
  the renumber commit rather than a calendar date, since correct same-day material
  now exists on both sides of it.
- This index table is hand-kept — a deliberate, documented exception to methodology
  rule 3: it is append-only and one line per ADR, the lowest-drift shape a hand-kept
  list can have.

| ADR | Decided | Decision | Status |
|---|---|---|---|
| [0001](0001-five-layer-taxonomy.md) | 2026-07-28 | Five-layer taxonomy: models, harnesses, extensions, frameworks, environments | superseded by 0007 (numbering) + 0020 (split) |
| [0002](0002-extensions-demoted-to-bucket.md) | 2026-07-30 | Extensions demoted from rung to cross-layer bucket | accepted |
| [0003](0003-environments-stay-a-rung.md) | 2026-08-16 | Execution environments stay a rung (adjudicated, reversed same day by E2B evidence) | accepted |
| [0004](0004-core-triad-reframing.md) | 2026-08-17 | Core-triad reframing; numbers kept as storage keys | storage-keys rule superseded by 0007 |
| [0005](0005-rename-to-extensions.md) | 2026-08-17 | Rename "portable artifacts" → "Extensions" | accepted |
| [0006](0006-layer-2-program.md) | 2026-08-18 | Framework code-outcome A/Bs stop; the layer-2 program | accepted |
| [0007](0007-renumber-core-triad-first.md) | 2026-08-18 | Renumber: core triad 1–3, frameworks 4, extensions 5 | accepted |
| [0008](0008-standards-into-cross-cutting.md) | 2026-08-18 | Standards folded into cross-cutting (one non-layer bucket) | accepted |
| [0009](0009-candidates-ledger.md) | 2026-08-18 | Candidates ledger: one pre-report rung, cross-layer (`tools/candidates.md`) | append-mostly clause superseded by 0031 |
| [0010](0010-two-taxonomies.md) | 2026-08-18 | Two taxonomies: tool taxonomy + feature taxonomy (registry, cross-layer view) | accepted |
| [0011](0011-graded-gate-enforcement.md) | 2026-08-18 | Graded enforcement values (engine/hook/script/prose) for the gate features | accepted |
| [0012](0012-layer-2-feature-set.md) | 2026-08-18 | Layer-2 feature set: `ptc` + graded `turn_end_gates` | accepted |
| [0013](0013-memory-features-block.md) | 2026-08-19 | Third registry block: `memory_features` for layer-5 memory tools | accepted |
| [0014](0014-model-features-into-registry.md) | 2026-08-19 | Model API-feature keys fold into the registry (`model_features` block) | accepted |
| [0015](0015-layers-become-categories.md) | 2026-08-19 | Layers become categories: canonical top-level term rename, encoded in `taxonomy.yaml` | accepted |
| [0016](0016-extensions-stay-broad.md) | 2026-08-19 | Extensions stay broad: memory is a type, not the category (narrowing considered, rejected as arc-sample bias) | superseded by 0020 |
| [0017](0017-environment-features-block.md) | 2026-08-20 | Fifth registry block: `environment_features` for category-3 environments | accepted |
| [0018](0018-harness-features-block-rename.md) | 2026-08-21 | The harness block renames: `features:` → `harness_features:` (schema_renames decoder) | accepted |
| [0019](0019-category-5-coverage-strata.md) | 2026-08-22 | Coverage strata for category 5: mechanism / content / reach inside the unchanged seven-type bucket | superseded in part by 0020 |
| [0020](0020-memory-category-extensions-renumbered.md) | 2026-08-22 | Memory becomes category 5; Extensions becomes category 6 (owner decision, supersedes 0016 and part of 0019) | accepted |
| [0021](0021-harness-three-component-decomposition.md) | 2026-08-22 | Harness decomposition: three components (loop, context assembly, permission gate) + two descriptive axes | accepted |
| [0022](0022-refs-repo-voice-sweepable.md) | 2026-08-22 | Repo-voice prose in `refs/` is sweepable (quotes stay period); decoders relocate to this index | accepted |
| [0023](0023-category-4-5-components.md) | 2026-08-25 | Components for categories 4 (four functions + substrate finding) and 5 (capture · consolidation · recall); tracing discipline category-generic | accepted |
| [0024](0024-notes-to-tools-single-digit.md) | 2026-08-26 | Path rename: `notes/` → `tools/`, category dirs `0N-` → `N-` (storage-path decision; decoder above) | accepted |
| [0025](0025-cross-cutting-becomes-docs.md) | 2026-08-26 | Cross-cutting notes move to root as `docs/`, chartered for repo-structure/methodology/idea notes; concept name unchanged | placement clause superseded by 0026 |
| [0026](0026-constitution-into-docs.md) | 2026-08-26 | The constitution (`taxonomy.md`, `methodology.md`, `design-principles.md`, `taxonomy.yaml`) moves root → `docs/`; `docs/` rechartered in two halves | accepted |
| [0027](0027-index-front-doors-become-readme.md) | 2026-08-26 | Hand-kept front doors are `README.md` (seven renamed); `index.md` means a generated listing (`refs/index.md`) | accepted |
| [0028](0028-conclusions-out-of-readme.md) | 2026-08-26 | Conclusions move to `docs/conclusions.md`; README keeps the headline index, numbers unchanged | accepted |
| [0029](0029-category-6-keeps-its-name.md) | 2026-08-26 | "Extensions" stays the name of category 6 (rename to "Stranger Things" declined); the residual-pull strain recorded in §6 instead | accepted |
| [0030](0030-tool-taxonomy-prefix.md) | 2026-08-26 | `taxonomy.md` / `taxonomy.yaml` gain a `tool-` prefix to pair with `feature-taxonomy.md`; the lint keeps its name | accepted |
| [0031](0031-candidates-ledger-is-a-backlog.md) | 2026-08-26 | The candidates ledger is a backlog: promotion removes the row (supersedes 0009's append-mostly clause); six promoted rows removed | accepted |
| [0032](0032-value-type-column.md) | 2026-08-26 | `value_type` on every registry entry (9 values, repo vocabulary not generic types), rendered as the Type column; unknown values are a generator error | accepted |
| [0033](0033-pricing-structured.md) | 2026-08-26 | `pricing` becomes a mapping (numeric core + regime + verbatim note); tenth `value_type` `structured`; first cell-value check | accepted |
| [0034](0034-references-papers-and-cards.md) | 2026-08-26 | `refs/` → `references/`, split into `papers/` + `cards/`; card notes carry a required archive `snapshot` | accepted |
| [0035](0035-generated-sqlite-export.md) | 2026-08-26 | Generated SQLite export (`comparisons/repo.db`, gitignored) for querying; frontmatter stays authoritative | accepted |
| [0036](0036-feature-taxonomy-yaml-split.md) | 2026-08-26 | The feature registry becomes `docs/feature-taxonomy.yaml`, pairing with its prose like `tool-taxonomy.{md,yaml}` | accepted |
| [0037](0037-knowledge-cutoff-structured.md) | 2026-08-26 | `knowledge_cutoff` becomes a mapping: two dates + `basis` (vendor-stated \| inherited \| not-stated \| retracted); third cell-value check | two-date clause superseded by 0038 |
| [0038](0038-cutoff-single-date.md) | 2026-08-26 | One cutoff date, meaning the training-data limit; the finer vendor figure moves to `note` | accepted |
| [0039](0039-value-type-types-the-fact.md) | 2026-08-26 | `value_type` types the fact: `knowledge_cutoff` is `date`; `structured` means plural facts; `renders_note` marks matrix-visible prose | accepted |
| [0040](0040-reasoning-replaces-thinking.md) | 2026-08-26 | `thinking` + `effort_control` → `reasoning` (presence) + `reasoning_type` (toggleability enum) + `reasoning_effort` (`family:specific` dial); repo voice says *reasoning*, vendor words stay quoted; fourth cell-value check | accepted |
