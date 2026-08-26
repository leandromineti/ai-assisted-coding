# ADR-0029 — "Extensions" stays the name of category 6

`decided: 2026-08-26` · status: **accepted**

## Decision

Category 6's display name stays **Extensions** (full: "Extensions & protocols"). A
proposed rename to **"Stranger Things"** — tongue-in-cheek, and meant to communicate that
the bucket holds what goes beyond the taxonomy's current structure or cannot yet be
classified — is declined.

The observation behind the proposal is accepted as real and recorded where it belongs: as
a dated strain in `docs/taxonomy.md` § 6, with a falsifiable trigger, alongside the
category's existing re-promotion trigger.

## Why

**The same decision already exists in the other direction.** ADR-0005 renamed this bucket
*away* from "portable artifacts" on 2026-08-17 for one reason: the name asserted a
property its members do not intrinsically have. Portability "is a status the ecosystem
confers by adoption," so how portable each type is belongs in a dated per-type
measurement — "not a name." "Stranger Things" asserts *unclassified*, and § 6 denies it:
the bucket carries a positive definition (distributable content the agent can see and
touch), an independent-distribution membership test naming seven harnesses that accept the
same MCP server, coverage strata[^strata], and a dated re-promotion trigger. ADR-0016
considered narrowing the bucket and rejected that; ADR-0002 demoted it but gave the
demotion a shape — "artifacts distributed on file conventions — content plus specs, which
is a bucket's shape". A name asserting *unclassifiable* would contradict the most-argued
category in the repo.

**The name orphans the member noun.** The prose depends on a singular — "an extension",
"extension artifacts", the `type:` vocabulary — and there is no usable member noun under
the proposed name. "The stranger thing's independent-distribution test" does not survive a
sentence, so the prose would keep saying "extension" while the category said otherwise:
a divergence between name and content that no lint can catch, since the lint enforces the
name from `taxonomy.yaml` and cannot judge whether that name is *true*.

**It is the public map.** The taxonomy ships downstream as the mineti.dev article, so the
name travels to readers who never see this repo, and a pop-culture reference dates faster
than the findings it labels.

## What was recorded instead

The proposal identified something the record did not state anywhere: the bucket is
**residual in origin** — ADR-0002 demoted it to what remained after the runtimes and write
paths were absorbed into category 2 — while being **positive in test**. That gap is what
creates the pull to file anything homeless at 6, and `tools/candidates.md` is a holding pen
for unclassified *tools* only, with no equivalent for a shape the vocabulary cannot yet
name. § 6 now carries that as a strain, with the trigger that would force the question:
the first subject filed at 6 that fails the independent-distribution test, or a second
sighted shape with no home in categories 1–6. The first such shape —
orchestrator-above-harnesses (orca, 2026-08-20) — was filed at category 2 as the
least-wrong primary, which is the pull being resisted once, on the record.

If that trigger fires, the answer is a place for the not-yet-classifiable — not a renamed
category 6.

## Boundary

**No decoder.** Nothing was renamed, renumbered, or moved: the canonical name in
`taxonomy.yaml`, the `tools/6-extensions/` path, `CATEGORY_NAMES` in
`scripts/build-tool-index.py`, and every `6 · Extensions` table cell are unchanged, so no
dated material anywhere needs remapping. The only edits are § 6's new strain paragraph and
its `checked:` date.

[^strata]: [ADR-0019](0019-category-5-coverage-strata.md), decided 2026-08-22, superseded
in part by [ADR-0020](0020-memory-category-extensions-renumbered.md).
