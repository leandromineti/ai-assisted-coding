---
name: gemini-3-8-flash
category: 1
maker: Google
url: https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash
license: proprietary
access: closed-source   # inference from absence, not a documented negative — no download or license surface exists for these weights (model card, models index, per-model page, launch post all checked 2026-09-04); Google publishes no "weights not released" statement the way it publishes Gemma licenses
model_id: gemini-3.8-flash
release_date:
  date: 2026-09-02
  stage: GA
  note: "launch post 'Sep 02, 2026' (blog.google, verified 2026-09-04); the models index badges it 'New Stable' — Google's stage vocabulary is Stable/Preview/Experimental rather than GA/beta, and Stable is its GA-equivalent ('Most production apps should use a specific stable model'). The launch post itself uses no stage word at all; the badge lives on the models index, not the per-model page"
context_window: 1048576
max_output: 65536
pricing:
  input: 0.75          # USD per MTok — base list rate (see the registry's rule); introductory, see regime
  output: 3.75
  currency: USD
  regime: time-of-day   # closest existing value — actually DATE-tiered: every cell doubles 2027-01-01
  note: "introductory $0.75 / $3.75 per MTok 'through December 31, 2026', then $1.50 / $7.50 'starting January 1, 2027' — the pricing page states the cliff inline in every cell, so the intro window is verifiable on the page itself, not only in the launch post. No context-length tiering (single flat rate at all prompt lengths — unlike Gemini 3.1 Pro's >200k doubling). Cache read $0.075 (→$0.15), cache storage $0.50/MTok/hr (→$1.00), Batch and Flex both 50% ($0.375/$1.875 →$0.75/$3.75), Priority $1.35/$6.75 (→$2.70/$13.50). Verified 2026-09-04"
knowledge_cutoff:
  date: 2026-03          # the limit date on training data
  basis: vendor-stated
  note: "DeepMind model card, verified 2026-09-04: 'The knowledge cutoff date for Gemini 3.8 Flash is March 2026 – users can expect updated information for some domains while in others they may experience the model's knowledge is limited to January 2025' — a headline date with an in-sentence floor clause. The API docs carry no cutoff row anywhere; the card is the fact's only home (card note: references/cards/2026-gemini-3-8-flash.md). The identical sentence appears verbatim on the 3.7 and 3.6 Flash cards — copy-forward, not evidence of fresh 3.8 training"
model_features:   # nested per ADR-0014 (2026-08-19); reasoning keys split per ADR-0040
  reasoning: true
  reasoning_type: always-on   # thinking docs table, verified 2026-09-04: "gemini-3.8-flash | On (medium) | low, medium, high" — no off state and no `minimal` level; the only Off default in the table is gemini-2.5-flash-lite. gemini-3.5-flash's row still lists `minimal`; 3.8 dropped it (§ Reasoning surface)
  reasoning_effort: "levels:low/medium/high@medium"   # `thinking_level` parameter (the 3.x control; no thinking_budget documented for this model), default medium per the thinking docs table, verified 2026-09-04
  prompt_caching: "context caching: read $0.075 per MTok (0.1x of intro input) + storage $0.50 per MTok per hour — both double 2027-01-01 with the rest of the price sheet ($0.15 read / $1.00 storage). Verified 2026-09-04"
  batch_discount: "50% in+out ($0.375 / $1.875 intro; $0.75 / $3.75 from 2027-01-01) — and a separate Flex tier priced identically to Batch (verified 2026-09-04)"
  fast_mode: true   # Priority inference covers this model (supported-models table, verified 2026-09-04): `service_tier: "priority"`, "priced at 75-100% more than the standard API"; the realized premium is exactly 1.8x on both input and output ($1.35/$0.75, $6.75/$3.75) — DERIVED from the pricing page, never a quoted figure. Rate limits 0.3x standard; congestion overflow "gracefully downgraded to Standard processing" rather than 429/503
  stop_sequence_honesty: "ambiguous — OBSERVED 2026-09-05: stop-honored truncation before the trigger word, but the triggering call's finish reason (STOP) matches the no-stop control's own natural finish value — Gemini's shared STOP value cannot distinguish a stop-sequence halt from a natural completion, so the verdict rests on text comparison only, cell_id:`gemini-3-8-flash--stop-truncation--triggering--default`, probe_id:`gemini-3-8-flash--stop-truncation--triggering--default--c83e86af`, promoted ADR-0050."
  seed_determinism: "1/5 same-seed pairs (partial) — OBSERVED 2026-09-05: one of five disjoint same-seed pairs matched byte-identically (joining gpt-6-astra as the sweep's first nonzero same-seed rates; gemini-3-1-pro measured 0/5 under the same design) — still far below the unhedged bar Gemini's own undocumented-strength seed wording sets; the seed-99 effect control differed, and 8 of 10 repeats finished MAX_TOKENS at max 600 (reasoning burn), cell_id:`gemini-3-8-flash--seed--42--default`, probe_id:`gemini-3-8-flash--seed--42--default--r1--4d896ab5`, promoted ADR-0050."
  sampling_repeatability: "0/4 repeat pairs (varies) — OBSERVED 2026-09-05: gemini-3-8-flash accepts an explicit temperature:0 in default mode — a genuine temperature-0 test, not a substitute — and all five repeats produced distinct outputs (its Preview sibling gemini-3-1-pro measured 2/4 partial on the same design; the Stable-track model is LESS temp-0-stable than the Preview one), cell_id:`gemini-3-8-flash--temperature--0--default`, probe_id:`gemini-3-8-flash--temperature--0--default--r1--a3519b85`, promoted ADR-0050."
  multi_candidate_delivery: "rejected — OBSERVED 2026-09-05: candidateCount:2 returns HTTP 400 — 'Multiple candidates is not enabled for this model' — the same wire rejection as gemini-3-1-pro; the 400 body names the capability rather than the field, so the mechanical classification is corrected by a dated overrides.yaml entry (D-08), probe_id:`gemini-3-8-flash--gemini-candidate-count--2--default--6827f27f`, promoted ADR-0050."
  logprobs_delivery: "rejected — OBSERVED 2026-09-05: logprobs returns HTTP 400 — 'Logprobs is not enabled for this model' — capability-named rather than field-named, corrected by a dated overrides.yaml entry (D-08), probe_id:`gemini-3-8-flash--logprobs--true--default--f181e09c`, promoted ADR-0050."
  service_tier_contract: "response-asymmetric — OBSERVED 2026-09-05: `serviceTier` rides the request top level but is reported back NESTED at `usageMetadata.serviceTier` (the same asymmetric shape as gemini-3-1-pro and the Anthropic family), measured at this model's own audit cells: `standard` and `flex` echo verbatim, `unspecified` and an omitted field translate to `standard` — and a requested `priority` (the paid 1.8x tier this report's fast_mode cell records) comes back `standard`, silently: the request is accepted, billed at whatever actually served it, and only the nested echo says the premium tier did not, cell_id:`gemini-3-8-flash--service-tier-audit--priority--default`, cell_id:`gemini-3-8-flash--service-tier-audit--flex--default`, cell_id:`gemini-3-8-flash--service-tier-audit--omitted--default`, promoted ADR-0050."
checked: 2026-09-04   # spec block; the six wire-behavior OBSERVED cells above carry their own 2026-09-05 dates
depth: stub
---

# Gemini 3.8 Flash

"Our most intelligent Flash model, engineered for long-horizon software engineering,
autonomous agents, and complex enterprise workflows" — launched 2026-09-02 and badged
**New Stable** on the models index, which makes it **the sweep's first Stable-track
Gemini**: the only other Google entry, [Gemini 3.1 Pro](gemini-3-1-pro.md), has sat
in Preview since 2026-02-19. A restricted sibling, **Gemini 3.8 Flash Cyber**, ships
"to a set of trusted defenders" via the **Fairwind Program** (governments, critical
infrastructure operators, software maintainers) — no key path, no card on the
DeepMind index, no pricing section, so per ADR-0048 it has no first-party API
surface to assess and stays a named sighting, not a subject.

## The category-1 axes (taxonomy §1)

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | · — the positioning claims agentic use; nothing measured here |
| Long-horizon coherence | · — "long-horizon" is the vendor's own positioning word; unmeasured |
| Usable context (vs advertised) | 1,048,576 in / 65,536 out, printed exactly on the per-model page; the card rounds to "up to 1M" / "64K". No context-length price tiering, unlike 3.1 Pro |
| Cost per completed task | The intro price is a **dated, scoreable claim**: every cell doubles 2027-01-01, stated inline per cell. Floor cost is structurally higher than the sibling it replaces — thinking cannot go below `low` (no `minimal`, no off) and output billing includes thinking tokens |
| Release mode & access routes (1b) | API (Gemini API/AI Studio), Antigravity, Android Studio, Stitch, Gemini Enterprise, consumer Gemini surfaces; Cyber sibling gated by access program — the second use-domain-gated twin in the sweep after Claude's Mythos line |

## Reasoning surface

All three cells from the thinking docs table, verified 2026-09-04:

- Row: `gemini-3.8-flash | On (medium) | low, medium, high` → `always-on`,
  `levels:low/medium/high@medium`. The 3.x dial is **`thinking_level`** (no
  `thinking_budget` documented for this model).
- *"Gemini models engage in dynamic thinking by default, automatically adjusting the
  amount of reasoning effort based on the complexity of the request."*
- **The level set narrowed downward.** `gemini-3.5-flash`'s row still lists
  `minimal`; 3.8 Flash's floor is `low`, and no off state exists. Combined with the
  pricing row's label — *"Output price (including thinking tokens)"* — the cheapest
  possible response got structurally more expensive across the Flash generations,
  the inverse of the level-set growth the category README records elsewhere.
- Default `medium` joins GPT-5.6 Sol as the only non-top-half defaults in the sweep
  — still consistent with the regional pattern (every Western model defaults below
  its ceiling; four non-Western models default at theirs).

## Pricing: a prediction to score

The introductory price is exactly the shape this repo's forward-claims discipline
wants: **$0.75 / $3.75 per MTok through 2026-12-31, then $1.50 / $7.50 from
2027-01-01**, stated inline in every pricing cell — cache, batch, flex, and priority
cells all double on the same date. Score it at the first `checked:` refresh of 2027:
if the cliff lands as printed, the row just needs its base rates swapped; if Google
extends the intro window, that extension is itself a finding about how "dated" a
dated price can be.

Serving tiers are **four, not two**: Standard, Batch, Flex (priced identically to
Batch — a separate tier with separate docs), and Priority. The `fast_mode` cell
carries Priority (the premium path, ADR-0049's subject); Flex is recorded here as
the second discount path beside Batch.

## Role in this repo's work

Probed. The six ADR-0050 wire-behavior cells were filled 2026-09-05 by issue
#43's phase-2 roster fork (this model's share $0.0038 — cheapest of the three).
Two wire results worth prose beyond the cells:

- **A requested `priority` tier is silently served as `standard`.** The audit
  cell asked for the paid 1.8x tier and the nested `usageMetadata.serviceTier`
  echo said `standard` came back — accepted, no error, no top-level signal.
  Whether that is the documented graceful congestion downgrade or a key/tier
  entitlement gap, the only tell is the nested echo, which is exactly the
  failure surface conclusion 22's response-asymmetry finding warned about.
- **Stable is less repeatable than Preview here.** At temperature 0 this model
  measured 0/4 matching pairs where its Preview sibling gemini-3-1-pro measured
  2/4 — the stability label on the release channel says nothing about sampling
  stability.

## Surprises

1. **The cheapest level got deleted.** A Flash-line model dropping `minimal` while
   the family's public story is about cost is the same shape as qwen3.8-flash's
   silent `high`→`xhigh` promotion — the floor of the reasoning dial is where the
   effective price hides.
2. **The 1.8x priority premium is arithmetic, not a quote.** The docs commit only to
   "75-100% more"; the exact 1.8x on both input and output falls out of the pricing
   table. The category README's earlier "~1.8x" for Google is confirmed for this
   model — but as a derived figure.
3. **The cutoff lives only on the DeepMind card**, again — and its sentence is
   verbatim-identical across three generations of Flash cards, so the freshest-
   looking fact on the card is copy-forward prose.
4. **Antigravity is named before the API** in the launch post's developer sentence —
   the maker's own harness gets first billing over the raw model surface
   (§ Maker span's pattern, from the distribution side).

## Open questions

- Does the 2027-01-01 price cliff land as printed? (Score at next re-check.)
- ~~The six wire-behavior cells, once the probe roster forks~~ **Probed
  2026-09-05** (cells above). New question they opened: is the silent
  priority→standard tier substitution an entitlement gap on this key or the
  documented congestion downgrade — and does a Priority-enabled billing account
  see the echo flip?
- Does `thinking_level` reject or silently map the missing `minimal`/`xhigh` names?
  (The qwen3.8-flash aliasing question, portable here; a negative probe is free.)
- Does Gemini 3.8 Flash Cyber ever get a public surface (card, pricing, key path)?
  If yes it becomes a candidate; until then it is a named sighting only.
