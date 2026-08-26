# ADR-0026 — The constitution moves into `docs/`

`decided: 2026-08-26` · status: **accepted**

## Decision

`methodology.md`, `taxonomy.md`, `design-principles.md`, and `taxonomy.yaml` leave the
repository root and join `docs/`, unrenamed. `docs/` is rechartered as **everything that
is not a tool report, a source note, or an experiment**, in two halves: the constitution
(the rules the repo answers to) and the cross-category notes (ADR-0025's founding
contents). `docs/index.md` states the constitution first and the notes below it.

Root keeps only `README.md`, `CLAUDE.md`, `LICENSE`, and the eight directories.

This overturns one clause of [ADR-0025](0025-cross-cutting-becomes-docs.md) — *"the
constitution stays at root; `docs/` holds the notes around it, not the rules
themselves"* — decided earlier the same day. Everything else in 0025 stands: the
rules-vs-notes distinction survives as `docs/index.md`'s two-part structure rather than
as a directory boundary, and "cross-cutting" remains the concept name for the
category-spanning notes.

## Why

Owner request (2026-08-26): root rendered sixteen entries on GitHub before the README
began, and these four were the largest movable block. The counter-argument on the
record — that root placement is what signals "read these first, they outrank
`CLAUDE.md`" — is answered by `docs/index.md` carrying that sentence explicitly, and by
`README.md` and `CLAUDE.md` both linking the three in their first screen.

A `constitution/` directory was designed and rejected: it would have preserved 0025's
boundary at a cost of one root entry, but **"constitution" is already load-bearing
vocabulary here** for spec-kit's artifact (design principle F1, README conclusion 7,
experiment 02 throughout). A directory named for a studied
tool's concept is precisely the drift `check-taxonomy.py` exists to prevent.

Lint-scope check before moving, same as 0025: root `.md` files and `docs/*.md` were both
already linted, and neither is in `exempt_paths` — so the move changes no lint coverage.
`scripts/check-taxonomy.py` reads the YAML by path (one constant), and no other script
referenced any of the four.

## The decoder

Anything dated **on or before 2026-08-26** cites these four at root — `taxonomy.md`,
`methodology.md`, `design-principles.md`, `taxonomy.yaml`. All four map to
`docs/<file>`, unrenamed. Chains with the ADR-0024 and ADR-0025 decoders for material
predating them.

## Boundary

Same as 0024/0025: living docs, `adrs/README.md`, `scripts/`, `known_sites`, and the
generated matrices are rewritten or regenerated; **ADR bodies and preregistered
experiment protocols keep their period paths** and read under the decoder above. Three
links go stale by that rule and are left deliberately stale —
`adrs/0010-two-taxonomies.md`, `adrs/0019-category-5-coverage-strata.md`, and
`experiments/03-minimal-harness/README.md` — joining the equivalent stale links ADR-0024
left behind.

One correction made in passing: the `"egress layer"` `known_sites` pair in
`taxonomy.yaml` was re-derived rather than repathed, and both entries turned out to have
been line-stale before the move (`methodology.md:229` pointed at a blank line;
`CLAUDE.md:142` at an unrelated one). They now read `docs/methodology.md:248` and
`CLAUDE.md:160`. `known_sites` keys on `file:line`, so a stale entry vouches for nothing
and the lint stays green either way — a second net with a hole in it, worth knowing about
the next time one is relied on.
