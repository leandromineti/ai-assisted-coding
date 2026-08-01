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

The replacement is not a harder trap set: withholding information produces headroom reliably at
both scales measured in the literature — ~80 points on function-level tasks
([`clareval`](../../refs/clareval.md) Figure 3) and 28 points on repository issues
([`ambig-swe`](../../refs/ambig-swe.md) Figure 3) — whereas escalating edge-case difficulty is
speculative and needs its own headroom proof.

### Attention split
Wall-clock divided into *autonomous* vs *attention-required*, with each blocking event logged
verbatim (exp-02 protocol). Genuinely ours, and named as a gap by
[`from-prompt-to-process`](../../refs/from-prompt-to-process.md) §7 ("rate of human review
required"). But it is coarser than ATC/EAR, which price *when* information arrived rather than
just how long someone was blocked. Prefer ATC + EAR where a per-question turn index exists;
keep attention split for arms that block on approvals rather than questions.

### Cost ledger
Output · cache-write · cache-read · uncached-input tokens, per model, from transcripts
(methodology 5c). No literature equivalent found — most papers report latency or nothing.
Keep it, and keep attributing per model: Run A's ledger showed an auxiliary Haiku call the
protocol's "sole model" wording hadn't anticipated.
