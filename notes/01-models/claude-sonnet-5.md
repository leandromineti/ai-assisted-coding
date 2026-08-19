---
name: claude-sonnet-5
category: 1
vendor: Anthropic
url: https://platform.claude.com/docs/en/about-claude/models/overview
license: proprietary
open_source: false
model_id: claude-sonnet-5
release_mode: api-only
released: "GA 2026-06-30, no preview stage — launched as the default model on Free/Pro plans day one (verified 2026-08-17)"
context_window: 1000000
max_output: 128000
pricing: "$2 / $10 per MTok — now STANDARD: the launch framing 'introductory through 2026-08-31, then $3/$15' was retired and the scheduled increase cancelled (verified 2026-08-17; ledgers recorded at $2/$10 need no September renormalization)"
knowledge_cutoff: "Jan 2026 (reliable); training data Jan 2026"
model_features:   # nested per ADR-0014 (2026-08-19); values unchanged
  thinking: adaptive
  effort_control: "effort param; defaults high on Claude API and Claude Code"
  prompt_caching: "write 1.25x (5m TTL) / 2x (1h TTL), read 0.1x — $2.50 / $4 / $0.20 per MTok"
  batch_discount: "50% in+out ($1 / $5 per MTok); 300k max output via beta header"
checked: 2026-08-17
depth: survey
---

# Claude Sonnet 5

Anthropic's mid-tier: "the best combination of speed and intelligence." In this repo's
terms: **the standardized experiment model** — the deliberate cost/capability
compromise chosen so category-4 comparisons measure frameworks, not model headroom.

## The category-1 axes

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | OBSERVED (2026-08-17): 6 autonomous headless runs on the rig's tarpeek task (Run A + 5 screening baselines) — 6/6 completed with an installable artifact, 12–20 turns, zero blocking questions. See § Measured in this repo |
| Long-horizon coherence | · (the tarpeek task is too small to load this axis) |
| Usable context (vs advertised) | 1M advertised; unprobed here |
| Cost per completed task | **Measured** (2026-08-17, at $2/$10): $0.31–0.51 per completed tarpeek run, mean $0.41 (n=6). The time-sensitivity warning that used to live here is retired — see Surprises §1's dated correction: $2/$10 became the standard price, so August ledgers need no September renormalization |
| Release mode & access routes (1b) | API-only; Claude API + Bedrock + Vertex + Foundry. `effort` defaults to `high` on the Claude API and Claude Code — a cost-relevant default worth pinning in experiment configs |

## Role in this repo's work

- **The rig's pinned model** — exp-02's pre-run amendment names `claude-sonnet-5` the
  *sole* model for all arms of all category-4 comparisons
  ([`experiments/02-spec-kit-vs-plain/`](../../experiments/02-spec-kit-vs-plain/README.md),
  amendment §1; [`experiments/rig/`](../../experiments/rig/README.md) pins table).
- The machine's standing subagent tier for lighter search/mechanical work (alongside
  Opus for substantive analysis).
- Adaptive thinking; no legacy extended-thinking toggle — prompt/config written for
  4.x-era thinking controls doesn't carry over unchanged.

## Measured in this repo (2026-08-17, all OBSERVED)

Five unaided baseline runs on the tarpeek task (fresh containers, `package-hosts-only`,
CLI 2.1.220) plus the Run A calibration — the rig held everything fixed except the
model, so these are model-attributable behaviors, not harness effects:

- **Verifier distribution 18–20/21** (19 · 20 · 20 · 18 · 18, mean 19.0; Run A 20).
  Full tables: [`exp-02 log`](../../experiments/02-spec-kit-vs-plain/log.md)
  § Screening verdict.
- **Failure signature is fine-grained-but-incomplete error handling:** it
  differentiates exit codes (distinct not-a-tar vs empty codes in 3/5 runs) but 3/5
  runs let an unhandled traceback escape on a truncated archive, and 5/5 crash under
  strict stdio encoding on a non-UTF-8 member name (T4c). Timezone discipline was
  perfect (0/5 failures, UTC pinned or documented).
- **Known-groups anchor:** fully separated from Haiku 4.5 on the same instrument —
  every completed Haiku run scored 17/21, below Sonnet's worst (18). The reversal
  (Haiku beat Sonnet on the truncated-archive item) is a failure-style effect, not a
  capability inversion — see [`benchmark-survey`](../cross-cutting/benchmark-survey.md)
  § 6 and README conclusion 10.
- **Observed session throughput ≈ 91 tok/s** (mean = median, range 75–106, n=15
  sessions: screening + Run A′ + every exp-02 Run B step ≥500 output tokens).
  Session-level, not decode speed — computed by `scripts/observed-throughput.py`
  from the committed transcripts; definition and caveats in
  [`metrics.md`](../cross-cutting/metrics.md) § Observed session throughput. The
  planning rule of thumb this buys: ~2 min of API time per 10k output tokens.

## Surprises

1. **The introductory-pricing window lands mid-experiment-arc.** If exp-02 runs in
   August and exp-03 in September, their raw dollar ledgers are not comparable without
   normalizing to list price — recorded here *before* either run so the ledgers can't
   silently mislead.
   *Corrected 2026-08-17:* the window dissolved instead of closing — the vendor made
   $2/$10 the standard price and cancelled the scheduled 2026-09-01 increase (pricing
   page note, retrieved 2026-08-17). Every ledger in this repo recorded at $2/$10 is
   now simply at list price; the cross-month normalization concern is moot. The
   meta-lesson stands and sharpens: pricing claims drift *in both directions*, and a
   dated `checked:` is what let this one be corrected instead of silently rotting.
2. Max output 128k (and 300k via a batch-API beta header) — output ceilings have
   quietly stopped being the binding constraint for agent work; iteration structure
   has.

## Open questions

- ~~Exp-02 will produce the first measured trap-discovery and attention data on this
  model — fold the result back here (this report graduates to `deep-dive` when the
  repo's own measurements exist).~~ *Corrected 2026-08-17:* the measurements exist
  (§ Measured in this repo) and are folded back, but the graduation clause predated
  methodology rule 1a — closure caps a report at `survey`; measured behavior is
  OBSERVED-grade, and no amount of it reads the weights. Depth stays `survey`,
  now with evidence in every load-bearing cell.
- Does `effort: high`-by-default change the cost profile enough that experiment
  configs should pin it explicitly? (The rig currently doesn't set it.)
