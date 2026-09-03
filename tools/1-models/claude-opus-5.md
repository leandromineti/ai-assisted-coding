---
name: claude-opus-5
category: 1
maker: Anthropic
url: https://platform.claude.com/docs/en/about-claude/models/overview
license: proprietary
access: closed-source
model_id: claude-opus-5
release_date:
  date: 2026-07-24
  stage: GA
  note: "no preview stage — 'available today' across all surfaces (verified 2026-08-17)"
context_window: 1000000
max_output: 128000
pricing:
  input: 5          # USD per MTok — base list rate (see the registry's rule)
  output: 25
  currency: USD
  regime: flat
  note: "$5 / $25 per MTok; fast mode (research preview, Claude API only) $10 / $50 (verified 2026-08-17)"
knowledge_cutoff:
  date: 2026-05          # the limit date on training data
  basis: vendor-stated
  note: "May 2026 (reliable); training data May 2026 — the two coincide. corroborated 2026-08-26 by a second first-party surface — the [Opus 5 system card](../../references/cards/2026-claude-opus-5.md) §1.1: 'Claude Opus 5's knowledge cutoff date is May 2026' — and re-verified the same day against the models overview page's own structured data (`reliableKnowledgeCutoff` / `trainingDataCutoff` — the field name is where this note's '(reliable)' comes from). The freshest cutoff in the current lineup, newer than Fable 5's and Sonnet 5's Jan 2026"
model_features:   # nested per ADR-0014 (2026-08-19); reasoning keys split per ADR-0040
  reasoning: true
  # Both keys below settled 2026-08-26 against the thinking + effort docs (§ Reasoning surface).
  reasoning_type: default-on   # docs table Default "On"; accepts `disabled` — but ONLY at effort ≤ high, see below
  reasoning_effort: "levels:low/medium/high/xhigh/max@high"   # "supports all five effort levels"; `output_config.effort`
  prompt_caching: "write 1.25x (5m TTL) / 2x (1h TTL), read 0.1x — $6.25 / $10 / $0.50 per MTok"
  batch_discount: "50% in+out ($2.50 / $12.50 per MTok); 300k max output via beta header"
  fast_mode: true    # "up to 2.5x higher output tokens per second" at $10/$50 (2x list), `speed: "fast"` + fast-mode-2026-02-01 beta header; research preview, Claude API only, Opus 5/4.8 only; explicitly NOT the Priority Tier ("Fast mode is not available with a Priority Tier commitment") — first-party fast-mode page, verified 2026-08-27; OBSERVED 2026-08-31: a plain pay-as-you-go key with no waitlist enrollment was served `usage.speed: "fast"` on the first request — the research-preview gate did not gate in practice
  stop_sequence_honesty: "honest — OBSERVED 2026-09-03: stop-honored truncation before the trigger word, and the response's own stop_reason field reports the distinguishable value stop_sequence (vs. end_turn on the no-stop control), cell_id:`claude-opus-5--stop-truncation--triggering--default`, probe_id:`claude-opus-5--stop-truncation--triggering--default--58a5a42f`, promoted ADR-0050."
  seed_determinism: "n/a (no request-side field) — OBSERVED 2026-09-03: Anthropic's Messages API reference documents no seed parameter for claude-opus-5 — the full top-level Body parameters list was read end to end with no match (rule 1b checked-absence), docs-claims:`seed/anthropic`, promoted ADR-0050."
  sampling_repeatability: "0/4 repeat pairs (no-signal) — OBSERVED 2026-09-03: claude-opus-5 rejects an explicit temperature value outright in default mode (HTTP 400); this default-config-repeatability SUBSTITUTE asks the same default-sampling question, but four of the five repeat calls hit the max_tokens budget while one completed naturally (end_turn) — the mixed truncation states confound the comparison, so the 0/4 rate reflects that mismatch, not observed sampling variation, cell_id:`claude-opus-5--default-config-repeatability--no-temperature--default`, probe_id:`claude-opus-5--default-config-repeatability--no-temperature--default--r1--08c093fe`, promoted ADR-0050."
  multi_candidate_delivery: "n/a (no request-side field) — OBSERVED 2026-09-03: Anthropic's Messages API reference documents no n/candidateCount-equivalent multi-candidate parameter for claude-opus-5 — the full top-level Body parameters list was read end to end with no match (rule 1b checked-absence), docs-claims:`n/anthropic`, promoted ADR-0050."
checked: 2026-08-17
depth: survey
---

# Claude Opus 5

Anthropic's agentic workhorse: "for complex agentic coding and enterprise work." The
tier below Fable 5 on capability and half its price; 1M context is **standard** (the
seed inventory's "ships a 1M variant" phrasing is stale — the docs list 1M as the base
window, verified 2026-07-31).

## The category-1 axes

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | Anecdotal-positive from heavy orchestration use (see Role) — no measured figure |
| Long-horizon coherence | Anecdotal-positive: multi-hour deep-dive/experiment sessions in this repo's history ran on it without derailment; not instrumented |
| Usable context (vs advertised) | 1M advertised; sessions here run with summarization long before the raw window binds, so unprobed |
| Cost per completed task | · (exp-01's cost data measured *framework* overhead on this model, not the model itself) |
| Release mode & access routes (1b) | API-only; all four cloud routes. `effort` defaults `high` on Claude API + Claude Code |

## Reasoning surface

**Both cells resolved 2026-08-26** (issue #38), against two pages neither of which is this
report's `url` — the overview table does not carry either fact:

- [`/build-with-claude/effort`](https://platform.claude.com/docs/en/build-with-claude/effort)
  — *"Claude Opus 5 supports all five effort levels"*, *"The API default is `high`"*, and
  *"Setting `effort` to `"high"` produces exactly the same behavior as omitting the
  `effort` parameter entirely."* The dial is `output_config.effort`, request-level.
- [`/build-with-claude/thinking-troubleshooting`](https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting#supported-models)
  — the per-model configuration table: Opus 5 is *"Adaptive only"*, Default **On**, and
  *"Models marked `On` default to thinking but accept `thinking: {type: "disabled"}`."*

**Opus 5 is the sweep's only conditionally-toggleable model, and it strains the enum.**
The table's footnote: *"Claude Opus 5 accepts `"disabled"` at effort `high` or below;
combining it with effort `xhigh` or `max` returns a 400 error. This restriction applies to
Claude Opus 5 and later models and is enforced on each request."* So toggleability here is
not a static property of the model — it is a function of another parameter's value in the
same request. `default-on` is the honest cell (it defaults on and does accept `disabled`),
but a harness that hardcodes `disabled` and raises effort gets a 400 rather than a
downgrade, which no cell value can convey on its own.

What the old free-text cells held, for the record (verified 2026-08-17): `thinking:
adaptive` and *"effort param; defaults high on Claude API and Claude Code."* Neither was
wrong; neither was enough. `adaptive` names who *sizes* the reasoning and is silent on the
toggle, and a default without its level set cannot fill `levels:<set>@<default>` — which is
what kept both cells at `·` through the ADR-0040 reshape rather than being guessed.

The row's `checked:` stays **2026-08-17**: only the reasoning cells were re-verified today,
and the field dates the whole spec block — same discipline as the `knowledge_cutoff` note's
`re-verified 2026-08-26` above it.

## Role in this repo's work

- **Exp-01's arm model**: both GSD and plain arms ran on Opus per the original standing
  machine rule ([`experiments/01-gsd-vs-plain/`](../../experiments/01-gsd-vs-plain/README.md))
  — superseded by Sonnet 5 for exp-02+ (standardization decision, 2026-07-28).
- The machine's designated subagent tier for substantive analysis/planning work, and
  the orchestrating model for most of this repo's session history through 2026-07-30.
- Its **May 2026 knowledge cutoff** — newer than Fable 5's — is occasionally
  load-bearing for a repo that studies tools released through mid-2026: less of the
  survey territory is post-cutoff for Opus than for the flagship.

## Probed (2026-08-31) — first observed-grade cells

The first pass of [issue #42](https://github.com/leandromineti/ai-assisted-coding/issues/42)'s
thin-client probes (raw HTTP, no SDK; combined cost < $0.001):

1. **Fast mode is obtainable, not just documented.** A fresh pay-as-you-go key with no
   waitlist enrollment sent `speed: "fast"` + the beta header and was served
   `usage.speed: "fast"` on the first request. The docs' research-preview framing
   ("contact your account manager… join the waitlist") did not gate in practice — the
   distance between a vendor's stated access process and its enforced one is itself a
   1b-flavored fact.
2. **The conditional-toggleability strain is confirmed observed**, with a better error
   than the docs promise: `thinking: {type: "disabled"}` at `output_config.effort:
   "xhigh"` returns 400 — *"output_config.effort 'xhigh' is not supported when thinking
   is disabled on this model. Use effort 'high' or below, or enable thinking."* The
   `default-on` cell's condition (recorded 2026-08-26 from docs) now rests on the API's
   own refusal, at zero cost — a rejected request bills nothing.

## Surprises

1. **The workhorse knows more recent facts than the flagship** (May vs Jan 2026
   cutoff). Capability tiering and knowledge recency are independent axes — worth
   remembering when choosing a model to *survey recent tools* vs to *reason hard*.

## Open questions

- Exp-01 vs exp-02 will eventually give a loose Opus-vs-Sonnet contrast on similar
  task shapes (different tasks, so indicative only — the cross-experiment caveat in
  the exp-02 prereg applies).
