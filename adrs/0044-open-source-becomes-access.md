# ADR-0044 — the `open_source:` boolean becomes the `access:` enum, registered across all six categories

`decided: 2026-08-26` · status: **accepted**

## Decision

The top-level report frontmatter key `open_source: <true|false>` is replaced by
**`access: <open-source | closed-source | open-weights>`** across all 45 tool reports and both
templates, and is **registered** in `docs/feature-taxonomy.yaml` → `transcription_fields:`
with `applies_to: [1, 2, 3, 4, 5, 6]`, `value_type: closed-enum`,
`verification: source-or-docs`, `rendered_in: [tools.md, features.md]`.

The field answers exactly one question — **what of the subject can the public obtain and
inspect** — and it is a **pair** with `license:`, which answers *under what terms*.

Three consequences follow, and all three are the point:

1. `access` renders as its own column beside `License` in `comparisons/tools.md` and in all
   five `comparisons/features.md` tables.
2. `comparisons/tools.md`'s **Version read** column loses the openness literal it used to
   substitute for a version, and means one thing again.
3. Validation: `check_access` in `scripts/build-tool-index.py` — the repo's **fifth
   cell-value check**, and the first that is *required on every report in every category*.

Registered in `docs/tool-taxonomy.yaml` → `schema_renames` with `status: applied`, so LINT-05
fails any surviving `open_source:` key under `tools/`.

## Context — the boolean carried four meanings

`open_source:` was on all 45 reports and both templates. It was also the **only** universal
frontmatter field never registered as a transcription field: undocumented, unrendered as
itself, unvalidated. What it actually held varied by report, and every variance was rescued by
a YAML comment that `yaml.safe_load` drops before any matrix renders:

| Report | `license` | was | the comment's meaning |
|---|---|---|---|
| pilot-shell | proprietary | `false` | non-OSI terms — but the source *is* public, and pinned here at `c8c8243` |
| modal | Apache-2.0 | `false` | the product is closed; only the client SDK is open |
| daytona | AGPL-3.0 | `false` | AGPL at the freeze pin, closed *today* — a time split |
| claude-code | proprietary | `false` | a public repo that is issues + distribution, not source |
| qwen3-coder-next | Apache-2.0 | `true` | **weights** are published; no source ever was |

Four meanings and a category error. The generator was already working around it —
`build-tool-index.py`'s pin check carries the comment "a recorded pin with a clone present is
checked regardless of `open_source`", which is a script apologising for its own schema.

The category-1 case is the sharpest: **weights are not source**. `open_source: true` on
qwen3-coder-next asserted something about source code that was never published.

## Why `access`, and why these three values

The field is about **reach**, not terms. Under that reading the ecosystem's third state,
*source-available*, is not a value at all — it is a **cell in a cross product**, read off the
pair:

| | OSI `license` | non-OSI / proprietary `license` |
|---|---|---|
| `access: open-source` | open source (codex, mem0) | **source-available** (pilot-shell) |
| `access: closed-source` | the license covers an accessory (modal) | closed (claude-code) |

That is what makes it a duality rather than two columns saying the same thing twice, and it is
why **pilot-shell flips** (`false` → `open-source`): the old field meant OSI-ness, which is the
license's job; the new one means reach, and pilot-shell's source is public.

Two rules the definition must carry, because both were previously only in comments:

- **The subject is the thing the report is about, as shipped** — never an accessory. Modal is
  `closed-source` though its client SDK is Apache-2.0; claude-code is `closed-source` though
  its repo is public.
- **The value is dated like every transcribed fact.** Daytona is `closed-source` *today* and
  AGPL-3.0 at its freeze pin — the closure event the report exists to document.

### Rejected alternatives

- **A pure boolean** (`source_public: true|false`). Rejected on the owner's objection, which is
  correct: the model equivalent of open source is **open weights**, and a boolean named for
  source cannot say that without lying about what was published.
- **`openness:`** as the key. Rejected — it names a *judgment* where the field holds a *fact*.
- **`access:` collides in prose** with type **1b — model access** (`docs/tool-taxonomy.md`,
  `tools/1-models/README.md`, the model template's axis row). Accepted rather than avoided:
  that type is always written "model access" or "1b", no `terms:` entry exists for it, and the
  bare-word alternatives (`distribution:` — rule 8b's distributed artifact, category-6
  distribution, 5f's statistical distributions) collide worse.
- **`open-source` on a proprietary EULA reads wrong** to anyone importing the OSI sense of the
  phrase. This is a real cost of naming values after the ecosystem's words rather than after
  the artifact (`source` / `weights` / `closed`). Mitigated structurally: `license` is the
  adjacent cell in both matrices, and the index prose says to read them together.

## The category-1 wrinkle, recorded rather than hidden

For all eleven models read so far, `access` is **fully derivable from `release_mode:`** —
`api-only` ⇔ `closed-source`, `open-weights`/`both` ⇔ `open-weights`, 11 of 11. Today the
column adds no information in category 1, and rule 3's instinct is to not hand-keep what is
derivable.

It is kept anyway, for two stated reasons: it makes **one comparable statement across all six
categories**, and it can express a state `release_mode` cannot — a model whose **training
source** is public (the OLMo shape) reads `open-source`, where `release_mode` can only reach
`open-weights`. Zero instances so far. Zeros are honest, and this one is written into the
field's registry note so a future reader can confront it rather than rediscover it.

## Consequences

- **`Version read` says one thing again.** The column rendered `closed source` for eight of
  eleven category-1 rows — an openness fact in a column named for versions, for subjects that
  have no clone at all. Those cells now read `—`.
- **`closed_source_pin_note` survives with a narrower job.** Daytona's one-report exception
  (CR-01, 2026-08-21) used to *substitute* `commit` for the openness literal; it now
  *annotates* the version — `v0.189.0-9-g4ee2c6365 (pre-closure pin)` — so a reader meeting a
  closed subject with a readable pin still learns why.
- **A wrong registry definition surfaced by being rendered.** `version:` was defined as
  "omitted for closed source". Both halves were false: a closed product can have a pinned open
  client (modal), and a subject with no clone can still report a version — claude-code's cell
  is `claude --version`, self-reported and machine-checked by nothing, which its own field
  comment says and the index prose now repeats. The error was invisible while the column hid
  every closed row behind a literal.
- **Six category READMEs bump their transcription-field counts** (9→10, 11→12, 7→8, 8→9 ×3).
- **`access` joins `build-db.py`'s `SCALARS`**, so it is a real column rather than JSON in
  `extra` — queryable beside `license`, which is the whole point of a pair.
- **The decoder is honest about being unusual.** Every other `schema_renames` entry says
  "values are unchanged — purely a key rename". This one changes the values too, and says so;
  reading it as a spelling change would lose the reason it exists.
