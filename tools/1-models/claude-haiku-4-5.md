---
name: claude-haiku-4-5
category: 1
vendor: Anthropic
url: https://platform.claude.com/docs/en/about-claude/models/overview
license: proprietary
open_source: false
model_id: claude-haiku-4-5-20251001
release_mode: api-only
released: "GA 2025-10-15, no preview stage — the model-id snapshot suffix (20251001) predates the announced date by two weeks; the announcement text is the source (verified 2026-08-17)"
context_window: 200000
max_output: 64000
pricing:
  input: 1          # USD per MTok — base list rate (see the registry's rule)
  output: 5
  currency: USD
  regime: flat
  note: "$1 / $5 per MTok (verified 2026-08-17)"
knowledge_cutoff:
  date: 2025-07          # the limit date on training data
  basis: vendor-stated
  note: "Feb 2025 (reliable); training data Jul 2025 — the lineup's only model where the two DIVERGE, by five months. re-verified 2026-08-26 against the models overview page's own structured data (`reliableKnowledgeCutoff` / `trainingDataCutoff` — the field name is where this note's '(reliable)' comes from); the docs define the pair as knowledge = the date through which knowledge is most extensive, training data = the broader range of data used — RECORDED HERE AS THE TRAINING-DATA LIMIT (2025-07); the vendor's finer 'reliable knowledge cutoff' is 2025-02 (ADR-0038: one date, the outer bound)"
model_features:   # nested per ADR-0014 (2026-08-19); reasoning keys split per ADR-0040
  reasoning: true
  reasoning_type: opt-in      # confirmed 2026-08-26: docs table Default "Off", "Extended only", rejects `adaptive`
  reasoning_effort: budget:tokens   # the sweep's only `budget:` dial; effort's supported-models list EXCLUDES 4.5
  prompt_caching: "write 1.25x (5m TTL) / 2x (1h TTL), read 0.1x — $1.25 / $2 / $0.10 per MTok"
  batch_discount: "50% in+out ($0.50 / $2.50 per MTok)"
checked: 2026-08-17
depth: survey
---

# Claude Haiku 4.5

Anthropic's small/fast tier: "the fastest model with near-frontier intelligence." The
only current Claude model still on a dated model ID (`-20251001`), the only one at
200k context, and the only one with legacy extended thinking instead of adaptive
thinking — a generation seam running visibly through the lineup.

## The category-1 axes

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | OBSERVED (2026-08-17): 5 autonomous headless runs on the rig's tarpeek task — all 5 sessions completed and reported success, but 1/5 shipped an artifact that is dead on arrival off-container (undeclared runtime dependency). See § Measured in this repo |
| Long-horizon coherence | · (its designed role — short mechanical subagent work — mostly sidesteps the axis) |
| Usable context (vs advertised) | 200k advertised; unprobed |
| Cost per completed task | **Measured** (2026-08-17): $0.10–0.20 per tarpeek run, mean $0.150 (n=5) — ~2.7× cheaper than Sonnet's measured $0.41 on the identical task, at a measured quality gap (17/21 vs 19.0/21) and one packaging failure. The retry-rate question below is no longer hypothetical: the DOA run *is* the retry case |
| Release mode & access routes (1b) | API-only; four cloud routes |

## Reasoning surface

The sweep's only `budget:` dial, and the reason the `reasoning_effort` family is closed
rather than free. The old free-text cell held, verified 2026-08-17: *"extended
(budget_tokens) — the only current model without adaptive thinking."*

That string carries both cells: **extended** means reasoning happens only when the caller
asks for it (`reasoning_type: opt-in`), and **budget_tokens** means the caller allocates
the size up front rather than picking a level the model spends against
(`reasoning_effort: budget:tokens`). Every other model in the sweep is on a level enum —
this is the generation seam, visible in one column instead of buried in prose.

**Both cells were derivations at the reshape, and both were confirmed 2026-08-26** — worth
recording, because the alternative was to guess and be right by luck:

- [`/build-with-claude/thinking-troubleshooting`](https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting#supported-models)
  — the per-model table gives Haiku 4.5 as *"Extended only"*, Default **Off**, rejecting
  `"adaptive"` with a 400. Default Off is precisely `opt-in`, read from the vendor rather
  than inferred from what "extended" implies.
- [`/build-with-claude/effort`](https://platform.claude.com/docs/en/build-with-claude/effort)
  — its supported-models list **excludes** Claude Haiku 4.5 entirely. So the absence of a
  level dial here is now a verified absence rather than an unexamined one, and
  `budget:tokens` is the whole surface. (Claude Opus 4.5 is called out as *"the only
  extended-thinking-only model that supports effort"* — 4.5-era models are not uniform,
  which is why this had to be read per model.)

The row's `checked:` stays **2026-08-17**: only the reasoning cells were re-verified today,
and the field dates the whole spec block.

## Role in this repo's work

None pinned. Notably, the tools *studied* here use it where this repo doesn't: **ECC's
instinct pipeline runs its background analysis on Haiku**
([`../6-extensions/ecc.md`](../6-extensions/ecc.md)), and
hermes routes auxiliary/compression work to cheap models of this class. The small tier's
real niche in mid-2026 practice appears to be *background cognition inside other
tools* — continuous, low-stakes, volume-priced — rather than interactive work.

## Measured in this repo (2026-08-17, all OBSERVED)

Five unaided baseline runs on the tarpeek task, identical rig configuration to the
Sonnet 5 screening runs (same harness CLI 2.1.220, same instruction, same enforced
network) — the first in-repo measurement where only the model varied:

- **Uniform 17/21 on the verifier in every completed run** (n=4; Sonnet: 18–20).
  Faster wall-clock (1m11s–2m05s) but *more* turns (16–34 vs Sonnet's 12–20) — it
  iterates smaller.
- **Observed session throughput ≈ 109 tok/s** (median 116, range 91–124, n=5) — only
  ~20% above Sonnet 5's 91 in the same rig, far less than the tier gap suggests:
  session overhead (TTFT, tool turns) compresses the difference. Computed by
  `scripts/observed-throughput.py`; caveats in
  [`metrics.md`](../../docs/metrics.md) § Observed session throughput.
- **Failure style, not just failure count:** blanket `rc=1` error handling — no
  traceback ever escapes (it *beat* Sonnet on the truncated-archive trap, 0/4 vs
  3/5) but no failure is distinguishable (distinct-exit-codes trap failed 4/4).
  The entire ambient-config family failed in every completed run: local-time
  output, undocumented, plus the strict-stdio crash.
- **The packaging DOA (1/5):** `cli.py` imports `tabulate`, the README documents
  it, `pyproject.toml` never declares it — the agent pip-installed it by hand
  in-container, so its own tests passed while the shipped package cannot run from
  a fresh install. A concrete instance of conclusion 4 (structural completeness ≠
  runtime correctness) in packaging.
- **Discarded-candidate checks caught it where Sonnet never failed:** filter-to-empty
  crash 2/4, directory-path traceback 1/4 (Sonnet: 0 failures in 25 check-runs).
  Full tables: [`exp-02 log`](../../experiments/02-spec-kit-vs-plain/log.md)
  § Model-tier calibration verdict.

## Surprises

1. **Feb 2025 knowledge cutoff** — seventeen months stale by now, in a lineup whose
   workhorse knows May 2026. For the background-cognition role that mostly doesn't
   matter; for anything touching current tooling it quietly does.

## Open questions

- The `learning_loop` machinery this repo now tracks (hermes, codex, ECC) all needs an
  always-on cheap model. Is the small tier's economics the actual enabler of the
  autonomous-memory pattern — i.e., is conclusion 8's absorption story downstream of
  Haiku-class pricing?
