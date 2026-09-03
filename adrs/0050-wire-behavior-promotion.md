# ADR-0050 — Wire-behavior promotion: six keys from classified evidence to permanent registry vocabulary

`decided: 2026-09-03` · status: **accepted**

## Decision

Six probed parameters become permanent registry vocabulary — a new sixth `model_features`
group, **`wire-behavior`** (`order: 43`, between `reasoning` at 42 and `environment-binding`
at 50) — in this exact order, the canonical order the matrix column layout transcribes:

1. **`seed_determinism`** — whether requesting the same `seed`/`seed`-equivalent value across
   repeated calls produces byte-identical output. Domain: the 8 models that expose a
   request-side `seed` field (every tracked model except the 4 Claude models, which have none —
   `docs-claims:seed/anthropic`). Clears D-01 on the **combined** contract-plus-behavioral
   picture: the contract sweep shows `seed` uniformly `accepted-unverified` across its domain —
   a flat cell that would fail D-01's variance test on its own — and only the behavioral rate
   exposes that "accepted" never means "deterministic," while the classified *kind* of
   non-determinism still varies (`varies` vs `no-signal`, see below).
2. **`sampling_repeatability`** — whether the model's own default (implicit) sampling, or a
   real `temperature: 0` request where the model accepts one, repeats across calls. Domain: all
   12 tracked models — every model gets a cell, either a real `temperature: 0` test (7 models)
   or a `default-config-repeatability` SUBSTITUTE (5 models: `claude-fable-5`, `claude-opus-5`,
   `claude-sonnet-5`, `gpt-5-6-sol`, `kimi-k3`, all of which reject `temperature` outright in
   `default` mode) testing the model's own implicit sampling instead. The two designs are never
   conflated in a cell's context prose (Pitfall 1) — the design that fired is always named.
3. **`stop_sequence_honesty`** — whether the model's finish-reason field can distinguish a
   triggered `stop`-sequence truncation from a natural completion, independent of whether
   truncation itself is honored. Domain: the 10 models whose `stop` parameter the contract
   sweep accepts in `default` mode (`gpt-5-6-sol` and `grok-4-5` reject `stop` outright, HTTP
   400, and are out of this key's domain by construction, not a gap).
4. **`multi_candidate_delivery`** — whether requesting `n`/`candidateCount` > 1 candidates
   returns that many, is silently ignored, or is rejected. Domain: the 8 models with a
   request-side `n`/`candidateCount` field (the 4 Claude models have none —
   `docs-claims:n/anthropic`). `gemini-3-1-pro`'s cell is settled by its CONTRACT-layer
   rejection of `candidateCount`, not a behavioral re-test — see the precedence rule in
   § Cell-value grammar below.
5. **`logprobs_delivery`** — whether requesting `logprobs` returns per-token content, is
   silently ignored (accepted but empty), or is rejected. Domain: the 8 models with a
   request-side `logprobs` field (the 4 Claude models have none).
6. **`service_tier_contract`** — the joint fact of whether a `service_tier`/`serviceTier`
   request value is honored, silently translated, or ignored, AND whether the response side
   mirrors it at the top level, nests it under a usage envelope, or carries no response-side
   field at all. Per D-09, a promoted cell for this key cites BOTH the presence probe row
   (`service-tier`) and the value-enum row (`openai-service-tier-values`, `openai_compat`
   family only) plus the BHV-06 tier-audit cells — one wire field, two tested contracts, cited
   together because citing only one understates what was verified. Domain: all 12 models for
   presence; the `openai_compat` family (6 models) for the value enum; all 12 for the
   audit/asymmetry fact once BHV-06's per-model shape is known.

All six clear D-01's cross-model-variance test over the domain where each is grammatical, judged
over the **combined** contract-plus-behavioral evidence base — never contract acceptance alone.
`seed_determinism` is the sharpest illustration: uniform `accepted-unverified` at the contract
layer, real cross-model variance only once the behavioral rate is read (§ Context, item 1).

**All six are compact `value_type: string` cells (D-05), never an enum.** This is a deliberate
choice recorded here rather than assumed by copy-paste. The registry's own closed `value_type`
set distinguishes `string` — "a single identifier or name" — from `free-text` — "the vendor's or
subject's own words; no controlled vocabulary." The two annotated-string cells these six are
modelled on, `prompt_caching` and `batch_discount`, are both declared `free-text`; D-05 locks
these six to `string` instead, even though the worked cell shape (a rate/verdict token plus a
dated `OBSERVED` clause) visually resembles the `free-text` precedent. Nothing breaks either
way — `scripts/build-tool-index.py`'s registry validation checks only that `value_type` is a
member of the closed set (`VALUE_TYPES`), never that a report's actual cell string matches its
declared shape — so this is a taxonomic choice, not a mechanical constraint, and it is recorded
here so a future re-read finds a decision rather than an inconsistency between six `string`
cells and two visually similar `free-text` ones.

## Context

Per-key evidence, VERIFIED this session by direct read of `probes/classified/behavioral.yaml`
and `probes/classified/contract-sweep.yaml` (`13-RESEARCH.md § "The promoted set, mechanically
derived"`, re-confirmed against the classified YAML while drafting this ADR). Every row below
keeps its `cell_id`/`probe_id`.

### 1. `seed_determinism` (BHV-01, 8-model domain)

| Model | Rate | Verdict | cell_id |
|---|---|---|---|
| gpt-5-6-sol | 0/5 | varies | `gpt-5-6-sol--seed--42--default` |
| gemini-3-1-pro | 0/5 | varies | `gemini-3-1-pro--seed--42--default` |
| grok-4-5 | 0/5 | varies | `grok-4-5--seed--42--default` |
| kimi-k3 | 0/5 | no-signal (reasoning-length exhaustion, not a real signal) | `kimi-k3--seed--42--default` |
| deepseek-v4 | 0/5 | varies | `deepseek-v4--seed--42--default` |
| glm-5.3 | 0/5 | no-signal (reasoning-length exhaustion) | `glm-5.3--seed--42--default` |
| qwen3.8-max | 0/5 | varies | `qwen3.8-max--seed--42--default` |
| qwen3.8-flash | 0/5 | varies | `qwen3.8-flash--seed--42--default` |

The 4 Claude models are structurally out of this key's domain (no request-side `seed` field)
and carry the not-applicable head with the `no request-side field` reason.

### 2. `sampling_repeatability` (BHV-02, 12-model domain)

| Model | Design | Rate | Verdict | cell_id |
|---|---|---|---|---|
| claude-fable-5 | substitute | 0/4 | varies | `claude-fable-5--default-config-repeatability--no-temperature--default` |
| claude-opus-5 | substitute | 0/4 | no-signal | `claude-opus-5--default-config-repeatability--no-temperature--default` |
| claude-sonnet-5 | substitute | 0/4 | varies | `claude-sonnet-5--default-config-repeatability--no-temperature--default` |
| claude-haiku-4-5 | real temp=0 | 4/4 | deterministic | `claude-haiku-4-5--temperature--0--default` |
| gpt-5-6-sol | substitute | 0/4 | varies | `gpt-5-6-sol--default-config-repeatability--no-temperature--default` |
| gemini-3-1-pro | real temp=0 | 2/4 | partial | `gemini-3-1-pro--temperature--0--default` |
| grok-4-5 | real temp=0 | 0/4 | varies | `grok-4-5--temperature--0--default` |
| kimi-k3 | substitute | 0/4 | varies | `kimi-k3--default-config-repeatability--no-temperature--default` |
| deepseek-v4 | real temp=0 | 0/4 | varies | `deepseek-v4--temperature--0--default` |
| glm-5.3 | real temp=0 | 0/4 | no-signal | `glm-5.3--temperature--0--default` |
| qwen3.8-max | real temp=0 | 0/4 | varies | `qwen3.8-max--temperature--0--default` |
| qwen3.8-flash | real temp=0 | 0/4 | varies | `qwen3.8-flash--temperature--0--default` |

Only `claude-haiku-4-5` (4/4) and `gemini-3-1-pro` (2/4 partial) show any repeatability signal
at all — 10 of 12 models show zero, combined with item 1's own 8/8 zero — determinism is nearly
universally absent on the live wire (`docs/parameter-patterns.md`'s worked finding).

### 3. `stop_sequence_honesty` (BHV-03, 10-model domain — the tracer's own promoted key)

| Model | Truncation verdict | Finish-reason honest | Triggering probe_id |
|---|---|---|---|
| claude-fable-5 | stop-honored | **honest** | `claude-fable-5--stop-truncation--triggering--default--61baa082` |
| claude-opus-5 | stop-honored | **honest** | `claude-opus-5--stop-truncation--triggering--default--58a5a42f` |
| claude-sonnet-5 | stop-honored | **honest** | `claude-sonnet-5--stop-truncation--triggering--default--905e8ef4` |
| claude-haiku-4-5 | stop-honored | **honest** | `claude-haiku-4-5--stop-truncation--triggering--default--19f5c60f` |
| gemini-3-1-pro | stop-honored | ambiguous | `gemini-3-1-pro--stop-truncation--triggering--default--c83e86af` |
| kimi-k3 | stop-honored | ambiguous | `kimi-k3--stop-truncation--triggering--default--5b566140` |
| deepseek-v4 | stop-honored | ambiguous | `deepseek-v4--stop-truncation--triggering--default--970252c9` |
| glm-5.3 | **inconclusive** (empty visible text at budget, not re-fired) | ambiguous | `glm-5.3--stop-truncation--triggering--default--01466ba7` |
| qwen3.8-max | stop-honored | ambiguous | `qwen3.8-max--stop-truncation--triggering--default--67a34da7` |
| qwen3.8-flash | stop-honored | ambiguous | `qwen3.8-flash--stop-truncation--triggering--default--d1ae15ef` |

Truncation itself is nearly universal (9/10 clean, 1 inconclusive); the variance is in
`finish_reason_honest`: only the 4 Anthropic models report a distinguishable
`stop_reason: stop_sequence` vs. natural-completion value; every other tracked vendor shares one
generic finish value for both cases. `gpt-5-6-sol` and `grok-4-5` reject `stop` outright at the
contract layer (`gpt-5-6-sol--stop--["the"]--default--6a86352a`,
`grok-4-5--stop--["the"]--default--ee1a658f`, both HTTP 400) and carry the not-applicable head
with the `parameter rejected at the contract sweep` reason.

### 4. `multi_candidate_delivery` (BHV-04 + one contract cell, 8-model domain)

| Model | Requested | Returned | State | probe_id |
|---|---|---|---|---|
| gpt-5-6-sol | 2 | 2 | accepted-honored | `gpt-5-6-sol--n--2--default--b94c8df8` |
| gemini-3-1-pro | 2 (`candidateCount`) | — | **rejected** (contract, HTTP 400) | `gemini-3-1-pro--gemini-candidate-count--2--default--3d7b5857` |
| grok-4-5 | 2 | 2 | accepted-honored | `grok-4-5--n--2--default--10c7bf17` |
| kimi-k3 | 2 | 0 | rejected | `kimi-k3--n--2--default--141537ec` |
| deepseek-v4 | 2 | 0 | rejected | `deepseek-v4--n--2--default--53194c57` |
| glm-5.3 | 2 | 1 | **accepted-ignored** (silently returns only 1 of 2) | `glm-5.3--n--2--default--b1d9be3b` |
| qwen3.8-max | 2 | 0 | rejected (thinking-mode conditionality, docs-corroborated) | `qwen3.8-max--n--2--default--e510e3ee` |
| qwen3.8-flash | 2 | 0 | rejected (same conditionality) | `qwen3.8-flash--n--2--default--8df7372d` |

`gemini-3-1-pro`'s cell is settled by its own contract-layer rejection, not a behavioral
re-test — a parameter the maker rejects by name is a measured fact, not an absent one; the
derivation never substitutes a not-applicable head for a real rejection verdict.

### 5. `logprobs_delivery` (BHV-05 reverify + contract, 8-model domain)

| Model | State | Evidence source | probe_id |
|---|---|---|---|
| gpt-5-6-sol | rejected (HTTP 400) | contract | `gpt-5-6-sol--logprobs--true--default--c1192127` |
| gemini-3-1-pro | rejected (HTTP 400) | contract | `gemini-3-1-pro--logprobs--true--default--82d54982` |
| kimi-k3 | rejected (HTTP 400) | contract | `kimi-k3--logprobs--true--default--b9b3e6f3` |
| grok-4-5 | **accepted-ignored** (0 token entries, confirmed at a non-masking budget) | BHV-05 reverify | `grok-4-5--logprobs-reverify--combined--default--389d3fcc` |
| deepseek-v4 | accepted-honored | contract | `deepseek-v4--logprobs--true--default--3e9e0cfd` |
| glm-5.3 | **accepted-ignored** (0 token entries, confirmed at a non-masking budget) | BHV-05 reverify | `glm-5.3--logprobs-reverify--combined--default--d9f149fc` |
| qwen3.8-max | accepted-honored | BHV-05 reverify (agrees with contract) | `qwen3.8-max--logprobs-reverify--combined--default--97ef0c4f` |
| qwen3.8-flash | **accepted-honored — REVISED from Phase 11** | BHV-05 reverify | `qwen3.8-flash--logprobs-reverify--combined--default--4543428e` |

`qwen3.8-flash`'s Phase-11 contract cell (`qwen3.8-flash--logprobs--true--default--04bf05c1`)
classified `accepted-ignored`; the BHV-05 reverify at a larger, non-masking budget flipped the
verdict to `accepted-honored`. Per methodology rule 1a's evidence-grade ordering, the derivation
uses the BHV-05 (higher-grade, OBSERVED) value, never the stale Phase-11 contract classification.

### 6. `service_tier_contract` (D-09: cites BOTH `service-tier` and
`openai-service-tier-values` rows, plus BHV-06 tier-audit cells; 12-model domain for presence)

Presence (`probes/inventory.yaml:740-762`, all 12 models, contract layer): the 4 Claude models
and 5 of 6 non-`gemini` compat vendors (`kimi-k3`, `deepseek-v4`, `glm-5.3`, `qwen3.8-max`,
`qwen3.8-flash`) are `accepted-ignored`; `gpt-5-6-sol` and `grok-4-5` are `silently-translated`;
`gemini-3-1-pro` is tested under its own top-level `serviceTier` row.

Value enum (`openai-service-tier-values`, `openai_compat` family only, 4 values × 6 models):
`gpt-5-6-sol`/`grok-4-5` honor `default`/`priority`, silently translate `auto`, and split on
`flex` (honored at `gpt-5-6-sol`, silently translated at `grok-4-5`,
`grok-4-5--openai-service-tier-values--flex--default--5807985b`); the remaining 5 compat models
show all 4 values `accepted-ignored` uniformly.

**The asymmetry (BHV-06):** Anthropic's 4 models each show `response_field_path:
usage.service_tier` present, `response_top_level_present: absent`, plus a trap cell sending the
response-vocabulary word `standard` as a request value, rejected with HTTP 400 naming the field
(`claude-haiku-4-5--service-tier-audit--auto--default--613638b0`,
`claude-haiku-4-5--service-tier-audit--trap--default--8fc20f53`). Gemini independently shows the
structurally identical asymmetry — request field `serviceTier` (top level), response field
`usageMetadata.serviceTier` (nested) — across all 5 of its own audit cells
(`gemini-3-1-pro--service-tier-audit--flex--default`). `kimi-k3`/`deepseek-v4`/`glm-5.3`/
`qwen3.8-flash` show `response_present: absent` — no response-side tier field at all, a genuine
third state.

Registry entries and cells for keys 2 through 6 land in this same phase, after this ADR (keys 4
through 6 in plan 13-04, key 2 in plan 13-03); only `stop_sequence_honesty` (key 3) is written
by the tracer plan that carries this ADR.

## Considered, left matrix-only

Every key below shows real cross-model variance in the contract sweep (a mix of `rejected` and
`accepted-*` states over its grammatical domain) but carries no behavioral (rate-with-count)
verification — per D-02, "accepted-unverified is acceptance testimony, not verified behavior."
**Ten** keys, presented and reconciled explicitly here: the plan's own prose draft referred to
"nine," and that count is corrected in the plan's execution summary as a disclosed deviation —
the table below, matching RESEARCH.md's own D-03 table and CONTEXT.md D-02's own key list, has
ten rows.

| Key | Variance summary (unique models) | Reason left matrix-only |
|---|---|---|
| `top-p` | 6 `rejected` (`claude-fable-5`, `claude-opus-5`, `claude-sonnet-5`, `claude-haiku-4-5`, `gpt-5-6-sol`, `kimi-k3`) / 8 `accepted-unverified` | acceptance-only, no behavioral honor check |
| `top-k` | 5 `rejected` (`claude-fable-5`, `claude-opus-5`, `claude-sonnet-5`, `claude-haiku-4-5`, `gpt-5-6-sol`) / 8 `accepted-unverified` | same |
| `presence-penalty` | 4 `rejected` (`gpt-5-6-sol`, `gemini-3-1-pro`, `grok-4-5`, `kimi-k3`) / 5 `accepted-unverified`; skipped at all 4 Claude models (no field) | same |
| `frequency-penalty` | same shape as `presence-penalty` | same |
| `tool-choice` | 6 `rejected` (all 4 Claude + `gpt-5-6-sol`, `grok-4-5`) / 5 `accepted-unverified` | same |
| `response-format` | mixed `accepted-honored`/`accepted-ignored`/`needs-review`/`rejected` | acceptance state alone verified; conformance grading is out of scope (REQUIREMENTS.md exclusion) |
| `logit-bias` | 3 `rejected` (`gpt-5-6-sol`, `grok-4-5`, `kimi-k3`) / 4 `accepted-unverified`; skipped at all 4 Claude models | exhaustive vocabulary sweep out of scope |
| `top-logprobs` | 4 `rejected` (`gpt-5-6-sol`, `gemini-3-1-pro`, `kimi-k3`, `deepseek-v4`) / 4 `accepted-unverified` (`grok-4-5`, `glm-5.3`, `qwen3.8-max`, `qwen3.8-flash`); skipped at all 4 Claude models | acceptance-only; `logprobs` itself (promoted) carries the honor-verification burden |
| `parallel-tool-calls` | 1 `rejected` (`gpt-5-6-sol`) / rest `accepted-unverified` | same |
| `stream-options-include-usage` | 4 `rejected` (`gpt-5-6-sol`, `deepseek-v4`, `qwen3.8-max`, `qwen3.8-flash`) / rest `accepted-unverified` | same |

No key is dropped from this table silently — a future verification phase re-checks the promoted
set against it.

## Cell-value grammar

The formal contract every promoted-key OBSERVED cell obeys, and the exact contract
`scripts/check-probe-drift.py` parses. A cell is one string, of the shape:

```
<head> — OBSERVED <YYYY-MM-DD>: <context>, <citation>[, <citation> ...], promoted ADR-0050.
```

**`<head>` is one of three forms:**

1. **Rate head** — `<N>/<M> <unit phrase>`, optionally followed by a trailing parenthesised
   verdict token where the classified evidence distinguishes a real variation from a no-signal
   result: `<N>/<M> <unit phrase> (<verdict-token>)`. A rate is always carried as its two
   integers, never as a computed or rounded percentage.
2. **Bare verdict head** — a single closed verdict token drawn from the key's own vocabulary
   (below), with no rate.
3. **Not-applicable head** — `n/a (<reason>)`, where `<reason>` is exactly one of the two closed
   phrases: `no request-side field` (the vendor's API has no such parameter for this model) or
   `parameter rejected at the contract sweep` (the parameter exists but the contract sweep
   observed an outright rejection, so no honesty/delivery verdict is reachable).

**`<citation>` is one or more of** `` cell_id:`<id>` `` or `` probe_id:`<id>` ``, backtick-delimited
so an id containing brackets, quotes, or other punctuation (several `stop`-param probe_ids
literally embed a JSON array, e.g. `` `gpt-5-6-sol--stop--["the"]--default--6a86352a` ``) parses
unambiguously — the checker scans for these tokens rather than splitting on commas, since prose
context legitimately contains commas of its own.

**Three worked heads, from real evidence:**

- Rate head, real variation: `` 0/5 same-seed pairs (varies) — OBSERVED 2026-09-03: gpt-5-6-sol's
  seed field is accepted-unverified at the contract layer; five same-seed repeat calls produced
  five distinct outputs, cell_id:`gpt-5-6-sol--seed--42--default`, probe_id:`gpt-5-6-sol--seed--42--default--r1--b19cbdbe`,
  promoted ADR-0050. ``
- Rate head, no-signal (a zero rate that produced no signal is not the same fact as a zero rate
  that varied, and the grammar must be able to say so): `` 0/5 same-seed pairs (no-signal) —
  OBSERVED 2026-09-03: kimi-k3's five same-seed repeats each hit reasoning-length exhaustion
  before producing a comparable visible completion, so the 0/5 rate reflects exhausted budget,
  not observed variation, cell_id:`kimi-k3--seed--42--default`, probe_id:`kimi-k3--seed--42--default--r1--785f1743`,
  promoted ADR-0050. ``
- Not-applicable head: `` n/a (parameter rejected at the contract sweep) — OBSERVED 2026-09-03:
  `stop` returns HTTP 400 in default mode, so no honesty verdict is reachable,
  probe_id:`gpt-5-6-sol--stop--["the"]--default--6a86352a`, promoted ADR-0050. ``

**Closed verdict vocabularies, all six keys** (fixed here; later plans add registry entries and
cells against these vocabularies without editing this ADR):

| Key | Head form | Verdict vocabulary |
|---|---|---|
| `seed_determinism` | rate | `varies`, `no-signal` |
| `sampling_repeatability` | rate | `deterministic`, `partial`, `varies`, `no-signal` |
| `stop_sequence_honesty` | bare verdict | `honest`, `ambiguous`, `inconclusive` |
| `multi_candidate_delivery` | bare verdict | `accepted-honored`, `accepted-ignored`, `rejected` |
| `logprobs_delivery` | bare verdict | `accepted-honored`, `accepted-ignored`, `rejected` |
| `service_tier_contract` | bare verdict | `accepted-ignored`, `silently-translated`, `response-asymmetric`, `response-absent` |

Citations must resolve against committed classified evidence
(`probes/classified/behavioral.yaml` or `probes/classified/contract-sweep.yaml`) — an id that
resolves nowhere is a `check-probe-drift.py` finding, never a silently-accepted citation. An
unparseable cell (a head matching none of the three forms, a missing `OBSERVED` marker, a
missing or malformed date, no citation, or no trailing `promoted ADR-` clause) is always a loud
failure — never skipped.

**Precedence rule (methodology rule 1a):** where a model/key pair has both a contract result and
a behavioral result, the behavioral result governs the derived head — `qwen3.8-flash`'s
`logprobs_delivery` case above is the worked instance, an earlier lower-confidence contract
classification superseded by a later, non-masking-budget behavioral reverify. Where a model/key
pair's evidence is a contract REJECTION rather than a behavioral rate (`gemini-3-1-pro`'s
`multi_candidate_delivery` cell above), the derived head is that rejection's own verdict, never
a not-applicable head — a parameter the maker rejects by name is a measured fact, not an absent
one.

## Consequences

- `docs/feature-taxonomy.yaml` gains one `groups:` entry (`wire-behavior`, order 43) and, in
  this plan, one `features:` entry (`stop_sequence_honesty`); the remaining five entries land in
  plans 13-03 and 13-04, after this ADR, never before it.
- `tools/1-models/*.md` gain OBSERVED cells across the 12 probed reports — 12 in this plan
  (`stop_sequence_honesty` only), 60 more across 13-03/13-04.
- `scripts/check-probe-drift.py` (new) is the read-only two-way drift checker enforcing this
  ADR's grammar and every promoted key's per-model coverage; it joins `CLAUDE.md`'s pre-commit
  battery as its sixth command.
- `CLAUDE.md` § Lint gains that sixth command and its own exit-code paragraph.
- `docs/conclusions.md` and `README.md` are touched by plan 13-05 (conclusion 19's amendment;
  conclusions 20-22 minted), not by this plan.
- The phase closes by asserting that this ADR's six-key set and the registry's `wire-behavior`
  group membership agree — no promoted key without a registry entry, and no registry entry
  outside this ADR's set.
- Existing matrices and reports are unaffected beyond the additions above — no report loses a
  row and no existing key changes meaning.
