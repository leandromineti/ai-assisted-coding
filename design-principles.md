# Derived design principles

`derived: 2026-07-30` · status: **hypotheses under revision, not verified best practices**

What the documented tools converged on — and what they still dispute — read as design
guidance. Every principle below is *derived from the evidence in this repo's reports*,
cited and dated; none is imported from blog-post folklore.

**Evidence base at derivation time:** two deep-dives (opencode, hermes-agent), three
surveys (cline, continue, spec-kit), one framework run end-to-end (gsd-core,
experiment 01), one preregistered experiment with results. *Updated 2026-08-17:* two
frameworks now run end-to-end (spec-kit via exp-02's full pipeline), two preregistered
experiments with results. Known biases: n is small;
the sample is survivorship-filtered (tools got read *because* they're prominent); and a
pattern shared by successful tools is what builders *believe*, not what's been measured
to work. Where a principle rests on a single well-engineered instance, it says so.

**Confidence vocabulary** (used on every principle):
- **convergent** — ≥2 independent implementations arrived at the same shape;
- **single-instance** — one tool, but structurally argued, not incidental;
- **contested** — the set visibly disagrees; recorded as a decision you must make, not
  a principle to follow.

**Revision rule:** every future deep-dive or experiment must confront this file —
confirm, contradict, or note silence per relevant principle. A principle no new
evidence has touched in two read-cycles gets flagged stale.

---

## Layer 2 — harness design

**H1. Treat running out of context as a normal loop outcome, not an error.**
*(convergent — 3 instances)* opencode models one provider turn as
`"compact" | "stop" | "continue"` — compaction is a peer of finishing
([opencode](notes/02-harnesses/opencode.md), `processor.ts:30`). hermes wraps
compression in a pluggable `ContextEngine` ABC with a documented lifecycle, and names it
the *only* sanctioned exception to prompt immutability
([hermes-agent](notes/02-harnesses/hermes-agent.md)). codex compacts mid-turn as a loop
`continue`, compacts *pre-sampling* before turns, and even exposes a
`new_context_window` tool so the model can request rollover itself
([codex](notes/02-harnesses/codex.md), confirmed 2026-07-30). Designs that treat
overflow as an exception path are the ones that break on long tasks.

**H2. The loop needs an explicit stuck-state policy — and who resolves it is a product
decision.** *(**contested** since 2026-08-16 — was "convergent on existence, contested on
resolution; one silence" until codex's absence was verified; see the settlement note
below)* Both
2026-07-28 deep-dived harnesses detect repeated-identical-call loops. opencode escalates
to the *human* through the permission subsystem (doom-loop as a permission prompt);
hermes resolves *in-band* with the model (warning guidance → synthetic tool results →
bounded halt). The principle is that silence is not a policy; the human-vs-model choice
is a position on autonomy. *Revision-rule note (2026-07-30):* the codex read found no
repeated-call guard in the turn path — recorded in its report as unverified absence,
not a counter-instance; settle it before counting codex either way.

*Settled 2026-08-16 — codex is a verified counter-instance, and the confidence marker
moves.* A workspace-wide grep at HEAD finds no repeated-call guard and no iteration cap
anywhere in codex's 94 crates, and nothing in 206 commits of drift adds one
([`notes/02-harnesses/codex.md`](notes/02-harnesses/codex.md)). So of the three
deep-dived harnesses, **two detect the loop and one deliberately does not** — this is
`contested`, not `convergent on existence`. The principle survives in weaker form: where
a harness *does* guard, the human-vs-model choice is a real position on autonomy. What
cannot be claimed any more is that guarding is what serious harnesses converge on.
codex's silence is also not obviously carelessness — it is the harness that ends turns on
model-declared completion with no step budget at all, so a repeated-call guard would be
the only bound in a design that otherwise trusts the model to stop. Worth asking the next
deep-dive explicitly, since a third data point either way settles the shape.

**H3. Two chokepoints, not one: shape what the model can see, then gate what it does.**
*(convergent — the strongest architectural pattern in the set; deepened 2026-07-30)*
opencode filters the tool list before the model sees it (`visibleTools`) and gates
execution at call time (`Permission.ask`). hermes filters the schema by service
availability (`check_fn`, TTL-cached) and gates dangerous commands at dispatch, with
hard write-denials underneath that no approval can override. The emphases differ
(permission-filtering vs availability-filtering) but the two-stage architecture is
identical: **visibility shaping pre-decision, execution gating post-decision,
invariants below both.** codex confirms and extends it to a third, compiled layer:
per-step advertised-tool finalization → `SafetyCheck` classification → execution
*inside an in-process OS sandbox* (Seatbelt/Landlock/bwrap), where approval cannot
grant what the sandbox denies ([codex](notes/02-harnesses/codex.md)). The revised
statement: visibility, decision, **enforcement** — and the strongest designs make the
third layer mechanical, not prose.
*Earliest measured evidence found (2026-08-17, [swe-agent-2024](refs/swe-agent-2024.md)
full read):* the 2024 ACI ablations price both chokepoints separately, holding the
model fixed — visibility shaping (100-line viewer window beats both 30 lines and
full file; last-5 history collapse beats full history, +3.0pp) and mechanical
enforcement (an in-`edit` linter that *discards* invalid edits, +3.0pp) each buy
points, and a badly shaped tool (iterative search) scores *below having no tool at
all* (−6.0 vs −2.3). The pattern this repo found convergent in 2026 harness source
was measured at NeurIPS 2024.

**H4. Prompts are versioned data, not string literals.** *(convergent, spans layers 2
and 4)* opencode imports tool descriptions from `.txt` files; spec-kit's product *is*
markdown templates, with 131 commits debugging them like code; GSD is 1,398 markdown
files against 810 of code; hermes builds its skill index from `SKILL.md` frontmatter
with snapshot caching. Prose that drives the model belongs in diffable artifacts with
their own history.

**H5. Cache economics govern prompt architecture — but "never mutate the prefix" has
two implementations, not one.** *(revised 2026-07-30 per the revision rule)* Original
form: order by volatility, never mutate the prefix, prefer staleness to invalidation —
hermes' design law ("per-conversation prompt caching is sacred"), paid for with
date-only timestamps, stale-by-design git snapshots, deferred mode flips.
Corroborating: exp-01 found cache reads *dominating* framework spend (~30–50× baseline);
opencode counts cache reads toward its overflow budget (cheap ≠ absent). **codex showed
a third position that keeps the invariant while dropping the staleness cost:** rebuild
ambient state per step as a sectioned `WorldState`, snapshot-diff it, and **append only
the delta** to history — the prefix stays byte-stable *and* the model sees fresh state,
paid for in machinery and history growth ([codex](notes/02-harnesses/codex.md)). The
durable core of the principle is *append-only prefix discipline*; freshness-vs-staleness
is an implementation choice on top of it. Also recorded as differentiation axis 6 in
[`notes/02-harnesses/index.md`](notes/02-harnesses/index.md).

**H6. Termination must be designed; budgets shape behavior in ways you choose.**
*(convergent on the first clause, two designs on the second)* opencode terminates on
explicit conditions (finish reasons, content filters, structured-output failure) with no
step budget; hermes caps iterations (500 parent / 50 subagent) and *refunds*
programmatic-tool-calling turns — a deliberate incentive for the model to collapse tool
chains into scripts whose intermediate results never touch context. If you meter
something, you're steering the model toward whatever the meter doesn't count. Choose
knowingly.

**H7. Model-agnostic is not prompt-agnostic — you must take a position on model
divergence, and no position currently has eval backing.** *(contested — five documented
positions as of 2026-07-30)* Nine full per-model prompts (opencode); one prompt after
*dismantling* a per-family registry (cline); ~15 lines betting prompts barely matter
(continue); one shared prompt plus ~4.4KB of per-family patches covering every major
family except Anthropic's (hermes); and the vendor-native pole — codex swaps model
instructions per model slug *inside* its WorldState, per-model prompting applied to one
vendor's own family. README conclusion 1 has the detail. This file records it as a
*forced decision*, not a principle: harness builders cannot avoid it, and none of the
five has published evidence.

**H8. Keep the core a narrow waist; ship capability at the edges as data.**
*(convergent)* hermes states it outright (every core tool is paid for on every API
call; new capability arrives as skills/plugins) and enforces it with service-gated
schema entries. opencode's `packages/llm` redesign draft draws the same line by
excluding permissions, sessions, and orchestration from the model-calling package.
cline's growth (SDK, CLI, hub around a core) rhymes. The waist is the loop + dispatch;
everything else should be removable.

## The artifacts bucket (formerly layer 3) — extension design *(two principles; bucket status per the 2026-07-30 taxonomy revision)*

**X1. Design for the waist everything converged on: a prompt file in a directory.**
*(convergent, structural)* spec-kit compiles one definition to 44 harnesses precisely
because "slash command = prompt file" became universal; skills reached convention-level
the same way (`SKILL.md` consumed by ≥4 harnesses — README conclusion 3). An extension
that needs more than files-in-known-directories forfeits portability — see F1 for what
that costs frameworks.

**X2. Standing-instruction surface is a hard budget; bodies load on demand.**
*(single-instance mechanism, structurally forced everywhere)* hermes budgets its skill
index at ~60 chars of description per skill in the system prompt — its authoring
standards call the limit "NOT cosmetic: anything past char 60 is silently cut and never
routes" — and loads skill bodies only on invocation. The general form: every installed
extension competes for the same standing-context budget, so the *index* must be cheap
and the *content* just-in-time.

## Layer 4 — workflow-framework design

**F1. The methodology is prose, prose doesn't bind — plan the deterministic escape
hatch from day one.** *(convergent — 3 instances, one an existence proof; strengthened
2026-07-31)* Both frameworks first studied hit enforcement-by-typography limits
(spec-kit fixed hook execution twice by rewriting instructions "more forcefully"; its
constitution went eight months unenforced) and both grew deterministic engines
(spec-kit's `workflows/` YAML runner, GSD's `gsd-pi`). Layer-4→2 bleed is the
structural symptom. **OpenSpec is the existence proof for the "from day one" clause:**
its deterministic engine (delta-merge compiler, DAG workflow engine over declarative
schemas, machine validator) is the *founding architecture*, with prose shrunk to thin
CLI adapters (`allowed-tools: Bash(openspec:*)`) —
[openspec](notes/04-workflow-frameworks/openspec.md). If a gate *must* hold, it
eventually needs code, not capitalization — and the lean pole shows starting there is
viable.

**F2. Spend tokens measuring the domain, not on ceremony.** *(n=1, preregistered;
under active test)* Exp-01's entire observed quality margin traced to agents that
*measured* git (fixture repos, crafted commits, timezone probes) and to verification
gates with measured expected values — almost none to the surrounding process ceremony,
at ~30–50× cost (README conclusion 6). **Confirmed by exp-02 (2026-08-17, measured,
n=1 per arm against an n=5 baseline band):** the complementary claim held — intent
capture *without* measurement produced trap-identical code (19/21 = 19/21, same two
failures) at 7.8× cost, and the mechanism was visible: clarify converted the
exit-code ambiguity into a documented *wrong* decision its tests then enforced,
while pinning UTC output right — steering without discovery (README conclusion 11).
Exp-03 is designed to isolate this principle directly. This is the repo's most
consequential hypothesis, which is exactly why it's being tested rather than trusted.

**F3. Fresh context per stage works as a refinement funnel — but only if the return
path is compact.** *(convergent, with the boundary condition observed in both
directions)* GSD's staged fresh contexts caught each prior stage's vagueness four times
in one run (exp-01). spec-kit forked `/analyze` into a subagent and **reverted** it —
the 300–500-line report re-entered the main context anyway and compounded until
sessions froze (#3185). Isolation pays when stage outputs are contracts (task graphs,
verdicts), not transcripts.

**F4. Budget human attention as an explicit, designed quantity.** *(convergent across
layers)* spec-kit caps clarification markers at 3, clarify questions at 5, asks one at
a time, and attaches a recommended answer acceptable with "yes" — attention economics
in the template grammar. hermes gates its self-improvement asks behind nudge intervals
rather than firing per-turn. The anti-pattern is unbounded question streams; the
instrument for pricing this is exp-02's attention-split measurement. *First measured
2026-08-17 (exp-02 Run B): the ration is real — one clarify question and one
remediation offer across a full 7-step pipeline, ~63s orchestrator-blocked of 21m33s
total. The cap did its job; the cost moved to the answer's* quality *(the one
question got the trap-deciding deferral), which attention-split does not price.*

**F5. Verification gates must fail closed, abstain when subjective, and control their
false-positive rate.** *(convergent, three complementary lessons)* Fail-closed: the
rig's rule — a verifier that passes an empty environment is a scorer bug — earned its
keep catching vacuous T4/T5 passes before any run. Abstention: GSD's verifiers return
`human_needed` on subjective checks instead of auto-passing. False-positive control:
hermes' verification-stop ships a suppression list because a gate that nags on README
edits trains users to bypass it. A gate missing any of the three degrades into either
theater or noise. *Vocabulary sharpened 2026-07-31 (openspec read):* gates come in
three mechanisms — **format** gates (deterministic checks on artifacts: OpenSpec's
validator), **prose** gates (the model reading instructions: spec-kit's constitution
check), and **measured** gates (checks against measured domain behavior: GSD/exp-01) —
and only the third traced to exp-01's quality margin. Determinism and domain-contact
are independent axes; a gate can be fully deterministic and never touch behavior.

**F6. Installing a methodology means granting prose your harness's authority —
maintainership is a security property.** *(single-instance, structural)* GSD's upstream
went dark amid a token rug-pull association; the community fork explicitly states it
cannot verify upstream security and forked for that reason. Layer-4 supply chain is
real: you are `curl | sh`-ing *instructions* that will run with everything your agent
can touch.

## Layer 5 — execution-environment design

**E1. Blast radius sets the autonomy ceiling — buy autonomy with isolation, not model
quality.** *(convergent; taxonomy scope-note position)* Every fully-autonomous product
documented bundles a sandbox, not a smarter model; hermes ships eight terminal-backend
implementations and its serverless pitch is an *economics* answer to keeping an
always-on agent isolated. The same permission flag that is reckless on a host is sane
in a container.

**E2. Isolation without fidelity produces layer-2-looking failures — engineer the
fidelity back explicitly.** *(convergent)* The worktree/gitignore trap
([`notes/05-execution-environments/`](notes/05-execution-environments/index.md)):
isolation that hides `node_modules`/`.env`/plans breaks agents in ways misread as
harness bugs. hermes engineers around the same class from the other side — file-sync
plus a file-based RPC transport so programmatic tool calling still works *inside*
remote backends. Isolation is only half the design; the other half is what you
deliberately let back in.

**E3. How a harness *relates* to its environment is a design position, and there are
exactly four — plus abstention.** *(convergent — four instances, one per verb, each found
at a different deep-dive)* **bundle** (Devin ships one), **bind** (hermes attaches to
eight swappable backends), **internalize** (codex compiles Seatbelt/Landlock/bwrap into
the binary), **inhabit** (Warp detects the container it is already inside for workload
identity). opencode takes the fifth position: **none of them** — it runs on the host and
does nothing about isolation, which is a choice rather than an omission. Defined in
[`notes/05-execution-environments/index.md`](notes/05-execution-environments/index.md),
rendered in [`comparisons/environments.md`](comparisons/environments.md).

*Recorded with the principle, because it is the uncomfortable part:* all four verbs are
properties of **layer-2 tools**, discovered inside layer-2 reads. The 2026-08-16
adjudication first concluded from this that layer 5 fails as a population and proposed
demotion to a layer-2 axis — **then the E2B read the same day overturned it** (README
conclusion 9). E2B is a layer-5 entity that produces substantive facts *about the
environment*, not about any harness's relationship to it (E4 below is one), so the verbs
being harness-side does not make the layer harness-side. E1–E3 stand as layer-5 principles.

**E4. An execution environment's economics leak upward into kernel and scheduler choices
that no harness can see.** *(single-instance — E2B, 2026-08-16; structurally argued)* Every
"create" is a snapshot **resume** with no warm pool; the resume working-set is computed by
booting the template twice at build time and intersecting touched pages; guest `kcompactd`
is disabled because host-side hugepage backing would dirty the snapshot diff; `discard` on
the guest ext4 mount is a snapshot-*size* optimization, not a speed one. These are facts
about the *environment as a product*, invisible from any SDK, and they are the concrete
content that defeated the "layer 5 is just an axis of layer 2" verdict. Falsifiable and
single-instance by construction: if a **closed** environment read (Modal/Daytona/Cloudflare)
yields only testimony, E4 is real but legible only when the environment is open —
[`notes/05-execution-environments/e2b.md`](notes/05-execution-environments/e2b.md), issue #11.

---

## The composite architecture (what the evidence points at, assembled)

No single tool implements all of this; each clause is held by at least one documented
implementation. If building a harness-plus-method stack today, the derived shape:

1. A small loop with **designed termination** (H6) and a **stuck-state policy** (H2),
   treating **compaction as an outcome** (H1).
2. An **immutable, volatility-ordered prompt prefix** (H5) assembled from **prose
   artifacts under version control** (H4).
3. Tools in a **registry with data descriptions**, **availability-shaped before the
   model sees them, gated after it decides**, invariants underneath (H3), behind a
   **narrow core** (H8).
4. Capability as **on-demand packages indexed cheaply** (X2) on the **files-in-
   directories waist** (X1).
5. Method enforced by **deterministic engines where it must hold** (F1), spending its
   tokens on **measuring the domain** (F2), staged through **fresh contexts with
   compact return paths** (F3), under **explicit attention budgets** (F4).
6. Gates that **fail closed, abstain, and control false positives** (F5).
7. All of it running where **blast radius is chosen, with fidelity engineered back
   in** (E1, E2).

## What the field visibly does *not* agree on

Recorded as open decisions, not principles — with the positions documented:

| Decision | Positions in the set |
|---|---|
| Per-model prompting | five incompatible answers, none eval-backed (H7) |
| Stuck-agent resolution | human-escalate (opencode) vs in-band (hermes) (H2) |
| Memory authorship | autonomous agent-written **shipped on** (hermes) vs **built, stabilized, default-off** (codex, 2026-07-30) vs user-curated files — [issue #2](https://github.com/leandromineti/ai-assisted-coding/issues/2)'s two-verified-instances threshold is now met |
| Session-data posture | harness as training-data instrument (hermes, Cursor) vs stores-nothing (opencode) — taxonomy boundary-rule note |
| Where verification lives | layer 4 gates (GSD), layer 2 native (hermes `verification_stop`; codex stop hooks that can veto turn end), external CI — cross-cutting note, feeds exp-03 |

Verdicts on these belong to future experiments, not to this file.
