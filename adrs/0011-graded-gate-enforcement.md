# ADR-0011 — Graded enforcement values for gate features

`decided: 2026-08-18` · status: **accepted**

## Decision

The three gate keys in the feature taxonomy (`format_gates`, `measured_gates`,
`process_gates`) change from boolean to **graded enforcement values**:

`engine | hook | script | prose | true | false`

The value names the **strongest verified enforcer** of that gate class in the tool:
`engine` — an in-runtime code path that errors/blocks; `hook` — a harness-native
deterministic hook; `script` — a shell/CLI check that can hard-fail; `prose` — present
but enforced by the LLM applying instructions to itself; `true` — verified present,
enforcer not yet classified (the honest stub value); `false` — checked and absent.
Presence semantics are unchanged (any non-false value counts as "present" in the
cross-layer table); the grading adds the *who enforces* dimension without new keys.

## Context

Both 2026-08-18 deep-dives hit the same wall from opposite sides. spec-kit: a survey
✓ on `format_gates` flipped to ✗ when the deep-dive showed all its artifact gates are
prose (15/19 gates agent-enforced; the engine's own gate checks nothing). gsd-core:
the deep-dive found a four-rung enforcement ladder — plan-schema code errors,
deterministic gate verdicts that emit `{block:true}` with exit 0, a codified ban on
LLM-verdict blocking ("non-deterministic checks may not halt the loop"), and three
hard-blocking harness hooks — which a boolean flattens into the same ✓ a prose
checklist gets. The calibration lesson recorded at the spec-kit flip ("a gate stated
in prose looks like machinery until you check who enforces it") is thereby promoted
from a warning in a comment to a value the matrix can carry. Two verified instances,
per the issue-#2 discipline for vocabulary changes.

## Consequences

- Read-tool cells migrate now (gsd-core, spec-kit, openspec); stub cells stay `true`
  until their sources are read. The matrix stops equating GSD's `engine`-enforced plan
  schema with prose ceremony.
- `true` becomes a work-queue marker: every `true` in a gate column is an unanswered
  "who enforces?" question.
- Boolean keys outside the gate trio are unchanged; if the same ambiguity appears
  there (e.g. `context_isolation`, now hook-enforced in GSD), a future ADR can extend
  the scheme.
