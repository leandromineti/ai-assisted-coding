---
name: deepseek-v4
layer: 1
vendor: DeepSeek
url: https://api-docs.deepseek.com/quick_start/pricing
license: "unverified for V4 weights (HF org page shows no license in the listing checked; do not assume the V2/V3-era licenses carry over)"
open_source: true
model_id: deepseek-v4-pro / deepseek-v4-flash (API); deepseek-ai/DeepSeek-V4-Pro, DeepSeek-V4-Flash (+ -Base, -DSpark variants) on HF
release_mode: both   # first-party API and published weights, verified on both surfaces 2026-07-31
context_window: 1000000
max_output: 384000
pricing: "Pro $0.435 / $0.87 per MTok (cache-hit input $0.003625); Flash $0.14 / $0.28 (cache-hit $0.0028) (verified 2026-07-31)"
knowledge_cutoff: unverified
checked: 2026-07-31
depth: stub
---

# DeepSeek V4 (Pro / Flash)

DeepSeek's fourth-generation line, resolving the seed inventory's `unverified` row:
the current API is **deepseek-v4-pro** and **deepseek-v4-flash**, both 1M context,
both with **384K max output** — 3× the largest Western max-output in this sweep — and
**weights published** on HF (Pro at 1.6T-scale, Flash smaller, each with Base and
DSpark variants; per-model licenses unverified). Both modes ship thinking-by-default
with a non-thinking toggle, JSON output, and tool calls.

## The layer-1 axes

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | · (supported; unmeasured) |
| Long-horizon coherence | · |
| Usable context (vs advertised) | 1M advertised; unprobed |
| Cost per completed task | The sweep's outlier: Flash output at $0.28/MTok is **~90× cheaper than Fable 5 output**; Pro at $0.87 is ~29× cheaper. Cache-hit input at fractions of a cent effectively makes cached context free. If per-task quality holds anywhere near frontier, the cost axis isn't a tradeoff here — it's a different sport |
| Release mode & access routes (1b) | **Both** — first-party API *and* open weights, the only line in this sweep with full route spread plus frontier-scale claims. Concurrency tiering (Flash 2500 vs Pro 500) is an access-route fact APIs elsewhere hide |

## Role in this repo's work

None run. Appears in llm-coding-benchmark's roster (through opencode's `default.txt`
prompt — one of the models the upstream issue #12 flagged as *not* getting a bespoke
prompt, relevant if its benchmark showings there are re-read).

## Surprises

1. **384K max output** — an order-of-magnitude statement about what the vendor thinks
   agents do (generate a lot, iterate less?). Every other vendor caps at 128K.
2. **Cache-hit pricing near zero** ($0.0028/MTok) — the most aggressive prompt-cache
   economics in the sweep; H5's cache-discipline principle has very different stakes
   at this price point (violating cache warmth costs ~50× more than honoring it).
3. The R2 that dominated 2025 rumor cycles still doesn't exist; the actual shipping
   line is V4. Rumor-tracking and inventory-keeping are different activities — this
   row stayed honest by staying `unverified` until today.

## Open questions

- V4 weights licenses — read them on HF before any "open" claim stronger than
  "downloadable".
- HF shows Flash at 158B (with a 292B Flash-Base) — third-party writeups say 284B
  total / 13B active. Reconcile from the model card/config before citing any
  parameter count.
- At ~1/30th frontier pricing with 1M context: what does per-completed-task cost look
  like on this repo's task shapes? The rig could answer this cheaply — a natural
  future arm.
