# ADR-0036 — The feature registry becomes `feature-taxonomy.yaml`

`decided: 2026-08-26` · status: **accepted**

## Decision

The registry leaves `docs/feature-taxonomy.md`'s fenced block and becomes a real file:
**`docs/feature-taxonomy.yaml`** (440 lines — 48 assessed keys, 19 transcription fields,
comments intact). The prose half stays at `docs/feature-taxonomy.md`, now 78 lines, and
points at its sibling.

The two taxonomies are therefore shaped identically, which is the point:

| | prose | machine-readable |
|---|---|---|
| what a tool **is** | `tool-taxonomy.md` | `tool-taxonomy.yaml` |
| what is **assessed on** it | `feature-taxonomy.md` | `feature-taxonomy.yaml` |

## Why

Owner proposal, on the symmetry. Three things it buys beyond that:

1. **The fence extraction goes away.** Both consumers were doing
   `re.search(r"```yaml\n(.*?)```", text, re.DOTALL)` and exiting if it missed — a parser
   for a data format, duplicated in two scripts. Now `yaml.safe_load(text)`.
2. **A `.yaml` file gets YAML tooling.** Editors, linters, and diffs treat it as data
   rather than as a code block inside prose.
3. **It removes the schema's one unguarded copy**, found an hour earlier when the question
   "where does the feature schema live?" turned up five re-encoded fragments in Python.
   Four exit on drift (`known_blocks` twice, `VALUE_TYPES`, `PRICING_REGIMES`); the fifth —
   `BLOCKS` in `build-db.py`, added the same day — silently ignored anything new, so a
   sixth registry block would have produced a database quietly missing a column. It now
   derives from the registry in two lines, which reading a plain YAML file makes trivial.

## Boundary

**No decoder needed for paths** — `feature-taxonomy.md` keeps its name and place; a file
was added beside it. What *is* period: prose dated on or before 2026-08-26 says the
registry is "the YAML block below" or "the ```yaml block in feature-taxonomy.md". It is
now the sibling file. ADR bodies keep that wording.

Not done here, still open: `PRICING_REGIMES` remains in Python because the registry does
not yet carry permitted *values* for `closed-enum` and `graded` keys — ADR-0032's deferred
half, now the last hardcoded fragment with no home in the registry. A plain YAML file makes
that follow-on easier, not harder.
