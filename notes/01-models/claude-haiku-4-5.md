---
name: claude-haiku-4-5
layer: 1
vendor: Anthropic
url: https://platform.claude.com/docs/en/about-claude/models/overview
license: proprietary
open_source: false
model_id: claude-haiku-4-5-20251001
release_mode: api-only
released: "GA 2025-10-15, no preview stage — the model-id snapshot suffix (20251001) predates the announced date by two weeks; the announcement text is the source (verified 2026-08-17)"
context_window: 200000
max_output: 64000
pricing: "$1 / $5 per MTok (verified 2026-08-17)"
knowledge_cutoff: "Feb 2025 (reliable); training data Jul 2025"
thinking: "extended (budget_tokens) — the only current model without adaptive thinking"
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

## The layer-1 axes

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | OBSERVED (2026-08-17): 5 autonomous headless runs on the rig's tarpeek task — all 5 sessions completed and reported success, but 1/5 shipped an artifact that is dead on arrival off-container (undeclared runtime dependency). See § Measured in this repo |
| Long-horizon coherence | · (its designed role — short mechanical subagent work — mostly sidesteps the axis) |
| Usable context (vs advertised) | 200k advertised; unprobed |
| Cost per completed task | **Measured** (2026-08-17): $0.10–0.20 per tarpeek run, mean $0.150 (n=5) — ~2.7× cheaper than Sonnet's measured $0.41 on the identical task, at a measured quality gap (17/21 vs 19.0/21) and one packaging failure. The retry-rate question below is no longer hypothetical: the DOA run *is* the retry case |
| Release mode & access routes (1b) | API-only; four cloud routes |

## Role in this repo's work

None pinned. Notably, the tools *studied* here use it where this repo doesn't: **ECC's
instinct pipeline runs its background analysis on Haiku**
([`../03-capability-extensions/ecc.md`](../03-capability-extensions/ecc.md)), and
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
- **Failure style, not just failure count:** blanket `rc=1` error handling — no
  traceback ever escapes (it *beat* Sonnet on the truncated-archive trap, 0/4 vs
  3/5) but no failure is distinguishable (distinct-exit-codes trap failed 4/4).
  The entire ambient-config family failed in every completed run: local-time
  output, undocumented, plus the strict-stdio crash.
- **The packaging DOA (1/5):** `cli.py` imports `tabulate`, the README documents
  it, `pyproject.toml` never declares it — the agent pip-installed it by hand
  in-container, so its own tests passed while the shipped package cannot run from
  a fresh install. A concrete instance of conclusion 4 (structural completeness ≠
  runtime correctness) at the packaging layer.
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
