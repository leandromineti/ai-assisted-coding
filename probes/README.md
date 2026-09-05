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

Phase 12 adds a second, parallel pipeline over the SAME raw evidence stage — a behavioral
question ("does a repeated call vary, or match?") that the four-state contract
classification above cannot answer, since that classification only ever fires each cell
once:

```
probes/sets/behavioral/*.yaml    Phase 12 — hand-authored behavioral probe sets, one
                                  file per test family (D-09's `repeat` coordinate;
                                  runner.py reads only `probes:`)
        ↓
probes/raw/{vendor}.jsonl        the SAME raw evidence stage as above — a behavioral
                                  repeat is one more `probe_id` line among the contract
                                  sweep's, not a separate evidence file
        ↓
scripts/classify-behavioral.py   Phase 12 — reads every declared behavioral set +
                                  probes/raw/*.jsonl, groups repeat entries, reduces
                                  each group to a rate-with-count verdict against a
                                  fail-loud-cited expectation (--check/--selftest)
        ↓
probes/classified/behavioral.yaml  Phase 12 — GENERATED classified behavioral evidence
                                  (rule 3: never hand-edited; --check/--selftest).
                                  Rate-with-count schema, never a bare boolean
        ↓
scripts/build-behavioral-matrix.py  Phase 12 — reads probes/classified/behavioral.yaml
                                  alone and renders the matrix (--check/--selftest)
        ↓
comparisons/behavioral.md        Phase 12 — GENERATED behavioral matrix (rule 3: never
                                  hand-edited)
```

Both `scripts/classify-behavioral.py --check` and `scripts/build-behavioral-matrix.py
--check` are deliberately NOT in `CLAUDE.md`'s pre-commit battery — the same precedent
`scripts/build-docs-vs-wire.py`'s own entry below already records for itself and
`scripts/build-probe-matrix.py`: they are generator drift checks, run on demand, not on
every commit, and the absence is a design choice, not an oversight. What DOES gate a
commit touching this evidence, already in `CLAUDE.md`'s battery: `probes/audit-evidence.py
--check` (the privacy scanner) and `probes/check-docs-claims.py --check` (the claims
validator), both of which run over the extended evidence base this phase adds. This
decision is recorded here so a future session does not re-litigate it from scratch.

## Layout

| Path | Contents |
|---|---|
| `probes/harness/` | the runner (two probe-set grammars: `--set` for scalar parameter cells, `--content-block-set` for the image-input/cache-control content-block cells, MODAL-01, Phase 11 plan 11-03 — schema in `probes/inventory.yaml`, not restated here), the stdlib HTTP client, the append-only ledger, and one adapter module per wire family (`probes/harness/adapters/`) |
| `probes/harness/fixtures.py` | the pinned tiny-PNG test payload the content-block firing path sends (Phase 11 plan 11-03, MODAL-01) — `TINY_PNG_BASE64`, provenance-only `make_tiny_png()`, `--selftest` |
| `probes/harness/models.yaml` | wire facts for all 15 active tracked models (D-01; 12 at Phase 11, +3 on 2026-09-04 by issue #43's roster fork) — self-contained, never parses `tools/1-models/` prose at runtime |
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
| `probes/sets/behavioral/` | Phase 12 — hand-authored behavioral probe sets, one file per test family (`control-arm.yaml`, `seed-determinism.yaml`, `temp0-repeatability.yaml`, `stop-truncation.yaml`, `n-candidate-count.yaml`, `logprobs-reverify.yaml`, `service-tier-audit.yaml`, `docs-drift-annex.yaml`). Each carries four top-level keys: the runner's own `probes:` list (the only key `probes/harness/runner.py` reads — a `repeat: 1..N` entry field marks a probe as one repeat of a repeat-based cell, joined and reduced by `scripts/classify-behavioral.py` below; a non-repeated entry has no `repeat` key at all), plus `expectations:`, `skips:`, and `cited_cells:` (Phase 12 plan 12-05 — an audit row resolved directly against an already-fired raw record by `probe_id`, no `probes:` entry required), which only `scripts/classify-behavioral.py` reads. Every `expectations:`/`skips:` citation carries exactly one of three prefixes: `docs-claims:<param>/<vendor>` (resolves against `probes/docs-claims.yaml`), `phase11:<probe_id>` (resolves against `probes/classified/contract-sweep.yaml`), or `prereg:<section anchor text>` (resolves against `probes/PREREGISTRATION.md`'s own Phase 12 section) — `prereg:` is accepted ONLY on a `design: control` row, since a calibration finding has no vendor doc or Phase 11 cell to cite, only the preregistration's own stated calibration design |
| `scripts/classify-behavioral.py` | Phase 12 — reads every declared behavioral set plus `probes/raw/*.jsonl`, recomputes each declared entry's exact `probe_id` via `probes/harness/runner.py`'s own `probe_id()`/`apply_omit()` (never reimplemented), groups repeat entries, and reduces each group to a rate-with-count verdict against its declared expectation (`--check`/`--selftest`). Writes `probes/classified/behavioral.yaml`. Its citation gate is fail-loud: an expected value that resolves to nothing aborts generation — a behavioral row asserted from memory can never be generated into the classified file at all |
| `probes/classified/behavioral.yaml` | Phase 12 — GENERATED classified behavioral evidence (rule 3: **never hand-edited**; `--check`/`--selftest`). Rate-with-count schema (e.g. `rate: "0/4"`, `rate_pct`, `distinct_outputs`) — no verdict, echo-relation, presence, or truncation-verdict field anywhere in the file is a bare boolean |
| `scripts/build-behavioral-matrix.py` | Phase 12 — reads `probes/classified/behavioral.yaml` alone and renders `comparisons/behavioral.md` (rule 3: never hand-edited; `--check`/`--selftest`), one section per requirement with its own design-dispatched column layout |
| `comparisons/behavioral.md` | Phase 12 — GENERATED behavioral matrix (rule 3: never hand-edited) |

The two new drift checks' deliberate absence from the pre-commit battery, and what
gates a commit over this evidence instead, is recorded once above (the behavioral
pipeline diagram) rather than repeated per row.

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

## Adding a model to the roster

`added: 2026-09-05` — written from the first roster change after v3.0 shipped
(issue #43 phase 2: gpt-6-astra + gemini-3-8-flash + claude-fable-5-1, commits
31f37f5 + 579f997). Neither explorer of the pipeline found a runbook before that
fork; this is the dependency-ordered procedure it proved, so the next roster
change starts here instead of re-deriving it.

1. **Working tree first, no commit.** `models.yaml` (+row per model — the slug MUST
   equal the report filename stem in `tools/1-models/`, since `check-probe-drift.py`
   joins on exactly that; resolve the `api_model_id` with the zero-cost ListModels
   call, see § Wire questions #3) and `prices.yaml` (+row, same slug — **nothing
   cross-checks this file**: a missing row silently yields `cost=None` and no ledger
   line). Slug-keyed `vendor_overrides`/`probe_value_overrides` in `inventory.yaml`
   where the family thinking fragment doesn't fit (the Claude adaptive shape is the
   worked example). A same-vendor addition needs no new key, raw file, or
   docs-claims entries (claims are per-vendor); a NEW vendor needs all three.
2. **Regenerate and re-partition.** `inventory-to-sets.py`, then update every
   `expect_cells:` in `sweep-stages.yaml` from the actual regenerated counts;
   `runner.py --check-stages` + `inventory-to-sets.py --check`/`--selftest` clean.
3. **Pre-flight.** `--dry-run` per stage: verify the new bodies (max-tokens field
   name, nesting, thinking fragment) and that every EXISTING model's probe_id
   resolves verbatim in the raw seen-set — the resume proof; the ledger alone
   under-proves it, since rejected cells bill nothing and never appear there.
4. **Preregister, then a blocking spend sign-off.** Append a dated section to
   `PREREGISTRATION.md` pinning the regenerated cell counts and the envelope;
   commit it ALONE (the roster stays uncommitted, keeping the battery green on
   main — `check-probe-drift`'s model domain is `models.yaml`, so a committed
   roster without cells is 18 findings per 3 models). The owner's line lands
   verbatim in the Run log before any cell fires.
5. **Fire contract stages in order** (1–2 are the zero-cost + calibration read —
   confirm each new model's thinking fragment behaves as its docs predict before
   the paid bulk). Capability-named 400s the classifier can't match get dated
   `classified/overrides.yaml` entries, never a loosened matcher.
6. **Hand-extend the behavioral sets** (models are hand-enumerated there — known
   debt): dump each file's top-level key layout before anchor-inserting (one file
   carries a `cited_cells:` section between `probes:` and `expectations:`), mirror
   the closest sibling's full field set from a parsed dict, and cite skips only
   with resolvable tokens — a `phase11:`-style contract citation cannot be written
   before that contract cell exists, which is what forces contract-before-behavioral.
7. **Classify, derive, then write the report cells.** Both classifiers + the three
   matrix generators, each `--check` byte-stable; then derive the expected head per
   (key, model) by importing `check-probe-drift.py`'s own `DERIVE_FUNCS` and write
   the OBSERVED cells to match — never hand-compose a verdict the checker will
   re-derive.
8. **Close.** Full battery + closing ledger read into the Run log; one commit
   carries roster, sets, evidence, classified, matrices, and report cells together
   — green at commit.

## The DeepSeek row

`tools/1-models/deepseek-v4.md` is one report but names two API-callable model ids
(`deepseek-v4-pro`, `deepseek-v4-flash`). `probes/harness/models.yaml` represents
DeepSeek with a single row using `deepseek-v4-pro` — the report's headline/primary
pricing figures — with `deepseek-v4-flash` named as an available sibling that is not
separately tracked. This is what kept the registry at 12 rows matching "12 active
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
