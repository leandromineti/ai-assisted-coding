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
emitted scalar probes (one row x model x mode x value expansion each): 396
emitted content-block probes: 16
skipped cells (param x model pairs never emitted, D-11): 246 (no-thinking-off-toggle=53, toggle-not-a-request-parameter=22, toggle-shape-unknown=11, wire-shape-incompatible=160)
```

**The 42 swept rows, by group** (`python3 -c` over `probes/inventory.yaml`'s own
`params:` list, grouping by `(group, status)`): sampling=10, structural=10,
reasoning-toggle=4, service-tier=1, exotic=15, content-block=2 — sums to 42, matching
the printed `swept=42`. Plus 9 `excluded` rows (never emitted, D-09) = 51 total rows.

**The derivation, by group, cross-checked against the actual generated file
(`python3 -c` over `probes/sets/generated/contract-sweep.yaml`'s `probes:` list,
grouping each entry by its row's `group`):**

- **structural: 104.** Eight `firing_scope: all` rows × 12 models × 1 mode (no axis)
  = 96, plus the two `anthropic-structured-output-output-*` rows'
  `firing_scope: home-vendor` narrowing each to the 4 Anthropic models × 1 mode = 8.
  96 + 8 = 104.
- **service-tier: 12.** One `firing_scope: all` row, no axis, × 12 models = 12.
- **reasoning-toggle: 14.** `openai-reasoning-effort` (wire-family, home
  `openai_compat`, 7 models) + `anthropic-thinking-object` (wire-family, home
  `anthropic_messages`, 4 models) + `gemini-thinking-config` (home-vendor, 1 model) +
  `qwen-enable-thinking` (home-vendor, 2 models) = 7 + 4 + 1 + 2 = 14.
- **sampling: 160.** The per-model mode multiplier implied by each `reasoning_toggle`
  value (D-06): `always-on` and `none` each emit exactly ONE real cell (5 models are
  `always-on` in this registry: claude-fable-5, gemini-3-1-pro, grok-4-5, kimi-k3,
  glm-5.3 — no model is currently `none`); `default-on` and `opt-in` each emit BOTH
  cells (6 models `default-on`: claude-opus-5, claude-sonnet-5, gpt-5-6-sol,
  deepseek-v4, qwen3.8-max, qwen3.8-flash; 1 model `opt-in`: claude-haiku-4-5). Per
  sampling row: 5×1 + 6×2 + 1×2 = 19 cells; × 10 sampling rows = 190 candidate cells
  before availability skips. `axis_fragment_availability()` then removes every cell a
  `vendor_overrides` entry admits it cannot construct (D-08): DeepSeek's null
  `toggle-not-a-request-parameter` override removes both modes × 10 rows = 20; Kimi's
  null `toggle-shape-unknown` override removes its one always-on-model mode × 10 rows
  = 10. 190 − 20 − 10 = 160, matching the generated file exactly.
- **exotic: 106.** The 15 exotic-group rows' mixed `firing_scope` (`wire-family` fires
  at 4–7 models depending on home family; `home-vendor` fires at 1–4; `all` for
  `gemini-temperature-range`'s sibling-scope none — it is itself `home-vendor`), summed
  directly from the generated file rather than re-derived arithmetically here, since
  the group mixes three different firing scopes and one boundary-contract row with two
  probe values — the same reason this section states the COMMAND that produced the
  number rather than a hand-typed total (CLAUDE.md: a count carries its measure).
- **Total scalar: 104 + 12 + 14 + 160 + 106 = 396**, matching
  `emitted scalar probes: 396` exactly.
- **content-block: 16.** `image-input` (`firing_scope: all`, 12 models) +
  `anthropic-cache-control-block` (`firing_scope: home-vendor`, 4 Anthropic models) =
  12 + 4 = 16, matching `emitted content-block probes: 16` exactly.

**412 total probe cells** (396 scalar + 16 content-block) will be fired by the sweep as
currently designed, plus 246 cells that are declared skips and never fired at all
(D-11) — every param × model pair is therefore either an emitted cell or a
skipped-cells.yaml entry with a reason, never a silent absence.

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

**Per-vendor envelope** (from `probes/harness/prices.yaml`'s per-model rates × the
assumed 9 input / model-specific output tokens, summed across every scalar AND
content-block cell that vendor's models fire, per the § Expected cell count
derivation):

| Vendor | Emitted cells (scalar + content-block) | Raw cost | Envelope (rounded up) |
|---|---|---|---|
| anthropic | 126 + 8 = 134 | $0.1803 | **$0.19** |
| dseek | 22 + 1 = 23 | $0.0061 | **$0.01** |
| gemini | 24 + 1 = 25 | $0.0605 | **$0.07** |
| kimi | 24 + 1 = 25 | $0.0247 | **$0.03** |
| openai | 44 + 1 = 45 | $0.0884 | **$0.09** |
| qwen | 90 + 2 = 92 | $0.0199 | **$0.02** |
| xai | 33 + 1 = 34 | $0.0137 | **$0.02** |
| zai | 33 + 1 = 34 | $0.0100 | **$0.02** |
| **Total (sum of rounded)** | **412** | **$0.4036** | **$0.45** |

This envelope's total ($0.45, an over-count upper bound per the assumptions above) is
under 5% of the milestone's $10 global hard ceiling (HARN-03) and under 5% of even the
CURRENT $1.50 per-vendor soft default — the contract sweep, as designed, is not close
to threatening either ceiling. That headroom is exactly what the next section proposes
tightening, as a falsifiable prediction rather than an applied change.

## Proposed sub-ceiling adjustments (dated prediction, NOT applied)

`probes/harness/ceilings.yaml` is unchanged by this phase — verified by an automated
`git status --porcelain` gate in this plan's own Task 3 verification — and is edited
only at Phase 11 start, under the owner's explicit spend sign-off (D-16). Everything in
this section is a proposal and a dated (2026-09-01) falsifiable prediction, not an
applied number.

**Proposal: lower `vendor_soft_usd_default` from $1.50 to $0.50.** Derivation: the
highest per-vendor envelope above (anthropic, $0.19) leaves roughly 2.6x headroom under
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
unanticipated retry storm inflated the attempt count well past 412. Confirmed if real
per-vendor spend across the full Phase 11 sweep stays under $0.50 for all eight
vendors, matching the ~10x-to-2.6x headroom this document derives.

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
2. **The two open Phase 9 robustness findings from `09-REVIEW`** — CR-01 (a
   connection-level `URLError`/timeout uncaught in `client.py`: one flaky network
   moment crashes a whole sweep) and CR-02 (`_find_vendor_breach` reports only the
   FIRST breaching vendor, masking later breaches) — remain unfixed as of this plan.
   Neither bit Phase 9's 5-probe smoke; both are far more likely to bite Phase 11's
   412-cell, 8-vendor sweep. Fix via `/gsd-code-review 9 --fix` or fold into Phase 11
   planning before firing begins.
3. **The evidence-commit policy for `probes/raw/` and `probes/ledger.jsonl` is
   provisional** (owner checkpoint `gitignore-evidence`, 2026-09-01, "maybe I will
   change it later" — `.planning/STATE.md` § Blockers/Concerns). Its revisit gate is
   Phase 11, before the sweep's 412 real HTTP responses become the evidence base this
   milestone's promotion phase (Phase 13) relies on.
4. **The skip-reason vocabulary this phase's plans introduced** (`SKIP_REASONS` in
   `probes/inventory-to-sets.py`: `no-thinking-off-toggle`, `no-thinking-capability`,
   `wire-shape-incompatible`, `toggle-shape-unknown`, `toggle-not-a-request-parameter`)
   is what lets Phase 11 satisfy "every param × model cell is either an emitted probe
   or an explicit, reasoned skip" — the 246 skipped-cells.yaml entries are already
   proof this holds at design time; Phase 11 should not need a sixth reason unless a
   genuinely new admitted-unknown shape shows up mid-sweep.
5. **`anthropic-thinking-budget-floor` needs a per-row `max_tokens` raise before
   firing.** Its two probe values (500, 1024 budget_tokens) both exceed the registry's
   shared `defaults.max_tokens` (64) — firing this row with the shared default would
   confound the floor finding with an unrelated `max_tokens`-too-small rejection, since
   Anthropic's own documented constraint requires `budget_tokens < max_tokens`. There
   is no per-row `max_tokens` override field in `probes/inventory-to-sets.py` as of
   this plan (only a per-MODEL `defaults.max_tokens_overrides`) — Phase 11 needs either
   a one-off `max_tokens` override for this specific cell, or a registry field this
   plan did not add.
