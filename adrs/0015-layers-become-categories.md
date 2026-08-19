# ADR-0015 — Layers become categories

`decided: 2026-08-19` · status: **accepted**

## Decision

The taxonomy's top-level divisions are canonically called **categories**, not layers.
The rename is a vocabulary decision, not a reclassification: no tool changes its home,
the numbering (per [ADR-0007](0007-renumber-core-triad-first.md)) is unchanged, and the
five divisions keep their current names.

The old → new decoder:

| Old term | New term | Scope |
|---|---|---|
| `layer` (prose noun, e.g. "layer 2") | `category` | prose everywhere, and the report frontmatter key `layer:` |
| `kind` (category-5 sub-classification) | `type` | prose and the frontmatter key `kind:` in category-5 reports |
| `sub-category` | `type` | prose (the same category-5 sub-classification vocabulary as `kind`) |
| `## The stack` (taxonomy.md section heading) | `## Tool categories` | the taxonomy.md divisions heading |

Every touchpoint above must move together in a single commit: report frontmatter keys
across all tool reports, `notes/_template-tool-report.md`, `scripts/build-tool-index.py`,
and the remaining living prose (`taxonomy.md`'s body and its `## Layer indexes` heading).
Renaming any one of these alone breaks the others' agreement with it.

## Context

1. **The owner's driving argument.** "Categories" is a more general term that does not
   imply the divisions are stacked — the owner's own framing, verbatim: "categories… a
   more general term that does not imply they are stacked (necessarily)." The decision
   was made by the owner in discussion; this ADR documents the reasoning, it does not
   re-litigate it.

2. **The triad-vs-stack argument from [ADR-0004](0004-core-triad-reframing.md).** The
   core-triad reframing already weakened the stacking claim: model + harness +
   environment became three fundamentals with two interfaces (workflow frameworks,
   extensions) rather than a five-rung ladder to climb. Once the "stack" framing was
   demoted to describing the fundamentals-plus-interfaces relationship rather than the
   whole taxonomy's shape, the section heading `## The stack` — naming the taxonomy's
   top-level divisions, not the triad — had outlived the frame it was coined under.
   "Categories" names what the divisions actually are (classification buckets), where
   "stack" asserted a stacking relationship the reframing had already backed away from.

3. **The collision analysis.** The word "category" was already in use three ways in
   `taxonomy.md` before this decision:
   - **"category error"** in the opening line ("`Claude Code vs. GSD vs. Opus 5` is a
     category error"). **KEPT.** Under the rename this phrase *aligns* rather than
     collides: comparing tools across categories without accounting for what category
     each occupies is now literally a category error — the phrase becomes more
     accurate, not less, after the rename. This is the argument the owner found
     persuasive (D-04).
   - **"sub-categories"** in the header block ("Layers may carry **sub-categories**
     (layer 5's `kind`; layer 4's SDD / context-discipline / decision-governance
     poles)"). **BECOMES `types`** under the `kind` → `type` rename (D-02) — this usage
     was always naming the same category-5 sub-classification concept as `kind:`, so it
     folds into the same new term rather than staying a separate synonym.
   - **"a category that isn't a layer at all"** in the Standards section opening. This
     phrase is reworded in plan 02 of this phase (D-05) — after the rename, the phrase
     itself would misread as self-contradictory ("a category that isn't a category"),
     so it needs new wording, not merely a term swap; that wording work is deliberately
     scoped to plan 02 rather than this ADR.

   All three sites were checked and none of them silently collide after the rename —
   each is either kept with an improved reading, folded into the new term, or scheduled
   for a reword.

## The decoder

Material predating the sweep commit that lands the rename repo-wide (report frontmatter
keys, `notes/_template-tool-report.md`, `scripts/build-tool-index.py`, and the remaining
living prose — Phase 3 of this project, see `## Sequencing` below) reads under the old
vocabulary: `layer`, `kind`, `sub-category`, `## The stack`. That sweep commit has not
been made yet as of this ADR's acceptance — no commit hash is recorded here; the
boundary is that future sweep commit, not this ADR's date, and the sweep commit's own
message cites this ADR (`ADR-0015`) as its authority, matching the "boundary is the
commit, not the calendar date" idiom established at
[ADR-0007](0007-renumber-core-triad-first.md#the-decoder).

Directory slugs (`notes/03-execution-environments/`, `notes/05-capability-extensions/`)
contain no banned word and are unaffected by this decision (D-14) — no directory rename
is implied or required.

Git history, experiment protocols and logs (immutable by methodology rule 5), published
article snapshots, and old GitHub URLs predating the sweep also read under the old
vocabulary, by the same boundary.

## Sequencing

`scripts/build-tool-index.py` declares `REQUIRED = ("name", "layer", "depth")` and reads
`r["layer"]` at roughly 18 call sites; 40 files under `notes/` carry a `layer:`
frontmatter key. Renaming the generator's required key before the reports migrate breaks
the generator (`missing ['category']` warnings on every report); renaming the reports
before the generator does the same in the other direction. The two key renames (`layer`
→ `category`, `kind` → `type`) therefore land in **one atomic commit in Phase 3** —
generator, `notes/_template-tool-report.md`, and report frontmatter together.
`taxonomy.yaml`'s `schema_renames` block is the machine-readable form of this contract,
so Phase 3 executes a recorded contract rather than a memory.

This phase (Phase 1) executes **zero** of the mechanical rename: it only decides the
vocabulary (this ADR) and encodes it machine-readably (`taxonomy.yaml`). Verified at
this ADR's acceptance: `python3 scripts/build-tool-index.py --check` and
`python3 scripts/build-refs-index.py --check` both exit 0 ("38 reports checked, 0
unverifiable"; "22 refs checked, 0 problem(s)"; the `behind:` lines are drift reports,
not failures) — proof this phase did not over-reach into Phase 3's rename.

## Consequences

- Category values 1–5 are unchanged across all reports — this is purely a key rename
  (`layer:` → `category:`, `kind:` → `type:`), not a reclassification (D-03).
- `taxonomy.yaml` is a new file at the repo root, sibling of `taxonomy.md`, and becomes
  the sole source of truth for taxonomy vocabulary (canonical terms, deny-lists,
  reference formats, carve-outs); `taxonomy.md` becomes a prose document linted against
  it rather than holding vocabulary data itself (D-06, D-07).
- Resolved fact: `scripts/build-refs-index.py` contains zero occurrences of the word
  `layer` (verified 2026-08-19) and needs no edit in either phase. Its own `kind:` key
  (`REQUIRED = ("key", "title", "year", "kind", "read_depth", "retrieved")`) is refs'
  source-kind vocabulary (`paper` / `benchmark` / `blog-post`, etc.) — an entirely
  different vocabulary from category-5's `kind:`, unrelated to D-02, and is never
  renamed by this decision.
- Compound-word resolution: `cross-layer` is drift and becomes `cross-category`;
  `cross-cutting` is untouched because it contains no banned word — the same resolution
  `taxonomy.yaml`'s `terms` encoding records, so the two cannot disagree.
- `bucket` stays canonical (per [ADR-0002](0002-extensions-demoted-to-bucket.md)) — it
  names category 5's *shape*, a loose collection, and is not a synonym for `category`
  (D-10); it is not swept by this rename.
