---
title: "Measuring AI-Coding Frameworks: a $3 Rig, a Trap Instrument, and One Revealing Question"
date: 2026-08-17
description: "No public benchmark isolates the model from the harness — so I built the isolation myself. What a preregistered A/B says about whether spec-driven workflow frameworks buy code quality, and what the instrument taught me on the way."
tags: ["ai", "developer-tools", "benchmarks", "experiments"]
maturity: seed
draft: true
series: "AI-Assisted Coding, Measured"
seriesOrder: 2
---

The [first article in this series](the-ai-coding-stack.md) ended on an accusation:
public leaderboards score model+harness *pairings*, so nobody knows which category
they're praising. The one benchmark I found that fixes the harness turned out to
route each model through a different system prompt — a confound its own maintainer
didn't know about until [I reported it](../tools/1-models/README.md), which became
the repo's first upstream contribution
([conclusion 2](../docs/conclusions.md)).

This article is about building the isolation myself, at personal scale, and what it
measured. Fair warning about the sample sizes up front: single runs are called
probes here, because that's what they are. The interesting part is less any single
number than how often the *instrument* — not the tools under test — turned out to be
the thing that needed engineering.

## The rig

<figure>
  <img src="img/the-rig.svg" alt="Diagram of the measurement rig: inside a dashed border labeled 'internal Docker network — no direct route out', an arm container (pinned image by digest, pinned harness CLI and model, fixed timezone and locale) where the agent works autonomously in /app on the same one-paragraph task. All egress flows through an allowlist proxy — the only way out — whose log is the probe record. Green arrows reach the model API and the package registry (allowed); a red dashed arrow to 'everything else' is denied and logged, so no web research is possible. Below, a hidden verifier lane the arms never see: 21 binary checks over the final container state in a fresh venv, five seeded trap families, ground truth measured from what the fixture builder actually built, proven fails-closed and fair before any arm ran. The score flows into a box reading 'read against the noise band: five fresh baselines, 18–20 of 21, mean 19.0 — a score is a draw from a distribution, not a truth'." />
  <figcaption>The rig: everything pinned, egress enforced and logged, and a verifier the arms never see.</figcaption>
</figure>

The setup ([full description](../experiments/rig/README.md)) is deliberately boring:

- A **pinned container** — base image by digest, harness CLI version pinned, fixed
  timezone and locale. One task, packaged in Terminal-Bench's community format.
- A **hidden verifier** the tools under test never see, asserting against ground
  truth that was *measured from what the fixture builder actually built*, never
  assumed.
- An **enforced network condition**: the container sits on an internal Docker
  network with no route out; the only egress is an allowlist proxy (package
  registries + the model API), and the proxy log is the probe record. Version 1
  merely denied the web *tools* in harness config — then I measured `curl` reaching
  the internet from inside. Tool-layer denial is not a network policy. Now it's
  enforced at egress and probed before every run.

The task is small on purpose: build `tarpeek`, a ~150-line Python CLI that
summarizes tar archives — with five families of hidden traps seeded in the fixtures
(encoding, time, exit codes, ambient config, safety). Total cost to calibrate the
whole thing and run a two-arm experiment: about **$8 in API spend**, of which the
scored arms were [under $5](../experiments/02-spec-kit-vs-plain/log.md).

## The instrument fought back

Almost everything I learned about measurement came from the instrument failing in
instructive ways ([the full log](../experiments/02-spec-kit-vs-plain/log.md) is
append-only and unflattering):

**It saturated.** The first baseline run scored 8/8 — a ceiling, which means the
instrument couldn't measure a *better* arm. Preregistration had to stop and rebuild:
densify the 8 checks into 21 within the same trap families, then prove three
properties before accepting the new set — a do-nothing stub fails **every** check, a
hardened reference implementation passes **every** check, and the calibration
artifact fails at least three. That last leg failed (the old baseline was genuinely
good), which triggered a preregistered escalation: screen a committed pool of *new*
trap candidates against five fresh baseline runs, keep what fails in ≥2 of 5. The
result was a clean null — all seven candidates passed everywhere and were discarded.

**The escalation still paid.** Five fresh baselines replaced a point estimate with a
distribution: scores of 19 · 20 · 20 · 18 · 18 out of 21. Three checks carry all the
discrimination (baseline failure rates of 40–100%); the rest are consumed at this
task size. Every later comparison gets read against that noise band, not against a
single lucky draw.

**It separates model tiers — non-monotonically.** As a validity check, five runs of
a deliberately weaker model (Haiku 4.5) against the same instrument: every completed
run scored exactly 17/21, fully below the stronger model's worst draw — known-groups
validity, preregistered ([conclusion 10](../docs/conclusions.md)). The reversal
inside that result is the finding I keep retelling: the weaker model *beat* the
stronger one on the truncated-archive trap, because its blanket `rc=1` error
handling never lets a traceback escape — while failing everything that requires
*distinguishing* failures. Trap items don't measure skill on a single axis; some
measure **failure style**.

## The A/B: does intent capture buy code quality?

The experiment ([preregistered 2026-07-28, protocol untouched since](../experiments/02-spec-kit-vs-plain/README.md))
pits GitHub's spec-kit — a spec-driven workflow framework whose center of mass is
*intent capture* — against a plain agent with the identical one-paragraph task
prompt. Same model, same container, same enforced network, same hidden instrument.
Two preregistered predictions: the framework writes materially better
**requirements** (P1), and its **code** is equal-or-worse on the hidden traps (P2),
because nothing in its pipeline ever measures the domain.

Both held ([results](../experiments/02-spec-kit-vs-plain/README.md#results-2026-08-17--both-arms-run-under-amendment-4-protocol-above-untouched),
[conclusion 11](../docs/conclusions.md)):

| | Plain arm | spec-kit arm |
|---|---|---|
| Hidden traps | 19/21 | 19/21 — the **same two failures** |
| Written requirements | ~10 prose claims | 21 numbered criteria, 6 explicit assumptions |
| Cost / wall clock | $0.57 / 2m49s | $4.43 / 21m33s (~7.8×) |

The number that matters isn't in the table. During the framework's clarify step, it
asked me exactly one blocking question — and it was *precisely the right question*,
aimed dead at one of the hidden traps: should different failure reasons get distinct
exit codes, or one generic non-zero code? Then it **recommended the trap-failing
answer** ("a single generic exit code is simpler"). My preregistered policy was to
defer — "your call, make a reasonable choice and document the assumption" — so the
framework took its own recommendation, documented it beautifully, and wrote tests
that enforced the failing behavior faithfully. The same machinery pinned ISO-8601
UTC timestamps before any code existed, deciding the timezone traps in the *passing*
direction.

That's the mechanism in one anecdote: **intent capture steers trap-relevant
decisions — in both directions — but discovers nothing.** A framework that never
measures the domain converts ambiguity into *documented* decisions, not *correct*
ones; which way they go is the model's priors wearing a process costume. The
measured quality margin in an earlier framework experiment came from agents that
probed the domain and gates that checked measured values
([conclusion 6](../docs/conclusions.md)) — and that decomposition has now survived
its second framework.

## Small numbers worth having

- Baseline cost for this task class: **~$0.41 per completed run** (the weaker tier:
  $0.15). The whole two-month measurement program, including all calibration,
  fits in a lunch budget.
- Observed session throughput: **~91 tokens/second** for the workhorse model,
  ~109 for the small one — session-level, overhead included, which is why the tier
  gap compresses to ~20% ([metric definition](../docs/metrics.md)).
  Rule of thumb that falls out: ~2 minutes of API time per 10k output tokens.
- Human attention cost of the framework arm: **two blocking events, ~63 seconds**.
  The framework's rationed clarification budget is real — but as the exit-code story
  shows, time-based attention metrics price the interruption, not the leverage of
  the answer.

## What's next

Two arms are queued. **Exp-03** strips the framework question to its core: a minimal
harness with only the two mechanisms the evidence credits — empirical grounding and
measured verification gates — against the now-confirmed baseline. And a **local
open-weights arm**: the same instrument pointed at models running on my own
hardware, where the field's real bottleneck isn't benchmark scores but
tokens-per-second ([the groundwork](../tools/1-models/README.md)).

---

*All experiments in this series are preregistered before any run, logs are
append-only, and every number above links to the file it was copied from. If a link
contradicts this article, the link is newer — trust it.*
