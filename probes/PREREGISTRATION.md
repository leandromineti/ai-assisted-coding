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

**2026-09-01, plan 11-04 Task 1 — Stage 1 fired (`python3 probes/harness/runner.py
--set probes/sets/generated/contract-sweep.yaml --stage 1`).** 6 cells declared, 5
fired live, 1 (`gemini-3-1-pro`/`gemini-temperature-range`/`2.0`) skipped as
already-logged — it is the plan 11-01 tracer cell, sharing this same probe_id, and
Stage 1's own selector deliberately owns that exact value per `sweep-stages.yaml`'s
first-match-wins design. All 6 cells now have a `terminal: verdict` record on disk;
none ended without a verdict. Outcomes: 5 of 6 REJECTED (HTTP 400) as
SWEEP-DESIGN.md predicted, and the pre-existing 6th (Gemini temperature 2.0) stayed
ACCEPTED (HTTP 200, recorded 11-01) — the prediction that cell already refuted.
Every rejection's error body names its own tested parameter, not a confound: Kimi's
`invalid temperature: only 1 is allowed for this model` (the `kimi-fixed-sampling-point`
cell, value `0.3`) and all four Claude models' `thinking.enabled.budget_tokens: Input
should be greater than or equal to 1024` (the `anthropic-thinking-budget-floor` cells,
value `{"budget_tokens":500,"type":"enabled"}`) — this is the D-07 rejection-strictness
signal Task 2's classifier reads. Actual spend for the 5 newly-fired cells: **$0.00**
(all rejected, billed nothing — read via `python3 probes/harness/ledger.py`: global
total unchanged at `$0.000614`, carrying forward Phase 9's smoke spend plus the 11-01
tracer cell). No ceiling verdict fired. Stage 1's rule-5d discrimination check: 5/5
newly-fired predicted-rejection cells landed as HTTP 4xx with the parameter named in
the error body — the classifier's exact verdict (rejected vs. needs-review) is
determined in Task 2 against this same evidence.

**2026-09-01, plan 11-04 Task 1 — Stage 2 fired (`python3 probes/harness/runner.py
--set probes/sets/generated/contract-sweep.yaml --stage 2`).** 14 cells declared (the
four thinking-toggle rows: `openai-reasoning-effort` × 7 models,
`anthropic-thinking-object` × 4 models, `gemini-thinking-config` × 1 model,
`qwen-enable-thinking` × 2 models), all 14 fired live, all 14 landed
`terminal: verdict` — none ended without a verdict, so D-10's refire branch was not
needed. Outcomes by HTTP status: 10 ACCEPTED (200) — `gemini-thinking-config`
(gemini-3-1-pro), `openai-reasoning-effort` at grok-4-5/kimi-k3/deepseek-v4/glm-5.3/
qwen3.8-max/qwen3.8-flash, `qwen-enable-thinking` at qwen3.8-max/qwen3.8-flash. 4
REJECTED (400) — `openai-reasoning-effort` at gpt-5-6-sol, and all four
`anthropic-thinking-object` cells (claude-fable-5/opus-5/sonnet-5/haiku-4-5).

**Two real, dated findings from this stage's rejections, neither a harness bug —
recorded per rule 1b/5e (settled on the wire, not assumed), surfaced at the D-09
checkpoint for the owner, not silently patched:**

1. **`anthropic-thinking-object`'s probe value is stale for 3 of 4 Claude models.**
   claude-fable-5/opus-5/sonnet-5 each returned: `"thinking.type.enabled" is not
   supported for this model. Use "thinking.type.adaptive" and "output_config.effort"
   to control thinking behavior.` — these three models have moved to a DIFFERENT
   thinking-toggle shape (`type: adaptive` + a separate `output_config.effort` field)
   than the row's probed `{"type":"enabled","budget_tokens":N}` shape. The 4th model,
   claude-haiku-4-5, returned a DIFFERENT 400 instead: `` `max_tokens` must be greater
   than `thinking.budget_tokens` `` — the same max_tokens-too-small confound
   `anthropic-thinking-budget-floor` had (11-02's fix), but on THIS row, which never
   received a `max_tokens_override` in 11-02 (only the budget-floor row did). Both
   error bodies name their own tested field (`thinking.type.enabled` /
   `thinking.budget_tokens`), so D-07's classifier will read these as legitimate
   parameter-named rejections, not needs-review — but the underlying signal is exactly
   what SWEEP-DESIGN's D-08 stage-2 gate exists to catch: **the anthropic-thinking
   toggle is broken (in two different ways) for all 4 Claude models**, before any
   sampling-family thinking-on cell fires downstream. No fix applied in this task —
   this is presented at the D-09 checkpoint below (§ "whether all four thinking-toggle
   shapes worked").
2. **`gpt-5-6-sol` rejects `max_tokens` outright, unrelated to `openai-reasoning-effort`.**
   Its 400 body: `Unsupported parameter: 'max_tokens' is not supported with this
   model. Use 'max_completion_tokens' instead.` (`param: "max_tokens"` in the error
   JSON) — the harness's `openai_compat` adapter sends `max_tokens` universally; this
   model requires the newer `max_completion_tokens` field. The error names `max_tokens`,
   NOT `reasoning_effort` — this is the exact D-07 boundary case (a non-429 4xx whose
   body names a DIFFERENT field than the one under test), so Task 2's classifier must
   route it to `needs-review`, never `rejected`. Left unfixed, every gpt-5-6-sol cell
   in the eventual bulk sweep (44 scalar + 1 content-block, OpenAI's full envelope)
   would 400 this same way regardless of what parameter each cell tests — a
   systemic per-model harness/model-registry gap, not a per-cell finding. No fix
   applied in this task (a per-model request-field override is a harness/registry
   design decision, out of this task's scope) — surfaced at the D-09 checkpoint.

**A genuine evidence-privacy finding, found and fixed within this task, before
classification.** `probes/audit-evidence.py --check` against the enlarged evidence
base initially reported 18 findings (exit 1): 7 were the already-known,
already-tracked pre-existing debt from plans 11-01/11-03 (`.planning/WINDOWS.md` #2:
Kimi's Phase-9 Msh-* header leak; #3: Gemini's documented `thoughtSignature` field,
a false positive on the scanner's generic key-fragment pattern) — untouched, per
that same precedent (append-only evidence, no second exemption, no pattern
narrowing). The remaining 11 were a genuinely NEW leak class this task's own firing
introduced: `set-cookie` response headers (Cloudflare's `__cf_bm` bot-management
cookie at openai/kimi, Alibaba Cloud WAF's `acw_tc` anti-crawler cookie at
qwen/zai) were never in `runner.py`'s `_ORG_IDENTIFYING_RESPONSE_HEADERS` denylist.
Fixed structurally (both casings, `set-cookie`/`Set-Cookie`, added and selftested —
`runner.py --selftest`: 42 cases, 0 problems) and the 5 already-captured records
that carried it were redacted in place (the leaked cookie value removed from
`response_headers`; `probe_id`/`terminal`/`usage`/`cost_usd` untouched — no
re-firing, no re-spending on cells that already returned a valid verdict).
Re-running `probes/audit-evidence.py --check` after the fix: 8 findings (the 7
pre-existing plus one more instance of the same known `thoughtSignature` class,
from this stage's own `gemini-thinking-config` cell) — the intended property (no
NEW leak class in newly captured evidence) holds; the two pre-existing debt items
remain exactly where 11-03 left them, for plan 11-06's evidence-commit decision.
Recorded in `.planning/WINDOWS.md` (#4, marked fixed).

Actual spend for Stage 2's 14 cells, read from `python3 probes/harness/ledger.py`
(never estimated): global total **$0.002347** (up from $0.000614 after Stage 1,
which billed $0), carrying forward Phase 9's smoke spend and the 11-01 tracer cell.
By vendor: anthropic $0.000035 (unchanged, all 4 Stage 2 cells rejected), kimi
$0.001041, gemini $0.00009, xai $0.00089, dseek $0.0000238, zai $0.0000412, qwen
$0.000226. No ceiling verdict fired; every vendor's running total stayed far under
the $0.50 sub-ceiling (highest, kimi, at ~0.2% of it).

**2026-09-01, plan 11-04 Task 3 — the D-09 checkpoint, resolved.** The checkpoint
presented three options (`approve-revised` / `approve-with-anthropic-cap` / `hold`)
plus a surfaced fourth path — fixing the two instrument confounds Task 1's Stage 2
found (§ "Two real, dated findings," above) before stage 3 fires — and recommended:
approve-revised, and ask for both registry fixes before stage 3 fires (fire stages
3–6 under the revised $0.52 envelope, default ceilings in force — $10 hard / $8
warn / $0.50 per-vendor soft — no extra anthropic sub-cap, after fixing (a) the
stale Anthropic thinking-toggle shape (+ Haiku max_tokens override) and (b) the
gpt-5-6-sol max_tokens→max_completion_tokens override).

The owner's reply, verbatim, quoted per the repo's sign-off convention:

> Fix-before-fire

Read in context (the reply to the recommendation above) as: approve-revised at the
$0.52 envelope, WITH the fix-first rider — the two instrument fixes land before any
further firing, and stages 3–6 do not fire in this plan. **No cell of stages 3–6 is
fired by this task or the rest of plan 11-04** — the bulk fire is plan 11-05's job,
gated on this fix having landed and verified clean, matching D-09's own "one
calibration pause, then autonomous" design (the pause is now extended by exactly the
two fixes below, not by a second human checkpoint).

**Fix (a) — the Anthropic thinking-toggle shape, split per model.** Stage 2's own
calibration record (§ "Two real, dated findings," above) showed
`axes.thinking.shapes.anthropic_messages`'s `"on"` fragment
(`{thinking:{type:"enabled",budget_tokens:1024}}`) is stale for 3 of Anthropic's 4
models: claude-fable-5/claude-opus-5/claude-sonnet-5 each 400'd with `"thinking.type.enabled"
is not supported for this model. Use "thinking.type.adaptive" and "output_config.effort"
to control thinking behavior.` — confirmed against each model's own report
(`tools/1-models/claude-{fable-5,opus-5,sonnet-5}.md` § Reasoning surface,
`output_config.effort`, a level enum defaulting `high`, retrieved 2026-08-26).
claude-haiku-4-5 ("opt-in", legacy extended thinking, "the only current model
without adaptive thinking" per `tools/1-models/claude-haiku-4-5.md`) is unaffected —
it keeps the old shape, but its own calibration record showed the SAME budget-floor
confound plan 11-02 already fixed for `anthropic-thinking-budget-floor`
(`` `max_tokens` must be greater than `thinking.budget_tokens` ``), unresolved for
THIS row/shape.

Registry change, `probes/inventory.yaml`:
- `axes.thinking.shapes.anthropic_messages.vendor_overrides` gained three entries,
  keyed by MODEL SLUG (`claude-fable-5`, `claude-opus-5`, `claude-sonnet-5`) rather
  than `model["vendor"]` — every pre-existing `vendor_overrides` entry in this file
  is vendor-keyed because those are genuinely single-model vendors within this
  milestone's 12 tracked models; Anthropic's 4 models sharing one `vendor: anthropic`
  key is the first case where a single vendor's own models diverge from each other.
  Rather than invent a second, parallel per-model override dict,
  `probes/inventory-to-sets.py`'s `resolve_vendor_override()` (new) widens ONLY the
  lookup — model slug first, vendor second — a minimal, documented extension
  (deviation, Rule 3), not a new mechanism. Only the `"on"` key is overridden; no
  calibration evidence says the `"off"` shape (`{type:"disabled"}`) is broken for
  opus-5/sonnet-5 (their own reports confirm `disabled` IS accepted), and fable-5
  never fires a thinking-off cell at all (`reasoning_toggle: always-on`).
- The `anthropic-thinking-object` row itself (the row this stage's own probe fired)
  gained `max_tokens_override: 1025` (row-level, the same mechanism plan 11-02 used
  for `anthropic-thinking-budget-floor`, extended here to a second row) and a new
  `probe_value_overrides` field (new, deviation, Rule 3): keyed by model slug,
  `{value, extra_fields}` — `value` replaces the row's shared `probe_values` entry
  for that model, `extra_fields` (`output_config: {effort: high}`) is merged into
  `extra_params` at the top level, beside `thinking` rather than inside it.
  `probes/inventory-to-sets.py` gained `resolve_probe_value_override()` (new),
  consulted in `expand_params()`'s scalar loop before both the rendered `value:`
  field and `extra_params` are built, so both reflect the same resolved value.
  claude-haiku-4-5 is deliberately absent from `probe_value_overrides` — its shared
  `probe_values` entry (the legacy enabled/budget_tokens shape) is correct as-is; only
  its `max_tokens` needed raising, which the row-level override (applying to all 4
  models uniformly, harmless for the other 3) already covers.

`scripts/build-probe-matrix.py` needed a companion fix, discovered only once the
registry change was regenerated and reclassified: every row before this one shared
one value (or a boundary-contract row's small shared value set, D-03) identically
across every firing model, so a (mode, value) row-key was safe to treat as global.
`anthropic-thinking-object` is the first row where firing models genuinely diverge —
3 of 4 fire one value, the 4th fires a different one, at the same mode. `resolve_cell()`
failed loud (structural-defect diagnostic, by design) the first time this was
regenerated. Fixed (deviation, Rule 1 — a real bug the registry change exposed, not
introduced): `row_keys_for_param()` now detects a "per-model-divergent" mode (any
value's firing-model-set is a proper subset of the mode's full firing-model-set,
rather than every value applying to every model) and collapses it to a `(mode, None)`
sentinel row; `resolve_cell()` gained a fourth fallback tier (`model_mode_index`) that
resolves each model's OWN cell directly when the sentinel is in play. Every
pre-existing row's rendering is provably unchanged (the sentinel path is only reached
when the new detection condition is true, which was never true before this row
existed) — `--check`/`--selftest` both confirm 0 problems, and the two new selftest
cases (`row_keys_for_param`/`resolve_cell` on a synthetic two-model-two-value fixture)
exercise the new tier directly.

**Fix (b) — gpt-5-6-sol's `max_tokens` field rename.** Stage 2's own record: this
model rejects `max_tokens` outright — `Unsupported parameter: 'max_tokens' is not
supported with this model. Use 'max_completion_tokens' instead.` (`param:
"max_tokens"` in the error JSON). `probes/harness/models.yaml`'s `gpt-5-6-sol` row
gained `max_tokens_field: max_completion_tokens` (new field, deviation, Rule 3).
`probes/harness/runner.py` gained `apply_max_tokens_field_override()` (new),
called right after `adapter.build_request()`/`build_content_request()` return, in
BOTH the scalar and content-block branches of `build_entry_request()` — deliberately
OUTSIDE `probes/harness/adapters/openai_compat.py`, whose own docstring states "No
conditional in this file branches on a vendor or maker name"; a per-model
field-rename is exactly that kind of conditional, so it lives in the one place that
already varies per (entry, row) pair instead. Absent (every model but gpt-5-6-sol):
a no-op, verified by two new `runner.py --selftest` cases.

**Verification, all read from the actual runs, none assumed:**
- `python3 probes/inventory-to-sets.py` (regeneration): 329 scalar + 16
  content-block = 345 declared cells, 284 skipped — byte-identical counts to before
  either fix (neither fix changes which/how many cells fire, only what request body
  4 of them carry).
- `python3 probes/inventory-to-sets.py --check`: 0 problem(s).
  `--selftest`: 23 cases run, 0 problem(s) — UNCHANGED count (verified against the
  pre-task committed file, `git show HEAD:probes/inventory-to-sets.py`, run
  standalone: also 23, 0 problems). The two new functions —
  `resolve_vendor_override()`/`resolve_probe_value_override()` — are already
  exercised end-to-end by the pre-existing fixture battery's own
  drift/vendor-override/name-resolution cases (they run inside `expand_params()`,
  which every one of those cases already calls); no new dedicated fixture was
  needed to reach them.
- `python3 probes/harness/runner.py --selftest`: 44 cases run, 0 problem(s) (was 42;
  +2 for `apply_max_tokens_field_override()`).
- `python3 probes/harness/runner.py --check-stages`: 345 cells across 6 stages
  (396 checks run), 0 problem(s) — unchanged.
- `python3 probes/harness/ledger.py --selftest`: 12 cases, 0 problem(s).
  `python3 probes/harness/client.py --selftest`: 27 cases, 0 problem(s). Both
  unchanged by this task (neither file was touched).
- `python3 scripts/classify-probes.py` / `--check`: 0 problem(s). Regenerating over
  UNCHANGED evidence with the fixed registry reclassifies exactly the 4 cells the fix
  touches — `anthropic-thinking-object` at all 4 Claude models moves from `rejected`
  (the pre-fix, confounded request) to `unfired` (a NEW probe_id: the corrected
  request has never been fired). The 4 old raw records are NOT deleted (append-only,
  rule 3) — they now show as "ignored raw records (no matching declared cell)" in the
  regeneration summary, a correct, honest description: they are historical evidence
  of the pre-fix confound, not evidence for the (now-different) declared cell. Every
  other classified row is untouched.
- `python3 scripts/build-probe-matrix.py` / `--check`: 0 problem(s) after the
  companion fix above (2 attempts before green — the first surfaced the
  per-model-divergent bug, the second fixed it; both within this task's own fix
  scope, not a new deviation). `--selftest`: 14 cases run, 0 problem(s) (was 13; +1
  for the new per-model-divergent fixture). `comparisons/probes.md`'s
  `anthropic-thinking-object` row now renders one row (not "multi" — the sentinel
  collapses to a single row-key), 4 Anthropic columns showing `—` (unfired) and the
  other 8 vendor columns `·` (skipped, wire-shape-incompatible) — legible at a glance,
  confirmed by direct inspection.
- `python3 probes/audit-evidence.py --check`: exit 1, 8 findings — UNCHANGED from
  Task 1's own post-fix count (§ "A genuine evidence-privacy finding," above): the 7
  pre-existing findings (`.planning/WINDOWS.md` #2/#3) plus the 1 already-tracked
  `thoughtSignature` instance from Stage 2's own `gemini-thinking-config` cell. No new
  finding — expected, since this task fired nothing and touched no evidence-writing
  code path.
- `python3 scripts/check-taxonomy.py --check`: 133 files checked, 0 problem(s).

**No API call was made in this task.** Every fix above is a registry/harness change,
verified against the calibration batch's own already-captured evidence and each
model's own already-read report — zero incremental spend. The global ledger total
remains **$0.002347** (unchanged from the end of Task 1's Stage 2 entry, above).
Stages 3–6 remain unfired; the bulk fire (D-09's approved-with-fixes go) is plan
11-05's task.

**2026-09-02, plan 11-05 Task 1 — Stages 3, 4 and 5 fired (the 309 scalar cells),
under D-09's "Fix-before-fire" go.** Fired in order, as three separate commands, each
read before the next started, spanning 2026-09-01T23:xx into 2026-09-02T00:20 UTC:

```
python3 probes/harness/runner.py --set probes/sets/generated/contract-sweep.yaml --stage 3
python3 probes/harness/runner.py --set probes/sets/generated/contract-sweep.yaml --stage 4
python3 probes/harness/runner.py --set probes/sets/generated/contract-sweep.yaml --stage 5
```

**Stage 3 (sampling, 110 declared cells).** All 110 fired live, all landed
`terminal: verdict` — no stragglers. By HTTP status: 74×200, 36×400. Ledger after
this stage (`python3 probes/harness/ledger.py`): global **$0.013738** (up from
$0.002347 after Stage 2), by vendor: anthropic $0.000155, kimi $0.001041, gemini
$0.000264, xai $0.007414, dseek $0.0000238, zai $0.0004004, qwen $0.0027294, openai
$0.0017100. No ceiling verdict fired; every vendor's total stayed far under the
$0.50 sub-ceiling (highest, xai, at ~1.5% of it).

**Stage 4 (structural-and-service-tier, 99 declared cells).** All 99 fired live,
all landed `terminal: verdict` — no stragglers. By HTTP status: 61×200, 37×400,
1×422 (grok-4-5's `tools` cell — a structural-contract rejection, not a retry
condition; `client.py`'s `retry_decision()` correctly treats a 422 as a non-retryable
terminal verdict like any other non-429/5xx 4xx). Ledger after this stage: global
**$0.029021** (delta **+$0.015283**), by vendor: anthropic $0.005167, kimi $0.004749,
gemini $0.000324, xai $0.011132, dseek $0.000792, zai $0.000815, qwen $0.003761,
openai $0.002280. No ceiling verdict fired; highest vendor (xai) at ~2.2% of its
sub-ceiling.

**Stage 5 (exotics, 100 declared cells — the on-floor `anthropic-thinking-budget-floor`
1024-token cells' actual billing point, per the 11-02 amendment above).** 96 of 100
landed `terminal: verdict`; 4 ended without a verdict (D-10: recorded, run continued,
carried forward to Task 3's refire pass), all 4 real transient failures, not a
harness defect — reproduced twice under manual `--dry-run` inspection of the same
requests, ruling out a malformed body:

- `kimi-k3--openai-metadata--{"probe":"true"}--default--f0fe2f92` — 429, `retry_exhausted` (4 attempts)
- `kimi-k3--openai-service-tier-values--default--default--de496171` — 429, `retry_exhausted` (4 attempts)
- `kimi-k3--openai-verbosity--low--default--dc48b7e4` — 429, `retry_exhausted` (4 attempts)
- `qwen3.8-max--qwen-repetition-penalty--0.5--thinking-on--43fdcef3` — status 0 (synthesized
  connection failure), `retry_exhausted` (4 attempts)

By HTTP status of the 96 verdicts: 84×200, 12×400. Ledger after this stage: global
**$0.050129** (delta **+$0.021108**), by vendor: anthropic $0.005421, kimi $0.009030,
gemini $0.000366, xai $0.021964, dseek $0.002328, zai $0.001279, qwen $0.005940,
openai $0.003800. No `CEILING skip_vendor` line printed at any point across all
three stages; every vendor's running total stayed far under the $0.50 sub-ceiling
(highest, xai, at ~4.4% of it after Stage 5) — Prediction 1 (SWEEP-DESIGN's $0.50
sub-ceiling headroom) holds so far, scored fully once Stage 6 and the refire pass
are in. Kimi ($0.009030) and zai ($0.001279) both stayed proportionate to their
siblings — Prediction 2 (kimi/zai's `max_tokens` cap moots their expensive reasoning
default) also holds so far.

**Running total after Stages 3–5: distinct probe_ids on disk 334 (up from 20 after
Stage 1–2), global ledger $0.050129.** Verified directly:
`python3 -c "import json,glob,pathlib; print(len({json.loads(l)['probe_id'] for p in
glob.glob('probes/raw/*.jsonl') for l in pathlib.Path(p).read_text().splitlines() if
l.strip()}))"` → 334.

**A genuine evidence-privacy finding for `probes/audit-evidence.py --check` — two
new false-positive instances of the same class WINDOWS #3 already tracks, no new
account-identifying leak.** `--check` against the enlarged evidence base reports 25
findings (exit 1): 5 pre-existing (`.planning/WINDOWS.md` #2, Kimi's Msh-* header
leak) + 12 pre-existing/already-tracked (#3, Gemini's `thoughtSignature` field,
now hit by 12 records instead of 1 since Stage 3-5 fired many more Gemini cells) +
5 anthropic + 3 dseek, both NEW. Read directly (not assumed): the 5 anthropic
findings are all Claude's own documented `thinking` content block `signature` field
(a base64 integrity token, present on every `claude-fable-5`/`claude-haiku-4-5`
accepted response with thinking active — the FIRST time either model received a
200 with thinking on, since every prior calibration-batch cell at these two models
either rejected or omitted thinking). The 3 dseek findings are all DeepSeek's
CloudFront-assigned `X-Amz-Cf-Id` response header — a per-request CDN routing id,
not account-identifying, the same non-identifying class as the already-kept
`request-id`/`msh-request-id` headers, just happening to match the generic
long-base64-blob shape `PII_PATTERNS`' `vendor-key-fragment` rule catches. Neither
is a real secret or an account identifier; both are the SAME structural
false-positive class WINDOWS #3 already documents for Gemini's `thoughtSignature` —
not resolved by widening the tiny-PNG exemption or narrowing the pattern (D-05's
never-loosen-the-pattern rule), recorded as two new entries in `.planning/WINDOWS.md`
(#5 anthropic `signature`, #6 dseek `X-Amz-Cf-Id`), both `open`, tracked for plan
11-06's denylist/pattern-completeness review across all 8 vendors. No genuinely new
account-identifying leak was found in Stages 3-5's evidence.

**A genuine classify-probes.py join bug, discovered while verifying this task,
scoped to Task 3 (its own declared file).** `scripts/classify-probes.py`'s
`scalar_probe_id()` recomputes a declared cell's expected probe_id via
`adapter.build_request()` + `apply_omit()` directly — it does NOT call
`apply_max_tokens_field_override()`, the per-model request-field rename plan 11-04's
fix (b) added to `runner.py`'s actual fire path (`build_entry_request()`). Every one
of `gpt-5-6-sol`'s 44 non-content-block sampling/structural cells therefore fires
with `max_completion_tokens` (correct, on the wire) but classifies as `unfired`
(the join computes a different hash, since it still builds the request with
`max_tokens`) — confirmed directly: re-deriving each Stage 3/4/5 declared cell's
probe_id via the SAME path `main()` actually uses (`build_entry_request()`, not
`scalar_probe_id()`'s shortcut) finds ZERO missing records — all 309 cells are
correctly on disk under their real fired probe_id; this is a classification-time
join defect, not a re-fire or re-bill risk (`seen_probe_ids()` reads raw records'
own stored `probe_id` field directly, which IS correct, so a rerun or the refire
pass will not re-bill any `gpt-5-6-sol` cell). Left unfixed in this task — Task 3
owns `scripts/classify-probes.py` and its own read_first names this exact function;
fixing `scalar_probe_id()` to also call `apply_max_tokens_field_override()` (mirroring
`build_entry_request()`) is Task 3's first job before the coverage assertion can
honestly read zero `unfired` rows.
