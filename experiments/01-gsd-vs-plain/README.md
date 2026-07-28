# Experiment 01 — GSD vs. plain agent on a deliberately small task

`preregistered: 2026-07-28` · status: **preregistered, not yet run**

This file is written and committed **before** either run, so the protocol can't drift to
flatter the result.

## Question

The layer-4 index records this open question about workflow frameworks: *what's the
task-size threshold below which the ceremony costs more than it saves?* This experiment
probes it from below — one task chosen to be **smaller** than the threshold, run twice.
If GSD wins even here, the ceremony is cheaper than assumed; if plain wins, we have a
first data point for where the floor is.

## Task (identical prompt for both runs)

> Build `gitwho`, a Python CLI that summarizes contributor activity for a git
> repository. Given a repo path (default `.`), it prints a per-author table: commits,
> lines added, lines deleted, first and last commit date. Support `--since DATE` to
> restrict the window and `--json` for machine-readable output. Sort by commit count
> descending. Handle a directory that isn't a git repo, and an empty repo, with clear
> errors and non-zero exit. Include tests and a README.

Size rationale: ~100–200 lines of Python, one file plus tests — a task a competent
developer finishes in an afternoon without writing a plan.

## Protocol

- **Run A — plain**: the session agent builds it directly in a fresh directory. No
  framework, no planning artifacts, whatever workflow feels natural.
- **Run B — GSD**: the same task in a fresh git repo through the installed GSD flow:
  `new-project → plan phase → execute phase → verify`. GSD's own artifacts left intact.
  Subagents run on Opus/Sonnet per standing machine rule (never the session model).
- Run A executes **first**. Contamination direction is therefore known and one-way: the
  orchestrating agent has seen a solution before run B begins. Mitigation: run B's
  planning and execution happen in *fresh subagent contexts* that do not share the
  session's memory of run A; the orchestrator's contamination surface is limited to
  answers it gives during GSD's discovery questions, which will be logged verbatim in
  the run log.
- Both runs happen in scratch space; key artifacts are copied into `artifacts/` here
  afterwards. `log.md` is appended to *during* the runs, not reconstructed after.

## Measurements (decided now)

| Metric | How measured |
|---|---|
| Wall-clock per run | session timestamps |
| Model invocations | count of LLM-bearing steps: subagent spawns + orchestrator turns |
| Artifacts produced | file count and LOC, split into product vs. process files |
| Correctness | same manual test script run against both: normal repo, `--since`, `--json`, non-repo dir, empty repo |
| Test quality | do the tests exercise the real git path or mock it away (the llm-coding-benchmark lesson) |
| Where structure helped / bound | qualitative, logged during run B |

## What would falsify what

- **GSD's bet** ("agents fail from insufficient structure") predicts run B's output is
  materially better — more edge cases handled, better tests — even on a small task.
- **The ceremony hypothesis** predicts near-equal output quality at a multiple of the
  cost (time, calls, files).
- A mixed result (better tests, big cost multiple) is the expected boring outcome; the
  interesting outcomes are the two ends.

## Known limitations

- n=1, one task, one session, non-blind scoring by the same agent that ran both. This is
  a probe, not a proof — the point is a first honest data point and a reusable protocol.
- The orchestrator answers GSD's discovery questions itself (logged), which understates
  the value GSD gets from a genuinely engaged human.
