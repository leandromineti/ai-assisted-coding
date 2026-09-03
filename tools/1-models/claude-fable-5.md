---
name: claude-fable-5
category: 1
maker: Anthropic
url: https://platform.claude.com/docs/en/about-claude/models/overview
license: proprietary
access: closed-source
model_id: claude-fable-5
release_date:
  date: 2026-06-09
  stage: GA
  note: "no preview stage; then suspended 2026-06-12 and redeployed (vendor update dated 2026-07-01) — the sweep's only GA interruption (verified 2026-08-17)"
context_window: 1000000
max_output: 128000
pricing:
  input: 10          # USD per MTok — base list rate (see the registry's rule)
  output: 50
  currency: USD
  regime: flat
  note: "$10 / $50 per MTok (verified 2026-08-17)"
knowledge_cutoff:
  date: 2026-01          # the limit date on training data
  basis: vendor-stated
  note: "Jan 2026 (reliable); training data Jan 2026 — the two coincide. re-verified 2026-08-26 against the models overview page's own structured data (`reliableKnowledgeCutoff` / `trainingDataCutoff` — the field name is where this note's '(reliable)' comes from). Older than Opus 5's May 2026, same as Sonnet 5"
model_features:   # nested per ADR-0014 (2026-08-19); reasoning keys split per ADR-0040
  reasoning: true
  reasoning_type: always-on   # confirmed 2026-08-26: docs table Default "Always on"; rejects BOTH `enabled` and `disabled`
  reasoning_effort: "levels:low/medium/high/xhigh/max@high"   # settled 2026-08-26 — `output_config.effort` (§ Reasoning surface)
  prompt_caching: "write 1.25x (5m TTL) / 2x (1h TTL), read 0.1x — $12.50 / $20 / $1 per MTok"
  batch_discount: "50% in+out ($5 / $25 per MTok)"
  fast_mode: false   # checked and absent: the fast-mode page's supported-models list is Opus 5 + Opus 4.8 only, and `speed: "fast"` on an unsupported model returns an error (verified 2026-08-27)
  stop_sequence_honesty: "honest — OBSERVED 2026-09-03: stop-honored truncation before the trigger word, and the response's own stop_reason field reports the distinguishable value stop_sequence (vs. end_turn on the no-stop control) — the finish field alone proves which case fired, cell_id:`claude-fable-5--stop-truncation--triggering--default`, probe_id:`claude-fable-5--stop-truncation--triggering--default--61baa082`, promoted ADR-0050."
  seed_determinism: "n/a (no request-side field) — OBSERVED 2026-09-03: Anthropic's Messages API reference documents no seed parameter for claude-fable-5 — the full top-level Body parameters list was read end to end with no match (rule 1b checked-absence), docs-claims:`seed/anthropic`, promoted ADR-0050."
  sampling_repeatability: "0/4 repeat pairs (varies) — OBSERVED 2026-09-03: claude-fable-5 rejects an explicit temperature value outright in default mode (HTTP 400); this default-config-repeatability SUBSTITUTE instead asks whether the model's own default (implicit) sampling is repeatable across five identical requests with no temperature parameter sent at all — the closest question this model's own accepted request surface can answer — and all five completed naturally (end_turn) with five distinct outputs, cell_id:`claude-fable-5--default-config-repeatability--no-temperature--default`, probe_id:`claude-fable-5--default-config-repeatability--no-temperature--default--r1--bbdda63f`, promoted ADR-0050."
  multi_candidate_delivery: "n/a (no request-side field) — OBSERVED 2026-09-03: Anthropic's Messages API reference documents no n/candidateCount-equivalent multi-candidate parameter for claude-fable-5 — the full top-level Body parameters list was read end to end with no match (rule 1b checked-absence), docs-claims:`n/anthropic`, promoted ADR-0050."
  logprobs_delivery: "n/a (no request-side field) — OBSERVED 2026-09-03: Anthropic's Messages API reference documents no logprobs parameter for claude-fable-5 — the full top-level Body parameters list was read end to end with no match (rule 1b checked-absence), docs-claims:`logprobs/anthropic`, promoted ADR-0050."
  service_tier_contract: "response-asymmetric — OBSERVED 2026-09-03: `service_tier` is accepted at the presence probe but not echoed back at the requested value (accepted-ignored), probe_id:`claude-fable-5--service-tier--auto--default--aa7ed336`; the value-enum row (openai-service-tier-values) does not fire for Anthropic models — not tested here. The response-side shape is the shared Anthropic Messages API contract (same field, same endpoint across all 4 Claude models), verified directly at sibling model claude-haiku-4-5: the tier is reported at `usage.service_tier`, nested under the usage envelope and never mirrored to the top level, and sending the response-vocabulary word `standard` as a request value is rejected outright naming the field, cell_id:`claude-haiku-4-5--service-tier-audit--auto--default`, probe_id:`claude-haiku-4-5--service-tier-audit--auto--default--613638b0`, cell_id:`claude-haiku-4-5--service-tier-audit--trap--default`, probe_id:`claude-haiku-4-5--service-tier-audit--trap--default--8fc20f53`, promoted ADR-0050."
checked: 2026-08-17
depth: stub
---

# Claude Fable 5

Anthropic's most capable widely released model: "next-generation intelligence for
long-running agents." GA 2026-06-09 across Claude API and all cloud routes — then
**suspended three days later** (2026-06-12) and redeployed, with the vendor's
restoration update dated 2026-07-01 (anthropic.com/news/redeploying-fable-5). The only
GA interruption in this sweep: a lifecycle event no "GA date" cell can carry alone,
and a reminder that GA is a state, not a milestone.
Comparative latency: *slower* — the flagship trades speed for depth. Adaptive reasoning
is **always on** (not merely available). A sibling exists: **Claude Mythos 5**, same
specs and pricing, invitation-only under Project Glasswing for defensive-cybersecurity
work — the first case in this study of a frontier model gated by *use-domain* rather
than by tier.

## The category-1 axes

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | · |
| Long-horizon coherence | The vendor's own positioning claim ("long-running agents") — unmeasured here, and exactly the axis the taxonomy says has no standard measure |
| Usable context (vs advertised) | 1M advertised, with a tokenizer caveat that matters: Fable 5 uses the Opus-4.7-era tokenizer — the same text costs ~30% more tokens than on pre-4.7 models, so cross-generation token counts are not comparable |
| Cost per completed task | 2× Opus per token; whether it's cheaper per *completed task* is an open empirical question (the taxonomy's preferred metric) |
| Release mode & access routes (1b) | API-only; four cloud routes; Mythos twin gated by domain |

## Reasoning surface

`reasoning_effort` **resolved 2026-08-26** (issue #38) and `reasoning_type` confirmed the
same day, against two pages neither of which is this report's `url`:

- [`/build-with-claude/effort`](https://platform.claude.com/docs/en/build-with-claude/effort)
  — *"Effort is the primary control for trading off intelligence, latency, and cost on
  Claude Fable 5. **Start with `high`, the default**"*; the level table lists Fable 5 under
  both `max` and `xhigh`, so all five are available. The dial is `output_config.effort`.
- [`/build-with-claude/thinking-troubleshooting`](https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting#supported-models)
  — the per-model table: *"Adaptive only"*, Default **Always on**, and it is the strictest
  row in the lineup, rejecting **both** `"enabled"` and `"disabled"` with a 400. *"Models
  marked `Always on` cannot turn thinking off."*

Fable 5 is where the two keys come apart most cleanly. Reasoning cannot be switched off at
all (`always-on`), yet it has the full five-level dial — so "can't turn it off" and "can't
control it" are plainly different facts, which a single free-text cell tended to blur.

The old cell held, verified 2026-08-17: `thinking: "adaptive (always on)"` — two facts in
one string, which is what ADR-0040 split. The row's `checked:` stays **2026-08-17**: only
the reasoning cells were re-verified today, and the field dates the whole spec block.

## Role in this repo's work

None pinned yet — no experiment or standing rule routes to it (subagent rules
deliberately exclude it on this machine). This report exists because the flagship is
the reference point everything else is benchmarked against; it graduates past `stub`
when repo work actually runs on it with evidence worth recording.

## Surprises

1. **The ~30% tokenizer inflation** hiding inside "1M context" — cross-model cost and
   context comparisons that ignore tokenizer generation are quietly wrong. Directly
   relevant to any future cross-model experiment ledger (methodology 5c measures
   tokens from transcripts; those tokens are not a constant unit across models).
2. **Domain-gated model access** (Mythos/Glasswing) as a release mode — neither
   API-only nor open-weights; the 1b access-routes vocabulary gains a third shape.

## Open questions

- Does the "long-running agents" positioning survive a measured long-horizon probe —
  and what would that probe even be? (The category-1 index's open question, now with a
  designated subject.)
- Is 2× Opus pricing justified per completed task on this repo's task shapes?
