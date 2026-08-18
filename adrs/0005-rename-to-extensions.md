# ADR-0005 — Rename "portable artifacts" → "Extensions"

`decided: 2026-08-17` · `recorded: 2026-08-18 (backfill — text extracted verbatim from
taxonomy.md §3 as of commit fd9f189)` · status: **accepted**

## Decision

The bucket's display name becomes **Extensions** (full: "Extensions & protocols").

## Record (extracted from taxonomy.md, as written)

> **Renamed "portable artifacts" → "Extensions" (2026-08-17).** The old display name
> baked an adoption *outcome* into the category's identity. Portability is not an
> intrinsic property of an extension — it is a status the ecosystem confers by
> adoption, and it has been conferred unevenly: hooks are the control group (same kind
> of thing, no second adopter, no portability), rules files gained portability when a
> rival vendor chose to link competitors' formats (artifact unchanged, market moved —
> the Warp evidence under conclusion 3), and MCP holds the limit case, portability by
> standardization. The bucket's members are extensions; *how portable each kind is* is
> a dated, per-kind measurement (the Standards scoreboard), not a name.

## Consequences

Directory slug stayed `…-capability-extensions` (storage key); display name
"Extensions" everywhere else, including the generator's layer-name table.
