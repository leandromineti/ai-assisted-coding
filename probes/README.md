# probes/ — the wire-evidence pipeline

**Front door only — read `.planning/phases/09-harness-adapters/09-RESEARCH.md` and
`docs/methodology.md` for the full design and rationale.**

`probes/` is v3.0's API parameter-surface instrument: a small harness — stdlib-only on
the wire transport/retry path (`probes/harness/client.py`, no vendor SDK, no
third-party HTTP or retry library) — that fires declared HTTP probes against the 12
active tracked models across three wire families, logs every request/response
verbatim, and ledgers every dollar spent. Config/probe-declaration parsing
(`models.yaml`, `prices.yaml`, `ceilings.yaml`, `probes/sets/*.yaml`) is a scoped,
documented exception: `runner.py` imports PyYAML (WR-01, phase-09 code review
2026-09-01) — that dependency must be installed in the environment this runs in.
It mirrors this repo's existing registry-driven docs pipeline
(`docs/feature-taxonomy.yaml` → `comparisons/*.md`): a raw evidence stage, a
classified stage, and a generated matrix — this directory owns only the raw stage.

```
probes/inventory.yaml            Phase 10 — the parameter registry (D-01); the
                                  generator INPUT, never fired directly
        ↓
probes/inventory-to-sets.py      Phase 10 — expands the registry into declared probe
                                  sets: firing scope, mode-cell expansion, content-
                                  block routing (--check/--selftest)
        ↓
probes/sets/generated/*.yaml     Phase 10 — GENERATED probe-set declarations (rule 3:
                                  never hand-edited; drift-checked against the
                                  registry). Two grammars, two runner.py flags:
                                  contract-sweep.yaml (`probes:`, --set) and
                                  content-blocks.yaml (`content_block_probes:`,
                                  --content-block-set, MODAL-01, Phase 11) — the
                                  runner refuses each grammar under the other
                                  flag loudly, exit 2
        ↓
probes/raw/{vendor}.jsonl        one JSONL file per vendor — every request/response
                                  verbatim, written by probes/harness/runner.py
        ↓
scripts/classify-probes.py       Phase 11 — reads probes/raw/*.jsonl + this
                                  directory's own overrides.yaml, joins them
                                  against every declared cell, and emits the
                                  four-state contract classification
        ↓
probes/classified/*.yaml         Phase 11 — GENERATED classified evidence (rule 3:
                                  never hand-edited; --check/--selftest). Cites
                                  probe_id for every fired row. Hand-kept input:
                                  probes/classified/overrides.yaml (D-08)
        ↓
scripts/build-probe-matrix.py    Phase 11 — reads probes/classified/*.yaml alone
                                  and renders the matrix (--check/--selftest)
        ↓
comparisons/probes.md            Phase 11 — GENERATED probe matrix (rule 3: never
                                  hand-edited)
```

Schemas for `scripts/classify-probes.py` and `scripts/build-probe-matrix.py` live in the
scripts themselves and in `probes/classified/*.yaml`'s own comments — not restated here.

## Layout

| Path | Contents |
|---|---|
| `probes/harness/` | the runner (two probe-set grammars: `--set` for scalar parameter cells, `--content-block-set` for the image-input/cache-control content-block cells, MODAL-01, Phase 11 plan 11-03 — schema in `probes/inventory.yaml`, not restated here), the stdlib HTTP client, the append-only ledger, and one adapter module per wire family (`probes/harness/adapters/`) |
| `probes/harness/fixtures.py` | the pinned tiny-PNG test payload the content-block firing path sends (Phase 11 plan 11-03, MODAL-01) — `TINY_PNG_BASE64`, provenance-only `make_tiny_png()`, `--selftest` |
| `probes/harness/models.yaml` | wire facts for all 12 active tracked models (D-01) — self-contained, never parses `tools/1-models/` prose at runtime |
| `probes/harness/prices.yaml` | per-token USD prices for the same 12 models, each row dated and sourced (D-02) |
| `probes/inventory.yaml` | the parameter registry (Phase 10, D-01) — one row per parameter or content-block, each carrying `source:`/`retrieved:`; a GENERATOR INPUT, never fired directly |
| `probes/inventory-to-sets.py` | the registry -> probe-set generator (Phase 10) — reads `inventory.yaml` + `harness/models.yaml`, writes `sets/generated/*.yaml`; `--check` (drift + registry validators) and `--selftest` (embedded fixtures) |
| `probes/sets/generated/` | GENERATED probe-set declarations (rule 3: **never hand-edited** — same discipline `comparisons/` carries elsewhere in this repo). `contract-sweep.yaml` (scalar parameter probes, runner.py's `probes:` grammar), `content-blocks.yaml` (image/cache-control rows, deliberately keyed `content_block_probes:` so the runner refuses it, D-12), `skipped-cells.yaml` (every declared skip with its reason, D-11) |
| `probes/sets/*.yaml` (hand-authored) | declarative probe-set files the runner consumes directly (D-03) — distinct from the generated sets above |
| `probes/SWEEP-DESIGN.md` | the contract sweep's design (Phase 10): probe firing order, a cell count derived from the generator's own printed summary, per-vendor dollar envelopes, and dated Phase-11 handoffs — NOT the rule-5 preregistration, which is authored at Phase 11 start. Its two dated 2026-09-01 falsifiable predictions are scored in an appended § Scoring section |
| `probes/PREREGISTRATION.md` | the rule-5 preregistration (Phase 11): spend sign-off, falsification criteria, the preregistered execution path, and the append-only Run log — every dated entry from the tracer cell through the final evidence-commit decision |
| `probes/raw/{vendor}.jsonl` | append-only wire evidence, one file per vendor (D-08) — tracked by git since 2026-09-02 (Phase 11 plan 11-06, D-04's revisit gate) |
| `probes/ledger.jsonl` | append-only spend log, one line per billed attempt (D-07) — tracked by git since 2026-09-02, same gate |
| `probes/audit-evidence.py` | D-05's fail-closed privacy scanner — a per-vendor `DENYLIST_FIELD_NAMES` (each entry annotated observed-live-with-vendor-and-date or documented-guess-with-searched-surface) plus pattern rules; non-empty `--check` findings block an evidence commit. In `CLAUDE.md`'s pre-commit lint battery |
| `probes/classified/overrides.yaml` | hand-kept, dated hand-override entries (D-08) — probe_id + date + reason, applied last and deterministically by `scripts/classify-probes.py`; never edits to the generated classified YAML |
| `probes/sweep-stages.yaml` | the firing-stage declarations `runner.py --stage N` reads (Phase 11 plan 11-02) — the machine-readable form of SWEEP-DESIGN.md § Probe ordering |
| `probes/docs-claims.yaml` | Phase 11.1, D-02 — the first-party vendor-documentation claims registry: one `sources:` entry per vendor docs page fetched and archived, one `claims:` entry per (`inventory.yaml` row x in-scope vendor) pair. **Hand-kept, explicitly NOT generated and NOT an extension of `probes/inventory.yaml`** — rule 3 does not apply (it transcribes external references; nothing in-repo regenerates it) |
| `probes/check-docs-claims.py` | Phase 11.1, D-03 — `docs-claims.yaml`'s fail-closed validator (`--check`/`--selftest`): completeness (every row x vendor pair present), first-party sourcing (DOCP-03), rule-1b searched-surface requirements. In `CLAUDE.md`'s pre-commit lint battery |
| `scripts/build-docs-vs-wire.py` | Phase 11.1, D-04 — the docs-vs-wire confrontation generator (`--check`/`--selftest`): reads `probes/docs-claims.yaml` (the claims) and `probes/classified/contract-sweep.yaml` (Phase 11's wire evidence) — plus `probes/harness/models.yaml` and `probes/inventory.yaml` for model-column and group-section order only, never a second hand-maintained list — and writes `comparisons/docs-vs-wire.md` (rule 3: never hand-edited). Its `--check` is deliberately NOT in `CLAUDE.md`'s pre-commit battery — same precedent as `scripts/build-probe-matrix.py`'s own drift check, run on demand rather than on every commit; the absence is a design choice, not an oversight |

## DOCP-05 — the claims-before-generator ordering

2026-09-02. The claims registry's first commit, `11691d5` (2026-09-02T18:50:56+00:00,
`feat(11.1-01): docs-claims schema, validator, and one live-archived Anthropic claim
(D-02/D-03)`), is strictly earlier than — and a different commit from — the
docs-vs-wire confrontation generator's first commit, `c0dbfe6`
(2026-09-02T20:15:01+00:00, `feat(11.1-04): docs-vs-wire generator, closed verdict
vocabulary + anti-overclaiming (DOCP-04)`). Read directly from `git log --reverse --
probes/docs-claims.yaml` and `git log --reverse -- scripts/build-docs-vs-wire.py
comparisons/docs-vs-wire.md`, never asserted or manufactured. This is the only
mechanical evidence that the 408-claim registry was recorded as a prior rather than
reverse-engineered from the confrontation (D-06): for Phase 12's not-yet-fired
behavioral runs, every claim already existed as a genuine expected value before any
wire evidence for it exists; for Phase 11's already-fired 727-cell evidence, the
confrontation in `comparisons/docs-vs-wire.md` is post-hoc and labelled as such in
the artifact's own limitation note. Of the 612 rendered `(param, model)` pairs, the
generator's own printed summary reports 79 `docs-contradicted`, 54
`docs-corroborated`, 151 `docs-undecidable`, 324 `docs-untested` (includes every
excluded-inventory-row x model pair, which has a claim but never a wire cell), and 4
`docs-silent`.

## The DeepSeek row

`tools/1-models/deepseek-v4.md` is one report but names two API-callable model ids
(`deepseek-v4-pro`, `deepseek-v4-flash`). `probes/harness/models.yaml` represents
DeepSeek with a single row using `deepseek-v4-pro` — the report's headline/primary
pricing figures — with `deepseek-v4-flash` named as an available sibling that is not
separately tracked. This is what keeps the registry at 12 rows matching "12 active
models" rather than silently becoming 13.

## Wire questions — settled by plan 09-03's smoke test

Full field-by-field evidence: [`SMOKE-TEST-2026-09-01.md`](SMOKE-TEST-2026-09-01.md).

1. **Kimi K3's actual API host — SETTLED 2026-09-01: `api.moonshot.ai`.** The primary
   candidate answered directly with HTTP 200 on the first live attempt (`probe_id
   kimi-k3--baseline--none--default--b3540b5c`); the fallback (`api.kimi.ai`) was
   never needed and stays an untested, documented candidate in `models.yaml`.
2. **Whether Anthropic's `max_tokens` is required on the Messages API — SETTLED
   2026-09-01: yes, required.** A live probe that deliberately omits the field via
   the runner's `omit` key received HTTP 400, `"max_tokens: Field required"`
   (`probe_id claude-haiku-4-5--max-tokens--omitted--default--869449db`).
3. **Gemini's actual API model id — a contradiction of the milestone research,
   settled 2026-09-01: `gemini-3.1-pro-preview`, not the bare `gemini-3.1-pro`.** The
   bare id 404s; a zero-cost ListModels call confirmed the Preview suffix is part of
   the API path segment for this still-Preview model. `models.yaml`'s Gemini row now
   carries the corrected id, dated.
4. **Whether `gemini-3.1-pro`'s `thoughtsTokenCount` field is ever absent —
   OBSERVED present on both live fires this session.** What DID go absent under a
   too-small `max_tokens` budget was `candidatesTokenCount` (the output-token
   field), when the model's always-on reasoning consumed the whole budget before any
   output text — see the artifact for the full read.
5. **Whether a `Retry-After` header was ever seen — NOT OBSERVED, not confirmed
   absent (rule 1b).** No 429/5xx occurred against any of the five probes fired this
   phase; the 429/5xx retry-with-backoff half of HARN-04 stays unit-verified only
   (`client.py --selftest`) until a live rate-limit response is actually encountered.
6. **Content-block cells' `max_tokens` — closed 2026-09-01, Phase 11 plan 11-03
   (not the 09-03 smoke test above): each `content-blocks.yaml` entry now carries
   its own per-model `max_tokens`,** the same registry-driven value the scalar
   cells use (`gemini-3-1-pro`'s 200-token override reaches its image cell too) —
   schema in `probes/inventory.yaml`, not restated here.

## Append-only rule

`probes/raw/*.jsonl` and `probes/ledger.jsonl` are append-only, same discipline as
`experiments/*/log.md`: one record per real HTTP response, written and flushed
during the run, never rewritten, reordered, deduplicated, or deleted afterward.
Superseded evidence stays visible rather than being cleaned up. No line in either
file may originate from anything other than a real HTTP response — no simulated,
hand-authored, back-filled, or replayed records.

**Evidence commit policy (decided 2026-09-02):** `probes/raw/` and
`probes/ledger.jsonl` are tracked by git — the owner's provisional 2026-09-01
decision to gitignore them was revisited at Phase 11 (D-04's revisit gate) and
flipped, conditional on `probes/audit-evidence.py --check` passing clean over the
complete 8-vendor evidence base, which it does. `probes/harness/` (code) and
`probes/sets/` (declarations) were never affected and always commit normally. See
`.gitignore` and `probes/PREREGISTRATION.md`'s Run log for the dated record.
