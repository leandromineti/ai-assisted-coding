# Cross-cutting concerns

`checked: 2026-08-17`

These are **not layers**. Each appears at several layers simultaneously, and forcing them
onto the stack distorts them. See [`../../taxonomy.md`](../../taxonomy.md).

---

## Benchmarks as instruments → [`benchmark-survey.md`](benchmark-survey.md)

**Where it lives:** every layer at once — a benchmark score binds a model, a harness, and
an environment into one number (conclusion 2), and vendor span makes that binding
structural. The survey's thesis: the field ships instruments with at most one of the
three properties an instrument needs (headroom, validity, contamination control) and
retrofits the rest after scores mislead. Written 2026-08-17 from 13 refs; the generated
[benchmark matrix](../../comparisons/benchmarks.md) is its catalog half.

---

## Context engineering

**Where it lives:** layer 2 (the harness decides what to load and when), layer 3 (rules
files, skills, memory), layer 4 (frameworks impose context discipline as method). No single
layer owns it — which is exactly why it's mis-taught as a prompting trick.

**The core tension:** more context is not better context. Every token of standing
instruction competes with the tokens the model actually needs for the task, and irrelevant
context measurably degrades attention on the relevant parts.

**Sub-topics to work through:**

- Rules files — `CLAUDE.md` / `AGENTS.md`. Marginal value of length, and where it turns negative.
- Retrieval vs. dumping — repo maps, semantic search, `grep`-driven exploration.
- Memory — persistent facts across sessions, and when stale memory is worse than none.
- Compaction — what survives a summarization, and what silently doesn't.
- Subagent isolation — spawning a fresh context to protect the main one. *Evidence in
  both directions (2026-07-28):* GSD's fresh-context stages caught each prior stage's
  vagueness (the refinement funnel, experiment 01); spec-kit tried forking its
  `/analyze` command into a subagent context and **reverted** it — the 300–500-line
  report re-entered the main chat anyway and each later fork inherited the growth,
  compounding until sessions froze (#3185). Isolation only pays if the *return path* is
  compact — see [`../04-workflow-frameworks/spec-kit.md`](../04-workflow-frameworks/spec-kit.md).
- Just-in-time loading — skills that load on demand rather than up front.

**Candidate first experiment.** One task with real ambiguity in an unfamiliar mid-size
codebase, run three ways: no rules file, a hand-written one, a generated one. Same model,
same harness, notes on *where each run went wrong* rather than whether it succeeded.
Failure modes are the signal; success is too coarse to learn from.

---

## Verification & evaluation

**Where it lives:** layer 3 (review-bot MCP servers), layer 4 (frameworks that build in
verification gates — GSD's "evidence" principle), layer 5 (sandboxes that make failure
cheap to observe), plus the whole external CI apparatus. **And, as of 2026-07-30, layer 2
natively — two instances:** hermes-agent ships an evidence-ledger verification gate
inside the harness — `verification_stop` nudges the model back (bounded, ≤3 times) when
it tries to finish right after editing code without fresh verification evidence, plus a
`pre_verify` plugin hook for user policy. codex's stop hooks occupy the same
architectural slot with more teeth: a stop hook can **veto turn termination** and inject
a continuation prompt (`session/turn.rs`, confirmed at the branch site same day). That's
exp-01's "measured verification gate" mechanism — the one conclusion 6 credits with the
layer-4 quality margin — living below layer 4, twice.

**Implication for experiment 03 (recorded before its design):** if harnesses ship
verification gates natively, the layer-4 margin can migrate down the stack. The
minimal-harness protocol must inventory what the *harness* already enforces before
attributing any gate effect to the framework layer — otherwise exp-03 risks crediting
layer 4 for a mechanism the layer-2 baseline silently exercises. (Hermes' gate is
weaker than exp-01's: its evidence bar is "ran something fresh", not a hidden verifier —
the distinction between *a* gate and a *measured* gate matters and should be scored,
not blurred.)

**Gate vocabulary for exp-03 (added 2026-07-31, openspec read):** three mechanisms,
two axes (deterministic?, domain-contact?): **format** gates — deterministic checks on
artifacts (OpenSpec's validator rejecting malformed/zero-delta changes); **prose**
gates — the model reading gate instructions (spec-kit's constitution check, README
conclusion 7's enforcement-by-typography); **measured** gates — checks against
measured domain behavior (GSD/exp-01, the rig's hidden verifier). Only measured gates
traced to exp-01's quality margin. Exp-03's "minimal harness" must therefore hold
*measured* gates as its ingredient, and score any format/prose gating in either arm
separately — a fully deterministic framework can still never touch the domain.
**Priced instance for the format quadrant (2026-08-17,
[swe-agent-2024](../../refs/swe-agent-2024.md)):** SWE-agent's in-`edit` linter — a
deterministic, no-domain-contact gate that discards invalid edits mechanically — is
worth a measured **+3.0pp** on SWE-bench Lite, and the paper's recovery curve shows
why: edit-success odds halve after a single failed edit, so the gate's value is
cascade *prevention*, not correctness checking. Format gates are not zero; they are
bounded by what syntax can see. Exp-03's scoring should keep the quadrants separate
precisely because both now carry measured, non-equal values.

**Why it's first-class here:** it's the least-explored part of the field and the one that
decides whether any of the rest is working. Everyone measures whether they *feel* faster.
Almost nobody measures whether the output is *better*.

**Sub-topics:**

- Tests as the agent's feedback loop — TDD-with-agents as a control strategy, not a ritual.
- Review bots — CodeRabbit, Greptile, and harness-native review commands.
- Agent-run observability — what did it actually do, and can you reconstruct why?
- Benchmarks — SWE-bench, Terminal-Bench. Note they measure **model + harness together**,
  never a model alone.
- Personal eval — the hard and interesting one: how would *you* tell whether a technique
  helped, on your own work, without a leaderboard?

**The question that gates everything — partially answered (2026-07-28):** you can't run
the same task twice cleanly — the first run changes the repo and your own understanding.
Experiment 01's working answer: preregister the protocol and falsification criteria
before any run, run the contaminated arm second with fresh subagent contexts, log during
(never reconstruct), and state n honestly (methodology rule 5;
[`experiments/01-gsd-vs-plain/`](../../experiments/01-gsd-vs-plain/README.md) is the
template). The epistemic caveat stands: n=1 preregistered is a *probe*, not a proof —
but it's no longer anecdote, and the difference is the preregistration.

---

## Cost & economics

**Where it lives:** layer 1 (token prices), 1b (route-dependent caching and rate limits),
layer 2 (how efficiently the harness spends context), layer 5 (metered sandboxes).

**The framing that matters:** per-token price is the least interesting form of cost. The
ones that bite:

- **Cost per completed task** — a cheap model that needs four attempts isn't cheap.
- **Cost of a failed run** — including the human time spent discovering it failed.
- **Review time** — the dominant cost once generation is nearly free, and the thing that
  actually caps throughput.
- **Cost shape** — a flat subscription and a metered API bill push behavior in opposite
  directions, independent of the total.

Grok 4.5's pitch is explicitly this argument: ~60% cheaper per token than the frontier
tier, and roughly half the *per-task* cost in Codex. Whether per-task savings survive
contact with harder tasks is the thing to check.

One measured data point so far (2026-07-28, experiment 01, transcript-measured per
methodology 5c): a layer-4 framework cost **~30–50× the plain-agent baseline** on a
below-threshold task — and the orchestrator's cache reads, invisible to per-agent
notification metadata, dominated the spend. Framework overhead is a real line item, and
it hides in the aggregates.

**Measure from transcripts, not from aggregates** (personal experience, mid-2026): Claude
Code's `stats-cache.json` inflates cache reads by roughly 2.6x and can't be trusted for
cost analysis. Parsing the session transcripts directly is the reliable route. Two things
that bite when you try it: transcripts auto-purge after about 30 days per install, so
long-run analysis needs its own archive; and a single user can accumulate several data
roots (machine changes, a Windows→WSL move), which have to be combined — session IDs are
disjoint, so there's no double-counting risk in doing so.

---

## Human practices

Techniques with no tool attached: task decomposition, when to restart a context, review
discipline, knowing when to stop and write the code yourself. Filed here rather than as a
layer, because there's nothing to install.
