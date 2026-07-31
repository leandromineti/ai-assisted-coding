---
name: grok-4-5
layer: 1
vendor: xAI
url: https://docs.x.ai/docs/models
license: proprietary
open_source: false
model_id: grok-4.5
release_mode: api-only
context_window: 500000
max_output: unverified   # not stated on the models page checked
pricing: "$2 / $6 per MTok for prompts <200k tokens; $4 / $12 above; cached input $0.30–$0.60 (verified 2026-07-31)"
knowledge_cutoff: "Feb 1, 2026"
checked: 2026-07-31
depth: stub
---

# Grok 4.5

xAI's recommended model "for code and chat" (released 2026-07-08 on the 1.5T-param V9
base, per the 2026-07-28 verified sweep). The layer-1↔2 story attached to it is why it
matters to this repo: **trained on real Cursor session data** — the sharpest instance
of the harness-as-training-data-instrument pattern in the taxonomy's boundary-rule
note. No EU availability at launch (2026-07-28 check; not re-verified today).

## The layer-1 axes

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | · — though the training-data story implies optimization for *harness-shaped* interaction specifically |
| Long-horizon coherence | · |
| Usable context (vs advertised) | 500k — **half of the 1M its own cheaper siblings offer** (Grok 4.3 and 4.20: 1M at $1.25/$2.50). The flagship trades window for capability, inverting the usual assumption |
| Cost per completed task | The cross-cutting note records xAI's own pitch: ~60% cheaper per token than frontier tier, ~half the per-task cost in Codex — vendor claim, unmeasured here |
| Release mode & access routes (1b) | API-only (`console.x.ai`); tiered pricing at the 200k boundary like Google |

## Role in this repo's work

None as a model. As a *case*, load-bearing: it anchors the taxonomy's vertical-
integration story (Cursor acquisition → session data → Grok 4.5) and the layer-2
index's open question about whether telemetry-tuned models produce a durable
advantage.

## Surprises

1. **The flagship has the smallest window in its own lineup** (500k vs siblings' 1M)
   — capability tier and context tier are independent axes at xAI, and they chose
   capability.
2. A hermes-style per-family patch targets Grok in hermes' prompt appendices (grouped
   with GPT/Codex for execution-discipline failures) — a third-party read on its
   *behavioral* family resemblance: harnesses treat Grok as GPT-shaped.

## Open questions

- Does Cursor-session training measurably improve performance *inside Cursor* vs
  other harnesses — the cleanest possible test of the layer-1↔2 integration thesis,
  if anyone can run it?
- EU availability since launch? (Unchecked since 2026-07-28.)
