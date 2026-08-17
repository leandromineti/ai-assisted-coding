---
title: "The AI-Coding Stack: a Map for a Landscape That Won't Sit Still"
date: 2026-08-17
description: "Models, harnesses, and execution environments — plus the two interfaces between you and them. A working taxonomy of AI-assisted coding tools, built from reading source code rather than marketing pages."
tags: ["ai", "developer-tools", "taxonomy"]
maturity: seed
draft: true
series: "AI-Assisted Coding, Measured"
seriesOrder: 1
---

Every week ships a new AI coding tool, and every announcement uses the same words:
agent, context, autonomous, 10x. If you try to reason about "AI coding tools" as one
category, you end up comparing a frontier model to a YAML workflow runner to a
Firecracker microVM vendor — and the comparison produces noise, because those are not
three competitors. They are three *layers* of one stack.

Since late July 2026 I've been keeping a small public research repo,
[ai-assisted-coding](../README.md), with one rule: claims come from reading source
code and running preregistered experiments, not from launch posts. This article is
the map that survived a month of that. The next one in this series is about what
happened when I started measuring.

## The core triad

<figure>
  <img src="img/the-core-triad.svg" alt="Minimal diagram of the core triad: a small person figure labeled You, centered above a Harness container and connected to it by a vertical double-headed arrow. Inside the harness, the Model is a wide horizontal slab nearly filling its width, lifted by a soft drop shadow — a mounted, swappable component, like a card seated in a chassis. Below the harness sits an equal-width Execution environment box, and the two are joined in a circular loop: an arrow labeled actions curves out of the harness's right side down into the environment, and an arrow labeled feedback curves out of the environment's left side back up into the harness. The model carries the diagram's only accent color." />
  <figcaption>The core triad: you talk to a harness, a swappable model is seated inside it, and the harness runs a loop of actions and feedback against an environment.</figcaption>
</figure>

Strip any working coding agent to the parts it cannot lack and three things remain
([the full taxonomy](../taxonomy.md)):

**Models** — the weights, and the API surface around them. This layer drifts fastest:
pricing, caching economics, effort controls, and lifecycle stages change monthly (one
vendor repriced its entire API to time-of-day billing the day before I checked
[its row](../notes/01-models/deepseek-v4.md)). The part nobody advertises: vendors
don't even share a lifecycle vocabulary — of ten models I track, one has been "in
Preview" for six months with no GA plan stated, another's GA was quietly suspended
three days after launch and redeployed weeks later
([the released column](../comparisons/models.md), verified 2026-08-17).

**Harnesses** — the software that turns a model into an agent: the loop that
assembles context, offers tools, executes actions, and decides when to stop. Claude
Code, Codex CLI, OpenCode, Cursor. This is the layer most discourse treats as
plumbing. It isn't, and there's now good evidence it isn't — more below.

**Execution environments** — where the agent's actions actually land: your host, a
git worktree, a devcontainer, a cloud microVM. For weeks I suspected this layer was
just an *attribute* of the harness ("where does it attach?"), and the repo carried a
pre-committed demotion rule for it. Then the first environment studied as a product
in its own right — E2B, read from its open-source infrastructure — produced roughly
[26 facts invisible from the SDK](../notes/05-execution-environments/e2b.md): every
"create" is secretly a snapshot resume, the guest's memory compactor is disabled for
the host's snapshot-diff economics, the credential-injection proxy doesn't exist in
the open-source build. An interface that hides that much is a layer, not an attribute
(decided 2026-08-16, [conclusion 9](../README.md#conclusions)).

## The harness is a capability layer, not plumbing

The cleanest evidence predates the current tool wave. The SWE-agent paper (NeurIPS
2024) held the model fixed and redesigned only the *interface* the agent works
through — and moved SWE-bench Lite from 11.0% (bare Linux shell) to 18.0%, a +64%
relative improvement from interface design alone
([full read notes](../refs/swe-agent-2024.md)). The same paper contains my favorite
negative result in the field: a search tool faithfully copied from *human* UI
patterns scored **below having no search tool at all**. Tool existence is not tool
value; a checkmark on a feature matrix can be negative.

The people building harnesses know all this and disagree with each other about what
follows. On the question of whether models have "converged" enough to share one
prompt, the three major portable harnesses answer three different ways: one maintains
nine bespoke per-model prompts sharing zero substantive lines, one built that
architecture and then dismantled it, and one runs ~15 lines and bets the prompt
barely matters ([the comparison](../notes/02-harnesses/index.md), 2026-07-28). Nobody
backs their position with a published eval. When the practitioners best placed to
know can't agree, "the harness doesn't matter" is not a safe assumption.

## The two interfaces

<figure>
  <img src="img/the-ai-coding-stack.svg" alt="The same triad diagram with exactly two additions. Between the centered You figure and the Harness, a dashed harness-width box labeled Workflow framework now intercepts the vertical arrow — a layer you may put between yourself and the harness, its connection to the harness implied by touching distance. Inside the harness, below the accent-colored Model slab, a second mounted slab labeled Extensions lists MCP, skills, rules, hooks, and memory. The actions/feedback loop between harness and environment is unchanged from the first diagram." />
  <figcaption>The full stack is the triad plus two additions: a process layer between you and the harness, and extensions seated inside it alongside the model.</figcaption>
</figure>

Between you and that triad sit two things that look like layers but behave like
boundaries.

**Extensions** — MCP servers, skills, rules files, hooks, memory stores: packaged capabilities
that plug into a harness. Portability is not an intrinsic property of an extension —
it's a status the ecosystem confers by adoption, and it has been conferred very
unevenly across the four kinds ([the taxonomy's bucket](../taxonomy.md) tracks
exactly this). As of my last scoreboard check, exactly
one of these has fully standardized (MCP, with a spec and version negotiation). Two
more — skills and rules files — are converging as *filename conventions* rather than
standards: `SKILL.md` is now consumed by at least five harnesses, and one vendor's
project-init flow offers to link seven *competitors'* rules files into its own
([the Warp evidence](../notes/02-harnesses/warp.md), 2026-08-11). Hooks and subagent
definitions remain harness-specific. "Write once, run anywhere" is true for exactly
one extension kind and a polite fiction for the rest
([conclusion 3](../README.md#conclusions)).

**Workflow frameworks** — spec-kit, GSD, and their cousins: processes that refine
your intent into specs and subtasks going down, and carry research and verified
evidence coming up. Their structural bind, visible in their git histories: they buy
cross-harness portability by being made of prompts, which means their runtime *is
the model reading prose*. One framework fixed its hook execution twice by rewriting
instructions "more forcefully" — enforcement by typography — and left its
constitution unenforced during implementation for eight months
([the spec-kit source read](../notes/04-workflow-frameworks/spec-kit.md),
2026-07-28). Both frameworks I studied eventually grew small deterministic engines as
escape hatches. Portability and enforcement power are the same tradeoff
([conclusion 7](../README.md#conclusions)) — a finding independently reproduced by a
[six-framework academic study](../refs/from-prompt-to-process.md) using documentation
analysis alone.

## The stack is being eaten from the middle

The reason this map needs dates on it: the layers don't respect each other's
territory. Mechanisms that adjacent layers sell keep turning up *natively in
harnesses* — turn-end verification gates, autonomous memory loops, programmatic tool
calling, plan modes ([conclusion 8](../README.md#conclusions), from the
[hermes](../notes/02-harnesses/hermes-agent.md) and
[codex](../notes/02-harnesses/codex.md) deep-dives). One harness now treats *rival
harnesses* as swappable execution backends for its own multi-agent orchestration —
absorption sideways, not just up and down. Any claim that "you need layer X for
capability Y" has a shelf life, and any measured margin for a workflow framework has
to be re-baselined against what the harness underneath already does.

## Why bother with a map

Because the alternative is reasoning from benchmarks that can't see layer boundaries.
Public leaderboards score *pairings* — "Codex CLI + GPT-5.5" — so nobody knows which
layer they're praising. The one benchmark I found that fixes the harness to isolate
the model turned out to inherit that harness's per-model prompt dispatch: a confound
its own maintainer didn't know about until
[I reported it upstream](../notes/01-models/index.md)
([conclusion 2](../README.md#conclusions)).

The frustrating part is that the isolation the field lacks is *buildable* — at
personal scale, for about $3 in API spend. That's what the next article in this
series is about: a pinned container, a hidden verifier, an enforced network
condition, and what a preregistered A/B actually said about whether workflow
frameworks buy code quality.

---

*Everything here links into the [research repo](../README.md), where each claim
carries its verification date. If a link contradicts this article, the link is
newer — trust it.*
