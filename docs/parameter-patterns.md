# Parameter patterns

`checked: 2026-09-03`

The pattern-analysis document this milestone's evidence base earns: cross-vendor asymmetries,
docs-vs-wire contradictions, and support-state distributions synthesized from Phase 11's
727-cell contract sweep, Phase 11.1's docs-vs-wire confrontation, and Phase 12's 83-cell
behavioral matrix — read as a results view, not as a re-derivation. Every claim below ends in a
`probe_id` or `cell_id` that resolves against committed classified evidence
(`probes/classified/contract-sweep.yaml`, `probes/classified/behavioral.yaml`); a claim without
one is not a finding here (methodology rule 4). Hand-kept per D-10 — a repo-level cross-category
finding, not probe tooling, and distinct from `comparisons/`, which is generated-only (rule 3).

**Valid through:** every rate/state cited in this document is valid only as of the evidence
dates below; no claim here should outlive a re-probe of the live APIs. Contract-sweep evidence:
`probes/classified/contract-sweep.yaml`'s own `checked: 2026-09-01`. Behavioral evidence:
`probes/classified/behavioral.yaml`'s own `checked:`/`evidence_through: 2026-09-03`.

This document grows across Phase 13's plans as each promoted key lands its finding section; this
plan seeds it with the opening framing and the first fully-cited finding, `stop_sequence_honesty`
— the tracer key this phase proves end-to-end before promoting the remaining five.

---

## Stop-sequence honesty

Truncation itself is nearly universal — the model stops generating at (or immediately after) the
requested stop sequence in 9 of the 10 domain models. What varies is whether the response's OWN
finish-reason field can prove that a stop, rather than a natural completion, is what happened.

**Domain: 10 of 12 tracked models.** `gpt-5-6-sol` and `grok-4-5` are structurally out of this
key's domain — the contract sweep observed both rejecting the `stop` parameter outright in
`default` mode, HTTP 400 (`gpt-5-6-sol--stop--["the"]--default--6a86352a`,
`grok-4-5--stop--["the"]--default--ee1a658f`), so no honesty verdict is reachable for either.

Only the 4 Anthropic models report a genuinely distinguishable finish value — `stop_reason:
stop_sequence` on the triggering call versus `end_turn` on the no-stop control
(`claude-fable-5--stop-truncation--triggering--default--61baa082`,
`claude-opus-5--stop-truncation--triggering--default--58a5a42f`,
`claude-sonnet-5--stop-truncation--triggering--default--905e8ef4`,
`claude-haiku-4-5--stop-truncation--triggering--default--19f5c60f`). Every other domain vendor
shares ONE generic finish value for both the natural-completion and the stop-sequence case:
Gemini's `STOP` (`gemini-3-1-pro--stop-truncation--triggering--default--c83e86af`) and the
`openai_compat` family's shared `stop` value (`kimi-k3--stop-truncation--triggering--default--5b566140`,
`deepseek-v4--stop-truncation--triggering--default--970252c9`,
`qwen3.8-max--stop-truncation--triggering--default--67a34da7`,
`qwen3.8-flash--stop-truncation--triggering--default--d1ae15ef`) are each emitted identically on
both the triggering call and its no-stop control — the finish field alone cannot distinguish the
two, and text comparison against the control is the only evidence this family trusts.

`glm-5.3` is a genuine third state, not a match to either group: the triggering call returned
empty visible text at the fired budget, so truncation itself was never confirmed against the
trigger word in this sweep (`glm-5.3--stop-truncation--triggering--default--01466ba7`) — recorded
`inconclusive`, distinct from both `honest` and `ambiguous`.

**Reading this for a caller:** a harness author who wants to detect "the model was cut off by MY
stop sequence" rather than "the model happened to end its own turn there" can trust the finish
field only at the four Anthropic models; everywhere else in this domain, the finish field is
silent on that distinction and the caller must compare against a control or inspect the returned
text directly.

Domain, per-model states, and every citation above are drawn from BHV-03
(`probes/classified/behavioral.yaml`), the promoted `stop_sequence_honesty` key, cited from the
report frontmatter as of `promoted ADR-0050`.

---

## Cross-vendor asymmetries

### Sampling determinism

Two promoted keys converge on the same finding from different domains: requesting the same
`seed` value across repeats, and requesting `temperature: 0` (or, where a model rejects
`temperature` outright, the model's own default implicit sampling), both fail to reproduce
identical output almost everywhere this sweep can test.

**`seed_determinism`, 8-model domain** (the 4 Claude models have no request-side `seed` field —
`docs-claims:seed/anthropic` — and are structurally out of this key's domain, not a gap):

| Model | Rate | Verdict | cell_id |
|---|---|---|---|
| gpt-5-6-sol | 0/5 same-seed pairs | varies | `` cell_id:`gpt-5-6-sol--seed--42--default` `` |
| gemini-3-1-pro | 0/5 same-seed pairs | varies | `` cell_id:`gemini-3-1-pro--seed--42--default` `` |
| grok-4-5 | 0/5 same-seed pairs | varies | `` cell_id:`grok-4-5--seed--42--default` `` |
| kimi-k3 | 0/5 same-seed pairs | no-signal | `` cell_id:`kimi-k3--seed--42--default` `` |
| deepseek-v4 | 0/5 same-seed pairs | varies | `` cell_id:`deepseek-v4--seed--42--default` `` |
| glm-5.3 | 0/5 same-seed pairs | no-signal | `` cell_id:`glm-5.3--seed--42--default` `` |
| qwen3.8-max | 0/5 same-seed pairs | varies | `` cell_id:`qwen3.8-max--seed--42--default` `` |
| qwen3.8-flash | 0/5 same-seed pairs | varies | `` cell_id:`qwen3.8-flash--seed--42--default` `` |

**`sampling_repeatability`, 12-model domain** (every tracked model gets a cell — either a real
`temperature: 0` test, or, for the 5 models whose `temperature` parameter the contract sweep
rejects outright in `default` mode, a `default-config-repeatability` SUBSTITUTE that instead
asks whether the model's own implicit sampling repeats):

| Model | Design | Rate | Verdict | cell_id |
|---|---|---|---|---|
| claude-fable-5 | substitute | 0/4 repeat pairs | varies | `` cell_id:`claude-fable-5--default-config-repeatability--no-temperature--default` `` |
| claude-opus-5 | substitute | 0/4 repeat pairs | no-signal | `` cell_id:`claude-opus-5--default-config-repeatability--no-temperature--default` `` |
| claude-sonnet-5 | substitute | 0/4 repeat pairs | varies | `` cell_id:`claude-sonnet-5--default-config-repeatability--no-temperature--default` `` |
| claude-haiku-4-5 | real temperature:0 | 4/4 repeat pairs | deterministic | `` cell_id:`claude-haiku-4-5--temperature--0--default` `` |
| gpt-5-6-sol | substitute | 0/4 repeat pairs | varies | `` cell_id:`gpt-5-6-sol--default-config-repeatability--no-temperature--default` `` |
| gemini-3-1-pro | real temperature:0 | 2/4 repeat pairs | partial | `` cell_id:`gemini-3-1-pro--temperature--0--default` `` |
| grok-4-5 | real temperature:0 | 0/4 repeat pairs | varies | `` cell_id:`grok-4-5--temperature--0--default` `` |
| kimi-k3 | substitute | 0/4 repeat pairs | varies | `` cell_id:`kimi-k3--default-config-repeatability--no-temperature--default` `` |
| deepseek-v4 | real temperature:0 | 0/4 repeat pairs | varies | `` cell_id:`deepseek-v4--temperature--0--default` `` |
| glm-5.3 | real temperature:0 | 0/4 repeat pairs | no-signal | `` cell_id:`glm-5.3--temperature--0--default` `` |
| qwen3.8-max | real temperature:0 | 0/4 repeat pairs | varies | `` cell_id:`qwen3.8-max--temperature--0--default` `` |
| qwen3.8-flash | real temperature:0 | 0/4 repeat pairs | varies | `` cell_id:`qwen3.8-flash--temperature--0--default` `` |

**Why a uniform-looking key still promotes.** The contract sweep alone would fail `seed` on
D-01's cross-model variance test: every fired cell in its domain is `accepted-unverified`, flat
(VERIFIED by direct query of `probes/classified/contract-sweep.yaml`'s `seed` rows — 0 of 17
fired cells in any state other than `accepted-unverified`). The promotion case rests on the
**combined** picture, per ADR-0050: contract evidence shows `seed` uniformly accepted, and only
the behavioral rate — 0/5 in all 8 domain models — exposes that "accepted" never meant
"deterministic." That is the finding, not an absence of one.

**Substitute design, named where it fires.** Five of the twelve `sampling_repeatability` cells
above are not a `temperature: 0` test at all — they are the `default-config-repeatability`
substitute, for the five models whose `temperature` the contract sweep rejects outright in
`default` mode (`claude-fable-5`, `claude-opus-5`, `claude-sonnet-5`, `gpt-5-6-sol`, `kimi-k3`).
The design column above names the substitute explicitly on every row that used it; paraphrasing
`comparisons/behavioral.md`'s own generated sentence for these cells, the substitute asks
whether the model's own DEFAULT (implicit) sampling — with no `temperature` parameter sent at
all — repeats across five identical requests, the closest behavioral question the model's own
accepted request surface can answer. A substitute cell's `0/4` rate is never the same fact as a
real `temperature: 0` cell's `0/4` rate, and this document never states one where it means the
other.

**Signal versus no-signal.** Four of the twenty rows above carry a `no-signal` verdict rather
than `varies`: `kimi-k3` and `glm-5.3` in the `seed_determinism` table (both hit reasoning-length
exhaustion before producing a comparable visible completion across all five repeats), and
`claude-opus-5` and `glm-5.3` (a real `temperature: 0` cell here) in the `sampling_repeatability`
table. A `no-signal` `0/N` rate is not the same finding as a `varies` `0/N` rate: `varies` means
five (or four) distinct outputs were actually compared and none matched; `no-signal` means the
budget was exhausted before a comparable completion existed to compare at all, so the zero
reflects an absent measurement, not an observed one. Reading the two verdicts as equivalent would
overstate how much of this domain was actually confirmed to vary.

**The signal that exists.** Only `claude-haiku-4-5` (4/4, real `temperature: 0`) and
`gemini-3-1-pro` (2/4 partial, real `temperature: 0`) show any repeatability signal at all across
both tables — 10 of the 12 `sampling_repeatability` models, and all 8 of the `seed_determinism`
domain, show zero. Determinism is close to universally absent on the live wire this sweep
reaches.

### Temperature's two axes

`temperature` is heterogeneous on two independent axes, confirmed by direct query of
`probes/classified/contract-sweep.yaml`'s `temperature` rows across all fired modes.

**Axis 1 — cross-vendor, `default`-mode rejection.** 5 of the 12 tracked models reject
`temperature` outright in `default` mode: `claude-fable-5`, `claude-opus-5`, `claude-sonnet-5`,
`gpt-5-6-sol`, `kimi-k3` (count taken directly from the `state: rejected` rows at `mode: default`
in `probes/classified/contract-sweep.yaml`'s `temperature` cells).

**Axis 2 — within one model, mode-conditional acceptance.**

| Model | default | thinking-off | thinking-on |
|---|---|---|---|
| claude-haiku-4-5 | accepted-unverified (`` probe_id:`claude-haiku-4-5--temperature--0.7--default--a41444ed` ``) | accepted-unverified (`` probe_id:`claude-haiku-4-5--temperature--0.7--thinking-off--df4c6c49` ``) | rejected (`` probe_id:`claude-haiku-4-5--temperature--0.7--thinking-on--7ac71847` ``) |
| gpt-5-6-sol | rejected (`` probe_id:`gpt-5-6-sol--temperature--0.7--default--f4a07a21` ``) | accepted-unverified (`` probe_id:`gpt-5-6-sol--temperature--0.7--thinking-off--b4358295` ``) | rejected (`` probe_id:`gpt-5-6-sol--temperature--0.7--thinking-on--ed5fbf8b` ``) |

**The two axes are independent, and `gpt-5-6-sol` demonstrates it by sitting on both.**
`gpt-5-6-sol` is one of the 5 axis-1 default-mode rejecters AND is itself mode-conditional on
axis 2 (rejects at `default` and `thinking-on`, accepts at `thinking-off`) — a model's
membership in the cross-vendor rejection set says nothing about whether that same model is
internally consistent across its own modes, and `gpt-5-6-sol` is the one domain member proving
the two questions must be asked separately.

### Anthropic rejects its own documented structured-output parameters

All four tracked Claude models reject BOTH `output_config` and the legacy `output_format` field
name for Anthropic's own structured-output feature — HTTP 400 at every one of the 8 pairs — even
though Anthropic's own documentation (`anthropic-messages-api-ref`, `anthropic-structured-outputs`)
describes both as accepted, including an explicit transition-period statement for the legacy
name: *"The API continues to accept the old beta header (`structured-outputs-2025-11-13`) and
the `output_format` request field for a transition period."*

Both rows are cited directly from `comparisons/docs-vs-wire.md`'s own Contradictions table (never
an ad-hoc classified-YAML read): `anthropic-structured-output-output-config` contradicts at all
4 Claude models, and `anthropic-structured-output-output-format` contradicts at all 4 Claude
models — 8 rows, counted by filtering that table's own listing to the two parameter names. Out
of the table's own stated 79 contradicted pairs, these two parameters account for 8 of them
(8/79 ≈ 10.1% of every contradiction the sweep found, from one maker's own documented feature
rejecting itself at every model that carries it).

This is the sharpest same-maker contradiction the sweep found: not a third-party compat
implementation drifting from an origin vendor's contract, but Anthropic's own live Messages API
rejecting parameters Anthropic's own current documentation says it accepts, on Anthropic's own
models, including a name the docs explicitly promise a transition period for.

### The service-tier field-location asymmetry, twice

Anthropic documents `service_tier` as a request-top-level field and `usage.service_tier` as its
nested response-side mirror — never promoted to the response top level. This is confirmed
against a live response body: `claude-haiku-4-5`'s own non-trap audit cells all show
`response_field_path: usage.service_tier` present, `response_top_level_present: absent`
(`` cell_id:`claude-haiku-4-5--service-tier-audit--auto--default`, probe_id:`claude-haiku-4-5--service-tier-audit--auto--default--613638b0` ``).
The asymmetry carries its own trap: sending the RESPONSE-vocabulary word `standard` as a REQUEST
value returns HTTP 400 naming the field
(`` cell_id:`claude-haiku-4-5--service-tier-audit--trap--default`, probe_id:`claude-haiku-4-5--service-tier-audit--trap--default--8fc20f53` ``)
— the "caller reads the wrong field" hazard this asymmetry implies is not hypothetical; the API
itself rejects the confused direction.

Gemini independently exhibits the structurally identical asymmetry, with no shared code between
the two makers: request field `serviceTier` at the top level, response field
`usageMetadata.serviceTier` nested, across all 5 of Gemini's own audit cells
(`` cell_id:`gemini-3-1-pro--service-tier-audit--flex--default`, probe_id:`gemini-3-1-pro--service-tier-audit--flex--default--a9f9f805` ``).
Gemini's own cells were never fired as a trap, but the shape — request top level, response
nested under a `usage`/`usageMetadata` envelope — is the same fact discovered independently at a
second maker.

The genuine third state belongs to neither asymmetric maker: `kimi-k3`, `deepseek-v4`, `glm-5.3`,
and `qwen3.8-flash` each show `response_present: absent` on their own BHV-06 audit cells — no
response-side tier field at all, and their documentation is silent on the response side too
(`` cell_id:`kimi-k3--service-tier-audit--omitted--default`, probe_id:`kimi-k3--service-tier-audit--omitted--default--43b8c30e` ``
and the equivalent `--omitted--default` cell at each of the other three siblings). `qwen3.8-max`
is distinct again: it has zero BHV-06 audit cells of its own, so its `service_tier_contract`
disposition falls back to the presence-row contract state (`accepted-ignored`) rather than any
response-side finding — a fourth, no-audit-evidence case, not a fifth asymmetric or third-state
one.

---

## The docs-versus-wire confrontation

**A fresh render, dated.** `python3 scripts/build-docs-vs-wire.py --check` (run 2026-09-03):
`0 problem(s)` — the file this section cites is current. The same command without `--check`
prints the full verdict tally rather than just the "## Contradictions" heading's own count:

```
rows (param x model pairs): 612
  docs-corroborated: 54
  docs-contradicted: 79
  docs-undecidable: 151
  docs-untested: 324
  docs-silent: 4
non-unanimous pairs: 66
docs-silent claims: 4
facets awaiting behavioral test: 115
```

`git status --short -- comparisons/docs-vs-wire.md` reported no diff after this run — the file
was already at this exact render; this document quotes a dated run, not a static file header.

**Two denominators, stated explicitly.** 79 of the 612 total `(param, model)` pairs are
contradicted — but 324 of those 612 are `docs-untested` (no wire evidence exists for the pair at
all), so a rate over all 612 understates how often the wire actually disagreed with the docs
where the wire had anything to say. Two readings:

- **Over all pairs:** 79/612 = 12.9%.
- **Over pairs where wire evidence exists** (612 − 324 = 288, i.e. `docs-corroborated` (54) +
  `docs-contradicted` (79) + `docs-undecidable` (151) + `docs-silent` (4) = 288): 79/288 = 27.4%.

**This document's headline number is 79/288 (27.4%).** The 612-pair denominator counts a large
mass of pairs (324, more than half the matrix) the sweep never fired at all — a rate over that
denominator answers "how much of the theoretically-checkable surface is contradicted," a
different and less actionable question than "of the surface the wire actually spoke to, how
often did it disagree with the docs." The two readings differ by more than a factor of two, and
citing one without naming the other is exactly the failure mode this section exists to avoid.

**The shape of the contradictions**, counted directly from `comparisons/docs-vs-wire.md`'s own
Contradictions table (79 rows): concentration is heaviest at `tool-choice` (6 rows),
`temperature`/`top-p` (5 rows each), and `service-tier`/`openai-service-tier-values` (5 rows
each). By maker, the 4 Claude models together account for 28 of the 79 rows (35.4%) and
`gpt-5-6-sol` alone accounts for 14 (17.7%) — Anthropic and the OpenAI-origin model together
carry over half the sweep's contradictions (42/79, 53.2%).

One family lands its contradictions exactly at the makers whose documentation never claimed the
concept at all: `service-tier` and `openai-service-tier-values` contradict at exactly the same 5
models — `kimi-k3`, `deepseek-v4`, `glm-5.3`, `qwen3.8-max`, `qwen3.8-flash` — the five
non-OpenAI-family-adjacent compat vendors whose own documentation is silent on a service-tier
concept altogether (each row's `Quote` column is `—`, i.e. no documented claim exists to
corroborate or contradict, yet the wire accepted the field, so `docs-claims.yaml`'s own explicit
absence-of-documentation entry is what the wire evidence contradicts). Link into
`comparisons/docs-vs-wire.md`'s own listing for every row-level quote, `source_ref`, `probe_id`,
and HTTP status.

## Support-state distributions

Derived from `probes/classified/contract-sweep.yaml`'s own `state`/`skip_reason` fields across
all 727 rows (definition: a Python read of every cell's `state` field, tallied by value — 443
fired cells + 284 declared skips, matching the file's own generated header comment).

**Of the 443 fired cells:** `accepted-unverified` 218 (49.2%), `rejected` 115 (26.0%),
`accepted-honored` 50 (11.3%), `accepted-ignored` 39 (8.8%), `needs-review` 16 (3.6%),
`silently-translated` 5 (1.1%). Nearly half the fired surface (218/443) is acceptance testimony
with no behavioral honor check behind it — exactly the gap ADR-0050's D-02 promotion bar exists
to name: `accepted-unverified` is what a parameter looks like before anyone checks whether
acceptance means the model actually did what was asked. Only 89 of the 443 fired cells
(`accepted-honored` 50 + `silently-translated` 5, i.e. the two states where the wire's own
response resolves the question one way or the other without further testing, plus the
39-`accepted-ignored` cells that were themselves later re-tested behaviorally for the promoted
keys) approach a settled answer without a dedicated behavioral probe.

**Of the 284 declared skips**, only 46 (`no-request-field-for-vendor`) are the "never grammatical
for this maker" case this document uses throughout to mean structural absence (e.g. `seed`/`n`
at the 4 Claude models). The remaining 238 skips are per-mode declarations that do not mean
"never grammatical" in that sense: 160 `wire-shape-incompatible` (a parameter shaped for one
wire family, e.g. Gemini's `candidateCount`, correctly never fired against an `openai_compat`
model), 45 `no-thinking-off-toggle`, 22 `toggle-not-a-request-parameter`, and 11
`toggle-shape-unknown` (all three about a model's reasoning-toggle surface, not about the
parameter under test). Conflating any of these with the 46 genuine structural-absence skips would
overstate how much of the matrix is "not applicable" versus "not fired at this mode for other
reasons."

## The silent-acceptance hazard

Five `openai-*`-named parameters are accepted-unverified, uniformly, across every one of the 5
foreign `openai_compat`-family siblings — `grok-4-5`, `kimi-k3`, `deepseek-v4`, `glm-5.3`,
`qwen3.8-max`, `qwen3.8-flash` — a caller sending one of these to a sibling vendor gets neither an
error nor a confirmation:

- `openai-verbosity`
- `openai-prediction` (additionally `rejected` at its own origin, `gpt-5-6-sol` — HTTP 400,
  `` probe_id:`gpt-5-6-sol--openai-prediction--{"content":"hello","type":"content"}--default--1bd2232f` ``
  — still uniform among the 5 foreign siblings)
- `openai-store`
- `openai-safety-identifier`
- `openai-prompt-cache-key`

All five are skipped (`no-request-field-for-vendor`) at the 4 Claude models and at
`gemini-3-1-pro`, so the domain for this finding is the 6 `openai_compat` models (origin +
5 siblings); the uniformity claim itself is over the 5 siblings.

**The excluded sixth candidate.** `openai-metadata` was checked against the same pattern and
excluded: `grok-4-5`/`kimi-k3`/`deepseek-v4`/`qwen3.8-max`/`qwen3.8-flash` are
`accepted-unverified` like the five fields above, and `gpt-5-6-sol` is `rejected` at its own
origin like `openai-prediction` — but `glm-5.3`'s own cell is `needs-review`
(`` probe_id:`glm-5.3--openai-metadata--{"probe":"true"}--default--9d1cdbd3` ``), breaking the
uniformity the other five fields show cleanly. An excluded near-miss is evidence for the claim,
not a footnote to it: it shows the silent-acceptance pattern is a real, checkable property that
some fields have and at least one adjacent field does not.

**The reader-facing consequence.** An absent rejection is not evidence of support. A harness
author who sends `openai-prediction` (or any of its four siblings) to `kimi-k3` and receives a
200 with no error has learned nothing about whether the field did anything — the same wire shape
a genuinely-honored field would produce.

## The compat dialect finding

`gpt-5-6-sol` — OpenAI's own model — rejects the shared `openai_compat` family's `max_tokens`
field outright, the exact field name every sibling vendor in this domain (`grok-4-5`, `kimi-k3`,
`deepseek-v4`, `glm-5.3`, `qwen3.8-max`, `qwen3.8-flash`) still accepts, because each sibling
copied OpenAI's own Chat Completions field name when building its own compat surface. Quoted
directly from `probes/PREREGISTRATION.md:340-344`:

> `gpt-5-6-sol` rejects `max_tokens` outright, unrelated to `openai-reasoning-effort`. Its 400
> body: `Unsupported parameter: 'max_tokens' is not supported with this model. Use
> 'max_completion_tokens' instead.` (`param: "max_tokens"` in the error JSON) — the harness's
> `openai_compat` adapter sends `max_tokens` universally; this model requires the newer
> `max_completion_tokens` field.

**The caveat, in the prose, not around it.** This fact is NOT visible in any classified row.
`probes/harness/models.yaml:73` applies a per-model request-field-rename override
(`max_tokens_field: max_completion_tokens`) BEFORE firing, so every classified `max-tokens` cell
already shows uniform `accepted-honored` — the override masks the underlying vocabulary split in
the classified evidence entirely. This is the one claim in this document whose evidence is a harness
configuration rather than a probe result: `probes/PREREGISTRATION.md:340-344` (the passage
quoted above, recording the origin model's own rejection before the override existed) and
`probes/harness/models.yaml:73-79` (the override itself, which is why no fired cell shows the
split today). No `comparisons/docs-vs-wire.md` row exists for this fact, and citing one would be
wrong — there is none to cite. Saying so here is what keeps this claim honest: the compat dialect
this repo's harness now papers over at the wire is still true of the API, and it would resurface
immediately if the override were ever removed.

---

## Matrix-only dispositions

Every key below passed D-01's cross-model-variance test in `probes/classified/contract-sweep.yaml`
(a mix of `rejected` and `accepted-*` states over its own grammatical domain) but stayed out of
the registry — per D-02, "accepted-unverified is acceptance testimony, not verified behavior."
This mirrors ADR-0050's own "Considered, left matrix-only" table exactly, same key set, same
count, because a future verification phase re-checks the promoted set against this list, and a
silent drop between the two surfaces would leave nothing to re-check against.

**The count is ten, not nine.** An earlier draft of this phase's own planning prose said "nine";
reconciled here in the open against `RESEARCH.md`'s own D-03 table and `CONTEXT.md`'s own D-02
key list, both of which enumerate ten rows (the definition: every row in the "considered, left
matrix-only" table — i.e. every contract-sweep parameter that shows real cross-model variance in
its own domain and carries no promoted-key registry entry). The "nine" reading is rejected; it
undercounted the table by one row before the reconciliation and is not used anywhere in this
document or in ADR-0050.

**Unique-model counts are `sorted(set(...))` over ALL fired modes per model, for every row
below** — stated once here rather than per row. A model that rejects a parameter at one mode and
accepts it at another (e.g. `claude-haiku-4-5`, `gpt-5-6-sol` on several rows, the same
mode-conditionality documented for `temperature` above) counts in BOTH the rejected and the
accepted set for that row; the two set sizes are not complementary counts of the same 8-or-12
models and should not be read as if they were.

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

No key is dropped from this table silently. It is the list a future verification phase re-checks
against when behavioral evidence arrives for any of these parameters — the reason it exists at
all is that a silent drop here would leave nothing to re-check.

## The candidate register

Every conclusion candidate this phase's own material surfaced, walked from `RESEARCH.md`'s
"Conclusions + ADR mechanics" section, `CONTEXT.md`'s D-11, and the owner's recorded Task 1
gate decision in `13-01-SUMMARY.md` (see "Owner Sign-off": *"the conclusion set (amend 19; mint
20, 21, 22; park the five silent openai-* fields)"*). Candidates below are numbered in the order
D-11's own candidate list names them, since no earlier document assigns a specific conclusion
number to a specific candidate ahead of the mint itself (plan 13-05's own job) — this is the
register's own ordering choice, stated so a reader does not mistake it for a locked assignment.

**Reconciled 2026-09-03, after plan 13-05's mint landed.** The register holds 5 candidates
total: 4 promoted (1 amendment to conclusion 19, 3 newly minted as conclusions 20/21/22) and 1
parked, and 4 + 1 = 5. Every promoted row below now carries the conclusion number it actually
landed as in `docs/conclusions.md`, not the "destined for" placeholder this document carried
before the mint — the numbers match because the three-candidate ordering this register chose
(seed/temp-0 determinism, compat dialect, docs-vs-wire contradiction rate) is the same order
`docs/conclusions.md` minted them in.

| Candidate | Disposition |
|---|---|
| Anthropic's documented request/response service-tier field asymmetry, confirmed on the wire (this document's own "service-tier field-location asymmetry" section above), plus Gemini's independent structurally identical second instance | **Amended into conclusion 19** — extends its existing title ("The served API outranks its own documentation") with a second, distinct field-location fact; not a new number, per the owner's own gate decision |
| Seed/`temperature: 0` determinism is nearly universally absent on the live wire (this document's own "sampling determinism" section above) | **Promoted as conclusion 20** |
| The compat dialect outlived its author — `gpt-5-6-sol` rejects its own legacy `max_tokens` vocabulary while every third-party compat sibling still accepts it (this document's own "compat dialect" section above) | **Promoted as conclusion 21** |
| The docs-vs-wire contradiction rate (79/288 = 27.4% of pairs the wire had anything to say about; this document's own "docs-versus-wire confrontation" section above) | **Promoted as conclusion 22** |
| The uniform silent acceptance of five `openai-*` foreign fields across the compat family (this document's own "silent-acceptance hazard" section above) | **Parked** — per the owner's explicit Task 1 gate directive ("park the five silent openai-* fields"). It does not clear D-11's "changes what a reader should do" bar as cleanly as the three promoted candidates on its own; this document's own silent-acceptance section already states the reader-facing guidance directly ("an absent rejection is not evidence of support"), which is the disposition the owner chose over minting a fourth conclusion number |

**Walked but not a distinct candidate.** `openai-metadata` (the excluded sixth field in the
silent-acceptance section above) is evidence INSIDE the parked silent-acceptance candidate, not
a separate candidate in its own right — no source in this phase's material names it as a D-11
candidate on its own, and this register does not manufacture one.

## What would falsify this document

**Valid through the dates stated at the top of this file.** Contract-sweep evidence is dated
`checked: 2026-09-01`; behavioral evidence is dated `checked:`/`evidence_through: 2026-09-03`.
No rate, verdict, or contradiction count in this document should outlive a re-probe of the live
APIs past those dates.

**A dated, falsifiable re-probe prediction.** If the twelve tracked models' APIs are re-probed
with the same harness and the same parameter/value sets, and nothing about any vendor's contract
or behavior has changed since the dates above, the re-run should reproduce: the same 727-cell
contract-sweep state distribution (443 fired / 284 skipped, the same six-way state split within
measurement noise); the same 79-contradiction docs-vs-wire tally at the same 612-pair
denominator; and the same 72-cell wire-behavior grid's rates and verdicts, within the sampling
noise the small-N repeatability designs (4-5 repeats per cell) already carry — a model moving
from `varies` to `deterministic` or back on a re-run of `seed_determinism`/`sampling_repeatability`
would not by itself falsify this document unless the new rate crossed the same verdict boundary
`check-probe-drift.py`'s own vocabulary already draws. This document is worth re-running against
the live wire within 90 days of the evidence dates above (by **2026-12-02**) — past that window,
vendor-side changes (a documentation update, a silent behavior change, a new model revision) are
plausible enough that any claim here should be treated as historical until re-confirmed, not
re-cited as current.
