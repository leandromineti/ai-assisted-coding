# ADR-0035 — A generated SQLite export; frontmatter stays authoritative

`decided: 2026-08-26` · status: **accepted**

## Decision

`scripts/build-db.py` builds **`comparisons/repo.db`**, a SQLite view over the corpus:
`reports` (45), `features` (312 — the nested blocks unpivoted to report·block·key·value),
`papers` (22), `cards` (2), plus a `meta` build stamp. Gitignored, rebuilt from scratch in
**~0.4 s**, queryable with `--query "SQL"` (there is no `sqlite3` CLI on this host).

**The frontmatter remains the source of truth.** The database has exactly the standing of
anything in `comparisons/`: generated, never hand-edited, safe to delete. Nothing may cite
it, and **no fact may live only there** — if a query wants a column that does not exist,
the fix is a registry key and a reading, not a column in the build script.

This records a decision that until now lived only in conversation: files-as-database was
chosen over an actual database, because a claim in frontmatter sits next to the evidence
that earned it (rule 4) and stays git-diffable, and because the `# comments` beside values
carry provenance a row cannot (`turn_end_gates: engine  # session/turn.rs, confirmed at
the branch site`). The revisit condition then agreed was "a concrete query workload, and
then only as a generated export". Both halves are now satisfied.

## Why SQLite, and why now

The trigger was three owner queries: order every model's cutoff; does every model have a
fast mode; which is cheapest on fast mode.

**Relational over document-store**, because the questions are joins and orderings — "who
has `turn_end_gates: engine`", "which vendors span ≥3 categories", "models by input
price". The existing matrices in `comparisons/` are already relational projections done by
hand in Python. A Mongo-shaped store would fit the *source* better and buy nothing: schema
flexibility is already covered by JSON columns, and SQL is the part that was missing.

The hybrid is what makes it fit: real columns for the spine every report shares, **JSON
columns** for the five heterogeneous feature blocks (48 assessed keys that do not overlap
across categories), an `extra` JSON column so a field added tomorrow is queryable today
without touching the script, and the unpivoted `features` table because most questions are
`WHERE key = …` rather than a JSON path.

The ~0.4 s rebuild is a design constraint, not a statistic: at that cost nobody edits the
artifact or repairs it, which is what keeps it from quietly becoming authoritative.

## What the three queries proved

Built against the schema as it stands, deliberately, before changing any field — and
**two of the three fail on schema, not on storage**, which is the finding:

- **Order the cutoffs** — runs, returns nonsense. `knowledge_cutoff` is free-text in three
  date formats, so `ORDER BY` yields `Feb 16, 2026` · `Feb 2025` · `Jan 2026` · `January
  2025` · `May 2026` · `RETRACTED…` · four `not stated…`. Sorted alphabetically, as
  promised.
- **Does every model have a fast mode** — 11 category-1 reports, **0** registered keys
  matching `%fast%`, **1** prose mention (`claude-opus-5`'s pricing note). The answer is
  *unknown for ten models*, and a database renders unknown and absent identically — the
  omitted-vs-`false` distinction only exists for registered keys.
- **Cheapest on fast mode** — one row, and its numbers are the *base* rate, because
  fast-mode pricing is a variant living in prose.

For contrast, the half that was structured this morning answers instantly: base input
price across all eleven models, ordered, with the regime that qualifies each figure.

That contrast is the export's real first result. It is cheap evidence about which fields
deserve structure next, and it argues for the sequence **schema → reading → query**:
`knowledge_cutoff` wants the pricing treatment (sortable core, prose preserved,
`stated: false` for the six vendors that publish nothing), and `fast_mode` wants to be an
assessed key filled by reading eleven vendor pages — work no tooling removes.

## Boundary

No decoder: nothing renamed or moved. `comparisons/` gains one gitignored artifact and
`scripts/` one generator. The three `--check` lints are untouched — the database is not a
gate, and a stale copy is a non-event because it is never read by anything but a human
asking a question.
