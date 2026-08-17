# A taxonomy of AI-assisted-coding tooling

`checked: 2026-08-17`

The point of this document is a **shared vocabulary**. Without one, "Claude Code vs. GSD
vs. Opus 5" is a category error — three things that aren't the same kind of thing at all.
Every note and comparison in this repo declares which layer its subject occupies, so that
comparisons stay like-for-like.

## The stack

**Reframed 2026-08-17 — the core triad and its two interfaces.** A recorded revision, and
a *reframing rather than a reclassification*: no tool changes its home, the stress test
stands unchanged, and the numbers remain storage keys (3 kept its number at the
2026-07-30 demotion for the same reason — renumbering breaks dated cross-references for
zero information gain). The 2026-07-30 "three core layers + bucket" framing this
supersedes survives as the classification record in section 3.

A running agent system requires exactly three things; everything else in this repo either
parameterizes them or mediates between them and the human:

- **Model (1)** — cognition. The weights.
- **Harness (2)** — mediation. Runs the loop, assembles context, gates permissions,
  fronts the user, reaches tools and files.
- **Environment (5)** — situation. Where execution lands and what it can damage; the
  autonomy ceiling lives here (principle E1), not in the model.

**The necessity asymmetry** is why the layers feel so different to study: the model has
**no degenerate form**, the harness degenerates to a bare while-loop around the API, and
the environment degenerates to the host. Much of the field is the project of making the
two degenerate forms non-degenerate — harness sophistication is the contested ground of
2026, and every fully-autonomous product to date bought its autonomy at the environment.

The two non-fundamentals are **interfaces**:

- **Extensions (3 — the cross-layer bucket)** parameterize the **edges of the
  triad**: rules files and per-model prompts sit on the model↔harness edge, MCP on the
  harness↔world edge, memory on the agent↔time edge, and the four layer-5 relationship
  verbs (*bundle/bind/internalize/inhabit*) are the topology options of the
  harness↔environment edge. This is not incidental — the repo's strongest findings are
  *edge* findings (conclusion 1's per-model prompts; hermes' cache-vs-self-modification
  tension; E2B's egress credential substitution), which is the empirical case that the
  interactions deserve first-class vocabulary.
- **Workflow frameworks (4)** sit on the **human⇄stack boundary** — see section 4 for
  the four-function decomposition (intent flows down, evidence flows up).

**Countervailing evidence and falsifiers, recorded at reframing time rather than
buried:** (a) ECC is a 236k-star business built entirely on edge content, and the
instinct-exchange re-check (~2027-01) can still force artifacts back from "interface
detail" to a layer — the demotion's reverse trigger is unchanged by this reframing.
(b) Warp shows the mediation role *nests* (a harness driving other harnesses), so
"harness" names a function, not a unique slot. (c) The frame itself is falsifiable: it
fails if artifacts standardize into an independently exchanged layer, or if a framework's
measured value ever concentrates in intent-capture with the grounding and verification
stripped out — the latter is exactly what exp-02 can test once its instrument is
unblocked (issue #4).

### 1. Models

The weights themselves. The foundation everything else sits on.

Judged for *this* field on: tool-call fidelity, long-horizon coherence (staying on task
across hundreds of steps — the property that separates an agentic model from a good chat
model), usable context, cost per **completed task** rather than per token, and release
mode (API-only vs. open weights).

#### 1b. Model access

How you actually reach the weights: first-party APIs, aggregators/routers, cloud
marketplaces, and local runtimes. A sub-layer rather than a peer layer, but it earns
mention because it silently explains a lot of "why did it get worse" — prompt-caching
support, quantization, rate limits, and context truncation all differ by route while the
model name stays the same.

### 2. Harnesses

The program that runs the agent loop. Concretely: **loop + context assembly + permission
model + UI**.

Described by two axes, recorded separately because products increasingly span both:

- **Surfaces** — where you interact: terminal, IDE, desktop, web. **Multi-valued.** An
  earlier version of this taxonomy used a single surface bucket; that forced converged
  products into one label (Claude Code spans all four; OpenCode ships terminal + desktop +
  IDE from one core) and conflated web-as-interface with remote-as-execution.
- **Execution** — how it runs: `local` (synchronous, on your machine, you watch) vs.
  `async-remote` (Devin, Jules, cloud Codex, Claude Code on web — the agent runs elsewhere
  and reports back). Claude Code on web and Devin are *not* the same kind of thing, and
  the old "async/cloud" bucket said they were.

  *Strain recorded (2026-07-30, hermes-agent deep-dive):* a third shape exists that
  neither value describes — the **resident** agent: a persistent daemon that outlives any
  conversation, receives messages from ~20 platforms, and runs cron jobs unattended
  (hermes' gateway; its serverless backends hibernate between sessions). Not promoted to
  a third value on one instance — recorded here so the second instance triggers the
  revision. Same read strained **surfaces**: messaging platforms don't fit the four-value
  vocabulary and are recorded as an annotation, not a fifth value.

Which layer-5 *environments* a harness can bind to (host, worktree, container, remote
sandbox) is recorded on the harness entry as its bleed — not as harness configuration.
The environments themselves remain independently distributed products; see the layer-5
scope note.

As of mid-2026 this is the most contested layer, and the consensus reason is worth
recording: the frontier models have converged enough that the harness now decides most of
the day-to-day experience.

### 3. Extensions & protocols — a cross-layer bucket, not a rung (since 2026-07-30)

What the agent can **see and touch**, as *distributable content*: MCP servers, skills,
rules files (`CLAUDE.md`, `AGENTS.md`), hook configs, subagent definitions, config
packs at scale (ECC) — and the specifications they ride on (MCP the protocol, the
`AGENTS.md` and `SKILL.md` conventions, tracked in the Standards section, which is this
bucket's spec half).

Formerly "layer 2's ecosystem layer"; demoted to a bucket by the executed revision
above. The reasoning that survives from the layer era: the *runtimes* (MCP clients,
skills loaders, hook engines) were always layer-2 features, the *write paths* are being
absorbed into layer 2 (conclusion 8), and what remains genuinely independent is
**artifacts distributed on file conventions** — content plus specs, which is a bucket's
shape, not a rung's. The number **3 is retained as a storage and index key only**
(`notes/03-capability-extensions/`, `layer: 3` frontmatter, the comparisons tables) —
renumbering would break every dated cross-reference in the repo for zero information
gain.

The independent-distribution test still governs what belongs *in the bucket*: an MCP
server is authored, versioned, and installed separately from any harness, and the same
one works across Claude Code, Codex, Cursor, Copilot, Gemini CLI, OpenCode, and Devin.

Distinct from layer 4: capability extensions govern **what the agent can reach**;
workflow frameworks govern **what process it follows**.

**Renamed "portable artifacts" → "Extensions" (2026-08-17).** The old display name
baked an adoption *outcome* into the category's identity. Portability is not an
intrinsic property of an extension — it is a status the ecosystem confers by
adoption, and it has been conferred unevenly: hooks are the control group (same kind
of thing, no second adopter, no portability), rules files gained portability when a
rival vendor chose to link competitors' formats (artifact unchanged, market moved —
the Warp evidence under conclusion 3), and MCP holds the limit case, portability by
standardization. The bucket's members are extensions; *how portable each kind is* is
a dated, per-kind measurement (the Standards scoreboard), not a name.

**Revision executed — "three core layers + bucket" (recorded and gated 2026-07-30 am;
trigger (a) fired same day at the ECC deep-dive).** The challenge, raised after the
hermes/codex deep-dives: layer 3's *mechanisms* were always layer-2 features (every
harness ships its own MCP client, skills loader, hooks runtime), and the deep-dives
showed the *write path* absorbed too (autonomous learning loops author the memory/skill
artifacts — README conclusion 8). Trigger (a) required the ECC read to find **no
process spine** (confirmed: opt-in catalog, orchestration outsourced to an external
runtime) **and portability reducing to file conventions** (confirmed for the portable
bundle: copy-with-adaptation into per-harness convention dirs; even its background
observer daemon is installed as files and launched through each harness's own hook
system). Per the gate, the revision executes: **the core stack is layers 1, 2, and 4,
plus layer 5** (kept on its own surviving falsifier); **the former layer 3 becomes the
cross-layer bucket below.**

*Countervailing evidence, recorded at execution rather than buried:* the same read
showed the artifact ecosystem is product-grade — ECC is a 236k-star business built
entirely on independently distributed capability artifacts, and its instinct
import/export design points at a *new* exchangeable artifact class. If instinct-like
formats standardize across vendors (the ~2027-01 standards re-check remains scheduled),
the bucket may deserve re-promotion to a layer — the door swings both ways, and that
re-check is now the recorded trigger for the reverse revision.

### 4. Workflow frameworks

The **human⇄stack boundary**: an encoded methodology that turns what a person wants into
something the triad can execute, and turns what the triad did into something a person can
trust. Four functions, each observed in the studied frameworks *(decomposition recorded
2026-08-17)*:

1. **Refine intent into specs** — spec-kit's `/specify` + `/clarify` with budgeted
   `[NEEDS CLARIFICATION]` markers; OpenSpec's proposal → delta-spec grammar.
2. **Decompose work into concrete subtasks** — spec-kit's `tasks.md` task grammar
   (`T001 [P] [US1]` + file path, phases by user story); GSD's structured task graphs.
3. **Flag gaps that need research** — GSD's empirical research agents (fixture repos,
   crafted commits — the machinery conclusion 6 credits with nearly all of GSD's measured
   margin); spec-kit's Phase-0 `research.md` dispatch per unknown.
4. **Set up verification that converts progress into evidence** — GSD's verifiers with
   *measured* expected values and `human_needed` abstention; OpenSpec's validator
   (enforcement by exit code); spec-kit's checklists and `/analyze`.

Intent flows down through 1–2; evidence flows up through 3–4. The one preregistered
experiment (exp-01) located nearly all of the measured value in **3 and 4** and almost
none in 1–2's ceremony (conclusion 6, under re-examination via issue #8) — so when
reasoning about a framework, weigh its grounding and verification machinery over its
spec ceremony.

The analogy: if the harness is the runtime, this is the framework. Node is to Next.js as
Claude Code is to GSD.

The layer test is **harness portability by design**: both GSD and spec-kit target many
harnesses from one definition. A tool that only makes sense inside one harness's loop is
probably that harness's feature, not a framework.

*Addendum (2026-07-28, from the spec-kit source read).* The portability test now has a
verified mechanism and a known price. Mechanism: portability is a **compile step over
prompt files** — cheap because every harness converged on "slash command = prompt file in
a directory." Price: that prose-only common denominator means the framework's **runtime
is the model reading instructions**, so enforcement is only as strong as the prose
(README conclusion 7). Corollary: layer-4→2 bleed is a *structural symptom*, not vendor
ambition — both frameworks studied grew deterministic engines (GSD's `gsd-pi`, spec-kit's
`workflows/` YAML runner) as the escape hatch from prose-level control. Evidence:
[`notes/04-workflow-frameworks/spec-kit.md`](notes/04-workflow-frameworks/spec-kit.md).

### 5. Execution environments

Where the agent's code actually runs, and what it can damage: git worktrees,
devcontainers, Docker, remote sandboxes (E2B, Modal, Cloudflare Sandbox SDK), cloud VMs.
In the 2026-08-17 reframing this is the **third fundamental of the core triad** — kept at
its historical number as a storage key, like everything else.

Easy to overlook until it bites. Isolation that hides the files the agent needs is a
layer-5 problem routinely misread as a layer-2 bug — the worktree/gitignore trap written
up in [`notes/05-execution-environments/`](notes/05-execution-environments/index.md) is
the case that convinced me this layer is real.

**Scope note.** This layer is in scope only through the lens of agents. Most of its
entities are borrowed infrastructure — Docker, devcontainers, and worktrees predate the
field and earn no survey of their own here. The questions asked of them are agent-shaped:
**blast radius** (what can the agent damage), **fidelity** (does the project's tooling run
unmodified inside), and **parallelism** (how many agents at once, at what bootstrap cost).
The reason those questions matter is that the field's autonomy ceiling is set by blast
radius, not model capability — every fully-autonomous product to date bundles a sandbox,
not a smarter model, and the same permission flag that is reckless on a host is sane in a
container. The position is falsifiable: if sustained study never shows a layer-5 fact
changing a tool choice or explaining a failure, demote this layer to a cross-cutting note.
The prediction recorded here is the opposite — as autonomy rises, the environment question
becomes more central, not less.

**Adjudicated 2026-08-16, then RESOLVED the same day.** The adjudication returned a split
verdict — *"explaining a failure"* passed via the worktree trap, *"changing a tool choice"*
had no instance — and proposed **gated** demotion to a "fifth axis of layer 2," pending the
first report of an agent-native environment studied as a product in its own right. **That
report landed the same day (E2B) and fired the "keep it a rung" arm of the gate.** Full
reasoning in
[`notes/05-execution-environments/index.md`](notes/05-execution-environments/index.md);
the short form: E2B produced ~26 environment-facts against 6 attachment-restatements, every
one of the 26 invisible from the SDK (no jailer on Firecracker; create-is-resume with no warm
pool; the credential-injection proxy closed-source; guest `kcompactd` disabled for host
snapshot economics). One genuine population member falsifies "fails as a population," so
**layer 5 stays a rung and the demotion does not execute.** The live successor question — is
this an artifact of E2B being open source, versus a closed environment yielding only
testimony — is [issue #11](https://github.com/leandromineti/ai-assisted-coding/issues/11).

**The relationship vocabulary** (*bundle* · *bind* · *internalize* · *inhabit*, plus the
null case) is defined once in
[`notes/05-execution-environments/index.md`](notes/05-execution-environments/index.md).
The stress-test rows below record where each verb was *discovered*; the index is where the
vocabulary lives.

## Cross-cutting concerns

These are **not layers**. They appear at several layers at once, and forcing them onto the
ladder distorts them. Each gets a note of its own.

- **Context engineering** — lives in the harness (layer 2), the rules files (layer 3), and
  the workflow framework (layer 4) simultaneously. Probably the highest-leverage topic in
  the repo.
- **Verification & evaluation** — tests, CI gates, review bots, agent-run observability,
  benchmarks. The least-explored area of the field, and the one that decides whether any
  of the rest is actually working.
- **Cost & economics** — per-token price is the least interesting form of this. Cost per
  completed task, cost of a failed run, and cost of review time all matter more.

## Standards

The stress test below surfaced a category that isn't a layer at all: **standards**. MCP,
the `AGENTS.md` convention, and the emerging agent-permission conventions are
specifications, not installable things. A standard is recorded here, once, and referenced
from the layers that implement it — never given a layer entry of its own.

- **MCP (Model Context Protocol)** — the protocol is a standard; the *servers* that speak
  it are layer 3.
- **`AGENTS.md` / `CLAUDE.md`** — rules-file conventions; the files are layer 3 artifacts.
- **Agent-permission conventions** — emerging; nothing confirmed as a named standard.

Written up in [`notes/standards/`](notes/standards/index.md), which also tracks the
question this category exists to answer: whether skills and hooks standardize the way MCP
did, or stay vendor features — which decides whether layer 3 is a real layer.

## The boundary rule

**The layers are analytic, not physical.** Real products bundle across them constantly:

- Claude Code ships skills and hooks (layer 3) and plan mode (layer 4) inside the harness.
- GSD is distributed *as* Claude Code skills, but also ships `gsd-pi`, its own CLI — so it
  reaches down into layer 2.
- Devin bundles its own sandbox (layer 5) with its harness (layer 2).

So every entry records a **primary layer** plus an explicit **bleed** note. The bleed is
signal, not noise: it's how you watch layers consolidate. The clearest current example is
xAI/SpaceX's $60B acquisition of Anysphere (Cursor), announced 2026-06-16 — a layer-1
vendor buying a layer-2 product, then training Grok 4.5 on that harness's session data.
That acquisition is not bleed, though — it is *vendor span*, the distinct dimension
formalized just below. Vertical integration across layers is the live structural story of
2026.

*Second instance (2026-07-30):* the harness-as-training-data-instrument pattern is not
exclusive to acquisitions. hermes-agent — open source, MIT — ships trajectory export and
compression tooling openly labeled "for training the next generation of tool-calling
models" (its maker, Nous Research, is a layer-1 vendor). opencode's "stores no code or
context server-side" is the explicit counter-position. Two instances plus a named
counter-position make this a pattern to track, not an anecdote:
**who a harness's maker is at layer 1 predicts what the harness collects.**

### Vendor span — when the layers stop being independent choices *(2026-08-16)*

Bleed and vendor span are different axes, and the framework reasons about them differently:

- **Bleed** is a property of a *tool* — one product reaching into an adjacent layer (codex
  internalizing a sandbox, GSD shipping `gsd-pi`). Recorded per report, in the `bleed` note.
- **Vendor span** is a property of a *maker* — one vendor owning distinct products across
  several layers at once, and tuning them to each other. Recorded here, because it is a
  fact about a company, not about any single entry.

The framework's default posture treats the layers as **independent axes**: pick a model,
pick a harness, pick an environment. That holds for the field's composable middle — a Nous
model driven by OpenCode inside a Modal sandbox is three vendors and three separable
decisions. It **breaks for vertically-integrated vendors**, where the choices *co-vary*:
choosing the harness chooses the model, the sandbox, and the extension format, because one
maker ships all of them. This is the single most important thing the taxonomy has to warn
its reader about before they treat a layer choice as free.

Clearest spanners as of 2026-08-16 (✓ tracked with a report · ○ observation-only, closed):

| Vendor | 1 · Model | 2 · Harness | 3 · Artifacts | 5 · Environment |
|---|---|---|---|---|
| **OpenAI** | gpt-5-6-sol ✓ | Codex CLI ✓ · cloud Codex ○ | — | Codex's *internalized* OS sandbox ✓ · cloud Codex microVM ○ *(bundle)* |
| **Anthropic** | opus/sonnet/fable/haiku ✓ | Claude Code ✓ *(observation-only, 2026-08-17)* | skills, MCP ○ | Managed Agents / code-exec container ○ *(bundle)* |
| **Google** | gemini-3-1-pro ✓ | Gemini → Antigravity CLI ✓ | — | — |
| **xAI** | grok-4-5 ✓ | Cursor ○ *(acquired 2026-06)* | — | — |

Two consequences a reasoner must carry:

1. **"Portable" means less inside a spanned stack.** MCP is portable across harnesses *in
   principle*; but a vendor owning model + harness + sandbox can co-optimize in ways a
   portable extension never reaches, so the portability guarantee is weakest exactly where a
   vendor is most integrated. Layer-3 independence (the standards question) is a claim about
   the composable middle, not about a spanned stack.
2. **Attribution is confounded by construction.** When a spanned stack succeeds or fails,
   you cannot hold the model fixed and swap the harness to find the cause — the vendor did
   not build them to separate. This is the same confound README conclusion 2 records for
   benchmarks ("Codex CLI + GPT-5.5"), promoted from a measurement artifact to a structural
   property of the vendor.

**Why this table is hand-kept, not generated** (and it is the one deliberate exception to
rule 3 in this repo): the sharpest spanners are *closed* — Claude Code, cloud Codex, and
Managed Agents have no report files — so a frontmatter-generated matrix would **understate
vendor span precisely for the vendors that have the most of it.** The generated half does
exist: [`comparisons/vendors.md`](comparisons/vendors.md) derives vendor coverage from
`vendor:` frontmatter and is the tracked-only **floor** (2026-08-17: it finds 2 spanners
where this table shows 4 — that gap *is* the closed-product blind spot, quantified). This
table deliberately admits observation-only (○) products to show the real shape, and is
illustrative, not an index — re-date it when a spanner's coverage changes rather than
trusting it to stay current on its own.

## Stress test

Five deliberately hard cases, classified. If a new case has no defensible home, the
taxonomy needs revision — not the case.

| Case | Verdict | Reasoning |
|------|---------|-----------|
| **Cursor's agent mode** | Layer 2, IDE-embedded | The IDE is the UI; the agent loop underneath is a harness. "IDE feature" describes the surface, not the kind. Now bleeds into layer 1 via xAI ownership. |
| **Claude Code Skills** | Layer 3, bundled in layer 2 | Independently authored, versioned, and portable in principle — that's the layer-3 test. Shipping inside a harness is distribution, not identity. |
| **Devin** | Layer 2, bundles layer 5 | A harness that happens to ship its own sandbox. You can't adopt one without the other, but bundling ≠ layer identity. |
| **Aider** | Layer 2, opinionated | It *has* a methodology (commit per change, repo map), but you can't install that methodology on top of a different harness. Not portable → harness with strong defaults, not a framework. |
| **MCP itself** | Not a layer — a standard | Forced the "Standards" section above. The protocol is a spec; its servers are layer 3. |
| **ECC (everything-claude-code)** | **Resolved: layer 3** (was layer-4 provisional) | Added 2026-07-28 as the live case; resolved 2026-07-30 at deep-dive. No process spine: workflow content is opt-in catalog items ("start with the workflow you need, not the full catalog"), and the multi-* orchestration commands outsource to an external runtime. A config pack at scale with a harness-independent learning runtime. The resolution **fired trigger (a) of the three-core-layers revision** — see the executed revision note in the layer-3 section. [`notes/03-capability-extensions/ecc.md`](notes/03-capability-extensions/ecc.md). |
| **hermes-agent** | Layer 2 confirmed — with recorded strain | Resolved 2026-07-30 at deep-dive. The classification test worked: other things install *into* it (spec-kit → `~/.hermes/skills`), which is the harness signature. But it's a personal agent with a coding *posture* (a runtime mode entered inside a git repo), and it strains both layer-2 axes — see the execution-axis note above. Kept at layer 2 because the taxonomy classifies by *kind* (it runs the loop, assembles context, gates permissions, owns the UI), not by how much of the product is about coding. [`notes/02-harnesses/hermes-agent.md`](notes/02-harnesses/hermes-agent.md). |
| **Warp** | Layer 2 — that runs *other* layer-2 harnesses | Added 2026-08-11 at survey. The classification is not in doubt (own loop, embedding-indexed context assembly, execution-profile permissions, owns the UI), but two of its bleeds are new shapes. **Harness-over-harness:** `enum Harness { Oz, Claude, OpenCode, Gemini, Codex }` makes Warp's own agent one selectable backend among five for a spawned child agent, with per-harness drivers and transcript parsers (`app/src/ai/agent_sdk/driver/harness/`); the Codex driver installs Warp's plugin hooks into Codex and passes `--dangerously-bypass-hook-trust` so they run unreviewed. Orchestrating peers is layer-4-shaped behaviour, but it fails the layer-4 test — the process is not portable off Warp, it *is* Warp — so this is a harness with an orchestration tier, not a framework. **A fourth layer-5 verb:** after bundle (Devin), bind (hermes), and internalize (codex), Warp **inhabits** — `crates/isolation_platform/` detects the container Warp is *already running inside* (`Docker`/`DockerSandbox`/`Kubernetes`/`Namespace`) to obtain a workload-identity token, rather than launching anything. [`notes/02-harnesses/warp.md`](notes/02-harnesses/warp.md). |
| **Codex CLI's in-process sandboxing** | Layer 2 that *internalized* layer 5 | Added 2026-07-30 at deep-dive. The layer-5 relationship vocabulary had two verbs — *bundle* (Devin ships a sandbox product alongside) and *bind* (hermes attaches to Docker/SSH/Modal). codex is a third: Seatbelt policies, Landlock, bwrap, and a Windows sandbox are **compiled into the harness binary** and invoked per tool call, plus pre-main process hardening. Still layer 2 — the sandbox is not independently distributed, so it fails the layer test — but the scope note's prediction ("as autonomy rises, the environment question becomes more central") gains a data point: the environment became a *harness subsystem*. [`notes/02-harnesses/codex.md`](notes/02-harnesses/codex.md). |

## Deliberate exclusions

- **Agent SDKs** (Claude Agent SDK, LangGraph, Mastra, PydanticAI) — a different consumer:
  you're *building* an agent rather than *using* one. Excluded for now, not dismissed;
  revisit if the repo's scope widens.
- **Human practices** — task decomposition, when to restart context, review discipline.
  Real and important, but they're techniques rather than tooling; they belong in
  `notes/cross-cutting/`.

## Layer indexes

| Layer | Index |
|-------|-------|
| 1 · Models | [`notes/01-models/index.md`](notes/01-models/index.md) |
| 2 · Harnesses | [`notes/02-harnesses/index.md`](notes/02-harnesses/index.md) |
| 3 · Extensions (bucket) | [`notes/03-capability-extensions/index.md`](notes/03-capability-extensions/index.md) |
| 4 · Workflow frameworks | [`notes/04-workflow-frameworks/index.md`](notes/04-workflow-frameworks/index.md) |
| 5 · Execution environments | [`notes/05-execution-environments/index.md`](notes/05-execution-environments/index.md) |
| ✕ Cross-cutting | [`notes/cross-cutting/index.md`](notes/cross-cutting/index.md) |
| ✕ Standards | [`notes/standards/index.md`](notes/standards/index.md) |

Per-tool reports use [`notes/_template-tool-report.md`](notes/_template-tool-report.md) and
are indexed flat, across layers, in [`comparisons/tools.md`](comparisons/tools.md).
