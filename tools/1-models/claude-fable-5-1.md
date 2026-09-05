---
name: claude-fable-5-1
category: 1
maker: Anthropic
url: https://platform.claude.com/docs/en/models/fable-5-1/overview
license: proprietary
access: closed-source
model_id: claude-fable-5-1
release_date:
  date: 2026-09-01
  stage: GA
  note: "docs model page: 'Latest. Released September 1, 2026'; the announcement (anthropic.com/claude-fable-and-mythos-5-1) is dated month-level only ('September 2026') but supplies the stage word — 'Fable 5.1 is generally available, while Mythos 5.1 is available only through our trusted access programs'. Day-level date is docs-sourced (model page + the release-notes heading '## September 1, 2026'); verified 2026-09-04"
context_window: 1000000
max_output: 128000
pricing:
  input: 10          # USD per MTok — base list rate (see the registry's rule)
  output: 50
  currency: USD
  regime: flat
  note: "$10 / $50 per MTok, unchanged from Fable 5 — the launch's entire price move lives in the cache-read rate (see prompt_caching); verified 2026-09-04"
knowledge_cutoff:
  date: 2026-06          # the limit date on training data
  basis: vendor-stated
  note: "Jun 2026, and the model page's two fields coincide again ('Reliable knowledge cutoff | Jun 2026' / 'Training data cutoff | Jun 2026') — same shape as Fable 5, five months fresher than its Jan 2026. Verified 2026-09-04 on the per-model overview page"
model_features:   # nested per ADR-0014 (2026-08-19); reasoning keys split per ADR-0040
  reasoning: true
  reasoning_type: always-on   # per-model troubleshooting table, verified 2026-09-04: "Claude Fable 5.1 | Adaptive only | Always on", rejecting BOTH `"enabled"` and `"disabled"` with a 400 — the same strictest row Fable 5 holds
  reasoning_effort: "levels:low/medium/high/xhigh/max@high"   # effort page, verified 2026-09-04: "Claude Fable 5.1 supports all five effort levels. Start with `high`, the default." Dial is `output_config.effort`
  prompt_caching: "write 1.25x (5m TTL, $12.50) / 2x (1h TTL, $20), read 0.025x — $0.25 per MTok. The read rate is the launch's headline price move: every other Claude model reads cache at 0.1x, and the pricing-page footnote names Fable 5.1 + Mythos 5.1 as the only 0.025x models (verified 2026-09-04 on the model page, the pricing page, and the what's-new page)"
  batch_discount: "50% in+out ($5 / $25 per MTok) — what's-new page, verified 2026-09-04"
  fast_mode: false   # checked and absent: the fast-mode page's supported-models pricing table has one row, "Claude Opus 5 / Claude Opus 4.8" — Fable 5.1 appears on that page only in sidebar navigation, not content (verified 2026-09-04)
  stop_sequence_honesty: "honest — OBSERVED 2026-09-05: stop-honored truncation before the trigger word, and the response's own stop_reason field reports the distinguishable value stop_sequence (vs. end_turn on the no-stop control) — the same honest verdict claude-fable-5 measured, reproduced at the revision's own cell, cell_id:`claude-fable-5-1--stop-truncation--triggering--default`, probe_id:`claude-fable-5-1--stop-truncation--triggering--default--63b65222`, promoted ADR-0050."
  seed_determinism: "n/a (no request-side field) — OBSERVED 2026-09-05: Anthropic's Messages API reference documents no seed parameter — the checked absence recorded at the 5.0 roster (rule 1b) carries to the revision, declared as this model's own cited skip, docs-claims:`seed/anthropic`, promoted ADR-0050."
  sampling_repeatability: "0/4 repeat pairs (varies) — OBSERVED 2026-09-05: claude-fable-5-1 rejects an explicit temperature value outright in default mode (HTTP 400, the documented post-Opus-4.6 contract); this default-config-repeatability SUBSTITUTE asks whether the model's own default (implicit) sampling is repeatable across five identical requests with no temperature parameter sent — all five completed naturally (end_turn) with five distinct outputs, the exact 0/4 (varies) its 5.0 predecessor measured, cell_id:`claude-fable-5-1--default-config-repeatability--no-temperature--default`, probe_id:`claude-fable-5-1--default-config-repeatability--no-temperature--default--r1--0775d278`, promoted ADR-0050."
  multi_candidate_delivery: "n/a (no request-side field) — OBSERVED 2026-09-05: Anthropic's Messages API reference documents no n/candidateCount-equivalent multi-candidate parameter — the 5.0 roster's checked absence (rule 1b) carries to the revision, declared as this model's own cited skip, docs-claims:`n/anthropic`, promoted ADR-0050."
  logprobs_delivery: "n/a (no request-side field) — OBSERVED 2026-09-05: Anthropic's Messages API reference documents no logprobs parameter — the 5.0 roster's checked absence (rule 1b) carries to the revision, declared as this model's own cited skip, docs-claims:`logprobs/anthropic`, promoted ADR-0050."
  service_tier_contract: "response-asymmetric — OBSERVED 2026-09-05: measured at this model's OWN audit cells rather than the sibling inference the 5.0 cell rested on — `service_tier` rides the request top level and is reported back NESTED at `usage.service_tier` (auto, standard_only, and an omitted field all resolve to a nested `standard`, top level absent), and sending the response-vocabulary word `standard` as a request value is rejected outright naming the field (HTTP 400) — the haiku-measured request/response vocabulary split reproduced at the revision, cell_id:`claude-fable-5-1--service-tier-audit--auto--default`, cell_id:`claude-fable-5-1--service-tier-audit--trap--default`, probe_id:`claude-fable-5-1--service-tier-audit--auto--default--c4f4cca9`, promoted ADR-0050."
checked: 2026-09-04   # spec block; the six wire-behavior OBSERVED cells above carry their own 2026-09-05 dates
depth: stub
---

# Claude Fable 5.1

Anthropic's successor flagship, GA 2026-09-01 — "Latest" in the docs' own status
vocabulary, with [Fable 5](claude-fable-5.md) simultaneously restamped "Legacy"
(still Active, retirement "Not sooner than June 9, 2027"). Same specs and list price
as 5.0 in every visible cell but three: the cache-read rate (cut 75%, below), the
knowledge cutoffs (Jan → Jun 2026), and the release/retirement dates. The paired
sibling **Claude Mythos 5.1** (`claude-mythos-5-1` — the 5.1 docs state the id its
5.0 predecessor never got) is "the same model, but with different levels of
safeguards", trusted-access only. The framing shifted between generations: the 5.0
pages contrasted the two by safety classifiers Fable carries and Mythos lacks; the
5.1 pages drop the classifier contrast entirely.

**Sighting chain, worth keeping:** this model was first sighted in a *rival's*
benchmark table — OpenAI's GPT-6 Astra launch post (2026-09-03) scores a "Claude
Fable 5.1" column — and only then located first-party. The two same-week launch
posts score each other's models, giving the roster its first cross-vendor scoring
pair (see [gpt-6-astra](gpt-6-astra.md)).

## The category-1 axes (taxonomy §1)

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | · — though the API *contract* moved: forced tool use (`tool_choice: any`/`tool`) now returns 400 on this model, a breaking change from 5.0 (docs what's-new, 2026-09-04) |
| Long-horizon coherence | · — vendor positioning only |
| Usable context (vs advertised) | 1M advertised, unchanged; the 5.0 tokenizer caveat (~30% inflation vs pre-4.7 models) presumably carries but is not restated on the 5.1 pages — unverified here |
| Cost per completed task | The cache-read cut is aimed exactly at this axis: vendor estimates "around 25%" cheaper for typical workloads, "up to approximately 45%" for highly agentic work — both estimates, not measured rates |
| Release mode & access routes (1b) | GA on the Claude API + cloud routes; the announcement says "Microsoft Azure" where the docs say "Microsoft Foundry" and add "Claude Platform on AWS" as a fifth platform the announcement doesn't name — the two first-party surfaces disagree on the route list (2026-09-04) |

## What changed from Fable 5 (as documented, 2026-09-04)

Identical: context (1M), max output (128K), $10/$50, both cache-write rates, batch
$5/$25, thinking (adaptive, always on, rejects both toggle values), the five-level
effort dial and its `high` default, tokenizer, platform list.

Changed or new:

- **Cache reads $1 → $0.25 per MTok (0.1x → 0.025x)** — the only price change, and
  the first break in what had been a universal 0.1x cache-read multiplier across
  Claude models. Corroborated on four first-party surfaces; the pricing-page
  footnote: *"Cache hits and refreshes on Claude Fable 5.1 and Claude Mythos 5.1 are
  priced at 0.025x the base input price. All other models use the standard 0.1x
  multiplier."* Directly changes `probes/harness/prices.yaml` math for any future
  Anthropic agentic cells.
- **Cutoffs Jan 2026 → Jun 2026**, reliable and training still coinciding.
- **Forced tool use returns 400** — a breaking API change on this model.
- **Thinking blocks are bound to the producing model and conversation** (400 "The
  block is bound to a different conversation"), enforced for accounts created on or
  after 2026-08-31.
- Betas: per-message effort (`mid-conversation-output-config-2026-07-01`),
  turn-scoped system messages, `thinking.display: "updates"`.
- Text watermarking + C2PA metadata.

## Safeguards (announcement, 2026-09-04 — read the denominators)

Three vendor claims that are easy to transcribe wrong, recorded with their exact
scopes:

- Two *different* 60% figures coexist in the announcement: "our newest safeguards
  block 60% fewer false positives than before" (cybersecurity, general) and "Claude
  Code users can expect an average of around 60% fewer interventions per session"
  — different denominators, not one claim.
- The 85% biology figure is **not a 5.1 delta**: *"our latest biology safeguards for
  Fable 5.1 and Fable 5 fire 85% less often for benign requests…"* — it covers both
  models and predates this launch ("As we recently shared").
- The vulnerability/exploit split is narrower than the headline: discovery is
  permitted, exploit development refused, and *"safeguards do, however, still
  redirect several kinds of dual-use cybersecurity tasks… to our Opus models"*
  (penetration testing, exploit generation, binary-based vulnerability scanning).

## Vendor-stated benchmarks (announcement, month-stamped September 2026)

Terminal-Bench 4.0 **55.8%** (Mythos 5.1: 60.9%) · Terminal-Bench-Science 0.1
**52.6%** · HLE no-tools **60.9%** · CursorBench 3.2.0 **73.4%**. OpenAI's Astra
post provides same-week third-party numbers for this model — the cross-vendor pair
above.

## Role in this repo's work

Probed — and this report is now **the scored first test of ADR-0050's promoted
wire-behavior vocabulary against a model revision** (issue #43 phase 2, fired
2026-09-05 at this model id, never inherited from
[claude-fable-5](claude-fable-5.md)'s 5.0-roster probes). **Verdict: all six
cells reproduce the 5.0 record in kind.** Three checked absences carry
(seed/n/logprobs — re-declared as this model's own cited skips), the
sampling-repeatability substitute lands on the identical 0/4 (varies), stop
honesty is again `honest` with the distinguishable `stop_sequence` value, and
the service-tier response asymmetry — which the 5.0 cell could only assert via
the shared-contract argument through claude-haiku-4-5 — is now measured at this
model's own audit cells, including the vocabulary-split trap rejection. The
promoted vocabulary survived its first revision without a wording change; what
the revision test actually bought is an evidence upgrade (sibling inference →
own cells) rather than a verdict change. Fork share: ~$0.056.

## Surprises

1. **A structural price cut.** Base rates unchanged; the entire "cheaper" claim
   lives in one multiplier (cache reads 0.1x → 0.025x). A price table that records
   only input/output would show this launch as a no-op.
2. **A breaking change shipped inside a point release** — forced `tool_choice`
   returning 400 changes harness-facing behavior under a model id whose siblings
   accept it.
3. **First-party surfaces disagree on the platform list** (Azure vs Microsoft
   Foundry, and a fifth route only the docs name).
4. **The announcement carries no day-level date.** "September 2026" is all the post
   states; the GA day exists only in the docs. A citekey or release row sourced
   from the announcement alone would be month-precision.

## Open questions

- ~~The six wire-behavior cells — probed at `claude-fable-5-1`, do they reproduce
  the 5.0 verdicts?~~ **Answered 2026-09-05: yes, all six in kind** (§ Role) —
  the revision test's value was the evidence upgrade, not a verdict change.
- Does the 0.025x cache-read rate actually deliver the "~25% / up to ~45%" vendor
  estimates on this repo's own agentic transcripts? (`prices.yaml` gives the
  arithmetic once the roster batch lands.)
- The system card — *"Claude Fable 5.1 and Mythos 5.1"* (September 2026), at
  anthropic.com/claude-fable-5-1-mythos-5-1-system-card, a page rather than a PDF —
  is an unread lead; a card note (with snapshot) is owed if it is read.
- Does the ~30% tokenizer-inflation caveat recorded on the 5.0 report carry to 5.1?
  The 5.1 pages don't restate it either way.
