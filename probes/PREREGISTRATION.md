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

**2026-09-01, plan 11-01 Task 3 — tracer cell fired.** `probes/sets/tracer-cell.yaml`
(`gemini-temperature-range` / `gemini-3-1-pro` / value `2.0` / mode `default`) fired
against the live wire: `probe_id
gemini-3-1-pro--gemini-temperature-range--2.0--default--0af9d352`, HTTP 200,
`terminal: verdict`. **Result: ACCEPTED, not rejected** — this refutes, for this one
cell, SWEEP-DESIGN.md § Probe ordering stage 1's prediction that Gemini's
temperature-2.0 value would 4xx (the secondary source stating "Gemini accepts 0 to 1"
is wrong, at least as observed live this session; settled on the wire, not by a third
documentation pass, per D-15/conclusion 19). The classifier correctly recorded this as
`accepted-unverified` with `honor_evidence: none` rather than misclassifying it —
`scripts/classify-probes.py`'s own discrimination is what this record demonstrates,
independent of which way the underlying hypothesis landed. Actual spend for this
cell: **$0.00003** (read from `probes/ledger.jsonl`, never assumed). Running global
ledger total after this cell (carrying forward Phase 9's $0.000584 smoke-test spend):
**$0.000614** — far under every ceiling in force (D-02/D-03: $10 hard / $8 warn /
$0.50 per-vendor soft). No ceiling verdict fired.

## Amendment, 2026-09-01, plan 11-02 Task 1 (pre-run — appended below the protocol,
which is not edited above this line)

**Registry change.** `probes/inventory.yaml`'s `anthropic-thinking-budget-floor` row
now carries `max_tokens_override: 1025` — the smallest integer strictly greater than
that row's largest `budget_tokens` probe value (1024), satisfying Anthropic's
documented `budget_tokens < max_tokens` constraint at the lowest billed ceiling. This
closes SWEEP-DESIGN.md's Handoff #5 and 11-RESEARCH.md's Pitfall 1: firing this row's
two probe values (500, 1024) at the registry's shared `defaults.max_tokens` (64) would
have confounded the floor-rejection finding with an unrelated max_tokens-too-small
rejection, and specifically would have corrupted 4 of Stage 1's 6 zero-cost
calibration cells (the below-floor 500-token value fires at all 4 Claude models).
`probes/inventory-to-sets.py`'s scalar branch of `expand_params()` now reads a row's
`max_tokens_override` in place of `max_tokens_for(defaults, model_slug)` when
present; a new registry validator, `check_max_tokens_override()`, enforces the
strictly-greater rule generically for any row that declares the field.

**The re-derived envelope, and the expression each figure came from.** Every scalar
probe assumes 9 input tokens (SWEEP-DESIGN.md's own `chars/4`-rounded-up convention)
and an output token count equal to the cell's own `max_tokens` (the same
100%-acceptance, full-`max_tokens` over-count SWEEP-DESIGN's whole envelope already
assumes) — cost per cell = `(9 * input_usd_per_mtok + max_tokens * output_usd_per_mtok)
/ 1e6`, at `probes/harness/prices.yaml`'s per-model rates, rounded up to the cent once
per vendor (summing every model's raw per-probe cost first), matching SWEEP-DESIGN.md
§ "Dollar envelopes"'s stated rounding direction exactly. Recomputed directly from
`probes/harness/prices.yaml` and the regenerated `probes/sets/generated/*.yaml` (only
this row's 8 cells changed `max_tokens`; every other cell's cost is unchanged from
SWEEP-DESIGN.md's own table, cross-checked cell-for-cell against that table's
per-vendor cell counts).

- The 8 `anthropic-thinking-budget-floor` cells (4 Claude models × 2 probe values)
  move from `max_tokens: 64` to `1025`. Raw cost per cell:
  `(9*input_rate + 1025*output_rate)/1e6`, summed × 2 probe values per model.
  Old 8-cell raw total: `$0.011844` (at `max_tokens: 64`, cross-checked against
  SWEEP-DESIGN.md's implied per-row contribution). New 8-cell raw total:
  `$0.184824`. Delta: `+$0.17298`.
- **Anthropic's vendor envelope** (73 cells total: 65 scalar, including this
  row's own 8, plus 8 content-block, unchanged by this fix): raw cost
  = old anthropic raw (`$0.1026`, SWEEP-DESIGN.md's own table) − old 8-cell raw
  (`$0.011844`) + new 8-cell raw (`$0.184824`) = **`$0.2756`**, rounds up to
  **`$0.28`** (was `$0.11`). No other vendor's cells changed max_tokens (this row
  fires only at Anthropic's 4 models), so every other vendor's rounded envelope
  figure in SWEEP-DESIGN.md's table is unchanged: dseek `$0.01`, gemini `$0.05`,
  kimi `$0.03`, openai `$0.09`, qwen `$0.02`, xai `$0.02`, zai `$0.02`.
- **The sweep total**, following SWEEP-DESIGN.md's own documented convention —
  the "Total" column is the SUM of each vendor's already-rounded figure, not a
  single round of the summed raw total (verified against the old table:
  `0.11+0.01+0.05+0.03+0.09+0.02+0.02+0.02 = 0.35`, matching its stated `$0.35`
  exactly, not `round($0.3114, 2) = $0.31`). Applying the same sum-of-rounded
  method to the new figures: `0.28+0.01+0.05+0.03+0.09+0.02+0.02+0.02 =
  **$0.52**`. Equivalently: old total (`$0.35`) − old anthropic rounded (`$0.11`)
  + new anthropic rounded (`$0.28`) = `$0.52`.

**This exceeds D-01's signed-off `≤$0.35` envelope.** The prior sign-off ("Spend
signed off, 2026-09-01: the ≤$0.35 envelope for the full 345-cell sweep is approved")
was scored against the pre-fix figures; the honest, re-derived total for the same 345
cells is **`$0.52`**, `$0.17` over the approved envelope. This change is not hidden
inside a later spend report — it is written down here, before it is spent.

**Consequence: stage 5 must not fire until the owner has approved the revised `$0.52`
figure at the D-09 checkpoint in plan 11-04.** Stage 5 (`exotics`, per
`probes/sweep-stages.yaml`, plan 11-02 Task 3) is where the on-floor 1024-value
budget-floor cells actually fire and bill at the new 1025-token ceiling; every dollar
of the `+$0.17298` delta above is billed there, not in Stages 1–2.

**Stages 1–2 remain unaffected.** The Stage 1 budget-floor cells are the below-floor
`{"budget_tokens":500,"type":"enabled"}` value — SWEEP-DESIGN.md § Probe ordering
predicts a 4xx rejection for this value regardless of `max_tokens`, and a rejected
request bills nothing (conclusion 19's economics point, restated in SWEEP-DESIGN.md
§ "Dollar envelopes"). Stage 1's own $0 cost is therefore unchanged by this
amendment; only Stage 5's on-floor (1024) value, fired later and only after the
owner's go, carries the new cost.
