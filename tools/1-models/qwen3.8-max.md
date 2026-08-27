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
  # reasoning_type: DELIBERATELY OMITTED, not unchecked — the docs put this model in the
  # `Hybrid` mode ("toggle thinking on or off per request with `enable_thinking`") but no
  # first-party surface states the DEFAULT, which is the one thing the enum encodes.
  # `always-on` is excluded by the toggle; `default-on` vs `opt-in` is unresolved. See
  # § Reasoning surface.
  reasoning_effort: "levels:low/medium/xhigh@xhigh"   # docs, verbatim: "Example with `qwen3.8-max` (options: `low`, `medium`, `xhigh`; default `xhigh`)"
  prompt_caching: "two priced modes on one model page: implicit cache read $0.25 per MTok (0.125x of input, no opt-in stated), explicit cache creation $2.50 (1.25x) + explicit cache read $0.17 per MTok (0.085x). No TTL and no breakpoint surface stated anywhere checked (2026-08-27)"
  batch_discount: "platform Batch API is '50% of the real-time price', results 'delivered within 24 hours' (first-party batch guide) — but the guide's supported-model list names only the older `qwen-max`/`qwen-plus`/`qwen-flash`/`qwen-turbo` ids and never mentions `qwen3.8-max`, while the model page itself carries a Batch card ('Asynchronously process requests in batches to reduce costs'). Two first-party surfaces, one claim each way; recorded unresolved (2026-08-27)"
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
access route for one model name. Type 1b's standing claim in this repo is that "the same
model reached by different routes is not the same product"; this is the cleanest specimen
yet, because for once the vendor writes the difference down instead of leaving it to be
discovered.

## The category-1 axes (taxonomy §1)

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | · — "official built-in tools" are named as an API-side addition over the weights; nothing measured here |
| Long-horizon coherence | · — third-party coverage of the launch repeats a vendor claim about a 16-day autonomous engineering run; the press release itself returned HTTP 403 to two fetch attempts (2026-08-27), so it is **not** recorded as a fact |
| Usable context (vs advertised) | **The gap is documented rather than suspected.** The weights card states *"262,144 natively and extensible up to 1,010,000 tokens"*; the API serves 1M "by default". So the 1M is a serving configuration over a 256K-native model, and the model page's own limits row (max input **991K**, dropping to **983K** in thinking mode) shows the advertised round number is not all addressable in one request |
| Cost per completed task | · — $2 / $6 per MTok list, flat. But `reasoning_effort` defaults to `xhigh`, the most expensive of three levels, so list price understates realized cost by an unmeasured factor (the same caveat GLM-5.3 and Kimi K3 carry) |
| Release mode & access routes (1b) | Weights on Hugging Face under a bespoke license + first-party API on QwenCloud, whose changelog also lists the raw `qwen3.8-2.4t-a95b` since 2026-08-13 — the platform sells **both** the served flagship and its underlying weights, side by side, ten days apart |

## Reasoning surface

Two of the three reasoning cells are verified; the third is deliberately blank, and the
reason is the point.

- **`reasoning: true`** — the docs list Qwen3.8 among the series supporting thinking, and
  the model streams it as `response.reasoning_text.delta` before the answer.
- **`reasoning_effort: levels:low/medium/xhigh@xhigh`** — verbatim from the thinking guide:
  *"Example with `qwen3.8-max` (options: `low`, `medium`, `xhigh`; default `xhigh`)"*. The
  same guide adds a constraint no other model here has: *"`qwen3.8-max` does not support
  setting `reasoning_effort` and `thinking_budget` simultaneously — doing so returns an
  error."* Both dials exist; using them together is an error, which makes this the sweep's
  first model where the two `reasoning_effort` families (levels vs budget) are **mutually
  exclusive within one model** rather than a per-vendor choice.
- **`reasoning_type`: omitted on purpose.** The guide's mode taxonomy is *"**Hybrid**:
  toggle thinking on or off per request with `enable_thinking`. **Thinking-only**: always
  thinks — cannot be disabled"*, and it places this model in Hybrid — corroborated by the
  weights card's "non-thinking support" as an API addition. That rules out `always-on`. It
  does **not** decide between `default-on` and `opt-in`, which is exactly what the enum
  records, and no surface checked states the default *for this model*: the platform states
  it for the open weights ("thinking enabled by default") and for the Flash sibling
  ("Thinking mode is enabled by default"), and for its flagship it does not.

Omitting the cell costs something real — the matrix renders `·`, which the repo reads as
"not checked", and this was checked. That is a **known strain point in the enum**, the
second one recorded (the first is Opus 5's effort-conditional toggleability, in
[`../1-models/README.md`](README.md)). Two strain points is this repo's stated bar for
revisiting a vocabulary, so this belongs in the ADR queue rather than in a guessed cell.

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

- Is thinking on by default for `qwen3.8-max`? A single API call answers it (send no
  thinking parameters, look for `reasoning_text`); until then the cell stays empty.
- Is the 22:00–08:00 (UTC+8) half-price night window real for this model? If it is, the
  regime is `time-of-day` (DeepSeek V4's shape), not `flat` — this changes a comparable
  number, so it needs a first-party page, not a press citation.
- Does the Batch API accept the `qwen3.8-max` id? The model page and the batch guide
  disagree; one request settles it.
- Does the 1M serving window behave like context or like a truncation cliff past the
  262,144 native length? The rig could probe this cheaply, and the answer generalizes to
  every "extensible up to" model in the sweep.
