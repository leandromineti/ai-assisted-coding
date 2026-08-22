# ADR-0022 — Repo-voice prose in `refs/` is sweepable; decoders relocate to the ADR index

`decided: 2026-08-22` · status: **accepted**

## Decision

Two revisions to how the vocabulary sweep boundary and its decoders are carried:

- **`refs/` repo-voice prose is sweepable.** ADR-0015's sweep excluded `refs/` entirely,
  on the rationale that source quotes legitimately use their authors' vocabulary. That
  rationale covers quotes — it never covered the repo's *own* sentences inside ref
  notes ("this repo's layer-2 premise", a verdict field that flows into the generated
  index). The boundary is revised: **author quotes and reported content stay in period
  vocabulary; repo-voice prose (verdicts, `bears_on` commentary, the note's own
  analysis) is current-state text and is swept.** `refs/` stays out of the lint's reach
  (`skip_entirely`) because no mechanical check can split quote from repo voice — the
  sweep is manual and dated, and this record is its evidence.
- **The concrete decoders move to `adrs/README.md`.** taxonomy.md's lead-in carried
  the two decoders (pre-2026-08-18 numbering → ADR-0007's mapping; pre-2026-08-22
  "category 5" ambiguity → ADR-0020's memory-vs-extensions split). They relocate to
  the ADR index — the document whose stated job is "the ADR trail is the decoder" —
  leaving taxonomy.md a single line above its footnote block.

## The sweep executed with this decision (2026-08-22)

- `notes/cross-cutting/feature-taxonomy.md`: ten layer-N sites in YAML comments and
  `note:`/`definition:` strings, previously invisible to the lint via code-context
  carve-outs. The ADR-0007 → ADR-0020 double decode was applied per referent:
  layer-5-as-memory → category 5; layer-5-as-hooks and layer-5-as-rules-file-artifacts
  → **category 6**. `comparisons/` regenerated.
- refs repo-voice: four sites in three notes (`2024-swe-agent` verdict + one body
  line, `2024-humanevalcomm`, `2026-from-prompt-to-process`). `refs/index.md`
  regenerated. Author-quoted vocabulary untouched.

## What stays in period vocabulary, and why

ADR bodies (immutable after acceptance), experiment protocol text and `log.md` files
(methodology rule 5: appended live, never reconstructed), `refs/log.md` (append-only
reading log), git history, and old URLs. These are permanent carriers of superseded
numbering by design — which is why the decoders survive as living pointers in
`adrs/README.md` rather than being deleted with the sweep.
