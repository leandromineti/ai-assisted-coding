---
name: glm-5.3
category: 1
maker: Z.ai (Zhipu AI)
url: https://docs.z.ai/guides/llm/glm-5.3
license: "unverified — no GLM-5.3 weights published yet, so there is no license to read; do not assume the GLM-5/5.1/5.2 repo licenses carry over"
access: closed-source   # today; weights announced for after a "two-week safety evaluation" — see the dated prediction below, which scores this cell flipping to open-weights
model_id: glm-5.3 (API); the announced HF repo does not exist yet — zai-org lists GLM-5, GLM-5.1, GLM-5.2 (+ FP8 variants) and no 5.3 (HF API `author=zai-org&search=GLM-5`, checked 2026-08-26)
release_date:
  date: 2026-08-14
  stage: not-stated
  note: "no stage vocabulary at all ('GLM-5.3 is now available to all GLM Coding Plan users'); the day is third-party-corroborated (unite.ai, marktechpost, both 2026-08-14), Z.ai's own blog being unfetchable (JS shell). Open weights announced but held back for a 'two-week safety evaluation and hardening period' (verified 2026-08-26)"
context_window: 1000000
max_output: 128000
pricing:
  input: 1.4          # USD per MTok — base list rate (see the registry's rule)
  output: 4.4
  currency: USD
  regime: flat
  note: "$1.40 / $4.40 per MTok — same list price as GLM-5.2 and 5.1; base GLM-5 sits at $1 / $3.20, GLM-5-Turbo $1.20 / $4.00 (verified 2026-08-26)"
knowledge_cutoff:
  date: null          # the limit date on training data
  basis: not-stated
  note: "not stated — the model guide carries no cutoff, and no HF model card exists yet to check (checked 2026-08-26)"
model_features:   # nested per ADR-0014; reasoning keys split per ADR-0040
  reasoning: true
  reasoning_type: always-on    # "GLM-5.3 always operates with reasoning enabled"; thinking.type: disabled is "no longer supported"
  reasoning_effort: "levels:low/high/max@max"   # 'Deep Reasoning' — identical surface and default to Kimi K3
  prompt_caching: "cached input $0.26 per MTok (≈0.19x of the $1.40 input rate); cached-input storage 'Limited-time Free' (undated); mechanism described only as 'intelligent caching' — no TTL, no explicit-breakpoint surface stated"
  batch_discount: "no batch API found on the pricing page or model guide (checked 2026-08-26); the guide's off-peak '50% of the standard points' is GLM Coding Plan subscription quota, not API pricing — don't conflate it with DeepSeek's off-peak API rates"
  fast_mode: false   # checked and absent: the pricing page lists input/cached-input/storage/output only; GLM-5-Turbo is a sibling model, not a serving mode of 5.3 (verified 2026-08-27)
checked: 2026-08-26
depth: stub
---

# GLM-5.3

Z.ai's coding/agent flagship: 1M context, 128K max output, always-on reasoning with
a three-level `reasoning_effort` (default `max`). Launched API-first on 2026-08-14
with the open weights explicitly **held back two weeks for a safety evaluation** —
Z.ai's stated reason is that the model "developed offensive security capability
faster than expected, with its largest gains on the exploitation end of the chain."
Same base model as GLM-5.2; Z.ai attributes every capability gain to scaled-up
post-training.

## The category-1 axes (taxonomy §1)

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | · (supported; unmeasured) |
| Long-horizon coherence | · |
| Usable context (vs advertised) | 1M advertised; unprobed |
| Cost per completed task | · — list $1.40 / $4.40 per MTok puts it between DeepSeek V4 Pro and the Western mid-tier (Sonnet 5 $2 / $10); with `reasoning_effort` defaulting to `max`, list price understates realized cost more than usual |
| Release mode & access routes (1b) | **api-only today, `both` announced**: first-party API live 2026-08-14, weights promised "downloadable by anyone" after a two-week safety hold. The zai-org HF org has published every prior 5.x line (GLM-5, 5.1, 5.2, each with FP8 variants), so the precedent supports the promise |

**Prediction (dated, falsifiable):** a `zai-org/GLM-5.3` repo appears on Hugging Face
by **2026-08-31** (the announced two-week hold from 2026-08-14 ends ~08-28; +3 days
slack). Score this at the next re-read; if it lands, flip `access` to `open-weights`
and read the license before any "open" claim stronger than "downloadable". (Restated
2026-08-26: the prediction was written against `release_mode: both`, retired by
ADR-0046 — the claim, the date and the falsifier are unchanged.)

## Reasoning surface

What the three reasoning cells rest on, verified 2026-08-26 against the model guide
(carried verbatim from the free-text `thinking`/`effort_control` cells those keys
replaced, ADR-0040): *"always-on — 'GLM-5.3 always operates with reasoning enabled';
`thinking.type: disabled` is 'no longer supported', and the migration note tells 5.2
users to flip disabled→enabled before upgrading"* and *"`reasoning_effort`: low/high/max,
default MAX ('Deep Reasoning') — the same surface and same most-expensive default as Kimi
K3, ending K3's run as the sweep's only default-to-max."*

Z.ai is the clean specimen of the vendor split this repo's key names had to resolve: the
prose says *reasoning*, the parameter is still called `thinking.type`.

## Role in this repo's work

None run. Z.ai appears in the repo's orbit only as an API *route* in
llm-coding-benchmark's roster (see [`README.md`](README.md) § References) — earlier
GLM models, not 5.3.

## Surprises

1. **The weights delay is a first-party negative-capability disclosure.** Z.ai
   publicly stated its own model gained offensive-security (exploitation-end)
   capability faster than expected and gated the weights on a hardening period —
   the same publish-negative-results epistemics this repo credits in tools, applied
   to a frontier model release. No other vendor in the sweep has staged weights
   behind a safety hold with a stated reason.
2. **Default `reasoning_effort: max` is no longer unique to Kimi K3.** GLM-5.3
   ships the identical low/high/max surface with the identical most-expensive
   default — two Chinese vendors now bet that agent workloads want maximum
   reasoning unless told otherwise, while every Western vendor defaults lower.
   (kimi-k3.md's "only default-to-most-expensive" claim amended, dated.)
3. **Reasoning became non-optional mid-family.** 5.2 accepted
   `thinking.type: disabled`; 5.3 rejects it, and the docs carry a migration note
   telling users to flip the parameter before upgrading. A capability *removal*
   (the off switch) shipped inside a point release — version-pinning behavior worth
   remembering when a harness hardcodes thinking params.
4. **Point-release pricing creep, flat within the generation:** 5.1, 5.2, and 5.3
   all list $1.40 / $4.40, a step up from base GLM-5's $1 / $3.20 — the vendor
   prices the *generation line*, not the individual point release.

## Open questions

- Weights license and parameter count — unknowable until the HF repo lands; check
  against the prediction above.
- Knowledge cutoff — not stated anywhere first-party found; re-check the HF model
  card when it exists.
- Does "intelligent caching" have a TTL or explicit-breakpoint surface? The docs
  don't say; the $0.26 cached rate (≈0.19x) is mid-pack (Anthropic/OpenAI 0.1x,
  Grok 0.15x).
