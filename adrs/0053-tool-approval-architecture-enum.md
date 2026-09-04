# ADR-0053 — tool_approval regraded from presence to a gate-architecture enum

`decided: 2026-09-04` · `status: accepted`

## Decision

`tool_approval` (category-2 `harness_features:`, control-gates group) changes
`value_type` from `presence` to `closed-enum`:

> the gate's architecture at tool dispatch: `prompt` (a bare confirm function —
> no policy data, no tiers) | `policy` (a declarative rule/policy layer decides
> when to ask) | `sandbox` (no ask-gate; a compiled confinement layer stands in
> its place) | `none` (no gate and no substitute — confinement delegated to the
> operator)

The definition's scope is unchanged: dispatch-time approval, distinct from
sandbox *bounds* (`environment_relation`), turn gates (`turn_end_gates`), and
headless resolution (`headless_approval`).

## Why the boolean was a dodge, and what unblocked the regrade

The key went boolean on 2026-08-25 partly to sidestep the then-open
keys-vs-enum-values question (issue #34's own record). By 2026-08-27 the column
was complete — 12/12, 10 ✓ / 2 ✗ — and the ✓ was flattening a seven-way
mechanism spread (one confirm function with one modifier bit; a ~12.8k-line
tiered TOML policy engine; a six-level chain with a model-authored escape;
SafetyCheck inside a compiled OS sandbox; a three-value policy with a monotonic
clamp), while the two ✗s rendered dsh and pi — **opposite philosophies** — as
identical cells. Issue #34's decision (2026-09-04: the two-instance rule binds
keys, not enum values) removed the blocker; issue #46 item 2 is this regrade.

Value census, every cell already source-cited at its pin (no re-reads; the
existing comments carry the mechanisms):

- `prompt` (1): aider — 7 `confirm_ask` sites, "one boolean function, one
  modifier bit, no policy data, no tiers".
- `policy` (9): claude-code (permission modes/rules, docs-route), cline
  (per-tool `autoApprove` policy, surface-set), continue (three-value policy +
  per-argument dynamic evaluation, monotonic clamp), codex (SafetyCheck presets
  stacked on the OS sandbox), opencode (`Permission.ask` + rules), warp
  (`can_autoexecute_command` six-level chain), gemini-cli (tiered TOML policy
  engine, ASK_USER default), hermes-agent (`tools/approval.py`, hard denials
  beneath), qwen-code (four ApprovalModes + block-only LLM classifier).
- `sandbox` (1): dsh — pre-execute defaults allow; the gate is the compiled
  per-call OS sandbox.
- `none` (1): pi — no permission system, no sandbox; confinement delegated to
  external containerization by docs.

`prompt`, `sandbox`, and `none` are single-instance values — admitted under
issue #34's key-scope rule, the same way ADR-0052's postures were. The key-level
fact (a dispatch-time gate architecture) has twelve instances.

## Argued and not admitted (with triggers)

- **A second key for model authority in the gate** (warp's model-authored
  `is_risky:false` can WIDEN permission; qwen-code, continue, and cline clamp
  model/dynamic decisions to tighten-only). Both directions have ≥2 instances
  and the axis is the sharpest security finding in the column — but it is a
  property *of* `policy`-architecture gates, not a separate architecture, and
  admitting it today would double the control-gates delta in one day. Parked in
  the cell comments where it already lives. Trigger: a third widen-capable gate,
  or any harness where the direction is configurable.
- **An ADR-0011 grade ladder** (engine | hook | script | prose). Rejected on the
  merits: every verified gate here is engine-grade — the ladder cannot
  discriminate this column.
- **A cell-value checker** for the enum. The category's existing enums
  (`headless_approval`, `turn_end_gates`) are unvalidated today; a validator for
  all of `harness_features`' closed values would be one coherent change, not a
  per-key rider. Left open as its own candidate.

## Consequences

- Registry entry regraded in `docs/feature-taxonomy.yaml` (value_type,
  definition; note condensed — this ADR carries the history the old note
  narrated).
- 12 cells re-valued, comments preserved with their citations; only dsh and pi
  need lead-in rewrites (their "checked and absent" now reads `sandbox` /
  `none`).
- `tools/2-harnesses/README.md`: the presence-count passage and the pi
  four-✗ warning recount (pi's `tool_approval` is now a named value, not ✗ —
  its correlated-absence row drops to three ✗ cells).
- Decoder: in prose written before 2026-09-04, `tool_approval: true` reads as
  "any of prompt | policy"; `false` as "sandbox | none". The 10/2 split in
  older text maps to 1+9 / 1+1.
