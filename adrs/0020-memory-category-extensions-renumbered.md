# ADR-0020 — Memory becomes category 5; Extensions becomes category 6

`decided: 2026-08-22` · status: **accepted**

## Decision

Category 5 splits:

- **Category 5 — Memory.** The memory extensions (persistent cross-session state; the
  `memory_features` block, ADR-0013) become a full category. All nine reports stay at
  `category: 5`; the directory renames to `notes/05-memory/`. Reports keep
  `type: memory` in frontmatter — now redundant with the category, retained as data
  (dated here so the redundancy reads as decided, not drifted).
- **Category 6 — Extensions.** The residual bucket: ECC (`type: config-pack`) plus the
  six non-memory artifact types (`mcp-server · skill · hook · subagent-def ·
  rules-file · config-pack`) and the Standards spec-half. Bucket status transfers
  intact — ADR-0002's demotion logic and re-promotion trigger now speak about
  category 6. `ecc.md` moves to `notes/06-extensions/` with `category: 6`.

## Why, honestly

This **supersedes ADR-0016** (extensions stay broad) ahead of its recorded reopen
triggers (the ~2027-01 standards re-check; the issue-#30 balance arc closing), and
**supersedes ADR-0019 in part** (its mechanism stratum is promoted to a category rather
than thickening inside the bucket). The sample-bias objection ADR-0016 recorded — the
bucket looks memory-shaped because one arc seeded seven memory reports in a day — was
not answered by new evidence. It was acknowledged and **overridden by owner decision**
(2026-08-22): the memory kind has earned category status on its own vocabulary
(13-key feature block, its own matrix, a mechanism-adder identity the boundary
discussion sharpened), and the owner prefers the taxonomy to say so now rather than
after the balance arc. Recorded as a decision, not a finding.

What survives from the superseded records:

- ADR-0019's **content and reach strata carry forward as category-6 coverage
  semantics**: content types get Standards tracking plus exemplar reads; reach-side
  (MCP servers) gets capped exemplars, never censuses; `hook` remains the port, and
  `config-pack` is graded by payload (ECC: mechanism-grade). The X3 absorption bet in
  `design-principles.md` is unaffected.
- ADR-0016's warning stands as calibration: category 5's nine-report roster is still
  arc-shaped, and the balance arc (#30) continues — now as the **category-6 balance
  arc** — so the ~2027-01 re-check can judge the *extensions* bucket on a fair sample.

## The decoder

Pre-split references to "category 5" decode **by type**:

| Old | New |
|---|---|
| category 5, `type: memory` (and the memory arc, `memory_features`, ADR-0013 context) | **category 5 — Memory** |
| category 5, every other type (MCP servers, skills, hooks, rules files, subagent defs, config packs, ECC, the Standards coupling, kind_link supply side) | **category 6 — Extensions** |
| `notes/05-capability-extensions/<report>.md` | `notes/05-memory/<report>.md` — except `ecc.md` → `notes/06-extensions/ecc.md` |
| "the extensions category/bucket" (ADR-0002/0005/0016 prose) | category 6 |

Immutable ADR bodies (0002, 0005, 0007, 0010, 0012, 0013, 0015, 0016, 0018, 0019)
keep their pre-split numbers and paths; they decode through this table and are not
edited (beyond `superseded-by` lines on 0016 and 0019).

## Consequences

- `taxonomy.yaml` registers `5 · Memory` and `6 · Extensions`, so LINT-02 enforces the
  new pairings; the "memory layer" near-miss note inverts (the phrase now shadows a
  real division name and the canonical phrasing is "the memory category" / "category
  5"); the `types` and `bucket` term definitions re-anchor to category 6.
- Generator: `CATEGORY_NAMES` gains 6; the kind_link supply side splits (`memory`
  supplies from category 5, all other kinds from category 6); the harness-vocabulary
  matrix section covers categories 3, 5, and 6; the vendors table gains a sixth
  column; `harness_targets` renders for category 6.
- The kind→type rename gate (LINT-05) widens to categories 5 and 6, with a selftest
  fixture proving it fires at 6.
- Issue #30 continues as the category-6 balance arc; its premise (give the ~2027-01
  re-check a fair non-memory sample) is unchanged.
- A second config-pack ingest lands in category 6 and would give `config-pack` its
  feature-vocabulary instance bar (issue #2 rule) there.
