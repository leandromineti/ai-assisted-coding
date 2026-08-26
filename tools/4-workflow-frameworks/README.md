# Category 4 — Workflow frameworks

`checked: 2026-08-26`

An encoded **methodology** riding on top of a harness. Runtime is to framework as harness
is to this. See [`../../docs/tool-taxonomy.md`](../../docs/tool-taxonomy.md).

The category test is **harness portability by design**: the methodology is defined once and
targets many harnesses.

## What we assess here

The assessed block is **`workflow_features:`, 9 keys** (2026-08-26, added 2026-08-18):
`intent_pipeline`, `deterministic_engine`, `format_gates`, `measured_gates`,
`process_gates`, `context_isolation`, `parallel_orchestration`, `state_store`,
`retrospectives` — one per mechanism the category sells, which is what makes the same
vocabulary reusable for the absorption question asked of harnesses in
[category 2](../2-harnesses/README.md#what-category-2-has-absorbed--the-category-4-feature-set-checked-against-harnesses).
The three gate keys are **graded** (`engine | hook | script | prose | true | false` —
[ADR-0011](../../adrs/0011-graded-gate-enforcement.md)) after the GSD deep-dive supplied a
second instance of the who-enforces ambiguity; a bare `true` in a gate column is an
explicit unanswered question.

The division of labor with the mechanism table below: a **feature** is a presence-claim
(the machinery exists, verified in source or docs); a **mechanism** is a value-claim (it
measurably pays). The matrix says *what* each framework built; the experiments say
*whether it matters*.

**First falsification, the same day the block was created (2026-08-18):** spec-kit's
`format_gates` went ✓→✗ at deep-dive — the survey-visible gates turned out to be prose the
agent enforces on itself, not machinery. The calibration this buys: **a gate stated in
prose looks like a feature until you check who enforces it**, so every README-sourced ✓ in
a stub row (pilot-shell's `measured_gates` especially) carries an implicit asterisk until
its source is read.

The other half is **9 transcription fields** — `maker`, `license`, `access`, `stars`,
`first_commit`, `version`, `commit`, `stack`, `harness_targets` — facts copied from a dated
source rather than judged.

Both halves are read as **six groups** — Identity · Provenance · Shape · The spine ·
Verification gates · Orchestration — each opening with what it is about and how its keys
read together: [`feature-registry.md` § Workflow frameworks](../../comparisons/feature-registry.md#workflow-frameworks).

Definitions:
[`comparisons/feature-registry.md`](../../comparisons/feature-registry.md). Values:
[`comparisons/features.md § Workflow frameworks`](../../comparisons/features.md#workflow-frameworks-category-4).
A key is set **only** when verified — omitted means "not checked", `false` means "checked
and absent", and absences are findings (Conductor's verified-absent engine; haft's
verified-absent intent pipeline).

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

| Piece | What | Category |
|-------|------|-------|
| `gsd-core` | The framework proper; 18 install targets @ 182f60b4/v1.11.0, list byte-identical since fee72d55 — growth redirected to the out-of-tree EoS Registry (Gemini CLI removed upstream 2026-06-18 — July's list was stale at read time). | 4 |
| `gsd-pi` | Standalone CLI for autonomous workflows. | **2 — bleed** |
| `gsd-browser` | Deterministic Chrome control with recording and assertions. | **3 — bleed** |
| `gsd-workbench` | Desktop workspace. Announced, not shipped at check date. | 2 |
| `gsd-cloud` | Hosted cross-device state. Announced, not shipped at check date. | — |

*(2026-08-18: the "already installed on this machine" advantage is gone — no gsd-*
artifacts under `~/.claude` on this host, almost certainly lost in the 2026-08-06 server
rebuild. Deep-dived 2026-08-18 at fee72d55 — the category's third deep-dive; release
re-read 2026-08-21 at v1.11.0 (182f60b4), pin moved per rule 4b:
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

### ECC (everything-claude-code) — **moved to the extensions bucket** (2026-07-30; category 5 then, 6 since the 2026-08-22 split)

*(Added 2026-07-28 as a deliberate boundary case; resolved at deep-dive.)* The source
read answered the question this entry was created to ask: **no process spine** — the
README's own guidance is "start with the workflow you need, not the full catalog,"
workflow content is opt-in catalog items, and the multi-* orchestration commands
require an external runtime (`ccg-workflow`). A config pack at scale with a real
learning runtime, not an encoded methodology. Report now at
[`../6-extensions/ecc.md`](../6-extensions/ecc.md). What it
contributed to *this* category's questions: verification gates can arrive as installable
Stop hooks (a category-6 delivery vehicle for the mechanism exp-01 credited to category 4),
and its `ecc2` Rust control plane repeats the conclusion-7 escape-hatch pattern from
outside category 4 proper.

### BMAD-METHOD — <https://github.com/bmad-code-org/BMAD-METHOD> · [report](bmad-method.md)

*(Stubbed and deep-dived 2026-08-18, same pin `86beb065` — the category's fourth deep-dive.)*
The AiDD delivery loop, mid-molt: build-first entry (`bmad-build`, planning artifacts
optional context — the "process-heavy funnel" prediction falsified), a real one-shot/full
fork that is nonetheless one prose judgment biased heavy and deleted in the unattended
variant. Ships the category's fourth engine shape: ~2.6k lines of tested Python state
tooling with **no authority** — every script failure licenses the LLM to proceed by best
judgment, zero hooks. Portability is anti-translation: byte-identical Agent Skills copied
to 47 platform codes (22 distinct dirs, 26 sharing `.agents/skills/`) — no translation to
degrade; the real price is a hand-forked 6-skill `web-bundles/`. The category's purest
large-scale model-trust bet, falsifiable by exp-01's mechanism finding.
Companion: [**bmad-loop**](bmad-loop.md) *(stubbed 2026-08-18)* — the ecosystem's
enforcement, sold separately: a deterministic Python orchestrator ("No LLM in the
control loop") with the tracked ecosystem's first **engine-graded measured and process
gates**; drives claude/codex/gemini/copilot/antigravity sessions via tmux + harness
hooks. Even there, retro→plan stays roadmap.

### Stubs — promoted from the ledger (2026-08-18)

Five candidates ingested at stub depth in one sweep — mechanical facts plus README
skim, sources unread; each report says what a survey read should check first.
*(BMAD-METHOD graduated from this list to a deep-dive the same day — entry above.)*

- [**Conductor**](conductor.md) — Google-org SDD plugin; the smallest subject in the category (22 markdown files *are* the framework) — purest prose-only pole for the conclusion-7 question.
- [**pilot-shell**](pilot-shell.md) — spec spine (`/prd`→`/spec` TDD→`/build` judge loops) inside an ECC-shaped platform; only non-OSI subject (source-available EULA). Spine or catalog?
- [**spec-kitty**](spec-kitty.md) — spec-kit fork grown into a worktree-parallel "governed software factory"; imported parent history verifiable in `first_commit`. What did the fork change in the parent's pipeline?
- [**haft**](haft.md) — decision-governance pole (FPF: typed records, evidence decay); heaviest runtime in the category (2k+ Go files). Encoded methodology or memory extension?

## Candidates

The "Considered, not added (2026-07-28)" table moved to the cross-category
[candidates ledger](../candidates.md) on 2026-08-18 ([ADR-0009](../../adrs/0009-candidates-ledger.md)) —
candidate is now the named pre-report step of the engagement ladder, one ledger for
all categories.

## Spec-Driven Development (SDD)

*(Added 2026-08-18 — the term was already load-bearing in the reports but defined nowhere.)*

**SDD** names the category-4 sub-family whose organizing artifact is the **specification**:
written first, machine-validated, and treated as the *generator* of the implementation
rather than documentation that guides it. The term is vendor-coined — it is
[spec-kit's own branding](spec-kit.md) — but third-party usage has settled on a
recognizable set, the "2026 SDD trio": **BMAD / spec-kit / OpenSpec** (so named in the
[OpenSpec report](openspec.md)). The repo now tracks all three: spec-kit and
OpenSpec (the ceremony and lean poles respectively) deep-dived first, and BMAD
deep-dived 2026-08-18 — whose read complicates the pole labels: v6 is shedding ceremony
while remaining the most prose-governed of the trio ([report](bmad-method.md)).

SDD is a sub-family, not the category: **GSD is category 4 without being SDD** — its organizing
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

## Mechanisms — the unit of value

*(Added 2026-07-28 after experiment 01. "GSD is a category-4 tool" proved true and nearly
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
- ~~Claude Code ships plan mode natively. Where's the line between a harness's built-in
  process features and an installed framework — and is category 4 being absorbed into category 2?~~
  **Answered 2026-08-18** — systematized against the feature registry: 6 of the 9
  category-4 keys have ≥2 verified harness-native instances, at `engine`/`hook` grades the
  frameworks themselves never reach; the unabsorbed remainder is exactly the SDD spine
  (intent pipeline, format gates, workflow-scoped state). The line, on current evidence:
  harnesses absorb *mechanisms*, methodology stays here. →
  [category-2 index, "What category 2 has absorbed"](../2-harnesses/README.md#what-category-2-has-absorbed--the-category-4-feature-set-checked-against-harnesses)
- ~~Neither is easy to A/B test, since you can't run the same task twice cleanly. What
  would a fair comparison even look like?~~ **Working answer 2026-07-28:** preregister
  the protocol and falsification criteria, run the contaminated arm second with fresh
  subagent contexts, log during (not after), and state n honestly. Experiment 01 is the
  template; its limitations section is part of the answer.
