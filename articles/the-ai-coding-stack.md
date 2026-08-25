---
title: "The AI-Coding Stack: a Map for a Landscape That Won't Sit Still"
date: 2026-08-17
description: "Models, harnesses, and execution environments — plus the two interface categories around them: workflow frameworks and memory. A working taxonomy of AI-assisted coding tools, built from reading source code rather than marketing pages."
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
three competitors. They are three *categories* of one stack.

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

### Models

The weights, and the API surface around them —
[Claude Sonnet 5](https://platform.claude.com/docs/en/about-claude/models/overview),
[GPT-5.6](https://developers.openai.com/api/docs/models),
[DeepSeek V4](https://api-docs.deepseek.com/quick_start/pricing). This
category drifts fastest: pricing,
caching economics, effort controls, and lifecycle stages change monthly (one
vendor repriced its entire API to time-of-day billing the day before I checked
[its row](../notes/01-models/deepseek-v4.md)). The part nobody advertises: vendors
don't even share a lifecycle vocabulary — of ten models I track, one has been "in
Preview" for six months with no GA plan stated, another's GA was quietly suspended
three days after launch and redeployed weeks later
([the released column](../comparisons/models.md), verified 2026-08-17).

Beyond benchmark quality, the axes that actually separate model APIs are the
surface around the weights: whether thinking is adaptive or a budget you set,
what the effort controls default to, the write/read economics of prompt
caching, whether batch pricing exists at all — tracked in each vendor's own
vocabulary in [the model matrix](../comparisons/models.md). And the route
matters as much as the name: the same model reached through a first-party
API, an aggregator, a cloud marketplace, or a local runtime is not the same
product — prompt-caching support, quantization, rate limits, and silent
context truncation all vary by route
([model access](../notes/01-models/index.md)).

### Harnesses

The software that turns a model into an agent: the loop that assembles context,
offers tools, executes actions, and decides when to stop.
[Claude Code](https://github.com/anthropics/claude-code),
[Codex CLI](https://github.com/openai/codex),
[OpenCode](https://github.com/anomalyco/opencode). This is the category most
discourse treats as plumbing. It isn't.

The cleanest evidence predates the current tool wave. The SWE-agent paper
(NeurIPS 2024) held the model fixed and redesigned only the *interface* the
agent works through — and moved SWE-bench Lite from 11.0% (bare Linux shell)
to 18.0%, a +64% relative improvement from interface design alone
([full read notes](../refs/2024-swe-agent.md)). The same paper contains my
favorite negative result in the field: a search tool faithfully copied from
*human* UI patterns scored **below having no search tool at all**. Tool
existence is not tool value; a checkmark on a feature matrix can be
negative.

Feature lists mislead here — the repo's own warning at the top of its
harness notes. The axes that actually differentiate harnesses, out of the
deep dives: context assembly (what gets loaded, when, and what gets
dropped), the permission model (how much it does without asking), the
extension surface (whether workflow frameworks, memory, and extensions can
attach at all), the isolation story (which execution environment it
assumes), failure behavior (what it does when it's wrong — where the real
cost lives), and cache economics (whether prompt-cache discipline is an
optimization or the architecture's governing rule)
([the six axes](../notes/02-harnesses/index.md)). Nine harnesses are
tracked, four of them traced to deep-dive depth
([the tool index](../comparisons/tools.md)).

### Execution environments

Where the agent's actions actually land: your host, a git worktree, a
devcontainer, a cloud sandbox like [E2B](https://github.com/e2b-dev/E2B),
[Modal](https://github.com/modal-labs/modal-client), or
[Daytona](https://github.com/daytonaio/daytona). For weeks I suspected
this category was just an
*attribute* of the harness ("where does it attach?"), and the repo carried a
pre-committed demotion rule for it. Then the first environment studied as a
product in its own right — E2B, read from its open-source infrastructure —
produced roughly
[26 facts invisible from the SDK](../notes/03-execution-environments/e2b.md): every
"create" is secretly a snapshot resume, the guest's memory compactor is disabled for
the host's snapshot-diff economics, the credential-injection proxy doesn't exist in
the open-source build. An interface that hides that much is a category, not an attribute
(decided 2026-08-16, [conclusion 9](../README.md#conclusions)).

Three questions organize the category: blast radius (what can the agent
damage), fidelity (does the project's tooling run unmodified inside), and
parallelism (how many agents at once, at what bootstrap cost) — and the
field's autonomy ceiling is set by blast radius, not model capability
([the taxonomy](../taxonomy.md)). How a harness relates to its environment
is a design position of its own, with exactly four verified shapes — bundle
one, bind to one, internalize one, inhabit one — plus a legitimate fifth:
deliberate abstention. [The environment-bindings
matrix](../comparisons/environments.md) tracks the products, the forms you
don't buy (host, worktree, devcontainer), and which harness holds which
position.

## The two additional interfaces

<figure>
  <img src="img/the-ai-coding-stack.svg" alt="The same triad diagram with exactly two additions. Between the centered You figure and the Harness, a dashed harness-width box labeled Workflow framework now intercepts the vertical arrow — a category you may put between yourself and the harness, its connection to the harness implied by touching distance. Inside the harness, below the accent-colored Model slab, a second mounted slab labeled Memory — persistent state that survives the session. The actions/feedback loop between harness and environment is unchanged from the first diagram." />
  <figcaption>The full stack is the triad plus two additions: a process category between you and the harness, and memory seated inside it alongside the model, carrying state from one session to the next.</figcaption>
</figure>

Around that triad sit two more categories that behave less like parts of the
machine and more like boundaries: workflow frameworks on the boundary between
you and the stack, memory on the boundary between one session and the next.

### Memory

Persistent cross-session state as an installable product —
[mem0](https://github.com/mem0ai/mem0),
[MemOS](https://github.com/MemTensor/MemOS),
[ai-memory](https://github.com/akitaonrails/ai-memory): fed by hooks during
the session, consolidated between sessions, injected back at the next session
start — on any harness ([the taxonomy's newest category](../taxonomy.md),
split out 2026-08-22). The category's survival bet is the one thing a single
harness cannot absorb: continuity *across* harnesses — measured real, and
entirely pull-shaped, in the repo's first memory probe
([conclusion 14](../README.md#conclusions), n=1 per arm). Two findings frame
the products below: they sell to coding agents but benchmark on chat
([conclusion 13](../README.md#conclusions)), and they share zero formats —
each vendor pays the harness-fragmentation cost separately, in code, up to
and including one product's plugin blocking the harness's native memory
writes to redirect them into its own store
([the memory index](../notes/05-memory/index.md)).

Where the products split is the interesting part: the store wager (a
git-versioned markdown wiki, a vector platform, a knowledge graph, a scored
policy database — no two alike), the capture path (hook, adapter, or
agent-invoked), whether recall is injected automatically or only when the
agent asks, and the trust axes — whether injected memory arrives framed as
data or with instruction authority, and who may revise a memory once it
turns out to be wrong ([the feature matrix](../comparisons/features.md)).
Eight products are tracked, three at deep-dive depth
([the tool index](../comparisons/tools.md)).

### Workflow frameworks

[spec-kit](https://github.com/github/spec-kit),
[OpenSpec](https://github.com/Fission-AI/OpenSpec),
[GSD](https://github.com/open-gsd/gsd-core), and their cousins: processes
that refine your intent into specs and subtasks going down, and carry
research and verified evidence coming up. Their structural bind, visible in
their git histories: they buy
cross-harness portability by being made of prompts, which means their runtime *is
the model reading prose*. One framework fixed its hook execution twice by rewriting
instructions "more forcefully" — enforcement by typography — and left its
constitution unenforced during implementation for eight months
([the spec-kit source read](../notes/04-workflow-frameworks/spec-kit.md),
2026-07-28). The first two frameworks I studied eventually grew small deterministic
engines as escape hatches. Portability and enforcement power are the same tradeoff
([conclusion 7](../README.md#conclusions)) — a finding independently reproduced by a
[six-framework academic study](../refs/2026-from-prompt-to-process.md) using documentation
analysis alone.

Decomposed across the studied set, a framework does four things: refines
intent into specs, decomposes work into concrete subtasks, flags gaps that
need research, and sets up verification that converts progress into
evidence. Intent flows down through the first two; evidence flows up
through the last two — and the preregistered experiments located nearly all
of the measured value in the last two and almost none in the ceremony of
the first two ([the four functions](../taxonomy.md),
[conclusion 6](../README.md#conclusions)). Nine frameworks are tracked,
four at deep-dive depth ([the tool index](../comparisons/tools.md)).

## The stack is being eaten from the middle

The reason this map needs dates on it: the categories don't respect each
other's territory. Mechanisms that adjacent categories sell keep turning up
*natively in harnesses* ([conclusion 8](../README.md#conclusions)) — and the
pattern looks different on each edge, starting with the one where nothing is
being eaten at all.

### Harness ↔ model

This may be the map's best-defined frontier: harnesses are not trying to
bite anything off the model category. No tracked harness ships or trains its
own weights, and the repo's absorption findings never name the model as a
target — the model stays the swappable slab in the diagram. Where the
frontier is crossed, the movement runs the other way: model vendors treating
harnesses as data instruments — xAI's acquisition of Cursor, followed by
training Grok 4.5 on that harness's session data, and hermes shipping
trajectory-export tooling openly labeled for training its maker's next
models ([the vendor-span section](../taxonomy.md)).

Well-defined does not mean uneventful. Every harness is forced to take a
position on whether models have "converged" enough to share one prompt, and
the five documented positions are incompatible: nine bespoke per-model
prompts sharing zero substantive lines (opencode), a per-family prompt
registry built and then dismantled (cline), ~15 lines betting the prompt
barely matters (continue), one shared prompt plus per-family appendices
covering every major family except Anthropic's (hermes), and a vendor
swapping instructions per model slug within its own family (codex)
([the five positions](../notes/02-harnesses/index.md), 2026-07-30). None of
the five is backed by a published eval. When the practitioners best placed
to know can't agree, "the harness doesn't matter" is not a safe assumption.

And yet in public reporting the frontier barely exists. Leaderboards score
*pairings* — "Codex CLI + GPT-5.5" — and publish them as model results, so
nobody knows which category they're praising. The one benchmark I found
that fixes the harness to isolate the model turned out to inherit that
harness's per-model prompt dispatch: a confound its own maintainer didn't
know about until [I reported it upstream](../notes/01-models/index.md)
([conclusion 2](../README.md#conclusions)). And for the vendors that span
both categories, attribution is confounded by construction — the model and
the harness were never built to separate ([the taxonomy](../taxonomy.md)).
That isolation is buildable — the repo's own rig does it at personal scale
for a few dollars — which is where the next article in this series picks up.

### Harness ↔ environment

One harness doesn't attach to a sandbox — it *is* one: Codex CLI compiles
Seatbelt, Landlock, bwrap, and a Windows sandbox into its own binary and
invokes them per tool call; a Node or Python harness can call a sandbox, a
Rust harness can be one
([the codex deep-dive](../notes/02-harnesses/codex.md)). Claude Code ships
worktrees as a first-class native operation, and its cloud side bundles its
own sandbox. Underneath sits a substitution: permission gates and
environments restrict the same thing — the harness gates per action in
software, codex per action in the OS, a container structurally
([the substitution axis](../notes/03-execution-environments/index.md)). What
has *not* been absorbed is the environments themselves: they remain
independently distributed products a harness binds to — bleed, not merger.

### Harness ↔ workflow

The turn-end verification gate — the mechanism the framework experiments
credit with category 4's quality margin — now runs natively inside
harnesses: hermes as an always-on loop policy that re-prompts the model when
it finishes without fresh verification evidence, codex as stop hooks that
can veto termination. Plan modes are everywhere, in four diverging shapes
(an enforced mode, a tool, a bundled skill, a per-query flag), and subagent
context isolation is native in all six harnesses checked
([the absorption table](../notes/02-harnesses/index.md)). The inversion
underneath: every tracked framework's gates grade as prose or scripts —
their runtime is the model reading instructions — while the harness-native
forms grade as engine or hook. The framework category's hardest problem is
the harness category's default posture. And what is *not* absorbed is a
coherent remainder, not a lag: staged intent artifacts, artifact-structure
gates, and workflow-scoped state — the spec-driven spine. Harnesses absorb
*mechanisms* and leave *methodology* alone.

### Harness ↔ memory

Autonomous memory loops are native in three of the four harnesses checked
for them, in four different mechanism shapes: hermes runs a background fork
on by default, codex ships a pipeline that is stable but off, Claude Code
writes memory in-loop — and Warp is the verified counter-instance,
agent-proposed but human-committed, with a deprecated field showing an
auto-write path that was built and then removed
([the learning-loop column](../notes/cross-cutting/feature-taxonomy.md)).
"Native memory" was never uniform. And on this edge the traffic runs both
ways: memory products colonize harnesses that already absorbed the feature
— memos installs into hermes alongside hermes' own loop — and one escalates
to displacement, blocking the harness's native memory writes to replace
them with its own: the cross-harness bet from the memory section, fighting
back.

Absorption isn't only vertical. Warp's multi-agent orchestration treats
rival harnesses as selectable backends — an enum whose variants are its own
agent, Claude Code, OpenCode, Gemini, and Codex — with drivers and
transcript parsers for its competitors, and it launches those children with
their own permission gates disabled: absorption of orchestration without
absorption of governance
([the Warp deep-dive](../notes/02-harnesses/warp.md)). Any claim that "you
need category X for capability Y" therefore has a shelf life — and not only
because harnesses grow. In a preregistered ablation, one model tier
absorbed a workflow mechanism's entire measured value: a grounding
instruction that lifted a smaller model's trap discovery did nothing for
the next tier up, which grounded unprompted
([conclusion 12](../README.md#conclusions)). A measured margin for a
workflow framework is a claim about current-tier models, with a built-in
expiration date.

## Where the map ends

The map stops at five categories on purpose. The repo tracks a sixth
bucket that cuts across them — MCP servers, skills, rules files, hooks, and
config packs like ECC ([the extensions bucket](../taxonomy.md)):
distributable content that parameterizes the triad's edges rather than
standing as a category of its own
([conclusion 3](../README.md#conclusions)).

---

*Everything here links into the [research repo](../README.md), where each claim
carries its verification date. If a link contradicts this article, the link is
newer — trust it.*
