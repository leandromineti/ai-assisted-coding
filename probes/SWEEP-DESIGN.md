# probes/SWEEP-DESIGN.md — the contract sweep's design

**Read `probes/inventory.yaml` and `probes/inventory-to-sets.py` first — this document
explains the design those files implement; it does not restate their schema.**

## What this is, and the preregistration boundary

This document is the sweep's DESIGN: firing order, a cell count derived from the
generator's own output, per-vendor dollar envelopes, and dated ceiling-adjustment
predictions. It is written at Phase 10 close, before any probe fires — Phase 10 spends
zero dollars (see `git status --porcelain probes/harness/ceilings.yaml`, verified
empty by this plan's own automated check).

**This is NOT the preregistration.** Methodology rule 5 requires a formal preregistered
protocol before a scored run; that document, plus the owner's explicit spend sign-off,
is authored at Phase 11 start, where the sweep actually fires (D-14 draws this
boundary). A reader who wants "the protocol the sweep is graded against" should look
for `probes/PREREGISTRATION.md` (or equivalent) dated at Phase 11's start, not here.

## Probe ordering

The registry (`probes/inventory.yaml`) declares parameters as data, not as a firing
sequence — `probes/inventory-to-sets.py` emits `contract-sweep.yaml` in a fixed,
deterministic sort order (group order, then row id, then models.yaml row index, then
mode label) so regeneration is byte-stable, not so it matches the order Phase 11 should
actually FIRE probes in. That firing order is this section's job.

1. **Zero-cost rejection probes first.** The boundary-contract rows' below-boundary
   probe values — `anthropic-thinking-budget-floor`'s 500-token (below-floor) entry,
   `kimi-fixed-sampling-point`'s 0.3 (off-schedule) entry, and
   `gemini-temperature-range`'s 2.0 entry (predicted rejected per its own hypothesis
   note) — are each PREDICTED to return a 4xx. A rejected request bills nothing
   (conclusion 19's economics point holds at this scale too), so firing these first is
   free, AND it is the baseline-arm-first discipline methodology rule 5d requires: it
   proves the four-state classifier (rejected / accepted-honored /
   accepted-echoed-not-honored / accepted-silently-translated) actually discriminates
   before a single dollar is spent on an ambiguous cell. This is a firing-ORDER
   decision within a row's own probe_values, not a row-level reordering the generator's
   file layout expresses — Phase 11's runner applies it explicitly.

2. **The four thinking-toggle rows, before any axis-dependent cell (D-08, the
   load-bearing rule).** `openai-reasoning-effort`, `anthropic-thinking-object`,
   `gemini-thinking-config`, `qwen-enable-thinking` (group `reasoning-toggle`, 14
   emitted cells total) fire next, before every `sampling`-group cell. The reason: a
   broken or mis-shaped toggle invalidates every downstream mode cell built on top of
   it — if `thinking:{type:"disabled"}` itself 400s at Anthropic, every
   `thinking-off` cell fired afterward for the sampling family is confounded by that
   same failure, and the spend on those cells is wasted discovering a problem the
   toggle rows would have caught for free. Catching it here means re-spending budget
   never happens; catching it after 160 sampling-family cells have already fired would
   mean re-spending all of them.

3. **The axis-dependent sampling cells** (group `sampling`, 10 rows × the real
   thinking-on/thinking-off cells each of the 12 models actually supports per its
   `reasoning_toggle` — 160 emitted cells, D-07). Fired only after step 2 has confirmed
   the toggle mechanism itself works for every wire family the sampling rows depend on.

4. **The flat structural cells** (group `structural`, 10 rows, no axis expansion — 104
   emitted cells) and the service-tier presence row (group `service-tier`, 1 row, 12
   emitted cells) — a vendor's JSON-schema or streaming support does not change when
   reasoning is toggled, so these carry no ordering dependency on steps 2–3.

5. **The exotics** (group `exotic`, 15 rows, 106 emitted cells — the nine INV-03 named
   rows, `kimi-fixed-sampling-point`'s on-schedule value, OpenAI's long tail, and
   `gemini-temperature-range`'s in-range value). Fired last among the scalar rows
   because their whole point is asymmetry: a rejection or an unexpected acceptance
   here is not corrected by any other cell, so there is no cost to firing them after
   everything that COULD invalidate a downstream reading already has.

6. **The content blocks** (group `content-block`, 2 rows, 16 emitted cells —
   `image-input`, `anthropic-cache-control-block`). Fired last of all, and only once
   `runner.py` gains the content-block request path this document's own Handoffs
   section names as outstanding (MODAL-01) — there is no ordering argument for firing
   them earlier, since nothing downstream depends on their result.

## Expected cell count, with its derivation

Every number below is read from `python3 probes/inventory-to-sets.py`'s own printed
summary, run against the registry as of this plan's last commit:

```
params rows: 51 total (excluded=9, swept=42)
emitted scalar probes (one row x model x mode x value expansion each): 329
emitted content-block probes: 16
skipped cells (param x model pairs never emitted, D-11): 284 (no-request-field-for-vendor=46, no-thinking-off-toggle=45, toggle-not-a-request-parameter=22, toggle-shape-unknown=11, wire-shape-incompatible=160)
```

**Dated 2026-09-01, plan 10-04, closing CR-01:** plan 10-03's version of this section
read 396 (before-fix) for the scalar total and 246 (before-fix) for the skip total.
Plan 10-04's own § CR-01 closure subsection (below) explains why; every count in this
section is re-derived
from the current generator output, not hand-adjusted from the earlier figures.

**The 42 swept rows, by group** (`python3 -c` over `probes/inventory.yaml`'s own
`params:` list, grouping by `(group, status)`): sampling=10, structural=10,
reasoning-toggle=4, service-tier=1, exotic=15, content-block=2 — sums to 42, matching
the printed `swept=42`. Plus 9 `excluded` rows (never emitted, D-09) = 51 total rows.
Unchanged by plan 10-04 — no registry row was added, removed, or reclassified; the
`no-request-field-for-vendor` fix moves cells from "emitted" to "skipped" without
touching a single row's group or status.

**The derivation, by group, cross-checked against the actual generated file
(`python3 -c` over `probes/sets/generated/contract-sweep.yaml`'s `probes:` list,
grouping each entry by its row's `group`):**

- **structural: 88** (was 104). Eight `firing_scope: all` rows × 12 models × 1 mode (no
  axis) = 96, plus the two `anthropic-structured-output-output-*` rows'
  `firing_scope: home-vendor` narrowing each to the 4 Anthropic models × 1 mode = 8.
  96 + 8 = 104 candidate cells — **before** the CR-01 fix. Five of those eight
  `firing_scope: all` rows carry an explicit null `names:` entry at one or both of
  `anthropic_messages`/`gemini` with no vendor override, and now route those (row,
  model) pairs to a `no-request-field-for-vendor` skip instead of emitting a no-op
  cell: `response-format` (−4, the 4 Claude models), `parallel-tool-calls` (−4 Claude,
  −1 gemini-3-1-pro), `stream` (−1 gemini-3-1-pro), `stream-options-include-usage` (−4
  Claude, −1 gemini-3-1-pro), `tool-choice` (−1 gemini-3-1-pro). Total loss: 4+5+1+5+1
  = 16. 104 − 16 = 88.
- **service-tier: 11** (was 12). One `firing_scope: all` row, no axis, × 12 models = 12
  candidate cells; its `names:` map is null at `gemini`, so gemini-3-1-pro's cell is now
  a `no-request-field-for-vendor` skip. 12 − 1 = 11.
- **reasoning-toggle: 14** (unchanged). `openai-reasoning-effort` (wire-family, home
  `openai_compat`, 7 models) + `anthropic-thinking-object` (wire-family, home
  `anthropic_messages`, 4 models) + `gemini-thinking-config` (home-vendor, 1 model) +
  `qwen-enable-thinking` (home-vendor, 2 models) = 7 + 4 + 1 + 2 = 14. None of these
  four rows carries a null `names:` entry at a wire family it fires at, so CR-01 does
  not touch this group.
- **sampling: 110** (was 160). Of the 10 sampling rows, 7 carry a null `names:` entry
  at `anthropic_messages` (`presence-penalty`, `frequency-penalty`, `logprobs`,
  `top-logprobs`, `seed`, `n`) and, for `logit-bias` alone, at `gemini` as well; the
  other 3 (`temperature`, `top-p`, `top-k`) carry a real name at every wire family and
  are untouched by this fix. The pre-CR-01 per-row candidate count (D-06's
  reasoning_toggle mode multiplier: `always-on`/`none` emit 1 cell, `default-on`/
  `opt-in` emit 2, minus DeepSeek's and Kimi's null-toggle removal) was 16 for every
  one of the 10 rows. For the 6 rows null only at `anthropic_messages`, all 4 Claude
  models' cells (claude-fable-5 always-on ×1, claude-opus-5/claude-sonnet-5 default-on
  ×2 each, claude-haiku-4-5 opt-in ×2) — 1+2+2+2 = 7 cells — are now
  `no-request-field-for-vendor` skips: 16 − 7 = 9 cells each, × 6 rows = 54. For
  `logit-bias` (null at both `anthropic_messages` and `gemini`), the same 7 Claude
  cells plus gemini-3-1-pro's 1 always-on cell = 8 cells removed: 16 − 8 = 8. The 3
  untouched rows keep their pre-fix 16 each = 48. Total: 48 + 54 + 8 = 110.
- **exotic: 106** (unchanged). The 15 exotic-group rows' mixed `firing_scope`
  (`wire-family` fires at 4–7 models depending on home family; `home-vendor` fires at
  1–4), summed directly from the generated file rather than re-derived arithmetically
  here, since the group mixes several firing scopes and one boundary-contract row with
  two probe values. None of the 15 rows carries a null `names:` entry at a wire family
  it fires at (D-11's home-vendor/wire-family scoping means these rows never reach a
  wire family their own `names:` map doesn't cover in the first place) — CR-01 does not
  touch this group, the same reason it does not touch reasoning-toggle.
- **Total scalar: 88 + 11 + 14 + 110 + 106 = 329**, matching
  `emitted scalar probes: 329` exactly (was 396; net change −67, matching the 67 no-op
  cells CR-01 closes).
- **content-block: 16** (unchanged). `image-input` (`firing_scope: all`, 12 models) +
  `anthropic-cache-control-block` (`firing_scope: home-vendor`, 4 Anthropic models) =
  12 + 4 = 16, matching `emitted content-block probes: 16` exactly. Content-block rows
  carry no `names:` map (D-12's `body_template` shape instead), so CR-01 cannot reach
  them.

**345 total probe cells** (329 scalar + 16 content-block, was 412) will be fired by the
sweep as currently designed, plus 284 cells that are declared skips and never fired at
all (D-11, was 246) — every param × model pair is therefore either an emitted cell or a
skipped-cells.yaml entry with a reason, never a silent absence.

**The accounting-shape change, and why emitted-plus-skipped is not conserved across
this fix (dated 2026-09-01).** A `no-request-field-for-vendor` skip is recorded ONCE per
(row, model) pair, at mode `n/a` — mirroring the existing `wire-shape-incompatible`
scope-skip, because a name that does not resolve is a property of the pair, not of a
mode. A toggle skip (`no-thinking-off-toggle`/`no-thinking-capability`), by contrast, is
recorded per MODE. For a sampling-group (row, model) pair where the model's
`reasoning_toggle` is `always-on` or `none`, the pre-fix registry ALREADY emitted one
no-op cell (the one real mode) and recorded one toggle skip (the missing mode) for that
same pair — CR-01's fix replaces BOTH of those with a single pair-level
`no-request-field-for-vendor` record. That is why the skip-reason table does not simply
gain 67 new entries: 67 emitted cells and 8 mode-level `no-thinking-off-toggle` skips
(53 → 45, the always-on/none sampling-row pairs affected) collapse into 46 pair-level
`no-request-field-for-vendor` records (46 − 8 replaced-in-place = 38 pairs that had no
prior skip at all, mostly the axis-`none` structural/service-tier rows, where a single
mode was emitted and there was never a second mode to skip). A reader who tries to
reconcile the before-fix 396 + 246 = 642 against the current 329 + 284 = 613 without
this paragraph will conclude one of the two totals is wrong; neither is — they are
counting different things (modes vs pairs) for the 8 pairs where both apply.

## CR-01 closure, dated 2026-09-01 (plan 10-04)

10-REVIEW.md's CR-01 found that `firing_scope: all` fired regardless of whether a row's
`names:` map actually resolved a request-body key at the model's wire family: for 13
canonical rows (`presence-penalty`, `frequency-penalty`, `logprobs`, `top-logprobs`,
`seed`, `n`, `logit-bias`, `response-format`, `tool-choice`, `parallel-tool-calls`,
`stream`, `stream-options-include-usage`, `service-tier`) an explicit null at
`anthropic_messages` and/or `gemini` (D-02's checked-absence marker) meant the emitted
cell's request body never contained the parameter it claimed to test — 67 of the
before-fix 396 emitted scalar cells, billed and indistinguishable on the wire from any
other row's cell at the same model/mode.

**Decision: all 13 rows keep their explicit null and route to a declared skip; no row's
`names:` map was re-authored.** The reviewer offered a second closure — re-author the
null to the family-default canonical name and let the compat-shim swallow the request,
the pattern `top-k` already uses — but the evidence says that applies to none of these
13: (1) every null carries its own dated, sourced `source:`/`retrieved:` pair recording a
genuine checked absence, and re-authoring it to make a generator bug disappear would
falsify a sourced registry fact; (2) `top-k` carries a REAL non-null name at all three
wire families, so there is no "send the family default where the family has no field"
intent to preserve here — none of the 13 express that intent; (3) the compat-shim
swallow test (D-10) lives INSIDE the `openai_compat` family, where these rows' names stay
non-null and keep firing; the nulls sit at `anthropic_messages`/`gemini`, a genuine
wire-shape mismatch that would measure the wire format, not the parameter; (4) no
hypothesis coverage is lost — the three LOW-confidence FEATURES.md claims already live in
their own dedicated home-vendor rows.

**What now prevents recurrence:** two audits plus a validator, in `probes/inventory-to-sets.py`.
The no-op audit (`emitted N no-op M`, run against `probes/sets/generated/contract-sweep.yaml`
cross-referenced with each entry's row `names:`/`name_overrides`) read before-fix `emitted 396 no-op 67`; after, `emitted 329 no-op 0`. The partition audit (every
unresolvable-name (row, model) pair either doesn't emit or carries a closed-vocabulary
skip reason) read 46 violating pairs before and 0 after. `check_emitted_carries_param()`
(new, wired into `--check`) re-resolves every emitted entry's parameter name and fails
the gate if it is ever absent from that entry's `extra_params` — confirmed to discriminate
by locally reverting the fix (not committed) and observing `--check` report the defect
again, naming CR-01, before the revert was discarded.

## Coverage gap: DeepSeek and Kimi get zero cells across the whole sampling family

Named, dated 2026-09-01 (10-REVIEW.md WR-02) — not merely an arithmetic term feeding the
cell count above, a real hole in INV-01's "union of every vendor's documented request
parameters" claim for these two vendors specifically. Both DeepSeek's and Kimi's
`axes.thinking.shapes.openai_compat.vendor_overrides` entries declare BOTH `on` and `off`
as an explicit null (`toggle-not-a-request-parameter` for DeepSeek — thinking mode is
selected by model id, not a request field; `toggle-shape-unknown` for Kimi — no
documented request shape exists at all). Because every sampling-group row carries
`axis: thinking` (D-07) and there is no fallback path that fires a row once in a
mode-agnostic "default" state when a vendor's toggle can't be constructed, EVERY mode
candidate for these two vendors on EVERY one of the 10 sampling rows (`temperature`,
`top-p`, `top-k`, `presence-penalty`, `frequency-penalty`, `logprobs`, `top-logprobs`,
`seed`, `n`, `logit-bias`) is a declared skip — `deepseek-v4` and `kimi-k3` fire zero
sampling-family cells in the entire sweep. This is declared (every skip carries a
closed-vocabulary reason in `skipped-cells.yaml`, never silent, D-11) and
dollar-accounted-for (their envelope figures above already reflect it), but a reader of
this document would otherwise have to notice the gap themselves by cross-referencing the
skip-reason table against `models.yaml`. No fix is proposed in this plan — the same
"admitted unknown beats invented fragment" reasoning (rule 1b) that produced the null
overrides in the first place argues against inventing a fallback fragment just to fill
this hole; a future plan authoring a real DeepSeek/Kimi thinking-toggle shape (if one is
ever documented) is what closes it, not a generator change.

## Dollar envelopes, per vendor

**Stated assumptions (a reader must be able to recompute every figure below from
these, and only these):**

- **Assumed input-token count per probe: 9.** Every scalar probe shares the same
  one-word prompt (`defaults.prompt`, `probes/inventory.yaml`): `"Reply with exactly
  one word: hello."` — 35 characters. A `chars/4` token-count heuristic (a common
  rough English-text approximation, not vendor-tokenizer-exact — the real per-vendor
  tokenizer would give a slightly different figure per maker, which this document does
  not attempt to reproduce) gives 35/4 = 8.75, rounded UP to 9 whole tokens (the
  rounding direction stated below, applied uniformly).
- **Assumed output-token count per probe: `defaults.max_tokens`, per model.** 64 for
  every model except `gemini-3-1-pro`, which carries `defaults.max_tokens_overrides:
  gemini-3-1-pro: 200` (plan 09-03's finding: its always-on reasoning consumed a
  16-token budget entirely before any output text, see `probes/README.md` § Wire
  questions #4). `max_tokens` is a hard generation-length CAP enforced server-side at
  every vendor in this set — the true billed output token count can be LESS than this
  figure (if the model stops early) but never more, so treating it as the assumed
  output count makes every per-vendor figure below an upper bound on the ACCEPTED
  subset, never an underestimate.
- **A rejected request bills nothing.** Every cell this document predicts will be
  rejected (see § Probe ordering step 1) costs $0 in practice; the figures below
  assume EVERY emitted cell is accepted and billed at the full assumed token counts —
  a deliberate over-count, since real acceptance is certainly less than 100% (multiple
  rows exist specifically because a rejection is expected — see the boundary-contract
  and checked-absence rows).
- **Content-block probes are priced using the SAME token-count assumption as scalar
  probes (9 in / model-specific max_tokens out) — the image payload's OWN billed
  input-token cost is NOT modeled here.** Reading that real number is MODAL-01's job
  (Phase 11), not this envelope's; this is a stated gap, not a hidden one. The envelope
  below therefore understates the true cost of the 16 content-block cells by an
  unknown-but-small amount.
- **Rounding direction: round UP, to the cent**, applied once per vendor (summing every
  model's raw per-probe cost first, then rounding the vendor total) — never per-probe,
  which would compound rounding error across the higher-volume vendors.

**Per-vendor envelope, dated 2026-09-01, recomputed after plan 10-04's CR-01 fix**
(from `probes/harness/prices.yaml`'s per-model rates × the assumed 9 input /
model-specific output tokens, summed across every scalar AND content-block cell that
vendor's models fire, per the § Expected cell count derivation). Only `anthropic` and
`gemini` cell counts changed — they are the two wire families the 13 CR-01 rows carry an
explicit null at; the other six vendors are byte-identical to the pre-fix figures:

| Vendor | Emitted cells (scalar + content-block) | Raw cost | Envelope (rounded up) |
|---|---|---|---|
| anthropic | 65 + 8 = 73 (was 126 + 8 = 134) | $0.1026 | **$0.11** (was $0.19) |
| dseek | 22 + 1 = 23 | $0.0061 | **$0.01** |
| gemini | 18 + 1 = 19 (was 24 + 1 = 25) | $0.0459 | **$0.05** (was $0.07) |
| kimi | 24 + 1 = 25 | $0.0247 | **$0.03** |
| openai | 44 + 1 = 45 | $0.0884 | **$0.09** |
| qwen | 90 + 2 = 92 | $0.0199 | **$0.02** |
| xai | 33 + 1 = 34 | $0.0137 | **$0.02** |
| zai | 33 + 1 = 34 | $0.0100 | **$0.02** |
| **Total (sum of rounded)** | **345** (was 412) | **$0.3114** (was $0.4036) | **$0.35** (was $0.45) |

This envelope's total ($0.35, an over-count upper bound per the assumptions above, and
itself an over-count relative to the pre-fix $0.45 figure — see the dated note below) is
under 4% of the milestone's $10 global hard ceiling (HARN-03) and under a quarter of
even the CURRENT $1.50 per-vendor soft default — the contract sweep, as designed, is not
close to threatening either ceiling. That headroom is exactly what the next section
proposes tightening, as a falsifiable prediction rather than an applied change.

**Dated 2026-09-01 (plan 10-04): the pre-fix $0.45 envelope was an over-estimate for a
reason this document did not know at the time.** 67 of the 396 cells the earlier
envelope priced never carried their own parameter (CR-01) — they were still real,
billable HTTP requests (a rejected-vs-accepted verdict on SOME cell would still have
been returned and billed), so the earlier total wasn't wrong about what would be spent,
but it was wrong about what that spend would have PURCHASED: 67 of the priced cells
would have returned a verdict about the WRONG thing (thinking-toggle or JSON-schema
plumbing, not the row's own parameter). The corrected $0.35 is the honest price of the
345 cells that actually test what they claim to.

## Proposed sub-ceiling adjustments (dated prediction, NOT applied)

`probes/harness/ceilings.yaml` is unchanged by this phase — verified by an automated
`git status --porcelain` gate in this plan's own Task 3 verification — and is edited
only at Phase 11 start, under the owner's explicit spend sign-off (D-16). Everything in
this section is a proposal and a dated (2026-09-01) falsifiable prediction, not an
applied number.

**Dated 2026-09-01 (plan 10-04): re-derived from the post-CR-01 envelope, not
re-typed.** The pre-fix version of this section derived its $0.50 proposal from
anthropic's then-highest $0.19 envelope (~2.6x headroom). Anthropic is still the
highest-spending vendor after the fix, but its own figure dropped to $0.11 (removing 61
zero-signal cells) — a strictly LARGER margin under the same proposed $0.50 ceiling than
the earlier derivation assumed, so the proposal itself does not need to change, only its
derivation's numbers do.

**Proposal: lower `vendor_soft_usd_default` from $1.50 to $0.50.** Derivation: the
highest per-vendor envelope above (anthropic, $0.11) leaves roughly 4.5x headroom under
a $0.50 sub-ceiling — enough margin to absorb the assumptions' known slack (higher real
acceptance rate than a naive worst case, the unmodeled content-block image-token cost)
without nuisance-tripping mid-sweep, while catching a genuine per-vendor billing
anomaly (a retry storm, a misconfigured model id burning tokens on every call) roughly
3x earlier than the current $1.50 default would. **Falsifiable prediction:** if any
vendor's real accepted-probe spend during the Phase 11 sweep exceeds $0.50, this
envelope's assumptions undercounted something — either the real accepted fraction is
far higher than the worst-case-100%-accepted assumption already used above (which
would be strange, since that assumption is already a ceiling), the true per-probe
token counts exceed `max_tokens` (a metering surprise this document's assumptions
explicitly rule out as impossible, since `max_tokens` is stated as a hard cap), or an
unanticipated retry storm inflated the attempt count well past 345. Confirmed if real
per-vendor spend across the full Phase 11 sweep stays under $0.50 for all eight
vendors, matching the ~50x-to-4.5x headroom (dseek's $0.01 lowest to anthropic's $0.11
highest) this document derives.

**No per-vendor override table is proposed.** `probes/harness/ceilings.yaml`'s own
comment (2026-09-01) names kimi and zai as "the most plausible candidates to need a
lower (or a deliberately raised) sub-ceiling" because both default `reasoning_effort`
to `max`, the most expensive default reasoning setting among the 8 makers. This
document's derivation predicts that worry is MOOT under this sweep's specific
`max_tokens` design: because `max_tokens` caps TOTAL billed output tokens regardless of
how much of that budget reasoning consumes (the same cap this document already treats
as an upper bound above), kimi's and zai's envelope figures ($0.03 and $0.02) are not
meaningfully higher than any other vendor's, despite the expensive reasoning default. A
second falsifiable prediction, riding on the same Phase 11 evidence as the first: if
kimi's or zai's real spend is disproportionately higher than its sibling vendors'
(rather than merely close to the proposed $0.50 ceiling like everyone else), that would
be evidence the `max_tokens` cap does NOT bound total billed tokens the way assumed for
those two vendors specifically — which would also bear directly on the excluded
`max-tokens-semantics` row's own unresolved hypothesis (FUT-01).

## Handoffs to Phase 11

Dated 2026-09-01. Each names what must happen before or during the sweep — none of
these are silent gaps; each is recorded here specifically so Phase 11 planning starts
from a known list rather than rediscovering them mid-sweep.

1. **`runner.py` needs a content-block request path before
   `probes/sets/generated/content-blocks.yaml` can fire (MODAL-01).** The file is
   deliberately keyed `content_block_probes:` (not `probes:`) so the current runner
   refuses it loudly (exit 2) rather than firing an image/cache-control row through the
   scalar accept/reject template — proven by this plan's own Task 2 verification. The
   16 content-block cells stay unfired until this path exists.
2. **The two open Phase 9 robustness findings from `09-REVIEW`** — note: Phase 9's
   `09-REVIEW` numbers this same finding-id `CR-01`, distinct from THIS plan's CR-01
   (`10-REVIEW.md`'s no-request-field-for-vendor fix) — a connection-level
   `URLError`/timeout uncaught in `client.py` (one flaky network moment crashes a whole
   sweep) and CR-02 (`_find_vendor_breach` reports only the FIRST breaching vendor,
   masking later breaches) — remain unfixed as of this plan. Neither bit Phase 9's
   5-probe smoke; both are far more likely to bite Phase 11's 345-cell, 8-vendor sweep.
   Fix via `/gsd-code-review 9 --fix` or fold into Phase 11 planning before firing
   begins.
3. **The evidence-commit policy for `probes/raw/` and `probes/ledger.jsonl` is
   provisional** (owner checkpoint `gitignore-evidence`, 2026-09-01, "maybe I will
   change it later" — `.planning/STATE.md` § Blockers/Concerns). Its revisit gate is
   Phase 11, before the sweep's 345 real HTTP responses become the evidence base this
   milestone's promotion phase (Phase 13) relies on.
4. **The skip-reason vocabulary this phase's plans introduced** (`SKIP_REASONS` in
   `probes/inventory-to-sets.py`: `no-thinking-off-toggle`, `no-thinking-capability`,
   `wire-shape-incompatible`, `toggle-shape-unknown`, `toggle-not-a-request-parameter`,
   and — added 2026-09-01, plan 10-04, closing CR-01 — `no-request-field-for-vendor`:
   the row's parameter has no request field at this model's wire family, an explicit
   null in `names:` with no vendor override supplying one) is what lets Phase 11
   satisfy "every param × model cell is either an emitted probe or an explicit,
   reasoned skip" — the 284 skipped-cells.yaml entries (was 246 before plan 10-04's
   fix) are already proof this holds at design time; Phase 11 should not need a
   seventh reason unless a genuinely new admitted-unknown shape shows up mid-sweep.
5. **`anthropic-thinking-budget-floor` needs a per-row `max_tokens` raise before
   firing.** Its two probe values (500, 1024 budget_tokens) both exceed the registry's
   shared `defaults.max_tokens` (64) — firing this row with the shared default would
   confound the floor finding with an unrelated `max_tokens`-too-small rejection, since
   Anthropic's own documented constraint requires `budget_tokens < max_tokens`. There
   is no per-row `max_tokens` override field in `probes/inventory-to-sets.py` as of
   this plan (only a per-MODEL `defaults.max_tokens_overrides`) — Phase 11 needs either
   a one-off `max_tokens` override for this specific cell, or a registry field this
   plan did not add.

## Scoring, dated 2026-09-02 (Phase 11 plan 11-06 Task 3)

Appended below the untouched prediction text above, per this document's own
prediction-scoring discipline (§ conventions this repo applies to dated,
falsifiable claims). The prediction text above this heading is byte-identical to
its previous revision — nothing above this line was edited to produce this
scoring. Every measured figure below is read from
`probes/PREREGISTRATION.md`'s Run log (plan 11-05 Task 3's final table, itself
read from `python3 probes/harness/ledger.py`, never estimated), never
re-derived here.

### Prediction 1 — the $0.50 sub-ceiling headroom: **CONFIRMED**

| vendor | predicted envelope | measured spend | measured / predicted |
|---|---|---|---|
| anthropic | $0.28 | $0.009442 | 3.4% |
| dseek | $0.01 | $0.002328 | 23.3% |
| gemini | $0.05 | $0.002586 | 5.2% |
| kimi | $0.03 | $0.011133 | 37.1% |
| openai | $0.09 | $0.004185 | 4.7% |
| qwen | $0.02 | $0.005940 | 29.7% |
| xai | $0.02 | $0.021964 | 109.8% |
| zai | $0.02 | $0.001279 | 6.4% |
| **total** | **$0.52** | **$0.058858** | **11.3%** |

Every vendor's real accepted-probe spend stayed under $0.50, the confirmation
criterion stated above — the highest, xai, reached only ~4.4% of the sub-ceiling.
xai is the one vendor whose measured spend exceeds its own SWEEP-DESIGN-predicted
per-vendor envelope (by ~10%, $0.021964 vs. $0.02), still two orders of magnitude
under the $0.50 sub-ceiling this prediction actually scores against — recorded
honestly rather than rounded away, no envelope-scoring or ceiling concern. Every
other vendor's measured spend landed well under its own predicted envelope (the
3%–37% range above), consistent with this document's own stated
100%-acceptance-at-full-`max_tokens` over-count assumption.

### Prediction 2 — kimi/zai's `max_tokens` cap moots their expensive reasoning default: **CONFIRMED**

Kimi ($0.011133) and zai ($0.001279) both stayed proportionate to (or below) their
sibling vendors' spend rather than disproportionately higher — neither is the
sweep's highest-spending vendor (xai, at $0.021964, is), and neither shows the
signature of a `max_tokens`-cap failure (an outlier far above every other
vendor's figure despite similarly-sized cell counts). The `max_tokens` cap bounds
total billed output tokens for these two vendors the way this document assumed;
no evidence surfaced bearing on the excluded `max-tokens-semantics` row's own
unresolved hypothesis (FUT-01).

### The re-derived envelope question (plan 11-02's amendment, above this section but appended later): **resolved as expected**

Plan 11-02's amendment (Run log entry, 2026-09-01, appended to
`probes/PREREGISTRATION.md`) re-derived this document's own sweep total from
$0.35 to **$0.52** after `anthropic-thinking-budget-floor`'s `max_tokens_override`
fix raised that row's billed ceiling — exceeding D-01's original ≤$0.35 sign-off,
and it stated a consequence: stage 5 must not fire until the owner approved the
revised $0.52 figure at the D-09 checkpoint in plan 11-04. That is exactly what
happened — the owner's verbatim reply to the D-09 checkpoint, "Fix-before-fire"
(`probes/PREREGISTRATION.md`, plan 11-04 Task 3 entry), approved the revised
$0.52 envelope with a rider (land two instrument fixes first), and stage 5 did
not fire until plan 11-05, after both fixes landed and verified clean. The gate
plan 11-02's amendment named held exactly as designed — no cell fired against an
unapproved envelope.

(One correction to this plan's own task text, made honestly rather than
silently: the task instructions that generated this section refer to "the
$0.35-versus-re-derived-$0.49 envelope question." The actual re-derived figure,
computed and cross-checked multiple times in `probes/PREREGISTRATION.md`'s Run
log and in `.planning/STATE.md`'s decision log, is **$0.52**, not $0.49 — this
section scores the real, on-the-record figure rather than reproducing an
apparent typo.)
