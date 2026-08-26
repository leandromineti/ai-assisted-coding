---
name: grok-4-5
category: 1
vendor: xAI
url: https://docs.x.ai/docs/models
license: proprietary
open_source: false
model_id: grok-4.5
release_mode: api-only
released: "July 2026, no stage vocabulary ('now available on the xAI API') — month-level only from the first-party release notes; the day this repo carries (07-08) is third-party-corroborated, x.ai's dated announcement being unfetchable (verified 2026-08-17)"
context_window: 500000
max_output: "no model-specific figure published; generic max_completion_tokens defaults to 128000, visible-output only (checked 2026-08-17)"
pricing:
  input: 2          # USD per MTok — base list rate (see the registry's rule)
  output: 6
  currency: USD
  regime: context-tiered
  note: "$2 / $6 per MTok for prompts <200k tokens; $4 / $12 at ≥200k — the higher rate applies to ALL tokens once the prompt reaches 200k (re-verified 2026-08-17)"
knowledge_cutoff:
  date: null          # the limit date on training data
  basis: retracted
  note: "RETRACTED 2026-08-17 — the 'Feb 1, 2026' recorded 2026-07-31 is documented for Grok 4.6, not 4.5; no first-party page states a 4.5 cutoff (model page, overview, release notes, launch post all checked)"
model_features:   # nested per ADR-0014 (2026-08-19); values unchanged
  thinking: "reasoning always-on, 'cannot be disabled'; reasoning_tokens in usage, encrypted reasoning content via include param"
  effort_control: "reasoning_effort: low/medium/high, default high; 'xhigh' silently downgraded to high (xhigh is 4.6+ only)"
  prompt_caching: "automatic (server-affinity via prompt_cache_key / x-grok-conv-id); cached input $0.30 (<200k) / $0.60 (≥200k) per MTok = 0.15x; TTL not stated anywhere in the caching docs"
  batch_discount: "verified absent — Grok 4.5 is excluded from the Batch API entirely ('will be rejected'); the 20% batch discount covers 4.3/4.20-era models only"
checked: 2026-08-17
depth: stub
---

# Grok 4.5

xAI's recommended model "for code and chat" (released 2026-07-08 on the 1.5T-param V9
base, per the 2026-07-28 verified sweep). The category-1↔2 story attached to it is why it
matters to this repo: **trained on real Cursor session data** — the sharpest instance
of the harness-as-training-data-instrument pattern in the taxonomy's boundary-rule
note. No EU availability at launch (2026-07-28 check; not re-verified today).

## The category-1 axes

| Axis | Evidence here |
|---|---|
| Tool-call fidelity | · — though the training-data story implies optimization for *harness-shaped* interaction specifically |
| Long-horizon coherence | · |
| Usable context (vs advertised) | 500k — **half of the 1M its own cheaper siblings offer** (Grok 4.3 and 4.20: 1M at $1.25/$2.50). The flagship trades window for capability, inverting the usual assumption |
| Cost per completed task | The cross-cutting note records xAI's own pitch: ~60% cheaper per token than frontier tier, ~half the per-task cost in Codex — vendor claim, unmeasured here |
| Release mode & access routes (1b) | API-only (`console.x.ai`); tiered pricing at the 200k boundary like Google |

## Role in this repo's work

None as a model. As a *case*, load-bearing: it anchors the taxonomy's vertical-
integration story (Cursor acquisition → session data → Grok 4.5) and the category-2
index's open question about whether telemetry-tuned models produce a durable
advantage.

## Surprises

1. **The flagship has the smallest window in its own lineup** (500k vs siblings' 1M)
   — capability tier and context tier are independent axes at xAI, and they chose
   capability.
2. A hermes-style per-family patch targets Grok in hermes' prompt appendices (grouped
   with GPT/Codex for execution-discipline failures) — a third-party read on its
   *behavioral* family resemblance: harnesses treat Grok as GPT-shaped.
3. **This report carried a wrong cutoff for 17 days** (caught 2026-08-17): "Feb 1,
   2026" is stated on xAI's overview page for *Grok 4.6* — the only cutoff sentence on
   the page — and was recorded here against 4.5. No first-party source states a 4.5
   cutoff at all. Retracted in frontmatter with the audit trail; the failure mode is
   reading a lineup page's lone spec sentence as applying to the row you came for.
4. **Newest models locked out of their own vendor's batch lane** (2026-08-17): the
   Batch API rejects grok-4.5 and grok-4.6 outright; the 20% discount covers only the
   older 4.3/4.20 line. Same shape as Moonshot (batch excludes K3) — batch support is
   trailing-edge at two vendors, presumably a capacity choice.

## Open questions

- Does Cursor-session training measurably improve performance *inside Cursor* vs
  other harnesses — the cleanest possible test of the category-1↔2 integration thesis,
  if anyone can run it?
- EU availability since launch? (Unchecked since 2026-07-28.)
