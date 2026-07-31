# Derived design principles

`derived: 2026-07-30` · status: **hypotheses under revision, not verified best practices**

What the documented tools converged on — and what they still dispute — read as design
guidance. Every principle below is *derived from the evidence in this repo's reports*,
cited and dated; none is imported from blog-post folklore.

**Evidence base at derivation time:** two deep-dives (opencode, hermes-agent), three
surveys (cline, continue, spec-kit), one framework run end-to-end (gsd-core,
experiment 01), one preregistered experiment with results. Known biases: n is small;
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
decision.** *(convergent on existence, contested on resolution; one silence)* Both
2026-07-28 deep-dived harnesses detect repeated-identical-call loops. opencode escalates
to the *human* through the permission subsystem (doom-loop as a permission prompt);
hermes resolves *in-band* with the model (warning guidance → synthetic tool results →
bounded halt). The principle is that silence is not a policy; the human-vs-model choice
is a position on autonomy. *Revision-rule note (2026-07-30):* the codex read found no
repeated-call guard in the turn path — recorded in its report as unverified absence,
not a counter-instance; settle it before counting codex either way.

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

## Layer 3 — extension design *(thin evidence — two principles only, held loosely)*

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
hatch from day one.** *(convergent; README conclusion 7)* Both frameworks studied hit
enforcement-by-typography limits (spec-kit fixed hook execution twice by rewriting
instructions "more forcefully"; its constitution went eight months unenforced) and both
grew deterministic engines (spec-kit's `workflows/` YAML runner, GSD's `gsd-pi`).
Layer-4→2 bleed is the structural symptom. If a gate *must* hold, it eventually needs
code, not capitalization.

**F2. Spend tokens measuring the domain, not on ceremony.** *(n=1, preregistered;
under active test)* Exp-01's entire observed quality margin traced to agents that
*measured* git (fixture repos, crafted commits, timezone probes) and to verification
gates with measured expected values — almost none to the surrounding process ceremony,
at ~30–50× cost (README conclusion 6). Exp-02 tests the complementary claim
(intent capture without measurement); exp-03 is designed to isolate this principle
directly. This is the repo's most consequential hypothesis, which is exactly why it's
being tested rather than trusted.

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
instrument for pricing this is exp-02's attention-split measurement.

**F5. Verification gates must fail closed, abstain when subjective, and control their
false-positive rate.** *(convergent, three complementary lessons)* Fail-closed: the
rig's rule — a verifier that passes an empty environment is a scorer bug — earned its
keep catching vacuous T4/T5 passes before any run. Abstention: GSD's verifiers return
`human_needed` on subjective checks instead of auto-passing. False-positive control:
hermes' verification-stop ships a suppression list because a gate that nags on README
edits trains users to bypass it. A gate missing any of the three degrades into either
theater or noise.

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
