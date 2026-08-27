# Category 1 — Models

`checked: 2026-08-27`

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

The assessed block is **`model_features:`, 6 keys** (5 since 2026-08-26; `fast_mode`
added 2026-08-27, ADR-0049; counts below re-run over 13 models): `reasoning`,
`reasoning_type`, `reasoning_effort`, `prompt_caching`, `batch_discount`, `fast_mode`.
The weights
themselves are untraceable at this repo's level of analysis — which is why category 1
deliberately has no component decomposition — so what *is* assessable is the first-party
surface around them: the three keys that change how a harness can drive the model, and the
three that decide what a completed task costs. Each is verified against the report's `url`
on its `checked` date.

Since 2026-08-27 that framing is a **stated decision, not an accident of practice**
([ADR-0048](../../adrs/0048-category-1-assesses-api-versions-only.md), and the §1 scope
note in [`tool-taxonomy.md`](../../docs/tool-taxonomy.md)): every spec and assessed key
describes the **first-party API-served product**. A published weights release is
acknowledged — `access`, `license`, the HF id in `model_id`, its row in the 1b table —
and never assessed as a second subject, even where the vendor documents the two diverging
(qwen3.8-max, the forcing case).

Two of the three cost keys (`prompt_caching`, `batch_discount`) are free text in each
vendor's own vocabulary
([ADR-0014](../../adrs/0014-model-features-into-registry.md)): the economics differ
structurally across vendors and flattening them to ✓/✗ would erase the finding. The third,
**`fast_mode`** ([ADR-0049](../../adrs/0049-fast-mode-presence-key.md), 2026-08-27), is a
presence key and `batch_discount`'s inverse — batch trades speed for a discount, fast mode
buys output-token throughput at a premium for the *same* model (a fast sibling doesn't
count). It earns ✓/✗ where `reasoning` couldn't because it genuinely discriminates:
first sweep **3 ✓ / 9 ✗ / 1 ·**, and the ✓s are exactly Anthropic (`speed: "fast"`,
2.5× OTPS at 2× price, Opus-only), OpenAI (`service_tier: fast|priority` — priority
processing *renamed* fast mode 2026-07-30), and Google (Priority tier, ~1.8×). Every
non-Western maker checked has none — the near-mirror of `reasoning_effort`'s regional
split below: the West sells speed as the premium add-on, the Chinese makers spend the
premium on reasoning by default. The three
reasoning keys are **typed**, and they discriminate here for a reason worth stating
([ADR-0040](../../adrs/0040-reasoning-replaces-thinking.md), 2026-08-26 — they replace a
single free-text `thinking` key that held four independent facts at once):

- **`reasoning`** (presence) — does the model generate reasoning tokens at all. The honest
  base fact, and a **weak discriminator today**: 10 present, 1 absent (qwen3-coder-next)
  — **12 present, 1 absent of 13 after the two Qwen3.8 additions** (2026-08-27), i.e.
  weaker still. Recorded as weak rather than quietly dropped — it is the fact the
  other two are conditional on, and non-reasoning models ship again.
- **`reasoning_type`** (closed enum) — `always-on` · `default-on` · `opt-in` · `none`.
  **Toggleability**, chosen over Anthropic's adaptive-vs-extended axis because every
  vendor states it and only three state theirs. Nothing is lost: adaptive-vs-extended is
  the question of who *sizes* the reasoning, and that surfaces below.
- **`reasoning_effort`** (`family:specific`) — the caller-facing depth dial. The family is
  who sizes it: `levels:<set>@<default>` (the model spends against a level) or
  `budget:<unit>` (the caller allocates up front — Haiku 4.5 is the sweep's only one).
  Deliberately *not* a ✓/✗: ten of eleven models have a dial, and the eleventh is
  qwen3-coder-next, so a boolean would have reproduced the `reasoning` column exactly —
  an instrument that cannot discriminate cannot measure (methodology rule 5d). The
  variation is in the level set and the default, which is why both live in the cell:
  `@high` mostly, `@medium` at OpenAI, **`@max`** at Kimi K3 and GLM-5.3. **2026-08-27:**
  twelve of thirteen, and the most-expensive-default group is now four models across three
  makers — Kimi K3 and GLM-5.3 at `@max`, both Qwen3.8 models at `@xhigh` (their top
  level). Every Western model still defaults lower. The level *sets* have stopped
  converging too: Qwen's `low/medium/xhigh` overlaps Anthropic's five-level set only
  partially, and qwen3.8-flash silently promotes the two names it doesn't implement
  (`high`, `max`) to `xhigh`.

**All three keys are now 11/11** (2026-08-26). The reshape left five cells at `·`, all
Anthropic; [issue #38](https://github.com/leandromineti/ai-assisted-coding/issues/38)
closed them the same day against two first-party pages —
[`/build-with-claude/effort`](https://platform.claude.com/docs/en/build-with-claude/effort)
and the per-model configuration table at
[`/build-with-claude/thinking-troubleshooting`](https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting#supported-models).
Neither is the `url` those four reports point at: **the models overview table carries
neither fact**, so the surface that answered the knowledge-cutoff question was the wrong
one here. The three Anthropic frontier models turn out to share one dial —
`levels:low/medium/high/xhigh/max@high`, `output_config.effort` — while differing on
toggleability, which is exactly the separation the split was for.

Two things that pass came out of it, both recorded rather than smoothed over:

- **The enum has a known strain point.** Opus 5 is `default-on`, but conditionally: the
  docs reject `thinking: {type: "disabled"}` at effort `xhigh` or `max` while accepting it
  at `high` or below. Toggleability is therefore not always a static per-model property —
  here it is a function of another parameter in the same request. `default-on` is the
  honest cell; the condition lives in the report. If a second vendor ships the same shape,
  that is the two-instance bar for revisiting the enum.
- **The two Haiku 4.5 cells were derivations, and both were confirmed.** The reshape read
  `opt-in` / `budget:tokens` out of the old cell's *"extended (budget_tokens)"*; the
  per-model table independently gives Default **Off**, and effort's supported-models list
  excludes Haiku 4.5 outright. A derivation that survives its own check is worth noting —
  the ones that don't are why the other three cells stayed `·` instead.

**2026-08-27 — 13 models, and the first blank that isn't ignorance.** Adding
[qwen3.8-max](qwen3.8-max.md) and [qwen3.8-flash](qwen3.8-flash.md) leaves `reasoning`
**13/13** and `reasoning_effort` **13/13**, but `reasoning_type` at **12/13**: the flagship
is documented as *Hybrid* ("toggle thinking on or off per request with `enable_thinking`"),
which excludes `always-on`, and no first-party surface states its **default** — the one
thing the enum encodes. Qwen states that default for the open weights and for the Flash
sibling, and not for the flagship. The cell was left empty rather than guessed, at a real
cost: the matrix renders `·`, which this repo reads as *not checked*, and this was checked.

That is a **second, different strain on the same enum** — the Opus 5 case above is
toggleability being conditional on another parameter; this is toggleability being
*undocumented* while adjacent models document it. The two-instance bar for revisiting a
vocabulary is met in spirit but not in kind, so the queued question is narrower than a new
enum value: does `reasoning_type` need a `not-stated` marker of the sort `release_date.stage`
and `knowledge_cutoff.basis` already carry, so that "checked, vendor silent" stops
rendering as "unchecked"? One more instance and it stops being a question.

The other half of the surface is **9 transcription fields** — `maker`, `license`,
`access`, `model_id`, `release_date`, `context_window`, `max_output`, `pricing`,
`knowledge_cutoff` — facts copied from a dated source rather than judged.

Both halves are read as **four groups** — Identity · Capacity · Cost · Reasoning — and
each opens with what it is about and how its keys read together: [`feature-registry.md`
§ Models](../../comparisons/feature-registry.md#models). The groups cross the assessed/transcribed line on purpose;
the **Basis** column is what marks it.

Definitions for every key:
[`comparisons/feature-registry.md`](../../comparisons/feature-registry.md). Values:
[`comparisons/features.md § Models`](../../comparisons/features.md#models-category-1) and
the fuller [`comparisons/models.md`](../../comparisons/models.md). A key is set **only**
when verified — omitted means "not checked", `false` means "checked and absent", and both
are claims.

## Inventory

| Model | Maker | Release | One-line |
|-------|--------|---------|----------|
| [**Fable 5**](claude-fable-5.md) | Anthropic | GA 2026-06-09 (suspended 06-12, redeployed ~07-01) | Frontier tier; always-on adaptive reasoning; ~30% tokenizer inflation vs pre-4.7 models; domain-gated Mythos 5 twin. $10/$50. |
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
| [**Qwen3.8-Max**](qwen3.8-max.md) | Alibaba | API 2026-08-03, no stage stated (the same changelog says "General Availability" for another model — the omission is a choice) | Added 2026-08-27. The line's actual flagship: **2.4T total / 95B activated**, native vision, 1M served context, $2/$6. Weights published (`Qwen3.8-2.4T-A95B`) under a **bespoke `qwen3.8-max` license** — and the card says the API adds vision, non-thinking mode, 1M-by-default and built-in tools *over* them. `reasoning_type` is the sweep's first deliberately-blank cell: Hybrid is verified, the default is unstated. |
| [**Qwen3.8-Flash**](qwen3.8-flash.md) | Alibaba | API 2026-08-26, no stage stated (the changelog prints the year as **2025** — a first-party typo, reconstructed from its own ordering) | Added 2026-08-27. **The cheapest model in the sweep** — $0.15/$0.47, 1M ctx, multimodal. Production form of `Qwen3.8-Flash-Next` (125B total / **6B activated** + a 51B n-gram embedding layer the Qwen team frames as a Qwen4 preview), so `access` is `closed-source`: the served weights are not published, a preview relative's are. Silently promotes `high`/`max` effort to `xhigh`. |

## Type 1b — Model access

| Route | One-line |
|-------|----------|
| First-party APIs | Anthropic, OpenAI, Google, xAI (`console.x.ai`). Reference behavior; caching and rate limits as designed. |
| Aggregators / routers | OpenRouter, Models.dev. One key, many models — at the cost of an extra hop and inconsistent caching support. |
| Cloud marketplaces | AWS Bedrock, GCP Vertex. Procurement and data-residency plays; feature lag is common. |
| Local runtimes | Ollama, llama.cpp, vLLM. Only viable for open-weight models, and quantization changes behavior under the same model name. *(acknowledged, not assessed — ADR-0048)* |

**Why this type matters:** the same model name reached by different routes is not the
same product. Prompt-caching support, quantization, rate limits, and silent context
truncation all vary by route — and in the extreme case the routes carry different
artifacts outright (qwen3.8-max's API adds vision, non-thinking mode, and 1M-default
context over its published weights, per the vendor's own card).

**These are acknowledged routes, not assessed subjects** (2026-08-27,
[ADR-0048](../../adrs/0048-category-1-assesses-api-versions-only.md)): every assessment
in this category binds to the first row. The other three exist here so a reader knows
route variance is real before blaming a model for its route.

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

- **Anthropic system cards** —
  [`anthropic.com/system-cards`](https://www.anthropic.com/system-cards) (index verified
  2026-08-26, HTTP 200). A **different genre from a model card**, and the differences are
  load-bearing:
  - **Safety-evaluation documents, and long.** The one opened to ground this entry —
    `System Card: Claude Opus 4 & Claude Sonnet 4`, May 2025 — runs **123 pages**, with
    training data and process as one subsection among dozens. A DeepMind model card is
    ~10 pages of specs.
  - **One card can cover several models** — that example covers two in a single document.
    Which is exactly why a card note's `models_covered` is a list, and the same axis that
    produced the Grok 4.5/4.6 retraction.
  - **URLs are content-addressed** (`www-cdn.anthropic.com/<40-hex>.pdf`), which inverts
    the mutability risk. A DeepMind card is rewritten at a stable URL, so the bytes move
    under you; an Anthropic card's bytes are pinned by its own name, but the *index* can
    repoint to a new hash and leave the old URL unreferenced. The snapshot guards a
    different failure: not silent revision, but silent replacement.
  - The index renders its labels client-side — raw HTML exposes only the PDF URLs — so
    mapping a model to its card means opening the page.

  **Checked 2026-08-26 for two of the four tracked Claude models, and they disagree:**
  the [Opus 5 card](../../references/cards/2026-claude-opus-5.md) (198 pp) states *"Claude
  Opus 5's knowledge cutoff date is May 2026"* in §1.1; the
  [Sonnet 5 card](../../references/cards/2026-claude-sonnet-5.md) (146 pp, same §1.1
  heading, three weeks earlier) has **zero occurrences of "cutoff"** and gives its training
  data's sources and methods without a date. So within Anthropic the cards are an
  inconsistent specs surface and **the docs table is the reliable one** — it carries both
  cutoff fields for every model, as structured data, in one fetch.

- **Anthropic API docs beat the system cards for specs, and it isn't close.**
  [`docs.claude.com/en/docs/about-claude/models/overview`](https://docs.claude.com/en/docs/about-claude/models/overview)
  ships the model table as structured data — one page, every model, with
  `reliableKnowledgeCutoff` **and** `trainingDataCutoff` as separate fields (plus
  `releasedOn`, `contextWindowTokens`, `maxOutputTokens`, `thinking`, `defaultEffort`,
  and a full `pricing` block). All four tracked models re-verified there 2026-08-26 in a
  single fetch. The system cards would have meant opening 123-page PDFs whose model→card
  mapping the index does not even expose in HTML. **Cards are for depth — training
  process, safety evaluations, the reasoning behind a release; the docs are for specs.**
  Where Google splits the same information across two surfaces and states the cutoff only
  on the card, Anthropic states it in the docs and elaborates in the card.

  The pair of fields is worth carrying into the notes, because Anthropic distinguishes
  them: knowledge cutoff is *"the date through which the model's knowledge is most
  extensive"*, training data cutoff is *"the broader range of data used"*. **Haiku 4.5 is
  the specimen where they diverge** — 2025-02 vs 2025-07, five months — while the three
  Claude 5 models have them equal. A single-date field would have flattened that.

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
- ~~Does open-weight parity (Kimi K3) actually change anything practical, given that
  self-hosting a 2.8T-param model is out of reach for an individual?~~ **Closed by scope
  2026-08-27** ([ADR-0048](../../adrs/0048-category-1-assesses-api-versions-only.md)):
  answering it would mean assessing the self-hosted route, which this category
  deliberately does not. The question was pointing at a real asymmetry — that is now
  recorded as the scope note's falsifier rather than an open probe.
