# CLAUDE.md — how this repo works

`created: 2026-07-31`

A survey of AI-assisted coding tooling, organised as a **taxonomy of tool categories** with
**dated, evidence-linked** findings. The point is not to ship a product; it is to know things
that are true, and to be able to show why.

Read these three first. They are the constitution, and they outrank anything in this file:

| File | What it governs |
|---|---|
| [`methodology.md`](methodology.md) | the rules. Nine numbered, each scarred by a specific failure. Rule 3 (generated indexes), rule 4 (traceable claims), rule 5 (preregistration + 5a–5f), rule 8 (docs/source/run) constrain nearly every task here |
| [`taxonomy.md`](taxonomy.md) | the categories, and what a category *test* is |
| [`design-principles.md`](design-principles.md) | the hypotheses, and the rule for revising them |

`README.md` holds the numbered **Conclusions** — the repo's actual output. A conclusion without a
linked note is an assertion; a finding that changed no note is an anecdote (rule 6).

## Where things go

| Path | Contents | Hand-kept? |
|---|---|---|
| `notes/0N-*/` | one report per tool, by taxonomy category. Template: `notes/_template-tool-report.md` | yes |
| `notes/0N-*/index.md` | narrative front door per category: what the category *is*, seed inventory | yes |
| `notes/candidates.md` | cross-category ledger of sighted-but-not-ingested tools — the pre-`stub` stage (candidate → stub → survey → deep-dive). Dated hand-typed stars are its documented exception | yes |
| `notes/cross-cutting/` | findings that span categories, plus [`metrics.md`](notes/cross-cutting/metrics.md) (measurement vocabulary) and [`feature-taxonomy.md`](notes/cross-cutting/feature-taxonomy.md) — the registry the feature matrices generate from (ADR-0010–0014); add feature keys there, nowhere else | yes |
| `refs/` | one note per **source read** (papers, benchmarks). See [`refs/README.md`](refs/README.md) | notes yes, index no |
| `comparisons/` | **generated** matrices — `tools.md`, `features.md`, `models.md`, `environments.md`, `vendors.md`, `benchmarks.md` | **no — generated** |
| `experiments/NN-*/` | preregistered A/Bs: protocol, `log.md` appended live, artifacts | yes |
| `experiments/rig/` | the pinned container + hidden verifier both arms run against | yes |
| `upstream/` | cloned study copies. **Gitignored** — a manifest, not the code | n/a |
| `refs/pdf/` | cached papers. **Gitignored** — refetchable from each note's `arxiv`/`doi` | n/a |
| `scripts/` | the generators (`build-tool-index.py`, `build-refs-index.py`, `repo-facts.sh`) plus the taxonomy lint (`check-taxonomy.py`) — it checks; it writes nothing | yes |
| `adrs/` | dated, immutable decision records for taxonomy/structure decisions. Living docs always speak the current state; ADRs hold how it was reached and the old→new decoders. Never edit an accepted ADR except `superseded-by`. See [`adrs/README.md`](adrs/README.md) | yes |
| `articles/` | public-facing drafts, one file per article, site-schema frontmatter. Drafted here so claims keep repo-relative links (rule 4 for prose); published to the personal site as a downstream copy. See [`articles/README.md`](articles/README.md) | yes |

**Never hand-edit anything in `comparisons/` or `refs/index.md`.** Edit the frontmatter of the
note it summarises and re-run the generator. Hand-kept indexes drift and you find out when
they're already wrong (rule 3).

## The three operations

**Ingest a source.** Read it — actually read it. Write `refs/<year>-<name>.md` (year-first citekeys since 2026-08-18) from
[`refs/_template-ref-note.md`](refs/_template-ref-note.md), cache the PDF in `refs/pdf/`, set
`read_depth` honestly, fill `bears_on` and `verdict`. Then update whatever note or conclusion the
source actually touches, append a line to `refs/log.md`, and re-run
`python3 scripts/build-refs-index.py`.

**Ingest a tool.** Clone into `upstream/`, run `scripts/repo-facts.sh` for the mechanical facts
(never hand-type stars or first-commit dates), write the report, re-run
`python3 scripts/build-tool-index.py`. Set a `features:` key **only** when verified in source or
docs — omitted means "not checked", `false` means "checked and absent", and both are claims.

**Lint.** Before committing:

```sh
python3 scripts/build-tool-index.py --check   # pinned commits still match clone HEADs
python3 scripts/build-refs-index.py --check   # frontmatter, unread-but-cited, dangling links
python3 scripts/check-taxonomy.py --check     # deny-listed synonyms, stale category names/numbering, unregistered vocabulary, unapplied ADR decoders
```

For the two index generators (`build-tool-index.py`, `build-refs-index.py`), `--check`
distinguishes two conditions. **UNVERIFIABLE** (exit non-zero) means a pinned
commit no longer resolves — claims can't be checked against their source at all.
**behind** is not a failure, but it is not noise either: it is a work queue. Ask whether
the drift touches what the report claims and record the answer, dated, in the report —
**without moving the pin** (methodology rule 4b). ECC's 16-commit drift contained the
upstream bug fix that falsified a claim in its deep-dive.

The taxonomy lint (`check-taxonomy.py`) has different semantics: it reads `taxonomy.yaml`
and has no pins and no behind state. Exit 1 means findings to fix (or to deliberately
exempt); exit 0 prints a trailing `0 problem(s)`; exit 2 means a bad argument. Run
`python3 scripts/check-taxonomy.py --selftest` after touching `taxonomy.yaml` or the
lint itself — it is the lint's permanent calibration (methodology rule 5d). `--selftest`
deliberately prints ERROR diagnostics from fixtures designed to fail, so its verdict is
the trailing `0 problem(s)` line and the exit code, never the absence of ERROR output.

Three green `--check` runs are not proof the repo's vocabulary is correct — the lint
enforces only what `taxonomy.yaml` lists. `taxonomy.yaml`'s own `split_meaning_terms`
records at least one sense (`stack`) no lint can judge, and a word inflection outside a
deny-listed entry is invisible to it (see the deny-list growth procedure below for a
worked example of exactly this gap).

**Growing the deny-list.** When you discover a new drift term:

1. Decide it's drift before denying anything. A word with legitimate non-taxonomy uses is
   not a deny-list candidate — record it instead as a `false_positive_notes` entry under
   the relevant term in `taxonomy.yaml`. Precedent: the bare `kind` token is deliberately
   not denied (only the frontmatter-key form `` `kind:` `` is) because a bare-token entry
   would guarantee false positives — the reason this repo chose a deny-list over an
   allow-list in the first place.
2. To deny it: add the term as a string under the matching `terms[].deny_list` in
   `taxonomy.yaml`. That is the only file to edit — no Python change is required. Two
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
5. Bump `checked:` in `taxonomy.yaml` (dates on everything).
6. The one case that needs code: a genuinely new sort of exemption — a new
   `carve_outs[].id` — needs a matching predicate in `scripts/check-taxonomy.py`, or the
   lint refuses to run and says so. Deny-list entries, exempt compounds, and exempt paths
   never need code.

## The honesty columns

Two fields carry more weight than anything else here, and both exist because a confident-sounding
claim turned out to rest on nothing:

- **`depth`** on a tool report — `stub` (facts collected mechanically, nobody read the source) ·
  `survey` (used or skimmed) · `deep-dive` (agent loop and context assembly actually traced).
- **`read_depth`** on a ref note — `full` · `extract` (a tool answered questions against it) ·
  `abstract` · `unread`. **An `unread` source may not be cited anywhere outside `refs/`**, and
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
