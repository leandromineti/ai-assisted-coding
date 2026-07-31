---
name: claude-sonnet-5
layer: 1
vendor: Anthropic
url: https://platform.claude.com/docs/en/about-claude/models/overview
license: proprietary
open_source: false
model_id: claude-sonnet-5
release_mode: api-only
context_window: 1000000
max_output: 128000
pricing: "$3 / $15 per MTok — INTRODUCTORY $2 / $10 through 2026-08-31 (verified 2026-07-31; affects any cost ledger recorded before September)"
knowledge_cutoff: "Jan 2026 (reliable); training data Jan 2026"
checked: 2026-07-31
depth: survey
---

# Claude Sonnet 5

Anthropic's mid-tier: "the best combination of speed and intelligence." In this repo's
terms: **the standardized experiment model** — the deliberate cost/capability
compromise chosen so layer-4 comparisons measure frameworks, not model headroom.

## The layer-1 axes

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | · (exp-02 will produce the first in-repo evidence) |
| Long-horizon coherence | · |
| Usable context (vs advertised) | 1M advertised; unprobed here |
| Cost per completed task | **Time-sensitive:** intro pricing $2/$10 until 2026-08-31, then $3/$15 — a run costed in August is ~33% cheaper than the same run in September. Exp-02's ledger must record which price was in force |
| Release mode & access routes (1b) | API-only; Claude API + Bedrock + Vertex + Foundry. `effort` defaults to `high` on the Claude API and Claude Code — a cost-relevant default worth pinning in experiment configs |

## Role in this repo's work

- **The rig's pinned model** — exp-02's pre-run amendment names `claude-sonnet-5` the
  *sole* model for all arms of all layer-4 comparisons
  ([`experiments/02-spec-kit-vs-plain/`](../../experiments/02-spec-kit-vs-plain/README.md),
  amendment §1; [`experiments/rig/`](../../experiments/rig/README.md) pins table).
- The machine's standing subagent tier for lighter search/mechanical work (alongside
  Opus for substantive analysis).
- Adaptive thinking; no legacy extended-thinking toggle — prompt/config written for
  4.x-era thinking controls doesn't carry over unchanged.

## Surprises

1. **The introductory-pricing window lands mid-experiment-arc.** If exp-02 runs in
   August and exp-03 in September, their raw dollar ledgers are not comparable without
   normalizing to list price — recorded here *before* either run so the ledgers can't
   silently mislead.
2. Max output 128k (and 300k via a batch-API beta header) — output ceilings have
   quietly stopped being the binding constraint for agent work; iteration structure
   has.

## Open questions

- Exp-02 will produce the first measured trap-discovery and attention data on this
  model — fold the result back here (this report graduates to `deep-dive` when the
  repo's own measurements exist).
- Does `effort: high`-by-default change the cost profile enough that experiment
  configs should pin it explicitly? (The rig currently doesn't set it.)
