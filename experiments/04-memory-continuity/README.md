# Experiment 04 — cross-harness memory continuity: does the kind's headline bet survive contact?

`preregistration drafted: 2026-08-19` · status: **DRAFT — not yet binding.** Rule 5
makes a preregistration binding when committed *before any run*; this file has had no
run against it, its fixtures are not yet written, and the scored arms have no spend
sign-off. Owner review → sign-off (quoted verbatim in log.md) → fixture build →
calibration arm → scored arms, in that order.

Protocol follows the template line of [`../03-minimal-harness/`](../03-minimal-harness/README.md);
results append below the untouched protocol. `log.md` appended live during runs.

## Question

The memory kind's verified identity bet is **cross-harness continuity** — the one thing
no single harness can absorb (conclusion 8 counter-current; conclusion 13). The
[ADR-0013 matrix](../../comparisons/features.md) showed it is also the kind's
*least-instantiated* feature: exactly one source-verified mechanism (ai-memory's
handoff baton), and that mechanism is thin by design — first prompt + last prompt +
tool names, no LLM, rich memory pull-only via MCP
([ai-memory report](../../notes/05-capability-extensions/ai-memory.md)). The bucket
index's standing rig question: *"capture a session, switch harness, measure what the
second agent actually knows."* This probe answers it for the only tool that can
currently attempt it.

## Subject & pin

ai-memory at report pin `acd9c0b` (deep-dive 2026-08-18). The probe builds/runs the
daemon from the pinned clone (prebuilt release binary acceptable if it matches the
pin's version; record which in log.md). Harness A = Claude Code (installed). Harness
B = opencode (to be installed at a recorded version; issue #17's fallback harness).

## Design

**Fixture: planted facts, not derivable from the workspace (5d's discriminating
instrument).** A scratch project (small TS utility, ~10 files) plus a scripted working
session in harness A that establishes **10 facts conversationally** — never written to
any file by the protocol: 4 decisions (D1–D4, e.g. "we chose base32 ids because of
case-insensitive filesystems"), 3 constraints (C1–C3, e.g. "never bump the schema
field without a migration note"), 2 preferences (P1–P2), 1 task-state item (T1, "the
edge-case in parseRange is unfixed"). The exact fact texts, the capture-session
script, and the 10-question quiz **with a fails-closed binary answer key** are written
and committed BEFORE the capture session runs (5a). A fact scores 1 only if the arm's
answer contains the key's required tokens (regex, case-insensitive); anything else —
including "I don't know" and plausible invention — scores 0.

**Arms** (all n=1 — this is a probe and says so; same workspace snapshot, fresh agent
context per arm):

| Arm | Order | What | Expected if bet holds |
|---|---|---|---|
| **B0 calibration** | FIRST | opencode, fresh session, **no ai-memory**, quiz | ≤2/10 — else facts leak from the workspace and the instrument cannot discriminate (5d): STOP, fix fixtures, re-run B0 before any scored arm |
| **B1 baton-only** | second | opencode + ai-memory hooks, **MCP pull tools denied** (permission config), quiz | the automatic floor — measures what switching harnesses gives you for free |
| **B2 baton+pull** | third | full ai-memory (baton + MCP tools allowed), quiz | the ceiling — measures what an agent that *knows to ask* recovers |
| **A-control** | last | Claude Code (the capture harness), fresh session, full ai-memory, quiz | same-harness comparison — is cross-harness worse than same-harness? |

**Also recorded per arm**: bytes of memory-derived context actually injected (from
hook logs / transcript), whether B2 actually called pull tools unprompted, wall-clock.

**Smoke test (5e)**: the full driver (session spawn → quiz → transcript scoring) runs
once end-to-end with empty memory before anything is scored; success read from
artifacts (a scored quiz JSON exists and every check evaluated), never exit status.

**Declared network condition (8a, honest limitation)**: this probe runs on the HOST,
not the egress-controlled rig — ai-memory's daemon is localhost-bound; model traffic
goes to Anthropic. Declared as: host network, daemon loopback, no egress enforcement.
This is weaker than the rig standard and is why the result is a probe, not a
comparison. Identical condition across all arms.

**What would falsify what** (5f): B0 high → instrument broken (no claim possible).
B1 ≈ B0 → the automatic floor is negligible; the baton buys ~nothing and the bet
rests entirely on agent-initiated pulls. B2 >> B1 → continuity is real but *pull-
shaped* — it depends on the receiving agent's tool use, corroborating the report's
"rich memory is pull-only" reading. B2 ≈ B0 → the headline bet fails contact for the
only tool that ships it. A-control >> B2 → continuity degrades across harness
boundaries specifically, i.e. the cross-harness claim is the weak link.

## Spend & gates

- Scored arms: ~5 short sessions total (1 capture + 4 quiz) + 1 smoke. Claude Code
  sessions ride the subscription; opencode arms need an Anthropic API key on this box
  — estimate **< $5** at Sonnet-tier pricing, zero if a key is not available (then the
  probe blocks on the harness-B question and says so).
- **No scored arm runs before**: owner protocol review, spend sign-off quoted verbatim
  in `log.md`, B0 calibration passing its gate.
- Amendments: dated, appended, labelled pre-/post-run; protocol text above never
  edited (rule 5).
