---
name: qwen3.8-max
category: 1
maker: Alibaba (Qwen team)
url: https://www.qwencloud.com/models/qwen3.8-max
license: "qwen3.8-max — a bespoke license, named after the model, shown on the weights repo Qwen/Qwen3.8-2.4T-A95B (checked 2026-08-27); NOT Apache-2.0 like qwen3-coder-next, and not the `qwen-community-1.0` its Flash sibling's upstream carries"
access: open-weights
model_id: qwen3.8-max (API, QwenCloud); weights Qwen/Qwen3.8-2.4T-A95B (+ a served `qwen3.8-2.4t-a95b` id on the same platform since 2026-08-13)
release_date:
  date: 2026-08-03
  stage: not-stated
  note: "QwenCloud's own model-release changelog dates the entry 'August 3, 2026 — qwen3.8-max' and uses no stage word for it. `not-stated` is load-bearing rather than absent here: the SAME changelog writes 'General Availability' for wan3.0-video three weeks later (2026-08-24), so the platform does have stage vocabulary and did not apply it to its flagship (checked 2026-08-27)"
context_window: 1000000
max_output: 131072   # model page prints rounded '1M' context / '131K' out (max input 991K, 983K in thinking mode); the exact 131,072 is what the docs print for the sibling qwen3.8-flash — see § Usable context
pricing:
  input: 2.0          # USD per MTok — base list rate (see the registry's rule)
  output: 6.0
  currency: USD
  regime: flat
  note: "$2 / $6 per MTok, no context tiering on the model page — the same headline pair as Grok 4.5's sub-200k tier, at 2× the context (verified 2026-08-27). A third-party-reported 22:00–08:00 (UTC+8) 50%-off night window is NOT verified first-party: the only discount page that resolves is `qwencloud.com/promo/discount-qwen`, and it is Qwen3.7-Max's, expired 2026-07-31"
knowledge_cutoff:
  date: null          # the limit date on training data
  basis: not-stated
  note: "not stated on any surface checked 2026-08-27: the QwenCloud model page, the platform's model-release changelog entry, and the Hugging Face card for the weights (Qwen/Qwen3.8-2.4T-A95B) are all silent. Third-party 'August 2026' figures are ship-date inference, not the fact"
model_features:   # nested per ADR-0014; reasoning keys split per ADR-0040
  reasoning: true
  reasoning_type: default-on   # OBSERVED 2026-08-31 (issue #42 thin-client probe), closing the cell left deliberately blank 2026-08-27: a request with NO thinking params returned `reasoning_content` (36 reasoning tokens billed), and `enable_thinking: false` returned none — default-on, toggleable, both directions observed. The docs' `Hybrid` classification stands; the DEFAULT was never stated on any first-party surface, so this cell is the sweep's first enum value that rests on a probe rather than a page. See § Reasoning surface.
  reasoning_effort: "levels:low/medium/xhigh@xhigh"   # docs, verbatim: "Example with `qwen3.8-max` (options: `low`, `medium`, `xhigh`; default `xhigh`)"
  prompt_caching: "two priced modes on one model page: implicit cache read $0.25 per MTok (0.125x of input, no opt-in stated), explicit cache creation $2.50 (1.25x) + explicit cache read $0.17 per MTok (0.085x). No TTL and no breakpoint surface stated anywhere checked (2026-08-27)"
  batch_discount: "checked and absent — OBSERVED 2026-08-31: batch creation fails validation with `model_not_found`: 'The provided model 'qwen3.8-max' is not supported by the Batch API' (issue #42 probe; failed validation bills nothing). This RESOLVES the two-surface disagreement recorded 2026-08-27 — the batch guide's supported-model list (older qwen-max/plus/flash/turbo ids only) was right, and the model page's own Batch card was wrong for this model. The platform batch discount itself is 50% of real-time, 24h window — just not for this model"
  fast_mode: false   # checked and absent: QwenCloud's Prime Mode ("TPS is 1.5~2x that of the standard API") is the platform's throughput mode, and its supported-models list excludes this model (glm-5.2-fast-preview and wan3.0-video-prime only; verified 2026-08-27)
  stop_sequence_honesty: "ambiguous — OBSERVED 2026-09-03: stop-honored truncation before the trigger word, but the openai_compat family's shared stop finish value matches the no-stop control's own finish reason — text comparison only, cell_id:`qwen3.8-max--stop-truncation--triggering--default`, probe_id:`qwen3.8-max--stop-truncation--triggering--default--67a34da7`, promoted ADR-0050."
  seed_determinism: "0/5 same-seed pairs (varies) — OBSERVED 2026-09-03: qwen3.8-max's seed field is accepted-unverified at the contract sweep; five same-seed repeat calls produced five distinct outputs, cell_id:`qwen3.8-max--seed--42--default`, probe_id:`qwen3.8-max--seed--42--default--r1--497b033d`, promoted ADR-0050."
  sampling_repeatability: "0/4 repeat pairs (varies) — OBSERVED 2026-09-03: qwen3.8-max accepts an explicit temperature:0 value in default mode — a genuine temperature:0 test, not a substitute; all five repeat calls completed naturally with five distinct outputs, cell_id:`qwen3.8-max--temperature--0--default`, probe_id:`qwen3.8-max--temperature--0--default--r1--8d1713bd`, promoted ADR-0050."
  multi_candidate_delivery: "rejected — OBSERVED 2026-09-03: a request for 2 candidates was rejected outright in default mode, a rejection Qwen's own documentation corroborates as thinking-mode-conditional, cell_id:`qwen3.8-max--n--2--default`, probe_id:`qwen3.8-max--n--2--default--e510e3ee`, promoted ADR-0050."
  logprobs_delivery: "accepted-honored — OBSERVED 2026-09-03: `logprobs` returns real per-token content, the behavioral reverify agreeing with the contract sweep's own already-unambiguous reading, cell_id:`qwen3.8-max--logprobs-reverify--combined--default`, probe_id:`qwen3.8-max--logprobs-reverify--combined--default--97ef0c4f`, promoted ADR-0050."
  service_tier_contract: "accepted-ignored — OBSERVED 2026-09-03: `service_tier` is accepted at the presence probe but not echoed back at the requested value, probe_id:`qwen3.8-max--service-tier--auto--default--21c5dfa8`; the value-enum row fires here (openai_compat family) — all 4 values accepted-ignored uniformly, probe_id:`qwen3.8-max--openai-service-tier-values--auto--default--21c5dfa8`; unlike its qwen3.8-flash sibling, the BHV-06 tier audit did not fire against this model — the response-side shape (nested, absent, or flat) is not tested here, so the cell states only what the presence and enum rows established, promoted ADR-0050."
checked: 2026-08-27
depth: stub
---

# Qwen3.8-Max

Alibaba's flagship, and the largest model tracked here: a **2.4T-parameter MoE with 95B
activated per token**, natively multimodal (image + text + video in, text out), served at
1M context on QwenCloud — the global platform Alibaba Cloud launched 2026-05-26 and the
first-party surface every fact above was verified against. It replaces qwen3-coder-next as
the Qwen line's headline entry here, and it is a different bet entirely: that report's
subject is an 80B/3B-activated model an individual can self-host, this one is thirty times
its total size and about as self-hostable as Kimi K3.

The **weights are published** (`Qwen/Qwen3.8-2.4T-A95B`), which puts three of the four
largest models in this sweep — K3, this, and DeepSeek V4 — on the open-weights side. The
license is not: it is a bespoke document named `qwen3.8-max`, so the Qwen line no longer
speaks with one voice on terms (qwen3-coder-next is Apache-2.0).

## The API is not the weights, and the card says so

The single most useful sentence found for this report is on Qwen's own weights card, which
says the repo holds the post-trained model behind the commercial service and that the API
**adds** *"more features, such as vision input & non-thinking support, 1M context length by
default, official built-in tools."* Read that against the same card's reasoning section —
the open weights think **always**, in `<think>` tags, and cannot be told not to.

So the reasoning contract, the context window, and the input modalities all differ by
access route for one model name — and for once the vendor writes the difference down
instead of leaving it to be discovered. When first written (2026-08-27, same day) this
section framed that as a strain on type 1b: the type's "same model, different product"
claim had meant *serving* variance, and this is *artifact* variance — the routes hand you
different things. **Resolved the same day by scoping, not by splitting**
([ADR-0048](../../adrs/0048-category-1-assesses-api-versions-only.md)): every spec and
assessed key in this report describes the API-served product, and the weights divergence
above is acknowledged context — which is exactly what this section now is.

## The category-1 axes (taxonomy §1)

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | · — "official built-in tools" are named as an API-side addition over the weights; nothing measured here |
| Long-horizon coherence | · — third-party coverage of the launch repeats a vendor claim about a 16-day autonomous engineering run; the press release itself returned HTTP 403 to two fetch attempts (2026-08-27), so it is **not** recorded as a fact |
| Usable context (vs advertised) | **The gap is documented rather than suspected.** The weights card states *"262,144 natively and extensible up to 1,010,000 tokens"*; the API serves 1M "by default". So the 1M is a serving configuration over a 256K-native model, and the model page's own limits row (max input **991K**, dropping to **983K** in thinking mode) shows the advertised round number is not all addressable in one request |
| Cost per completed task | · — $2 / $6 per MTok list, flat. But `reasoning_effort` defaults to `xhigh`, the most expensive of three levels, so list price understates realized cost by an unmeasured factor (the same caveat GLM-5.3 and Kimi K3 carry) |
| Release mode & access routes (1b) | Weights on Hugging Face under a bespoke license + first-party API on QwenCloud, whose changelog also lists the raw `qwen3.8-2.4t-a95b` since 2026-08-13 — the platform sells **both** the served flagship and its underlying weights, side by side, ten days apart |

## Reasoning surface

All three cells are now verified — but the third took a probe where the first two took a
page, and the four-day gap between those is the story of this section.

- **`reasoning: true`** — the docs list Qwen3.8 among the series supporting thinking, and
  the model streams it as `response.reasoning_text.delta` before the answer.
- **`reasoning_effort: levels:low/medium/xhigh@xhigh`** — verbatim from the thinking guide:
  *"Example with `qwen3.8-max` (options: `low`, `medium`, `xhigh`; default `xhigh`)"*. The
  same guide adds a constraint no other model here has: *"`qwen3.8-max` does not support
  setting `reasoning_effort` and `thinking_budget` simultaneously — doing so returns an
  error."* Both dials exist; using them together is an error, which makes this the sweep's
  first model where the two `reasoning_effort` families (levels vs budget) are **mutually
  exclusive within one model** rather than a per-vendor choice.
- **`reasoning_type: default-on` — observed, not read.** As written on 2026-08-27 this
  cell was *deliberately blank*: the guide's mode taxonomy (*"**Hybrid**: toggle thinking
  on or off per request with `enable_thinking`"*) ruled out `always-on`, but no
  first-party surface stated the **default** for this model — the platform states it for
  the open weights and for the Flash sibling, and for its flagship it did not. Rather
  than guess between `default-on` and `opt-in`, the cell stayed empty and the gap was
  recorded as an enum strain (the matrix renders `·` = "not checked" for a cell that
  *was* checked). **Resolved 2026-08-31 by the first [issue #42] thin-client probe**: a
  request with no thinking parameters returned `reasoning_content` (36 reasoning tokens
  billed), and `enable_thinking: false` returned none — default-on, toggleable, both
  directions observed for well under a cent. The strain resolved by **escalating the
  evidence route** (docs → probe), not by widening the enum; the queued question of a
  `not-stated` marker for `reasoning_type` lost its only instance the day the probe
  route opened, which is an argument that probes, not vocabulary, are the fix for
  vendor silence about *observable* behavior.

[issue #42]: https://github.com/leandromineti/ai-assisted-coding/issues/42

## Role in this repo's work

None run. Qwen reaches this repo's work through category 2 — [qwen-code](../2-harnesses/qwen-code.md)
(deep-dived 2026-08-27) is the maker's own harness, and `qwen` is one of the families
hermes-agent patches for tool-use enforcement. Whether qwen-code's defaults point at this
model is unchecked and is the obvious next probe.

## Surprises

1. **A flagship whose vendor publishes the weights and then sells a strictly better
   version of them.** Not a teaser: vision input, non-thinking mode, 4× the default
   context, and built-in tools are all API-only, stated plainly on the card. The
   open-weights release is real and the hosted model is genuinely a different product —
   a third position between "open" and "closed" that this repo's `access` enum (ADR-0044)
   flattens to `open-weights` without complaint.
2. **The platform states the thinking default for the free weights and for the cheap
   sibling, but not for the flagship.** The one model where a wrong assumption about
   default-on costs the most per token is the one left unstated.
3. **`reasoning_effort` and `thinking_budget` are an either/or.** Every other model here
   offers one family or the other; this offers both and errors when you use them together.

## Open questions

- ~~Is thinking on by default for `qwen3.8-max`? A single API call answers it (send no
  thinking parameters, look for `reasoning_text`); until then the cell stays empty.~~
  **Resolved 2026-08-31** exactly as predicted — one paramless call, `reasoning_content`
  returned, `default-on` (§ Reasoning surface).
- Is the 22:00–08:00 (UTC+8) half-price night window real for this model? If it is, the
  regime is `time-of-day` (DeepSeek V4's shape), not `flat` — this changes a comparable
  number, so it needs a first-party page, not a press citation.
- ~~Does the Batch API accept the `qwen3.8-max` id? The model page and the batch guide
  disagree; one request settles it.~~ **Resolved 2026-08-31, in two probe rounds**: the
  first attempt hit an account-verification wall (`access_denied: "The user information
  is not completed"`); after the owner completed the QwenCloud account, batch validation
  failed with `model_not_found`: *"The provided model 'qwen3.8-max' is not supported by
  the Batch API."* **The API is the tiebreaker when two doc surfaces disagree** — the
  batch guide's model list was right, the model page's Batch card wrong. Cell updated;
  failed validation billed nothing.
- Does the 1M serving window behave like context or like a truncation cliff past the
  262,144 native length? The rig could probe this cheaply, and the answer generalizes to
  every "extensible up to" model in the sweep.
