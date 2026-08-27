# ADR-0049 — `fast_mode`: a presence key for speed-premium serving

`decided: 2026-08-27` · status: **accepted**

## Decision

The category-1 assessed block gains a sixth key: **`fast_mode`**, `value_type: presence`,
`group: cost`. ✓ means the first-party API offers a paid option to serve **this same
model** at higher output-token throughput — whatever the vendor calls it (Anthropic
"fast mode", OpenAI `service_tier: fast|priority`, Google "Priority" tier). Two things
deliberately do **not** count: a faster *sibling model* (Haiku, Flash, Luna, Turbo — a
different product, recorded in `pricing` notes and Maker span, not here), and a
capacity/SLA commitment that claims no token-speed gain. The premium multiplier and the
mechanism live in each report's cell comment and prose; the cell is the presence claim,
with the standard semantics (omitted = not checked, `false` = checked and absent).

It is `batch_discount`'s inverse — batch trades speed away for a discount, `fast_mode`
buys speed at a premium — which is why both sit in the `cost` group.

## Context — the owner's ask, and what the definition had to exclude

Owner-requested (2026-08-27): "the presence or not of a fast mode … it should indicate
if the API allows for faster token throughput." The definitional work was in the
exclusions. The request initially read as *fast model*, which would have keyed on the
speed-tier sibling — and that key would have failed rule 5d outright: every maker in the
sweep ships or plausibly ships a cheap-fast sibling, so the column would have been
~13/13 ✓. Fast *mode* — same weights, faster serving, higher price — discriminates:
the first sweep landed **3 ✓ / 9 ✗ / 1 ·** across 13 models.

The sweep's finding is in the split itself: the three ✓s are exactly the three Western
frontier vendors — Anthropic (up to 2.5× OTPS at 2× price, Opus 5/4.8 only, research
preview), OpenAI (all three GPT-5.6 tiers; "priority processing" renamed *fast mode*
2026-07-30, both `service_tier` values accepted), Google (Priority tier, ~1.8×, listed
for Gemini 3.1 Pro) — while every non-Western maker checked (DeepSeek, Moonshot, Z.ai,
Qwen×2) has none, and xAI has none. Read against `reasoning_effort`'s regional split
(non-Western makers default to their most expensive reasoning level, Western ones lower),
the two keys are near-mirror images: the West sells speed as the premium add-on, the
Chinese makers spend the premium on reasoning by default.

One vendor needed care: Anthropic also sells a "Priority Tier", which is a capacity
commitment, not a throughput claim — its fast-mode page explicitly separates the two
("Fast mode is not available with a Priority Tier commitment"). The definition's
"claims no token-speed gain" clause exists for exactly this.

## Rejected alternative — free-text like the other economics keys

The assistant's recommendation, overridden by the owner: carry the key as free-text in
vendor vocabulary (the `prompt_caching`/`batch_discount` shape), on the argument that
the premium multiplier is the fact that varies. Recorded honestly: the boolean is
defensible on its own terms — presence genuinely discriminates here (3/9/1, unlike
`reasoning`'s 12/1), the multiplier still lives one hop away in the cell comment, and a
sortable ✓/✗ column is what the matrix can actually use. If the multiplier later needs
to be comparable across vendors (three instances would be the bar), that is a
`structured` upgrade, not a regret.

## Consequences

- Registered in `docs/feature-taxonomy.yaml` after `batch_discount`; the matrices and
  `build-db` pick it up from the registry with no script change.
- Twelve cells filled at birth, each verified against a first-party surface dated
  2026-08-27 in its cell comment. One cell honestly omitted: **qwen3-coder-next** — the
  Model Studio page reachable today does not list the model, so there is no surface that
  could have shown the absence (rule 1b), and a ✗ would be a guess.
- The two Qwen3.8 ✗s ride one strong surface: QwenCloud's own Prime Mode page (TPS
  1.5–2× — the platform's throughput mode) enumerates its supported models and neither
  appears.
- Template and category README updated (5 keys → 6).
- No schema rename, no decoder.
