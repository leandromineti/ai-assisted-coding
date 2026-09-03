---
name: kimi-k3
category: 1
maker: Moonshot AI
url: https://huggingface.co/moonshotai/Kimi-K3
license: "Kimi K3 License (model card's own term; third-party summaries describe it as MIT-like with a commercial MaaS revenue gate — the gate did not appear in the card text checked, so its terms are unverified here)"
access: open-weights
model_id: moonshotai/Kimi-K3
release_date:
  date: null
  stage: not-stated
  note: "the launch blog prints NO calendar date and uses no stage vocabulary; third-party puts it ~2026-07-16, which is inference and not the fact. Weights were promised 'by July 27, 2026' and the HF initial commit is consistent with that, but this report has never recorded that commit's date — reading it off the HF repo is the open route to a first-party date (verified 2026-08-17)"
context_window: 1048576
max_output: "131072 default, settable up to 1048576 (first-party API max_completion_tokens; verified 2026-08-17)"
pricing:
  input: 3          # USD per MTok — base list rate (see the registry's rule)
  output: 15
  currency: USD
  regime: route-dependent
  note: "weights free; first-party API $3 / $15 per MTok flat across the window (platform.kimi.ai, USD). A separate first-party CNY surface (platform.kimi.com) lists ¥20 / ¥100 — two price lists, not one converted. Other routes remain route-dependent (verified 2026-08-17)"
knowledge_cutoff:
  date: null          # the limit date on training data
  basis: not-stated
  note: "not stated in quickstart, HF card, or GitHub README (checked 2026-08-17); the k3_tech_report.pdf — flagged as the one unread candidate — was READ 2026-08-26 (47 pp, via the HF model page's link to MoonshotAI/Kimi-K3) and is silent: no knowledge cutoff anywhere, the document's only 'cutoff' being an unrelated MoE routing threshold, and its §3.1 Pre-Training Data naming four corpus domains with no dates. Every candidate first-party surface is now checked"
model_features:   # nested per ADR-0014 (2026-08-19); reasoning keys split per ADR-0040
  reasoning: true
  reasoning_type: always-on    # docs: "K3 always thinks"; not toggleable (first-party API) — OBSERVED 2026-08-31 (issue #42 probe): reasoning_content returned with no params; and `enable_thinking: false` is ACCEPTED AND SILENTLY IGNORED — no error, reasoning still returned. Contrast Z.ai (rejects with an error) and Qwen (honors it): three vendors, three behaviors for the same param intent
  reasoning_effort: "levels:low/high/max@max"   # default-to-most-expensive; reasoning tokens bill as output
  prompt_caching: "automatic, no cache id or TTL surface, prior-request >256-tok threshold; cache-hit input $0.30 vs miss $3.00 per MTok (0.1x); no storage fee mentioned (first-party API)"
  batch_discount: "checked and absent for K3 — Moonshot's batch API (40% off) is explicitly scoped to kimi-k2.5/k2.6 only (first-party docs, 2026-08-17)"
  fast_mode: false   # checked and absent: the K3 pricing page bills only cache-hit input, cache-miss input, and output — no speed tier; kimi-k2-turbo-class ids are sibling models, not modes (verified 2026-08-27)
  stop_sequence_honesty: "ambiguous — OBSERVED 2026-09-03: stop-honored truncation before the trigger word, but the openai_compat family's shared stop finish value matches the no-stop control's own finish reason — text comparison is the only evidence, cell_id:`kimi-k3--stop-truncation--triggering--default`, probe_id:`kimi-k3--stop-truncation--triggering--default--5b566140`, promoted ADR-0050."
  seed_determinism: "0/5 same-seed pairs (no-signal) — OBSERVED 2026-09-03: kimi-k3's five same-seed repeats each hit reasoning-length exhaustion before producing a comparable visible completion, so the 0/5 rate reflects exhausted budget, not observed variation, cell_id:`kimi-k3--seed--42--default`, probe_id:`kimi-k3--seed--42--default--r1--785f1743`, promoted ADR-0050."
  sampling_repeatability: "0/4 repeat pairs (varies) — OBSERVED 2026-09-03: kimi-k3 rejects an explicit temperature value outright in default mode (docs-corroborated, no field documented and HTTP 400 on the wire); this default-config-repeatability SUBSTITUTE asks whether the model's own default sampling is repeatable across five identical requests with no temperature parameter sent at all, and all five completed naturally with five distinct outputs, cell_id:`kimi-k3--default-config-repeatability--no-temperature--default`, probe_id:`kimi-k3--default-config-repeatability--no-temperature--default--r1--c96c7328`, promoted ADR-0050."
checked: 2026-08-17
depth: stub
---

# Kimi K3

The largest open-weight model released as of mid-2026: **2.8T total parameters, 104B
activated** (896 experts, 16 per token), on Kimi Delta Attention + Attention Residuals
— 93 `layers` (69 KDA + 24 gated MLA), native vision, 1M context. Shipped **quantized by
design**: MXFP4 weights / MXFP8 activations via quantization-aware training, so the
published artifact *is* the low-precision model rather than a full-precision original
that third parties quantize down. Released July 2026.

## The category-1 axes

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | Vendor-claimed strength ("agentic" benchmark family); the card claims **88.3 on Terminal-Bench 2.1** — above every harness+model row in this repo's stale benchmark snapshot, with harness unstated (the category index's model+harness confound, from the other side) |
| Long-horizon coherence | · |
| Usable context (vs advertised) | 1,048,576 exactly (2^20) — same power-of-two budget as GPT-5.6's "1.05M" |
| Cost per completed task | Weights free; the real cost is inference infrastructure (vLLM/SGLang on H100/H20-class GPUs) — the taxonomy's open question about whether 2.8T-scale open weights change anything *practical* for individuals stands |
| Release mode & access routes (1b) | Open weights + hosted APIs + aggregators; the full 1b spread, with quantization variance built in rather than added downstream |

## Reasoning surface

What the three reasoning cells rest on, verified 2026-08-17 against the first-party API
docs (carried verbatim from the free-text `thinking`/`effort_control` cells those keys
replaced, ADR-0040): *"always-on, not toggleable — docs: 'K3 always thinks';
`reasoning_content` returned. Collapses K2's thinking/non-thinking variant split
(first-party API)"* and *"`reasoning_effort`: low/high/max, default MAX — was the only
default-to-most-expensive in the sweep until GLM-5.3 shipped the identical surface and
default (sweep-relative clause amended 2026-08-26; the K3 facts themselves are unchanged
from the 2026-08-17 check); reasoning tokens billed as output (first-party API)."*

Moonshot's docs say *thinks*; the response field says `reasoning_content`. Both are
quoted as written — only this repo's own voice standardised on *reasoning*.

## Role in this repo's work

Referenced, not run: the category index's open-weight-parity question names it, and it
appears in llm-coding-benchmark's model roster (driven through opencode — the harness
whose per-model dispatch this repo documented upstream).

## Surprises

1. **QAT-native release**: shipping MXFP4 as the canonical artifact collapses the 1b
   "quantization changes behavior under the same name" problem — there is no
   full-precision reference to diverge from. A structural fix to route variance,
   from the weights side.
2. **The benchmark direction reversed**: an open-weight vendor claiming to *beat*
   the frontier pairings on Terminal-Bench (88.3 vs the 83.4 the index records for
   Codex+GPT-5.5) — claims now flow from open-weight labs toward closed leaders, with
   harness pairing unstated in both directions.
3. **A bespoke license with a name** ("Kimi K3 License") — neither Apache/MIT nor
   proprietary; open-weights licensing is speciating, and `access: open-weights` needs
   the license field read, not assumed — the two fields are a pair, and this is exactly
   the case where the second does the work (ADR-0044).
4. **`reasoning_effort` defaults to `max`** (2026-08-17) — the only
   default-to-most-expensive in the sweep (OpenAI defaults `medium`, DeepSeek `high`,
   and reasoning tokens bill as output at $15/MTok). Thinking is also always-on with
   no toggle: "K3 always thinks." The vendor's default posture is maximum spend.
5. **Two first-party price lists, and a rebrand** (2026-08-17): `platform.moonshot.ai`
   now 301s to `platform.kimi.ai` (USD) and `platform.moonshot.cn` to
   `platform.kimi.com` (CNY, ¥20/¥100 — its own list, not a conversion). Moonshot's
   batch API (40% off) explicitly excludes K3: it covers only k2.5/k2.6.

## Open questions

- The license's actual commercial terms — read the license file itself, not
  summaries, before any claim stronger than "weights downloadable".
- What harness produced the 88.3 Terminal-Bench claim? (Unstated in the card
  summary; the model+harness confound cuts both ways.)
- ~~Does 104B-activated MoE inference actually fit any individual's budget via the
  GGUF/community route, and at what quality loss?~~ **Closed by scope 2026-08-27**
  ([ADR-0048](../../adrs/0048-category-1-assesses-api-versions-only.md)): the
  GGUF/community route is self-hosted serving, acknowledged but not assessed here.
