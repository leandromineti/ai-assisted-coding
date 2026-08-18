# ADR-0007 — Renumber the layers: core triad first

`decided: 2026-08-19` · status: **accepted** · supersedes the storage-keys rule of
[ADR-0004](0004-core-triad-reframing.md) (and ADR-0001's original ordering)

## Decision

The layer numbers now follow the conceptual frame instead of the historical accretion
order. The core triad is 1–3; the two interfaces are 4–5:

| # | Category | Previously |
|---|---|---|
| 1 | Models | 1 (unchanged) |
| 2 | Harnesses | 2 (unchanged) |
| 3 | **Execution environments** | **5** |
| 4 | Workflow frameworks | 4 (unchanged) |
| 5 | **Extensions (bucket)** | **3** |

A clean 3 ↔ 5 swap. Directories (`notes/03-execution-environments/`,
`notes/05-capability-extensions/`), `layer:` frontmatter, `upstream/repos.txt`, the
generator's layer tables, and all living prose move together in one commit.

## Context

ADR-0004's reframing made model+harness+environment the three fundamentals but kept the
numbers as storage keys, twice-justified as "renumbering breaks dated cross-references
for zero information gain." Two things changed that calculus:

1. **The repo went public (2026-08-18).** For new readers the mismatch between the
   conceptual order (triad first) and the storage order (environments last) is a
   standing confusion in the repo's front-door document — no longer zero information
   gain.
2. **This `adrs/` folder now exists.** The original cost — dated cross-references
   breaking silently — is paid differently: living documents always speak the current
   taxonomy, and anything dated earlier is decoded here rather than by inline
   disclaimers scattered through living text. The owner chose this structure
   explicitly (2026-08-19) over per-mention annotations.

## The decoder

Any material dated **before 2026-08-19** — git history, experiment protocols and logs
(immutable by methodology rule 5), published article snapshots, old GitHub URLs, issue
threads — uses the old scheme: **3 = extensions, 5 = execution environments**.
Everything at or after this date, and every living document at HEAD, uses the new
scheme. Design-principles' letter-coded principle IDs (H*, X*, F*, E*) are
number-free and unaffected; `notes/cross-cutting/layer-2-program.md` refers to the
harness layer, whose number did not change.

## Consequences

- Old public GitHub URLs into `notes/03-capability-extensions/` and
  `notes/05-execution-environments/` return 404; the renamed twins exist at the
  swapped numbers. Accepted cost, noted at decision time (the repo had been public
  for one day).
- README conclusions 3 and 9, whose original wording used the old numbers, were
  reworded to category names / current numbers under their "revisable by charter"
  status; their original wording is preserved in git history and decoded by this ADR.
- Issue #11 was retitled from its "Layer-5" prefix; the thread's older text reads
  under the old scheme.
