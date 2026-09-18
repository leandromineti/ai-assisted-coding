---
name: deepseek-v4
category: 1
maker: DeepSeek
url: https://api-docs.deepseek.com/quick_start/pricing
license: "MIT — verified 2026-09-18 on HF: `license: mit` in the card metadata of DeepSeek-V4-Pro, -V4-Flash, -V4-Flash-DSpark and -V4.1-Flash, and the card body reads 'This repository and the model weights are licensed under the MIT License'; the two -Base repos ship no README (404) but the same 1084-byte LICENSE file ('MIT License, Copyright (c) 2023 DeepSeek'). The 2026-08-17 'no license in the listing' was a card-metadata absence on the Base repos, not a licensing absence"
access: open-weights
model_id: "deepseek-v4-pro / deepseek-flash (API — since 2026-09-10 `deepseek-flash` is served by DeepSeek-V4.1-Flash, and the legacy ids `deepseek-v4-flash` / `deepseek-v4-flash-vision-exp` are 'still accepted, but the corresponding models have been retired', routing there; the pricing page names the served versions DeepSeek-V4.1-Flash and DeepSeek-V4-Pro-0813); HF: deepseek-ai/DeepSeek-V4-Pro, DeepSeek-V4-Flash (+ -Base, -DSpark variants), DeepSeek-V4.1-Flash (re-verified 2026-09-18 — the Pro half of this report is current, the Flash half is superseded in place)"
release_date:
  date: 2026-04-24
  stage: Preview
  note: "FIRST availability is the preview ('DeepSeek-V4 Preview is officially live & open-sourced'); GA followed 2026-08-13 under the vendor's own title 'GA Release' — the sweep's only explicit preview→GA arc, 3.5 months (verified 2026-08-17)"
context_window: 1000000
max_output: 384000
pricing:
  input: 1.32          # USD per MTok — base list rate (see the registry's rule)
  output: 3.96
  currency: USD
  regime: time-of-day
  note: "peak/off-peak — off-peak is 50% of peak; peak is 01:00–04:00 + 06:00–10:00 UTC and, since the 2026-09-10 repricing, 'Monday through Friday (all other hours are off-peak)' — weekends are now wholly off-peak: Pro $1.32 / $3.96 peak, $0.66 / $1.98 off-peak (unchanged since 2026-08-16, re-verified 2026-09-18; the 2026-09-10 announcement that Pro would be phased out on 2026-09-14 was reversed on the pricing page itself: 'we have decided to continue providing API services for DeepSeek V4 Pro after September 14, 2026, with the billing method remaining unchanged'); Flash (now V4.1-Flash) $0.30 / $1.20 peak, $0.15 / $0.60 off-peak per MTok, effective 2026-09-10 04:00 UTC (was $0.44 / $1.32 and $0.22 / $0.66, verified 2026-08-17; the flat launch rates were recorded 2026-07-31)"
knowledge_cutoff:
  date: null          # the limit date on training data
  basis: not-stated
  note: "not disclosed by vendor — no cutoff on the HF model card or either launch/GA announcement (checked 2026-08-17); re-checked 2026-09-18 across the pricing, thinking-mode, KV-cache, rate-limit, FAQ, updates and four news pages plus the V4-Pro, V4-Flash and V4.1-Flash HF cards (grepped cutoff / knowledge cut / training cut / trained up to / data up to — zero hits; the nearest statement is a corpus SIZE, '45T tokens', on the V4.1-Flash card); third-party 'April 2026' claims are ship-date inference"
model_features:   # nested per ADR-0014 (2026-08-19); reasoning keys split per ADR-0040
  reasoning: true
  reasoning_type: default-on   # on by default, toggled per request via thinking.type enabled/disabled — default-on half OBSERVED 2026-08-31 (issue #42 probe): reasoning_content returned with no params
  reasoning_effort: "levels:none/low/high/max@high"   # re-verified 2026-09-18: the API reference now enumerates 'Possible values: [none, low, high, max]' with 'none disables thinking mode' — a second, effort-channel off switch beside thinking.type (the Sol shape), added to the enum this sweep; the coercion table is now documented in full: minimal→low, medium→high, xhigh→high, ultra→max; same mapping Pro and Flash
  prompt_caching: "automatic on-disk, zero config, no TTL knob (best-effort expiry, 'hours to a few days'); usage exposes a DUAL cache surface, observed 2026-08-31: DeepSeek's own prompt_cache_hit_tokens/prompt_cache_miss_tokens alongside OpenAI-style prompt_tokens_details.cached_tokens; cache-hit input Pro $0.044 peak / $0.022 off-peak (unchanged), Flash $0.006 / $0.003 per MTok since 2026-09-10 (was $0.014 / $0.007); re-verified 2026-09-18 — the dual usage surface is now DOCUMENTED in the API reference, not just observed, and the KV-cache page adds a V4.1-era matching rule: 'Due to the Sliding Window Attention mechanism ... each cached prefix is an independent, complete unit. A subsequent request can only hit the cache if it fully matches a cache prefix unit'"
  batch_discount: "no batch API (re-verified 2026-09-18: zero 'batch' hits across the fetched api-docs pages) — time-of-day pricing instead: every rate halves off-peak, which is all hours outside 01:00–04:00 and 06:00–10:00 UTC on weekdays, and all of Saturday and Sunday since 2026-09-10"
  fast_mode: false   # checked and absent: the pricing page's only dimensions are peak/off-peak hours and cache hit/miss — no speed tier (verified 2026-08-27; re-verified 2026-09-18 across pricing, rate-limit, updates, news, FAQ and token-usage pages — no priority / flex / fast / service-tier vocabulary)
  stop_sequence_honesty: "ambiguous — OBSERVED 2026-09-03: stop-honored truncation before the trigger word, but the openai_compat family's shared stop finish value matches the no-stop control's own finish reason — text comparison only, cell_id:`deepseek-v4--stop-truncation--triggering--default`, probe_id:`deepseek-v4--stop-truncation--triggering--default--970252c9`, promoted ADR-0050."
  seed_determinism: "0/5 same-seed pairs (varies) — OBSERVED 2026-09-03: deepseek-v4's seed field is accepted-unverified at the contract sweep; five same-seed repeat calls produced five distinct outputs, cell_id:`deepseek-v4--seed--42--default`, probe_id:`deepseek-v4--seed--42--default--r1--b26d4485`, promoted ADR-0050."
  sampling_repeatability: "0/4 repeat pairs (varies) — OBSERVED 2026-09-03: deepseek-v4 accepts an explicit temperature:0 value in default mode — a genuine temperature:0 test, not a substitute; all five repeat calls completed naturally with five distinct outputs, cell_id:`deepseek-v4--temperature--0--default`, probe_id:`deepseek-v4--temperature--0--default--r1--16f2fb80`, promoted ADR-0050."
  multi_candidate_delivery: "rejected — OBSERVED 2026-09-03: a request for 2 candidates was rejected outright, cell_id:`deepseek-v4--n--2--default`, probe_id:`deepseek-v4--n--2--default--53194c57`, promoted ADR-0050."
  logprobs_delivery: "accepted-honored — OBSERVED 2026-09-03: `logprobs` returns real per-token content, already unambiguous at the contract sweep with no reverify needed, probe_id:`deepseek-v4--logprobs--true--default--3e9e0cfd`, promoted ADR-0050."
  service_tier_contract: "response-absent — OBSERVED 2026-09-03: `service_tier` is accepted at the presence probe but not echoed back at the requested value (accepted-ignored), probe_id:`deepseek-v4--service-tier--auto--default--1d5f1f91`; the value-enum row fires here (openai_compat family) — all 4 values accepted-ignored uniformly, probe_id:`deepseek-v4--openai-service-tier-values--auto--default--1d5f1f91`; the BHV-06 tier audit is the third, genuinely distinct response-side state — no service-tier field appears in the response at all, a real absence rather than a nesting the presence probe alone cannot see, cell_id:`deepseek-v4--service-tier-audit--omitted--default`, probe_id:`deepseek-v4--service-tier-audit--omitted--default--82ca9bf4`, promoted ADR-0050."
checked: 2026-09-18   # full docs-route re-verification (staleness sweep); the six wire-behavior OBSERVED cells keep their own 2026-09-03 dates
depth: stub
---

# DeepSeek V4 (Pro / Flash)

DeepSeek's fourth-generation line, resolving the seed inventory's `unverified` row:
the current API is **deepseek-v4-pro** and **deepseek-v4-flash**, both 1M context,
both with **384K max output** — 3× the largest Western max-output in this sweep — and
**weights published** on HF (Pro at 1.6T-scale, Flash smaller, each with Base and
DSpark variants; per-model licenses unverified). *Update 2026-09-18:* the Flash half
is superseded — since 2026-09-10 the API id is `deepseek-flash`, served by
**DeepSeek-V4.1-Flash** (552B backbone, 8B active per token at prefill / 16B at
decode, native vision, a new "Causal Encoder–Decoder" architecture); the V4-Flash ids
still resolve but the models are retired. Pro survives: its phase-out was announced
2026-09-10 and reversed on the pricing page before the 2026-09-14 date, "in response
to user demand". Licenses are MIT throughout (frontmatter). Both modes ship reasoning-on by default
with a per-request off switch (`thinking.type`), JSON output, and tool calls.

## The category-1 axes

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | · (supported; unmeasured) |
| Long-horizon coherence | · |
| Usable context (vs advertised) | 1M advertised; unprobed |
| Cost per completed task | Still the sweep's outlier, now time-of-day-dependent (repriced 2026-08-16, Flash again 2026-09-10): Flash output $0.60–1.20/MTok is ~42–83× cheaper than Fable 5 output; Pro $1.98–3.96 is ~13–25×. The 2026-07-31 figures ($0.28 / $0.87 flat) were launch promo rates, ~2–3× lower than today's. Cache-hit input remains fractions of a cent. The "different sport" framing survives the repricing, attenuated |
| Release mode & access routes (1b) | **Both** — first-party API *and* open weights, the only line in this sweep with full route spread plus frontier-scale claims. Concurrency tiering (Flash 2500 vs Pro 500) is an access-route fact APIs elsewhere hide |

## Reasoning surface

What the three reasoning cells rest on, verified 2026-08-17 (carried verbatim from the
free-text `thinking`/`effort_control` cells those keys replaced, ADR-0040): *"on by
default; toggled per-request via `thinking.type` enabled/disabled — one model id, a
parameter, not a variant; thinking mode rejects temperature/top_p/penalties"* and
*"`reasoning_effort`: low/high/max, default high; foreign values 'medium'/'xhigh'
silently coerced to high; identical mapping Pro and Flash."*

The sampling-parameter rejection is the part a harness feels: turning reasoning on here
invalidates a temperature setting elsewhere in the same request. *Corrected 2026-09-18
from the thinking-mode page and the API reference:* "rejects" was half right —
temperature and the two penalties "will not trigger an error but will also have no
effect" (silently ignored), while `top_p` is **clamped**, not ignored: "values below
0.95 are raised to 0.95; in non-thinking mode it is fixed at 1.0". The same read added
`none` to the effort enum (frontmatter) and confirmed the wire-observed `temperature:0`
acceptance in the `sampling_repeatability` cell is the documented behavior — accepted
and inert.

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
   like. (2026-09-18: the window is now weekdays only — weekends are wholly off-peak.)
5. **A deprecation announced and reversed on the same page, inside four days**
   (2026-09-18 read): the 2026-09-10 news post phased V4-Pro out from 2026-09-14 in
   favor of routing to V4.1-Flash "until V4.1-Pro launches"; the pricing page's
   footnote now keeps Pro alive "in response to user demand", billing unchanged. The
   flagship tier is demand-held, and a V4.1-Pro is named as forthcoming — a dated
   sighting, not a prediction, since the vendor gave no date.

## Open questions

- ~~V4 weights licenses — read them on HF before any "open" claim stronger than
  "downloadable".~~ **Resolved 2026-09-18: MIT** on every V4/V4.1 repo, from the card
  metadata, the card body and the LICENSE file itself (frontmatter).
- ~~HF shows Flash at 158B (with a 292B Flash-Base) — third-party writeups say 284B
  total / 13B active. Reconcile from the model card/config before citing any
  parameter count.~~ **Resolved 2026-09-18, and the lesson is a count carrying its
  measure:** the vendor's own card states "DeepSeek-V4-Pro with 1.6T parameters (49B
  activated) and DeepSeek-V4-Flash with 284B parameters (13B activated)" — the
  "third-party" 284B/13B was the vendor's number all along. The 292B is HF's
  `safetensors.total` for Flash-Base (292,021,347,282, all FP8), a storage count on a
  different measure; no repo reports 158B today — the nearest is the I8-quantized
  Flash-DSpark at 165,265,454,782. V4.1-Flash restates the gap and explains it: 552B
  backbone + "196B parameters" of Engram conditional memory ≈ 748B against a
  safetensors total of 763,205,315,794.
- At ~1/30th frontier pricing with 1M context: what does per-completed-task cost look
  like on this repo's task shapes? The rig could answer this cheaply — a natural
  future arm.
