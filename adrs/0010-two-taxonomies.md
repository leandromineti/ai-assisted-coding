# ADR-0010 — Two taxonomies: tool taxonomy and feature taxonomy

`decided: 2026-08-18` · status: **accepted**

## Decision

The repo carries two named taxonomies:

- The **tool taxonomy** — [`taxonomy.md`](../taxonomy.md), unchanged in structure —
  classifies what a tool *is*: the five layers, with sub-categories where a layer has
  grown them (layer 5's `kind` vocabulary; layer 4's SDD / context-discipline /
  decision-governance poles).
- The **feature taxonomy** —
  [`notes/cross-cutting/feature-taxonomy.md`](../notes/cross-cutting/feature-taxonomy.md),
  new — defines every characteristic assessed on tools **once**: id, one-line
  definition, the frontmatter block that carries it, an `applies_to` layer map, and an
  optional `kind_link` recording the demand↔supply correspondence between a harness
  feature and the layer-5 artifact kind that supplies it.

`build-tool-index.py` derives its valid-key lists (`FEATURE_KEYS`,
`WORKFLOW_FEATURE_KEYS`) from the registry instead of hardcoding them, and renders a
generated **cross-layer table** in `comparisons/features.md`: for each feature that
spans layers or has a `kind_link`, the demand side (presence counts from harness/
framework rows) against the supply side (count of tracked layer-5 tools of the linked
kind). Report frontmatter blocks are untouched in this pass; block-name unification is
recorded as a separable follow-up, not decided here.

Terminology settled the same day: "taxonomy" had been reserved for the layer structure
alone, and the per-layer key-sets were briefly titled a "feature taxonomy", then
debated as "vocabulary" vs "feature set". This ADR resolves it: there are two
taxonomies; "vocabulary" survives only as the mechanism phrase for a closed key list
(the don't-add-vendor-pet-names discipline).

## Context

The 2026-08-18 session created the layer-4 `workflow_features:` key-set, at which
point the repo had three disconnected key lists (harness features, workflow features,
model features) plus layer 5's `kind` — with the relationships between them living
only in prose. The proposal (Leandro's): consolidate classification into a tool
taxonomy and description into a feature taxonomy, so that cross-layer features become
quantifiable. The motivating observation is the bleed: `skills`, `hooks`, `subagents`,
`mcp`, `learning_loop` are simultaneously harness capabilities (demand) and layer-5
artifact kinds (supply); `measured_gates` — the mechanism exp-01 credited with
carrying quality — can arrive via a framework's prose or as installable Stop hooks
(the ECC finding). "The harness absorbs features from other layers" was a conclusion
stated in prose; the registry makes it a generated table.

New-key discipline carries over unchanged: issue #2's two-verified-instances rule.

## Consequences

- One source of truth for feature keys; the generator fails loudly if the registry is
  missing or unparsable. Adding a key anywhere else is now a lint-visible error.
- The bleed is measured, not asserted — the cross-layer table shows demand counts
  against tracked supply (including honest zeros where no supply-side tool is
  tracked yet).
- Template per-key definition comments moved to the registry (drift risk removed);
  the template keeps key skeletons and points here.
- Deferred, explicitly not decided: `workflow_features:` → `features:` block
  unification; folding `MODEL_FEATURE_KEYS` in; a `subfamily:` frontmatter field for
  tool-taxonomy sub-categories.
