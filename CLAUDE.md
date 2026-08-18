# CLAUDE.md — how this repo works

`created: 2026-07-31`

A survey of AI-assisted coding tooling, organised as a **layered taxonomy** with **dated,
evidence-linked** findings. The point is not to ship a product; it is to know things that are
true, and to be able to show why.

Read these three first. They are the constitution, and they outrank anything in this file:

| File | What it governs |
|---|---|
| [`methodology.md`](methodology.md) | the rules. Nine numbered, each scarred by a specific failure. Rule 3 (generated indexes), rule 4 (traceable claims), rule 5 (preregistration + 5a–5f), rule 8 (docs/source/run) constrain nearly every task here |
| [`taxonomy.md`](taxonomy.md) | the layers, and what a layer *test* is |
| [`design-principles.md`](design-principles.md) | the hypotheses, and the rule for revising them |

`README.md` holds the numbered **Conclusions** — the repo's actual output. A conclusion without a
linked note is an assertion; a finding that changed no note is an anecdote (rule 6).

## Where things go

| Path | Contents | Hand-kept? |
|---|---|---|
| `notes/0N-*/` | one report per tool, by taxonomy layer. Template: `notes/_template-tool-report.md` | yes |
| `notes/0N-*/index.md` | narrative front door per layer: what the layer *is*, seed inventory | yes |
| `notes/cross-cutting/` | findings that span layers, plus [`metrics.md`](notes/cross-cutting/metrics.md) — the measurement vocabulary | yes |
| `refs/` | one note per **source read** (papers, benchmarks). See [`refs/README.md`](refs/README.md) | notes yes, index no |
| `comparisons/` | **generated** matrices — `tools.md`, `features.md`, `models.md`, `environments.md`, `vendors.md`, `benchmarks.md` | **no — generated** |
| `experiments/NN-*/` | preregistered A/Bs: protocol, `log.md` appended live, artifacts | yes |
| `experiments/rig/` | the pinned container + hidden verifier both arms run against | yes |
| `upstream/` | cloned study copies. **Gitignored** — a manifest, not the code | n/a |
| `refs/pdf/` | cached papers. **Gitignored** — refetchable from each note's `arxiv`/`doi` | n/a |
| `scripts/` | the generators. `build-tool-index.py`, `build-refs-index.py`, `repo-facts.sh` | yes |
| `adrs/` | dated, immutable decision records for taxonomy/structure decisions. Living docs always speak the current state; ADRs hold how it was reached and the old→new decoders. Never edit an accepted ADR except `superseded-by`. See [`adrs/README.md`](adrs/README.md) | yes |
| `articles/` | public-facing drafts, one file per article, site-schema frontmatter. Drafted here so claims keep repo-relative links (rule 4 for prose); published to the personal site as a downstream copy. See [`articles/README.md`](articles/README.md) | yes |

**Never hand-edit anything in `comparisons/` or `refs/index.md`.** Edit the frontmatter of the
note it summarises and re-run the generator. Hand-kept indexes drift and you find out when
they're already wrong (rule 3).

## The three operations

**Ingest a source.** Read it — actually read it. Write `refs/<citekey>.md` from
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
```

`--check` distinguishes two conditions. **UNVERIFIABLE** (exit non-zero) means a pinned
commit no longer resolves — claims can't be checked against their source at all.
**behind** is not a failure, but it is not noise either: it is a work queue. Ask whether
the drift touches what the report claims and record the answer, dated, in the report —
**without moving the pin** (methodology rule 4b). ECC's 16-commit drift contained the
upstream bug fix that falsified a claim in its deep-dive.

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
- **This repo is public-facing.** No employer references, no pointers to private local files, no
  paths a reader can't resolve. Restate work-derived findings generically as personal experience
  with a rough date.
- Commits go straight to `main` (sole contributor, deliberate exception to branch-first).
