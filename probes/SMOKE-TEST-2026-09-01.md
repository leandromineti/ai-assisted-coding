# Smoke Test — 2026-09-01

**Rule 5e artifact (`docs/methodology.md` § 5e): a harness can exit 0 having done no
work. This document is the proof it did not — every claim below is read from a named
field of a record on disk, cited by `probe_id`, never from a process exit code or the
absence of an exception.**

Five records exist on disk after Phase 9: three live smoke probes (one per wire
family, `probes/sets/smoke.yaml`) and two zero-cost contract probes
(`probes/sets/contract-zero-cost.yaml`). Organized against Phase 9's five roadmap
success criteria (`.planning/ROADMAP.md`), verbatim section per criterion.

## Success Criterion 1 — harness exists, one runner, no vendor SDK imports

`probes/harness/` contains three adapter modules (`adapters/anthropic_messages.py`,
`adapters/openai_compat.py`, `adapters/gemini.py`), one runner entry point
(`runner.py`), and the shared `client.py`/`ledger.py`. No vendor SDK import exists
anywhere under `probes/harness/` — `grep -rniE "^\s*(import|from)\s+(anthropic|openai|google\.generativeai|genai)" probes/harness/`
returns nothing (checked this run). All three wire families dispatched through this
one runner in this smoke test: `probe_id`s `claude-haiku-4-5--baseline--none--default--3cb1ffa7`
(`anthropic_messages`), `kimi-k3--baseline--none--default--b3540b5c` (`openai_compat`),
`gemini-3-1-pro--baseline--none--default--7694eaf8` (`gemini`).

## Success Criterion 2 — resumability demonstrated on disk

Line counts of every file under `probes/raw/` and `probes/ledger.jsonl`, recorded
BEFORE re-running both probe sets unchanged, and AFTER:

| File | Before | After |
|---|---|---|
| `probes/raw/anthropic.jsonl` | 3 | 3 |
| `probes/raw/gemini.jsonl` | 1 | 1 |
| `probes/raw/kimi.jsonl` | 1 | 1 |
| `probes/ledger.jsonl` | 3 | 3 |

Identical on both sides. `python3 probes/harness/runner.py --set probes/sets/smoke.yaml`
printed `SKIP` for all three declared entries; `python3 probes/harness/runner.py --set
probes/sets/contract-zero-cost.yaml` printed `SKIP` for both — every previously-logged
`probe_id` resume-skipped, zero new lines anywhere. This is the on-disk evidence for
HARN-02 / roadmap success criterion 2, not a prose assertion.

## Success Criterion 3 — ledger from real usage fields, under $8, no auth material

See "Ledger reading" below for the full accounting. Headline: **$0.000584 total**,
computed from each response's own `usage`/`usageMetadata` object, never a pre-call
estimate — well under the $8 roadmap ceiling and the plan's own $1 sub-budget for this
task. Auth-hygiene check: for each of the 8 `PERSONAL_*` key values currently loaded
from `~/.secrets/model-probes.env` (name-only referenced here, values never printed),
a shell loop grepped every file under `probes/raw/` and `probes/ledger.jsonl` for the
literal value — **zero matches across 8 keys × 4 files**, run this session
(2026-09-01) immediately after all five records were written.

## Success Criterion 4 — the retry path, OBSERVED vs unit-verified

Roadmap criterion 4 has two halves and this smoke run only wire-exercises one of them.

**OBSERVED (wire-exercised this run):** every non-429 4xx recorded is retried zero
times and produces a verdict.

- `claude-haiku-4-5--max-tokens--omitted--default--869449db` — status 400, `retries: 0`,
  `terminal: "verdict"`, response body verbatim: `{"type":"error","error":{"type":"invalid_request_error","message":"max_tokens: Field required"}}`.
- `claude-haiku-4-5--max-tokens--invalid-negative--default--e4e3d0dc` — status 400,
  `retries: 0`, `terminal: "verdict"`, response body verbatim:
  `{"type":"error","error":{"type":"invalid_request_error","message":"max_tokens: must be greater than or equal to 0"}}`.

Both attempts arrays contain exactly one entry each (`n: 1`), confirming no retry loop
ever engaged for a non-429 4xx — the field, not an inference from an absent second
attempt entry in a longer array.

**NOT observed this run, unit-verified only:** a 429/5xx retried with backoff honoring
`Retry-After`, producing no contract verdict for that attempt. No live 429 or 5xx was
encountered by any of the five probes fired this phase (all five terminal statuses are
200 or 400 — see the field-by-field reads below; none is 429 or ≥500). Provoking one
for real would mean deliberately hammering a vendor endpoint, which the plan's own
flagged assumptions rule out at zero-cost-probe scale. This half rests entirely on
`client.py --selftest`, 21/21 cases passing this session (`09-02-SUMMARY.md`'s own
case count, re-run and confirmed here): a 429 with a numeric `Retry-After` retries
for exactly that wait; a 429 with lowercase `retry-after` casing retries identically
(case-insensitive header read); a 429 with no `Retry-After` retries with positive
backoff capped at 60s; a 429 with an unparseable `Retry-After` value falls back to
backoff rather than raising; `500`/`502`/`503`/`529` are all classified retryable;
a retryable status at the final permitted attempt is `exhausted` whether or not
`Retry-After` was present; and Anthropic's spend-cap 429 signal (`error.details.error_code:
"enforced_spend_limit_reached"`) is classified `fatal` on the first attempt AND
mid-run, without spending the retry budget. This is unit-level proof that the
classification logic is correct, not proof that a live 429/5xx was ever seen and
handled end-to-end through the runner's JSONL-writing path. If a 429 or 5xx is
encountered live during a future phase's sweep, it belongs in the OBSERVED column
of that phase's own artifact, not backfilled here.

## Success Criterion 5 — field-by-field reads, all five records

Per rule 5e: a 200 status is never read as "the probe succeeded" on its own. Every
record below is read for its actual returned content, its usage object's token counts
by kind, the price row applied, and the computed dollars.

### `claude-haiku-4-5--baseline--none--default--3cb1ffa7` (anthropic_messages, live)

- Endpoint actually used: `https://api.anthropic.com/v1/messages`
- Terminal HTTP status: `200`; attempts: 1; terminal action: `verdict`
- `response.content[0].text` (the actual returned text): `"hello"`
- `usage.input_tokens`: `15`; `usage.output_tokens`: `4`;
  `usage.cache_creation_input_tokens`: `0`; `usage.cache_read_input_tokens`: `0`
- Price row applied (`prices.yaml`, `claude-haiku-4-5`, retrieved 2026-09-01):
  `$1`/MTok in, `$5`/MTok out
- Computed dollars: `$0.000035`

### `kimi-k3--baseline--none--default--b3540b5c` (openai_compat, live)

- Endpoint actually used: `https://api.moonshot.ai/v1/chat/completions`
- Terminal HTTP status: `200`; attempts: 1; terminal action: `verdict`
- `response.choices[0].message.content` (the actual returned text): `""` (empty
  string) — `finish_reason: "length"`. `response.choices[0].message.reasoning_content`
  carries `"The user has asked me to reply with exactly one word: hello"` (13 reasoning
  tokens, cut off mid-thought). A 200 status here is NOT evidence the probe "worked" in
  the sense of producing assistant text — it is evidence the harness's full pipeline
  (request build → send → parse → JSONL write → ledger) executed correctly against a
  real response whose CONTENT happens to be empty. This is read here exactly per rule
  5e's warning: the field says what happened, not a green light.
- `usage.prompt_tokens`: `93`; `usage.completion_tokens`: `16` (the whole
  `max_tokens` budget — matches the empty-content/`finish_reason: length` observation);
  `usage.completion_tokens_details.reasoning_tokens`: `13`
- Price row applied (`prices.yaml`, `kimi-k3`, retrieved 2026-08-17): `$3`/MTok in,
  `$15`/MTok out
- Computed dollars: `$0.000519`, **recomputed by hand from the raw counts**: `(93 * 3 +
  16 * 15) / 1_000_000 = (279 + 240) / 1_000_000 = 0.000519` — matches the ledger line
  exactly, proving the ledger is auditable from tokens + price row, not a black box.

### `gemini-3-1-pro--baseline--none--default--7694eaf8` (gemini, live)

- Endpoint actually used:
  `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent`
- Terminal HTTP status: `200`; attempts: 1; terminal action: `verdict`
- `response.candidates[0].content.parts[0].text` (the actual returned text): `"hello"`
- `usage.input_tokens` (`usageMetadata.promptTokenCount`): `9`;
  `usage.output_tokens` (`usageMetadata.candidatesTokenCount`): `1`;
  `usage.reasoning_tokens` (`usageMetadata.thoughtsTokenCount`): `191`;
  `usage.cached_tokens` (`usageMetadata.cachedContentTokenCount`): absent (`null`)
- Price row applied (`prices.yaml`, `gemini-3-1-pro`, retrieved 2026-08-17): `$2`/MTok
  in, `$12`/MTok out
- Computed dollars: `$0.00003`
- **This is the corrected, second fire of this probe entry** — see "Gemini's actual
  API model id" below for what the discarded first attempt showed and why it was
  discarded rather than kept as a superseded-but-visible record.

### `claude-haiku-4-5--max-tokens--omitted--default--869449db` (anthropic_messages, zero-cost contract)

- Endpoint actually used: `https://api.anthropic.com/v1/messages`
- Terminal HTTP status: `400`; attempts: 1; terminal action: `verdict`
- `response.error.type`: `"invalid_request_error"`; `response.error.message`:
  `"max_tokens: Field required"`
- `usage`: `{}` (no usage object on a rejected request — no tokens billed)
- Cost: `null` (never generated, nothing to price)

### `claude-haiku-4-5--max-tokens--invalid-negative--default--e4e3d0dc` (anthropic_messages, zero-cost contract)

- Endpoint actually used: `https://api.anthropic.com/v1/messages`
- Terminal HTTP status: `400`; attempts: 1; terminal action: `verdict`
- `response.error.type`: `"invalid_request_error"`; `response.error.message`:
  `"max_tokens: must be greater than or equal to 0"`
- `usage`: `{}`; cost: `null`

## The two open wire questions this plan settles

**Kimi K3's actual API host — SETTLED, 2026-09-01.** `probe_id
kimi-k3--baseline--none--default--b3540b5c` fired against the primary candidate
(`https://api.moonshot.ai/v1/chat/completions`, the more specific of RESEARCH.md's
two contested citations) and answered directly with HTTP 200 on the first attempt —
no DNS failure, no connection failure, no 4xx that would have triggered the fallback
rule. The fallback host (`https://api.kimi.ai/v1`) was never tried live; it remains an
untested candidate, not a confirmed-wrong one. Evidence grade: **OBSERVED** (this
repo's vocabulary, `docs/methodology.md` § 1a — live behavior of a running
installation, dated) — upgrades RESEARCH.md's two conflicting **CITED** (vendor-docs
testimony) sources. `probes/harness/models.yaml`'s Kimi row comment now records this,
dated 2026-09-01, and marks the fallback URL as documented-but-unneeded rather than
promoting or deleting it.

**Whether Anthropic's Messages API requires `max_tokens` — SETTLED, 2026-09-01,
REQUIRED.** `probe_id claude-haiku-4-5--max-tokens--omitted--default--869449db`
omitted the field via the runner's new `omit` key and received HTTP 400,
`error.type: "invalid_request_error"`, `error.message: "max_tokens: Field required"`.
RESEARCH.md flagged this as unconfirmed ("did not confirm whether it appears in the
schema's `required` array") and recommended sending it unconditionally regardless —
that recommendation was already the harness's default behavior and stays correct.
Evidence grade: **OBSERVED**.

## Two further wire facts, settled or partially settled in the course of firing these probes

**Gemini's actual API model id — a genuine contradiction of RESEARCH.md, settled
2026-09-01.** RESEARCH.md's § Google — Gemini generateContent family states the API
path segment is "the bare id without that suffix," i.e. `gemini-3.1-pro` (stripping
the report frontmatter's "(Preview)" annotation). **The first live fire against that
bare id returned HTTP 404**: `{"error":{"code":404,"message":"models/gemini-3.1-pro
is not found for API version v1beta, or is not supported for generateContent...",
"status":"NOT_FOUND"}}`. A zero-cost `GET /v1beta/models` ListModels call (no billing,
read-only) listed the model as `models/gemini-3.1-pro-preview` — the "(Preview)"
suffix IS part of the API path segment for this still-Preview model, contradicting
RESEARCH.md's assumption. `probes/harness/models.yaml`'s Gemini row now carries
`api_model_id: gemini-3.1-pro-preview`, dated, with the contradiction recorded inline.
The erroneous 404 record was discarded before commit (uncommitted, gitignored
`probes/raw/`, same task, no downstream citations — same precedent as plan 09-01's
discarded leaked-header record) rather than kept as superseded-but-visible evidence,
because it reflected the harness's own wrong configuration, not an independently
interesting vendor behavior. Evidence grade: **OBSERVED**.

**`thoughtsTokenCount` presence on `gemini-3.1-pro` specifically — OBSERVED present,
both fires.** RESEARCH.md flagged this field as "possibly absent even with thinking
enabled on some models" and asked for confirmation on this model specifically. Both
the discarded 404-then-retried first fire (max_tokens=16, before the model-id fix) and
the corrected second fire (max_tokens=200) show `usageMetadata.thoughtsTokenCount`
present and non-zero (`12` and `191` respectively) — the field was never absent on
this model in either observation this session. What WAS absent on the first,
under-budgeted fire was a different field: `usageMetadata.candidatesTokenCount` — RFC
absent (not present as `0`) when the entire `maxOutputTokens` budget was consumed by
thinking before any candidate text was generated (`content: {}`, `finishReason:
"MAX_TOKENS"`). This is a real, if narrower, version of RESEARCH.md's concern: not
"the reasoning-token field can vanish" but "the OUTPUT-token field can vanish under a
too-small budget on an always-on-reasoning model" (the report's own
`reasoning_type: always-on` frontmatter flag for this model). `probes/sets/smoke.yaml`
now carries a dated comment recording this and the max_tokens increase (16→200) it
motivated.

**Whether any `Retry-After` header was seen — NOT OBSERVED (negative claim, rule 1b).**
The surface searched: the response headers of all five records collected in this
phase (`response_headers` field of each record's final attempt), which is the entire
set of live HTTP responses the harness has ever received as of this run. None carries
a `retry-after` or `Retry-After` key (case checked both ways). No 429 or 5xx status was
returned by any vendor to any of the five probes fired. This is recorded as **not
observed** — the surface that could have shown a `Retry-After` header (a real 429/5xx
response) never occurred in this run — not as "confirmed absent," which would overstate
what a clean run of small, cheap, well-formed (or deliberately-rejected-pre-generation)
requests can show.

## Ledger reading

`python3 probes/harness/ledger.py --totals`, run immediately after all five records
were written:

```
global total: $0.000584
  anthropic: $0.000035  (input_tokens=15, output_tokens=4)
  kimi:      $0.000519  (input_tokens=93, output_tokens=16, reasoning_tokens=13)
  gemini:    $0.00003   (input_tokens=9,  output_tokens=1,  reasoning_tokens=191)
```

Every figure above is read from `probes/ledger.jsonl`'s `cost_usd` field, itself
computed by `ledger.cost_usd()` from each response's own `usage`/`usageMetadata`
object at write time — never a pre-call estimate. The zero-cost contract probes
(`claude-haiku-4-5--max-tokens--omitted...` and `...--invalid-negative...`) both
returned `null` for `cost_usd` and were never written to the ledger (only billed
attempts get a ledger line — see `runner.py`'s `if cost is not None:` guard), matching
their design intent.

**Hand recomputation, per the plan's own "count carries its measure" discipline**
(`CLAUDE.md`): the Kimi line, `(93 input_tokens * $3/MTok + 16 output_tokens *
$15/MTok) / 1,000,000 = (279 + 240) / 1,000,000 = $0.000519` — matches the ledger's
recorded `cost_usd` exactly. The ledger is auditable from raw token counts and the
price row it cites, not a black box.

**Auth-hygiene check result:** ran a shell loop over all 8 `PERSONAL_*` key values
loaded from `~/.secrets/model-probes.env` against every file under `probes/raw/` and
`probes/ledger.jsonl` — **zero matches**. Result and the check itself are recorded
here; the values themselves are never reproduced in this document or anywhere else.

## What this smoke test does NOT cover

No sweep spend occurred (Phase 10 onward). No parameter beyond the baseline/`omit`/
invalid-`max_tokens` axes was probed. No image-input modality was tested. No repeat-
based behavioral verification (seed determinism, temperature-0 repeatability) ran —
that is Phase 12's job, gated on Phase 11's contract classifications existing first.
The 429/5xx retry-with-backoff half of HARN-04 stays unit-verified until a live
429/5xx is actually encountered by a future phase's real sweep traffic.
