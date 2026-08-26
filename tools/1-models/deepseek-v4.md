---
name: deepseek-v4
category: 1
vendor: DeepSeek
url: https://api-docs.deepseek.com/quick_start/pricing
license: "unverified for V4 weights (HF org page shows no license in the listing checked; do not assume the V2/V3-era licenses carry over)"
open_source: true
model_id: deepseek-v4-pro / deepseek-v4-flash (API); deepseek-ai/DeepSeek-V4-Pro, DeepSeek-V4-Flash (+ -Base, -DSpark variants) on HF
release_mode: both   # first-party API and published weights, verified on both surfaces 2026-07-31
released: "Preview 2026-04-24 ('DeepSeek-V4 Preview is officially live & open-sourced') → GA 2026-08-13 (vendor's own title: 'GA Release') — the sweep's only explicit preview→GA arc, 3.5 months (verified 2026-08-17)"
context_window: 1000000
max_output: 384000
pricing:
  input: 1.32          # USD per MTok — base list rate (see the registry's rule)
  output: 3.96
  currency: USD
  regime: time-of-day
  note: "peak/off-peak since 2026-08-16 16:00 UTC — off-peak is 50% of peak (peak 01:00–04:00 + 06:00–10:00 UTC): Pro $1.32 / $3.96 peak, $0.66 / $1.98 off-peak; Flash $0.44 / $1.32 peak, $0.22 / $0.66 off-peak per MTok (verified 2026-08-17; supersedes the flat launch rates recorded 2026-07-31)"
knowledge_cutoff:
  knowledge: null       # YYYY-MM or YYYY-MM-DD; null when none is published
  training_data: null
  basis: not-stated
  note: "not disclosed by vendor — no cutoff on the HF model card or either launch/GA announcement (checked 2026-08-17); third-party 'April 2026' claims are ship-date inference"
model_features:   # nested per ADR-0014 (2026-08-19); values unchanged
  thinking: "on by default; toggled per-request via thinking.type enabled/disabled — one model id, a parameter, not a variant; thinking mode rejects temperature/top_p/penalties"
  effort_control: "reasoning_effort: low/high/max, default high; foreign values 'medium'/'xhigh' silently coerced to high; identical mapping Pro and Flash"
  prompt_caching: "automatic on-disk, zero config, no TTL knob (best-effort expiry, 'hours to a few days'); cache-hit input Pro $0.044 peak / $0.022 off-peak, Flash $0.014 / $0.007 per MTok"
  batch_discount: "no batch API — time-of-day pricing instead: every rate halves off-peak, which is all hours outside 01:00–04:00 and 06:00–10:00 UTC"
checked: 2026-08-17
depth: stub
---

# DeepSeek V4 (Pro / Flash)

DeepSeek's fourth-generation line, resolving the seed inventory's `unverified` row:
the current API is **deepseek-v4-pro** and **deepseek-v4-flash**, both 1M context,
both with **384K max output** — 3× the largest Western max-output in this sweep — and
**weights published** on HF (Pro at 1.6T-scale, Flash smaller, each with Base and
DSpark variants; per-model licenses unverified). Both modes ship thinking-by-default
with a non-thinking toggle, JSON output, and tool calls.

## The category-1 axes

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | · (supported; unmeasured) |
| Long-horizon coherence | · |
| Usable context (vs advertised) | 1M advertised; unprobed |
| Cost per completed task | Still the sweep's outlier, now time-of-day-dependent (repriced 2026-08-16): Flash output $0.66–1.32/MTok is ~38–76× cheaper than Fable 5 output; Pro $1.98–3.96 is ~13–25×. The 2026-07-31 figures ($0.28 / $0.87 flat) were launch promo rates, ~2–3× lower than today's. Cache-hit input remains fractions of a cent. The "different sport" framing survives the repricing, attenuated |
| Release mode & access routes (1b) | **Both** — first-party API *and* open weights, the only line in this sweep with full route spread plus frontier-scale claims. Concurrency tiering (Flash 2500 vs Pro 500) is an access-route fact APIs elsewhere hide |

## Role in this repo's work

None run. Appears in llm-coding-benchmark's roster (through opencode's `default.txt`
prompt — one of the models the upstream issue #12 flagged as *not* getting a bespoke
prompt, relevant if its benchmark showings there are re-read).

## Surprises

1. **384K max output** — an order-of-magnitude statement about what the vendor thinks
   agents do (generate a lot, iterate less?). Every other vendor caps at 128K.
2. **Cache-hit pricing near zero** ($0.0028/MTok at the 2026-07-31 check; $0.007–0.044
   after the 2026-08-16 repricing — still the most aggressive in the sweep). H5's
   cache-discipline principle has very different stakes at this price point (violating
   cache warmth costs ~30–50× more than honoring it).
3. The R2 that dominated 2025 rumor cycles still doesn't exist; the actual shipping
   line is V4. Rumor-tracking and inventory-keeping are different activities — this
   row stayed honest by staying `unverified` until today.
4. **The vendor repriced by time of day, not by endpoint** (2026-08-17): no batch API —
   instead every rate halves during off-peak hours (all hours outside 01:00–04:00 and
   06:00–10:00 UTC). Same 50% number the batch-API vendors offer, but keyed to *when*
   you run, not whether you can wait — a different bet about what agent workloads look
   like.

## Open questions

- V4 weights licenses — read them on HF before any "open" claim stronger than
  "downloadable".
- HF shows Flash at 158B (with a 292B Flash-Base) — third-party writeups say 284B
  total / 13B active. Reconcile from the model card/config before citing any
  parameter count.
- At ~1/30th frontier pricing with 1M context: what does per-completed-task cost look
  like on this repo's task shapes? The rig could answer this cheaply — a natural
  future arm.
