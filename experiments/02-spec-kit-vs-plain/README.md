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
