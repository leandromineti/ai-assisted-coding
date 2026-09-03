---
name: qwen3.8-flash
category: 1
maker: Alibaba (Qwen team)
url: https://www.qwencloud.com/models/qwen3.8-flash
license: "not published for the SERVED model — no Hugging Face repo carries the name `qwen3.8-flash` (Qwen org search, 2026-08-27: Qwen3.8-Flash-Next, -Next-FP8, -27B, -27B-FP8, -2.4T-A95B, and nothing else). The upstream experimental preview it is built on, Qwen/Qwen3.8-Flash-Next, is `qwen-community-1.0` — a third license inside one model family (cf. qwen3-coder-next's Apache-2.0 and qwen3.8-max's bespoke terms)"
access: closed-source   # JUDGMENT CALL, see § Weights — the served model's weights are not published; its upstream preview's are
model_id: qwen3.8-flash (API, QwenCloud); upstream weights Qwen/Qwen3.8-Flash-Next (+ FP8)
release_date:
  date: 2026-08-26
  stage: not-stated
  note: "the QwenCloud changelog entry prints 'August 26, **2025**' — a first-party TYPO, not a fact: it sits at the TOP of a strictly descending list whose next entry is 2026-08-24, and QwenCloud itself only launched 2026-05-26, so a 2025 release is impossible on it. Day and month are taken from the entry, the year from the list it sits in; recorded 2026-08-26 (checked 2026-08-27). No stage word — the same changelog says 'General Availability' for wan3.0-video two days earlier, so the omission is a choice"
context_window: 1000000
max_output: 131072   # docs print exact figures for this model: "1,000,000 tokens" context, "131,072 tokens" output, 262,144 max thinking tokens; the model page's limits row shows max input 991K, 983K in thinking mode
pricing:
  input: 0.15         # USD per MTok — base list rate (see the registry's rule)
  output: 0.47
  currency: USD
  regime: flat
  note: "$0.15 / $0.47 per MTok (model page, verified 2026-08-27) — HALF DeepSeek V4 Flash's off-peak input rate and the cheapest model in this sweep. Widely reported third-party as $0.16 input; the first-party page says $0.15, and the page is what this row records"
knowledge_cutoff:
  date: null          # the limit date on training data
  basis: not-stated
  note: "not stated on any surface checked 2026-08-27: QwenCloud model page, the platform changelog entry, the docs' latest-model page, and the Hugging Face card for the upstream Qwen/Qwen3.8-Flash-Next"
model_features:   # nested per ADR-0014; reasoning keys split per ADR-0040
  reasoning: true
  reasoning_type: default-on   # docs, verbatim: "Thinking mode is enabled by default" + "To disable thinking entirely, set `enable_thinking=false` — the model answers directly"
  reasoning_effort: "levels:low/medium/xhigh@xhigh"   # docs: "`xhigh` (default)" / medium / low, and "`max` and `high` are automatically mapped to `xhigh`" — an alias mapping no other model here publishes
  prompt_caching: "implicit cache read $0.016 per MTok (≈0.107x of input); explicit cache creation $0.20 (1.33x) + explicit cache read $0.016 per MTok. Described as storing 'shared prefixes for long-context requests'; no TTL and no breakpoint surface stated (2026-08-27)"
  batch_discount: "checked and absent — OBSERVED 2026-08-31: batch creation fails validation with `model_not_found`: 'The provided model 'qwen3.8-flash' is not supported by the Batch API' (issue #42 probe; failed validation bills nothing). This RESOLVES the two-surface disagreement recorded 2026-08-27 — the batch guide's supported-model list (older qwen-max/plus/flash/turbo ids only) was right, and the model page's own Batch card was wrong for this model. The platform batch discount itself is 50% of real-time, 24h window — just not for this model"
  fast_mode: false   # checked and absent: QwenCloud's Prime Mode ("TPS is 1.5~2x that of the standard API") is the platform's throughput mode, and its supported-models list excludes this model (glm-5.2-fast-preview and wan3.0-video-prime only; verified 2026-08-27)
  stop_sequence_honesty: "ambiguous — OBSERVED 2026-09-03: stop-honored truncation before the trigger word, but the openai_compat family's shared stop finish value matches the no-stop control's own finish reason — text comparison only, cell_id:`qwen3.8-flash--stop-truncation--triggering--default`, probe_id:`qwen3.8-flash--stop-truncation--triggering--default--d1ae15ef`, promoted ADR-0050."
  seed_determinism: "0/5 same-seed pairs (varies) — OBSERVED 2026-09-03: qwen3.8-flash's seed field is accepted-unverified at the contract sweep; five same-seed repeat calls produced five distinct outputs, cell_id:`qwen3.8-flash--seed--42--default`, probe_id:`qwen3.8-flash--seed--42--default--r1--714d17f5`, promoted ADR-0050."
  sampling_repeatability: "0/4 repeat pairs (varies) — OBSERVED 2026-09-03: qwen3.8-flash accepts an explicit temperature:0 value in default mode — a genuine temperature:0 test, not a substitute; all five repeat calls completed naturally with five distinct outputs, cell_id:`qwen3.8-flash--temperature--0--default`, probe_id:`qwen3.8-flash--temperature--0--default--r1--660c8774`, promoted ADR-0050."
  multi_candidate_delivery: "rejected — OBSERVED 2026-09-03: a request for 2 candidates was rejected outright in default mode, the same documented thinking-mode conditionality as qwen3.8-max, cell_id:`qwen3.8-flash--n--2--default`, probe_id:`qwen3.8-flash--n--2--default--8df7372d`, promoted ADR-0050."
  logprobs_delivery: "accepted-honored — OBSERVED 2026-09-03: this REVISES Phase 11's own contract classification (probe qwen3.8-flash--logprobs--true--default--04bf05c1, read accepted-ignored, 0 token entries found) — the BHV-05 reverify at a larger, non-masking budget chosen precisely because the first reading might have been budget-confounded found 39 real per-token entries with alternatives honored, and per methodology rule 1a this behavioral result SUPERSEDES the earlier, budget-confounded contract reading rather than sitting beside it as an equally-weighted alternative, cell_id:`qwen3.8-flash--logprobs-reverify--combined--default`, probe_id:`qwen3.8-flash--logprobs-reverify--combined--default--4543428e`, promoted ADR-0050."
  service_tier_contract: "response-absent — OBSERVED 2026-09-03: `service_tier` is accepted at the presence probe but not echoed back at the requested value (accepted-ignored), probe_id:`qwen3.8-flash--service-tier--auto--default--db747a31`; the value-enum row fires here (openai_compat family) — all 4 values accepted-ignored uniformly, probe_id:`qwen3.8-flash--openai-service-tier-values--auto--default--db747a31`; the BHV-06 tier audit is the third, genuinely distinct response-side state — no service-tier field appears in the response at all, a real absence rather than a nesting the presence probe alone cannot see, cell_id:`qwen3.8-flash--service-tier-audit--omitted--default`, probe_id:`qwen3.8-flash--service-tier-audit--omitted--default--dea5ae2d`, promoted ADR-0050."
checked: 2026-08-27
depth: stub
---

# Qwen3.8-Flash

The cheap end of the Qwen3.8 line and, at **$0.15 / $0.47 per MTok**, the cheapest model
tracked in this repo — roughly a thirteenth of qwen3.8-max's input rate for the same
advertised 1M context, the same three-level reasoning dial, and the same multimodal input
(image, text, video in; text out). Released three weeks after the flagship, on 2026-08-26.

What makes it worth a report beyond the price: it is the **production form of an
architecture preview**. Its upstream, `Qwen/Qwen3.8-Flash-Next`, is a 125B-total /
**6B-activated** MoE carrying two structures the Qwen team frames as previews of the next
generation — a **51B n-gram embedding layer** and a 4B MTP module. The cheap tier is where
the next architecture ships first, which is not where this repo would have looked for it.

## Weights: why this row says `closed-source`

The most revisable cell in this report, so the reasoning is stated rather than assumed.

- No Hugging Face repo carries the served name. The Qwen org publishes `Qwen3.8-Flash-Next`
  and its FP8 variant, `Qwen3.8-27B` (+FP8), and `Qwen3.8-2.4T-A95B` — checked 2026-08-27.
- The upstream card's own framing is *"Qwen3.8-Flash is the official version based on
  Qwen3.8-Flash-Next with more production features."* **Based on** is not **is**.
- Contrast the sibling: qwen3.8-max's weights card says its repo holds the post-trained
  model behind the commercial service. That is an identity claim, and it is why that report
  says `open-weights` and this one does not.

So what the public can obtain is a *related experimental preview*, not this model. Anyone
reading `closed-source` here should read this section with it — 125B weights in the same
lineage are downloadable, under `qwen-community-1.0`. Flip the cell the day a
`Qwen/Qwen3.8-Flash` repo exists, and read the license before calling it open.

This is the second Qwen3.8 report in a row where `access` (ADR-0044) turns out to be
coarser than the situation: one enum value covers "these exact weights are published",
"the post-trained base is published and the API adds features", and "a preview relative is
published". The distinction is currently carried by prose in two reports, which is where a
future axis usually starts.

## The category-1 axes (taxonomy §1)

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | · — the docs advertise multimodal agent use; nothing measured here |
| Long-horizon coherence | · |
| Usable context (vs advertised) | 1,000,000 advertised and printed exactly (not rounded, unlike the flagship's page); addressable input is **991K**, and **983K** once thinking is on. Upstream weights are *"262,144 natively and extensible up to 1,000,000 tokens"* — so, as with qwen3.8-max, the 1M is a serving configuration over a 256K-native model |
| Cost per completed task | **The cheapest list price in the sweep**, and the one where the reasoning default matters most: `xhigh` by default on a model bought for cost means realized cost can sit far above the $0.15 headline. A cheap model that thinks hard by default is not automatically a cheap model |
| Release mode & access routes (1b) | First-party API on QwenCloud; the served weights are not published, the upstream preview's are (§ Weights). No second first-party route found |

## Reasoning surface

All three cells verified against the docs' latest-model page, 2026-08-27:

- *"Thinking mode is enabled by default."* → `default-on`.
- *"To disable thinking entirely, set `enable_thinking=false` — the model answers
  directly"* → toggleable, which is what separates `default-on` from `always-on`.
- *"Use `reasoning_effort` to control reasoning intensity: `xhigh` (default) … `medium` …
  `low`"* → `levels:low/medium/xhigh@xhigh`, joining Kimi K3, GLM-5.3 and its own flagship
  sibling in defaulting to the most expensive level it offers. That is now **four models,
  three makers, all non-Western** — while every Western model in the sweep defaults lower
  (`@high` or `@medium`). What was a Kimi curiosity in July is a regional pattern in August.

One detail no other model in the sweep publishes: *"`max` and `high` are automatically
mapped to `xhigh`."* The API silently accepts two level names it does not implement and
promotes them to the most expensive one. A harness that sends OpenAI's `high` — a
perfectly reasonable default — gets `xhigh` and the bill that comes with it, with no error
to notice. That is conclusion 15's failure mode (harnesses track models by name, and API
drift disarms them) arriving through a *compatibility alias* rather than a rejection.

**The silence is now observed** (2026-08-31, issue #42 thin-client probe):
`reasoning_effort: "high"` was accepted with no error, and the response carries **no
effort field of any kind** — no echo of what was requested, no report of what ran, in
either the message or `usage` (which does itemize `reasoning_tokens`). The docs state
the mapping; the probe establishes that nothing in the response contract lets a caller
detect it. Fully silent, as feared.

## Role in this repo's work

None run. The obvious use is as a cheap arm in the rig: it is the only model in the sweep
whose list price makes a many-run experiment trivially affordable, and the only one where
`reasoning_effort` can be swept across three levels for less than a single Opus run costs.

## Surprises

1. **The next architecture shipped in the cheap tier, not the flagship.** The n-gram
   embedding layer and MTP module are framed as Qwen4 previews and appear in the $0.15
   model, while the 2.4T flagship is conventional MoE. Cost tiers are usually where
   vendors are most conservative.
2. **A first-party changelog with the wrong year on its newest entry** ("August 26,
   **2025**"). Every date in this repo is supposed to come from a first-party surface;
   this is the first time such a surface was internally inconsistent enough to need
   *reconstruction* from its own ordering rather than transcription.
3. **Silent level aliasing.** `max` and `high` are accepted and promoted to `xhigh`. Every
   other vendor here either implements the level or rejects it.
4. **Third-party consensus was one cent off.** Multiple outlets report $0.16 input; the
   vendor's page says $0.15. Small, and exactly the kind of drift that makes a repo of
   copied numbers worthless — the reason rule 1 exists.

## Open questions

- Do the served weights ever get published under this name, or does `-Next` remain the
  only downloadable form? That answer flips the `access` cell.
- ~~Does the Batch API accept the `qwen3.8-flash` id? Same unresolved two-surface
  disagreement as the flagship.~~ **Resolved 2026-08-31 identically to the flagship's**:
  batch validation fails with `model_not_found` — *"The provided model 'qwen3.8-flash'
  is not supported by the Batch API."* The batch guide was right, the model page's Batch
  card wrong; cell updated (issue #42 probe, $0).
- Is the `high` → `xhigh` promotion visible anywhere in the response (a returned effort
  field), or is it entirely silent? If silent, it belongs in conclusion 15's evidence.
- Cheapest-model claim: worth re-checking against DeepSeek V4 Flash's off-peak window,
  where a time-of-day rate can undercut a flat one for a given schedule.
