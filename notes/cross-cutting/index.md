# Cross-cutting concerns

`checked: 2026-07-28`

These are **not layers**. Each appears at several layers simultaneously, and forcing them
onto the stack distorts them. See [`../../taxonomy.md`](../../taxonomy.md).

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
- Subagent isolation — spawning a fresh context to protect the main one.
- Just-in-time loading — skills that load on demand rather than up front.

**Candidate first experiment.** One task with real ambiguity in an unfamiliar mid-size
codebase, run three ways: no rules file, a hand-written one, a generated one. Same model,
same harness, notes on *where each run went wrong* rather than whether it succeeded.
Failure modes are the signal; success is too coarse to learn from.

---

## Verification & evaluation

**Where it lives:** layer 3 (review-bot MCP servers), layer 4 (frameworks that build in
verification gates — GSD's "evidence" principle), layer 5 (sandboxes that make failure
cheap to observe), plus the whole external CI apparatus.

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

**Open question that gates everything:** you can't run the same task twice cleanly — the
first run changes the repo and your own understanding. So what does a fair A/B even mean
here? Until that's answered, every comparison in this repo is anecdote, and it should say so.

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
