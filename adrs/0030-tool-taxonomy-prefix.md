# ADR-0030 — The tool taxonomy's files take a `tool-` prefix

`decided: 2026-08-26` · status: **accepted**

## Decision

`docs/taxonomy.md` → **`docs/tool-taxonomy.md`**, and `docs/taxonomy.yaml` →
**`docs/tool-taxonomy.yaml`**. Contents unchanged.

The lint keeps its name — `scripts/check-taxonomy.py` — deliberately: it enforces this
repo's vocabulary as a whole, including the feature-registry key gate that reads
`docs/feature-taxonomy.md`, so `check-tool-taxonomy.py` would understate its scope.

## Why

Owner request (2026-08-26). ADR-0010 split this repo's vocabulary into **two taxonomies**:
the *tool* taxonomy, which classifies what a tool is, and the *feature* taxonomy, which
defines the characteristics assessed on tools. Only the second one's filename said which
half it was. `taxonomy.md` beside `feature-taxonomy.md` read as *the* taxonomy and its
qualified sibling, when they are peers.

The renamed file has described itself correctly since ADR-0010: *"This is the repo's **tool
taxonomy**, the half that classifies what a tool *is*; its companion, the **feature
taxonomy**, defines the characteristics assessed on tools."* The filename now says what
the first sentence has been saying all along, and the pair sorts together in `docs/`.

## The decoder

Anything dated **on or before 2026-08-26** cites `taxonomy.md` and `taxonomy.yaml` — at
root before ADR-0026, in `docs/` after it. Both map to the `tool-`-prefixed name in
`docs/`. `feature-taxonomy.md` is unaffected and unrenamed. Chains with the ADR-0024–0026
decoders for material predating them.

## Boundary

Same as 0024–0028: living docs, `adrs/README.md`, `scripts/`, and generated matrices are
rewritten or regenerated; **ADR bodies and preregistered experiment protocols keep their
period names** and read under the decoder above.

One trap worth recording, because the sweep hit it and the repair was not mechanical:
`adrs/README.md` is a living document that *quotes period names on purpose* — its standing
decoders exist precisely to tell a reader what old text looks like. A repo-wide rename
sweep rewrote those quotations too, turning "anything dated on or before 2026-08-26 cites
`taxonomy.md`" into a sentence that decoded the new name to itself. Four such statements
were repaired by hand (two decoder clauses, two index rows summarising decisions as they
were made); two neighbouring sentences that merely narrate history were reworded to name
the *concept* — "the tool taxonomy" — rather than any filename, which is drift-proof under
the next rename. **A decoder is the one kind of living text a rename must not touch.**
