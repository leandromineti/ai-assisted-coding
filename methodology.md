# Methodology

`checked: 2026-07-28`

How work is done in this repo — distilled from practice, not aspiration. Every rule here
earned its place by catching a real mistake at least once; each entry names where it's
enforced. Intent lives in [`README.md`](README.md); vocabulary in
[`taxonomy.md`](taxonomy.md). This file is the *how*.

## 1. Verify against primary sources; date every claim

Facts about tools come from their source, their official docs, or a measurement — never
from training-data memory. Every fact-bearing document carries `checked: YYYY-MM-DD`;
anything unconfirmable is marked `unverified` rather than asserted.

*Why it earned its place:* the opencode repo had moved orgs and GSD's org name didn't
match its npm registry entry — both would have been wrong if asserted from memory.

## 2. Honesty markers beat completeness theater

State-of-knowledge is always visible and machine-readable:

- `depth: stub | survey | deep-dive` on every tool report — "we looked" can never be
  mistaken for "we read it."
- `·` (not-yet-checked) is distinct from `✗` (verified absent) in the feature matrix.
- An unused tool gets an **empty** "my take" section. The blankness is the honest state.

## 3. Generated, never hand-kept

Anything that summarizes other files (`comparisons/tools.md`, `comparisons/features.md`)
is generated from their frontmatter by `scripts/build-tool-index.py`. Hand-kept indexes
drift, and you find out when they're already wrong. `--check` re-verifies that every
report's pinned commit still matches its clone's HEAD — a stale pin silently invalidates
every claim beneath it.

## 4. Source claims are traceable or they're opinions

Architecture claims name a file, a line, and a pinned commit
(`processor.ts:30 @ 017a5977d`). Reports on cloned tools are checked against the pin
mechanically. Blobless clones (`upstream/`) keep `git log`/`blame` usable — a design's
*history* is often better documentation than the design.

## 5. Experiments are preregistered

The protocol — task, measurements, falsification criteria, known contamination — is
written and committed **before** any run (`experiments/01-gsd-vs-plain/README.md` is the
template case). The log is appended *during* the run, never reconstructed after. Results
are appended below the untouched protocol. Artifacts are copied out of ephemeral space
before the session ends. Sample sizes are stated plainly (n=1 is a probe, not a proof —
say so).

*Why it earned its place:* the comparison script itself had a bug (wrong expected value);
preregistration made it discoverable as *scorer error* rather than silently flattering
either side.

Two sub-rules, both scarred in experiment 01:

- **5a. Scoring harnesses get measured expectations, not assumed ones.** The comparison
  script asserted a fixture author had 4 commits from memory of its own fixture; she had
  3. The framework under test measured its expected values and was right; the
  experimenter derived his and shipped a bug. A comparison harness is an artifact — its
  expected values need the same empirical grounding demanded of everything else. Run the
  fixture, record what it *actually* produces, then assert that.
- **5b. Orchestration experiments anchor paths absolutely and audit the staged set.**
  Frameworks may key state on ambient cwd (GSD's research cache materialized in the
  orchestrating repo's root, not the target project). When driving tooling against
  another directory: absolute paths everywhere, and review `git status` / the staged
  file list before any commit in the host repo — that review is what caught the leak.

## 6. Findings are promoted, not scattered

The path is: run log → tool report / layer note (dated) → `README.md` Conclusions
(numbered, dated, revisable, each linked to its evidence). A finding that changed no
note is an anecdote; a conclusion without a linked note is an assertion.

## 7. Upstream reports pass an awareness gate

Before filing an issue or PR on someone else's project: exhaustively check their docs,
issues, PRs, and any related blog series to confirm the finding is genuinely unknown to
them. File evidence-first, argue materiality **from the target's own data**, state
explicitly what the finding does *not* invalidate, and match the maintainer's
contribution patterns (for llm-coding-benchmark: code/docs only, opt-in flags, no
results). Case study: issue #12 / PR #13 there.

## 8. Same subject, both directions

Where possible, cross-check what a tool's docs *say* against what its source *does*
(opencode's nine prompts vs. the one-prompt marketing frame) and against what it *does
when run* (the GSD experiment). The only tool where all three views exist — gsd-core —
produced the repo's sharpest findings. Prefer subjects where behavior can be observed,
not just read.

## 9. Public docs are self-contained

No pointer in this repo may require access the reader doesn't have. Findings from
private experience are restated generically, attributed as personal experience with a
rough date, not linked to inaccessible sources.

## Anti-goals

- **No completeness for its own sake.** Stubs stay stubs until reading them is worth it;
  the dots in the feature matrix are a to-do list, not a scandal.
- **No methodology expansion without a scar.** A rule joins this file when its absence
  caused a real mistake, not because it sounds rigorous. (This is the meta-rule — the
  experiment showed process ceremony without empirical grounding produces cost, not
  quality. The same applies to this document.)
