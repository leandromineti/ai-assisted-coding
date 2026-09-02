# CLAUDE.md — how this repo works

`created: 2026-07-31`

A survey of AI-assisted coding tooling, organised as a **taxonomy of tool categories** with
**dated, evidence-linked** findings. The point is not to ship a product; it is to know things
that are true, and to be able to show why.

Read these three first. They are the constitution, and they outrank anything in this file:

| File | What it governs |
|---|---|
| [`docs/methodology.md`](docs/methodology.md) | the rules. Nine numbered, each scarred by a specific failure. Rule 1 (+1a evidence grades, **1b negative claims** — an absence is only as good as the surface you searched), rule 3 (generated indexes), rule 4 (traceable claims), rule 5 (preregistration + 5a–5f), rule 8 (docs/source/run) constrain nearly every task here |
| [`docs/tool-taxonomy.md`](docs/tool-taxonomy.md) | the categories, and what a category *test* is |
| [`docs/design-principles.md`](docs/design-principles.md) | the hypotheses, and the rule for revising them |

[`docs/conclusions.md`](docs/conclusions.md) holds the numbered **Conclusions** — the repo's actual
output (moved out of `README.md` 2026-08-26, ADR-0028; the README keeps the headline index). A
conclusion without a linked note is an assertion; a finding that changed no note is an anecdote
(rule 6). Add one there, then add its headline to `README.md`.

## Where things go

| Path | Contents | Hand-kept? |
|---|---|---|
| `tools/N-*/` | one report per tool, by taxonomy category. Template: `tools/_template-tool-report.md` — **except category 1**, which uses `tools/1-models/_template-model-report.md`: weights have no clone to pin, no source to trace, no drift to re-check, so the repo-shaped fields and sections don't apply | yes |
| `tools/N-*/README.md` | narrative front door per category: what the category *is*, seed inventory, and a **"What we assess here"** section (all six carry one since 2026-08-26) — the category's assessed block named with its key count and a date, why those keys discriminate *here*, the transcription fields, and links to the generated registry and matrix. Never copy the definitions in: the registry owns them (rule 3) | yes |
| `tools/candidates.md` | cross-category ledger of sighted-but-not-ingested tools — the pre-`stub` stage (candidate → stub → survey → deep-dive). Dated hand-typed stars are its documented exception | yes |
| `docs/` | the constitution (the three files above, moved from root 2026-08-26 by ADR-0026) plus general notes on the repo's structure, methodology, and ideas (ADR-0025; was `tools/cross-cutting/`) — the findings that span categories, [`metrics.md`](docs/metrics.md) (measurement vocabulary), and the feature taxonomy — prose in [`feature-taxonomy.md`](docs/feature-taxonomy.md), the registry itself in [`feature-taxonomy.yaml`](docs/feature-taxonomy.yaml) since ADR-0036, paired like `tool-taxonomy.{md,yaml}`; the feature matrices generate from the YAML, and feature keys are added there, nowhere else | yes |
| `references/papers/` | one note per **source read** (papers, benchmarks), each with its own `read_depth` | yes |
| `references/cards/` | one note per **vendor model card** read — a different schema (`models_covered`, `published`/`last_updated`, and a **required** `snapshot:` Wayback URL, because cards are rewritten in place). See [`references/README.md`](references/README.md) | yes |
| `comparisons/` | **generated** matrices — `tools.md`, `features.md`, `models.md`, `environments.md`, `benchmarks.md`, `feature-registry.md` (the feature taxonomy's YAML re-rendered as readable tables), `probes.md` (the contract sweep's classified evidence re-rendered, `scripts/build-probe-matrix.py`, since Phase 11). `vendors.md` was removed 2026-08-26 (ADR-0041): its one real signal — model makers ship harnesses for their own weights — is a sentence, and it lives in `docs/tool-taxonomy.md` § Maker span | **no — generated** |
| `experiments/NN-*/` | preregistered A/Bs: protocol, `log.md` appended live, artifacts | yes |
| `experiments/rig/` | the pinned container + hidden verifier both arms run against | yes |
| `probes/` | the API parameter-probe instrument (v3.0, since 2026-09-01): `harness/` (stdlib-only runner + 3 wire-family adapters + `models.yaml`/`prices.yaml`/`ceilings.yaml`/`sweep-stages.yaml`, all dated), declarative probe sets in `sets/`, `audit-evidence.py` (D-05's fail-closed privacy scanner, in the lint battery above), `PREREGISTRATION.md` (the rule-5 protocol + appended, dated Run log), `classified/` (hand-kept `overrides.yaml`; generated `contract-sweep.yaml`, rule 3), dated smoke/run artifacts. Front door: [`probes/README.md`](probes/README.md). `raw/` and `ledger.jsonl` are tracked by git since 2026-09-02 (Phase 11 plan 11-06, D-04's revisit gate — the owner's provisional 2026-09-01 decision was revisited and flipped) | yes |
| `upstream/` | cloned study copies. **Gitignored** — a manifest, not the code | n/a |
| `references/papers/pdf/` | cached papers. **Gitignored** — refetchable from each note's `arxiv`/`doi` | n/a |
| `scripts/` | the generators (`build-tool-index.py`, `build-refs-index.py`, `repo-facts.sh`), the taxonomy lint (`check-taxonomy.py`) — it checks; it writes nothing — and `build-db.py`, which builds the gitignored `comparisons/repo.db` for ad-hoc queries (`--query "SQL"`; a view over frontmatter, never authoritative, ADR-0035) | yes |
| `adrs/` | dated, immutable decision records for taxonomy/structure decisions. Living docs always speak the current state; ADRs hold how it was reached and the old→new decoders. Never edit an accepted ADR except `superseded-by`. See [`adrs/README.md`](adrs/README.md) | yes |
| `articles/` | public-facing drafts, one file per article, site-schema frontmatter. Drafted here so claims keep repo-relative links (rule 4 for prose); published to the personal site as a downstream copy. See [`articles/README.md`](articles/README.md) | yes |

**Never hand-edit anything in `comparisons/` or `references/index.md`.** Edit the frontmatter of the
note it summarises and re-run the generator. Hand-kept indexes drift and you find out when
they're already wrong (rule 3).

## The three operations

**Ingest a source.** Read it — actually read it. Write `references/papers/<year>-<name>.md` (year-first citekeys since 2026-08-18) from
[`references/papers/_template-paper-note.md`](references/papers/_template-paper-note.md), cache the PDF in `references/papers/pdf/`, set
`read_depth` honestly, fill `bears_on` and `verdict`. Then update whatever note or conclusion the
source actually touches, append a line to `references/log.md`, and re-run
`python3 scripts/build-refs-index.py`.

**Ingest a tool.** Clone into `upstream/`, run `scripts/repo-facts.sh` for the mechanical facts
(never hand-type stars or first-commit dates), write the report, re-run
`python3 scripts/build-tool-index.py`. Set a `harness_features:` key **only** when verified in source or
docs — omitted means "not checked", `false` means "checked and absent", and both are claims.

Two report-writing disciplines, both scars from the gsd-core v1.11.0 re-read (2026-08-21):

- **A count carries its measure.** At the re-read, three of four corrections to the deep-dive
  held *at its own pin* — a curated subset stated as a total, a figure no definition reproduced
  (candidate measures ranged 5–39), a total that depended on clone state. State the command or
  definition a count came from, or the next re-read cannot confront it — the enumerable cousin
  of "a citation is what makes a claim re-checkable".
- **Forward-looking claims are dated, falsifiable predictions.** The deep-dive's issue-counter
  forecast carried a number and a date, so the re-read could *score* it (landed within a day;
  ceiling mis-chosen). Write predictions that way on purpose, and score them at the next
  re-read — a free calibration instrument, the same epistemics this repo credits in tools
  that publish negative results about themselves.

**Lint.** Before committing:

```sh
python3 scripts/build-tool-index.py --check   # pinned commits still match clone HEADs
python3 scripts/build-refs-index.py --check   # frontmatter, unread-but-cited, dangling links
python3 scripts/check-taxonomy.py --check     # deny-listed synonyms, stale category names/numbering, unregistered vocabulary, unapplied ADR decoders
python3 probes/audit-evidence.py --check      # scans probes/raw/*.jsonl + ledger.jsonl for account-identifying leaks before they're committed
python3 probes/check-docs-claims.py --check   # docs-claims.yaml completeness, first-party sourcing, rule-1b searched surfaces
```

The fourth command is `probes/`'s own gate, D-05's fail-closed privacy scanner: exit 0
means clean, exit 1 means findings that block the commit, exit 2 means a bad
invocation. A finding is fixed in the evidence itself — repair or discard the offending
record and re-fire its cell — never by narrowing the scanner's denylist or patterns
(the same never-loosen-the-pattern discipline `check-taxonomy.py`'s deny-list
procedure below already models for a different lint). Since 2026-09-02,
`probes/raw/*.jsonl` and `probes/ledger.jsonl` are tracked by git (Phase 11 plan
11-06, D-04's revisit gate), so this scanner runs on every commit that touches them,
not just at the one-time evidence-commit decision.

The fifth command is `probes/docs-claims.yaml`'s own gate (Phase 11.1, D-03): exit 0
means clean, exit 1 means findings, exit 2 means a bad invocation. Like the fourth
command, a finding is fixed in the claims data, never by narrowing the validator.

For the two index generators (`build-tool-index.py`, `build-refs-index.py`), `--check`
distinguishes two conditions. **UNVERIFIABLE** (exit non-zero) means a pinned
commit no longer resolves — claims can't be checked against their source at all.
**behind** is not a failure, but it is not noise either: it is a work queue. Ask whether
the drift touches what the report claims and record the answer, dated, in the report —
**without moving the pin** (methodology rule 4b). ECC's 16-commit drift contained the
upstream bug fix that falsified a claim in its deep-dive.

The taxonomy lint (`check-taxonomy.py`) has different semantics: it reads
`docs/tool-taxonomy.yaml` and has no pins and no behind state. Exit 1 means findings to fix (or to deliberately
exempt); exit 0 prints a trailing `0 problem(s)`; exit 2 means a bad argument. Run
`python3 scripts/check-taxonomy.py --selftest` after touching `tool-taxonomy.yaml` or the
lint itself — it is the lint's permanent calibration (methodology rule 5d). `--selftest`
deliberately prints ERROR diagnostics from fixtures designed to fail, so its verdict is
the trailing `0 problem(s)` line and the exit code, never the absence of ERROR output.

Three green `--check` runs are not proof the repo's vocabulary is correct — the lint
enforces only what `tool-taxonomy.yaml` lists. `tool-taxonomy.yaml`'s own `split_meaning_terms`
records at least one sense (`stack`) no lint can judge, and a word inflection outside a
deny-listed entry is invisible to it (see the deny-list growth procedure below for a
worked example of exactly this gap).

**Growing the deny-list.** When you discover a new drift term:

1. Decide it's drift before denying anything. A word with legitimate non-taxonomy uses is
   not a deny-list candidate — record it instead as a `false_positive_notes` entry under
   the relevant term in `tool-taxonomy.yaml`. Precedent: the bare `kind` token is deliberately
   not denied (only the frontmatter-key form `` `kind:` `` is) because a bare-token entry
   would guarantee false positives — the reason this repo chose a deny-list over an
   allow-list in the first place.
2. To deny it: add the term as a string under the matching `terms[].deny_list` in
   `docs/tool-taxonomy.yaml`. That is the only file to edit — no Python change is required. Two
   mechanics to get right: matching is whole-token and case-insensitive with no stemming,
   so list every inflected form you mean to catch, and a longer word that merely contains
   an entry does not match; and position within the list doesn't matter, because the lint
   sorts entries longest-first when it builds its match pattern.
3. A legitimate compound use of a newly denied word goes under the same term's
   `deny_list_exempt_compounds`, each entry carrying `compound`, a `canonical_source`
   naming which already-canonical concept it refers to, and `known_sites`. `known_sites`
   file:line entries are re-derived by running the check, never hand-typed — the same
   discipline that forbids hand-typed stars and first-commit dates elsewhere in this file.
4. Re-run `python3 scripts/check-taxonomy.py --selftest`, then `--check`. New red findings
   are a work queue: fix the prose first, exempt only second and only with a written
   `canonical_source` — exemption is the cheapest way to turn a finding green and the
   easiest way to hollow the lint out.
5. Bump `checked:` in `tool-taxonomy.yaml` (dates on everything).
6. The one case that needs code: a genuinely new sort of exemption — a new
   `carve_outs[].id` — needs a matching predicate in `scripts/check-taxonomy.py`, or the
   lint refuses to run and says so. Deny-list entries, exempt compounds, and exempt paths
   never need code.

## The honesty columns

Two fields carry more weight than anything else here, and both exist because a confident-sounding
claim turned out to rest on nothing:

- **`depth`** on a tool report — `stub` (facts collected mechanically, nobody read the source) ·
  `survey` (used or skimmed) · `deep-dive` (the category's component decomposition
  actually traced, the report declaring which components — tool-taxonomy.md defines them for
  categories 2, 4, and 5, and category 3's (host · principal · working directory)
  live in its index with the three questions as the lens over them; tracing
  discipline per ADR-0021/0023, applied since 2026-08-25 — earlier deep-dives read
  under the two-part loop+context definition).
- **`read_depth`** on a ref note — `full` · `extract` (a tool answered questions against it) ·
  `abstract` · `unread`. **An `unread` source may not be cited anywhere outside `references/`**, and
  `--check` fails if it is. On 2026-07-31 two claims stated from extraction summaries were
  contradicted by the full PDFs, one of them backwards. That is what this field is for.

Downgrade either freely. Never upgrade one without doing the work.

## Experiments

Preregistered before any run (rule 5). `log.md` is appended **during** the run, never
reconstructed. Amendments are dated, appended, and labelled as pre- or post-run — the protocol
text above them is never edited. Results go below the untouched protocol. n=1 is a probe; say so.

Before running a comparison, two checks that exist because they were skipped once:

- **Does the instrument discriminate?** Not just fail closed — a baseline that saturates it means
  it cannot measure a difference (5d). Run the baseline arm first, as calibration.
- **Has the driver been smoke-tested end to end?** A harness can exit 0 having done nothing (5e).
  Read success from artifacts, never from exit status.

Both arms share one instrument, one model, one **declared network condition** (8a — declared,
enforced at the egress layer, probed, identical across arms; see
[`experiments/rig/README.md`](experiments/rig/README.md)).

## Conventions

- **Dates on everything.** Tool facts drift monthly; model pricing and specs drift faster.
  `checked:` / `read_at:` / `retrieved:` are load-bearing, not decoration.
- **Relative markdown links**, not wikilinks — they render on GitHub.
- **Issues are the backlog.** Propose the 1–3 strongest next moves; park the rest as GitHub
  issues rather than growing a TODO file.
- **Write as if public-facing, whatever the visibility.** No employer references, no pointers to
  private local files, no paths a reader can't resolve. Restate work-derived findings generically
  as personal experience with a rough date. (The GitHub repo's visibility has flipped before —
  most recently back to private on 2026-08-18 — and may flip again; this discipline is what
  makes that switch safe in either direction, so it holds regardless of current state.)
- Commits go straight to `main` (sole contributor, deliberate exception to branch-first).
