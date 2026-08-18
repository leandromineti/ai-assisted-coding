# ADR-0012 — Layer-2 feature-set revision: `ptc`, graded `turn_end_gates`

`decided: 2026-08-18` · status: **accepted**

## Decision

Two keys enter the feature taxonomy's layer-2 block (`features:`):

- **`ptc`** — programmatic tool calling: the model emits code that drives tools inside
  a sandboxed runtime, instead of chat-loop tool calls. Boolean.
- **`turn_end_gates`** — a native turn-end verification/stop gate: the harness can veto
  or re-prompt the model's attempt to end its turn. **Graded** per ADR-0011's scheme
  (`engine | hook | script | prose | true | false`, strongest verified enforcer) — this
  is the "future ADR can extend the scheme" case ADR-0011 anticipated for keys outside
  the layer-4 gate trio. `kind_link: hook` — the layer-5 supply side is the ECC finding
  (verification gates arriving as installable Stop hooks).

Two promotions are **deliberately deferred**, with the same discipline that admitted
the keys above:

- `plan_mode` mechanism enum (`mode | tool | skill`): the shapes diverge across five
  verified reports (mode: claude-code, opencode, cline · tool: codex · skill: hermes),
  but only `mode` has ≥2 instances. Recorded as a registry note; tracked with issue #13.
- `learning_loop` mechanism enum (`background | in-loop | manual`): issue #13, still
  blocked at 2/1/1 instances per variant.

## Context

Both new keys met issue #2's two-verified-instances rule *before* this pass, in the
July deep-dives:

- `ptc`: hermes' `execute_code` (model-written Python calls tools via RPC, iteration
  budget refunded) and codex's `code-mode*` crates (model-written code in an embedded
  V8 with the V8 sandbox enabled). Parked as issue #3 on 2026-07-30 to avoid
  "vocabulary growth by momentum"; admitted now as part of a deliberate layer-2
  feature-set definition pass, which is the forcing function #3 waited for.
- `turn_end_gates`: hermes' `verification_stop.py` (in-loop policy, ≤3 re-prompts when
  the model tries to finish without fresh verification evidence — `engine`) and codex's
  `run_turn_stop_hooks` → `should_block` (turn termination vetoed by hook — `hook`).
  This is conclusion 8's core leg — "the mechanism conclusion 6 credits with layer 4's
  quality margin, living below layer 4, twice" — which until now had no registry key
  and therefore no matrix column. Grading matters here for the same reason it did in
  ADR-0011: the layer-4 arc ended with every tracked framework's gates at `prose` or
  `script`; harness-native gates at `engine`/`hook` are the sharpest quantitative form
  of the absorption thesis, and a boolean would flatten exactly that.

## Consequences

- The layer-2 matrix gains two columns; cells migrate only where report bodies already
  carry the evidence (hermes, codex). All other reports: omitted = not checked; nobody
  back-fills without reading.
- The cross-layer table gains a `turn_end_gates` demand/supply row (`kind_link: hook`).
- Issue #3 closes; issue #13 stays open and now also tracks the `plan_mode` enum.
- Grading outside the layer-4 gate trio now has this precedent: extend per-key, by ADR,
  when the boolean demonstrably flattens a verified enforcement difference — not as a
  blanket migration.
