# ADR-0025 — `tools/cross-cutting/` moves to root as `docs/`

`decided: 2026-08-26` · status: **accepted**

## Decision

The cross-cutting directory leaves the reports tree and becomes a root-level
**`docs/`**, chartered as the home for general notes about the repository's
structure, methodology, and ideas — anything that belongs to no single category.
Its founding contents are the six cross-category notes unchanged
(`index.md`, `benchmark-survey.md`, `category-2-program.md`,
`feature-taxonomy.md`, `metrics.md`, `standards.md`). The constitution stays at
root (`methodology.md`, `taxonomy.md`, `design-principles.md`); `docs/` holds the
notes *around* it, not the rules themselves.

"Cross-cutting" survives as the **concept name** for the category-spanning notes
(ADR-0008's bucket; prose saying "the cross-cutting verification note" stays
correct) — what changed is only where the files live.

## Why

Owner request (2026-08-26), one day after ADR-0024 renamed `notes/` → `tools/`:
that rename made the mismatch visible — a directory named for *tool reports* was
hosting the feature registry, the metrics vocabulary, and the benchmark survey,
none of which is a tool report. Lint-scope check before moving: the two
report-scoped gates in `check-taxonomy.py` key on `tools/` paths and never applied
to these files (no report frontmatter), and deny-list linting walks every
non-exempt `.md` regardless of directory — so the move changes no lint coverage.

## The decoder

Anything dated before **2026-08-26** cites `notes/cross-cutting/<file>` or (for a
few hours on 2026-08-26) `tools/cross-cutting/<file>`; both map to `docs/<file>`,
files unrenamed. Chains with ADR-0024's decoder for pre-2026-08-26 material.

## Boundary

Same as ADR-0024: living docs, scripts (`FEATURE_REGISTRY_PATH` in both the
generator and the lint), `taxonomy.yaml` `known_sites`, and generated matrices
rewritten/regenerated; ADR bodies and experiment protocols keep their period paths
and read under the decoder.
