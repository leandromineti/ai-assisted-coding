---
name: claude-opus-5
layer: 1
vendor: Anthropic
url: https://platform.claude.com/docs/en/about-claude/models/overview
license: proprietary
open_source: false
model_id: claude-opus-5
release_mode: api-only
context_window: 1000000
max_output: 128000
pricing: "$5 / $25 per MTok (verified 2026-07-31)"
knowledge_cutoff: "May 2026 (reliable) — the freshest cutoff in the current lineup, newer than Fable 5's Jan 2026"
checked: 2026-07-31
depth: survey
---

# Claude Opus 5

Anthropic's agentic workhorse: "for complex agentic coding and enterprise work." The
tier below Fable 5 on capability and half its price; 1M context is **standard** (the
seed inventory's "ships a 1M variant" phrasing is stale — the docs list 1M as the base
window, verified 2026-07-31).

## The layer-1 axes

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | Anecdotal-positive from heavy orchestration use (see Role) — no measured figure |
| Long-horizon coherence | Anecdotal-positive: multi-hour deep-dive/experiment sessions in this repo's history ran on it without derailment; not instrumented |
| Usable context (vs advertised) | 1M advertised; sessions here run with summarization long before the raw window binds, so unprobed |
| Cost per completed task | · (exp-01's cost data measured *framework* overhead on this model, not the model itself) |
| Release mode & access routes (1b) | API-only; all four cloud routes. `effort` defaults `high` on Claude API + Claude Code |

## Role in this repo's work

- **Exp-01's arm model**: both GSD and plain arms ran on Opus per the original standing
  machine rule ([`experiments/01-gsd-vs-plain/`](../../experiments/01-gsd-vs-plain/README.md))
  — superseded by Sonnet 5 for exp-02+ (standardization decision, 2026-07-28).
- The machine's designated subagent tier for substantive analysis/planning work, and
  the orchestrating model for most of this repo's session history through 2026-07-30.
- Its **May 2026 knowledge cutoff** — newer than Fable 5's — is occasionally
  load-bearing for a repo that studies tools released through mid-2026: less of the
  survey territory is post-cutoff for Opus than for the flagship.

## Surprises

1. **The workhorse knows more recent facts than the flagship** (May vs Jan 2026
   cutoff). Capability tiering and knowledge recency are independent axes — worth
   remembering when choosing a model to *survey recent tools* vs to *reason hard*.

## Open questions

- Exp-01 vs exp-02 will eventually give a loose Opus-vs-Sonnet contrast on similar
  task shapes (different tasks, so indicative only — the cross-experiment caveat in
  the exp-02 prereg applies).
