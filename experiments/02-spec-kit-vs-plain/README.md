# Experiment 02 — spec-kit vs. plain agent: does intent capture alone buy code quality?

`preregistered: 2026-07-28` · status: **not yet run** ·
**amended 2026-07-28 (pre-run — see Protocol amendment at the end; original text
untouched)**

This file is written and committed **before** either run, so the protocol can't drift to
flatter the result. Protocol follows the template set by
[`../01-gsd-vs-plain/`](../01-gsd-vs-plain/README.md); results will be appended below the
untouched protocol.

## Question

Experiment 01 found a workflow framework's quality margin concentrated in **empirical
grounding + measured verification gates** (README conclusion 6). The spec-kit source read
(2026-07-28) profiled spec-kit as strong in exactly the opposite column — **intent
capture** — and thin in the two that carried exp-01's margin. This experiment runs
spec-kit for real, which simultaneously:

1. tests the mechanism-profile prediction below,
2. closes methodology rule 8's gap for spec-kit (currently *read*, never *run*), and
3. prices spec-kit's core bet — spending **human attention early** (clarify questions)
   to save rework later — using the attention-time instrument exp-01 lacked.

## Preregistered predictions

From spec-kit's mechanism profile
([`notes/04-workflow-frameworks/spec-kit.md`](../../notes/04-workflow-frameworks/spec-kit.md)):

- **P1 — requirements:** the spec-kit arm produces materially better *written
  requirements* than the plain arm (rubric below).
- **P2 — code:** the spec-kit arm's *code* is equal-or-worse on the seeded traps — its
  pipeline never measures the domain, so trap discovery should not beat a plain agent's.

**What would damage what:**

- If spec-kit's code **beats** plain on traps materially → conclusion 6 is damaged
  (intent capture alone buys ship-quality margin) and the mechanism profile mis-modeled
  where value lives.
- If spec-kit's requirements are **not** better → its core value proposition fails on
  home turf.
- If P1 and P2 both hold → the profile method is validated, and experiment 03 (minimal
  harness: grounding + gates only) proceeds against a confirmed baseline.

## Task (identical prompt for both arms)

> Build `tarpeek`, a Python CLI that summarizes the contents of a tar archive without
> extracting it. Given an archive path, print a per-member table: name, type
> (file/dir/symlink), size in bytes, and last-modified date. Support `--min-size BYTES`
> to filter members and `--json` for machine-readable output. Sort by size descending.
> Handle a path that isn't a tar archive, and an empty archive, with clear errors and
> non-zero exit codes. The tool must never write to the filesystem. Include tests and a
> README.

Same size class as exp-01's `gitwho` (~100–200 lines plus tests, below the ceremony
threshold for build speed), same *shape* (CLI over a measurable domain with hidden
sharp edges), **different domain** — deliberately not git, because exp-01 taught the
orchestrator git's trap inventory and a git task would leak that knowledge into design
and scoring.

## Seeded traps (scoring fixtures, hidden from both arms)

Five classes, drawn from exp-01's *families* (encoding, time, exit codes, ambient
config, safety) — explicitly **not** from spec-kit's known blind spots, per the
contamination declaration below. Fixtures are built by
[`fixtures/build_fixtures.py`](fixtures/build_fixtures.py) (committed with this
protocol; deterministic by construction) and their ground truth is emitted to
`fixtures/expected.json` — *measured from what the builder actually built*, per
methodology rule 5a.

| # | Class | Fixture | Pass condition |
|---|---|---|---|
| T1 | Encoding | A member whose name contains raw non-UTF-8 bytes (ustar header written directly) | Lists the member without crashing (any lossless or replacement rendering acceptable; crash = fail) |
| T2 | Time | Members with mtime 0 (epoch) and far-future mtime (2106) | Renders both without crashing; date format documented |
| T3 | Exit codes | A non-tar file and an empty (valid, zero-member) archive | Both non-zero, **distinct** exit codes, distinguishable messages (exp-01's exit-code-collision analog) |
| T4 | Ambient config | Same archive listed under `TZ=UTC` vs `TZ=America/Sao_Paulo` | Output either invariant or the timezone dependence is documented in README |
| T5 | Safety | A symlink member targeting `../../outside` and an absolute path | Listed as data, target shown or omitted, **nothing resolved or written** on the host filesystem |

## Protocol

- **Run A — plain** (first): a fresh-context agent receives exactly the task prompt and
  builds in a scratch directory. No framework. Model: Opus (per standing machine rule —
  arms never run on the session model).
- **Run B — spec-kit** (second): a fresh scratch git repo, `specify init` with the
  Claude integration, then the pipeline **exactly as spec-kit's own quickstart
  prescribes** — constitution → specify → clarify → plan → tasks → analyze → implement —
  driven by a fresh-context agent (Opus). No step skipped, none added: the run is
  "as directed," not a steelman or strawman.
- Contamination direction is one-way and known: run A executes first; the orchestrator
  has seen a solution before run B. Mitigation as in exp-01: run B happens in fresh
  contexts; the orchestrator's contamination surface is limited to answers given to
  spec-kit's interactive questions, which are **logged verbatim** in `log.md`.
- Neither arm can read this repository. Both run in scratch space; artifacts are copied
  into `artifacts/` afterwards. `log.md` is appended *during* the runs, never
  reconstructed.
- Scoring runs `fixtures/build_fixtures.py` in a clean directory and executes both CLIs
  against the generated archives, comparing against `expected.json`.

## Measurements (decided now)

| Metric | How measured |
|---|---|
| **Cost ledger** | From session + agent transcripts' `usage` fields, per methodology rule 5c — from the start, not retrofitted. Output, cache write, cache read, per arm, orchestrator vs. subagents split |
| **Attention split** | Wall-clock divided into *autonomous* vs. *attention-required* (arm blocked on a human answer). Per blocking event: which command asked, the question, the verbatim answer, minutes blocked. This is the instrument that prices spec-kit's clarify bet |
| Wall-clock per arm | session timestamps |
| Trap score | T1–T5 pass/fail per arm, machine-checked against `expected.json` |
| Functional checks | normal archive, `--min-size`, `--json`, non-tar, empty archive — same script, both arms |
| **Requirements rubric (P1)** | Scored from each arm's *written artifacts only* (spec/README/tests-as-documentation, before reading code): R1 count of machine-checkable acceptance criteria as written; R2 count of documented assumptions; R3 how many of the five trap classes are *anticipated in writing*; R4 ambiguities surfaced (questions asked or explicitly flagged) |
| Test quality | do tests exercise real archives or mock the tar layer away (the llm-coding-benchmark lesson) |
| Where structure helped / bound | qualitative, logged during run B |

## Contamination declaration (known before the first run)

1. The orchestrator read spec-kit's source at survey depth on the preregistration date.
   Mitigations: this protocol is committed before any run; the task domain is fresh;
   traps are drawn from exp-01's classes, not from weaknesses found in spec-kit's
   source.
2. Scoring is non-blind and performed by the same agent that ran both arms (as in
   exp-01). The trap score and functional checks are machine-checked to shrink the
   judgment surface; the requirements rubric is the subjective remainder and is scored
   against the written definitions above.
3. The orchestrator answers spec-kit's interactive questions itself, which understates
   the value a genuinely engaged human might extract from the clarify loop — same
   limitation as exp-01's discovery questions, logged the same way.

## Known limitations

- n=1, one task, one session. A probe, not a proof.
- Cross-experiment comparisons to exp-01 (GSD, plain-on-gitwho) are cross-*task* and
  indicative only; the within-experiment A/B is the measurement.
- The plain arm produces no mandated artifacts, so the requirements rubric partially
  measures "does the framework force writing things down" — that asymmetry is part of
  spec-kit's claim, not a scoring bug, but it's named here so the rubric isn't read as
  neutral.

---

## Protocol amendment (2026-07-28, before any run)

Amended after the standardized-rig design session (user-directed). Every change below
applies **identically to both arms**; nothing above this line was edited.

1. **Model: Sonnet 5 (`claude-sonnet-5`), sole model for all arms** — supersedes "Opus"
   in the Protocol section. Rationale: user's decision to standardize layer-4
   comparisons on one mid-tier model; cheaper; machine-rule compliant.
2. **Execution environment: the rig container** ([`../rig/`](../rig/README.md)) —
   supersedes "scratch directories". The task is packaged in Terminal-Bench task format
   at [`../rig/tarpeek/`](../rig/tarpeek/); pinned base image, fixed TZ/locale,
   Claude Code CLI `2.1.220` headless. Container build pending Docker installation on
   this machine — runs blocked until then.
3. **Network policy: model API only.** Web tools denied at the harness layer inside the
   container; framework "research" phases can therefore only do local measurement.
   (v1 enforcement is harness-level, not egress-level — gap recorded in the rig README.)
4. **Task instruction packaging:** one sentence appended to the task prompt — *"Name the
   command `tarpeek` and install it so it runs from any directory (e.g. `pip install`
   the project or place an executable script on PATH)."* Required so a state-based
   verifier can find the artifact; adds no semantic requirements beyond installability.
5. **Verifier relocated and hardened:** scoring now runs the rig's hidden pytest
   verifier ([`../rig/tarpeek/tests/test_outputs.py`](../rig/tarpeek/tests/test_outputs.py)),
   which asserts against the same `fixtures/expected.json`. Proven fails-closed before
   any run: with no `tarpeek` installed all 8 checks error; against a do-nothing stub
   all 8 fail — the first stub run exposed vacuous T4/T5 passes (a no-op tool is
   trivially "timezone-invariant" and "write-free"), fixed by requiring real listing
   content inside those tests. That catch is the fails-closed rule earning its keep.

---

## Protocol amendment 2 (2026-07-31, AFTER the calibration run — declared as such)

Amendment 1 was written before any run. **This one is not**, and is labelled accordingly: Run A
executed on 2026-07-31 (see `log.md`) before these changes were known to be necessary. Nothing
above this line has been edited. Each item applies identically to both arms.

1. **Driver mechanism.** `--dangerously-skip-permissions` (amendment 1's implied mechanism, via
   the rig) is unusable: the CLI refuses it when running as root, exiting 0 without doing any
   work. Replaced by an explicit `permissions.allow` list in the container's
   `settings.json` — the intended headless mechanism, and one that verifiably preserves the
   web-tool deny. Scarred into methodology 5e.
2. **Network condition = `package-hosts-only`, enforced at the egress layer and probed.**
   Amendment 1's "model API only, harness-level enforcement, gap acknowledged" is superseded:
   the gap was measured real (`curl` reached the internet). See the rig README's § Network
   condition for the configuration and four probe results. Scarred into methodology 8a.
3. **Run A (2026-07-31) is a calibration run, not the scored baseline.** Its result stands as
   evidence about the *instrument* — it saturated the trap set at 8/8 — but it is not the arm
   the framework arm gets compared against, because it ran under the unenforced network
   condition. The scored baseline is re-run alongside Run B under one shared instrument and one
   shared condition.
4. **Open falsification problem, unresolved at the time of writing.** The trap instrument has no
   headroom: a perfect baseline means the framework arm cannot score *better*, so the
   preregistered damage condition ("if spec-kit's code beats plain materially → conclusion 6 is
   damaged") is unfalsifiable on this task. P1 (requirements rubric) is unaffected. The four
   options are listed at the end of `log.md`; **the choice is deliberately not made here**,
   because making it after seeing Run A's score and before Run B is exactly the kind of
   post-hoc instrument selection preregistration exists to prevent. It must be settled and
   committed before either arm runs again.

---

## Protocol amendment 3 (2026-08-17, before any further run — settles amendment 2's open problem)

Amendment 2 item 4 left the trap-instrument choice deliberately unmade. It is made here,
**before either arm runs again**, informed by a community-practice review ingested
2026-08-17 (refs: `aider-polyglot-2024`, `swebench-verified-2024`, `evalplus-2023`,
`paperbench-2025`; synthesis on issue #4). Nothing above this line is edited.

1. **Decision: option 1, executed EvalPlus-first.** The trap dimension is kept and the
   instrument is rebuilt by **densifying checks on the existing five trap families**
   (T1–T5). New fixture members are permitted *within* those families; **no new trap
   families in this step**. Rationale: Run A's 8/8 has two candidate causes — the
   baseline genuinely clears the families, or the per-family checks are too shallow to
   see partial clears — and only the first requires new task content (EvalPlus's
   finding: densifying tests ~80× made previously-"passing" HumanEval solutions fail).

2. **Legitimacy of designing against the calibration artifact.** Amendment 2 reclassified
   Run A as calibration; methodology 5d says the baseline run *is* the instrument's
   calibration. Selecting checks that the calibration artifact fails is the
   select-by-baseline-failure step (Aider polyglot: keep items solved by ≤3/7 baselines)
   applied at check granularity. The line preregistration protects is unchanged and
   uncrossed: **no instrument choice may follow a framework-arm run**, and none has
   occurred.

3. **Acceptance criterion: the three-point instrument-validity proof.** The rebuilt
   verifier is accepted only if all three hold, each demonstrated by a recorded pytest
   run in `log.md`:
   - **Fails-closed** — the do-nothing stub fails every check (re-proof of the
     2026-07-28 property against the new set);
   - **Fairness** — a **hardened reference implementation** (new apparatus at
     `../rig/tarpeek/reference/`, part of the instrument like `build_fixtures.py`,
     never a contestant) passes every check. No check enters the set without this —
     the SWE-bench Verified lesson (61.1% of its tests could reject valid solutions);
   - **Headroom** — Run A's artifact (`artifacts/run-a/`, installed into a clean venv)
     **fails ≥ 3** of the new checks.

4. **Scoring form.** The verifier becomes ~15–20 small binary checks (each family split
   into graded sub-checks), machine-checked only, equal weights, reported per-family and
   as a total. This is analytic partial credit (PaperBench's shape) without an LLM
   judge; the original 8 checks survive as a subset so prior results remain comparable.

5. **Escalation rule, fixed now in case it is needed.** If densification cannot meet the
   headroom criterion (≥3 calibration-artifact failures with all fairness checks
   passing), the EvalPlus step is recorded as exhausted and the instrument moves to the
   Aider step: a candidate pool of **new** trap families, screened by **5 fresh unaided
   baseline runs** in the rig under the enforced network condition, keeping candidates
   that fail in **≥2 of 5** runs, fairness-screened against the reference. Those
   screening runs are instrument calibration, not scored arms. This step costs real API
   spend and does not begin without the owner's sign-off.

6. **Unchanged:** both scored arms (Run A re-run + Run B) execute only after this
   instrument is accepted, under it, and under the enforced `package-hosts-only`
   condition — one instrument, one condition, both arms (methodology 8a). P1
   (requirements rubric) is untouched by this amendment.

---

## Protocol amendment 4 (2026-08-17, before either scored arm — the execution procedure)

Owner sign-off for the scored A/B received 2026-08-17 ("Lets perform the AB test").
Declared before Run A′ or Run B executes; nothing above this line is edited. The
instrument is the accepted 21 checks; the condition is `package-hosts-only`; the model
is `claude-sonnet-5`; the harness is Claude Code CLI 2.1.220 in the pinned image.

1. **Run A′ is the scored plain baseline.** Mechanically identical to a screening run
   (fresh container, instruction verbatim at `/root/instruction.txt`, allow-list
   settings, one autonomous `claude -p` session), scored against the accepted 21 in a
   fresh venv under the declared condition. The five screening runs remain calibration
   only, as declared when they ran; Run A′ is a fresh draw, and the A/B comparison
   reads **both** arms against the measured baseline noise band (18–20/21, mean 19.0,
   n=5) rather than treating either as a point truth.

2. **Run B pipeline = the seven preregistered steps.** The original protocol names
   constitution → specify → clarify → plan → tasks → analyze → implement. **Discrepancy
   disclosed:** the quickstart at the preregistration pin (655a3cb) prescribes a
   9-step "full path" that also contains `/speckit.checklist` and `/speckit.converge`
   (and a 4-step "shorter path" for small features that omits constitution and
   clarify). The preregistered enumeration governs — rewriting the step list in either
   direction now, after five baseline draws are known, would be post-hoc protocol
   editing. The tension between "exactly as the quickstart prescribes" and the
   7-step enumeration is recorded here as a preregistration imprecision, resolved in
   favor of the explicit list.

3. **Session structure: one fresh headless session per pipeline step** (`claude -p`,
   new session each step — the protocol's "fresh contexts", and spec-kit's own bet
   that state lives on disk in `.specify/`, exercised honestly). **Within a step**, if
   the turn ends awaiting user input (clarify by design; any other step incidentally),
   the same session is continued with `--resume`, and every such continuation is a
   logged blocking event: command, question, verbatim answer, minutes blocked — the
   attention instrument. Turn-level `usage` from `--output-format json` is the cost
   ledger, per step, per methodology 5c.

4. **What the orchestrator feeds each step** (fixed now to bound contamination):
   - `/speckit.constitution` — generic engineering-quality principles, no domain
     content: *"Focus on code quality, testing standards, user experience consistency,
     and clear error behavior."*
   - `/speckit.specify` — the task instruction **verbatim** (the identical prompt both
     arms receive, 651 chars).
   - `/speckit.clarify` — bare, no focus area.
   - `/speckit.plan` — only content already present in the task instruction: *"Python
     CLI, installable with pip so `tarpeek` runs from any directory."*
   - `/speckit.tasks`, `/speckit.analyze`, `/speckit.implement` — bare.
   - **Clarify-answer policy:** answer from the task instruction where it decides the
     question; where it is silent, defer with *"your call — make a reasonable choice
     and document the assumption"* (spec-kit's own default posture). The orchestrator
     never volunteers trap-family specifics (encodings, timezones, symlink targets,
     exit-code layouts) beyond what the instruction text states. All Q&A verbatim in
     `log.md`.

5. **Scaffold provisioning is framework installation, not agent work.** `specify init`
   needs GitHub egress, which the condition denies at runtime; the scaffold
   (`.specify/`, `.claude/commands/speckit.*`) is therefore produced **outside the
   network condition** — CLI installed from the pinned source checkout (655a3cb, the
   preregistration pin; source install is a documented first-party route) — and
   copied into the container before the agent's first turn, in a fresh git repo as
   the protocol requires. Exact provenance (CLI version, template origin, any
   init-time fetches) recorded in `log.md`. The agent runs entirely under
   `package-hosts-only`.

6. **Driver smoke test before the scored Run B (methodology 5e).** On the same image:
   multi-turn `--resume` continuation works headless; the `speckit.*` commands resolve
   as slash commands; step artifacts appear on disk. Success is read from artifacts,
   never exit status. The smoke uses a throwaway prompt, not the task; its (small)
   cost is recorded. A smoke failure blocks the arm, never edits the protocol.

7. **Failure and spend rules, fixed now:** an API-errored turn is retried once and
   both attempts logged. If Run B's cumulative cost crosses **$20** (≈2.5× the high
   end of the $2–8 estimate; issue #5 forbids projecting from exp-01), the run pauses
   and the owner decides — recorded either way. A structurally stalled pipeline is a
   finding to record, not a thing to rescue by ad-hoc prompting: rescue prompts beyond
   the declared inputs would turn the arm into a steelman.
