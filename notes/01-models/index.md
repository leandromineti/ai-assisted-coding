# Layer 1 — Models

`checked: 2026-07-28`

The weights. See [`../../taxonomy.md`](../../taxonomy.md) for what this layer is and how
it's judged.

## Seed inventory

| Model | Vendor | Release | One-line |
|-------|--------|---------|----------|
| **Fable 5** | Anthropic | 2026 | Frontier tier; the reference point competitors benchmark against as of mid-2026. |
| **Opus 5** | Anthropic | 2026 | Agentic workhorse; ships a 1M-context variant (`claude-opus-5[1m]`). |
| **Sonnet 5** | Anthropic | 2026 | Mid-tier; the cost/capability compromise for high-volume agent loops. |
| **Haiku 4.5** | Anthropic | 2025-10 | Small/fast tier; mechanical subagent work. |
| **GPT-5.6 Sol** | OpenAI | 2026 | Frontier tier; cited alongside Fable 5 as the bar Kimi K3 was measured against. |
| **GPT-5.5** | OpenAI | 2026 | The version behind the Terminal-Bench 2.1 numbers below. |
| **Gemini 3.1 Pro** | Google | 2026 | Long-context specialist; the "hold the whole monorepo" option. |
| **Grok 4.5** | xAI | 2026-07-08 | Coding/agent-tuned, on the 1.5T-param V9 base. **Trained on real Cursor session data.** $2/$6 per M tokens. No EU availability at launch. |
| **Kimi K3** | Moonshot AI | 2026-07 | 2.8T params — largest open-weight model released. Kimi Delta Attention, 1M context, native vision. Trails Fable 5 / GPT-5.6 Sol overall but leads open weights. |
| **DeepSeek** *(unverified)* | DeepSeek | — | Open-weight line; current version not confirmed at check date. |
| **Qwen** *(unverified)* | Alibaba | — | Open-weight line, strong local-inference story; current version not confirmed. |

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

## Open questions

- Is there any public benchmark that isolates *model* from *harness*? If not, what does
  that mean for how this layer can be evaluated at all?
- Long-horizon coherence has no standard measure. What would a homegrown one look like?
- Does open-weight parity (Kimi K3) actually change anything practical, given that
  self-hosting a 2.8T-param model is out of reach for an individual?
