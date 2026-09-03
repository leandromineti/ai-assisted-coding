---
name: glm-5.3
category: 1
maker: Z.ai (Zhipu AI)
url: https://docs.z.ai/guides/llm/glm-5.3
license: "GLM-5.3 License — bespoke, named after the model (the sweep's third such, after Kimi K3's and qwen3.8-max's; LICENSE file read 2026-08-31). Not OSI-shaped: its distinctive term is a Model-as-a-Service gate — a licensee whose aggregate revenue exceeds $10B 'must pass Z.AI's security review before using the Software' — which rhymes with the offensive-security rationale for the weights delay. No attribution requirement, no output/synthetic-data clauses"
access: open-weights   # FLIPPED from closed-source 2026-08-31 per the report's own dated prediction, which scored a HIT (see § the prediction, scored) — weights landed 2026-08-25
model_id: glm-5.3 (API); weights zai-org/GLM-5.3 (+ GLM-5.3-Flash sibling, and -BF16 variants of both; all created 2026-08-25 — supersedes the 2026-08-26 no-repo check)
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
  note: "not stated — the model guide carries no cutoff (checked 2026-08-26); the HF card, once it existed, was read 2026-08-31 and is also silent: no cutoff or training-data date anywhere on zai-org/GLM-5.3"
model_features:   # nested per ADR-0014; reasoning keys split per ADR-0040
  reasoning: true
  reasoning_type: always-on    # "GLM-5.3 always operates with reasoning enabled"; thinking.type: disabled is "no longer supported" — OBSERVED 2026-08-31 (issue #42 probe): sending it returns error 1210, 'This model always engages in thinking and cannot be disabled; please use low, high, or max' — the refusal also names the exact low/high/max level set the reasoning_effort cell records
  reasoning_effort: "levels:low/high/max@max"   # 'Deep Reasoning' — identical surface and default to Kimi K3
  prompt_caching: "cached input $0.26 per MTok (≈0.19x of the $1.40 input rate); cached-input storage 'Limited-time Free' (undated); mechanism described only as 'intelligent caching' — no TTL, no explicit-breakpoint surface stated"
  batch_discount: "no batch API found on the pricing page or model guide (checked 2026-08-26); the guide's off-peak '50% of the standard points' is GLM Coding Plan subscription quota, not API pricing — don't conflate it with DeepSeek's off-peak API rates"
  fast_mode: false   # checked and absent: the pricing page lists input/cached-input/storage/output only; GLM-5-Turbo is a sibling model, not a serving mode of 5.3 (verified 2026-08-27)
  stop_sequence_honesty: "inconclusive — OBSERVED 2026-09-03: the triggering call returned empty visible text at this budget, so truncation itself was never confirmed against the trigger word in this sweep, and the shared openai_compat stop finish value matches the no-stop control's own finish reason regardless, cell_id:`glm-5.3--stop-truncation--triggering--default`, probe_id:`glm-5.3--stop-truncation--triggering--default--01466ba7`, promoted ADR-0050."
  seed_determinism: "0/5 same-seed pairs (no-signal) — OBSERVED 2026-09-03: glm-5.3's five same-seed repeats each hit reasoning-length exhaustion before producing a comparable visible completion, so the 0/5 rate reflects exhausted budget, not observed variation, cell_id:`glm-5.3--seed--42--default`, probe_id:`glm-5.3--seed--42--default--r1--5d9fe9d0`, promoted ADR-0050."
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
| Release mode & access routes (1b) | **Both, as of 2026-08-25**: first-party API live 2026-08-14; weights on HF eleven days later (`zai-org/GLM-5.3`, 753B total params per the card, + a GLM-5.3-Flash sibling and BF16 variants). The earlier "api-only today, `both` announced" reading held for eleven days and resolved per the scored prediction below |

**Prediction (dated, falsifiable):** a `zai-org/GLM-5.3` repo appears on Hugging Face
by **2026-08-31** (the announced two-week hold from 2026-08-14 ends ~08-28; +3 days
slack). Score this at the next re-read; if it lands, flip `access` to `open-weights`
and read the license before any "open" claim stronger than "downloadable". (Restated
2026-08-26: the prediction was written against `release_mode: both`, retired by
ADR-0046 — the claim, the date and the falsifier are unchanged.)

**Scored 2026-08-31 — HIT, early.** The repo was created **2026-08-25** (HF API
`createdAt`), inside the window with six days to spare — and *before* the announced
two-week hold would even have elapsed (~08-28). So the vendor beat its own stated
timeline: the safety hold ran eleven days, not fourteen. Both follow-through
obligations the prediction carried were executed the same day: `access` flipped to
`open-weights`, and the LICENSE file was read before any stronger claim — it is a
bespoke **"GLM-5.3 License"**, and the caution about assuming the 5.x predecessors'
terms was warranted: its distinctive clause gates Model-as-a-Service use by licensees
above **$10B aggregate revenue** behind "Z.AI's security review" — the license
encoding the same offensive-security posture that delayed the weights. Calibration
note: the prediction's ceiling was chosen well (precedent-based: zai-org had published
every prior 5.x line), but the estimate assumed the vendor would use its full stated
hold; vendors under release pressure apparently don't. A `GLM-5.3-Flash` sibling
shipped in the same push — folded here per the family convention, not rowed.

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

- ~~Weights license and parameter count — unknowable until the HF repo lands; check
  against the prediction above.~~ **Resolved 2026-08-31**: GLM-5.3 License (bespoke,
  $10B-revenue MaaS security-review gate — see frontmatter), 753B total params per
  the HF card; **activated params remain unstated**, the residue of this question.
- ~~Knowledge cutoff — not stated anywhere first-party found; re-check the HF model
  card when it exists.~~ **Checked 2026-08-31**: the HF card exists and is silent
  too — cutoff stays `not-stated`, now with both first-party surfaces searched.
- Does "intelligent caching" have a TTL or explicit-breakpoint surface? The docs
  don't say; the $0.26 cached rate (≈0.19x) is mid-pack (Anthropic/OpenAI 0.1x,
  Grok 0.15x). *Partial observation 2026-08-31 (issue #42 probe): the surface is at
  least response-visible — `usage.prompt_tokens_details.cached_tokens` appears on a
  plain request — so hit rates are measurable even though the mechanism stays
  undocumented. TTL still unknown; probing it needs two spaced requests.*
