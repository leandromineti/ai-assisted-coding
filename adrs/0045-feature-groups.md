# ADR-0045 — feature groups: the registry starts teaching its subject matter

`decided: 2026-08-26` · status: **accepted**

## Decision

Every entry in `docs/feature-taxonomy.yaml` — all 49 in `features:` and all 20 in
`transcription_fields:` — carries a **`group:`**, and a new top-level **`groups:`** list
defines each group with `id` · `title` · `order` · **`blurb`**.

`comparisons/feature-registry.md` renders one `###` subsection per group inside each category
section, opening with the group's blurb. `features:` entries are additionally stored **in
group order**, so the matrices inherit the same grouping: `HARNESS_FEATURE_KEYS` and its four
siblings are built from registry entry order, and `comparisons/features.md`'s columns follow.

A group's `applies_to` is **derived from its members**, never declared — one less thing to
drift, and the same pattern `render_feature_registry` already used to find each category's
block.

## Context — the registry taught notation and nothing else

The registry's intro already teaches how to read a *cell*, and teaches it well: `presence` vs
`graded`, omitted-vs-`false`, the `engine > hook > script > prose` order, the three
verification routes, why `closed-enum` is not `open-descriptive`.

Nothing anywhere taught the *subject matter*. A reader could decode any cell in the file and
still not know what reasoning is and why it takes three keys, what egress means, or what a
write path is. The tables made that worse by being flat and long — **26 rows** for harnesses,
22 for memory — ordered "all assessed keys, then all transcribed fields", which is the
placement test's shape rather than anything a reader wants.

So the division of labour is deliberate and stated in the YAML's own comment: **the intro
teaches notation, the blurbs teach subject matter.** Neither repeats the other, and neither
repeats a key's own `definition`.

## Groups span the placement test

Category 1's **Identity** holds `maker`, `license`, `access`, `model_id`, `release_mode` and
`released` — all transcribed. **Reasoning** holds three assessed keys. **Cost** holds both:
`pricing` (transcribed) beside `prompt_caching` and `batch_discount` (assessed), because those
two exist only to move the base rate the first one records, and a reader asking "what does this
model cost" wants all three.

That means the **Basis** column is now the only thing marking the assessed/transcribed line.
This is an improvement, not a loss: Basis is a column that exists for exactly that purpose, and
a reader who has to look at it is a reader who has noticed the distinction — where row position
conveyed it silently, to nobody.

## The groups

| Category | Groups |
|---|---|
| 1 Models | Identity · Capacity · Cost · Reasoning |
| 2 Harnesses | Identity · Provenance · Shape · Environment binding · Extension points · Control gates · Operations |
| 3 Execution environments | Identity · Provenance · Shape · The boundary · What crosses it · What persists |
| 4 Workflow frameworks | Identity · Provenance · Shape · The spine · Verification gates · Orchestration |
| 5 Memory | Identity · Provenance · Shape · Store & scope · Write path · Read path · Integration |
| 6 Extensions | Identity · Provenance · Shape |

Three shaping rules, each a rejection of something simpler:

- **No group of one.** Category 4's `retrospectives` joins the spine rather than standing as a
  "Learning" group by itself — a group of one carries a heading and a paragraph to say what a
  single definition already says.
- **A sequence beats a bucket where one exists.** Category 3's assessed keys are cast as
  *boundary → what crosses it → what persists*, and category 5's as *store → write path → read
  path*. A reader can hold a sequence; three feature buckets have to be memorised.
- **Shared groups are literally shared.** `identity`, `provenance` and `shape` are one group
  each, appearing in every category that has the keys, with one blurb rendered in each place.
  Generated repetition costs nothing and puts the explanation where the reader is; a
  cross-reference would have saved bytes and spent a click.

## Consequences

- **Three new gates in `_load_feature_registry`**, in the same fail-fast style as the existing
  `value_type` / `verification` / placement-test checks: an entry with no `group`, an entry
  whose `group` does not resolve, and a **group nothing points at** — a half-landed rename that
  would otherwise render as a teaching paragraph above an empty table. All three were
  calibrated against mutated copies of the registry, not assumed from a green run.
- **`comparisons/features.md` column order changed** — same column set, grouped rather than
  registry-arbitrary. Verified by diffing the header rows before and after: same sets, only
  reordered.
- **The YAML was edited as text, not round-tripped.** `safe_load` drops comments, and this
  file's comments carry the block framing, ADR provenance and calibration notes. Parsing both
  versions and diffing the structures confirmed the 69 entries are byte-identical apart from
  the added `group:` key.
- **The category READMEs name the groups and link.** They restate no definition — the registry
  owns those (rule 3) — so the "note per category" the groups needed already existed as the
  **What we assess here** section, and gained a skeleton rather than a copy.
