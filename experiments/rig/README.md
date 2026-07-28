# The rig — standardized task + sandbox for layer-4 framework comparisons

`created: 2026-07-28` · status: **files authored; verifier proven fails-closed
(no-binary → 8/8 error; do-nothing stub → 8/8 fail, after a hardening pass — the first
stub run exposed vacuous T4/T5 passes, fixed same day); container build pending Docker
install on this machine**

A reusable, pinned execution environment for comparing workflow frameworks fairly. First
consumer: [`../02-spec-kit-vs-plain/`](../02-spec-kit-vs-plain/README.md) (see its
pre-run amendment). Design rationale researched and decided 2026-07-28.

## What it is

Tasks are packaged in the **Terminal-Bench task format** (verified against
`harbor-framework/terminal-bench` samples, 2026-07-28 — the org moved from
`laude-institute`; task = `task.yaml` instruction + `Dockerfile` + hidden
`tests/` + `run-tests.sh`). The format was chosen because it is community-standard and
because its conventions match this repo's needs exactly:

- **Short natural-language instruction** — ambiguity is preserved, which is what
  workflow frameworks claim to handle (a fully-specified benchmark task would neutralize
  intent capture).
- **Pinned Docker environment** — the sandbox. Fixes exp-01's scars structurally: no
  ambient-cwd leakage into the host (the container *is* the blast radius), fixed
  `TZ`/locale, reproducible toolchain.
- **Hidden verifier over final container state** — complete ground truth the arms never
  see, measured (not assumed) per methodology rule 5a.
- **Canary GUID lines** — T-Bench's convention for keeping benchmark data out of
  training corpora; adopted in our task files since this repo is public.

## Pins (recorded here; placeholders resolved at first build)

| What | Pin |
|---|---|
| Base image | `ghcr.io/laude-institute/t-bench/python-3-13:20250620` (T-Bench's own base) — digest recorded at first build: `PENDING` |
| Harness | Claude Code CLI `2.1.220`, installed in-image via npm, run headless |
| Model | `claude-sonnet-5` — sole model, all arms, all frameworks |
| Framework versions | pinned per experiment in its preregistration (exp-02: spec-kit @ `655a3cb`) |
| Rig image digest | `PENDING` (requires Docker; not installed on this machine at authoring time) |

## Harness decision: Claude Code, not an open-source harness

Recorded reasoning (2026-07-28):

1. Claude Code is the only harness where **both** current subjects are first-class:
   gsd-core officially targets Claude Code/Codex/Gemini CLI/Cursor/Windsurf/Copilot (no
   opencode; a community port exists but is unofficial), and spec-kit targets 40+
   including Claude Code. An open-source harness would introduce a framework-maturity
   confound larger than the closed-source cost.
2. Terminal-Bench itself ships Claude Code as a supported agent, so this is a
   community-benchmarked configuration.
3. Reproducibility is carried by **pins + committed transcripts** (CLI version, image
   digest, model ID, framework commits, full session transcripts in each experiment's
   `artifacts/`), not by harness source access.

**Recorded costs of this choice:** context assembly inside Claude Code is unobservable,
and vendor updates can shift behavior between experiments — mitigated by pinning the CLI
version per experiment and never comparing across CLI versions. **Fallback:** opencode
(spec-kit supports it) if a future subject lacks Claude Code support.

## Driver protocol

The T-Bench task *format* is adopted; the stock autonomous runner (`tb run`) is not —
spec-kit's clarify loop requires interaction, and pricing that interaction
(autonomous vs. attention-required time) is one of the experiment's instruments. The
orchestrator drives each arm as headless Claude Code sessions inside the container,
logging every blocking question and answer verbatim to the experiment's `log.md`.
Running a plain arm under stock `tb run` later remains possible for loose comparison
against public T-Bench baselines.

Network policy: arms get **model API only**. v1 enforcement is at the harness layer
(container Claude Code settings deny WebSearch/WebFetch); hard egress filtering is
future work and the gap is acknowledged. Rationale: with no web access, framework
"research" phases can only do *local measurement* — the mechanism exp-01 found
load-bearing — so no arm can substitute web lookup for empirical grounding.

## Reuse rules

- **One plain baseline per task, reused by every framework tested on that task.** The
  comparable unit across frameworks is the *delta over plain*, never raw scores across
  different tasks.
- A task is a **consumable instrument**: once its traps have been exercised and
  discussed in this repo, new frameworks get scored on it only with the contamination
  declared, and genuinely fresh comparisons get a fresh task in the same trap-class
  family (encoding, time, exit codes, ambient config, safety).
- The verifier must be proven **fails-closed** before any arm runs: it must fail against
  an empty container and against a deliberately broken stub. A verifier that passes an
  empty environment is a scorer bug (exp-01, rule 5a).
- No `solution.sh` oracle is written before the arms run — T-Bench convention deviation,
  deliberate: the orchestrator implementing the task would deepen scorer contamination.
  Verifier satisfiability is instead proven by the first passing arm (or an oracle
  written *after* both arms, if neither passes).

## Tasks

| Task | Status | Used by |
|---|---|---|
| [`tarpeek/`](tarpeek/) | authored; image build pending | exp-02 (spec-kit vs plain), exp-03 planned (minimal harness) |
