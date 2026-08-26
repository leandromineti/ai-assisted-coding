# ADR-0046 — `release_mode` is retired; `released` becomes the structured `release_date`

`decided: 2026-08-26` · status: **accepted**

## Decision

Two changes to how a model's release is recorded, decided together because they are the
same question asked twice:

1. **`release_mode:` is retired** — removed from all 11 category-1 reports, the model
   template, `docs/feature-taxonomy.yaml` and `scripts/build-db.py`. No `schema_renames`
   decoder: there is nothing to translate it *to*.
2. **`released:` becomes `release_date:`**, and its free-text value becomes a mapping —
   `date` (the typed fact) + `stage` + `note` — following the `knowledge_cutoff` precedent
   (ADR-0037/0039, where `value_type` types the fact and `renders_note` carries the prose).
   Registered as a `schema_renames` decoder with `status: applied`.

## Why `release_mode` goes

It was raised as *"seems redundant with `access`"*. It is worse than redundant.

**It was already wrong on two of eleven rows**, and its own reports carried the
contradiction:

| Report | `release_mode` said | its own `pricing.note` said |
|---|---|---|
| kimi-k3 | `open-weights` | "first-party API $3 / $15 per MTok flat (platform.kimi.ai)" |
| qwen3-coder-next | `open-weights` | "first-party Model Studio (Singapore + Frankfurt, USD)" |

The field's own definition read *"api-only \| open-weights \| both — verified on both
surfaces before 'both' is claimed"*. A first-party API and published weights **is** `both`,
by that definition, for both models.

Correct them and the field collapses: `api-only` ×8, `both` ×3, `open-weights` ×**0** —
isomorphic to `access` (`api-only` ⇔ `closed-source`, `both` ⇔ `open-weights`), with the one
value that could have distinguished the two fields used by nothing. The unique bit it was
supposed to carry — *does a first-party API exist* — is already carried by `pricing`, whose
base-rate rule requires a first-party surface. That is precisely how the error was found.

**And nothing rendered it.** `rendered_in: []` meant the field appeared in no matrix, so two
wrong cells sat in the repo unread. The lesson generalises past this field: a transcribed
fact that no generated surface shows is a fact nobody re-reads.

The corrections are recorded here rather than applied to a field that then disappears —
fixing a value in the same commit that deletes it would leave no trace that it had been
wrong.

## Why `released` gets restructured rather than renamed

`release_date` was the requested name, and a bare rename would have been the third time this
field's name promised more than its value delivers. The history is on the record: `ga_date`
became `released` on **2026-08-17** exactly because the value is not a date, and the model
template still says so.

The values prove it. Of eleven:

- **kimi-k3** has **no first-party calendar date at all** — "the launch blog prints NO
  calendar date"
- **deepseek-v4** has **two** — "Preview 2026-04-24 → GA 2026-08-13"
- **grok-4-5** is **month-level** — "July 2026, no stage vocabulary"
- **four** use no stage vocabulary whatsoever, and **one** (gpt-5-6-sol) has a stage its
  vendor's own two surfaces disagree about on the same day

Structure is what lets the name promise a date honestly. `date` is **first availability**
(the earliest first-party date, or null); `stage` is the vendor's own word at that date, with
two controlled markers — `not-stated` when the vendor uses no stage vocabulary, `ambiguous`
when its surfaces disagree; `note` is required and carries the rest: a later stage
transition, why a date is month-level, why a date is null, the surface checked and when.

Nothing was invented in the conversion. Every date, stage and caveat was already in the old
free-text value, and kimi-k3's date stayed **null** rather than borrowing the third-party
"~2026-07-16" or the HF initial commit this report has never recorded — its note names
reading that commit as the open route to a first-party date.

## Consequences

- **A sixth cell-value check**, `check_release_date`, with one asymmetric rule: `date: null`
  requires `stage` to be `not-stated` or `ambiguous`. A null date beside a confident "GA"
  would be a report claiming the vendor announced a general release on no day at all.
  Calibrated against five fabricated failure modes and three valid shapes.
- **The category-1 axis "Release mode & access routes (1b)" is untouched.** It names a
  tool-taxonomy *type*, not this field, and it long predates it. The collision of words is
  noted so a future reader does not read the axis as a dangling reference.
- **A dated prediction was restated, not dropped.** `glm-5.3.md` predicted a
  `zai-org/GLM-5.3` HF repo by 2026-08-31 and said to "flip `release_mode` to `both`" if it
  lands. The prediction now scores against `access` flipping to `open-weights` — same claim,
  same date, same falsifier, with the restatement dated in place.
- **ADR-0045 is not edited.** Written an hour earlier, it lists `release_mode` and `released`
  among category 1's Identity group. That was true when written, ADRs are immutable, and this
  record is the decoder — which is the whole reason the rule exists.
- **`docs/feature-taxonomy.md`'s `renders_note` count moves from two to three.** `pricing`,
  `knowledge_cutoff`, and now `release_date` — the prose named `released` as an example of a
  field with caveats "the matrix must not show", and that is no longer true of it.
