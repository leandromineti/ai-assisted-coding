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
