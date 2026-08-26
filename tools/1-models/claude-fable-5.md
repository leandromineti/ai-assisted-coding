---
name: claude-fable-5
category: 1
vendor: Anthropic
url: https://platform.claude.com/docs/en/about-claude/models/overview
license: proprietary
open_source: false
model_id: claude-fable-5
release_mode: api-only
released: "GA 2026-06-09, no preview stage — then suspended 2026-06-12 and redeployed (vendor update dated 2026-07-01): the sweep's only GA interruption (verified 2026-08-17)"
context_window: 1000000
max_output: 128000
pricing:
  input: 10          # USD per MTok — base list rate (see the registry's rule)
  output: 50
  currency: USD
  regime: flat
  note: "$10 / $50 per MTok (verified 2026-08-17)"
knowledge_cutoff:
  knowledge: 2026-01       # YYYY-MM or YYYY-MM-DD; null when none is published
  training_data: 2026-01
  basis: vendor-stated
  note: "Jan 2026 (reliable); training data Jan 2026 — the two coincide. re-verified 2026-08-26 against the models overview page's own structured data (`reliableKnowledgeCutoff` / `trainingDataCutoff` — the field name is where this note's '(reliable)' comes from). Older than Opus 5's May 2026, same as Sonnet 5"
model_features:   # nested per ADR-0014 (2026-08-19); values unchanged
  thinking: "adaptive (always on)"
  prompt_caching: "write 1.25x (5m TTL) / 2x (1h TTL), read 0.1x — $12.50 / $20 / $1 per MTok"
  batch_discount: "50% in+out ($5 / $25 per MTok)"
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
Comparative latency: *slower* — the flagship trades speed for depth. Adaptive thinking
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
