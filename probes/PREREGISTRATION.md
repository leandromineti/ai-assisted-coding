# probes/PREREGISTRATION.md — the contract sweep's rule-5 protocol

`checked: 2026-09-01`

This is the formal preregistration methodology rule 5 requires — the protocol Phase
11's contract sweep is graded against — written and committed **before any Phase 11
probe fires** (a fact enforced by this plan's own `<verify>`: `git log --oneline -1 --
probes/PREREGISTRATION.md` must resolve before Task 3 fires the tracer cell).

**This is not the sweep's design document.** Firing order, the 345-cell derivation
(329 scalar + 16 content-block), per-vendor dollar envelopes, and the two dated
falsifiable predictions this preregistration scores all live in
[`probes/SWEEP-DESIGN.md`](SWEEP-DESIGN.md), written at Phase 10 close — that
document explicitly defers to this one for the rule-5 protocol itself (its own
§ "What this is" section). Read SWEEP-DESIGN.md first; this document does not
restate its derivations, only links to them.

## Spend sign-off

> Spend signed off, 2026-09-01: the ≤$0.35 envelope for the full 345-cell sweep is
> approved (owner selected "Approve ≤$0.35 envelope" in discuss-phase).

Quoted verbatim per this repo's sign-off convention (owner memory: quote informal
approvals exactly, never launch a scored/spending run without one). D-01,
`.planning/phases/11-contract-sweep/11-CONTEXT.md` § Implementation Decisions.

## Task

Fire the 345 designed probe cells (329 scalar + 16 content-block, per
SWEEP-DESIGN.md's derived count, itself re-derived from
`python3 probes/inventory-to-sets.py`'s own printed summary) across all 12 active
tracked models / 8 vendors, and classify every fired-or-skipped cell into the
four-state contract schema: `rejected` / `accepted-honored` / `accepted-ignored` /
`silently-translated`, plus the `honor_evidence: none` marker for an accepted cell
whose response carries no honor-discriminating signal (D-06). Requirements: SWP-01,
SWP-02, SWP-03, MODAL-01, MTX-01, MTX-02 (`.planning/REQUIREMENTS.md`).

## Measurements

Per fired cell, recorded verbatim in `probes/raw/{vendor}.jsonl` by
`probes/harness/runner.py` and then read (never re-derived) by
`scripts/classify-probes.py`:

- HTTP status and the record's `terminal` (`verdict` / `retry_exhausted` /
  `skipped_ceiling`)
- The four-state contract verdict plus the `honor_evidence` marker
  (`none` / `echoed-field` / `translated-field` / `candidate-count` /
  `logprobs-content` / `json-validity` / `usage-delta` / `n/a`)
- Billed usage (`usage`/`cost_usd`, already computed by the harness at fire time —
  `probes/harness/ledger.py`'s `cost_usd()`)
- For MODAL-01's 12 `image-input` content-block cells specifically: the billed
  **input**-token count, read from the same response's own `usage`/`usageMetadata`
  object each adapter's existing `parse_usage()` already parses — no new field, no
  separate accounting path.

Every cell declared in the registry but never fired (D-11's closed skip vocabulary,
`probes/sets/generated/skipped-cells.yaml`) is measured too: it classifies to state
`skipped`, carrying its declared reason, never a silent absence.

## Falsification criteria

SWEEP-DESIGN.md § "Proposed sub-ceiling adjustments" states two dated (2026-09-01)
falsifiable predictions this run's real spend scores directly:

1. **Prediction 1 (the $0.50 sub-ceiling headroom).** FAILED if any vendor's real
   accepted-probe spend during this sweep exceeds $0.50 — the tightened
   `vendor_soft_usd_default` this plan's Task 1 lands (D-02). SWEEP-DESIGN's own
   derivation gives every vendor at least ~4.5x headroom under this figure (anthropic,
   the highest-envelope vendor, at $0.11); a real breach means the envelope's
   100%-acceptance-at-full-`max_tokens` assumption undercounted something. CONFIRMED
   if every vendor's real spend stays under $0.50.
2. **Prediction 2 (kimi/zai's `max_tokens` cap moots their expensive reasoning
   default).** FAILED if kimi's or zai's real spend is *disproportionately* higher
   than its sibling vendors' (not merely close to the shared $0.50 ceiling like
   everyone else) — evidence that `max_tokens` does not bound total billed output
   tokens for those two vendors the way SWEEP-DESIGN assumes. CONFIRMED if their real
   spend stays in line with their siblings' (SWEEP-DESIGN's envelope: kimi $0.03, zai
   $0.02, both unremarkable against anthropic's $0.11).

Both predictions are scored in the Run log below once real spend is known.

## Known contamination and confounds

- **The `anthropic-thinking-budget-floor` × `max_tokens` confound** (11-RESEARCH.md
  Pitfall 1). The row's below-floor probe value (`budget_tokens: 500`) exceeds the
  registry's shared `defaults.max_tokens` (64); firing it unmodified would confound
  the intended floor-rejection finding with an unrelated max_tokens-too-small
  rejection, and would corrupt Stage 1's own rule-5d discrimination proof (4 of its 6
  zero-cost cells). Must be fixed (a per-row `max_tokens` override) before Stage 1
  fires — tracked as a Phase 11 handoff item, not this plan's own task.
- **DeepSeek's and Kimi's zero sampling-family coverage** (SWEEP-DESIGN.md §
  "Coverage gap"). Both vendors declare their thinking on/off toggle as an explicit
  null (`toggle-not-a-request-parameter` / `toggle-shape-unknown`) with no fallback
  mode-agnostic firing path, so every one of the 10 sampling-group rows contributes
  zero fired cells for `deepseek-v4` and `kimi-k3` — a real, admitted hole in
  SWP-01's "union of every vendor's documented parameters" claim for these two
  vendors specifically, not merely an arithmetic term. Declared, dollar-accounted,
  not fixed this phase (rule 1b: admitted unknown beats an invented fallback
  fragment).

## Preregistered execution path

The exact driver command lines this phase runs, in firing order (SWEEP-DESIGN.md §
"Probe ordering" states the *why*; this section states the *what*, so the run can be
scored against it):

```
# Stage 1-2 — calibration batch (20 cells, zero-cost predicted rejections + the
# 14 thinking-toggle cells), fired before the owner's go (D-09):
python3 probes/harness/runner.py --set probes/sets/generated/contract-sweep.yaml --stage 1
python3 probes/harness/runner.py --set probes/sets/generated/contract-sweep.yaml --stage 2
python3 scripts/classify-probes.py            # classify + present verdicts/spend to owner

# Stage 3-5 — the remaining paid scalar cells, fired only after the owner's go:
python3 probes/harness/runner.py --set probes/sets/generated/contract-sweep.yaml --stage 3
python3 probes/harness/runner.py --set probes/sets/generated/contract-sweep.yaml --stage 4
python3 probes/harness/runner.py --set probes/sets/generated/contract-sweep.yaml --stage 5

# Stage 6 — the 16 content-block cells (MODAL-01), fired last:
python3 probes/harness/runner.py --content-block-set probes/sets/generated/content-blocks.yaml

# End-of-run refire pass (D-10) for any straggler (retry_exhausted / skipped_ceiling
# after a raised ceiling), before classification is treated as final:
python3 probes/harness/runner.py --set probes/sets/generated/contract-sweep.yaml --refire-exhausted

# Classify, audit, commit evidence, render:
python3 scripts/classify-probes.py
python3 probes/audit-evidence.py               # D-05, fail-closed — blocks the next step on a finding
git add probes/raw probes/ledger.jsonl          # D-04, only after the audit passes
python3 scripts/build-probe-matrix.py
```

`--stage` (`probes/sweep-stages.yaml`) and `--content-block-set` are new CLI surface
this phase's own later plans add (11-02, 11-03 respectively) — naming them here,
before they exist, is the point of a preregistration: the protocol commits to a path,
not merely to a result.

**Rule 5e (execution path is smoke-tested, not just named):** this plan's own Task 3
fires exactly one real cell — `gemini-temperature-range` / `gemini-3-1-pro` / value
`2.0` — through the `runner.py → probes/raw → classify-probes.py →
probes/classified → build-probe-matrix.py → comparisons/probes.md` segment of the
path above, end to end, before any bulk firing begins. It does not exercise the
`--stage`/`--content-block-set` flags (those land with the plans that add them) or
the D-05 audit gate — it proves the pipeline's *generator* half (raw evidence →
classified YAML → rendered matrix) actually runs clean on a real record, the same
"prove the instrument discriminates before the bulk run" discipline SWEEP-DESIGN
already applies to firing order.

## Calibration design (rule 5d)

Stages 1–2 (20 cells: 6 zero-cost predicted-rejection cells + the 14 thinking-toggle
cells) fire first and are classified before a single dollar of Stage 3–6 spend, per
D-09. This is the baseline-arm-first discipline rule 5d requires: the pause exists to
prove the classifier actually discriminates (predicted-rejected cells classify
`rejected`, not `needs-review` or something stranger) and that every wire family's
thinking-toggle mechanism itself works, before ~315 paid cells build on that
assumption. Verdicts and actual spend-so-far are presented to the owner at this
pause; stages 3–6 fire only on the owner's explicit go. No other human gate exists
mid-sweep (D-09).

## Stopping rules

> D-10: Failure policy — record + continue, refire pass: a cell whose request ends
> without a verdict (synthesized status 0 connection failure, retries exhausted on
> 429/5xx) is recorded and the run continues; a dedicated refire pass at the end
> retries accumulated stragglers (probe_id resumability already skips completed
> cells). Only ceiling verdicts stop the run.

The ceilings in force after this plan's Task 1 (D-02/D-03): `global_hard_usd: 10.00`
(stops the whole run), `global_warn_usd: 8.00` (warns, continues),
`vendor_soft_usd_default: 0.50` (skips that vendor's remaining probes, continues with
the other seven — and, per D-03's CR-02 fix, correctly skips *every* vendor
simultaneously over its sub-ceiling, not only the first one iterated).

## Sample size

**n=1 per cell.** This is a probe of the contract surface — does a vendor's API
accept, reject, or silently translate a given parameter/value at a single request —
not a behavioral proof of anything repeatable about the model's output. A single
`accepted-unverified` or `accepted-honored` verdict records what happened on ONE
real request; it says nothing about whether firing the same cell again would produce
the same verdict. Repeat-based verification (temperature-0 repeatability, seed
determinism, n>1 candidate counts, and similar cheap behavioral checks) is Phase 12's
job, explicitly out of scope here.

## Run log

Appended **during** the run, never reconstructed afterward — the protocol text above
this section is never edited once committed (methodology rule 5). Each entry is
dated. Empty at creation.

<!-- Entries appended here as the sweep progresses. -->
