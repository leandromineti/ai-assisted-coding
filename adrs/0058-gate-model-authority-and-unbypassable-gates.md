# ADR-0058 — Two control-gate keys: `gate_model_authority` and `unbypassable_gates`

`decided: 2026-09-24` · `status: accepted`

## Decision

Two keys join the `harness_features:` control-gates group (category 2 only):

- **`gate_model_authority`** (closed-enum): who besides the human and the operator's rules
  can decide a tool call — `none` (no model in the decision) | `deny-only` (a model can only
  tighten: block or escalate, never approve) | `approve` (a *separate* model can approve what
  would otherwise prompt) | `self` (the acting model's own output can approve its call).
  Default-on/off and bounds (operator deny rules, fail-closed) go in the cell comment, as for
  every presence key.
- **`unbypassable_gates`** (presence): `true` = at least one tool-dispatch check that the
  harness's own full-auto mode cannot switch off; the comment names the check and its
  ordering relative to the bypass. `false` = the full-auto flag dissolves every gate (or, as
  in pi, there is no gate to dissolve).

## Why now

ADR-0053 parked "model authority in the gate" as a second axis on `tool_approval` with the
trigger *a third widen-capable gate*. The 2026-09-24 release re-read batch supplied it three
times over: warp `AgentDecided` (the acting model's `is_risky:false` self-authorizes, above
the redirection deny); Claude Code auto mode (a separate classifier model, Sonnet 5 by
default, approves what Manual would prompt on, default starting mode on subscription plans,
bounded by operator deny rules, fails closed — docs-route); codex Guardian (a separate
reviewer session whose `Allow` becomes `ReviewDecision::Approved`, present at both pins,
default routed to the human, forcible per model by managed config). Deny-only instances:
qwen-code's classifier (`shouldBlock` only), gemini-cli's CONSECA (default-off, one-way).
The axis was already legible in cell comments; the enum makes `self` and `approve` stop
rendering as the same `policy` as a bare confirm.

`unbypassable_gates` comes from the same batch: gemini-cli v0.61.0 ships two default-on gates
ordered above its YOLO short-circuit (the untrusted-flag/build-file taint gate, Build File
Protection); qwen-code has had "non-overridable shell safety gates that must run before
auto/YOLO execution" a month longer; hermes' `approvals.deny` glob list blocks even under
`--yolo`; Claude Code's docs list actions no mode auto-approves. `tool_approval` and
`headless_approval` say when the gate fires and what it does with nobody there; this key
says whether the harness's own bypass can remove it. Census at admission is in the registry
notes; cells were set from citations already in each report, omitted where the report never
checked (continue, warp's own bypass, hermes' `smart` mode).

## Consequences

`docs/feature-taxonomy.yaml` gains both entries under `control-gates`; `tools/2-harnesses/README.md`
§ What we assess here counts 19 keys; `comparisons/features.md` renders both columns.
Nothing is renamed, so no decoder. `plan_mode` for codex is regraded `tool → mode` in the
same pass (a sticky `CollaborationMode`, not the act/plan split — cell comment carries the
weak-enforcement caveat); `turn_end_gates` cells now state direction and basis in the comment
(pi: continue-only contract; cline: obligation bookkeeping) without a new key.
