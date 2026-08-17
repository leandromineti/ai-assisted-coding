# Layer 1 — Models

`checked: 2026-08-17`

The weights. See [`../../taxonomy.md`](../../taxonomy.md) for what this layer is and how
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

## Inventory

| Model | Vendor | Release | One-line |
|-------|--------|---------|----------|
| [**Fable 5**](claude-fable-5.md) | Anthropic | GA 2026-06-09 | Frontier tier; always-on adaptive thinking; ~30% tokenizer inflation vs pre-4.7 models; domain-gated Mythos 5 twin. $10/$50. |
| [**Opus 5**](claude-opus-5.md) | Anthropic | 2026 | Agentic workhorse; 1M context **standard** (the earlier "1M variant" phrasing was stale). Freshest knowledge cutoff in the lineup (May 2026). $5/$25. Exp-01's arm model. |
| [**Sonnet 5**](claude-sonnet-5.md) | Anthropic | 2026 | Mid-tier; **the rig's pinned model for all layer-4 experiment arms.** Now measured in-repo: 18–20/21 on the tarpeek verifier (n=6 incl. Run A), $0.41/run. $2/$10 became the *standard* price on 2026-08-17 — the scheduled September increase was cancelled, so August ledgers are at list price. |
| [**Haiku 4.5**](claude-haiku-4-5.md) | Anthropic | 2025-10 | Small/fast tier; in practice the *background-cognition* model inside other tools (ECC's instinct analysis runs on it). Now measured in-repo: uniform 17/21, one packaging DOA, $0.150/run — fully separated from Sonnet on the same instrument. Feb 2025 cutoff. $1/$5. |
| [**GPT-5.6 Sol**](gpt-5-6-sol.md) | OpenAI | 2026 | Frontier tier of a three-tier family (Sol $5/$30 · Terra $2/$12 · Luna $0.20/$1.20), all 1.05M ctx, Feb 2026 cutoff. **GPT-5.5 is retired** — gone from the current models page (2026-07-31), so the Terminal-Bench row below cites a model you can't buy. |
| [**Gemini 3.1 Pro**](gemini-3-1-pro.md) | Google | 2026 | Still **Preview** while the Flash line is Stable. Tiered pricing doubles above 200k input tokens — taxing the long-context pitch. Advertised window *not found on the checked pages*; the "hold the whole monorepo" framing is currently unsourced. |
| [**Grok 4.5**](grok-4-5.md) | xAI | 2026-07-08 | Coding/agent-tuned, 1.5T-param V9 base. **Trained on real Cursor session data.** 500k ctx — *half its cheaper siblings' 1M*. $2/$6 (<200k), $4/$12 above. No EU at launch (2026-07-28 check). |
| [**Kimi K3**](kimi-k3.md) | Moonshot AI | 2026-07 | Largest open-weight model: 2.8T total / 104B activated, KDA, 1M ctx (2^20 exactly), native vision, **QAT-native MXFP4 release**. Bespoke "Kimi K3 License". Claims Terminal-Bench 2.1 **88.3** — harness unstated. |
| [**DeepSeek V4**](deepseek-v4.md) | DeepSeek | 2026 (GA ~Jul) | Row verified: API is `deepseek-v4-pro`/`-flash`, both 1M ctx, **384K max output** (3× everyone else), weights on HF (`both` release mode). Flash output at $0.28/MTok ≈ 90× cheaper than Fable 5; cache hits near-free. |
| [**Qwen3-Coder-Next**](qwen3-coder-next.md) | Alibaba | 2026-02 | Row verified: 80B total / **3B activated**, 256K ctx, Apache-2.0 — the one genuinely self-hostable agent model in the sweep. Publishes its own modest Terminal-Bench 2.0 score (36.2). A "Qwen 4 Coder" successor is third-party rumor, unresolvable on the official org (2026-07-31). |

## Sub-layer 1b — Model access

| Route | One-line |
|-------|----------|
| First-party APIs | Anthropic, OpenAI, Google, xAI (`console.x.ai`). Reference behavior; caching and rate limits as designed. |
| Aggregators / routers | OpenRouter, Models.dev. One key, many models — at the cost of an extra hop and inconsistent caching support. |
| Cloud marketplaces | AWS Bedrock, GCP Vertex. Procurement and data-residency plays; feature lag is common. |
| Local runtimes | Ollama, llama.cpp, vLLM. Only viable for open-weight models, and quantization changes behavior under the same model name. |

**Why this sub-layer matters:** the same model name reached by different routes is not the
same product. Prompt-caching support, quantization, rate limits, and silent context
truncation all vary by route.

## Benchmark snapshot

Terminal-Bench 2.1, as reported mid-2026 — note these pair a **model with a harness**, so
they measure layers 1+2 together, never the model alone:

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
    [`../02-harnesses/opencode.md`](../02-harnesses/opencode.md) — so "same harness" still
    means each model gets its own system prompt. True isolation is harder than it looks.)
  - Its headline finding — **structural completeness does not predict runtime
    correctness**: models produce complete-looking apps whose tests mock hallucinated
    library APIs, so the output scores well while not actually running. That's a
    verification-layer insight as much as a model one; see
    [`../cross-cutting/index.md`](../cross-cutting/index.md).

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
