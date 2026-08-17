# Metric vocabulary

`created: 2026-07-31`

One definition per metric, each traceable to a source in [`../../refs/`](../../refs/index.md) or
to the experiment that scarred it. Written because this repo kept inventing measurements —
"trap score", "attention split" — without checking whether the literature already had a defined,
validated version. Twice it did, and better.

Rule: **do not define a metric here from an unread source.** Everything cited below is a
`read_depth` of `full` or `extract` in the reference index; `build-refs-index.py --check`
enforces it.

## Reliability

### `pass^k`
Source: [`tau-bench`](../../refs/tau-bench.md) (ICLR 2025), §3.

With `n` trials of a task of which `c` succeed:

```
pass^k = E_task[ C(c,k) / C(n,k) ]      # ALL k trials succeed
pass@k = 1 − E_task[ C(n−c,k) / C(n,k) ]  # at least one succeeds
pass^1 = pass@1 = E[c/n]
```

Why it matters here: **every measurement in exp-01 and exp-02 is n=1 per arm**, so a framework
whose value is consistency rather than peak quality is invisible to us by construction. τ-bench
found gpt-4o above 60% average success collapsing below 25% at pass^8. A framework that turns
3-of-5 into 5-of-5 has done real work and would score identically to plain on a single run.

At Run A's measured $0.374, k=5 costs under $2. The barrier was never cost.

## Clarification and information recovery

All four from [`clareval`](../../refs/clareval.md) §3.5 and Appendix B. They presuppose a task
built by **withholding** known information: `K` = expert-annotated required intents, `P` =
withheld premises, `R ⊆ P` = premises the agent recovered.

| Metric | Definition | Reads as |
|---|---|---|
| **KQC** — Key Question Coverage | \|C\| / \|K\| | did it ask about the right things? |
| **PIR** — Premise Identification Rate | \|I\| / \|P\|, first turn only | zero-shot planning quality |
| **MPR** — Missing Premises Recall | \|R\| / \|P\| by dialogue end | did it eventually get the information? |
| **ATC** — Average Turns to Clarify | (1/\|R\|) Σ Turn(pᵢ) | how much user friction it cost |
| **EAR** — Efficiency-Adjusted Recall | (1/\|P\|) Σ_{p∈R} 1 / log₂(Turn(p)+1) | recall, discounted by delay |

**EAR is the one to reach for**, because it closes a hole our attention-split instrument has:
MPR alone rewards an agent that asks thirty questions, ATC alone rewards one that asks none.
EAR gives a premise clarified in turn 1 a weight of 1.0, turn 2 ≈ 0.63, turn 3 = 0.5, and 0 if
never clarified — penalising both the "lazy agent" and the "inefficient agent".

**Implementation trap:** ATC is undefined when `|R| = 0` (ClarEval treats it as NaN and excludes
it from averages). An arm that clarifies nothing must not score as maximally efficient.

## Underspecification detection

Source: [`ambig-swe`](../../refs/ambig-swe.md) (ICLR 2026), §4.

Present the agent with fully-specified and underspecified tasks at random and measure whether it
chooses to interact: **accuracy**, **FPR** (interacted when it didn't need to — burden on the
user), **FNR** (failed to interact when it should have — silent wrong assumptions). Ideal is high
accuracy with both rates low.

**This is the control exp-02 is missing.** Ambig-SWE shows detection accuracy on one model moving
0.74 → 0.89 purely by how strongly the prompt encourages asking. So *encouragement level* is a
variable, not a constant, and must be declared and held identical across arms — otherwise
"the framework asked and plain didn't" measures the prompt, not the framework.

## Apparatus validation

### `ECE_Human–LLM`
Source: [`lost-in-simulation`](../../refs/lost-in-simulation.md), §3.4.

`Σᵢ wᵢ · |sᵢ^(Human) − sᵢ^(LLM)|` — weighted absolute deviation between agent success measured
with real users vs simulated ones, across difficulty bins; 0 = perfectly calibrated. The metric
to use if we ever check an oracle against real people.

Its finding is the reason to record the apparatus as a variable: swapping *only* the simulated
user model moved measured agent success ~9 points. And the miscalibration is **non-monotonic** —
simulated users overestimate agent success on moderate tasks and underestimate it on hard ones —
so no single correction factor fixes it.

## Ours, and what's wrong with them

### Trap score
Pass/fail against a preregistered set of seeded defect classes, machine-checked
(`experiments/rig/tarpeek/tests/`). **Retired as a comparison instrument** by exp-02 Run A: the
plain baseline scored 8/8, leaving no headroom (methodology 5d, issue #4). Still useful as a
regression check — it just cannot measure a *difference*.

**Un-retired as v2 (2026-08-17).** The 8/8 retirement was a single-point-calibration artifact
(methodology 5f): densified to 21 binary checks and calibrated against **five** fresh baseline
runs, the instrument discriminates — baselines score 18–20/21 (mean 19.0) with three checks
failing at 40–100% baseline rates — and it passes a known-groups test (below). A trap score is
read **against the measured baseline noise band**, never as a raw pass count: 21/21 beats every
observed baseline; 19–20 is inside baseline variance. Verdict tables:
[`exp-02 log`](../../experiments/02-spec-kit-vs-plain/log.md).

The withholding-information design below remains the plan for exp-03's headroom — it is a
different instrument for a different question, not a correction to this one:
withholding produces headroom reliably at both scales measured in the literature — ~80 points on
function-level tasks ([`clareval`](../../refs/clareval.md) Figure 3) and 28 points on repository
issues ([`ambig-swe`](../../refs/ambig-swe.md) Figure 3) — whereas escalating edge-case
difficulty needed its own headroom proof (which v2 now has).

### Known-groups separation
Standard psychometric construct-validity check, imported for instruments here on 2026-08-17
([`benchmark-survey`](benchmark-survey.md) §6): run the instrument on a population it *should*
separate, under otherwise identical conditions, and require separation. exp-02's execution:
Haiku 4.5 vs Sonnet 5, same harness/task/environment (n=5 each) — complete separation (every
completed Haiku run below every Sonnet run, plus one Haiku completion failure). Two caveats the
execution taught: report **completion rate separately** from per-check scores (a run that can't
install isn't a low score, it's a different failure), and judge on **distributions and
family-level patterns, not per-item dominance** — one trap item reversed (the weaker tier's
blanket error handling never tracebacks), because trap items can measure failure *style* rather
than skill.

### Attention split
Wall-clock divided into *autonomous* vs *attention-required*, with each blocking event logged
verbatim (exp-02 protocol). Genuinely ours, and named as a gap by
[`from-prompt-to-process`](../../refs/from-prompt-to-process.md) §7 ("rate of human review
required"). But it is coarser than ATC/EAR, which price *when* information arrived rather than
just how long someone was blocked. Prefer ATC + EAR where a per-question turn index exists;
keep attention split for arms that block on approvals rather than questions.

First real measurement 2026-08-17 (exp-02 Run B): 2 blocking events, ~63s
orchestrator-blocked in a 21m33s run. The measurement also exposed the instrument's
sharpest limitation, beyond the coarseness noted above: the run's decisive human
moment was not the *duration* of the block but the *content* of the answer (a
one-line deferral decided the exit-code trap). Time-based attention metrics price
the interruption, not the leverage.

### Correction rate (candidate, borrowed 2026-08-17 — not yet used in an experiment)
`correction attempts / trajectory steps`, from
[`agent-frameworks-eval`](../../refs/agent-frameworks-eval.md) (its RQ2). Borrowed WITH
its own sharpest caveat, which the paper demonstrates in its data: **zero corrections
signals missing self-monitoring, not efficiency** — its two lowest-correction frameworks
also had 3–10% repair rates. Never read this metric alone; pair it with an effectiveness
score. Candidate use here: exp-03's arms, where a gates-only harness should show
corrections concentrated at the gate rather than spread through the trajectory.

### Observed session throughput
`output_tokens (dominant model) / duration_api_ms`, per headless session, computed from
committed harness transcripts by `scripts/observed-throughput.py` — never hand-typed.
This is **session-level agent throughput, not decode speed**: the denominator includes
per-turn TTFT, tool-result processing, and inter-turn overhead, so it lower-bounds raw
generation and is the honest number for planning agent-run wall-clock. Known behaviors
(2026-08-17, first measurement): overhead compresses tier gaps (Haiku 4.5 measured only
~20% faster than Sonnet 5 in-session — far less than the tier difference suggests), and
sub-500-token turns are latency-bound, not throughput-bound (excluded by the script).
Why recorded at all: vendors publish no first-party tokens/sec (the models matrix
correctly has no column), but the planned **local open-weight arm** makes throughput a
first-class constraint — on self-hosted hardware, tok/s is the gating resource, and
this metric is the comparable the API side needs to already have (issue #15).

### Cost ledger
Output · cache-write · cache-read · uncached-input tokens, per model, from transcripts
(methodology 5c). No literature equivalent found — most papers report latency or nothing.
Keep it, and keep attributing per model: Run A's ledger showed an auxiliary Haiku call the
protocol's "sole model" wording hadn't anticipated.
