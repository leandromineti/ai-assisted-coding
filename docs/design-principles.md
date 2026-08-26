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

## Category 2 — harness design

**H1. Treat running out of context as a normal loop outcome, not an error.**
*(convergent — 3 instances)* opencode models one provider turn as
`"compact" | "stop" | "continue"` — compaction is a peer of finishing
([opencode](../tools/2-harnesses/opencode.md), `processor.ts:30`). hermes wraps
compression in a pluggable `ContextEngine` ABC with a documented lifecycle, and names it
the *only* sanctioned exception to prompt immutability
([hermes-agent](../tools/2-harnesses/hermes-agent.md)). codex compacts mid-turn as a loop
`continue`, compacts *pre-sampling* before turns, and even exposes a
`new_context_window` tool so the model can request rollover itself
([codex](../tools/2-harnesses/codex.md), confirmed 2026-07-30). Designs that treat
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
([`tools/2-harnesses/codex.md`](../tools/2-harnesses/codex.md)). So of the three
deep-dived harnesses, **two detect the loop and one deliberately does not** — this is
`contested`, not `convergent on existence`. The principle survives in weaker form: where
a harness *does* guard, the human-vs-model choice is a real position on autonomy. What
cannot be claimed any more is that guarding is what serious harnesses converge on.
codex's silence is also not obviously carelessness — it is the harness that ends turns on
model-declared completion with no step budget at all, so a repeated-call guard would be
the only bound in a design that otherwise trusts the model to stop. Worth asking the next
deep-dive explicitly, since a third data point either way settles the shape.

*Confronted 2026-08-26 (gemini-cli read 08-25, pi read 08-26) — two data points, still
contested, and the abstain pole gains company.* gemini-cli **guards**: loop detection is
default-on (5 identical calls / 10 repeated content chunks / an LLM loop-check after
turn 30), but its *first* firing is a coaching re-prompt and only the second aborts — a
fourth resolution shape (steer-in-band-then-halt-on-repeat), distinct from opencode's
human-escalation and hermes' synthetic-result path. pi **abstains**: no loop detection
and no turn/step/token budget anywhere (grep over all `packages/*/src` → 0), matching
codex's deliberate silence. So of five deep-dived harnesses the tally is **3 guard / 2
abstain**, and the two abstainers share a rationale — a loop guard would be the only
bound in a design that otherwise trusts the model (codex) or the environment (pi) to
stop. Still contested; what is newly clear is that abstention is a *position*, not an
oversight, held by two independent vendors.

**H3. Two chokepoints, not one: shape what the model can see, then gate what it does.**
*(convergent — the strongest architectural pattern in the set; deepened 2026-07-30)*
opencode filters the tool list before the model sees it (`visibleTools`) and gates
execution at call time (`Permission.ask`). hermes filters the schema by service
availability (`check_fn`, TTL-cached) and gates dangerous commands at dispatch, with
hard write-denials underneath that no approval can override. The emphases differ
(permission-filtering vs availability-filtering) but the two-stage architecture is
identical: **visibility shaping pre-decision, execution gating post-decision,
invariants below both.** codex confirms and extends it to a third, compiled category:
per-step advertised-tool finalization → `SafetyCheck` classification → execution
*inside an in-process OS sandbox* (Seatbelt/Landlock/bwrap), where approval cannot
grant what the sandbox denies ([codex](../tools/2-harnesses/codex.md)). The revised
statement: visibility, decision, **enforcement** — and the strongest designs make the
third category mechanical, not prose.
*Earliest measured evidence found (2026-08-17, [swe-agent-2024](../refs/2024-swe-agent.md)
full read):* the 2024 ACI ablations price both chokepoints separately, holding the
model fixed — visibility shaping (100-line viewer window beats both 30 lines and
full file; last-5 history collapse beats full history, +3.0pp) and mechanical
enforcement (an in-`edit` linter that *discards* invalid edits, +3.0pp) each buy
points, and a badly shaped tool (iterative search) scores *below having no tool at
all* (−6.0 vs −2.3). The pattern this repo found convergent in 2026 harness source
was measured at NeurIPS 2024.
*Confronted 2026-08-26 — gemini-cli confirms the three-category form; pi is the sharp
counter-instance on the second chokepoint.* gemini-cli implements all three cleanly:
visibility shaping (statically-denied tools stripped from the model's schema), decision
gating (a ~12.8k-line tiered TOML policy engine, ASK_USER default), and — a novel third
— an LLM-authored *one-way* policy checker (CONSECA) that can only tighten a decision,
never loosen it ([gemini-cli](../tools/2-harnesses/gemini-cli.md)). pi removes the middle
chokepoint entirely: no permission system, `bash`/`write`/`edit` dispatch unprompted
(README states it; grep `confirm|approve|permission` over core tools → 0), and its
`--tools`/`--exclude-tools` knobs are visibility-only, pre-decision
([pi](../tools/2-harnesses/pi.md)). So "gate what it does" is now a design *position*, not
a universal — two harnesses ship without it (dsh substituting a compiled sandbox, pi
substituting nothing). H3 holds as *what the strongest designs do*; it can no longer be
stated as *what all serious harnesses do*.

**H4. Prompts are versioned data, not string literals.** *(convergent, spans categories 2
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
paid for in machinery and history growth ([codex](../tools/2-harnesses/codex.md)). The
durable core of the principle is *append-only prefix discipline*; freshness-vs-staleness
is an implementation choice on top of it. Also recorded as differentiation axis 6 in
[`tools/2-harnesses/index.md`](../tools/2-harnesses/index.md).
*Confronted 2026-08-26 — both reads CONFIRM append-only prefix discipline, pi most
strongly.* gemini-cli documents a tiered cache layout (volatile memory kept out of the
system-instruction prefix; JIT subdirectory context appended to tool output). pi is the
strongest positive instance in the set — a deliberately clock-free prefix, default-on
`cache_control` at correct breakpoints, `cacheRetention:'none'` on one-off summaries —
and the only tracked harness that **instruments its own cache waste**, showing the user
an inline dollar figure for misses ([pi](../tools/2-harnesses/pi.md)). The invariant is now
convergent across five-plus harnesses; the freshness-vs-staleness implementation axis is
untouched by either read.

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
*Confronted 2026-08-26 — two more positions, both toward convergence.* gemini-cli ships
two full prompt bodies switched on model *family* (gemini-3+/custom vs legacy), not per
slug; pi ships **exactly one** across ~9 provider API families — the strongest
convergence vote yet, a multi-provider client with zero family-conditional prose (a
Claude Code identity block prepends on Anthropic *OAuth*, but that is auth-mode-keyed,
not model-keyed). The documented positions are now seven, and the two newest both sit at
or near the one-prompt pole. Still no eval backing for any position; still a forced
decision — but the centre of gravity has drifted toward "one prompt fits all".

**H8. Keep the core a narrow waist; ship capability at the edges as data.**
*(convergent)* hermes states it outright (every core tool is paid for on every API
call; new capability arrives as skills/plugins) and enforces it with service-gated
schema entries. opencode's `packages/llm` redesign draft draws the same line by
excluding permissions, sessions, and orchestration from the model-calling package.
cline's growth (SDK, CLI, hub around a core) rhymes. The waist is the loop + dispatch;
everything else should be removable.
*(2026-08-18 tension, recorded not resolved: conclusion 8's absorption is core growth —
the counter-motion to this principle. The tracked harnesses split on it: codex absorbs
turn-end gates as a hook SURFACE (waist-shaped — the mechanism is an extension point),
hermes as always-on loop POLICY (core growth). Whether absorbed mechanisms arrive as
surfaces or as core code may be H8's real test — see
[the absorption table](../tools/2-harnesses/index.md#what-category-2-has-absorbed--the-category-4-feature-set-checked-against-harnesses).)*
*Confronted 2026-08-26 (pi) — the strongest instance in the set, and it exposes H8's
uncomfortable corollary.* pi takes the narrow waist furthest of anything read: four
default tools, no budget, no loop detection, a stock loop with **zero active
interception points**, and every other capability — plan mode, subagents, gates, memory
— shipped as removable extensions ([pi](../tools/2-harnesses/pi.md)). But pi also pushes
the *permission gate* out to the edges (there is none in core), which is where "narrow
waist" and E1 collide: a waist this narrow means the loop ships with no safety of its
own and *depends* on category 3 to supply it. So H8 is confirmed as an architecture and
qualified as a safety stance — the removable-everything ideal is only safe when
something below the harness (the environment) is not removable. The
surface-vs-core-growth test (codex hook-surface vs hermes loop-policy) gains pi as the
limit case: it declines to grow the core at all, and exports the risk downward.

## Category 3 — execution-environment design *(renumbered from 5 per ADR-0007)*

**E1. Blast radius sets the autonomy ceiling — buy autonomy with isolation, not model
quality.** *(convergent; taxonomy scope-note position)* Every fully-autonomous product
documented bundles a sandbox, not a smarter model; hermes ships eight terminal-backend
implementations and its serverless pitch is an *economics* answer to keeping an
always-on agent isolated. The same permission flag that is reckless on a host is sane
in a container.
*Confronted 2026-08-26 (pi) — CONFIRMS in its purest form.* pi ships no permission gate
and no sandbox and states in its own README that isolation is the user's responsibility
(external containerization); its autonomy ceiling is *defined* to live in category 3,
gate-factor 1 ([pi](../tools/2-harnesses/pi.md)). The clearest instance yet of "buy
autonomy with isolation, not model quality" — a harness with, quite literally, nothing
but isolation available to buy it with.

**E2. Isolation without fidelity produces category-2-looking failures — engineer the
fidelity back explicitly.** *(convergent)* The worktree/gitignore trap
([`tools/3-execution-environments/`](../tools/3-execution-environments/index.md)):
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
[`tools/3-execution-environments/index.md`](../tools/3-execution-environments/index.md),
rendered in [`comparisons/environments.md`](../comparisons/environments.md).
*Confronted 2026-08-26 (pi) — a second abstention instance, which makes the fifth
position convergent.* After opencode's "none of the four verbs", pi is the second
harness to take the null environment relation deliberately: no sandbox, no worktree
machinery, no container launcher, no environment self-detection — confinement declined
and delegated to docs ([pi](../tools/2-harnesses/pi.md)). E3's "four verbs **plus
abstention**" now reads as the complete option set with two independent votes for the
abstention pole, rather than four verbs and a lone outlier. Note the contrast with
gemini-cli, which ships all four verbs but default-off — "abstention" (pi: nothing built)
and "dormant" (gemini-cli: built, unmounted) are different null states, and only pi's is
a design position on category 3 rather than a default.

*Recorded with the principle, because it is the uncomfortable part:* all four verbs are
properties of **category-2 tools**, discovered inside category-2 reads. The 2026-08-16
adjudication first concluded from this that category 3 fails as a population and proposed
demotion to a category-2 axis — **then the E2B read the same day overturned it** (README
conclusion 9). E2B is a category-3 entity that produces substantive facts *about the
environment*, not about any harness's relationship to it (E4 below is one), so the verbs
being harness-side does not make the category harness-side. E1–E3 stand as category-3 principles.

**E4. An execution environment's economics leak upward into kernel and scheduler choices
that no harness can see.** *(convergent — E2B, cloudflare-sandbox-sdk, Daytona, 2026-08-21;
microsandbox a bounded exception — see the 2026-08-21 confrontation below)* Every
"create" is a snapshot **resume** with no warm pool; the resume working-set is computed by
booting the template twice at build time and intersecting touched pages; guest `kcompactd`
is disabled because host-side hugepage backing would dirty the snapshot diff; `discard` on
the guest ext4 mount is a snapshot-*size* optimization, not a speed one. These are facts
about the *environment as a product*, invisible from any SDK, and they are the concrete
content that defeated the "category 3 is just an axis of category 2" verdict. Falsifiable and
single-instance by construction: if a **closed** environment read (Modal/Daytona/Cloudflare)
yields only testimony, E4 is real but legible only when the environment is open —
[`tools/3-execution-environments/e2b.md`](../tools/3-execution-environments/e2b.md), issue #11.

*Confronted 2026-08-21 (Phase 8 — cloudflare-sandbox-sdk, microsandbox, Daytona reads; full
verdicts in `08-04-SUMMARY.md`):*

**E1.** CONFIRMS, three times over. cloudflare-sandbox-sdk: the security module's own header
states "trust container isolation, only protect SDK control plane" as an explicit design
position — the same ceiling-not-model logic, stated by the vendor rather than inferred.
microsandbox: the logic sharpens with isolation fully decoupled from any service —
hardware-virt with no vendor, no control plane, no daemon; the cost that buys autonomy moves
entirely to the host (a KVM/HVF/WHP-capable machine) and to latency (no warm pool to hide a
cold boot behind). Daytona: a new mechanism — the autonomy ceiling is priced by billing tier,
$500 of lifetime spend converting a restricted network posture into open internet reach with
no code change involved.

**E2.** CONFIRMS, three times over, each the sharpest fit the category has produced so far in
its own report. cloudflare-sandbox-sdk: a FUSE overlay mount in production silently becomes an
`unsquashfs` extraction locally — same API, different persistence semantics, with an in-source
error hint that exists only because the mismatch once looked like nothing at all. microsandbox:
the purest form yet — not a partial absence (the worktree/gitignore trap this principle names)
but a total one; no `current_dir()` on any mount path anywhere in the SDK or CLI, so a bare
`Sandbox::start()` finds an empty machine. Daytona: the same principle running in the opposite
direction — where E2B spends isolation to protect its boundary, Daytona spends its boundary to
buy fidelity (privileged-by-default containers, `/dev/kvm` passthrough for Android emulation,
GPU passthrough), engineering fidelity back in by giving isolation up rather than by
re-injecting what isolation hid.

**E3.** Silent, matching precedent exactly — all three reads confirm what e2b.md and modal.md
already established: the read subject *is* the environment a harness relates to, not a harness
itself, so `environments:`/`environment_relation:` frontmatter stays unset on all five
category-3 reports. No new evidence for or against E3's own claim (the four verbs live in
category-2 tools); category 3's silence on E3 is now five-for-five.

**E4.** CONFIRMS on two of three, upgraded to convergent; genuinely CONTRADICTS as literally
stated on the third, which sharpens rather than breaks the principle. cloudflare-sandbox-sdk
*is* E4's own named falsification test, run for real: the closed isolation substrate yields
testimony only, a bare family with no source-nameable mechanism reachable at any grade —
exactly as the falsifiability clause predicted. Daytona confirms with a second convergent
instance: E2B and Daytona face the identical "make create cheap" pressure and solve it with
opposite mechanisms (snapshot-resume vs. a warm pool that rewrites ownership of an
already-running container) — economics leaking upward twice, independently, in different
products. Daytona also amends the falsifiability clause itself: economics that land in tier,
quota, or lifecycle policy are disclosure-forced and survive closure (the tier-gated egress
policy was already documented in Daytona's own frozen-source docs, months before closure);
economics that land in kernel, scheduler, or tenancy internals are removed completely by
closure (the warm-pool ownership-transfer mechanism has no post-closure analog reachable at
any grade). microsandbox contradicts the principle exactly as worded — there is no vendor at
all in the local-first path, so no vendor economics exist to leak — but the underlying
mechanism generalizes past the word "vendor": host-resource constraints (not billing) drive
the same kind of pressure into a dirty-page writeback credit pool and a CPU placement-lease
arbitration scheme shared fairly across every VM on one host. The refined form: *an execution
environment's resource economics — vendor-priced where a vendor exists, host-priced where none
does — leak upward into kernel, scheduler, and policy choices no harness can see; policy-level
leaks are disclosure-forced and survive closure, internals-level leaks do not.*

---

## Category 4 — workflow-framework design

**F1. The methodology is prose, prose doesn't bind — plan the deterministic escape
hatch from day one.** *(convergent — 3 instances, one an existence proof; strengthened
2026-07-31)* Both frameworks first studied hit enforcement-by-typography limits
(spec-kit fixed hook execution twice by rewriting instructions "more forcefully"; its
constitution went eight months unenforced) and both grew deterministic engines
(spec-kit's `workflows/` YAML runner, GSD's `gsd-pi`). Category-4→2 bleed is the
structural symptom. **OpenSpec is the existence proof for the "from day one" clause:**
its deterministic engine (delta-merge compiler, DAG workflow engine over declarative
schemas, machine validator) is the *founding architecture*, with prose shrunk to thin
CLI adapters (`allowed-tools: Bash(openspec:*)`) —
[openspec](../tools/4-workflow-frameworks/openspec.md). If a gate *must* hold, it
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
*Isolation test complete (2026-08-18, exp-03, two tiers):* the principle survives
**with a tier condition attached**. At Haiku tier the bare instruction to measure was
worth +4/9 trap-discovery checks over plain — the mechanism isolated cleanly, at ~1×
plain cost. At Sonnet tier the plain bundle did the measuring unprompted (8.3/9,
saturation branch) — **the instruction pays only where the model doesn't ground on
its own; what persists across tiers is the affordance** (a measurable domain within
reach), not the prose. Same experiment: gates-only discovered crash-visible traps but
never silent miscounts, and stacking both instructions diluted grounding to checkbox
compliance (README conclusion 12). F2's "spend tokens measuring" survives as a
statement about *affordances and weak tiers*, not as universal framework design
advice.

**F3. Fresh context per stage works as a refinement funnel — but only if the return
path is compact.** *(convergent, with the boundary condition observed in both
directions)* GSD's staged fresh contexts caught each prior stage's vagueness four times
in one run (exp-01). spec-kit forked `/analyze` into a subagent and **reverted** it —
the 300–500-line report re-entered the main context anyway and compounded until
sessions froze (#3185). Isolation pays when stage outputs are contracts (task graphs,
verdicts), not transcripts.

**F4. Budget human attention as an explicit, designed quantity.** *(convergent across
categories)* spec-kit caps clarification markers at 3, clarify questions at 5, asks one at
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
cannot verify upstream security and forked for that reason. Category-4 supply chain is
real: you are `curl | sh`-ing *instructions* that will run with everything your agent
can touch.

## The extensions bucket (6) — extension design *(three principles; bucket status per ADR-0002, renumbered per ADR-0007 and again per ADR-0020)*

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

**X3. The absorption bet: harnesses absorb mechanisms, bundle content, never absorb
reach.** *(registered bet, 2026-08-22 — falsifiable predictions, not yet a principle;
re-check rides the ~2027-01 standards re-check; registered per
[ADR-0019](../adrs/0019-category-5-coverage-strata.md) from the
[bucket boundary discussion](../tools/5-memory/index.md))* Harnesses absorb
*mechanisms* (gates, memory — both now verified native in multiple harnesses), *bundle*
content (Warp ships 13 skills; the loader was always category 2), and never absorb
reach. Independent mechanism extensions survive absorption on the one bet a single
harness cannot absorb — cross-harness continuity (conclusion 8's counter-current).
Predictions that would falsify the frame: a harness absorbing a slot-filler *as a
mechanism*; a mechanism-adder thriving long-term on a single-harness bet; a reach-side
artifact being absorbed rather than bundled.

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
| Memory authorship | autonomous agent-written **shipped on** (hermes) vs **built, stabilized, default-off** (codex, 2026-07-30) vs user-curated files vs — fourth position, **source-verified 2026-08-18** (memory-type arc) — **agent-written but independently stored**. The arc's finding: independent storage doesn't pick one authorship, it *stacks* them — ai-memory's wiki is simultaneously rule-written (session pages), agent-written with auto-approval (`_rules/` via its scheduler, `require_approval=false` default), and user-edited (Obsidian/vim watcher reconciles); memos' policy DB is fully machine-authored with feedback-gated lifecycles *(confirmed in source at the 2026-08-19 deep-dive — and default-unmounted: lightweight mode ships the whole authoring cascade off)*; cognee splits the decision *across repos* (agent-invoked writes in the MCP server, automation added by the plugin). The open question sharpened: not who writes memory, but who approves it — and as of 2026-08-19 that axis is a matrix column: `memory_revision` (auto: ai-memory, memos · caller-only: mem0, whose deep-dive found no auto-supersession path at all — the linking mechanism is dead code). [Bucket index](../tools/5-memory/index.md) |
| Session-data posture | harness as training-data instrument (hermes, Cursor) vs stores-nothing (opencode) — taxonomy boundary-rule note |
| Where verification lives | category 4 gates (GSD), category 2 native (hermes `verification_stop`; codex stop hooks that can veto turn end), external CI — cross-cutting note. exp-03 (2026-08-18) measured the category-4 pole: an instructed gate catches crash-visible failures only, and at Sonnet tier the bundle grounds/verifies unprompted — the live question is now category-2-native vs external CI (issue #17) |

Verdicts on these belong to future experiments, not to this file.
