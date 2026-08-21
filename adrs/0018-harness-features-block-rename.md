# ADR-0018 — The harness block renames: `features:` → `harness_features:`

`decided: 2026-08-21` · status: **accepted**

## Decision

The feature taxonomy's original block — the category-2 harness vocabulary carried in report
frontmatter as `features:` — renames to **`harness_features:`**. Purely a key rename: the 13
registry entries, their definitions, `kind_link`s, and every cell value are unchanged.

The rename is recorded as a third `schema_renames` entry in `taxonomy.yaml`
(`old: features, new: harness_features, status: applied, atomic: true`), enforced by the
existing LINT-05 unapplied-decoder check with **no new lint predicate** — LINT-05 is
generic over `schema_renames` entries and scans report frontmatter only. Three mechanical
lint-side literals do update in the same commit: the registry `known_blocks` set and the
LINT-04a block tuple in `check-taxonomy.py`, and two selftest fixtures whose synthetic
frontmatter carried the old block name.

## Why

Every block added after ADR-0010 took a `<category>_features` name: `model_features`
(ADR-0014), `workflow_features` (ADR-0010), `memory_features` (ADR-0013),
`environment_features` (ADR-0017). The original block kept the bare name `features` only
because it was first. That asymmetry has two costs beyond aesthetics:

- **The bare name states no scope.** A reader of a category-5 report's frontmatter (five
  memory reports carry the block, assessed on the harness vocabulary per the demand-side
  convention) cannot tell from `features:` *which* vocabulary the keys belong to; every
  other block name answers that in the key itself.
- **It collides with the registry's own top-level YAML key.** `feature-taxonomy.md`'s
  fenced registry block also begins `features:` (the list of all registry entries, all
  blocks) — two different meanings of the same token in the same file.

ADR-0010 deferred the *opposite* unification (folding `workflow_features:` into a shared
`features:` block); that deferral is now resolved by moving the other way — per-category
block names everywhere. ADR-0017's non-retrofit clause covered value *vocabularies* (the
colon-tag grammar), not block names, so no prior decision is contradicted.

## The decoder

| Old | New | Where |
|---|---|---|
| `features:` frontmatter block | `harness_features:` | 12 reports (7 category-2, 5 category-5 `type: memory`) + `notes/_template-tool-report.md` |
| `block: features` registry entries | `block: harness_features` | `notes/cross-cutting/feature-taxonomy.md` (13 entries) |
| `"features"` in `known_blocks` + `FEATURE_KEYS` filter + `r.get("features")` | `"harness_features"` / `HARNESS_FEATURE_KEYS` | `scripts/build-tool-index.py` |
| `"features"` in `known_blocks` + LINT-04a block tuple + two selftest fixtures | `"harness_features"` | `scripts/check-taxonomy.py` |

All three rows land in **one atomic commit** (ADR-0015 § Sequencing precedent: renaming
either side alone breaks the generator at import time).

**Unchanged, deliberately:**

- The registry's own top-level `features:` list key inside the fenced YAML block — it names
  "the registry entries", not the harness block, and lives in body text where LINT-05 never
  looks. Renaming it is a generator-internal concern with no report-facing surface.
- Historical ADRs (0010, 0012) that say `features:` — ADRs are immutable; this ADR is their
  decoder.
- The `kind_link` demand→supply mechanism and the cross-category table.

## Consequences

- Report frontmatter now answers "which vocabulary?" in the block name for all five blocks.
- Any surviving `features:` frontmatter key in notes/ fails `check-taxonomy.py --check` as
  an unapplied decoder (LINT-05, status `applied`).
- Older commits and external references to `features:` frontmatter decode through this ADR.
