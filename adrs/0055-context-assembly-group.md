# ADR-0055 — the context-assembly group: context_retrieval + context_compaction

`decided: 2026-09-04` · `status: accepted`

## Decision

Category 2's `harness_features:` gains a new group and two keys, batched ADR-0050
style (one ADR = one group + its keys, canonical order stated once):

- **Group `context-assembly`** (`order: 52`; control-gates and operations shift to
  53/54, rendering-only). It formalizes the category's component #2
  (tool-taxonomy § 2, ADR-0021) — the component the index has called the
  contested ground of 2026 — which until today had registry coverage only via
  extension-points apertures (`skills`, `rules_files`).
- **`context_retrieval`** (closed-enum): how repo content reaches the prompt
  without the human adding it — `ranked-index` | `search-tool` | `delegated` |
  `model-driven`.
- **`context_compaction`** (closed-enum, list allowed for stacked mechanisms,
  primary first — the `memory_store` precedent): what happens at context
  pressure — `llm-summarize` | `prune` | `truncate`.

## Why now, and the two censuses

Both keys were blocked on issue #34 (`context_retrieval`'s discriminating value is
single-instance; `context_compaction` sat as issue #33's candidate under
value-scope counting). The 2026-09-04 key-scope decision unblocked them; a
same-day probe-pass at existing pins settled both columns to 12/12 (one honest
omit).

**`context_retrieval`** — the four-value spread from the aider deep-dive
(conclusion 17): `ranked-index` 1 (aider — tree-sitter symbol index, real
`nx.pagerank`, ranked definitions' source lines injected as a user message every
turn, measured 71% of the assembled prompt), `search-tool` 1 (warp — the index's
chain ends in a `{name, path}` tool result with zero context lines), `delegated`
1 (gemini-cli — read-only investigator subagent; its embeddings path is dead
code), `model-driven` 9. The probe-pass settled the last five cells — hermes-agent,
dsh, cline, continue (source at pins), claude-code (docs-route) — all
`model-driven`, which is itself the conclusion-17 finding restated as a column:
every 2025–26 tool-dispatch design retrieves by asking. Three single-instance
values stand under key-scope, and `ranked-index` may stay that way — the position
that discriminates is held by the set's oldest, most dormant tool. continue's
cell carries the column's strongest caveat: an embeddings-backed codebase tool is
real in shared core but flag-gated off and structurally unwired in the CLI.

**`context_compaction`** — the probe's surprise is near-universality with a stack
behind it: `llm-summarize` appears in all 11 settled cells; what discriminates is
what else stands beside it and whether it runs unasked. `prune` 4 (dsh; opencode
opt-in; hermes-agent shipped off; claude-code docs-route, first-line), `truncate`
3 — a value issue #33 proposed speculatively and the probe then instanced three
times over (gemini-cli's failed-summary fallback `CONTENT_TRUNCATED`; codex's
opt-in `token_budget` fresh-window reset; cline's rule-based fallback for
models its summarizer doesn't support). **No `none` instance exists** — every
settled harness compacts — so no such value is minted (issue #34: values are
minted at cell-set time, from verified instances). warp's cell is deliberately
unset: compaction is entirely server-driven and the server implementation is
absent from the clone by construction — omit-with-reason, the null is data.

One body correction fell out of the probe (dated in place): pi's "deleted, not
summarized" holds for what survives in visible history, but the summarizer's
input does sample tool results, truncated to 2,000 chars
(`core/compaction/utils.ts:89,144`).

## Argued and not admitted (with triggers)

- **`cache_discipline`** (issue #33's second candidate). Stays body-prose: dsh
  enforces prefix stability repo-wide, hermes measures the tension, aider fixed
  the collision by silently disabling per-query personalization — real instances
  of a *tension* (design-principles H5), but no comparable cell definition has
  emerged; the placement test keeps a finding without one in prose. Trigger: a
  second harness stating prefix stability as an enforced design constraint in a
  form a cell can transcribe.
- **A default-on/opt-in axis on `context_compaction`.** Half the finding, but it
  is per-mechanism, not per-tool (opencode's summarize is on while its prune is
  off) — a cell cannot carry it without a grammar; comments do. Trigger: the
  same species of grammar need arising on a second key (ADR-0050's cell-grammar
  precedent would then apply to both at once).
- **A `hybrid` retrieval value** for continue's dormant embeddings tool.
  Rejected: the cell reads the shipped surface at the pin (flag-gated off,
  unwired in the CLI); presence-in-core belongs to the comment. Trigger: the
  flag defaults on, or the CLI mounts it.

## Consequences

- Registry: one `groups:` entry, two `features:` entries; harness registry rows
  28 → 30 (header comment re-counted); matrices and registry render regenerate.
- Cells: 12 + 11 set with citations; warp's compaction cell an in-block
  omit-with-reason comment.
- `tools/2-harnesses/README.md`: 15 → 17 keys; the component-mapping sentence
  gains the two keys under context assembly — the component was the only one of
  the three with no assessed key of its own.
- Issue #33 closes (compaction admitted; cache discipline parked here with a
  trigger); issue #46 closes (this ADR is its item 1; ADR-0053/0054 items 2–3).
- No decoder needed: no prior prose used other names for these facts — the
  category README's § context-assembly analysis predates the keys and reads
  unchanged, now with a registry column to point at.
