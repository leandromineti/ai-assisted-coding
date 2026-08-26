# ADR-0042 — the `vendor:` transcription field becomes `maker:`

`decided: 2026-08-26` · status: **accepted**

## Decision

The top-level report frontmatter key `vendor:` is renamed **`maker:`** across all 45 tool
reports and both templates. Values are unchanged; this is purely a key rename, registered
in `docs/tool-taxonomy.yaml` → `schema_renames` with `status: applied`, so LINT-05 fails any
surviving `vendor:` key in `tools/`.

The field's definition is rewritten from *"who maintains (or trains) it"* to **"who built or
trained it — a company, a research lab, or a named individual"**, dropping a hedge that
existed only because the old name was wrong.

## Context

"Vendor" asserts a commercial relationship the field does not carry. Of 37 distinct values,
**four are private individuals** — `Fabio Akita (akitaonrails)`, `Affaan Mustafa
(affaan-m)`, `Ivan Zakutnii (m0n0x41d)`, `Max Ritter` — and two more explicitly disclaim
one: `Open GSD`, and `superradcompany (open-source project; …)`. Calling a person the
vendor of their MIT-licensed side project is a category error, and the definition's
parenthetical hedge was the field quietly admitting it.

## Why not `provider`

`provider` was the owner's first proposal and is **rejected on collision**, not on accuracy.
It already means something specific and different throughout this repo: *the LLM API backend
a harness talks to*.

- `tools/2-harnesses/README.md` — "75+ **providers**", "multi-**provider** client"
- `tools/2-harnesses/pi.md` — "~9 **provider** API families", "spawns Codex/Claude Code as
  subagent **providers**"
- and it is the term of art in the source those reports quote: `model.providerID`,
  `resolveApiKey(providerId, …)`, `core/llm/llms/`

Renaming the field to `provider` would put `provider: Anomaly` (who *makes* opencode)
directly above prose about the 75+ providers opencode *talks to* — a new
`split_meaning_terms` entry on day one, in the category this file already records `stack`
under and admits **no lint can adjudicate**. Trading a wrong-but-unambiguous word for an
ambiguous one is a bad trade.

`maintainer` was also considered and is weaker for category 1: Anthropic does not *maintain*
Opus 5, it trained it once. `maker` covers trained-it and built-it in one word, is true of a
person and a company alike, and collides with nothing.

## Scope — and what is deliberately excluded

**`vendor:` on `references/cards/` is NOT renamed.** It is a different field on a
different note type, and it is correct there: a vendor model card is by definition a
commercial vendor's document, and all four tracked cards are from commercial vendors
(`references/README.md` calls them exactly that). No per-entry gate is needed in the lint —
`references/*` is `exempt_paths.skip_entirely`, so LINT-05 never walks it.

Prose uses of the English word remain and are correct where the subject really is a
commercial vendor: `docs/tool-taxonomy.md` § **Vendor span** (every row is a company, and
the co-optimization it warns about is a business strategy), the `vendor-stated`
`knowledge_cutoff.basis` value (all model makers with a stated cutoff are companies), and
"vendor-native" as a harness descriptor. *Vendor span is the subset of maker span with a
business behind it* — the distinction is now real rather than accidental, and § Vendor span
says so.

## Consequences

- **LINT-05 actually enforces this one.** Worth contrasting with
  [ADR-0040](0040-reasoning-replaces-thinking.md) the same day, where `schema_renames` was
  rejected as a silent false green: its matcher is `^{old}:(\s|$)`, anchored at column 0, so
  it cannot see keys nested inside a `*_features:` block. `vendor:` is top-level, so the
  mechanism fits, and the decoder is registered rather than merely described.
- **A stale `rendered_in` is corrected in passing.** The field's registry entry claimed
  `rendered_in: [tools.md]`; `comparisons/tools.md` has no such column and never did — the
  claim was true only of `vendors.md`, removed hours earlier in
  [ADR-0041](0041-vendors-matrix-removed.md), and the trim to `[tools.md]` was made without
  checking. It is now `rendered_in: []`: no generated matrix renders this field. It carries
  the hand-kept category inventories and § Vendor span.
- Six category `README.md` files list the field among their transcription fields; all six
  updated. `scripts/build-db.py`'s reports-table column follows the key.
- Anything dated before 2026-08-26 calls this field `vendor:`. The decoder is in
  `schema_renames` and in `adrs/README.md`'s standing decoders.
