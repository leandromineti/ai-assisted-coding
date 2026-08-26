# Category 1 — Models

`checked: 2026-08-26`

The weights. See [`../../docs/tool-taxonomy.md`](../../docs/tool-taxonomy.md) for what this category is and how
it's judged.

Per-model reports follow
[`_template-model-report.md`](_template-model-report.md) — adapted from the tool
template because closed weights have no source to trace: specs are verified against
the vendor page (dated `checked`), and the depth vocabulary maps to **stub** (specs
verified, not used) / **survey** (used on real work here, evidence named).
*Corrected 2026-08-17:* this mapping originally defined a third grade, deep-dive =
"this repo's experiments produced measured data" — written before methodology rule 1a
(2026-08-16), which it contradicts: closure caps a report at `survey`, and measured
behavior is OBSERVED-grade evidence, not source. Closed-weight models therefore top
out at `survey` no matter how much we measure them; the measurements go into a
report's evidence cells, not its depth field.

## What we assess here

The assessed block is **`model_features:`, 4 keys** (2026-08-26): `thinking`,
`effort_control`, `prompt_caching`, `batch_discount`. The weights themselves are
untraceable at this repo's level of analysis — which is why category 1 deliberately has no
component decomposition — so what *is* assessable is the first-party surface around them:
the two keys that change how a harness can drive the model, and the two that decide what a
completed task costs. Values are free text in each vendor's own vocabulary rather than
presence-claims ([ADR-0014](../../adrs/0014-model-features-into-registry.md)), because the
economics differ structurally across vendors and flattening them to ✓/✗ would erase the
finding. Each is verified against the report's `url` on its `checked` date.

The other half of the surface is **9 transcription fields** — `vendor`, `license`,
`model_id`, `release_mode`, `released`, `context_window`, `max_output`, `pricing`,
`knowledge_cutoff` — facts copied from a dated source rather than judged.

Definitions for every key:
[`comparisons/feature-registry.md`](../../comparisons/feature-registry.md). Values:
[`comparisons/features.md § Models`](../../comparisons/features.md#models-category-1) and
the fuller [`comparisons/models.md`](../../comparisons/models.md). A key is set **only**
when verified — omitted means "not checked", `false` means "checked and absent", and both
are claims.

## Inventory

| Model | Vendor | Release | One-line |
|-------|--------|---------|----------|
| [**Fable 5**](claude-fable-5.md) | Anthropic | GA 2026-06-09 (suspended 06-12, redeployed ~07-01) | Frontier tier; always-on adaptive thinking; ~30% tokenizer inflation vs pre-4.7 models; domain-gated Mythos 5 twin. $10/$50. |
| [**Opus 5**](claude-opus-5.md) | Anthropic | GA 2026-07-24 | Agentic workhorse; 1M context **standard** (the earlier "1M variant" phrasing was stale). Freshest knowledge cutoff in the lineup (May 2026). $5/$25. Exp-01's arm model. |
| [**Sonnet 5**](claude-sonnet-5.md) | Anthropic | GA 2026-06-30 | Mid-tier; **the rig's pinned model for all category-4 experiment arms.** Now measured in-repo: 18–20/21 on the tarpeek verifier (n=6 incl. Run A), $0.41/run. $2/$10 became the *standard* price on 2026-08-17 — the scheduled September increase was cancelled, so August ledgers are at list price. |
| [**Haiku 4.5**](claude-haiku-4-5.md) | Anthropic | GA 2025-10-15 | Small/fast tier; in practice the *background-cognition* model inside other tools (ECC's instinct analysis runs on it). Now measured in-repo: uniform 17/21, one packaging DOA, $0.150/run — fully separated from Sonnet on the same instrument. Feb 2025 cutoff. $1/$5. |
| [**GPT-5.6 Sol**](gpt-5-6-sol.md) | OpenAI | 2026-07-09 (stage ambiguous: 'preview' vs 'Released', vendor's two surfaces disagree) | Frontier tier of a three-tier family (Sol $5/$30 · Terra $2/$12 · Luna $0.20/$1.20), all 1.05M ctx, Feb 2026 cutoff. **GPT-5.5 is retired** — gone from the current models page (2026-07-31), so the Terminal-Bench row below cites a model you can't buy. |
| [**Gemini 3.1 Pro**](gemini-3-1-pro.md) | Google | Preview since 2026-02-19, no GA plan stated | Still **Preview** while the Flash line is Stable. Tiered pricing doubles above 200k input tokens — taxing the long-context pitch. Window resolved 2026-08-17: 1,048,576 in / 65,536 out, from the per-model page. |
| [**Grok 4.5**](grok-4-5.md) | xAI | 2026-07 (day 08 third-party only), no stage vocabulary | Coding/agent-tuned, 1.5T-param V9 base. **Trained on real Cursor session data.** 500k ctx — *half its cheaper siblings' 1M*. $2/$6 (<200k), $4/$12 above. No EU at launch (2026-07-28 check). |
| [**Kimi K3**](kimi-k3.md) | Moonshot AI | API ~2026-07-16 (vendor prints no date); weights by 07-27 | Largest open-weight model: 2.8T total / 104B activated, KDA, 1M ctx (2^20 exactly), native vision, **QAT-native MXFP4 release**. Bespoke "Kimi K3 License". Claims Terminal-Bench 2.1 **88.3** — harness unstated. |
| [**DeepSeek V4**](deepseek-v4.md) | DeepSeek | Preview 2026-04-24 → GA 2026-08-13 (vendor's words) | Row verified: API is `deepseek-v4-pro`/`-flash`, both 1M ctx, **384K max output** (3× everyone else), weights on HF (`both` release mode). Repriced 2026-08-16 to peak/off-peak (off-peak = 50%); still the sweep's cheapest, cache hits near-free. |
| [**GLM-5.3**](glm-5.3.md) | Z.ai (Zhipu AI) | API 2026-08-14 (day third-party-corroborated); weights held for a "two-week safety evaluation" | 1M ctx / 128K out, always-on reasoning, `reasoning_effort` default **max** (joining Kimi K3). $1.40/$4.40. Weights delayed with a stated offensive-security rationale — the sweep's only safety-gated weights release; prediction on record: HF repo by 2026-08-31. |
| [**Qwen3-Coder-Next**](qwen3-coder-next.md) | Alibaba | weights 2026-01-30 (HF commit); no stage stated | Row verified: 80B total / **3B activated**, 256K ctx, Apache-2.0 — the one genuinely self-hostable agent model in the sweep. Publishes its own modest Terminal-Bench 2.0 score (36.2). A "Qwen 4 Coder" successor is third-party rumor, unresolvable on the official org (2026-07-31). |

## Type 1b — Model access

| Route | One-line |
|-------|----------|
| First-party APIs | Anthropic, OpenAI, Google, xAI (`console.x.ai`). Reference behavior; caching and rate limits as designed. |
| Aggregators / routers | OpenRouter, Models.dev. One key, many models — at the cost of an extra hop and inconsistent caching support. |
| Cloud marketplaces | AWS Bedrock, GCP Vertex. Procurement and data-residency plays; feature lag is common. |
| Local runtimes | Ollama, llama.cpp, vLLM. Only viable for open-weight models, and quantization changes behavior under the same model name. |

**Why this type matters:** the same model name reached by different routes is not the
same product. Prompt-caching support, quantization, rate limits, and silent context
truncation all vary by route.

## Benchmark snapshot

Terminal-Bench 2.1, as reported mid-2026 — note these pair a **model with a harness**, so
they measure categories 1+2 together, never the model alone:

| Harness + model | Score |
|-----------------|-------|
| Codex CLI + GPT-5.5 | 83.4% |
| Claude Code + Opus 4.8 | 78.9% |
| Gemini CLI + Gemini 3.1 Pro | 70.7% |

These figures lag the current model generation (they cite Opus 4.8 and GPT-5.5, both
superseded). Treat leaderboard numbers as at least one generation stale by default.

## In-repo measured data (2026-08-17) — the model-isolated comparison

The confound the snapshot above suffers from is the one this repo's rig removes: the
2026-08-17 model-tier calibration held **harness (Claude Code CLI 2.1.220), task,
container, and network condition fixed** and varied only the model — the
model-isolated measurement that conclusion 2 says no public benchmark provides.
Small (n=5 per model, one task), but attributable:

| | Sonnet 5 | Haiku 4.5 |
|---|---|---|
| tarpeek verifier, completed runs | 18–20/21 (mean 19.0) | 17/21, uniform |
| completion | 5/5 | 4/5 (one undeclared-dependency DOA) |
| mean cost/run | $0.41 (intro) | $0.150 |
| characteristic failure | fine-grained exit codes, but tracebacks escape edge cases | blanket `rc=1`: never a traceback, never a distinguishable failure |

The tier separation is carried by *family-level* patterns (Haiku fails the whole
ambient-config family every run), and one item **reverses** (Haiku's coarse error
handling beats Sonnet on the truncated-archive trap) — trap items measure failure
style, not just capability. Details: the per-model reports' § Measured in this repo,
[`exp-02 log`](../../experiments/02-spec-kit-vs-plain/log.md) § Model-tier
calibration verdict, README conclusion 10.

## First-party surfaces worth knowing

`verification: dated-docs` means a fact was checked against the report's own `url` on its
`checked` date — but a vendor's "docs" is routinely **several** surfaces, and a fact
absent from one can be published on another. Recorded here as they are found, so the next
check starts where the fact actually lives:

- **Google DeepMind model cards** —
  [`deepmind.google/models/model-cards/`](https://deepmind.google/models/model-cards/)
  (index verified 2026-08-26: HTTP 200, **32 cards** listed, each with a landing page and
  a PDF). This is a *different* first-party surface from the API docs at
  `ai.google.dev/gemini-api/docs/models`, which every Gemini report carries as its `url`.
  The knowledge cutoff — when Google states one at all — lives on the card, not in the
  API spec table. Cards that this repo has read get a note in
  [`references/cards/`](../../references/cards/), with their quoted passages and a
  required archive snapshot (ADR-0034). The pattern found the first time it was read (2026-08-26,
  [gemini-3-1-pro](gemini-3-1-pro.md)): a later model's card can be **thin**, delegating
  most sections to its family parent's card rather than restating them. **Read what is
  being delegated.** A card that delegates a *section* which happens to contain a
  model-scoped figure does not transfer that figure — the Grok 4.5 cutoff was retracted
  2026-08-17 for exactly that inference. A card that delegates *the fact's own subject*
  does: Gemini 3.1 Pro's card sends its **training dataset** to the 3 Pro card, and a
  cutoff is a property of the training dataset, so the parent's January 2025 carries.

## References

- **[llm-coding-benchmark](https://github.com/akitaonrails/llm-coding-benchmark)** — Fabio
  Akita (`checked: 2026-07-28`). Many models build the *same* fixed Rails application spec
  — cloud (OpenRouter, Z.ai) and local (Ollama / llama-swap): Opus, GPT variants, DeepSeek,
  Qwen, Gemini, Kimi — all driven through the **same harness** (`opencode run`), scored on
  an 8-dimension / 100-point rubric (deliverables, API correctness, tests, error handling,
  persistence, Hotwire, architecture, production-readiness) plus manual code review. Two
  properties earn it a place here:
  - It **fixes the harness and varies the model** — the closest thing found so far to the
    model-isolating benchmark the open question below asks for. (And the fixed harness is
    opencode, whose per-model prompt dispatch is documented in
    [`../2-harnesses/opencode.md`](../2-harnesses/opencode.md) — so "same harness" still
    means each model gets its own system prompt. True isolation is harder than it looks.)
  - Its headline finding — **structural completeness does not predict runtime
    correctness**: models produce complete-looking apps whose tests mock hallucinated
    library APIs, so the output scores well while not actually running. That's a
    verification insight as much as a model one; see
    [`../../docs/README.md`](../../docs/README.md).

## Open questions

- Is there any public benchmark that isolates *model* from *harness*? **Partial answer
  2026-07-28:** [llm-coding-benchmark](https://github.com/akitaonrails/llm-coding-benchmark)
  (References above) fixes the harness and varies the model — though the fixed harness
  itself adapts its prompt per model, so the isolation is imperfect in an instructive way.
  **Reported upstream 2026-07-28** after confirming the team was unaware (all 11 blog
  posts, docs, and issues checked):
  [issue #12](https://github.com/akitaonrails/llm-coding-benchmark/issues/12) +
  [PR #13](https://github.com/akitaonrails/llm-coding-benchmark/pull/13), an opt-in
  `--uniform-system-prompt` mode that pins one prompt for all models via opencode's
  `agent.build.prompt` override.
- Long-horizon coherence has no standard measure. What would a homegrown one look like?
- Does open-weight parity (Kimi K3) actually change anything practical, given that
  self-hosting a 2.8T-param model is out of reach for an individual?
