---
name: gpt-6-astra
category: 1
maker: OpenAI
url: https://developers.openai.com/api/docs/models/gpt-6-astra
license: proprietary
access: closed-source
model_id: gpt-6-astra
release_date:
  date: 2026-09-03
  stage: not-stated
  note: "launch post (openai.com/index/gpt-6-astra, published 2026-09-03, read via Wayback 20260904072121 — openai.com 403s non-browser fetchers): 'rolling out today to a limited set of organizations and over the coming days will become available to all ChatGPT Plus, Pro, Business, and Enterprise users, as well as through the OpenAI API, Microsoft Azure, and AWS Bedrock' — a staged rollout with no GA/preview stage word on any surface checked. Enterprise workspace access 'off by default at launch'. The API stage resolved itself fast: `gpt-6-astra` answered a completion on this repo's personal probe key 2026-09-04 (issue #43's gate)"
context_window: 1050000   # docs: "1,050,000 context window" — but max INPUT is 922,000 ("Maximum input tokens: 922,000"), an in-window asymmetry the single number can't carry; the .md docs twin states both (verified 2026-09-04)
max_output: 128000
pricing:
  input: 10          # USD per MTok — base list rate (see the registry's rule)
  output: 50
  currency: USD
  regime: context-tiered
  note: "$10 / $50 per MTok base; 'Prompts with more than 272K input tokens are priced at 2x input and cache rates and 1.5x output for the full request' → $20 / $75 above the threshold. Cached input $1 (0.1x), cache writes $12.50 (1.25x). Batch AND Flex both 50%; fast mode 2x the applicable rates (stacks with the long-context tier: $40/$4/$50/$150). Data-residency endpoints +10% for models released on/after 2026-03-05. Verified 2026-09-04"
knowledge_cutoff:
  date: 2026-04-30          # the limit date on training data
  basis: vendor-stated
  note: "docs model page: 'Apr 30, 2026 knowledge cutoff' — day-level, docs-page-ONLY: the system card states no date ('cutoff' occurs once in its full text, dating nothing — checked absence, card note references/cards/2026-gpt-6-astra.md). Verified 2026-09-04"
model_features:   # nested per ADR-0014 (2026-08-19); reasoning keys split per ADR-0040
  reasoning: true
  reasoning_type: always-on   # reasoning guide, verified 2026-09-04: "does not support `none` reasoning effort. Setting `reasoning.effort` (Responses) or `reasoning_effort` (Chat Completions) to `none` returns HTTP 400" — and the system card states the withholding is deliberate: "Note we do not currently have plans to make reasoning=None available"
  reasoning_effort: "levels:low/medium/high/xhigh/max@medium"   # levels docs-verified 2026-09-04; the DEFAULT is stated on NO first-party surface (model page, reasoning guide, latest-model guide, API reference, launch post, system card all checked — the guide even warns "Defaults are also model-dependent rather than universal") and was settled by OBSERVED probe 2026-09-04: a Responses call omitting effort echoed reasoning:{effort:"medium", mode:"standard", context:"all_turns"} — the docs→probe escalation route, same as qwen3.8-max's reasoning_type. Mid-run effort change exists (`configuration_update`), Astra-only, "standard, single-agent mode", changes only reasoning effort
  prompt_caching: "cached input $1 per MTok (0.1x); cache writes $12.50 (1.25x uncached input rate) — and both double above the 272K long-context threshold (verified 2026-09-04)"
  batch_discount: "50% in+out ($5 / $25 per MTok) — and a Flex tier priced identically to Batch (verified 2026-09-04)"
  fast_mode: true   # `service_tier: "fast"` or `"priority"` ("Priority processing was renamed Fast mode on July 30, 2026"), 2x price per the pricing table. The SPEED claim is launch-post-only for this model ("up to 2x the speed of Standard processing at 2x the Standard price") — the docs' 2.5x banner figure is scoped to gpt-5.6-sol, not Astra. No latency SLA for Astra; unsupported with EU data residency; under ramp limits requests "may downgrade… to standard speeds and charge standard rates", detectable only by reading service_tier back off the response (verified 2026-09-04)
checked: 2026-09-04
depth: stub
---

# GPT-6 Astra

OpenAI's new flagship, launched 2026-09-03 as a **staged rollout** with no stage
word — "a limited set of organizations" first, everyone else "over the coming days"
— which made it the gate for this repo's three-model roster batch
([issue #43](https://github.com/leandromineti/ai-assisted-coding/issues/43)): the
batch started the day `gpt-6-astra` answered on the personal probe key
(2026-09-04, one day after launch). An unpriced sibling, **GPT-6 Astra Pro**, is
ChatGPT-plans-only: no API page (the models URL 404s), no pricing row, zero
mentions in the models index — not a candidate until a first-party API surface
exists (ADR-0048).

Two access programs bracket the model's safety posture: it is the first model
OpenAI ships at its **Critical cyber threshold** (refuses proof-of-concept exploit
work at launch), with a **"Daybreak"** program to relax those safeguards for vetted
users — the third use-domain-gated access shape in the sweep, after Anthropic's
Mythos line and Google's Fairwind/Flash-Cyber.

## The category-1 axes (taxonomy §1)

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | · — but the *contract* is unusual: "GPT-6 Astra supports Chat Completions, but tool calling requires Responses" — a hard constraint for any harness built on Chat Completions |
| Long-horizon coherence | · — the launch post's benchmark tables run MRCR at 512K–1M; nothing measured here |
| Usable context (vs advertised) | The docs themselves split the number: 1,050,000 window, **922,000 max input** — the advertised/usable gap stated first-party, before any measurement |
| Cost per completed task | Context-tiered: everything doubles above 272K input (output 1.5x), so long-agentic-session cost is nonlinear in a way flat-rate models aren't |
| Release mode & access routes (1b) | Staged rollout, no stage vocabulary; OpenAI API + Azure + AWS Bedrock; Enterprise off-by-default; Astra Pro plans-only; Daybreak program gates the cyber ceiling |

## Reasoning surface

- `reasoning.effort` (Responses) / `reasoning_effort` (Chat Completions):
  **`low/medium/high/xhigh/max`**, `none` → HTTP 400. The level set now matches
  Anthropic's five names exactly — the first non-Anthropic model to carry `xhigh`
  and `max`.
- **The default is documented nowhere** — five docs surfaces plus the launch post
  and system card checked, and the reasoning guide states defaults are
  model-dependent, then gives them only for gpt-5.5 and GPT-5.6. Settled by a
  single omitted-effort Responses probe (2026-09-04): the response echoes
  `reasoning: {"effort": "medium", "mode": "standard", "context": "all_turns"}`.
  `@medium` keeps OpenAI the only Western maker defaulting below `high`.
- The card documents *why* reasoning is mandatory: no-CoT capability "may have
  increased by about an order of magnitude", shrinking the monitorable surface —
  a rare first-party rationale for a withheld knob.
- Sampling knobs are gone: the migration guide says "Remove `temperature`,
  `top_p`, and `top_logprobs`." Directly relevant to the wire-behavior probes when
  the roster forks — the sampling-repeatability substitute row (the Fable 5 shape)
  will fire here too.

## Misalignment monitoring stops API tasks

The fact of most unusual interest to this repo, first-party on two surfaces
([card note](../../references/cards/2026-gpt-6-astra.md) + a dedicated docs guide):
production misalignment monitoring "can automatically pause or end the affected
conversation", API tasks included, and "Some conversations, including those stopped
through the API, cannot be resumed." The docs give the exact wire contract: **HTTP
403, error type `invalid_request_error`, code `misalignment_policy_violation`** —
"Match the error code rather than the message text", "Do not automatically retry
the blocked workflow", and "A stopped request does not undo earlier actions." It
can fire asynchronously, mid-stream, after output has been emitted.

Three consequences worth recording now:

1. **A new harness failure mode.** Agent loops need a non-retry path for one
   specific 403 code; a generic retry-on-403 makes it worse, per the vendor's own
   docs.
2. **An interface boundary:** the monitoring does not apply on Chat Completions —
   the same interface tool calling doesn't work on. The monitored surface and the
   agentic surface are deliberately the same one (Responses).
3. **Probe-able, carefully.** The *contract* (does an innocuous task stay clean;
   does the error shape match the docs) is wire-behavior territory; deliberately
   *triggering* the monitor is not something this repo's probes should do.

## Endpoint surface

Three endpoints supported — Chat Completions, Responses, Batch — and **all 14
others "Not supported"** in the docs' own endpoint table. The only snapshot is the
floating alias `gpt-6-astra` ("Default snapshot: `gpt-6-astra`", and the snapshot
list contains exactly that one name): **no dated model pin exists**, so re-checks
lean entirely on `checked:` dates, the same weakness this repo's rule 4b exists to
manage for git pins.

## Role in this repo's work

None yet. Ingested as the gate model of issue #43's roster batch. The six
ADR-0050 wire-behavior cells are deliberately absent until the probe roster forks
and the cells are fired (phase 2) — and this model brings two new probe-relevant
behaviors with it: the fast-mode silent-downgrade (`service_tier` echo is the only
tell) and the misalignment 403 contract above.

## Surprises

1. **A vendor publishing its own regression.** "GPT-6 Astra's monitorability has
   decreased relative to GPT-5.6 Sol" — the negative-result epistemics this repo
   credits in tools, from the largest vendor in the sweep.
2. **The docs moved under the report's feet.** `platform.openai.com/docs/*` now
   301s to `developers.openai.com/api/docs/*`, and the docs serve a Markdown twin
   at `<url>.md` that carries facts the HTML pass drops (the endpoint table's
   Supported markers, the max-input line). Recorded in the category README's
   first-party-surfaces section; the gpt-5-6-sol report's `url` now rides a
   redirect.
3. **Max input ≠ context window, stated first-party** (922K vs 1.05M). Other
   vendors leave the gap to be measured; OpenAI prints it.
4. **Seven service tiers** (`auto`, `default`, `flex`, `scale`, `priority`,
   `fast`, `ultrafast`) — `ultrafast` is a live enum value with no guide page,
   scoped to gpt-5.6-sol, access-controlled. The tier vocabulary is growing faster
   than its documentation.
5. **The benchmark tables score "Claude Fable 5.1"** — a same-week rival's model,
   before this repo had first-party sight of it. The sighting chain is recorded in
   [claude-fable-5-1](claude-fable-5-1.md); the pair gives the roster its first
   cross-vendor scoring instance.

## Open questions

- The six wire-behavior cells at probe time — especially: does the
  sampling-repeatability substitute fire (temperature removed), and does the
  service-tier contract expose the fast-mode silent downgrade?
- Does the misalignment 403 ever fire on innocuous agentic work? (The contract is
  probe-able; the trigger is out of scope.)
- Astra Pro: does a first-party API surface ever appear?
- The `configuration_update` mid-run effort change — "standard, single-agent
  mode" only: what does the restriction mean on the wire, and do harnesses use it?
- Cross-context-window notes in Codex (announced alongside Astra, "searchable
  earlier windows") — a categories-2/5 lead: harness-native memory absorption
  moving the way conclusion 8 predicts. Parked here so the sighting isn't lost;
  it belongs to a category-2 read, not this report.
