# The category-2 program — why framework A/Bs stopped and the bundle became the subject

`created: 2026-08-18` · status: **adopted** (owner decision 2026-08-18, exp-03 arc
close) · backlog: [issue #17](https://github.com/leandromineti/ai-assisted-coding/issues/17)

## The position

This repo no longer benchmarks workflow frameworks (category 4) on **code outcomes**.
Three preregistered experiments measured framework-shaped interventions against plain
baselines on hidden, fails-closed instruments, and the pattern is now consistent enough
to act on: category-4 effects on code ride on mechanisms the model+harness bundle absorbs
tier by tier, atop run-to-run noise wider than most of the effects themselves. The
measurable subject is the **bundle** — the model + harness system (category 2 in
[`tool-taxonomy.md`](tool-taxonomy.md)) — plus framework value at the *artifact* level,
where it demonstrably lives. Promoted as
[README conclusion 12](../README.md); this note is the assembled argument and the
program definition.

## The four evidence strands

**1. Bundle noise is wider than most treatment effects.** exp-03's calibration band —
five *identical* plain Haiku runs, same prompt, same corpus, same container — scored
**7–14/23** ([exp-03 log](../experiments/03-minimal-harness/log.md) § band v2). A
seven-check spread from sampling variance alone. exp-02 put the complementary point on
the record: spec-kit vs plain was **19/21 = 19/21, identical failures** — a zero
effect against baseline variance at 7.8× cost
([exp-02](../experiments/02-spec-kit-vs-plain/README.md) § Results). Detecting
sub-band effects honestly would need n far beyond what these run costs justify
(methodology 5f's distributions priced this: ~$0.30–2.46 per run depending on tier).

**2. The bundle absorbs the mechanisms frameworks sell — measured twice in one
experiment.** Conclusion 8 documented the structural version (harnesses natively
growing verification gates, memory, plan modes). exp-03 measured the dynamic version:
its v1 corpus saturated because **every plain Haiku run grounded spontaneously** —
discovering the corpus-only log format with no instruction (affordance beats
instruction, amendment 1); then at tier 2, **plain Sonnet scored 8.3/9 on buried-trap
discovery, matching Haiku-plus-grounding-instruction (8/9)** — one model tier absorbed
the instruction's entire measured value, on a pre-declared interpretation rule
([exp-03 README](../experiments/03-minimal-harness/README.md) § tier 2). A category-4
margin measured today is a claim about *current-tier* models with a built-in
expiration date.

**3. The published effect sizes live at category 2.** With the model held fixed,
[swe-agent-2024](../references/papers/2024-swe-agent.md) measured the agent-computer interface
alone at **+64% relative** over a bare shell, priced both chokepoints separately
(viewer window shape, history collapse, an edit-gating linter each worth points), and
found a badly shaped search tool scoring **below no tool at all**.
[agent-frameworks-eval](../references/papers/2025-agent-frameworks-eval.md) traced repair gaps to
patch *tooling*, not reasoning, and single-agent beat multi-agent on all its tasks.
Meanwhile our own category-2 baseline (Claude Code) has never been the varied factor in
any experiment here — we have been measuring the small lever while holding the big
one constant, and the big one is uncharacterized.

**4. Where framework effects are real, they are in artifacts, not code.** exp-02's
P1/P2 dissociation: materially better *written requirements* on every rubric item,
identical code (conclusion 11). exp-03's G-only arm echoed it — the one large code
effect came from a mechanism (grounding) the next model tier does unprompted, while
the ceremony-shaped intervention (stacking both process files) actively interfered.
Artifact-level measurement is cheap, large-effect, and free of the bundle-noise
problem, because documents are scored, not trajectories.

## The program

Three measurement tracks and a standing rule (backlog detail in issue #17):

1. **Harness A/B** — same model, same task, different harness. The inversion of every
   experiment so far. The rig supports it: the logpeek task + verifier are built and
   calibrated, and opencode is the rig's recorded fallback harness
   ([rig README](../experiments/rig/README.md) § Harness decision). Open design
   questions: driving a second harness headless under the enforced network condition;
   extracting comparable cost/transcripts; the confound that harnesses embed different
   default prompts (that *is* part of the treatment, and must be declared as such).
2. **Variance atlas** — bundle noise as a first-class measurement: score distributions
   per task, per tier, per harness. Seed capital already paid for: tarpeek Sonnet n=5,
   tarpeek Haiku n=5 (known-groups), logpeek Haiku n=5, logpeek Sonnet n=3
   (gate-reading, not a calibrated band — the 5f caveat travels with it). Doubles as
   the power analysis every future comparison needs.
3. ~~**Throughput arm** — [issue #15](https://github.com/leandromineti/ai-assisted-coding/issues/15),
   unblocked by the arc close: local open-weight models on owned hardware, on the
   hypothesis that tokens/second, not benchmark score, gates local agent use.~~
   **Retired 2026-08-27, killed with
   [ADR-0048](../adrs/0048-category-1-assesses-api-versions-only.md)** (category 1
   assesses first-party API versions only; self-hosted serving is acknowledged, never
   assessed). The throughput *metric* survives on its API-side value — recorded in
   [`metrics.md`](metrics.md) § Observed session throughput, amended the same day.

**Standing rule:** workflow frameworks are measured at the **artifact level only**
(requirements rubrics, documented-decision counts, attention-split). No more code-
outcome A/Bs at category 4.

## What would reopen category-4 A/Bs

The position is a bet, so its falsifiers are stated: (a) a task class where a
framework's code effect *exceeds* the measured band at the current model tier —
plausibly above the ceremony threshold (exp-01's term) where task size defeats a
single context window, a regime none of our below-threshold tasks touch; (b) a
framework whose enforcement is deterministic rather than prose
([OpenSpec](../tools/4-workflow-frameworks/openspec.md)-style engines), where the
intervention is code the bundle cannot silently absorb; (c) a bundle regression —
if a future harness/model pairing stops grounding unprompted, the tier-condition in
[design-principles F2](design-principles.md) cuts the other way. Any of these
earns a new preregistration; nothing else does.
