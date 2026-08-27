# Experiment 01 — GSD vs. plain agent on a deliberately small task

`preregistered: 2026-07-28` · status: **complete — results below** (protocol section
unchanged from preregistration; results appended after)

This file is written and committed **before** either run, so the protocol can't drift to
flatter the result.

---

## Results (appended 2026-07-28, after both runs — see `log.md` for the full trail)

### Cost — measured from session + agent transcripts (superseding the earlier estimate)

*(Initial accounting used the harness's per-agent notification metric, which summed to
"~1.47M subagent tokens." Transcript measurement shows actual subagent **output** was
346k — the notification metric is an opaque blend ~4× output. Same lesson as
`stats-cache.json`: measure from transcripts, not metadata. Methodology rule 5c was
added because this table's first version couldn't answer "what did it actually cost?")*

| Measured tokens | Run A (plain) | Run B (GSD) | Multiple |
|---|---|---|---|
| Output — orchestrator | 16.8k | 186k | — |
| Output — subagents | 0 | 346k | — |
| **Output — total** | **16.8k** | **532k** | **~32×** |
| Cache write — total | 26k | ~7.9M | ~300× |
| Cache read — total | 8.5M | ~141.6M | ~17× |
| Wall-clock | ~1 min | ~78 min | ~78× |
| Commits | 0 (uncommitted) | 15 (5 planning, 10 delivery) | — |
| Product LOC | 224 (3 files) | 763 (4 files) | 3.4× |
| Process LOC | 0 | ~3,750 across 16 planning docs | ∞ |

Rough dollar band (estimated — token figures above are measured; prices assumed at
Sonnet $3/$15, Opus $15/$75, session model $10/$50 per Mtok with standard cache rates):
run A ≈ **$10**, run B ≈ **$180–200**, so roughly **20×** in money.

**The cost surprise:** the *orchestrator*, not the subagents, dominated run B's cost —
~92M cache-read tokens accumulated by driving 15 stages from one long-lived context
(≈2/3 of estimated spend). The subagents' fresh contexts were comparatively cheap. This
directly validates GSD's own "run `/clear` between stages" advice and suggests the
cheapest big optimization is a thinner orchestrator, not thinner agents — relevant to
the "which mechanisms buy the margin" follow-up.

### Quality

- **Preregistered functional checks: tie, 6/6 each.** (The 7th check was a bug in the
  comparison script — both tools were right.)
- **The decisive delta:** against a fixture with a genuinely invalid-UTF-8 author name
  (creatable only via `git hash-object`, exactly as GSD's researcher demonstrated),
  **run A crashes with an unhandled `UnicodeDecodeError`; run B renders correctly.**
  The pitfall was predicted by research, became requirement DATA-05, was enforced by a
  plan gate, and was verified twice. That chain is the framework working exactly as
  advertised.
- Latent (unexercised) run-A defects found by run B's process: no `--no-renames` pin
  (ambient-config sensitivity), no locale forcing, undocumented merge policy,
  timezone-dependent behavior undocumented. Tests: 5 vs 21; run B's README documents
  caveats run A's author (me) didn't know existed.
- Run B also produced knowledge as a side effect: `--since` filters committer date while
  columns show author date; bare `--since` dates are timezone-dependent; `.mailmap`
  doesn't apply to `%an`. None of this is in run A.

### Verdict against the preregistered falsification criteria

The **mixed outcome** — near-equal functional surface at a large cost multiple, with a
real robustness margin for GSD — which the prereg called "the expected boring outcome."
But two things weren't boring:

1. **The margin is real, not cosmetic.** One genuine crash-class difference (DATA-05)
   and four latent-defect classes. For a tool meant to be *used*, run B is the one you'd
   ship; for a tool meant to *exist by tonight*, run A won 77 minutes ago.
2. **Where the value concentrated:** the empirical researchers and gate-running planner
   — agents that **measured git instead of believing their training data** — produced
   nearly all of the quality delta. The process ceremony around them (STRIDE threat
   model for a read-only CLI, three no-op default hooks, ROADMAP bookkeeping the
   framework itself kept forgetting to tick) produced nearly none of it. The
   interesting follow-up isn't "GSD vs plain" but **"which 20% of the ceremony buys
   80% of the margin"** — a cheaper harness that keeps empirical research + gates and
   drops the rest.

### Answer to the layer-4 index question

*"What's the task-size threshold below which the ceremony costs more than it saves?"* —
this task sits **below** the threshold for build-speed purposes and arguably **above**
it for ship-quality purposes. The threshold isn't one number; it splits by what "saves"
means. Recorded in `notes/04-workflow-frameworks/gsd-core.md`.

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

## Post-run note — 2026-08-18 (probe-reachability finding from the gsd-core deep-dive)

*(Dated, appended post-run per rule 5; the protocol and results above are untouched.)*

The 2026-08-18 gsd-core deep-dive found that GSD's spec-phase edge/prohibition probes
were unreachable dead prose from 2026-06-12 to 2026-07-31 — including at this
experiment's pin (d04592de, 2026-07-28). This does **not** touch the empirical-grounding
credit assigned above: the measured behavior observed here (fixture repos, crafted
commits, timezone probes) came from the researcher/planner instructions, which were
live. It does mean any reading of this experiment that attributes grounding to the
*spec-phase probe steps* specifically would be wrong — they could not have executed at
this pin. Details: [`notes/04-workflow-frameworks/gsd-core.md`](../../tools/4-workflow-frameworks/gsd-core.md).
