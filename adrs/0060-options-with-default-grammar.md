# ADR-0060 — options with a default: one registry-level grammar for config-dependent cells

`decided: 2026-11-08` · `status: accepted`

## Decision

The registry gains one grammar for a fact whose value depends on configuration: the cell is
the tool's **shipped default**, and the configured alternatives sit beside it as data.

- A report's cell keeps exactly the default value it has today (scalar, list or boolean).
  Every matrix, every hand tally and every `features` row in the database therefore reads
  the default with no consumer parsing a string, which is the default-path rule the
  category-5 census already uses.
- Alternatives live in a top-level `options:` mapping of the report, keyed by registry id,
  each a list of `{value, via}` records. `value` is the alternative cell value; `via` is
  free text naming the switch, route, harness or command that selects it, with its
  `file:line` and evidence grade.
- A registry entry whose key carries options declares its legal named values in an optional
  one-line `values:` list, written directly after `value_type:`. Presence keys carry none
  and imply true or false.
- The generator renders a cell's default followed by ` (also <alternatives>)`, and an empty
  list renders `∅`, distinct from `·` (not checked) and `✗` (checked and absent).

**A departure from the owner's framing, stated plainly.** The framing of 2026-11-05 asked
for one grammar that generalizes `reasoning_effort`'s in-value `levels:<set>@<default>`
([ADR-0040](0040-reasoning-replaces-thinking.md)), so that no second spelling exists. This
ADR does not do that. `reasoning_effort` stays exactly as ADR-0040 wrote it, because there
the level set is itself the assessed fact (the dial a caller meets), not a list of
configurations beside a fact. The repo therefore carries one options grammar beside one
fact-shaped set spelling, and this ADR does not claim a single grammar. The departure is
the owner's to settle at review; the alternative that honours the wording literally is
listed under "Considered and not adopted".

## The grammar

A report that records an alternative adds an `options:` mapping at the top level of its
frontmatter. Two worked records, from the 20 existing `# options:` comments:

```yaml
memory_features:
  team_sharing: attribution-only        # the shipped default stays the cell value
  memory_scope: [user, project]
options:
  team_sharing:
    - value: acl
      via: "per-project grants (`ai-memory project access --mode restricted`, root-only, projects.access_mode V68__project_grants.sql:38-40)"
  memory_scope:
    - value: [user]
      via: "workspacePeer = false / OPENVIKING_WORKSPACE_PEER, config-schema.mjs:68"
```

The first is ai-memory's `team_sharing` with its `acl` option; the second is openviking's
`memory_scope`, whose alternative is itself a list. On the registry side:

```yaml
- id: team_sharing
  value_type: closed-enum
  values: [attribution-only, acl, false]
  definition: "... attribution-only (...) | acl (...)"
```

`false` in `values:` is registry notation for "checked and absent" and parses as a boolean;
comparisons use parsed values, never the string "false".

**The rules**, exactly as `check_options` enforces them. For every key under `options:`:

- (a) the key is a registered id, and the report has a cell for it in that entry's block;
- (b) the registry entry declares `values:` (a presence key implies `[true, false]`);
- (c) every alternative `value`, every element when it is a list, is in `values:`;
- (d) no alternative equals the cell's default (lists compare as sets);
- (e) no two alternatives are equal;
- (f) each record is exactly `{value, via}` and `via` is a non-empty string;
- (g) separately from `options:`, every cell of a key that declares `values:` has its value,
  every element when it is a list, inside `values:`.

Two structural rules precede them: `options:` is a mapping, and each key's value is a list of
records.

**The registry self-check.** Every string token in a `values:` list must occur as a whole
token (hyphens part of the token) in the entry's own `definition`, so the list cannot drift
from the prose it summarises; `values:` that is not a list is an error.

**The block-level rule.** A dark capability whose shipped state has no legal value of its
own (a mechanism that exists but is switched off, with nothing to name) stays in the cell
comment. A record exists only when an alternative **value** differs from the default.

## Enforcement

- `check_options(reports)` in `scripts/build-tool-index.py` runs from `main()` under both a
  plain run and `--check`, beside `check_pricing` through `check_shape_axes`, and exits
  non-zero with a named diagnostic starting with the report's path. The `values:` drift guard
  runs in the registry loader, so a bad registry fails every run.
- A negative suite of fifteen cases on scratch copies of the tree: one clean control that
  exits 0, and fourteen that each exit non-zero with their rule's diagnostic (an alternative
  outside `values:`, equal to the default, duplicated, with an empty `via`, on an
  unregistered key, on a key with no cell, on a key with no `values:`, an `options:` that is
  not a mapping, a key not holding records, a presence alternative outside true and false, a
  list alternative with an illegal element, a cell outside `values:`, a `values:` token not in
  its definition, a `values:` that is not a list).
- `scripts/build-db.py` writes one `features` row per alternative, with block `options`, and
  keeps `options` out of the report's `extra` JSON; "who offers `acl`" is a WHERE.
- The matrix legend and the registry notation explain the ` (also …)` annotation and `∅`.

## Why data beside the cell, not in the value

`yaml.safe_load` drops `#` comments, so the 20 interim `# options:` comments reached no
generator, no checker and no database row: an annotation or a validator designed over them
would read nothing. The grammar has to be data.

Putting it inside the value, generalizing `levels:<set>@<default>` into
`<opt>|<opt>@<default>`, would be self-contained on one line, and it was weighed seriously.
It would also make every consumer parse a string, so a `features.value` WHERE for `acl`
would stop matching `attribution-only|acl@attribution-only`; it would make each tally
correct only by code repeated in each consumer; it has no natural spelling for list cells
(`memory_scope: [user, project]` with the alternative `[user]`); and it is the envelope
[ADR-0039](0039-value-type-types-the-fact.md) rejected, a cell wrapping provenance
around the fact.

In `reasoning_effort` the set IS the assessed fact, so set and default share the value. In
`options:` the fact is what the tool does by default, and the alternatives are
configurations beside it, so they sit beside it. `reasoning_effort` is unchanged.
[ADR-0050](0050-wire-behavior-promotion.md)'s cell-value grammar is the precedent that a
grammar is defined in an ADR and enforced by a script that parses the cell.

## Considered and not adopted (with triggers)

- **The in-value spelling** (`<opt>|<opt>@<default>`), which honours the owner's one-grammar
  wording literally. Not adopted for the reasons above. Trigger: the owner prefers it at
  review, or a consumer needs single-line cells.
- **A closed `kind` field on records** (switch, per-harness, per-command, route, runtime
  mode). Nine of the 20 existing comments are not a switch on one install, and `via` carries
  that in prose. Trigger: a consumer that reads the kind.
- **Counting every option in tallies.** Rejected by the default-path rule: a tally of what
  tools do by default would move with every documented switch. Trigger: none; revisit only
  by superseding this ADR.
- **Migrating other categories now.** The default-on and opt-in qualifiers parked in
  comments by [ADR-0055](0055-context-assembly-group.md) and
  [ADR-0058](0058-gate-model-authority-and-unbypassable-gates.md), and the
  `reasoning_type` KNOWN STRAIN, are out of scope here and parked in issue #56.
  Trigger: that issue.

## Consequences

- Registry: `values:` on the option-bearing keys, set where the cells and the 20 comments
  need them (`learning_loop`, `write_admission`, `memory_revision`, `team_sharing`,
  `memory_scope`, `capture_path`, `recall_injection`) and on the new `compaction_capture`.
- Cells: the 20 frontmatter `# options:` comments (23 alternatives; the whole-file count of
  28 includes eight body-prose lines) migrate to `options:` records in the cells commit,
  after the memory-vocabulary ADR is accepted. Three carry a clause about the default itself
  and move that clause into the cell's own comment by hand.
- Triggers fired: [ADR-0055](0055-context-assembly-group.md) parked a default-on/opt-in axis
  on `context_compaction` until "the same species of grammar need arising on a second key";
  the category-5 comments are that second need, and [ADR-0056](0056-learning-loop-mechanism-enum.md)
  parked the same axis for `learning_loop`. The cells of ADR-0055 and ADR-0058 that carry the
  qualifier in comments, and the `reasoning_type` KNOWN STRAIN, go to issue #56.
- `reasoning_effort` ([ADR-0040](0040-reasoning-replaces-thinking.md)) is unchanged.
- No decoder needed: no prior prose used another name for these records.
