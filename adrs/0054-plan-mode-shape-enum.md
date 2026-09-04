# ADR-0054 — plan_mode regraded from presence to a shape enum

`decided: 2026-09-04` · `status: accepted`

## Decision

`plan_mode` (category-2 `harness_features:`, control-gates group) changes
`value_type` from `presence` to `closed-enum`:

> the mechanism carrying the plan/act split: `mode` (sticky session state the
> harness holds until an exit transition) | `tool` (a model-invocable plan or
> switch tool) | `prompt` (a prompt-only convention, no state and no
> enforcement) | `flag` (a per-query, non-sticky nudge)

`false` keeps its meaning — checked and absent. Enforcement strength (read-only
state and policy data vs deliberately advisory) stays in cell comments; the
value names the carrier, not the strength.

## The deferral, and what fired

The shape spread has been in the registry note since the key was admitted:
"enforced MODE · tool · bundled skill · per-query FLAG — but only `mode` has ≥2
instances, so the enum promotion is deferred (ADR-0012, tracked with issue
#13)." That deferral was value-scope counting. Issue #34's decision (2026-09-04:
the two-instance rule binds keys, not enum values) dissolves it: the key-level
fact — a built-in plan/act split — has ten verified instances, and the values
are descriptive labels for mechanisms already recorded, source-cited, at the
cells.

Census from the existing comments (no re-reads):

- `mode` (5): claude-code (enforced read-only state + plan-file workflow +
  approval gate, docs-route), gemini-cli (`ApprovalMode.PLAN`, plan.toml
  catch-all deny — policy data, not prose; approved plans route to Flash),
  qwen-code (first-class mode with dedicated entry/shell policy files, threaded
  into compaction), dsh (sticky LOGGED session state + exit tool — deliberately
  NOT a tool restriction, and the comment carries that), cline
  (PLAN/ACT sticky state; `switch_to_act_mode` is the exit, not the carrier).
- `tool` (2): codex (a `plan` tool + collaboration-mode-templates), opencode
  (`plan.ts` tool; the prompt file rides along).
- `prompt` (2): continue (`DEFAULT_PLAN_SYSTEM_MESSAGE`), hermes-agent (`/plan`
  built-in command, still prompt-only, plans under `.hermes/plans/`, not a core
  loop mode).
- `flag` (1): warp (`UserQueryMode::Plan` derived per submission from the string
  prefix — no sticky state, no exit transition, `planning_enabled` hardcoded
  true server-side; "a nudge, not a capability switch").
- `false` (2): aider (grep → 0; `--chat-mode` is a different axis), pi (absent
  from the product; example extension only).

`flag` is single-instance — admitted under key-scope, and it is the value whose
loss to a `mode` merge would be a false claim (warp's own report insists the
distinction).

## Adjudication rule for borderlines

Where two mechanisms co-exist, the cell takes the one that HOLDS the split and
the comment names the other: cline is `mode` (the state is sticky; the tool
only exits it), opencode is `tool` (nothing sticky; the tool is the entry),
dsh is `mode` (sticky and logged, even though deliberately unenforced —
enforcement is not the axis).

## Argued and not admitted (with triggers)

- **An enforcement grade as a second axis** (ADR-0011-style: engine-enforced
  read-only state vs policy data vs prose). Real spread — claude-code/gemini-cli
  enforce, dsh declines to on principle, continue/hermes are prose — but it is
  the same species of fact the cell comments already carry, and control-gates
  has absorbed two regrades today. Trigger: a finding that turns on enforcement
  the shape value cannot express (e.g. a `mode` harness whose restriction is
  demonstrated bypassable).
- **A `skill` value.** hermes' plan skill was promoted to a built-in command in
  its v2026.8.31 window (alphabetical menu-trim, of all reasons) — the
  would-be instance no longer exhibits it, and no other cell does. Not minted;
  no speculative values (issue #34).

## Consequences

- Registry entry regraded (value_type, definition; the deferral sentence in the
  note replaced by the census — this ADR carries it).
- 12 cells re-valued per the census; comments preserved (they already carry the
  mechanisms and citations).
- `tools/2-harnesses/README.md` presence-count passage recounts (eleven
  presence, four not).
- Issue #13 is NOT closed by this ADR — its subject is `learning_loop`
  (category-5/6 seam), a separate re-read.
- Decoder: in prose written before 2026-09-04, `plan_mode: true` reads as "any
  of mode | tool | prompt | flag"; the old registry note's "bundled skill
  (hermes)" maps to today's `prompt`.
