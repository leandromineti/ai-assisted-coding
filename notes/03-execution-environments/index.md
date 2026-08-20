# Category 3 — Execution environments

`checked: 2026-08-20`

Where the agent's code actually runs, and what it can damage. See
[`../../taxonomy.md`](../../taxonomy.md).

The most-ignored category, because it's invisible until it fails.

## Seed inventory

| Environment | One-line | Isolation | Setup cost |
|-------------|----------|-----------|------------|
| **Host machine** | No isolation. The default, and the reason people are nervous about autonomy. | None | Zero |
| **git worktrees** | Parallel checkouts of one repo; lets several agents work without collision. | Filesystem only — same machine, same network, same credentials | Low |
| **Devcontainers** | Declarative dev environment in a container; reproducible toolchain. | Process + filesystem | Medium |
| **Docker** | General container isolation, hand-rolled. | Process + filesystem + network | Medium |
| **[E2B](e2b.md)** | Remote sandboxes purpose-built for agent code execution. **Deep-dived 2026-08-16** — Firecracker microVMs, no jailer, create-is-resume. The category's first and (so far) only report. | Full microVM/remote | Low, metered |
| **[Modal](modal.md)** | Serverless compute used as an agent sandbox; **gVisor `runsc`**, not a VM. **Read 2026-08-16** as the closed-environment control — client open, infra closed. | gVisor container | Low, metered |
| **Cloudflare Sandbox SDK** | Sandboxed execution on Workers; preview URLs, code interpreter. | Full remote | Low, metered |
| **Bundled (Devin, cloud Codex, Claude Code web)** | The harness ships its own sandbox; not separately selectable. | Vendor-defined | None — and no choice |

## The trap worth documenting first

Isolation that hides files the agent needs is a **category-3 problem that presents as a
category-2 bug**.

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

This is the clearest evidence I have that the category is real: nothing about the harness or
the model was broken.

## The component vocabulary

`added: 2026-08-20` *(from the category-5 boundary discussion — see the
[discussion-state note](../05-capability-extensions/index.md) — via the question "what
is the default environment?"; tested against this index's seed inventory and the codex,
Warp, and E2B deep-dives before recording)*

An execution environment is three components:

- **host** — machine + OS + installed toolchain + **network position** (network is
  declared here, not homeless: the rig's methodology 8a treats egress as an environment
  property, and this is where it lives).
- **principal** — the effective identity of the agent's process: OS permissions,
  ambient credentials (`~/.ssh`, keychains, dotfiles), inherited env vars. "User" in the
  default case, but the general term earns its keep: codex's internalized sandboxes
  restrict *only this component*, per tool call, without a new host or cwd; Warp's
  `inhabit` is the principal being *supplied by* the environment (workload-identity
  token from the detected container) rather than inherited.
- **working directory** — the anchor: where discovery walks from, what `pwd` context
  names, the unit the fidelity question attaches to.

**The default every harness runs in is {your machine, you, cwd} — full ambient
authority anchored at a folder.** The folder is what the agent is *pointed at*; host ×
principal is what it can *touch*; the category exists because of the gap between those
two, and every tool in the seed inventory is a device for narrowing it:

| Environment | Δ vs default |
|---|---|
| Host machine | none — the default itself |
| git worktrees | Δcwd only (the Isolation column's "same machine, same network, same credentials" said this in prose) |
| Devcontainers / Docker | Δhost + Δprincipal; cwd mounted |
| E2B / Modal / Cloudflare | Δ all three (new machine, synthetic principal, uploaded anchor) |
| Bundled (Devin, cloud Codex) | all three vendor-fixed — no choice per component |
| codex internalize | Δprincipal only, **per tool call** — the midpoint of the substitution axis below |

The three recorded category questions map one-to-one: **blast radius** = host ×
principal · **fidelity** = host toolchain + cwd completeness (the worktree trap is a
cwd incomplete relative to the toolchain) · **parallelism** = the cost of multiplying
cwd (worktrees) vs hosts (sandboxes).

**The substitution axis** (the lens this vocabulary hands back to category 2):
permission models and environments are substitutes for restricting the principal —
category-2 gates do it per action in software the model flows through; codex
internalize per action in the OS; containers structurally; pi (registered 2026-08-19,
category-2 index) ships *no permission system* and recommends containers — the fully
structural end. Warp is the cautionary specimen: a six-level chain for its own
principal on the host, then child harnesses launched with every gate bypassed —
category-2 discipline spent where the category-3 default made it most needed.

## The relationship vocabulary

`checked: 2026-08-20`

This is the category's own analytic contribution, and it was produced the hard way — one verb
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
A harness with *no* relationship to category 3 is a legitimate design position, and pretending
otherwise would inflate the category's apparent importance.

Rendered from frontmatter in
[`../../comparisons/environments.md`](../../comparisons/environments.md).

## Adjudication — does this category survive its own falsifier?

`checked: 2026-08-20`

The taxonomy pre-committed to a test: *"if sustained study never shows a category-3 fact
changing a tool choice or explaining a failure, demote this category to a cross-cutting
note."* After three weeks and 22 tool reports, here is the verdict. It is deliberately
split, because the falsifier has two clauses and they came out differently.

**Clause (b), "explaining a failure" — passed, decisively.** The worktree/gitignore trap
above is exactly that: an agent failure whose cause was neither the model nor the harness,
misdiagnosable as a category-2 bug indefinitely. It also generated two non-obvious
sub-findings (Turbopack rejecting symlinked `node_modules`; linked directories having to
be *fully* untracked) that no amount of harness study would have surfaced. Design
principle E2 generalizes it, and hermes independently engineers around the same class from
the other side.

**Clause (a), "changing a tool choice" — not passed. No instance exists.** The trap changed
a *configuration* choice (disable worktrees, or bootstrap them), not a choice between
tools. Nothing in this repo records picking tool X over tool Y because of a category-3 fact.

**But the sharper finding is that the falsifier asked a slightly wrong question.** category 3
is real; it is just not real *in the way the taxonomy describes it*. Every piece of
evidence the category has produced in three weeks is a **property of a category-2 tool**, not a
fact about an environment:

- All four verbs describe harness behaviour. They live in category-2 frontmatter.
- All four discoveries arrived as bleed notes inside category-2 deep-dives. **Not one came
  from studying an environment on its own.**
- The generated matrix has **zero category-3 rows** — 4 of 22 reports declare `environments:`,
  and all four are harnesses.
- The `worktree` column is **empty across every row**, despite the worktree trap being this
  category's founding scar. The one environment with a real war story here has no verified
  support data anywhere.
- The taxonomy's own scope note concedes the members are "borrowed infrastructure" that
  "earn no survey of their own here" — the category is defined such that its entities don't
  merit study. A category whose members nobody is meant to study.

So: **category 3 survives as an analytic lens and fails as a population.** It is not a
cross-cutting concern (those — context engineering, verification, cost — appear at several
categories at once; this appears at exactly one, as a relationship). It is closer to a
**fifth axis of category 2** than to a category of its own: the environment question is real,
load-bearing, and answered entirely by looking at harnesses.

**The proposed revision, gated rather than executed.** Re-describe category 3 as the
*environment-relationship axis* of category 2 — keeping the number as a storage key, exactly
as the extensions bucket kept its number at its 2026-07-30 demotion (both since renumbered — ADR-0007). Not executed today because it should turn on
evidence, not tidiness. **Trigger: the first report of an environment studied as a product
in its own right** (E2B, Modal, Cloudflare Sandbox SDK — the agent-native ones, not
borrowed infrastructure). If such a report produces findings that are *not* restatements
of some harness's relationship to it, the category is a population after all and stays a
category of its own. If it can't, or if nobody writes one within six months, the revision
executes on the grounds that a category nobody populates in six months of active study is
not a category.

**What would have falsified the category outright**, recorded so this isn't unfalsifiable in
retrospect: no worktree trap, no verb distinctions, and every environment fact reducing to
"it's a container, containers isolate things." category 3 cleared that bar easily. What it has
not cleared is the bar for being a *category*.

## Gate RESOLVED — 2026-08-16, "keep it a category" (the pending verdict above is now falsified)

The trigger fired the same day it was recorded, faster than expected: the E2B deep-dive
([`e2b.md`](e2b.md)) is the first report of an agent-native environment studied as a product
in its own right, and **it passes the gate decisively.** ~26 findings that are facts about
the environment itself against 6 that restate harness-attachment, with a clean discriminator:
**every one of the 26 is invisible from the SDK.** A study of "how a harness attaches to E2B"
produces the six and stops — it never learns that Firecracker runs with no jailer, that
create-is-resume with no warm pool, that the credential-injection proxy is closed-source, or
that guest `kcompactd` is disabled for host snapshot-diff economics.

So the "fails as a population" clause of the pending verdict is **wrong**, and the reasoning
is worth keeping visible: one genuine population member is all that claim needed to be false,
and E2B is unambiguously one — independently distributed (zero AI-framework deps, generic
Linux wire protocol), and productive of substantive non-derivative findings. **category 3
holds.** The proposed "fifth axis of category 2" revision does **not** execute; the reverse
trigger (six months with no such report) is void because the report exists.

**Two qualifications carried from the E2B read, because they bound what was actually shown:**

1. **The axes are not equally productive.** Blast radius, fidelity, and credential exposure
   each produced multiple non-obvious findings; **parallelism and startup produced mostly
   numbers** — real and comparable, but datasheet-shaped. The category's justification rests on
   the first three. If a future environment read finds *only* the numeric axes productive,
   that weakens the category again.
2. **The verdict rests on one instance, and a favourable one.** E2B open-sources its
   infrastructure; that is what made the environment-facts reachable. The open follow-up,
   now the category's live question, is whether a **closed** environment (Modal, Daytona,
   Cloudflare Sandboxes) yields the same or only testimony. If only testimony, the refined
   finding would be "category 3 is real but legible only when the environment is open" — sharper
   than either original pole. Filed on issue #11.

*What still stands from the pending verdict:* clause (b) of the original falsifier
("explaining a failure") passed independently via the worktree trap, and the relationship
vocabulary remains category 3's own analytic contribution. What is overturned is only the
"fails as a population / demote to an axis" conclusion.

### Successor question — first evidence (2026-08-16, Modal)

Bound #2 above asked whether the E2B pass was an artifact of E2B being open source. The
control read is [`modal.md`](modal.md): Modal's client is open (Apache-2.0), its
**infrastructure closed**. Result — **the category survives closure, with a precise grade cap:**

- Modal still yields ~9 **source-verified** environment-facts, because its client ships a
  richly-commented gRPC proto (a "leaky contract" — it must name every capability clients
  configure) *and* the in-container agent (`cuda-checkpoint --toggle` is a literal subprocess
  call). Plus mechanism-level **testimony** (gVisor built-in checkpoint/restore, a "pages"
  file, FUSE lazy-loading overlay).
- **But closure caps the grade at "declared / cited," never "audited."** Four of E2B's five
  signature findings (no-jailer, cgroups-account-only, kcompactd-disabled, closed-proxy-seam
  internals) have **no recoverable analog** — they are mechanism-below-the-API-line — and the
  fifth (claim-vs-code discrepancy) is *structurally impossible*: with no source, you cannot
  catch a vendor being wrong.

**The two reads together are stronger than either alone.** E2B (Firecracker microVM) and Modal
(gVisor userspace kernel) are two fundamentally different isolation primitives, both
agent-native, with one **convergent** egress-control shape (domain-allowlisting restricted to
TLS/443 in both). That is a **population with internal variation** — precisely what "category 3
holds" required and what a one-instance read could not show.

**Refined law, replacing the old binary framing:** *an execution environment is legible in
proportion to (client-contract richness + vendor disclosure); only open infrastructure yields
audit-grade facts.* n=2 for the category; n=1 for "closed but disclosure-rich." A **maximally**
closed environment — thin uncommented client, no engineering blog — is still untested, and is
the live question on issue #11.

## Axes that matter

- **Blast radius** — what can it destroy? Files, the repo, the machine, production?
- **Fidelity** — does the project's tooling actually run in there, unmodified?
- **Parallelism** — can N agents work at once without colliding?
- **Startup cost** — per-run overhead, in seconds and in dollars.
- **Credential exposure** — what secrets are reachable from inside?

## Open questions

- ~~Can an agent-native environment produce a finding that isn't a restatement of harness
  attachment?~~ **Answered 2026-08-16: yes (E2B). Category 3 holds.**
- ~~Does that hold for a **closed** environment?~~ **First evidence 2026-08-16 (Modal): yes,
  but only to audit-grade where the infra is open — closed caps the grade at declared/cited.**
  See the successor-question section above. Remaining: a **maximally** closed environment
  (thin client, no engineering disclosure) — untested. Issue #11.
- ~~Why has nobody verified `worktree` support for any harness?~~ **First cell filled
  2026-08-17: Claude Code, observed** — native enter/exit-worktree operations plus
  per-subagent worktree isolation ([`../02-harnesses/claude-code.md`](../02-harnesses/claude-code.md)).
  The irony is recorded there: the first verified worktree support is on the *closed*
  harness, from product-surface observation. The rest of the column is still `·` —
  the universal-or-unexamined question stands for the open harnesses, where checking
  is a grep away.
- Isolation and fidelity trade off directly. Where's the useful middle?
- Does parallel multi-agent work actually pay, once the environment-bootstrap tax is
  counted honestly?
- How much autonomy would a genuinely disposable environment justify? Is sandboxing the
  real unlock for hands-off agents, rather than better models?
