# Methodology

`checked: 2026-07-30`

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

- **1a. One evidence-grade vocabulary for closed subjects.** When a subject's source is
  not readable, every claim carries one of four grades, inline: **SOURCE** (read in a
  pinned clone — the only grade that supports architecture claims), **OBSERVED** (live
  behavior or config surface of a running installation, dated), **TESTIMONY** (vendor
  docs/blogs, `retrieved:` date — mechanism-level at best, never auditable), **INFERENCE**
  (marked as such). What none of them reaches is recorded as unverified, not omitted.
  Ordering is strict: source beats observation (you can catch a vendor being wrong),
  observation beats testimony (you can catch the docs being stale), and closure caps a
  report's ceiling — a subject with no readable source cannot honestly reach `deep-dive`.

  *Why it earned its place:* within one week two closed-subject reports coined two
  different vocabularies for the same distinction (modal: VERIFIED/TESTIMONY/OPAQUE;
  claude-code: OBSERVED/TESTIMONY/INFERENCE). Both were internally honest and mutually
  incomparable — a third report would have coined a third. Existing reports keep their
  original labels with this mapping: modal's VERIFIED = SOURCE (its client is open),
  its OPAQUE = unverified; claude-code's OBSERVED/TESTIMONY/INFERENCE map directly.

## 2. Honesty markers beat completeness theater

State-of-knowledge is always visible and machine-readable:

- `depth: stub | survey | deep-dive` on every tool report — "we looked" can never be
  mistaken for "we read it."
- `·` (not-yet-checked) is distinct from `✗` (verified absent) in the feature matrix.
- An unused tool gets an **empty** "my take" section. The blankness is the honest state.

## 3. Generated, never hand-kept

Anything that summarizes other files (`comparisons/tools.md`, `comparisons/features.md`,
`refs/index.md`, `comparisons/benchmarks.md`) is generated from their frontmatter by
`scripts/build-tool-index.py` and `scripts/build-refs-index.py`. Hand-kept indexes drift, and
you find out when they're already wrong. `--check` verifies every report's pinned commit is
still **reachable** in its clone; a pin that no longer resolves means the claims beneath it
can't be checked against their source, and that is an error.

**Upstream moving on is not an error, and conflating the two was a bug (fixed 2026-07-31).**
The check used to fail whenever a pin differed from clone HEAD, calling it "stale". But a pin
records *the commit that was read* — a dated historical fact — so the only action that silenced
the warning was re-pointing it at HEAD **without re-reading**, converting an honest dated
observation into a false claim about current code. A lint whose only cheap remedy is to lie is
worse than no lint. Drift is now reported with magnitude (commits ahead, files changed) so a
human can decide whether a re-read is warranted; that decision is judgement, not a lint pass.

- **3a. A count, ordinal, or "only" about this repo's own files is a claim that rots.**
  Rule 1 dates claims about tools; rule 3 generates claims that are indexes. A hand-written
  sentence about the corpus itself — "the category's only report", "the third deep-dive",
  "that column is empty in every row" — sits between them: no generator keeps it true and
  no lint can see it. Either derive the number at edit time and date it ("n=5 as of
  2026-08-21"), or phrase it as the dated event it records ("first read, 2026-08-16") —
  never as a standing present-tense fact.

  *Why it earned its place:* three instances shipped in v2.0's Phase 8 (2026-08-20/21) and
  were caught only by post-phase review: the category-3 index still called E2B "the
  category's first and (so far) only report" while sitting directly above four newer linked
  reports; "third/fourth/fifth read" ordinals disagreed between two reports and the index;
  and the index's Adjudication section asserted a matrix column empty that the same file's
  Open-questions section recorded as filled three days earlier. The sentence that failed
  hardest was *true when written* (2026-08-16) — it rotted precisely because it was phrased
  as a standing fact rather than a dated observation. v1.0 left the same class of scar (a
  stale hand-recorded `known_sites` line reference; an incomplete `scripts/` table), so
  this is a repeat offender, not a one-off.

## 4. Source claims are traceable or they're opinions

Architecture claims name a file, a line, and a pinned commit
(`processor.ts:30 @ 017a5977d`). Reports on cloned tools are checked against the pin
mechanically. Blobless clones (`upstream/`) keep `git log`/`blame` usable — a design's
*history* is often better documentation than the design.

- **4a. Docstrings are testimony; call sites are evidence.** A claim about *when or
  whether* a mechanism fires traces to its call site and gating condition, not the
  module header — mandatory for anything entering a report's "distinguishing bet" or
  "Surprises", the sections other conclusions build on. Well-documented codebases make
  docstring-leaning reads efficient and flattering — those are the ones this rule
  exists for. The mirror discipline for absence: a mechanism not found is recorded as
  *unverified absence* with the search scope stated, never asserted as absent (the
  prose analog of the matrix's `·` vs `✗`).

  *Why it earned its place:* the hermes-agent deep-dive (2026-07-30) reported an
  "after every turn" review fork from `background_review.py`'s docstring; the call
  site (`turn_finalizer.py:653`) showed interval-gated, success-only, best-effort. The
  overstated version was the report's flagship claim and had already propagated to the
  category-2 index before a parity check caught it. Applied prospectively in the codex
  read same day (memory pipeline verified at `turn_processor.rs:594`; missing stuck-loop
  guard recorded as unverified absence).

  *Second instance, found 2026-08-11 — the rule did not hold on the same day it was
  written.* The ECC deep-dive (2026-07-30, hours after the hermes correction) reported
  "`/evolve` clusters related instincts into skills/commands/agents." That is
  `cmd_evolve`'s docstring. The code below it keyed clusters on the whole trigger
  sentence, so `skill_candidates` was always empty and `agent_candidates`, filtered from
  it, always empty too — the mechanism did not fire *at all*, and it took an upstream bug
  fix twelve days later to surface it
  ([`tools/6-extensions/ecc.md`](tools/6-extensions/ecc.md)).
  Two lessons, both cheap: **a pipeline is only as traced as its least-interesting
  stage** — steps 1–3 were read at the call sites and the last step was skimmed because
  by then the design was convincing; and **"clusters"/"promotes"/"selects" are verbs that
  need a measurement, not a reading.** The fix's author reported one (42 instincts → 42
  clusters, largest size 1) that the read could have made in a minute. Where a docstring
  describes an aggregation, run it or read its key function — a grouping key is a
  one-line thing to check and the whole claim rests on it.

- **4b. The `behind` list is a work queue, not a status line.** When
  `build-tool-index.py --check` reports a report behind its pin, the obligation is to
  ask *whether the drift touches what the report claims* — and to record the answer,
  dated, in the report itself. Three outcomes, all of them writing:
  **contradicted** (correct the claim in place, citing the pin), **corroborated** (say
  so — upstream confirming a finding is evidence, and unrecorded it looks like silence),
  **untouched** (one line, so the next reader doesn't redo the check).

  **The pin does not move.** A drift check is not a re-read, and only a re-read earns a
  new pin (`upstream/README.md`'s scar). A report may carry a dated drift check well
  ahead of its `read_at` — that is the honest shape, not an inconsistency.

  *Why it earned its place:* ECC sat 16 commits behind for twelve days. Inside that
  drift was an upstream bug fix (#2664, 2026-08-04) proving that `/evolve` had never
  produced a skill or agent candidate — falsifying a claim in a **deep-dive** report,
  which is the depth most likely to be cited elsewhere. `--check` had been printing the
  `behind` line the whole time and nothing in this file said it was actionable, so the
  honest default was to read it as noise. Drift is where wrong claims surface, because
  the people fixing the bug write down what was broken. Corollary: the backlog compounds
  silently — issue #9 recorded gsd-core and spec-kit at 41 and 63 commits behind on
  2026-08-01; eleven days later they were at 207 and 123.

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
- **5c. Cost is measured from transcripts, not harness metadata.** Experiment 01's
  headline cost figure ("~1.47M subagent tokens") came from per-agent notification
  metadata and couldn't answer a direct "what did it cost?" — transcript measurement
  showed actual subagent output was 346k (the metadata metric is an opaque ~4× blend),
  and that the *orchestrator's* cache reads, invisible to notifications, dominated
  total spend. Session + agent transcripts carry exact `usage` fields; parse those.
  (Same failure family as `stats-cache.json` inflating cache reads —
  `tools/cross-cutting/index.md`.) Attribute usage **per model**: exp-02's Run A ledger
  showed an auxiliary `claude-haiku-4-5` call the protocol's "sole model" wording hadn't
  anticipated — immaterial at $0.0008, but you only know that by looking.
- **5d. Comparison instruments are proven to discriminate, not just to fail closed.**
  Fails-closed proves an instrument can register failure; it says nothing about whether it
  can register *difference*. Establish headroom before the comparative run: pilot the
  instrument against a competent reference — the plain baseline is the natural one, so
  **run the baseline arm first and treat it as instrument calibration** — and require a
  non-perfect, non-zero score. A baseline that saturates the instrument means it is not a
  comparison instrument for that pair; fix the instrument or narrow the claim *before*
  spending on the second arm.

  *Why it earned its place:* exp-02's trap set was proven fails-closed in-container (8/8
  error against an empty container, 8/8 fail against a stub) and still turned out useless
  for its main purpose — the plain arm cleared all five trap classes unaided on the first
  attempt, leaving the framework arm no room to score *better* and rendering the
  preregistered "intent capture buys code quality" damage condition unfalsifiable on that
  task. The floor was proven twice; nobody checked the ceiling once.
- **5e. The execution path is preregistered *and* smoke-tested; success is read from
  artifacts, not exit status.** A protocol that names a driver command is not validated
  until that exact command line has run end-to-end on a trivial prompt. And a harness can
  exit 0 having done no work — confirm every run against its produced artifacts and
  transcript before scoring it.

  *Why it earned its place:* exp-02's preregistered driver specified
  `--dangerously-skip-permissions`, which the harness refuses outright as root. The launch
  died in 2 seconds, wrote nothing, and **reported exit 0**; the failure was visible only on
  stderr. A $0.05 smoke run would have caught it before the protocol was called runnable.
  The replacement mechanism (an explicit `permissions.allow` list) is also strictly better,
  which is the tell that the original was never exercised.
- **5f. Instrument calibration is a distribution, not a point estimate.** One baseline
  run gives one draw from the baseline's score distribution: a strong draw reads as
  saturation, a weak one as headroom that isn't there, and nothing in a single run says
  which you got. When a verdict hangs on headroom, buy a small distribution of
  independent baseline runs (five reversed a verdict here), and when discrimination
  itself is the claim, add a known-groups check — a population the instrument *should*
  separate, run under identical conditions, that it in fact separates.

  *Why it earned its place:* exp-02's densified instrument was declared "consumed at
  this task size" on 2026-08-17 from a single calibration artifact scoring 20/21 —
  with 5d followed to the letter. Five fresh baseline runs later the same day (run to
  screen new candidate traps, every one of which was discarded) scored 18–20 with
  three checks failing at 40–100% baseline rates: the saturation verdict was an
  artifact of one strong draw. The ~$2 that bought the distribution also bought the
  known-groups result (a weaker tier fully separated, one trap *reversing* because it
  measures failure style rather than skill) — the screening's discarded candidates
  cost the same as its real finding.

## 6. Findings are promoted, not scattered

The path is: run log → tool report / category note (dated) → `README.md` Conclusions
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

- **8a. The same skepticism applies to the apparatus. The network condition is declared,
  enforced at the egress layer, verified by probe, and held identical across arms.**
  Configuring a tool permission is not enforcing a network policy. State which condition an
  experiment ran under — **closed**, **package-hosts-only**, or **open** — enforce it where
  traffic actually leaves the sandbox, prove it with a probe recorded in the log, and never
  compare arms that ran under different conditions.

  Open is a legitimate condition, not a failure: nobody runs these frameworks with the web
  unplugged, so a permanently closed rig measures a configuration that doesn't exist in
  practice. But it is never a *silent* default, because it lets a framework satisfy
  "empirical grounding" by lookup instead of local measurement — the exact mechanism
  conclusion 6 attributes the quality margin to — and because web content differs between
  two runs days apart, which is a live confound for an n=1 A/B.

  *Why it earned its place:* exp-02's rig denied the web *tools* and its README claimed arms
  therefore had model-API-only access; `curl https://example.com` from the Bash tool returned
  HTTP 200. The claim survived only because Run A's arm never thought to shell out — verified
  after the fact from its transcript, which is luck, not method.

- **8b. The pin describes the tree, not the artifact. When a tool's distribution has a
  publish step, probe the published artifact too.** A pinned clone is this repo's unit of
  verification, but anything injected at package/publish time — credentials, config,
  compiled assets — exists only in the distributed package, and a source-only read is
  structurally blind to it. Where a claim concerns what a *user* runs (defaults,
  telemetry, install behavior), fetch the published artifact (npm tarball, PyPI wheel,
  release binary), record its version against the pin, and read the claim from both.

  *Why it earned its place:* memos (2026-08-19 deep-dive) ships `telemetry: enabled` with
  the endpoint file gitignored and generated by CI from secrets at `npm publish`. Every
  clone at every pin says "no egress"; the npm 2.0.16 tarball contains live Aliyun ARMS
  credentials. The finding was reachable only by probing the artifact — and the same
  probe settled a second claim (the shipped default config) against what users actually
  receive rather than what the tree suggests.

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
