# ADR-0037 — `knowledge_cutoff` becomes structured, with two dates and a basis

`decided: 2026-08-26` · status: **superseded in part by
[ADR-0038](0038-cutoff-single-date.md) (2026-08-26): the two-date clause only — the
field now carries one date, the training-data limit, with any finer vendor figure in
`note`. The mapping, `basis`, the null-when-not-stated constraint and the cell-value
check all stand**

## Decision

```yaml
knowledge_cutoff:
  knowledge: 2025-02        # YYYY-MM or YYYY-MM-DD; null when no date is published
  training_data: 2025-07    # null unless the vendor publishes it separately
  basis: vendor-stated      # vendor-stated | inherited | not-stated | retracted
  note: "…"                 # required
```

**Two dates, one field.** Vendors publish two facts — Anthropic ships
`reliableKnowledgeCutoff` and `trainingDataCutoff` separately and defines them
differently (knowledge = the date through which the model's knowledge is most extensive;
training data = the broader range of data used), and Haiku 4.5 has them **five months
apart**. They stay sub-keys rather than becoming two fields: the pair describes one thing,
training recency, and a separate `training_data_cutoff` column would be null for every
vendor that publishes only one.

**`basis` is what keeps the date honest**, and `inherited` is why it is an enum rather
than a boolean: Gemini 3.1 Pro's card publishes no cutoff and delegates its *training
dataset* to the Gemini 3 Pro card, so January 2025 is neither stated-for-this-model nor
absent. `knowledge` **must** be null when `basis` is `not-stated` or `retracted` — the
constraint that stops a date the vendor does not stand behind from rendering as fact.

## Why

The trigger was an owner query — *order the model cutoffs* — run against the export the
day it was built. It returned:

```
Feb 16, 2026 · Feb 2025 · Jan 2026 · January 2025 · May 2026 · RETRACTED… · not stated ×4
```

Prose in three date formats, sorted alphabetically. Six of eleven values were not dates at
all but findings about their absence, which is exactly why the field stayed free-text when
this was argued two commits earlier — and the reason that argument was incomplete: the
absences needed a *place*, not a text field. `basis` gives them one, and the prose survives
in `note`.

It now sorts:

| | cutoff | training | basis |
|---|---|---|---|
| claude-opus-5 | 2026-05 | 2026-05 | vendor-stated |
| gpt-5-6-sol | 2026-02-16 | — | vendor-stated |
| claude-fable-5 · claude-sonnet-5 | 2026-01 | 2026-01 | vendor-stated |
| claude-haiku-4-5 | 2025-02 | **2025-07** | vendor-stated |
| gemini-3-1-pro | 2025-01 | 2025-01 | **inherited** |
| deepseek-v4 · glm-5.3 · kimi-k3 · qwen3-coder-next | — | — | not-stated |
| grok-4-5 | — | — | **retracted** |

## Consequences

Third cell-value check (`check_cutoff`, after `check_pricing`), enforcing: `basis` in the
enum, dates matching `YYYY-MM(-DD)`, `knowledge` null exactly when the basis says the
vendor stands behind nothing, and `note` present. Verified by two negative tests, restored
after each — `basis: retracted` with a date set → exit 1 *"a date the vendor does not stand
behind"*; `knowledge: "May 2026"` → exit 1 naming the required format.

`models.md` renders the date first, then the divergent training-data date when it differs,
then the basis, then the note verbatim — so the column leads with what sorts.

This also answers the "two cutoffs in one field?" question raised earlier the same day, and
supersedes the recommendation then given (leave it free-text, record a strain, revisit if a
consumer appears). The consumer appeared within the hour. The strain note was never
written, so nothing needs unwinding.

## Boundary

No decoder: `knowledge_cutoff` keeps its id, home, and meaning; only its shape changed, and
every prior value survives verbatim inside `note`. Migration was mechanical across 11
reports; the `note` strings were carried across unedited.

`build-db.py` needed one fix the migration exposed: YAML parses a full date (`2026-02-16`)
into a `date` object, which can now sit inside a structured value, and `json.dumps` refuses
it — `default=str`.
