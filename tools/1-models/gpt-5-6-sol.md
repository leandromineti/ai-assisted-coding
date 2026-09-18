---
name: gpt-5-6-sol
category: 1
maker: OpenAI
url: https://developers.openai.com/api/docs/models
license: proprietary
access: closed-source
model_id: gpt-5.6-sol (alias gpt-5.6); siblings gpt-5.6-terra, gpt-5.6-luna — and, since 2026-08-07, gpt-5.6-cyber (the "OpenAI Daybreak" program, $12.50/$75, aliased `gpt-daybreak-red-latest`; `gpt-daybreak-blue-latest` points at Sol) — a sighting recorded here, not a fourth assessed tier (re-verified 2026-09-18)
release_date:
  date: 2026-07-09
  stage: ambiguous
  note: "the vendor's own two surfaces disagree on the same day: the launch forum post calls it a partner-restricted 'preview', the API changelog says 'Released' with no stage word, and no later GA statement exists (verified 2026-08-17; changelog half re-verified 2026-09-18 — still 'Released', still no stage word on the models index, model page, pricing page, changelog, or deprecations page; the forum post was not re-read)"
context_window: 1050000
max_output: 128000
pricing:
  input: 4          # USD per MTok — base list rate (see the registry's rule); PROMOTIONAL since 2026-08-21, see note
  output: 20
  currency: USD
  regime: context-tiered
  note: "Sol $4 / $20 per MTok since 2026-08-21 (was $5 / $30 at launch, verified 2026-08-17) — the vendor labels it PROMOTIONAL: 'GPT-5.6 Sol's promotional pricing is available at least through November 21, 2026' (changelog 2026-08-21 + pricing page, re-verified 2026-09-18), so a reversion to $5 / $30 after 2026-11-21 is a dated risk to score at the next re-check; Terra $2 / $12; Luna $0.20 / $1.20 (both unchanged, re-verified 2026-09-18); prompts >272k input tokens billed 2x in / 1.5x out for the whole request — Sol long-context $8 / $30 (re-verified 2026-09-18)"
knowledge_cutoff:
  date: 2026-02-16          # the limit date on training data
  basis: vendor-stated
  note: "Feb 16, 2026 (all three tiers) — re-verified 2026-09-18 on the Sol, Terra and Luna model pages ('Feb 16, 2026 knowledge cutoff'); the models page still carries no training-data cutoff field"
model_features:   # nested per ADR-0014 (2026-08-19); reasoning keys split per ADR-0040
  reasoning: true
  reasoning_type: default-on   # on unless disabled per request — `reasoning.effort: none` is the off switch
  reasoning_effort: "levels:none/low/medium/high/xhigh/max@medium"   # the sweep's only default below `high`; re-verified 2026-09-18 on the reasoning guide ('If you omit `reasoning.effort`, GPT-5.6 defaults to `medium` in both modes') — 'both modes' is a SECOND reasoning axis the enum does not carry: `reasoning.mode: standard|pro`, `standard` the default, `pro` billed at standard token rates (sighted 2026-09-18, unregistered vocabulary)
  prompt_caching: "automatic (explicit breakpoints opt-in from 5.6), read 0.1x, write 1.25x, 30m TTL, 1024-tok minimum — cached input Sol $0.40 (was $0.50 before the 2026-08-21 cut) / Terra $0.20 / Luna $0.02 per MTok; mechanics re-verified 2026-09-18 on the caching guide, which also states 5.6 is 30m-ONLY: the extended 24h / in_memory retention list stops at gpt-5.5"
  batch_discount: "50% in+out (Sol $2 / $10 since the 2026-08-21 cut, was $2.50 / $15; Terra $1 / $6, Luna $0.10 / $0.60 per MTok); long-context batch = 2x in / 1.5x out of standard batch (Sol $4 / $15) — the earlier '2x standard batch' wording was the input half only, corrected on re-verification 2026-09-18"
  fast_mode: true    # `service_tier: "fast"` (also accepts "priority" — priority processing RENAMED to fast mode 2026-07-30): Sol $8/$40 short-context, $16/$60 long; offered on all three 5.6 tiers (first-party pricing page, verified 2026-08-27); OBSERVED 2026-08-31 on gpt-5.6-luna: both tier values accepted, and the response reports `service_tier: "priority"` EITHER WAY — the rename is input-side only, the response vocabulary still speaks the old name; docs re-verified 2026-09-18, and the fast-mode guide now STATES what the probe observed — 'For GPT-5.6 and earlier models, the response returns `priority` whether the request specifies `priority` or `fast`' (the old priority-processing URL 301s to /guides/fast-mode); Sol-only 'Ultrafast mode' ('up to 14x faster than Standard', limited preview, no public price) announced 2026-08-13 is a named sighting, not a cell
  stop_sequence_honesty: 'n/a (parameter rejected at the contract sweep) — OBSERVED 2026-09-03: stop returns HTTP 400 in default mode, so no honesty verdict is reachable, probe_id:`gpt-5-6-sol--stop--["the"]--default--6a86352a`, promoted ADR-0050.'
  seed_determinism: "0/5 same-seed pairs (varies) — OBSERVED 2026-09-03: gpt-5-6-sol's seed field is accepted-unverified at the contract sweep; five same-seed repeat calls produced five distinct outputs, cell_id:`gpt-5-6-sol--seed--42--default`, probe_id:`gpt-5-6-sol--seed--42--default--r1--b19cbdbe`, promoted ADR-0050."
  sampling_repeatability: "0/4 repeat pairs (varies) — OBSERVED 2026-09-03: gpt-5-6-sol rejects an explicit temperature value outright in default mode (HTTP 400); this default-config-repeatability SUBSTITUTE asks whether the model's own default sampling is repeatable across five identical requests with no temperature parameter sent at all, and all five completed naturally with five distinct outputs, cell_id:`gpt-5-6-sol--default-config-repeatability--no-temperature--default`, probe_id:`gpt-5-6-sol--default-config-repeatability--no-temperature--default--r1--87b44491`, promoted ADR-0050."
  multi_candidate_delivery: "accepted-honored — OBSERVED 2026-09-03: a request for 2 candidates returned 2 — as with every domain model, the single-candidate case (n:1) is uniformly honored and only the multi-candidate request discriminates, cell_id:`gpt-5-6-sol--n--2--default`, probe_id:`gpt-5-6-sol--n--2--default--b94c8df8`, promoted ADR-0050."
  logprobs_delivery: "rejected — OBSERVED 2026-09-03: `logprobs` returns HTTP 400 at the contract sweep, probe_id:`gpt-5-6-sol--logprobs--true--default--c1192127`, promoted ADR-0050."
  service_tier_contract: "silently-translated — OBSERVED 2026-09-03: the presence probe's requested `auto` value comes back as a DIFFERENT resolved value at the response's own top-level `service_tier` field, probe_id:`gpt-5-6-sol--service-tier--auto--default--edca588c`; the value-enum row fires here (openai_compat family) — `default`/`priority`/`flex` are echoed (accepted-honored), only `auto` is translated, probe_id:`gpt-5-6-sol--openai-service-tier-values--default--default--3a9bd29a`; the BHV-06 tier audit confirms the response field stays flat and present at the top level with no nesting under a usage envelope — not the same asymmetric shape Anthropic and Gemini show, cell_id:`gpt-5-6-sol--service-tier-audit--auto--default`, promoted ADR-0050."
checked: 2026-09-18   # full docs-route re-verification (staleness sweep); the six wire-behavior OBSERVED cells keep their own 2026-09-03 dates
depth: stub
---

# GPT-5.6 Sol (and the 5.6 family)

OpenAI's frontier tier — "frontier model for complex professional work" — atop a
three-tier family sharing one 1.05M-token window and one Feb 2026 cutoff: **Sol**
(flagship, $4/$20 since the 2026-08-21 promotional cut; $5/$30 at launch), **Terra**
("intelligence and cost", $2/$12), **Luna** ("cost-sensitive workloads", $0.20/$1.20).
Since 2026-09-03 it is no longer OpenAI's top model: [GPT-6 Astra](gpt-6-astra.md) took
the "flagship" slot on the models index, and Sol's own page now reads "a flagship model
in the GPT-5.6 family" (re-verified 2026-09-18). The naming moved from version numbers to
celestial tiers — same structural move as Anthropic's capability ladder, made nominal.

**GPT-5.5 status resolved (2026-07-31):** no longer on OpenAI's current models page —
superseded by the 5.6 family. The Terminal-Bench 2.1 figures the category index cites
(Codex CLI + GPT-5.5, 83.4%) now describe a *retired* model; the benchmark-staleness
warning in the index applies to its own snapshot. **Retracted 2026-09-18:** the models
index lists both `GPT-5.5` and `GPT-5.5 Pro` with their own pages and live pricing
($5/$30 and $30/$180; the batch table carries them too). Whether the 2026-07-31 absence
was a page state or a misread cannot be told from here, so the claim is downgraded from
"retired" to "superseded and still sold" — the staleness warning survives in that
narrower form.

## The category-1 axes

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | · (vendor lists Functions/Web search/File search/Computer use on all tiers) |
| Long-horizon coherence | · |
| Usable context (vs advertised) | 1.05M advertised — the odd 50k over the round number suggests an exact power-of-two budget (2^20 ≈ 1.049M); unprobed |
| Cost per completed task | · — the 25× Sol/Luna price spread within one family is the widest in the sweep; where each tier's per-task crossover sits is unmeasured |
| Release mode & access routes (1b) | API-only; the models driving Codex CLI/cloud (category-2 pairing) |

## Reasoning surface

What the three reasoning cells rest on, verified 2026-08-17 (carried verbatim from the
free-text `thinking`/`effort_control` cells those keys replaced, ADR-0040): *"adaptive
(docs: fewer tokens for simpler tasks); disable per-request via `reasoning.effort: none`"*
and *"`reasoning.effort`: none/low/medium/high/xhigh/max, default medium — identical
across tiers; no 'minimal' on the 5.6 family."*

The only model in the sweep where the off switch lives *inside* the effort enum rather
than beside it — which is why `reasoning_type: default-on` and the `none` level in
`reasoning_effort` are the same fact seen from two sides. Its `@medium` default is also
the sweep's only one below `high`.

## Role in this repo's work

None directly — appears as the benchmark counterpart in the category-2 shelf (Codex CLI
pairings) and as Kimi K3's claimed comparison target. No repo work has run on it.

## Surprises

1. **A 25× intra-family price spread** (Sol $30 vs Luna $1.20 output) under identical
   context and cutoff — the vendor is pricing capability tiers, not infrastructure.
   (16.7× after the 2026-08-21 Sol cut; the point stands.)
2. GPT-5.5's quiet disappearance between benchmark publication and this check —
   leaderboard citations now point at a model you can't buy.
3. **Cache economics converged on Anthropic's exact multipliers** (2026-08-17): read
   0.1×, write 1.25× — the same two numbers, differing only in TTL (one fixed 30m vs
   Anthropic's 5m/1h pair). The effort ladder (`none`→`max`, default `medium`) is also
   a six-step version of the same control Anthropic exposes as `effort`. Convergence at
   the API surface, whatever the models are doing underneath.
4. **The flagship's price fell 20%/33% six weeks after launch and the vendor calls it
   promotional** (2026-08-21; re-verified 2026-09-18) — "available at least through
   November 21, 2026". The same shape as Sonnet 5's launch pricing, which was framed as
   introductory and then made standard. **Prediction (2026-09-18):** Sol's $4/$20 is
   still the list rate at the first re-check after 2026-12-31, i.e. the promo becomes
   standard rather than reverting — Astra's 2026-09-03 launch above it removes the
   reason to price Sol as a flagship. Score it then.
5. **A re-check retraction of its own**: the GPT-5.5 "retired" claim above did not
   survive its second look (see the intro). Counts and absences stated from one page
   read are exactly what the 30-day docs-route window exists to catch.

## Open questions

- What actually differs across Sol/Terra/Luna — distillation tiers of one base, or
  different models? (OpenAI discloses nothing.)
- ~~Where does codex-the-model line fit now — the models page lists no codex-specific
  SKUs with specs; are Codex surfaces driven by these same tiers?~~ **Corrected
  2026-09-18:** the models index does list codex SKUs with their own pages
  (`codex-mini-latest`, GPT-5-Codex, GPT-5.1-Codex / -Mini / -Max, GPT-5.2-Codex,
  GPT-5.3-Codex) — all pre-5.6, none in the featured block. The narrower question
  stands: is there a 5.6- or 6-era codex SKU, or do Codex surfaces now run the general
  tiers? (Nothing on the models index says either way.)
- Sol/Terra/Luna re-checked 2026-09-18 across the models index, the Sol page, pricing,
  reasoning, caching, batch, fast-mode and flex guides, changelog and deprecations
  (grepped for "distill", "base model", "tier", "family"): still nothing about a shared
  base. The only vendor framing is that Sol "roughly corresponds to the unsuffixed model
  tier used in earlier GPT-5 families".
