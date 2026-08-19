# ADR-0014 — Model API-feature keys fold into the registry (`model_features` block)

`decided: 2026-08-19` · status: **accepted**

## Decision

The four layer-1 API-feature keys (`thinking`, `effort_control`, `prompt_caching`,
`batch_discount`) move from a hardcoded list in `build-tool-index.py` into the feature
taxonomy as a fourth block, **`model_features`** (`applies_to: [1]`), and from
top-level report frontmatter into a nested `model_features:` block on the ten layer-1
reports. Values stay free-text (the economics differ structurally across vendors —
multipliers vs absolute prices vs TTL tiers) with the same verified-only semantics:
set only when confirmed against the report's `url` on its `checked` date.

- `comparisons/features.md` gains a **Models (layer 1)** section rendering the block —
  every layer's capability slice now lives in one generated file.
- `comparisons/models.md` keeps its quantitative surface (context window, output,
  pricing, cutoff, `released` lifecycle, `checked`, depth) and derives its feature
  columns from the registry instead of the hardcoded list.
- The `released` lifecycle key stays top-level: it is a lifecycle fact in the vendor's
  own vocabulary, not an assessed capability — same reasoning that keeps `license`
  rendered-not-registered.

## Context

ADR-0010 deferred "folding MODEL_FEATURE_KEYS in" because the keys' top-level shape
did not fit the registry's block contract. Since then the registry gained per-block
precedent (ADR-0013) and the block contract proved cheap to migrate onto. The
trigger was cosmetic-but-telling: features.md acquired sections for every layer
except 1, and the hardcoded list sat directly beneath the generator comment saying
"Do NOT hardcode keys here." This closes ADR-0010's last deferred item — both
resolved in the more-blocks direction.

## Consequences

- One key discipline everywhere: all four blocks registry-driven, `KNOWN_BLOCKS`
  guard covers them, unknown-key warnings apply to model reports for the first time.
- Ten report frontmatters migrate mechanically (keys unchanged, values unchanged,
  nesting added). Generated matrices are re-derived; no cell content changes.
- New model-feature keys now require the same issue-#2 two-instances bar and
  registry entry as everywhere else.
