# ADR-0032 — `value_type` on every registry entry

`decided: 2026-08-26` · status: **accepted**

## Decision

Every entry in the feature taxonomy — all 48 assessed keys and all 19 transcription
fields — carries a **`value_type:`**, rendered as a **Type** column in
`comparisons/feature-registry.md`. Nine values:

| Value | Means | Count |
|---|---|---|
| `presence` | ✓/✗ presence-claim (omitted = not checked, `false` = checked-absent) | 25 assessed |
| `closed-enum` | one value from a closed set stated in the definition | 11 assessed · 3 transcribed |
| `graded` | ADR-0011's **ordered** enforcement scale: engine \| hook \| script \| prose \| true \| false | 4 assessed |
| `open-descriptive` | open vocabulary with a required `family:specific` shape | 3 assessed |
| `free-text` | the vendor's or subject's own words; no controlled vocabulary | 4 assessed · 3 transcribed |
| `list` | several values from a stated set | 1 assessed · 4 transcribed |
| `string` / `number` / `date` | a single identifier, a bare count, a date | 9 transcribed |

Unknown values are a generator **error**, not a warning — the same treatment `block` and
`verification` already get in `_load_feature_registry()`. An entry missing the field is
likewise fatal, so a new key cannot be added untyped.

## Why

Owner request (2026-08-26), reading the registry: a reader could see a key's definition
but not what shape its cell should take.

The information mostly existed — **21 of the 48 assessed keys already declared their shape
inside definition prose** (`warm_pool`: "boolean presence-claim"; `filesystem_sync`:
"closed lattice, plain enum: mount \| clone \| upload"; the four gate keys: "GRADED per
ADR-0011"). It was unstructured, unrendered, and absent from the other 27. This reifies
what was already being said.

**The vocabulary is the repo's own, not a generic type system**, and that was the live
decision. Generic types (`boolean`, `enum`, `number`, `date`, `text`) were considered and
rejected: they would flatten two distinctions this repo paid for. `closed-enum` vs
`open-descriptive` is ADR-0017's — a closed set a checker could validate against versus an
open vocabulary constrained only in shape — and collapsing both to "enum" would lose the
reason environment keys were designed that way. `graded` is ADR-0011's ordered scale,
where `engine` outranks `prose`; "enum" says nothing about order, and order is the whole
finding.

One shape question settled while assigning: `rules_files` takes `true` **or** a list of
filenames, and `memory_store` takes one store **or** a list for hybrids. Rather than mint
compound types, list-ness stays a property of the instance, recorded in the definition
where it already was; the key keeps its scalar type.

## What this buys next

Types are declarative today — rendered, not enforced against cells. The follow-on this
enables, and deliberately does not do yet: **enumerate the permitted values for each
`closed-enum` and `graded` key** (most are already spelled out in the definitions), at
which point `check-taxonomy.py` could fail a report whose `egress_default` says something
outside the declared set. Today that is silence. This ADR is the schema half of that; the
values half is a separate decision with a real filling cost.

## Boundary

No key, definition, or cell value changed — this adds a field and a column. No decoder:
nothing was renamed, and no dated material cites a Type column that did not exist.
`docs/feature-taxonomy.md` gains the vocabulary bullet; `comparisons/feature-registry.md`
is regenerated. The lint's duplicated `_load_feature_registry` is deliberately left
alone: it validates only what it uses (`id`, `block`), and coupling it to the generator's
schema was rejected when the duplication was chosen.
