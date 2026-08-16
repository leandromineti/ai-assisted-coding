# Layer 5 — Execution environments

`checked: 2026-08-16`

Where the agent's code actually runs, and what it can damage. See
[`../../taxonomy.md`](../../taxonomy.md).

The most-ignored layer, because it's invisible until it fails.

## Seed inventory

| Environment | One-line | Isolation | Setup cost |
|-------------|----------|-----------|------------|
| **Host machine** | No isolation. The default, and the reason people are nervous about autonomy. | None | Zero |
| **git worktrees** | Parallel checkouts of one repo; lets several agents work without collision. | Filesystem only — same machine, same network, same credentials | Low |
| **Devcontainers** | Declarative dev environment in a container; reproducible toolchain. | Process + filesystem | Medium |
| **Docker** | General container isolation, hand-rolled. | Process + filesystem + network | Medium |
| **E2B** | Remote sandboxes purpose-built for agent code execution. | Full VM/remote | Low, metered |
| **Modal** | Serverless remote compute, used as an agent sandbox. | Full remote | Low, metered |
| **Cloudflare Sandbox SDK** | Sandboxed execution on Workers; preview URLs, code interpreter. | Full remote | Low, metered |
| **Bundled (Devin, cloud Codex, Claude Code web)** | The harness ships its own sandbox; not separately selectable. | Vendor-defined | None — and no choice |

## The trap worth documenting first

Isolation that hides files the agent needs is a **layer-5 problem that presents as a
layer-2 bug**.

`git worktree add` checks out only *tracked* files. Anything gitignored — `node_modules/`,
build output, `.env*`, and (on GSD-convention projects) `.planning/` and `CLAUDE.md` — is
simply absent from a fresh worktree. The agent then can't see its own plan or run the
project's tooling, and a well-behaved one refuses rather than fabricating.

The instinct to fix it by un-ignoring things is wrong — secrets and build artifacts must
stay ignored, and un-ignoring the planning directory alone still leaves a worktree whose
tooling can't run. Two fixes that hold up:

1. **Disable worktrees.** Executors run sequentially against the main checkout, which sees
   everything. Simplest; costs intra-wave parallelism.
2. **Bootstrap each worktree.** As the agent's first action, link the gitignored
   dependencies in from the main checkout — `node_modules`, build output, `.env*`, the
   planning directory, the rules file. Keeps parallelism.

Two caveats found the hard way on fix 2 (personal experience, mid-2026):

- **Symlinked `node_modules` breaks `next dev`.** Turbopack rejects it outright — *"Symlink
  node_modules is invalid, it points out of the filesystem root."* To run a dev server from
  a worktree, use a hardlink clone instead: `cp -al ../main/node_modules ./node_modules` —
  instant, no duplicate disk. Symlinks remain fine for `tsc`, `vitest`, and Prisma.
- **The linked directories must be *fully* untracked.** One stray committed file inside
  them and the checkout shadows your symlink with a partial directory.

This is the clearest evidence I have that the layer is real: nothing about the harness or
the model was broken.

## The relationship vocabulary

`checked: 2026-08-16`

This is the layer's own analytic contribution, and it was produced the hard way — one verb
per deep-dive, each arriving as a surprise that the existing words couldn't describe. It
lived scattered across four `taxonomy.md` stress-test rows until 2026-08-16; the taxonomy
now points here rather than defining it in four places.

The question it answers is not *which* environment a tool reaches, but **how it relates to
one**:

| Verb | Instance | What it means |
|---|---|---|
| **bundle** | Devin | Ships its own sandbox alongside the harness. Not separately selectable — you can't adopt one without the other. |
| **bind** | hermes-agent | Attaches to independently-distributed environments as swappable backends (8 of them: local, Docker, SSH, Singularity, Modal ×2, Daytona, Vercel Sandbox). |
| **internalize** | codex | The sandbox is *compiled into the harness binary* — Seatbelt, Landlock, bwrap, a Windows sandbox — and invoked per tool call. No external environment involved. |
| **inhabit** | Warp | Detects the environment it is **already inside** (`Docker`/`DockerSandbox`/`Kubernetes`/`Namespace`) to obtain a workload-identity token. It launches nothing; it introspects. |

**And the null case, which matters as much as the four.** opencode reaches `host` and does
nothing about isolation — it neither bundles, binds, internalizes, nor inhabits. Its
`environment_relation` is deliberately unset rather than forced into the nearest verb.
A harness with *no* relationship to layer 5 is a legitimate design position, and pretending
otherwise would inflate the layer's apparent importance.

Rendered from frontmatter in
[`../../comparisons/environments.md`](../../comparisons/environments.md).

## Adjudication — does this layer survive its own falsifier?

`checked: 2026-08-16`

The taxonomy pre-committed to a test: *"if sustained study never shows a layer-5 fact
changing a tool choice or explaining a failure, demote this layer to a cross-cutting
note."* After three weeks and 22 tool reports, here is the verdict. It is deliberately
split, because the falsifier has two clauses and they came out differently.

**Clause (b), "explaining a failure" — passed, decisively.** The worktree/gitignore trap
above is exactly that: an agent failure whose cause was neither the model nor the harness,
misdiagnosable as a layer-2 bug indefinitely. It also generated two non-obvious
sub-findings (Turbopack rejecting symlinked `node_modules`; linked directories having to
be *fully* untracked) that no amount of harness study would have surfaced. Design
principle E2 generalizes it, and hermes independently engineers around the same class from
the other side.

**Clause (a), "changing a tool choice" — not passed. No instance exists.** The trap changed
a *configuration* choice (disable worktrees, or bootstrap them), not a choice between
tools. Nothing in this repo records picking tool X over tool Y because of a layer-5 fact.

**But the sharper finding is that the falsifier asked a slightly wrong question.** Layer 5
is real; it is just not real *in the way the taxonomy describes it*. Every piece of
evidence the layer has produced in three weeks is a **property of a layer-2 tool**, not a
fact about an environment:

- All four verbs describe harness behaviour. They live in layer-2 frontmatter.
- All four discoveries arrived as bleed notes inside layer-2 deep-dives. **Not one came
  from studying an environment on its own.**
- The generated matrix has **zero layer-5 rows** — 4 of 22 reports declare `environments:`,
  and all four are harnesses.
- The `worktree` column is **empty across every row**, despite the worktree trap being this
  layer's founding scar. The one environment with a real war story here has no verified
  support data anywhere.
- The taxonomy's own scope note concedes the members are "borrowed infrastructure" that
  "earn no survey of their own here" — the layer is defined such that its entities don't
  merit study. A rung nobody is meant to stand on.

So: **layer 5 survives as an analytic lens and fails as a population.** It is not a
cross-cutting concern (those — context engineering, verification, cost — appear at several
layers at once; this appears at exactly one, as a relationship). It is closer to a
**fifth axis of layer 2** than to a rung of its own: the environment question is real,
load-bearing, and answered entirely by looking at harnesses.

**The proposed revision, gated rather than executed.** Re-describe layer 5 as the
*environment-relationship axis* of layer 2 — keeping the number as a storage key, exactly
as layer 3 kept its number after demotion. Not executed today because it should turn on
evidence, not tidiness. **Trigger: the first report of an environment studied as a product
in its own right** (E2B, Modal, Cloudflare Sandbox SDK — the agent-native ones, not
borrowed infrastructure). If such a report produces findings that are *not* restatements
of some harness's relationship to it, the layer is a population after all and stays a rung.
If it can't, or if nobody writes one within six months, the revision executes on the
grounds that a layer nobody populates in six months of active study is not a layer.

**What would have falsified the layer outright**, recorded so this isn't unfalsifiable in
retrospect: no worktree trap, no verb distinctions, and every environment fact reducing to
"it's a container, containers isolate things." Layer 5 cleared that bar easily. What it has
not cleared is the bar for being a *rung*.

## Axes that matter

- **Blast radius** — what can it destroy? Files, the repo, the machine, production?
- **Fidelity** — does the project's tooling actually run in there, unmodified?
- **Parallelism** — can N agents work at once without colliding?
- **Startup cost** — per-run overhead, in seconds and in dollars.
- **Credential exposure** — what secrets are reachable from inside?

## Open questions

- **The one that decides this layer's fate:** can an agent-native environment (E2B, Modal,
  Cloudflare Sandbox SDK) produce a finding that *isn't* a restatement of some harness's
  relationship to it? That is the adjudication's trigger, and nothing else about layer 5
  matters as much until it is answered.
- Why has nobody verified `worktree` support for any harness, when the worktree trap is
  this layer's founding scar? Either it is universally supported and therefore boring, or
  nobody looked. The matrix currently cannot tell those apart.
- Isolation and fidelity trade off directly. Where's the useful middle?
- Does parallel multi-agent work actually pay, once the environment-bootstrap tax is
  counted honestly?
- How much autonomy would a genuinely disposable environment justify? Is sandboxing the
  real unlock for hands-off agents, rather than better models?
