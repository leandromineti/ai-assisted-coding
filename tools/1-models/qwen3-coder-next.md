---
name: qwen3-coder-next
category: 1
maker: Alibaba (Qwen team)
url: https://huggingface.co/Qwen/Qwen3-Coder-Next
license: Apache-2.0
access: open-weights
model_id: Qwen/Qwen3-Coder-Next
release_date:
  date: 2026-01-30
  stage: not-stated
  note: "weights: HF initial commit 2026-01-30 (refines the '~Feb 2026' recorded 2026-07-31); no vendor stage vocabulary anywhere — the Model Studio page carries no GA/preview label and a blank update-time field (checked 2026-08-17)"
context_window: 262144
max_output: 65536   # Model Studio context-limits table; max input 204800 of the 262144 window (verified 2026-08-17)
pricing:
  input: 0.3          # USD per MTok — base list rate (see the registry's rule)
  output: 1.5
  currency: USD
  regime: route-dependent
  note: "weights free; first-party Model Studio (Singapore + Frankfurt, USD) tiered by input length: $0.30 / $1.50 ≤32k, $0.50 / $2.50 32–128k, $0.80 / $4.00 128–256k per MTok; China-mainland CNY list ~half that; other routes route-dependent (verified 2026-08-17)"
knowledge_cutoff:
  date: null          # the limit date on training data
  basis: not-stated
  note: "not stated by Qwen — HF README (full read), Model Studio page, and launch blog all silent (checked 2026-08-17)"
model_features:   # nested per ADR-0014 (2026-08-19); reasoning keys split per ADR-0040
  reasoning: false             # verified absent: HF README "supports only non-thinking mode"
  reasoning_type: none
  reasoning_effort: none       # no reasoning mode, so no dial is offered for this model
  prompt_caching: "unsupported for this model — Model Studio capability row 'Context Caching: Unsupported'; the platform's implicit(0.2x)/explicit(0.1x, 5m TTL) caching lists only qwen3-coder-plus/flash"
  batch_discount: "unsupported for this model — capability row 'Batch Inference: Unsupported' (platform batch, ~50% where offered, excludes it)"
checked: 2026-08-17
depth: stub
---

# Qwen3-Coder-Next

The Qwen line's current **verified** coding release (card checked 2026-07-31,
resolving the seed inventory's `unverified` row): an 80B-total / **3B-activated** MoE
(512 experts, 10 per token), 256K native context, Apache-2.0, released ~Feb 2026.
Its pitch is the inverse of Kimi K3's: not the biggest open model, but "performance
comparable to models with 10–20× more active parameters" — the local-inference story
the seed inventory attributed to the Qwen line, now with a concrete artifact.

**Note on "Qwen 4 Coder":** third-party posts claim a June 2026 successor (Apache-2.0,
82% SWE-Verified, Mac-runnable). It does **not** resolve on the official HF org
(checked 2026-07-31) and the official card names no successor — recorded as
unverified rumor, the same discipline that kept DeepSeek's row honest through the R2
cycle.

## The category-1 axes

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | Card claims agent-oriented tuning; benchmark claims: SWE-bench Verified 70.6%, SWE-bench Pro 44.3%, Terminal-Bench 2.0 **36.2%** — the honest number in the set (a coding-agent model publishing a sub-40 terminal score) |
| Long-horizon coherence | · |
| Usable context (vs advertised) | 256K native — deliberately *not* the 1M class; the small-activated-params bet spends elsewhere |
| Cost per completed task | 3B activated params is the lowest inference cost in this sweep by far — this is the one model here an individual can genuinely self-host |
| Release mode & access routes (1b) | Open weights (Apache-2.0, the cleanest license in the sweep) + hosted routes; heavy GGUF ecosystem |

## Reasoning surface

The sweep's only verified **absence**, and the evidence is why it is a `✗` rather than a
`·` — verified 2026-08-17, carried verbatim from the free-text `thinking`/`effort_control`
cells those keys replaced (ADR-0040): *"none — verified absent: HF README 'supports only
non-thinking mode'; absent from Model Studio's deep-thinking model table (first-party)"*
and *"n/a — no thinking mode, so Model Studio's `thinking_budget`/`reasoning_effort`
surfaces are not offered for this model."*

Two first-party surfaces, one stating the absence and one failing to list the model where
listed models appear. That pair is what an absence claim costs here.

## Role in this repo's work

None run. The Qwen line appears in llm-coding-benchmark's roster (via opencode's
`default.txt` — no bespoke prompt, per upstream issue #12) and in hermes' per-family
tool-use enforcement list (`qwen` is patched, like GPT/Grok/Gemini — harness authors
treat it as needing execution-discipline correction).

## Surprises

1. **A vendor publishing a modest benchmark number** (Terminal-Bench 2.0 at 36.2)
   alongside strong SWE-bench claims — selective-but-honest disclosure, rarer than it
   should be, and more informative than Kimi's chart-topping claim precisely because
   it's believable.
2. **3B activated parameters** as a serious agent-model bet — the opposite pole from
   Kimi K3's 104B-activated within the same open-weights world. The open ecosystem is
   exploring the activated-params axis far more aggressively than the closed one.
3. **The vendor's own platform hosts it as a second-class citizen** (2026-08-17): on
   Model Studio, context caching, batch inference, and fine-tuning are all
   capability-row "Unsupported" for this model, while its siblings (coder-plus,
   coder-flash) get the platform's caching. A 1b lesson: "first-party hosted API
   exists" is not one fact but a per-feature matrix — the route can carry the model
   without carrying the platform's economics.

## Open questions

- Verify or bury "Qwen 4 Coder" at the next check — if real, it supersedes this
  report's subject within months of it.
- The 10–20× efficiency claim is benchmark-relative; does it survive an agentic
  workload with real tool loops? ~~(The rig could test a self-hosted arm cheaply.)~~
  *Self-hosted-arm clause closed by scope 2026-08-27
  ([ADR-0048](../../adrs/0048-category-1-assesses-api-versions-only.md)); the question
  itself stands, but any test runs against the first-party API route.*
