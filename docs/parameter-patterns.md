# Parameter patterns

`checked: 2026-09-03`

The pattern-analysis document this milestone's evidence base earns: cross-vendor asymmetries,
docs-vs-wire contradictions, and support-state distributions synthesized from Phase 11's
727-cell contract sweep, Phase 11.1's docs-vs-wire confrontation, and Phase 12's 83-cell
behavioral matrix — read as a results view, not as a re-derivation. Every claim below ends in a
`probe_id` or `cell_id` that resolves against committed classified evidence
(`probes/classified/contract-sweep.yaml`, `probes/classified/behavioral.yaml`); a claim without
one is not a finding here (methodology rule 4). Hand-kept per D-10 — a repo-level cross-category
finding, not probe tooling, and distinct from `comparisons/`, which is generated-only (rule 3).

**Valid through:** every rate/state cited in this document is valid only as of the evidence
dates below; no claim here should outlive a re-probe of the live APIs. Contract-sweep evidence:
`probes/classified/contract-sweep.yaml`'s own `checked: 2026-09-01`. Behavioral evidence:
`probes/classified/behavioral.yaml`'s own `checked:`/`evidence_through: 2026-09-03`.

This document grows across Phase 13's plans as each promoted key lands its finding section; this
plan seeds it with the opening framing and the first fully-cited finding, `stop_sequence_honesty`
— the tracer key this phase proves end-to-end before promoting the remaining five.

---

## Stop-sequence honesty

Truncation itself is nearly universal — the model stops generating at (or immediately after) the
requested stop sequence in 9 of the 10 domain models. What varies is whether the response's OWN
finish-reason field can prove that a stop, rather than a natural completion, is what happened.

**Domain: 10 of 12 tracked models.** `gpt-5-6-sol` and `grok-4-5` are structurally out of this
key's domain — the contract sweep observed both rejecting the `stop` parameter outright in
`default` mode, HTTP 400 (`gpt-5-6-sol--stop--["the"]--default--6a86352a`,
`grok-4-5--stop--["the"]--default--ee1a658f`), so no honesty verdict is reachable for either.

Only the 4 Anthropic models report a genuinely distinguishable finish value — `stop_reason:
stop_sequence` on the triggering call versus `end_turn` on the no-stop control
(`claude-fable-5--stop-truncation--triggering--default--61baa082`,
`claude-opus-5--stop-truncation--triggering--default--58a5a42f`,
`claude-sonnet-5--stop-truncation--triggering--default--905e8ef4`,
`claude-haiku-4-5--stop-truncation--triggering--default--19f5c60f`). Every other domain vendor
shares ONE generic finish value for both the natural-completion and the stop-sequence case:
Gemini's `STOP` (`gemini-3-1-pro--stop-truncation--triggering--default--c83e86af`) and the
`openai_compat` family's shared `stop` value (`kimi-k3--stop-truncation--triggering--default--5b566140`,
`deepseek-v4--stop-truncation--triggering--default--970252c9`,
`qwen3.8-max--stop-truncation--triggering--default--67a34da7`,
`qwen3.8-flash--stop-truncation--triggering--default--d1ae15ef`) are each emitted identically on
both the triggering call and its no-stop control — the finish field alone cannot distinguish the
two, and text comparison against the control is the only evidence this family trusts.

`glm-5.3` is a genuine third state, not a match to either group: the triggering call returned
empty visible text at the fired budget, so truncation itself was never confirmed against the
trigger word in this sweep (`glm-5.3--stop-truncation--triggering--default--01466ba7`) — recorded
`inconclusive`, distinct from both `honest` and `ambiguous`.

**Reading this for a caller:** a harness author who wants to detect "the model was cut off by MY
stop sequence" rather than "the model happened to end its own turn there" can trust the finish
field only at the four Anthropic models; everywhere else in this domain, the finish field is
silent on that distinction and the caller must compare against a control or inspect the returned
text directly.

Domain, per-model states, and every citation above are drawn from BHV-03
(`probes/classified/behavioral.yaml`), the promoted `stop_sequence_honesty` key, cited from the
report frontmatter as of `promoted ADR-0050`.
