# ADR-0040 — `thinking` + `effort_control` become three typed reasoning keys

`decided: 2026-08-26` · status: **accepted**

## Decision

The two category-1 API-feature keys that describe how a model reasons are replaced by
three typed keys in the same `model_features` block:

| old (free-text) | new | `value_type` |
|---|---|---|
| `thinking` | `reasoning` | `presence` |
| `thinking` | `reasoning_type` | `closed-enum` — `always-on` \| `default-on` \| `opt-in` \| `none` |
| `effort_control` | `reasoning_effort` | `open-descriptive` — `levels:<set>@<default>` \| `budget:<unit>` \| `none` |

`prompt_caching` and `batch_discount` are untouched and stay free-text: ADR-0014's
reasoning about structurally different economics still holds for them, and only for them.

**Repo voice standardises on *reasoning*.** The vendor's own word is quoted verbatim
wherever it appears — `thinking.type`, `budget_tokens`, `thinking_level`, *"K3 always
thinks"*, *"supports only non-thinking mode"* — and never translated. The key names are
this repo's vocabulary; the cells and body prose are the vendors'.

## Context

The trigger was a naming question — should `thinking` be called `reasoning`, since that
is the market's word? Reading the eleven reports to answer it turned up something larger.

**The market has not converged on one word; it has converged on a division of labour.**
The on/off surface is `thinking`-named at five vendors (Anthropic, Google, DeepSeek, Z.ai,
Alibaba) and `reasoning`-named at two (OpenAI, xAI). The *depth* surface is
`reasoning_effort` at five (OpenAI, xAI, DeepSeek, Z.ai, Moonshot) against Google's
`thinking_level` and Anthropic's `budget_tokens`. Z.ai is the specimen: its prose says
*"always operates with reasoning enabled"* while its parameter is still `thinking.type`.
A rename alone would have picked a side of a split that the two keys already straddled.

**`thinking` held four independent facts in one free-text cell**: whether the model
reasons at all; who *sizes* the reasoning; whether it can be disabled; and what the dial
looks like. The conflation was not hypothetical — it is why the cells could not be
compared. `claude-opus-5` said `adaptive`, `kimi-k3` said `always-on, not toggleable`, and
those two answer *different questions*.

**"Adaptive vs extended" is not the toggleability axis.** It is Anthropic's vocabulary for
who sizes the reasoning: `budget_tokens` (caller allocates up front) versus
`{type: "adaptive"}` (model decides, caller steers with a coarse effort level).
Toggleability is separate and orthogonal — on Anthropic's own current surface,
`{type: "disabled"}` is accepted on Sonnet 5, rejected on Fable 5, and accepted on Opus 5
only at effort `high` or below. The old key's declared enum (`adaptive | extended | none`)
was therefore both un-followed by its own cells and aimed at the wrong axis.

## Why toggleability won `reasoning_type`

Both axes are real. Toggleability is recorded because **every vendor states it** — nine of
eleven cells were settled from the existing record — while adaptive-vs-budgeted is stated
only by Anthropic, OpenAI and Google, and would have left five `·`.

Nothing is lost. Who sizes the reasoning moved to `reasoning_effort`'s **family**, which is
where a caller actually meets it: `levels:` means the model spends against a level you
pick, `budget:` means you allocate the tokens yourself. Haiku 4.5 is the sweep's only
`budget:` dial — the generation seam, now visible in a column instead of buried in prose.

## Why `reasoning_effort` is not a presence-claim

It was proposed as a boolean and rejected on **methodology rule 5d**, before being built.
Ten of eleven models expose a caller-facing depth dial; the eleventh is
`qwen3-coder-next`, which is also the only `✗` on `reasoning`. A boolean would have
reproduced the `reasoning` column exactly — two columns carrying one bit between them, an
instrument that cannot discriminate and therefore cannot measure.

The variation is not binary. It is in the level set (four distinct shapes) and the
default: `@high` mostly, `@medium` at OpenAI, **`@max`** at Kimi K3 and GLM-5.3. That
last one changes what a task costs, and it is a finding this repo already carried, so the
level set and the default live *in the cell* rather than in body prose.

`reasoning` is kept despite being a weak discriminator itself (10/1), and the registry
note says so in as many words. It is the base fact the other two are conditional on, and
a non-reasoning model is a thing that ships again. A weak key recorded as weak is not the
same as a weak key presented as a measurement.

## Enforcement — and one mechanism that would have failed silently

`check_reasoning` in `build-tool-index.py` is the repo's **fourth cell-value check**
(after `pricing`, `knowledge_cutoff`, and the cutoff-basis rule): it validates
`reasoning_type` against the closed enum, `reasoning_effort`'s family against
`{levels, budget}`, requires the `@default` on a `levels:` dial, and rejects the
contradictions (`reasoning: false` with a dial, `reasoning: true` with `none`). This is
what `open-descriptive` means operationally — the family is closed and checked, the
specific is free and is not.

Two mechanisms were considered for the old→new decoder and **rejected**:

- **`schema_renames` (LINT-05)** looked like the obvious home — it is what carried
  `layer:` → `category:` and `features:` → `harness_features:`. It would have been a
  silent false green: its matcher is `^{old}:(\s|$)`, anchored at column 0
  (`check-taxonomy.py`), and these keys are nested two spaces inside `model_features:`.
  Registering the rename there would have produced a check that never fires.
- **A deny-list entry** has no host term (`categories`, `types`, `bucket`, `stack` are
  tool-taxonomy vocabulary, not feature keys), and "thinking" has heavy legitimate use as
  vendor quotation — which the deny-list growth procedure's first step disqualifies.

The enforcement already existed: **LINT-04a** (`check_feature_registry`) errors on any
`model_features:` key that does not resolve against the registry, so a surviving
`thinking:` fails the moment the registry entry is gone. Verified by deliberately
reintroducing it and watching the lint exit non-zero, along with all three new
cell-value failure modes — a check nobody has seen fail is not yet a check.

## Consequences

- Eleven report frontmatters migrate. **No `checked:` date moves**: every cell derives
  from what was already recorded, at its existing check. Translating recorded vendor words
  into the new vocabulary is in scope; inferring a fact the record does not carry is not.
- Coverage after migration: `reasoning` 11/11 · `reasoning_type` 9/11 ·
  `reasoning_effort` 8/11. All five `·` are Anthropic, and the split is what exposed them:
  Opus 5 and Sonnet 5 said only `adaptive` (silent on toggleability), and their effort
  cells carried a **default** but never the **level set**, which `levels:<set>@<default>`
  needs. Fable 5 never had an effort cell at all. Tracked as a dated probe.
- Vendor prose displaced from the two old cells is carried verbatim into each report's new
  **§ Reasoning surface**, which states what its cells rest on and when it was checked.
  Nothing was discarded to make the cells tidy.
- `render_features`'s cell formatter is extracted as `fmt_feature_cell` and shared: the
  `model_features` block gained its first boolean, and the models matrices formatted every
  cell as code, so `reasoning: true` would have rendered as `` `True` ``.
- ADR-0014 is **amended, not superseded**. Its block structure, its verified-only
  discipline, and its free-text rule for the two economics keys all stand.
