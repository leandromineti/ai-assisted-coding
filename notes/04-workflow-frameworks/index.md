# Layer 4 — Workflow frameworks

`checked: 2026-07-28`

An encoded **methodology** riding on top of a harness. Runtime is to framework as harness
is to this. See [`../../taxonomy.md`](../../taxonomy.md).

The layer test is **harness portability by design**: the methodology is defined once and
targets many harnesses.

## Seed inventory

### GSD — <https://opengsd.net> · [report](gsd-core.md)

Bills itself as an *operating loop* for agentic engineering work — its stated enemy is
context bloat and scope drift. Note the provenance: `gsd-core` is a 2026-05-22 community
fork of the original `gsd-build/get-shit-done` (64.8k stars, now archived), whose
maintainer vanished amid a crypto-token rug-pull association — see the
[report's provenance section](gsd-core.md#provenance--a-fork-born-from-a-vanished-maintainer).

Three principles: explicit plans as **structured task graphs**, **clean execution
contexts** per unit of work, and **real verification** producing human-readable evidence.

Ships as several pieces, which is itself instructive:

| Piece | What | Layer |
|-------|------|-------|
| `gsd-core` | The framework proper; 18 install targets @ fee72d55 (Gemini CLI removed upstream 2026-06-18 — July's list was stale at read time). | 4 |
| `gsd-pi` | Standalone CLI for autonomous workflows. | **2 — bleed** |
| `gsd-browser` | Deterministic Chrome control with recording and assertions. | **3 — bleed** |
| `gsd-workbench` | Desktop workspace. Announced, not shipped at check date. | 2 |
| `gsd-cloud` | Hosted cross-device state. Announced, not shipped at check date. | — |

*(2026-08-18: the "already installed on this machine" advantage is gone — no gsd-*
artifacts under `~/.claude` on this host, almost certainly lost in the 2026-08-06 server
rebuild. Deep-dived 2026-08-18 at fee72d55 — the layer's third deep-dive:
[report](gsd-core.md).)*

### spec-kit — <https://github.com/github/spec-kit> · [report](spec-kit.md)

GitHub's toolkit for **Spec-Driven Development**: specifications come first and are treated
as executable artifacts that *generate* the implementation, rather than documentation that
merely guides it. Intent before mechanism — the "what" before the "how".

Workflow commands:

`/speckit.constitution` (project principles) → `/speckit.specify` (requirements) →
`/speckit.plan` (technical strategy) → `/speckit.tasks` (task list) → `/speckit.implement`
(execute). Optional: `/speckit.clarify`, `/speckit.analyze`, `/speckit.checklist`.

37 registered integrations @ 655a3cb (verified at deep-dive 2026-08-18; the earlier
"44 config dirs" figure did not reproduce). Install: `uv tool install specify-cli` —
needs Python 3.11+, git, and `uv`. Deep-dived 2026-08-18: two systems — prose methodology
+ an 11-step-type orchestration engine that dispatches the prose by name, never reads it,
and ships 78 lines of workflow against ~17k lines of runtime ([report](spec-kit.md)).

### OpenSpec — <https://github.com/Fission-AI/OpenSpec> · [report](openspec.md)

*(Added 2026-07-28; deep-dived 2026-07-31.)* The lean pole of spec-driven development:
**delta specs** — spec only the change, archive completed changes, and let a
**deterministic merge compiler** (`specs-apply.ts`: formal ADDED/MODIFIED/REMOVED/RENAMED
grammar, conflict detection, ordered application) accrete them into a living
source-of-truth. The read's headline: OpenSpec inverts conclusion 7 — the deterministic
engine is the *founding architecture* (workflow-as-schema-YAML interpreted by a DAG
engine; machine validation; prose shrunk to thin CLI adapters), not an escape hatch
grown after prose failed. But its gates are **format** gates, never *measured* gates —
it validates artifacts, not behavior (empirical grounding: absent, as predicted).
Dogfooded at scale: 91 changes through its own pipeline over 36 living specs. 29
harness adapters. 63k stars, MIT, 71% single-author.

### ECC (everything-claude-code) — **moved to layer 5** (2026-07-30)

*(Added 2026-07-28 as a deliberate boundary case; resolved at deep-dive.)* The source
read answered the question this entry was created to ask: **no process spine** — the
README's own guidance is "start with the workflow you need, not the full catalog,"
workflow content is opt-in catalog items, and the multi-* orchestration commands
require an external runtime (`ccg-workflow`). A config pack at scale with a real
learning runtime, not an encoded methodology. Report now at
[`../05-capability-extensions/ecc.md`](../05-capability-extensions/ecc.md). What it
contributed to *this* layer's questions: verification gates can arrive as installable
Stop hooks (a layer-5 delivery vehicle for the mechanism exp-01 credited to layer 4),
and its `ecc2` Rust control plane repeats the conclusion-7 escape-hatch pattern from
outside layer 4 proper.

### Stubs — promoted from the ledger (2026-08-18)

Five candidates ingested at stub depth in one sweep — mechanical facts plus README
skim, sources unread; each report says what a survey read should check first:

- [**BMAD-METHOD**](bmad-method.md) — the AiDD delivery loop; widest verified portability in the layer (47 installer platform codes). Is v6's "right-sized process" real routing or a default-heavy funnel?
- [**Conductor**](conductor.md) — Google-org SDD plugin; the smallest subject in the layer (22 markdown files *are* the framework) — purest prose-only pole for the conclusion-7 question.
- [**pilot-shell**](pilot-shell.md) — spec spine (`/prd`→`/spec` TDD→`/build` judge loops) inside an ECC-shaped platform; only non-OSI subject (source-available EULA). Spine or catalog?
- [**spec-kitty**](spec-kitty.md) — spec-kit fork grown into a worktree-parallel "governed software factory"; imported parent history verifiable in `first_commit`. What did the fork change in the parent's pipeline?
- [**haft**](haft.md) — decision-governance pole (FPF: typed records, evidence decay); heaviest runtime in the layer (2k+ Go files). Encoded methodology or memory extension?

## Candidates

The "Considered, not added (2026-07-28)" table moved to the cross-layer
[candidates ledger](../candidates.md) on 2026-08-18 ([ADR-0009](../../adrs/0009-candidates-ledger.md)) —
candidate is now the named pre-report rung of the engagement ladder, one ledger for
all layers.

## Spec-Driven Development (SDD)

*(Added 2026-08-18 — the term was already load-bearing in the reports but defined nowhere.)*

**SDD** names the layer-4 sub-family whose organizing artifact is the **specification**:
written first, machine-validated, and treated as the *generator* of the implementation
rather than documentation that guides it. The term is vendor-coined — it is
[spec-kit's own branding](spec-kit.md) — but third-party usage has settled on a
recognizable set, the "2026 SDD trio": **BMAD / spec-kit / OpenSpec** (so named in the
[OpenSpec report](openspec.md)). Of the trio, this repo tracks two (spec-kit, OpenSpec —
the ceremony and lean poles respectively) and holds BMAD first in line in the
[candidates ledger](../candidates.md).

SDD is a sub-family, not the layer: **GSD is layer 4 without being SDD** — its organizing
artifact is the task graph and its enemy is context bloat, not under-specified intent.
That is the same split "the shared bet" below describes without naming: where a framework
locates the failure (intent vs. context) determines whether it is SDD.

## The shared bet

Both wager that **agents fail from insufficient structure, not insufficient intelligence** —
that the fix for a drifting agent is a better-specified process, not a better model. GSD
locates the failure in context management; spec-kit locates it in under-specified intent.
Same diagnosis, different organ.

That bet is falsifiable, and testing it is one of the more valuable things this repo could
do: as models improve, does imposed structure keep paying, or does it become overhead?
First test run: [`experiments/01-gsd-vs-plain/`](../../experiments/01-gsd-vs-plain/README.md).

## Feature taxonomy (2026-08-18)

The layer now carries the layer-4 slice of the repo's **feature taxonomy** —
`workflow_features:` in report frontmatter, with every key defined once in
[`notes/cross-cutting/feature-taxonomy.md`](../cross-cutting/feature-taxonomy.md)
([ADR-0010](../../adrs/0010-two-taxonomies.md)), rendered in
[`comparisons/features.md`](../../comparisons/features.md). The division of
labor with the mechanism table below: a **feature** is a presence-claim (the machinery
exists, verified in source or docs); a **mechanism** is a value-claim (it measurably
pays). The matrix says *what* each framework built; the experiments say *whether it
matters*. Keys follow the same discipline as the harness vocabulary — omitted means
"not checked", `false` means "checked and absent", and absences are findings
(Conductor's verified-absent engine; haft's verified-absent intent pipeline).

Second calibration, also 2026-08-18: the GSD deep-dive supplied the second verified
instance of the who-enforces ambiguity, and the gate keys became **graded**
(`engine | hook | script | prose | true | false` — [ADR-0011](../../adrs/0011-graded-gate-enforcement.md));
a bare `true` in a gate column is now an explicit unanswered question.

First falsification, same day it was created (2026-08-18): spec-kit's `format_gates`
went ✓→✗ at deep-dive — the survey-visible gates turned out to be prose the agent
enforces on itself, not machinery. The calibration this buys: **a gate stated in prose
looks like a feature until you check who enforces it**, so every README-sourced ✓ in a
stub row (pilot-shell's `measured_gates` especially) carries an implicit asterisk until
its source is read.

## Mechanisms — the unit of value

*(Added 2026-07-28 after experiment 01. "GSD is a layer-4 tool" proved true and nearly
useless as an analytical claim: the value variance was inside the tool. The tool is the
unit of **distribution**; the mechanism is the unit of **value**. Compare frameworks
mechanism-by-mechanism, not brand-by-brand.)*

| Mechanism class | What it is | Exp-01 evidence (n=1) |
|---|---|---|
| **Intent capture** | Structured extraction and pinning of the "what" before execution: ID'd requirements, rationed clarification, artifacts that test the English itself | Not exercised by exp-01 (added 2026-07-28 from the spec-kit source read — GSD is thin here). **Measured by exp-02 (2026-08-17):** wins every requirements-rubric item, leaves trap score exactly at baseline — it *steers* trap-relevant decisions in both directions (documented wrong exit-code choice, right UTC choice) but discovers nothing (README conclusion 11) |
| **Empirical grounding** | Agents instructed to *measure* the domain (fixture repos, probes) rather than trust training data | Carried most of the quality margin: the invalid-UTF-8 crash class, timezone traps, exit-code collision were all found by measurement |
| **Verification gates** | Machine-checkable acceptance criteria with *measured* expected values; verifiers that re-derive rather than trust | Carried the rest: the checker caught an untested claim; verifiers exceeded brief and honestly abstained on subjective checks |
| **Context discipline** | Fresh right-sized context per unit of work; artifacts as the interface between stages | Plausibly load-bearing (each stage caught the previous stage's vagueness — the refinement funnel) but not isolated by this experiment |
| **Process gates** | Approval points, threat models, mode ceremonies | Near-zero observed value on this task (STRIDE for a read-only CLI; three no-op default-on hooks) |
| **Bookkeeping** | State files, checkboxes, traceability tables | Mixed: traceability caught requirement gaps; checkbox upkeep was dropped by the framework itself in both phases |

### Profiles so far

*(GSD: run + source read, exp-01. spec-kit: source read 2026-07-28 **and run
2026-08-17** — exp-02's full 7-step pipeline at the pin; the profile below was
validated by the run, see [spec-kit.md](spec-kit.md) § Profile validated by run.)*

| Mechanism class | GSD | spec-kit |
|---|---|---|
| Intent capture | Thin | **Center of mass**: FR-/SC- IDs, prioritized independently-testable stories, rationed clarification (max 3 markers / 5 questions), "unit tests for requirements" checklists |
| Empirical grounding | **Heavy** (fixture measurement, probes) | Nearly absent — Phase-0 "research" is best-practices lookup from training data |
| Verification gates | **Heavy**, measured expected values | Document-vs-document only; the one hard gate is user-overridable |
| Context discipline | **Core mechanism** (fresh subagent contexts) | Weakest column; the one isolation attempt (fork for analyze) was reverted after compounding-context freezes (#3185) |
| Process gates | Moderate (hooks, STRIDE, modes) | Moderate (hook ceremonies, constitution governance wrapper with no consumer) |
| Bookkeeping | Moderate, self-dropped under load | Strong grammar-enforced (task ID/[P]/[US] format, ≥80% traceability floor) |

The two frameworks are near-complements: GSD spends structure on the execution side,
spec-kit on the intake side; each is thin exactly where the other is thick. "GSD vs
spec-kit" as brands was the wrong comparison — this table is the real one.

## Open questions

- ~~GSD and spec-kit both add ceremony. What's the task-size threshold below which the
  ceremony costs more than it saves?~~ **Partially answered 2026-07-28** (experiment 01,
  n=1): the threshold splits by what "saves" means — the test task was below it for
  build speed (~78 min vs ~1 min) and arguably above it for ship quality (a real
  crash-class margin). The sharper successor question: **which mechanisms buy the
  margin?** (table above — empirical grounding + gates, on this evidence).
- Is the portability real? Does GSD-on-Cursor behave like GSD-on-Claude-Code, or does the
  underlying harness dominate the outcome? **Mechanism half answered 2026-07-28** for
  spec-kit (source-read): portability is a compile step over placeholder-token markdown,
  cheap because every harness converged on "slash command = prompt file in a directory" —
  and bounded by it: the methodology can't use any capability beyond prose-following, so
  forks, code-level hooks, and context isolation are structurally unavailable. Behavioral
  equivalence across harnesses remains untested.
- Claude Code ships plan mode natively. Where's the line between a harness's built-in
  process features and an installed framework — and is layer 4 being absorbed into layer 2?
- ~~Neither is easy to A/B test, since you can't run the same task twice cleanly. What
  would a fair comparison even look like?~~ **Working answer 2026-07-28:** preregister
  the protocol and falsification criteria, run the contaminated arm second with fresh
  subagent contexts, log during (not after), and state n honestly. Experiment 01 is the
  template; its limitations section is part of the answer.
