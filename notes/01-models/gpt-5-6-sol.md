---
name: gpt-5-6-sol
layer: 1
vendor: OpenAI
url: https://developers.openai.com/api/docs/models
license: proprietary
open_source: false
model_id: gpt-5.6-sol (alias gpt-5.6); siblings gpt-5.6-terra, gpt-5.6-luna
release_mode: api-only
context_window: 1050000
max_output: 128000
pricing: "Sol $5 / $30 per MTok; Terra $2 / $12; Luna $0.20 / $1.20 (verified 2026-07-31)"
knowledge_cutoff: "Feb 16, 2026 (all three tiers)"
checked: 2026-07-31
depth: stub
---

# GPT-5.6 Sol (and the 5.6 family)

OpenAI's frontier tier — "frontier model for complex professional work" — atop a
three-tier family sharing one 1.05M-token window and one Feb 2026 cutoff: **Sol**
(flagship, $5/$30), **Terra** ("intelligence and cost", $2/$12), **Luna**
("cost-sensitive workloads", $0.20/$1.20). The naming moved from version numbers to
celestial tiers — same structural move as Anthropic's capability ladder, made nominal.

**GPT-5.5 status resolved (2026-07-31):** no longer on OpenAI's current models page —
superseded by the 5.6 family. The Terminal-Bench 2.1 figures the layer index cites
(Codex CLI + GPT-5.5, 83.4%) now describe a *retired* model; the benchmark-staleness
warning in the index applies to its own snapshot.

## The layer-1 axes

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | · (vendor lists Functions/Web search/File search/Computer use on all tiers) |
| Long-horizon coherence | · |
| Usable context (vs advertised) | 1.05M advertised — the odd 50k over the round number suggests an exact power-of-two budget (2^20 ≈ 1.049M); unprobed |
| Cost per completed task | · — the 25× Sol/Luna price spread within one family is the widest in the sweep; where each tier's per-task crossover sits is unmeasured |
| Release mode & access routes (1b) | API-only; the models driving Codex CLI/cloud (layer-2 pairing) |

## Role in this repo's work

None directly — appears as the benchmark counterpart in the layer-2 shelf (Codex CLI
pairings) and as Kimi K3's claimed comparison target. No repo work has run on it.

## Surprises

1. **A 25× intra-family price spread** (Sol $30 vs Luna $1.20 output) under identical
   context and cutoff — the vendor is pricing capability tiers, not infrastructure.
2. GPT-5.5's quiet disappearance between benchmark publication and this check —
   leaderboard citations now point at a model you can't buy.

## Open questions

- What actually differs across Sol/Terra/Luna — distillation tiers of one base, or
  different models? (OpenAI discloses nothing.)
- Where does codex-the-model line fit now — the models page lists no codex-specific
  SKUs with specs; are Codex surfaces driven by these same tiers?
