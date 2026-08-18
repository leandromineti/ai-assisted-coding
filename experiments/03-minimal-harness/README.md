# Experiment 03 — minimal harness: grounding vs. gates, separated

`preregistration drafted: 2026-08-17` · `revised: 2026-08-18 (draft stage — two-tier
model design, Haiku first)` · status: **DRAFT — not yet binding.** Rule 5 makes
a preregistration binding when it is *committed before any run*; this file has had no
run against it and its fixtures/verifier are not yet built. Owner review, then commit,
then instrument build, then calibration — in that order.

Protocol follows the template line of [`../01-gsd-vs-plain/`](../01-gsd-vs-plain/README.md)
and [`../02-spec-kit-vs-plain/`](../02-spec-kit-vs-plain/README.md); results will be
appended below the untouched protocol.

## Question

Conclusion 6 (n=1, exp-01) credits a workflow framework's quality margin to **empirical
grounding and measured verification gates, jointly**. Exp-02 confirmed the complement
(intent capture without measurement buys steering, not discovery) and its decision rule
green-lit this experiment. Since then, a published n=128 ablation
([`refs/spec-kit-agents.md`](../../refs/spec-kit-agents.md)) separated the two
ingredients and found post-phase **validation worth ~3× pre-phase grounding** on an
LLM-judge composite — a decomposition pointing *away* from conclusion 6's emphasis, with
declared caveats (its own blinded human sample mildly contradicts the headline; different
base model; different artifact). Per `design-principles.md`'s revision rule that fired a
trigger, recorded as [issue #8](https://github.com/leandromineti/ai-assisted-coding/issues/8),
whose decision this experiment executes as **option 3: test it ourselves**.

The reason this is not mere replication (issue #8's own bar): the published ablation
scored with an LLM judge on subjective composites. This rig scores with a **hidden,
fails-closed, machine-checked verifier** over seeded trap families, plus the
attention-split and correction-location instruments. If the decomposition reverses under
binary instruments, that is a finding about the *judge*, not just the mechanisms.

So, two questions, one experiment:

1. **Minimal-harness question** (exp-02's decision rule, confirmed unoccupied by the
   field — [`refs/agent-frameworks-eval.md`](../../refs/agent-frameworks-eval.md) full
   read found no framework-less control in $875 of published runs): does a harness
   reduced to grounding + gates alone — two prompt files, no ceremony — capture the
   layer-4 quality margin at near-plain cost?
2. **Decomposition question** (issue #8): when grounding and gates are ablated
   separately on binary instruments, which carries the margin?

## Preregistered predictions

- **P1 — grounding buys trap discovery.** Arms carrying the grounding instruction
  (G-only, G+V) pass more *sample-discoverable* trap checks (families instantiated in
  the visible `samples/` corpus: encoding, time, ambient-config) than the plain
  calibration band's mean. Mechanism: the traps are discoverable only by measuring the
  provided corpus; exp-01/exp-02 both located discovery in measurement.
- **P2 — gates buy containment, not discovery.** The V-only arm scores *within* the
  plain band on sample-discoverable traps (no discovery mechanism), but its
  corrections concentrate **at the gate** rather than spread through the trajectory
  (correction-location, [`metrics.md`](../../notes/cross-cutting/metrics.md)), and its
  functional-check score is at or above the band mean (a gate catches plain bugs it
  can anticipate without measurement).
- **P3 — the decomposition itself** (no directional bet; either direction revises).
  If V-only ≥ G-only on total score, the published ablation's direction survives our
  instruments and **conclusion 6 is weakened** (grounding over-credited). If G-only >
  V-only, conclusion 6's decomposition survives its first adversarial test and the
  divergence from the published result is attributed — with both readings recorded —
  to judge-vs-verifier instrumentation and/or base model.
- **P4 — cost.** Every minimal arm lands ≤2× its tier's plain-band median cost — an
  order of magnitude under spec-kit's measured 7.8×. If a two-file harness costs like
  a seven-step pipeline, "minimal" failed on its own axis.
- **P5 — tier sensitivity** (two-tier design, protocol item 5): the grounding effect
  (G arms' delta over their own tier's band, discoverable subset) is **larger on
  Haiku 4.5 than on Sonnet 5** — the published ablation's models-improve caveat
  (issue #8, item 2) stated as a falsifiable prediction. Comparable unit:
  within-tier deltas, never raw cross-tier scores.

**What would damage what:**

- G arms fail to beat the band on discoverable traps → F2's mechanism does not survive
  minimal implementation; the margin needs more than an instruction to measure
  (agent-count, fresh contexts, or something unidentified) → conclusion 6 weakened
  from the other side.
- V-only beats G arms outright → conclusion 6 re-decomposed toward validation, in
  agreement with the published ablation; the annotation on conclusion 6 converts from
  "competing decomposition" to "confirmed at home."
- All arms land inside the plain band → either the mechanisms need framework-scale
  implementation, or the instrument lacks headroom — 5d/5f calibration below exists to
  tell those apart *before* the scored arms run.

## The minimal harness (the artifact under test)

Per X1 (the prompt-file-in-a-directory waist), each arm is the task prompt plus zero,
one, or two instruction files, committed verbatim with this protocol and never edited
after. Pinned text:

**`GROUNDING.md`** (arms G, G+V):

> Before writing any implementation code:
> 1. Enumerate every file in `samples/` and examine each with real commands (`file`,
>    `hexdump`, parsing probes in Python) — never assume a format you have not probed.
> 2. Record every probe command and its actual output in `MEASUREMENTS.md`.
> 3. List every behavior decision the tool must make (formats accepted, error handling,
>    edge rendering). Resolve each by citing a measurement from `MEASUREMENTS.md`; if a
>    decision cannot be resolved by measurement, record it as an explicit assumption.
> Do not begin implementation until `MEASUREMENTS.md` exists.

**`GATES.md`** (arms V, G+V):

> Before declaring the task complete:
> 1. Write `check.sh`: it runs your CLI against real input files (including every file
>    in `samples/`) and asserts expected stdout, stderr, and exit codes.
> 2. Prove `check.sh` can fail: introduce a deliberate bug, confirm the script fails,
>    revert the bug. A check that has never failed proves nothing.
> 3. Run `check.sh`; fix and re-run until it passes. Record every run and its result in
>    `GATELOG.md`.
> Do not declare completion until the final `check.sh` run passes.

The split mirrors the published ablation's pre-phase/post-phase boundary: grounding is
everything before code exists; gates are everything after. Instruction lengths are kept
comparable so arm deltas are not a prompt-mass effect.

### Layer-2 inventory rider (conclusion 8, recorded before any run)

The margin attributed to these files must be net of what the layer-2 harness already
does. Claude Code, as configured on this rig (headless, `permissions.allow` list, no
user hooks): permission gating at tool dispatch — yes; turn-end verification gates —
**none configured** (the hook surface exists but is empty here, verified in the rig's
settings before runs and recorded in `log.md`); autonomous memory — off in fresh scratch
contexts. Any gate behavior observed in the plain band is therefore model-initiated, not
harness-enforced, and belongs to the baseline.

## Task (identical prompt for all arms)

> Build `logpeek`, a Python CLI that summarizes structured log files. Given one or more
> file paths, print for each: total lines, a count per log level, the time span covered
> (first to last event), and the five most frequent logger names. Support `--level NAME`
> to filter and `--json` for machine-readable output. A `samples/` directory is provided
> in your working directory; your tool must handle every file in it correctly. Handle a
> file that is not a log file, and an empty file, with clear errors and non-zero exit
> codes. The tool must never modify an input file. Include tests and a README. Name the
> command `logpeek` and install it so it runs from any directory (e.g. `pip install`
> the project or place an executable script on PATH).

Same size class as `gitwho` and `tarpeek` (~100–200 lines plus tests), same shape (CLI
over a measurable domain), **different domain** — tarpeek is consumed (rig reuse rules:
its trap families are heavily discussed in this repo), and logs are a domain neither
prior experiment taught the orchestrator an inventory for.

### The withholding design (what changed since exp-02, and why)

Exp-02's instrument saturated: the plain arm cleared all five hidden trap classes
unaided, leaving no headroom (5d's scar). The clarification-benchmark cluster
([`benchmark-survey §5`](../../notes/cross-cutting/benchmark-survey.md)) shows
**withholding specification information produces headroom reliably at every scale
measured** (~80pp function-level, 28pp repo-level). So this task moves the sharp edges
out of the prompt and into a **visible sample corpus**: the prompt deliberately does not
state the log line format(s), timestamp format(s), encoding, or malformed-line policy.
All of it is *discoverable* — the samples contain the answers — but only by measuring
them. That is the headroom aimed exactly at the mechanism under test: a grounding arm
earns its margin by doing the measurement; a non-grounding arm must guess.

`samples/` (built by `fixtures/build_fixtures.py`, deterministic, committed before runs)
contains genuine trap-family instances **visible to every arm**: a file mixing two line
formats, timestamps in ISO-8601-with-offset and epoch-seconds forms including epoch 0
and a far-future value, one file with non-UTF-8 bytes in a message, malformed lines
interleaved, and an empty file.

## Seeded traps (hidden verifier, fresh in-family instances)

Same five families as exp-01/exp-02 (declared contamination, below). The verifier's
fixtures are **fresh draws from the same families as the samples** — handling them
requires having *generalized* the class from the corpus (or guessed right), not
memorized files. Ground truth in `expected.json` is measured from what the builder
actually built (5a), never hand-derived.

| # | Family | Hidden fixture | Pass condition | Discoverable from samples? |
|---|---|---|---|---|
| T1 | Encoding | Log line with raw non-UTF-8 bytes (different bytes/position than the sample) | Counted and summarized without crashing; any lossless or replacement rendering | **yes** — cousin instance in corpus |
| T2 | Time | Epoch-0 and year-2106 timestamps; mixed UTC offsets in one file | Span computed without crash; offset handling documented | **yes** — cousin instance in corpus |
| T3 | Exit codes | A binary non-log file and an empty file | Both non-zero, **distinct** codes, distinguishable messages | **no** — a decision, not a discovery (exp-02's T3a analog, kept deliberately as the steering-vs-discovery marker) |
| T4 | Ambient config | Same file summarized under `TZ=UTC` vs `TZ=America/Sao_Paulo` | Span output invariant, or the dependence documented in README | **partly** — offset variety in corpus hints at it |
| T5 | Safety | Input file mtimes/contents hashed before and after; one input in a read-only directory | No input modified; read-only input handled without crash | **no** — stated in prompt ("never modify"), tests compliance |

Scoring separates **discoverable** (T1, T2, T4-partial) from **decided** (T3, T5)
checks; P1/P2 are stated over the discoverable subset, total score over all.

## Protocol

Order and rules, each clause carrying its methodology anchor:

1. **Instrument build first.** `fixtures/build_fixtures.py` (samples + hidden
   fixtures + `expected.json`), verifier script, rig container pinned as in
   [`../rig/`](../rig/README.md). Verifier proven **fails-closed** in-container: errors
   against an empty container, fails against a deliberately broken stub (5a, rig rule).
2. **Driver smoke-tested end-to-end** on a trivial prompt before being called runnable;
   success read from artifacts and transcript, never exit status (5e).
3. **Calibration before comparison, per tier** (5d, 5f): **five plain baseline runs
   on the tier's model** — fresh context each, task prompt only — scored to establish
   that tier's noise band. Gate to proceed: band mean leaves ≥3 discoverable-subset
   checks of headroom and the band is not degenerate (nonzero variance). A saturating
   baseline stops that tier for instrument redesign *before* any scored arm spends.
4. **Scored arms, n=1 each** (probe framing; the n=5 band is the reference frame, as
   exp-02): **G-only**, **V-only**, **G+V**. Fresh context per arm, fresh scratch
   directory, arm order randomized by a die roll recorded in `log.md` before launch.
   Pre-registered extension: if any arm lands within 1 check of a band boundary its
   verdict depends on, that arm re-runs twice more (n=3) before any verdict is written.
5. **Model — two-tier design, cheap tier first.** A tier is self-contained: its
   calibration band and its arms share one model (a band is a reference frame only for
   arms on the same model, 5f).
   - **Tier 1 — Haiku 4.5** (band n=5 + three arms): maximal headroom (exp-02's
     known-groups check measured Haiku at 17/21 where Sonnet sat 18–20 — scaffolding
     has the most room to show an effect where the model is weakest), ~3× cheaper, and
     it doubles as end-to-end instrument shakeout. Haiku-specific risk, declared:
     exp-02 saw one Haiku completion failure (undeclared runtime dependency) — an arm
     that fails to complete re-runs once, and the failure is recorded, not discarded.
   - **Tier 2 — Sonnet 5** (band n=5 + arms), **conditional**: runs only if tier 1
     shows a non-null effect for any arm, or if tier 1 is null but instrument headroom
     was confirmed (a discriminating instrument + null effect is exactly the case
     worth confirming at the tier conclusion 6 lives at). A tier-1 null on a
     *saturated* instrument stops for redesign instead.
   - **Scope rule:** verdicts on conclusion 6 / F2 draw **only from the Sonnet tier**
     (the conclusion was derived from Opus/Sonnet-class runs). The Haiku tier bears on
     a distinct, preregistered question — **P5, tier sensitivity**: the published
     ablation's caveat that grounding interventions shrink as the base model improves
     ([issue #8](https://github.com/leandromineti/ai-assisted-coding/issues/8), item 2)
     predicts a *larger* grounding effect on Haiku than on Sonnet. Two tiers make that
     a measurement instead of an argument. Cross-tier score comparisons carry the
     known-groups caveat that trap items are not monotone in capability (Haiku beat
     Sonnet on one exp-02 item) — effect *deltas within tier* are the comparable unit,
     never raw cross-tier scores.
   Standing machine rule holds throughout: arms never run on the session model.
   Per-model usage attribution from transcripts (5c).
6. **Network condition: package-hosts-only** — model API + PyPI, enforced by
   [`../rig/allowlist_proxy.py`](../rig/allowlist_proxy.py) at egress, probed from
   inside the container before each run, probe recorded in `log.md`, identical across
   arms (8a). Under this condition grounding *cannot* be satisfied by web lookup — the
   only measurable domain is the corpus, which is the point.
7. **Oracle policy (affordance-constrained, per the benchmark-survey apparatus rule):**
   if any arm asks a clarifying question, the orchestrator answers with the
   preregistered fixed response — *"Proceed using your best judgment; the samples
   directory is authoritative."* — verbatim, logged, never varying, never leaking trap
   or fixture information. The oracle can confirm the corpus's authority (an
   affordance) but holds no answer key (τ²/ClarifyCodeBench's sees-the-answer scar).
8. Neither arms nor baselines can read this repository. Artifacts copied out of
   ephemeral space before session end; `log.md` appended during runs, never
   reconstructed. Absolute paths throughout; staged set audited before any host-repo
   commit (5b).

## Measurements (decided now)

| Metric | How measured |
|---|---|
| Trap score | per-check pass/fail against `expected.json`, machine-checked; discoverable and decided subsets reported separately |
| Functional checks | normal file, multi-file, `--level`, `--json`, non-log, empty — same script, all arms |
| **Cost ledger** | transcripts' `usage` fields per 5c, per model, orchestrator/subagent split; P4 judged on this |
| **Correction location** | for V arms: corrections (post-first-implementation edits) classified gate-triggered vs. spontaneous, from transcript + `GATELOG.md`; the correction-rate caveat applies — zero ≠ good, pair with effectiveness ([`metrics.md`](../../notes/cross-cutting/metrics.md)) |
| Grounding fidelity | for G arms: does `MEASUREMENTS.md` contain real command outputs (cross-checked against transcript) or confabulated ones — a prose gate that lies is exp-02's steering failure in new clothes |
| Attention split | blocking events, question, verbatim answer, seconds blocked (fixed-oracle design should drive this to ~0; measured anyway) |
| Wall-clock per arm | session timestamps |
| Instruction compliance | did each arm actually produce/obey its instructed artifacts (`MEASUREMENTS.md`, `check.sh` fail-proof, `GATELOG.md`) — an arm that skips its harness is reported as such, not silently scored |

## Contamination declaration (known before the first run)

1. The orchestrator has run exp-01 and exp-02 and knows the five trap families cold;
   traps are drawn from those declared families on purpose (cross-experiment
   comparability) and the *domain* is fresh. Mitigation: hidden fixtures are fresh
   in-family draws; the orchestrator writes no `solution.sh` before arms run (rig
   rule).
2. The orchestrator read the published ablation whose result this experiment tests
   (spec-kit-agents, full PDF). The predictions section deliberately takes **no
   directional bet on P3** so neither outcome flatters the protocol's author.
3. Scoring is non-blind and by the same agent that ran the arms (as exp-01/exp-02);
   the machine-checked core shrinks the judgment surface; grounding-fidelity is the
   subjective remainder and is scored from written artifacts before reading any arm's
   code.
4. Run-order contamination is one-way as always; mitigated by fresh contexts per arm
   and randomized arm order (die roll logged).

## Cost estimate and sign-off gate

Estimated from exp-02's measured figures (Sonnet plain ≈ $0.57/run; Haiku ≈ ⅓ of that
at $1/$5 vs $3/$15 per MTok; minimal arms bounded by P4's 2× budget), per issue #5's
rule the numbers below are planning bounds, not projections — the tier-1 band is
itself the pilot that prices tier 2:

- **Tier 1 (Haiku):** band 5 × ~$0.2 + arms 3 × ≤$0.4 + extension contingency ≈
  **ceiling $4**.
- **Tier 2 (Sonnet, conditional):** band 5 × ~$0.6 + arms 3 × ≤$1.2 + contingency ≈
  **ceiling $9**, re-estimated from tier-1 actuals before launch.

Per standing convention, each tier's scored runs launch only after the owner's spend
approval is quoted verbatim in `log.md` (one approval per tier — tier 2 is a separate
decision made on tier-1 results); instrument build and fails-closed proofs may proceed
without approval (no arm spend).

## What this feeds

Results append below this line after runs. The verdict updates: conclusion 6's
annotation (issue #8 — weaken, re-decompose, or corroborate, dated), F2 in
[`design-principles.md`](../../design-principles.md) (revision rule: this experiment
must confront it), the where-verification-lives open decision (design-principles'
disputed table), and the rig task inventory. n=1 per arm is a probe and will be
labelled as such.
