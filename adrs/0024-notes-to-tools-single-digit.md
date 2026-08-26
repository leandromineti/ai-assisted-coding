# ADR-0024 — `notes/` becomes `tools/`; category directories drop the leading zero

`decided: 2026-08-26` · status: **accepted**

## Decision

Two path renames, one commit, no semantic change:

- The reports directory `notes/` renames to **`tools/`** — named for what it holds
  (tool reports, the candidates ledger, the cross-cutting findings, the templates).
- The six category directories drop the zero-padding: `01-models` → **`1-models`**,
  `02-harnesses` → **`2-harnesses`**, `03-execution-environments` →
  **`3-execution-environments`**, `04-workflow-frameworks` →
  **`4-workflow-frameworks`**, `05-memory` → **`5-memory`**, `06-extensions` →
  **`6-extensions`**.

Category numbers, names, report frontmatter, and the two registries are untouched —
this is a storage-path decision, not a taxonomy decision.

## Why

Owner decision (2026-08-26), closing a session arc that repeatedly reorganized the
rendered surfaces around the category order (tools.md subsections, feature-registry
sections): the directory name `notes/` described the *form* of the contents while
every consumer treats them as the repo's tool database; and the zero-padded prefixes
implied a two-digit category space the taxonomy doesn't have (six categories, and
ADR-0002's bucket logic makes growth deliberate and rare). Single digits make the
directory listing read exactly like the taxonomy: `1-models` … `6-extensions`.

Lexicographic ordering is preserved for up to nine categories; a hypothetical
category 10 would sort wrong, and whoever adds it inherits this note as the warning.

## The decoder

Anything dated before **2026-08-26** cites the old paths. The mapping is mechanical:

| Old | New |
|---|---|
| `notes/<file>` | `tools/<file>` |
| `notes/0N-<name>/…` | `tools/N-<name>/…` |

## Boundary — what was rewritten and what deliberately was not

Living documents, scripts, `taxonomy.yaml` (including re-derived `known_sites`
paths), and generated matrices were rewritten/regenerated in the rename commit.
Immutable records keep their period paths and read under the decoder above, per the
same boundary ADR-0015's "pre-sweep-material" carve-out states: ADR bodies
(0001–0023), preregistered experiment protocol text and `log.md` entries, run
artifacts, published downstream article copies, git history, and GitHub issue text.
One recorded exception: `adrs/README.md`'s hand-kept index rows had their inline
paths updated so links resolve — the index is a living doc; the ADR bodies it links
to are the unedited record.
