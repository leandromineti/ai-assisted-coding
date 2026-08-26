# A taxonomy of AI-assisted-coding tooling

`checked: 2026-08-26`

The point of this document is a **shared vocabulary**: without one, "Claude Code vs.
GSD vs. Opus 5" is a category error — three things that aren't the same kind of thing
at all — so every note and comparison in this repo declares which category its subject
occupies, and comparisons stay like-for-like. This is the repo's **tool taxonomy**,
the half that classifies what a tool *is*; its companion, the
[**feature taxonomy**](feature-taxonomy.md)[^adr-0010], defines
the characteristics assessed on tools — once, with per-category applicability — and
the comparison matrices are generated from it. Categories may carry **types**
(category 6's `type`; category 4's SDD / context-discipline / decision-governance
poles), which live in the category indexes, and the canonical terms with their
deny-lists live in [`tool-taxonomy.yaml`](tool-taxonomy.yaml) — this document is prose, linted
against it.

## Tool categories

**The core triad and its three interfaces**[^adr-0004][^adr-0007]. A running agent
system requires exactly three things — the triad; everything else in this repo either
parameterizes the triad or mediates between it and the human:

- **Model (1)** — cognition. The weights, and the vendor surface that prices and
  meters them.
- **Harness (2)** — mediation. Runs the loop, assembles context, gates permissions
  (§2's three components), and fronts the user.
- **Environment (3)** — situation. Where execution lands and what it can damage; the
  autonomy ceiling lives here (principle E1), not in the model.

**The necessity asymmetry** is why the categories feel so different to study: the model has
**no degenerate form**, the harness degenerates to a bare while-loop around the API, and
the environment degenerates to the host. Much of the field is the project of making the
two degenerate forms non-degenerate — harness sophistication is the contested ground of
2026, and every fully-autonomous product to date bought its autonomy at the environment.

The three non-fundamentals are **interfaces**:

- **Workflow frameworks (4)** sit on the **human⇄stack boundary** — see section 4 for
  the four-function decomposition (intent flows down, evidence flows up).
- **Memory (5)** sits on the **agent↔time edge** — persistent cross-session state as an
  installable product. A full category since the 2026-08-22 split[^adr-0020].
- **Extensions (6 — the cross-category bucket)** parameterize the **remaining edges of
  the triad**: rules files and per-model prompts sit on the model↔harness edge, MCP on
  the harness↔world edge, and the four environment
  relationship verbs (*bundle/bind/internalize/inhabit*) are the topology options of the
  harness↔environment edge. This is not incidental — the repo's strongest findings are
  *edge* findings (conclusion 1's per-model prompts; hermes' cache-vs-self-modification
  tension; E2B's egress credential substitution), which is the empirical case that the
  interactions deserve first-class vocabulary.

**Live falsifiers on the frame** (recorded at reframing time[^adr-0004]): (a) the
instinct-exchange re-check (~2027-01) can still force extension artifacts back from
"interface detail" to a category — the bucket's re-promotion trigger. (b) Warp shows the
mediation role *nests* (a harness driving other harnesses), so "harness" names a
function, not a unique slot. (c) The frame fails if artifacts standardize into an
independently exchanged category, or if a framework's measured value ever concentrates in
intent-capture with the grounding and verification stripped out — tested by exp-02/03
(conclusions 11–12): measured framework value concentrated in written artifacts, and
the frame survived its first test.

### 1. Models

The weights, and the first-party API surface around them — the foundation everything
else sits on. The weights are the irreducible part (the asymmetry above); the surface
is where the drift lives.

Judged for *this* field on: tool-call fidelity, long-horizon coherence (staying on task
across hundreds of steps — the property that separates an agentic model from a good chat
model), usable context, cost per **completed task** rather than per token, and release
mode (API-only vs. open weights).

This category deliberately has **no component decomposition** (recorded 2026-08-25):
components are tracing units, and the weights are untraceable at this repo's level of
analysis regardless of release mode — an open checkpoint yields transcribable
architecture facts, not a traceable mechanism, and closed subjects cap at `survey`
under methodology rule 1a anyway. The judged-on axes above are the category's
assessment lens instead — behavioral, fillable by model-isolated measurement (the
rig's comparisons; conclusion 2) — with the `model_features` block covering the
observable surface and 1b covering the route. Minting model components would claim
tracing access the repo does not have.

How you actually reach the weights is a type of its own (**1b — model access**, four
routes, in [the category index](../tools/1-models/README.md)): the same model by a
different route is a different product — it silently explains a lot of "why did it get
worse".

### 2. Harnesses

The program that runs the agent loop. Formally, a harness implements an
**agent-computer interface**: it treats the language model as a new category of end
user and supplies everything that user touches — the commands it can issue, the shape
of the feedback it reads, the management of its context window
([the SWE-agent read](../references/papers/2024-swe-agent.md), the academic origin of this category's
premise; formulation adopted from the published article, 2026-08-25).
**Three components**[^adr-0021] (decomposition
recorded 2026-08-22), each an
agent-shaped question anchored by a finding traced in source — this category's cousin
of category 3's blast-radius/fidelity/parallelism questions, with a different job:
those are an ingestion lens for borrowed infrastructure, these are a tracing
discipline (a deep-dive should say which of the three it actually traced) and the
sorting frame for the `harness_features` vocabulary:

1. **The loop** — *who can stop or steer a turn, and with what authority?* The turn
   engine: iteration, tool dispatch, stop conditions, subagent fan-out, plan-mode
   checkpoints. Tools-and-files reach lives here as the loop's dispatch table — MCP
   extends it, the gate checkpoints it. Anchor: the enforcement inversion — native
   `engine`/`hook` turn gates vs frameworks' `prose`[^adr-0011][^adr-0012].
   *Strain (2026-08-22):* §6 gives MCP its own harness↔world edge, which reserves a
   seat for reach as a component; not promoted because reach doesn't currently
   discriminate (the `mcp` column is a uniform ✓; invocation shape — `ptc` — is what
   splits). Trigger: the first reach-shaped finding that isn't loop-shaped — an
   edit-format study, or verified MCP-client divergence (aider's matrix row, unread
   today, is the likeliest source).
2. **Context assembly** — *what reaches the prompt, who wrote it, and where does the
   agent's own output land?* Rules-file and skill injection, memory write-back,
   compaction, cache discipline. Anchor: the hermes cache-tension finding
   ([category index](../tools/2-harnesses/README.md)), which asks this component's
   question verbatim. This is the harness sophistication the lead-in calls the
   contested ground of 2026, and what the `deep-dive` depth is defined as tracing.
3. **The permission gate** — *what may the agent attempt without a human, and can the
   model influence that decision?* The harness's end of the harness↔environment edge:
   in-process policy, verified `engine`-grade in five tracked harnesses — distinct
   from the environment's *bounds* (blast radius, category 3). Boundary test: if the
   model can influence it or a child process can escape it, it's the gate (category
   2); if it holds regardless of what the software does, it's the bounds (category
   3). Anchor: Warp's `AgentDecided` crack — a model-authored `is_risky: false`
   self-authorizes ([warp report](../tools/2-harnesses/warp.md)). Autonomy is the
   product of gate policy × environment bounds (principle E1).

The five kind-linked `harness_features` keys are the components' **apertures** — the
pluggable form of each: hooks and subagent-defs extend the loop, MCP its dispatch,
skills and rules files feed context assembly.

Beside the components, two **descriptive axes** — transcription facts readable off
product docs, not traced mechanisms — recorded separately because products
increasingly span both:

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

A **human front** is deliberately not a fourth component[^adr-0021]: its
assessment-grade fragments already belong to the components (approval UI to the gate,
plan-mode checkpoints to the loop), the axes above carry its classification facts,
and the human⇄stack boundary is category 4's. Trigger to re-open: a deep-dive
mechanism finding that fits none of the three — likeliest the async-remote
report-back path (what evidence does the agent assemble for a human who wasn't
watching?), untraced in any current read.

Which category-3 *environments* a harness can bind to (host, worktree, container, remote
sandbox) is recorded on the harness entry as its bleed — not as harness configuration.
The environments themselves remain independently distributed products; see the category-3
scope note.

As of mid-2026 this is the most contested category, and the consensus reason is worth
recording: the frontier models have converged enough that the harness now decides most of
the day-to-day experience.

### 3. Execution environments

Where the agent's code actually runs, and what it can damage: git worktrees,
devcontainers, Docker, remote sandboxes (E2B, Modal, Cloudflare Sandbox SDK), cloud VMs.
The **third fundamental of the core triad**.

Easy to overlook until it bites. Isolation that hides the files the agent needs is a
category-3 problem routinely misread as a category-2 bug — the worktree/gitignore trap written
up in [`tools/3-execution-environments/`](../tools/3-execution-environments/README.md) is
the case that convinced me this category is real.

**Scope note.** This category is in scope only through the lens of agents. Most of its
entities are borrowed infrastructure — Docker, devcontainers, and worktrees predate the
field and earn no survey of their own here. The questions asked of them are agent-shaped:
**blast radius** (what can the agent damage), **fidelity** (does the project's tooling run
unmodified inside), and **parallelism** (how many agents at once, at what bootstrap cost).
The reason those questions matter is that the field's autonomy ceiling is set by blast
radius, not model capability — every fully-autonomous product to date bundles a sandbox,
not a smarter model, and the same permission flag that is reckless on a host is sane in a
container. The position is falsifiable: if sustained study never shows an environment
fact changing a tool choice or explaining a failure, demote this category to a cross-cutting
note. The prediction recorded here is the opposite — as autonomy rises, the environment
question becomes more central, not less. (The demotion question was adjudicated once and
the category held[^adr-0003]; the live successor
question is [issue #11](https://github.com/leandromineti/ai-assisted-coding/issues/11):
does the E4 fact class survive a closed environment, or is it legible only when the
environment is open source?)

**The components** — an execution environment is **host · principal · working
directory** — are defined once in
[`tools/3-execution-environments/README.md`](../tools/3-execution-environments/README.md),
where every seed is classified by which components it changes against the default
{your machine, you, cwd}. The three questions above are the lens over them: blast
radius = host × principal, fidelity = host toolchain + cwd completeness, parallelism =
the cost of multiplying cwd vs hosts.

**The relationship vocabulary** (*bundle* · *bind* · *internalize* · *inhabit*, plus the
null case) is defined once in the same index.
The stress-test rows below record where each verb was *discovered*; the index is where the
vocabulary lives.

### 4. Workflow frameworks

The **human⇄stack boundary**: an encoded methodology that turns what a person wants into
something the triad can execute, and turns what the triad did into something a person can
trust. Four functions, each observed in the studied frameworks *(decomposition recorded
2026-08-17)*:

1. **Intent refinement** — refine intent into specs. *Does the framework test the
   English before anything executes?* spec-kit's `/specify` + `/clarify` with budgeted
   `[NEEDS CLARIFICATION]` markers; OpenSpec's proposal → delta-spec grammar.
2. **Work decomposition** — decompose work into concrete subtasks. *Does work arrive
   at the triad in verifiable units?* spec-kit's `tasks.md` task grammar
   (`T001 [P] [US1]` + file path, phases by user story); GSD's structured task graphs.
3. **Gap research** — flag gaps that need research, and dispatch it. *Does the
   framework measure the domain, or trust training data?* GSD's empirical research agents (fixture repos,
   crafted commits — the machinery conclusion 6 credits with nearly all of GSD's measured
   margin); spec-kit's Phase-0 `research.md` dispatch per unknown.
4. **Verification** — set up verification that converts progress into evidence. *Who
   checks the claim of "done", and with what authority?* GSD's verifiers with
   *measured* expected values and `human_needed` abstention; OpenSpec's validator
   (enforcement by exit code); spec-kit's checklists and `/analyze`.

Intent flows down through 1–2; evidence flows up through 3–4. The preregistered
experiments located nearly all of the measured value in **3 and 4** and almost none in
1–2's ceremony (conclusion 6 — its decomposition tested and upheld, with a
model-tier caveat, by exp-03; issue #8 resolved 2026-08-18) — so when reasoning about a
framework, weigh its grounding and verification machinery over its spec ceremony.

The four functions are this category's **components**[^adr-0023] (the same tracing
discipline as §2: a category-4 deep-dive declares which functions it traced), and
sorting the nine `workflow_features` keys under them yields a finding rather than a
clean partition: `intent_pipeline` sorts to functions 1–2, the gate keys to 4 and the
boundary, `retrospectives` beside 3 — but `context_isolation`,
`parallel_orchestration`, and `state_store` sit on an **execution substrate outside
the four functions**, and that substrate is exactly what harnesses absorb natively
(conclusion 8; the [category-2 absorption table](../tools/2-harnesses/README.md)), while
what stays unabsorbed is the function-1/2 artifact spine. The decomposition predicts
the absorption boundary: frameworks own the translation; the substrate is borrowed
ground.

The analogy: if the harness is the runtime, this is the framework. Node is to Next.js as
Claude Code is to GSD.

Two boundary tests, an identity test and a membership test. **Identity**: a framework
sits *over* an agent you already run while being neither the agent itself nor a kit
for building one — the delimitation the independent six-framework study arrived at
([the from-prompt-to-process read](../references/papers/2026-from-prompt-to-process.md)), which is
also what separates this category from harnesses on one side and the excluded agent
SDKs on the other (formulation adopted from the published article, 2026-08-25).
**Membership**: **harness portability by design** — both GSD and spec-kit target many
harnesses from one definition. A tool that only makes sense inside one harness's loop is
probably that harness's feature, not a framework.

*Addendum (2026-07-28, from the spec-kit source read).* The portability test now has a
verified mechanism and a known price. Mechanism: portability is a **compile step over
prompt files** — cheap because every harness converged on "slash command = prompt file in
a directory." Price: that prose-only common denominator means the framework's **runtime
is the model reading instructions**, so enforcement is only as strong as the prose
(README conclusion 7). Corollary: category-4→2 bleed is a *structural symptom*, not vendor
ambition — both frameworks studied grew deterministic engines (GSD's `gsd-pi`, spec-kit's
`workflows/` YAML runner) as the escape hatch from prose-level control. Evidence:
[`tools/4-workflow-frameworks/spec-kit.md`](../tools/4-workflow-frameworks/spec-kit.md).

### 5. Memory

Persistent cross-session state as an installable product — **the agent↔time edge**. Fed
by hooks/MCP during a session, consolidated between sessions, injected back at the next
session start, on any harness. Reports carry the 13-key `memory_features`
block[^adr-0013]; the category's survival bet is the one
thing a single harness cannot absorb — cross-harness continuity — measured pull-shaped
in exp-04 (conclusion 14).

**Three components**[^adr-0023], lifted from the definition sentence above — the
pipeline a deep-dive traces (declaring which components, per §2's discipline), each
carrying its own trust sub-question:

1. **Capture** — *what enters the store, and who admitted it?* The write path:
   hook / adapter / agent-invoked (no two vendors alike), admission policy
   (`write_admission`), and the write-side trust boundary. Anchor: mem0's plugin
   *blocking the harness's native memory writes* to redirect them — the displacement
   finding (conclusion 8's counter-current;
   [category index](../tools/5-memory/README.md)).
2. **Consolidation** — *what happens to it between sessions, and does that run by
   default?* The store wager (files-git / vector / rows+vector / graph+vector+rows —
   the identity axis), tiers, decay, revision authority. Anchor: memos'
   presence≠operative finding — the entire evolution half verified in source and
   shipped dark behind a default-off flag
   ([memos report](../tools/5-memory/memos.md)).
3. **Recall** — *what reaches the next session's prompt — pushed or pulled, framed as
   data or as authority?* Injection mode, retrieval fusion, and the read-side trust
   boundary (memory injection is a prompt-injection vector). Anchor: exp-04's
   measurement — the automatic floor is 0/10, the pull ceiling 10/10, and the harness
   boundary costs nothing on the pull path; the category's pitch says "your agent
   remembers", the measurement says "your agent can look it up, if it asks"
   (conclusion 14; [experiment 04](../experiments/04-memory-continuity/README.md)).

The `harness_installer` key is the components' **aperture** — the shim/installer is to
a memory product what the kind-linked keys are to the harness: the pluggable seam
where the coding-agent behavior lives, not a pipeline stage.

A full category since the 2026-08-22 split[^adr-0020]: born 2026-08-18 as the
extensions bucket's `memory` type, promoted by owner decision — the earlier
sample-bias caution[^adr-0016] still applies to the category's eight-report roster, and is carried as
calibration, not erased. Reports keep `type: memory` as residual data.

Distinct from category 6: memory governs **what survives the session**; extensions
govern **what the agent can reach**. Distinct from category 2's native memory loops
(conclusion 8's absorption): the extension's bet is continuity *across* harnesses.

### 6. Extensions & protocols — a cross-category bucket, not one of the fundamentals

What the agent can **see and touch**, as *distributable content*: MCP servers, skills,
rules files (`CLAUDE.md`, `AGENTS.md`), hook configs, subagent definitions, config
packs at scale (ECC) — and the specifications they ride on (MCP the protocol, the
`AGENTS.md` and `SKILL.md` conventions, tracked in the Standards section, which is this
bucket's spec half). Renumbered 5 → 6 at the 2026-08-22 split[^adr-0020], which moved
the memory type out to category 5.

A bucket, not one of the fundamentals[^adr-0002]: the
*runtimes* (MCP clients, skills loaders, hook engines) were always category-2 features, the
*write paths* are being absorbed into category 2 (conclusion 8), and what remains genuinely
independent is **artifacts distributed on file conventions** — content plus specs, which
is a bucket's shape, not a fundamental's. Named "Extensions" because portability is conferred
by adoption, not intrinsic[^adr-0005]; *how
portable each type is* is a dated, per-type measurement (the Standards scoreboard), not
a name.

The independent-distribution test still governs what belongs *in the bucket*: an MCP
server is authored, versioned, and installed separately from any harness, and the same
one works across Claude Code, Codex, Cursor, Copilot, Gemini CLI, OpenCode, and Devin.

*Strain (2026-08-26):* this bucket is **residual in origin but positive in test** — it is
what remained once the runtimes and the write paths were absorbed into category
2[^adr-0002], while what belongs in it is decided by the independent-distribution test
just stated. The gap between those two exerts a pull: a newly sighted subject that fits
none of categories 1–5 drifts toward 6 *because* 6 is where the leftovers went, even when
it fails that test — and [`candidates.md`](../tools/candidates.md) is a holding pen for
unclassified *tools* only, with nothing equivalent for a shape the vocabulary cannot yet
name. The pull has been resisted once on the record: the orchestrator-above-harnesses
shape (orca, sighted 2026-08-20) was filed at category 2 as the least-wrong primary rather
than swept in here. Trigger: the first subject filed at 6 that fails the
independent-distribution test, or a second sighted shape with no home in categories 1–6 —
either forces the question of whether the taxonomy needs an explicit place for the
not-yet-classifiable, which is a different thing from this bucket and must not be
smuggled into it by treating 6 as a synonym for "unsorted".

*How deeply each type is studied* follows the surviving coverage
strata[^adr-0019] (carried forward at the split[^adr-0020]):
*content types* (skills, rules files, subagent defs) get Standards tracking plus
exemplar reads; *reach-side* (MCP servers) gets capped exemplars only, because the
population reachable through an unchanged interface is world, not stack — a census of
it would be as illegitimate as a census of CLI tools because agents have shells;
`config-pack` is graded by payload (ECC: mechanism-grade).

Distinct from category 4: capability extensions govern **what the agent can reach**;
workflow frameworks govern **what process it follows**.

**Live re-promotion trigger** (recorded at the demotion[^adr-0002]): the artifact
ecosystem is product-grade — ECC is a 236k-star business built entirely on independently
distributed capability artifacts, and its instinct import/export design points at a
*new* exchangeable artifact class. If instinct-like formats standardize across vendors
(the ~2027-01 standards re-check remains scheduled), the bucket may deserve re-promotion
to a fundamental — the door swings both ways.

## Cross-cutting concerns

These are **not categories**. They appear at several categories at once, and forcing them into a
single category distorts them. Each gets a note of its own.

- **Context engineering** — lives in the harness (category 2), the rules files (category 6), and
  the workflow framework (category 4) simultaneously. Probably the highest-leverage topic in
  the repo.
- **Verification & evaluation** — tests, CI gates, review bots, agent-run observability,
  benchmarks. The least-explored area of the field, and the one that decides whether any
  of the rest is actually working.
- **Cost & economics** — per-token price is the least interesting form of this. Cost per
  completed task, cost of a failed run, and cost of review time all matter more.

## Standards

The stress test below surfaced something that doesn't fit any tool category: **standards**. MCP,
the `AGENTS.md` convention, and the emerging agent-permission conventions are
specifications, not installable things. A standard is recorded here, once, and referenced
from the categories that implement it — never given a category entry of its own.

- **MCP (Model Context Protocol)** — the protocol is a standard; the *servers* that speak
  it are category 6.
- **`AGENTS.md` / `CLAUDE.md`** — rules-file conventions; the files are category-6 artifacts.
- **Agent-permission conventions** — emerging; nothing confirmed as a named standard.

Written up in [`docs/standards.md`](standards.md)
(one of the cross-cutting notes since 2026-08-18[^adr-0008]),
which also tracks the
question this category exists to answer: whether skills and hooks standardize the way MCP
did, or stay vendor features — which decides whether the extensions bucket is a real category.

## The boundary rule

**The categories are analytic, not physical.** Real products bundle across them constantly:

- Claude Code ships skills and hooks (category 6) and plan mode (category 4) inside the harness.
- GSD is distributed *as* Claude Code skills, but also ships `gsd-pi`, its own CLI — so it
  reaches down into category 2.
- Devin bundles its own sandbox (category 3) with its harness (category 2).

So every entry records a **primary category** plus an explicit **bleed** note. The bleed is
signal, not noise: it's how you watch categories consolidate. The clearest current example is
xAI/SpaceX's $60B acquisition of Anysphere (Cursor), announced 2026-06-16 — a category-1
vendor buying a category-2 product, then training Grok 4.5 on that harness's session data.
That acquisition is not bleed, though — it is *vendor span*, the distinct dimension
formalized just below. Vertical integration across categories is the live structural story of
2026.

*Second instance (2026-07-30):* the harness-as-training-data-instrument pattern is not
exclusive to acquisitions. hermes-agent — open source, MIT — ships trajectory export and
compression tooling openly labeled "for training the next generation of tool-calling
models" (its maker, Nous Research, is a category-1 vendor). opencode's "stores no code or
context server-side" is the explicit counter-position. Two instances plus a named
counter-position make this a pattern to track, not an anecdote:
**who a harness's maker is at category 1 predicts what the harness collects.**

### Vendor span — when the categories stop being independent choices *(2026-08-16)*

Bleed and vendor span are different axes, and the framework reasons about them differently:

- **Bleed** is a property of a *tool* — one product reaching into an adjacent category (codex
  internalizing a sandbox, GSD shipping `gsd-pi`). Recorded per report, in the `bleed` note.
- **Vendor span** is a property of a *maker* — one vendor owning distinct products across
  several categories at once, and tuning them to each other. Recorded here, because it is a
  fact about a company, not about any single entry.

The frontmatter field is `maker:`, not `vendor:` ([ADR-0042](../adrs/0042-vendor-becomes-maker.md)) —
four of its values are private individuals, so the field cannot assert commerce. This
section keeps the narrower word **on purpose**: every row below is a company, and the
co-optimization it warns about is a commercial strategy. *Vendor* span is the subset of
maker span that has a business behind it, which is the part a reader has to plan around.

The framework's default posture treats the categories as **independent axes**: pick a model,
pick a harness, pick an environment. That holds for the field's composable middle — a Nous
model driven by OpenCode inside a Modal sandbox is three vendors and three separable
decisions. It **breaks for vertically-integrated vendors**, where the choices *co-vary*:
choosing the harness chooses the model, the sandbox, and the extension format, because one
maker ships all of them. This is the single most important thing the taxonomy has to warn
its reader about before they treat a category choice as free.

Clearest spanners as of 2026-08-16 (✓ tracked with a report · ○ observation-only, closed):

| Vendor | 1 · Model | 2 · Harness | 3 · Environment | 6 · Artifacts |
|---|---|---|---|---|
| **OpenAI** | gpt-5-6-sol ✓ | Codex CLI ✓ · cloud Codex ○ | Codex's *internalized* OS sandbox ✓ · cloud Codex microVM ○ *(bundle)* | — |
| **Anthropic** | opus/sonnet/fable/haiku ✓ | Claude Code ✓ *(observation-only, 2026-08-17)* | Managed Agents / code-exec container ○ *(bundle)* | skills, MCP ○ |
| **Google** | gemini-3-1-pro ✓ | Gemini → Antigravity CLI ✓ | — | — |
| **xAI** | grok-4-5 ✓ | Cursor ○ *(acquired 2026-06)* | — | — |
| **DeepSeek** | deepseek-v4 ✓ | dsh ✓ | — | — |
| **Alibaba (Qwen)** | qwen3-coder-next ✓ | qwen-code ○ *(candidate — a gemini-cli fork)* | — | — |
| **Moonshot AI** | kimi-k3 ✓ | kimi-code ○ *(candidate, created 2026-05-22)* | — | — |
| **Z.ai (Zhipu)** | glm-5.3 ✓ | ZCode ○ *(closed; "Official Harness for GLM-5.3")* | — | — |

**The direction is one-way, with no exceptions left** *(2026-08-26)*: every vendor here
spans **from** category 1 **into** category 2. A model maker ships a harness for its own
weights; no harness maker in the set has trained a model and moved the other way. **All
eight** vendors with a tracked model report ship one. For a reader choosing a category-1
model, the practical form of this is: *there is always a first-party harness, and it is
always the one the model was tuned against.*

### How this paragraph was wrong three times in one day

It is kept as a worked example, because the failure repeated after the lesson was written
down — twice.

1. **Six of eight.** Moonshot and Z.ai named as holdouts, excused as "*not yet*". Moonshot's
   `kimi-code` had shipped **2026-05-22**, three months earlier. The absence was inferred
   from *this repo having no report*.
2. **Seven of eight.** Z.ai called "the real exception… a strategy rather than a gap",
   on the strength of a **GitHub org search** returning only model repos. **ZCode is
   closed-source** — a proprietary desktop/CLI product sold on subscription tiers. It could
   never have appeared in that search.
3. Both corrections were written *in this section*, one after the other, by the same hand
   that then made the next version of the same mistake.

Each time the method was identical: **infer absence from a surface that structurally cannot
show the thing.** Once from `tools/` (which only holds what someone has already ingested),
once from GitHub (which only holds what is open source). That is the blind spot
[ADR-0041](../adrs/0041-vendors-matrix-removed.md) deleted a whole generated matrix over —
and this section reproduced it in prose within the hour, then again fifteen minutes later.

The operational rule: **a negative claim about a vendor's product line needs a search of the
vendor's own site, not of a repository host or of this repo.** The closed products are
exactly the ones a code-shaped search misses, and they are disproportionately the ones that
matter here — Claude Code, cloud Codex, Cursor, Managed Agents, and now ZCode are all
closed, and all belong to the biggest spanners.

**The standing falsifier moves accordingly.** The one-way rule now predicts that a *harness*
maker with no model — Anomaly, Cline, Continue, Earendil Works, Warp — trains or brands one.
That is the claim to watch; the model→harness direction is saturated and can no longer
surprise.

Two consequences a reasoner must carry:

1. **"Portable" means less inside a spanned stack.** MCP is portable across harnesses *in
   principle*; but a vendor owning model + harness + sandbox can co-optimize in ways a
   portable extension never reaches, so the portability guarantee is weakest exactly where a
   vendor is most integrated. Extension-bucket independence (the standards question) is a
   claim about the composable middle, not about a spanned stack.
2. **Attribution is confounded by construction.** When a spanned stack succeeds or fails,
   you cannot hold the model fixed and swap the harness to find the cause — the vendor did
   not build them to separate. This is the same confound README conclusion 2 records for
   benchmarks ("Codex CLI + GPT-5.5"), promoted from a measurement artifact to a structural
   property of the vendor.

**Why this table is hand-kept, not generated** (and it is the one deliberate exception to
rule 3 in this repo): the sharpest spanners are *closed* — Claude Code, cloud Codex, and
Managed Agents have no report files — so a frontmatter-generated matrix would **understate
vendor span precisely for the vendors that have the most of it.** A generated half used to
exist alongside it (`comparisons/vendors.md`, removed 2026-08-26,
[ADR-0041](../adrs/0041-vendors-matrix-removed.md)): it grouped every report by `vendor:`
string and was billed as the tracked-only **floor**, its distance from this table
quantifying the closed-product blind spot. The measurement decayed — by removal day both
surfaces read "4 spanners" over *non-identical* sets, so the gap it existed to show had
become a coincidence that looked like agreement. The claim it was carrying is one
sentence, and it is stated above. This table deliberately admits observation-only (○)
products to show the real shape, and is
illustrative, not an index — re-date it when a spanner's coverage changes rather than
trusting it to stay current on its own.

## Stress test

Five deliberately hard cases, classified. If a new case has no defensible home, the
taxonomy needs revision — not the case.

| Case | Verdict | Reasoning |
|------|---------|-----------|
| **Cursor's agent mode** | category 2, IDE-embedded | The IDE is the UI; the agent loop underneath is a harness. "IDE feature" describes the surface, not the type. Now bleeds into category 1 via xAI ownership. |
| **Claude Code Skills** | category 6, bundled in category 2 | Independently authored, versioned, and portable in principle — that's the extensions-bucket test. Shipping inside a harness is distribution, not identity. |
| **Devin** | category 2, bundles category 3 | A harness that happens to ship its own sandbox. You can't adopt one without the other, but bundling ≠ category identity. |
| **Aider** | category 2, opinionated | It *has* a methodology (commit per change, repo map), but you can't install that methodology on top of a different harness. Not portable → harness with strong defaults, not a framework. |
| **MCP itself** | Not a category — a standard | Forced the "Standards" section above. The protocol is a spec; its servers are category 6. |
| **ECC (everything-claude-code)** | **Resolved: category 6, extensions** (was category-4 provisional; resolved as category 5 pre-split, renumbered 2026-08-22 at the split[^adr-0020]) | Added 2026-07-28 as the live case; resolved 2026-07-30 at deep-dive. No process spine: workflow content is opt-in catalog items ("start with the workflow you need, not the full catalog"), and the multi-* orchestration commands outsource to an external runtime. A config pack at scale with a harness-independent learning runtime. The resolution **fired trigger (a) of the bucket demotion**[^adr-0002]. [`tools/6-extensions/ecc.md`](../tools/6-extensions/ecc.md). |
| **hermes-agent** | category 2 confirmed — with recorded strain | Resolved 2026-07-30 at deep-dive. The classification test worked: other things install *into* it (spec-kit → `~/.hermes/skills`), which is the harness signature. But it's a personal agent with a coding *posture* (a runtime mode entered inside a git repo), and it strains both category-2 axes — see the execution-axis note above. Kept at category 2 because the taxonomy classifies by *kind* (it runs the loop, assembles context, gates permissions, owns the UI), not by how much of the product is about coding. [`tools/2-harnesses/hermes-agent.md`](../tools/2-harnesses/hermes-agent.md). |
| **Warp** | category 2 — that runs *other* category-2 harnesses | Added 2026-08-11 at survey. The classification is not in doubt (own loop, embedding-indexed context assembly, execution-profile permissions, owns the UI), but two of its bleeds are new shapes. **Harness-over-harness:** `enum Harness { Oz, Claude, OpenCode, Gemini, Codex }` makes Warp's own agent one selectable backend among five for a spawned child agent, with per-harness drivers and transcript parsers (`app/src/ai/agent_sdk/driver/harness/`); the Codex driver installs Warp's plugin hooks into Codex and passes `--dangerously-bypass-hook-trust` so they run unreviewed. Orchestrating peers is category-4-shaped behaviour, but it fails the category-4 test — the process is not portable off Warp, it *is* Warp — so this is a harness with an orchestration tier, not a framework. **A fourth environment verb:** after bundle (Devin), bind (hermes), and internalize (codex), Warp **inhabits** — `crates/isolation_platform/` detects the container Warp is *already running inside* (`Docker`/`DockerSandbox`/`Kubernetes`/`Namespace`) to obtain a workload-identity token, rather than launching anything. [`tools/2-harnesses/warp.md`](../tools/2-harnesses/warp.md). |
| **Codex CLI's in-process sandboxing** | category 2 that *internalized* category 3 | Added 2026-07-30 at deep-dive. The environment relationship vocabulary had two verbs — *bundle* (Devin ships a sandbox product alongside) and *bind* (hermes attaches to Docker/SSH/Modal). codex is a third: Seatbelt policies, Landlock, bwrap, and a Windows sandbox are **compiled into the harness binary** and invoked per tool call, plus pre-main process hardening. Still category 2 — the sandbox is not independently distributed, so it fails the category test — but the scope note's prediction ("as autonomy rises, the environment question becomes more central") gains a data point: the environment became a *harness subsystem*. [`tools/2-harnesses/codex.md`](../tools/2-harnesses/codex.md). |

## Deliberate exclusions

- **Agent SDKs** (Claude Agent SDK, LangGraph, Mastra, PydanticAI) — a different consumer:
  you're *building* an agent rather than *using* one. Excluded for now, not dismissed;
  revisit if the repo's scope widens.
- **Human practices** — task decomposition, when to restart context, review discipline.
  Real and important, but they're techniques rather than tooling; they belong in
  `docs/`.

## Category indexes

| Category | Index |
|-------|-------|
| 1 · Models | [`tools/1-models/README.md`](../tools/1-models/README.md) |
| 2 · Harnesses | [`tools/2-harnesses/README.md`](../tools/2-harnesses/README.md) |
| 3 · Execution environments | [`tools/3-execution-environments/README.md`](../tools/3-execution-environments/README.md) |
| 4 · Workflow frameworks | [`tools/4-workflow-frameworks/README.md`](../tools/4-workflow-frameworks/README.md) |
| 5 · Memory | [`tools/5-memory/README.md`](../tools/5-memory/README.md) |
| 6 · Extensions (bucket) | [`tools/6-extensions/README.md`](../tools/6-extensions/README.md) |
| ✕ Cross-cutting (incl. standards) | [`docs/README.md`](README.md) |

Per-tool reports use [`tools/_template-tool-report.md`](../tools/_template-tool-report.md) — with
one exception: category 1 uses
[`tools/1-models/_template-model-report.md`](../tools/1-models/_template-model-report.md), because
that template's repo-shaped spine (pinned commit, mechanically collected repo facts, traced
architecture, drift check) has no subject when the thing being reported on is weights behind an
API. All of them are indexed flat, across categories, in
[`comparisons/tools.md`](../comparisons/tools.md).

## Decision records cited

One dated, immutable record per decision; immutable material predating a rename still
reads in superseded vocabulary — [`adrs/`](../adrs/README.md) carries the decoders.

[^adr-0002]: [ADR-0002 — Extensions demoted to a cross-category bucket](../adrs/0002-extensions-demoted-to-bucket.md), decided 2026-07-30.
[^adr-0003]: [ADR-0003 — execution environments stay a full category (adjudicated)](../adrs/0003-environments-stay-a-rung.md), decided 2026-08-16.
[^adr-0004]: [ADR-0004 — core-triad reframing](../adrs/0004-core-triad-reframing.md), decided 2026-08-17.
[^adr-0005]: [ADR-0005 — rename "portable artifacts" → "Extensions"](../adrs/0005-rename-to-extensions.md), decided 2026-08-17.
[^adr-0007]: [ADR-0007 — renumber: core triad 1–3, frameworks 4, extensions 5](../adrs/0007-renumber-core-triad-first.md), decided 2026-08-18.
[^adr-0008]: [ADR-0008 — Standards folded into cross-cutting](../adrs/0008-standards-into-cross-cutting.md), decided 2026-08-18.
[^adr-0010]: [ADR-0010 — two taxonomies: tool taxonomy + feature taxonomy](../adrs/0010-two-taxonomies.md), decided 2026-08-18.
[^adr-0011]: [ADR-0011 — graded gate-enforcement values (engine/hook/script/prose)](../adrs/0011-graded-gate-enforcement.md), decided 2026-08-18.
[^adr-0012]: [ADR-0012 — the category-2 feature set: `ptc` + graded `turn_end_gates`](../adrs/0012-layer-2-feature-set.md), decided 2026-08-18.
[^adr-0013]: [ADR-0013 — the `memory_features` registry block](../adrs/0013-memory-features-block.md), decided 2026-08-19.
[^adr-0016]: [ADR-0016 — extensions stay broad](../adrs/0016-extensions-stay-broad.md), decided 2026-08-19; superseded by ADR-0020.
[^adr-0019]: [ADR-0019 — coverage strata for category 5](../adrs/0019-category-5-coverage-strata.md), decided 2026-08-22; superseded in part by ADR-0020.
[^adr-0020]: [ADR-0020 — Memory becomes category 5; Extensions becomes category 6](../adrs/0020-memory-category-extensions-renumbered.md), decided 2026-08-22.
[^adr-0021]: [ADR-0021 — harness decomposition: three components, two descriptive axes](../adrs/0021-harness-three-component-decomposition.md), decided 2026-08-22.
[^adr-0022]: [ADR-0022 — repo-voice prose in refs is sweepable; decoders relocate to the ADR index](../adrs/0022-refs-repo-voice-sweepable.md), decided 2026-08-22.
[^adr-0023]: [ADR-0023 — components for categories 4 and 5; tracing discipline goes category-generic](../adrs/0023-category-4-5-components.md), decided 2026-08-25.
