# probes/ — the wire-evidence pipeline

**Front door only — read `.planning/phases/09-harness-adapters/09-RESEARCH.md` and
`docs/methodology.md` for the full design and rationale.**

`probes/` is v3.0's API parameter-surface instrument: a small, stdlib-only harness
that fires declared HTTP probes against the 12 active tracked models across three
wire families, logs every request/response verbatim, and ledgers every dollar spent.
It mirrors this repo's existing registry-driven docs pipeline
(`docs/feature-taxonomy.yaml` → `comparisons/*.md`): a raw evidence stage, a
classified stage, and a generated matrix — this directory owns only the raw stage.

```
probes/raw/{vendor}.jsonl        one JSONL file per vendor — every request/response
                                  verbatim, written by probes/harness/runner.py
        ↓
probes/classified/*.yaml         Phase 11 — hand-classified contract sweep verdicts
                                  (rejected / accepted / echoed), cites probe_id
        ↓
comparisons/probes.md            Phase 13 — GENERATED probe matrix (rule 3: never
                                  hand-edited)
```

## Layout

| Path | Contents |
|---|---|
| `probes/harness/` | the runner, the stdlib HTTP client, the append-only ledger, and one adapter module per wire family (`probes/harness/adapters/`) |
| `probes/harness/models.yaml` | wire facts for all 12 active tracked models (D-01) — self-contained, never parses `tools/1-models/` prose at runtime |
| `probes/harness/prices.yaml` | per-token USD prices for the same 12 models, each row dated and sourced (D-02) |
| `probes/sets/*.yaml` | declarative probe-set files the runner consumes (D-03) |
| `probes/raw/{vendor}.jsonl` | append-only wire evidence, one file per vendor (D-08) |
| `probes/ledger.jsonl` | append-only spend log, one line per billed attempt (D-07) |

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

## Append-only rule

`probes/raw/*.jsonl` and `probes/ledger.jsonl` are append-only, same discipline as
`experiments/*/log.md`: one record per real HTTP response, written and flushed
during the run, never rewritten, reordered, deduplicated, or deleted afterward.
Superseded evidence stays visible rather than being cleaned up. No line in either
file may originate from anything other than a real HTTP response — no simulated,
hand-authored, back-filled, or replayed records.

**Evidence commit policy (provisional, 2026-09-01):** `probes/raw/` and
`probes/ledger.jsonl` are currently gitignored — the owner declined D-09's default
(commit raw evidence to the repo) for now, revisit planned at Phase 11 before the
contract sweep commits its evidence base. `probes/harness/` (code) and
`probes/sets/` (declarations) are unaffected and commit normally. See `.gitignore`
for the dated note.
