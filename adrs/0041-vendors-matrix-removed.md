# ADR-0041 — `comparisons/vendors.md` is removed; its one claim moves to prose

`decided: 2026-08-26` · status: **accepted**

## Decision

The generated vendor matrix `comparisons/vendors.md` and its `render_vendors()` generator
are deleted. The `vendor:` transcription field stays — it is still a fact worth recording
per report, and it still renders in `tools.md`.

The one signal the matrix carried moves into
[`docs/tool-taxonomy.md`](../docs/tool-taxonomy.md) § *Vendor span*, which was already the
**authoritative** surface for this question and said so.

## Context

The matrix printed one row per exact `vendor:` string, columns by category. At removal it
was 37 rows, of which **33 had a single tool in a single category** — a vendor's name
repeated back with one entry beside it. The information was in the last line: four vendors
span ≥2 categories, and all four are model makers whose second category is harnesses.

Its designed role was narrower than the table, and had quietly stopped working.
`tool-taxonomy.md` paired the two deliberately: the hand-kept table admits closed,
observation-only products (Claude Code, cloud Codex, Cursor, Managed Agents), the generated
matrix can only see tools that have report files, and **the gap between their spanner
counts was the closed-product blind spot, quantified**. That reading was recorded on
2026-08-17 as "2 generated vs 4 hand-kept".

By 2026-08-26 both surfaces read **4** — over *non-identical sets*. The generated four were
Anthropic, DeepSeek, Google, OpenAI; the hand-kept four were OpenAI, Anthropic, Google,
xAI. The instrument had converged on a number that looked like agreement and wasn't,
because DeepSeek gained a tracked harness (dsh) while xAI's harness (Cursor) remains closed
and unreportable. A gap metric whose two sides count different things does not measure the
blind spot; it hides it.

## The claim that survives

**Vendor span runs one way: model makers ship harnesses for their own weights.** Six of the
eight vendors with a tracked model report now have one — Anthropic (Claude Code), OpenAI
(Codex), Google (Gemini/Antigravity CLI), DeepSeek (dsh), xAI (Cursor, acquired), Alibaba
(qwen-code, a gemini-cli fork, tracked as a candidate). No harness maker in the set has
trained a model and moved the other way.

The two model vendors without a harness — Moonshot and Z.ai — are the sweep's most recent
model entries, so the absence reads as *not yet* rather than *not the pattern*. Recorded
that way on purpose: "this vendor has no harness" is a dated observation with a short shelf
life, not a stable fact.

## Consequences

- **Rule 3 is unaffected.** The rule forbids hand-keeping an index that could be generated;
  it does not require generating every index that *could* be. `tool-taxonomy.md` § Vendor
  span keeps its standing exception, for the reason it always had: the sharpest spanners
  are closed products with no frontmatter to generate from. Deleting the generated floor
  removes a second surface, not a check.
- **One fewer generated file to keep honest.** The removed matrix had a live maintenance
  cost — exact-string grouping meant a vendor spelling drift silently split one maker into
  two rows, which is why the `vendor:` field's registry definition warned about it. The
  definition is rewritten to name the real hazard (identity when reasoning about span)
  rather than a file that no longer exists.
- **The vendor-span picture is now single-sourced**, hand-kept, and dated. That is a
  deliberate loss of the automated floor: a future reader gets one table that admits closed
  products, instead of two that disagreed for a reason nobody re-derived.
- Inbound references updated: `CLAUDE.md`'s `comparisons/` row, `docs/tool-taxonomy.md`
  (both the table and the why-hand-kept paragraph), `tools/2-harnesses/claude-code.md`'s
  vendor-span bullet, and the `vendor` entry in `docs/feature-taxonomy.yaml`.
