# AI-assisted coding

A personal sandbox for understanding the AI-assisted-coding tooling landscape — from
first-hand trial rather than from marketing pages.

This is a learning repo. The deliverable is notes and conclusions, not a product.

## Start here

**[`taxonomy.md`](taxonomy.md)** — the shared vocabulary. A **core triad** — models,
harnesses, execution environments (categories 1–3), the three things a running agent cannot
lack — plus two **interfaces**: workflow frameworks (4 — the human⇄stack boundary:
intent refined into specs and subtasks going down, research and verified evidence coming
up), memory (5 — persistent cross-session state on the agent↔time edge, a full
category since the 2026-08-22 split), and extensions (6 — a cross-category bucket
parameterizing the triad's remaining edges; portability is conferred by adoption, not
intrinsic, so the name doesn't claim it). How the taxonomy reached this shape —
demotions, adjudications, the 2026-08-18 renumbering, the 2026-08-22 split — is one
dated decision record each in [`adrs/`](adrs/README.md).
With a boundary rule, a bleed/vendor-span distinction, and a stress test for the many
tools that straddle the divisions. Everything else in the repo declares where it belongs.

**[`methodology.md`](methodology.md)** — how work is done here: verification and honesty
rules, generated indexes, preregistered experiments, the upstream-reporting gate. Every
rule earned its place by catching a real mistake; the anti-goal section keeps it from
growing rigor for rigor's sake.

**[`design-principles.md`](design-principles.md)** — the synthesis layer: design
principles derived from the documented tools, per taxonomy category, each carrying a
confidence marker (convergent / single-instance / contested) and its evidence citations.
Hypotheses under revision, not best practices — every new deep-dive or experiment must
confirm, contradict, or note silence.

| Category | Index | Examples |
|-------|-------|----------|
| 1 · Models | [`notes/01-models/`](notes/01-models/index.md) | Opus 5, Fable 5, Grok 4.5, Kimi K3 |
| 2 · Harnesses | [`notes/02-harnesses/`](notes/02-harnesses/index.md) | Claude Code, OpenCode, Codex CLI, Cursor |
| 3 · Execution environments | [`notes/03-execution-environments/`](notes/03-execution-environments/index.md) | worktrees, devcontainers, E2B |
| 4 · Workflow frameworks | [`notes/04-workflow-frameworks/`](notes/04-workflow-frameworks/index.md) | GSD, spec-kit |
| 5 · Memory | [`notes/05-memory/`](notes/05-memory/index.md) | ai-memory, mem0, MemOS, cognee |
| 6 · Extensions (bucket) | [`notes/06-extensions/`](notes/06-extensions/index.md) | MCP servers, skills, hooks, rules files, config packs (ECC) |
| ✕ Cross-cutting | [`notes/cross-cutting/`](notes/cross-cutting/index.md) | context engineering, verification, cost, standards (MCP, `AGENTS.md`) |

## Layout

| Path | Holds |
|------|-------|
| `CLAUDE.md` | How the repo works: where things go, the ingest/lint operations, the honesty columns |
| `taxonomy.md` | The category definitions and boundary rule — the canonical reference |
| `methodology.md` | The working rules — verification, honesty markers, experiment protocol |
| `design-principles.md` | Design principles derived from the reports, per category, confidence-marked |
| `notes/` | One index per category, plus one file per tool, written while using it |
| `refs/` | One note per **source read** — papers and benchmarks — each carrying its own `read_depth`. See [`refs/README.md`](refs/README.md) |
| `upstream/` | Cloned open-source sources to read — **gitignored**, see [`upstream/README.md`](upstream/README.md) |
| `experiments/` | Small self-contained trials — ideally the *same* task, different tools |
| `comparisons/` | Side-by-side matrices distilled from the notes and experiments |
| `scripts/` | `sync-upstream.sh` (clone/update), `repo-facts.sh` (verified frontmatter facts), `build-tool-index.py` and `build-refs-index.py` (regenerate the indexes) |
| `articles/` | Public-facing writing drawn from the findings — drafted next to the evidence, every claim linked and dated. See [`articles/README.md`](articles/README.md) |

**[`comparisons/tools.md`](comparisons/tools.md)** is the flat cross-category index of every
tool with a report, **[`comparisons/features.md`](comparisons/features.md)** the
harness feature matrix, and **[`comparisons/models.md`](comparisons/models.md)** the
category-1 matrix (thinking control, caching economics, batch pricing — the API surface
that drifts fastest) — all generated from the reports' frontmatter, never hand-edited,
so they can't drift from them. In the matrices, `·` means *not yet checked*, which is
deliberately distinct from ✗ *verified absent*.

Tools queued for assessment but not yet cloned live as **GitHub issues on this repo**
([issue #1](https://github.com/leandromineti/ai-assisted-coding/issues/1) is the
pattern) — candidates already weighed and passed over are recorded in the relevant
category index's "considered, not added" table instead.

One report per tool, following
[`notes/_template-tool-report.md`](notes/_template-tool-report.md). Its **"distinguishing
bet"** field is the one that matters — what does this tool believe that its competitors
don't? — and **`depth`** is the honesty marker: `stub` (facts collected, source unread),
`survey` (used or skimmed), `deep-dive` (the category's components traced — defined in
[`taxonomy.md`](taxonomy.md) — the report saying which; pre-2026-08-25 deep-dives read
under the earlier loop+context definition).

The point of reusing one task across `experiments/` is to make comparisons honest instead
of impressionistic — though see the open question in
[`notes/cross-cutting/`](notes/cross-cutting/index.md) about whether a clean A/B is
possible here at all.

## Conventions

- Every claim about a tool carries a `checked: YYYY-MM-DD` date. This field moves fast and
  notes go stale quietly.
- Anything not confirmed against a primary source is marked `unverified` rather than
  asserted.
- A tool that hasn't actually been used gets an **empty** "my take" section. The blankness
  is the honest state.

## Conclusions

_The running answer to "what did I actually learn?" — each dated, each traceable to a
note. Revised when evidence moves._

1. **"The models have converged" is contested by the people best placed to know**
   (2026-07-28). The three portable harnesses answer the per-model-prompt question three
   different ways: opencode maintains nine bespoke prompts sharing zero substantive lines;
   cline built that architecture and *dismantled* it; continue runs ~15 lines and bets the
   prompt barely matters. Nobody's position is backed by a published eval. →
   [`notes/02-harnesses/index.md`](notes/02-harnesses/index.md)
2. **No public benchmark isolates model from harness** (2026-07-28). Leaderboards pair
   them ("Codex CLI + GPT-5.5"), and the one benchmark that fixes the harness turned out
   to inherit that harness's per-model prompt dispatch — a confound its maintainer didn't
   know about. Reporting it produced this repo's first upstream contribution
   ([issue #12](https://github.com/akitaonrails/llm-coding-benchmark/issues/12),
   [PR #13](https://github.com/akitaonrails/llm-coding-benchmark/pull/13)).
   **Complemented (2026-08-17):** the repo now holds its own model-isolated
   measurement — the rig fixed harness/task/environment and varied only the model
   (Sonnet 5 vs Haiku 4.5, n=5 each; see conclusion 10). The public-benchmark claim
   stands unchanged; what changed is that the isolation the field lacks is
   demonstrably buildable at personal scale for ~$3. →
   [`notes/01-models/index.md`](notes/01-models/index.md)
3. **The extensions bucket (category 6; numbered 5 until the 2026-08-22 split) is "MCP plus vendor features," so far** (2026-07-28). Of five capability-
   extension types, only MCP has fully standardized; rules files are converging on a
   filename convention; hooks and subagent definitions remain harness-specific.
   *Revised same day:* skills moved — spec-kit's integration registry shows `SKILL.md`
   consumed by at least four harnesses (Claude Code, Codex, Kimi, Hermes), so skills are
   now convention-level like rules files, no longer Claude-Code-shaped.
   Re-check the scoreboard ~2027-01. →
   [`notes/cross-cutting/standards.md`](notes/cross-cutting/standards.md)
   **Strengthened, headline unchanged (2026-08-11, Warp survey).** Both converging types
   gained their best evidence yet, and it is a better *class* of evidence: a first-party
   implementation by a rival vendor rather than a third-party installer targeting the
   format. Warp parses `SKILL.md` natively (`crates/ai/src/skills/`, 13 bundled skills) —
   a fifth consumer — and its project-init flow offers to link seven *competitors'* rules
   files (`CLAUDE.md`, `.cursorrules`, `GEMINI.md`, `.clinerules`, `.windsurfrules`,
   Copilot instructions, `AGENT.md`) into its own. The headline still stands: both remain
   filename-plus-frontmatter conventions with no schema, and hooks and subagent
   definitions did not move. → [`notes/02-harnesses/warp.md`](notes/02-harnesses/warp.md)
4. **Structural completeness does not predict runtime correctness** (2026-07-28, from
   llm-coding-benchmark's data): models produce complete-looking apps whose tests mock
   hallucinated APIs — green suites over dead code. Any personal eval must boot the
   artifact, not count its files. →
   [`notes/cross-cutting/index.md`](notes/cross-cutting/index.md)
5. **Reading source beats reading marketing, quickly** (2026-07-28). Every finding above
   except #4 came from a few hours of grepping cloned repos — none appears in any tool's
   own documentation. The `upstream/` workflow pays for itself.
6. **A workflow framework's value concentrates in empirical grounding, not process
   ceremony** (2026-07-28, n=1). In a preregistered A/B on a below-threshold task, GSD
   tied a plain agent on every preregistered functional check at ~30–50× the cost — but
   won decisively on a real crash class its research had predicted, gated, and verified.
   Nearly all of that margin traced to agents that *measured* the domain (fixture repos,
   crafted commits, timezone probes) and to measured verification gates; almost none to
   the surrounding ceremony. Open follow-up: which 20% of the ceremony buys 80% of the
   margin? → [`experiments/01-gsd-vs-plain/`](experiments/01-gsd-vs-plain/README.md)
   **Status 2026-07-31 — under re-examination, issue #8.** A published n=128 ablation
   separates the two ingredients this conclusion credits jointly and finds post-phase
   *validation* worth ~3× pre-phase *grounding* ([`refs/2026-spec-kit-agents.md`](refs/2026-spec-kit-agents.md)).
   Its headline is an LLM-judge score its own blinded human sample mildly contradicts, and it
   ran a different base model, so this is a competing decomposition rather than a refutation —
   but our n=1 does not support asserting the split either way.
   **Resolved 2026-08-18 — issue #8's option 3 executed (exp-03, conclusion 12).** On this
   repo's fails-closed binary instrument the split ran the *other* way: grounding-only beat
   gates-only (8/9 vs 5.7/9 trap discovery at Haiku tier), gates discovered only crash-visible
   failures, and the combination interfered. The divergence from the published LLM-judge result
   is recorded with both candidate attributions (instrument, base model). Conclusion 6's
   emphasis stands as written — with exp-03's tier caveat: at Sonnet tier the plain bundle
   grounds unprompted, so the split matters most where models are weak.
7. **A category-4 framework's portability and its enforcement power are the same tradeoff**
   (2026-07-28, spec-kit source read). Cross-harness portability is cheap because every
   harness converged on "slash command = prompt file" — but that lowest common
   denominator means the framework's runtime *is* the model reading prose. spec-kit's git
   history shows the consequence: hook execution was fixed twice by rewriting
   instructions more forcefully (#2901, #2713 — enforcement by typography), the
   constitution went eight months unenforced during implementation (#2460), and the one
   attempt at real context isolation was reverted after compounding-context freezes
   (#3185). Both frameworks studied grew deterministic engines (spec-kit's `workflows/`
   YAML runner, GSD's `gsd-pi`) as the escape hatch — category-2 bleed as a structural
   symptom, not a coincidence. →
   [`notes/04-workflow-frameworks/spec-kit.md`](notes/04-workflow-frameworks/spec-kit.md)
   **Independently corroborated (2026-07-31):** a six-framework taxonomy study covering the
   same subjects reaches the same tradeoff — "no framework strongly covers all six dimensions
   … a structural trade-off between process depth and portability" — from documentation
   alone, where ours came from reading git history
   ([`refs/2026-from-prompt-to-process.md`](refs/2026-from-prompt-to-process.md)). Two methods, one
   shape. Its GSD scores are also where our *run* evidence contradicts a docs-only reading.
   **Deepened by the 2026-08-18 deep-dives** (spec-kit + gsd-core, both traced in source):
   the "escape hatch" framing was too coarse — the two frameworks diverged. spec-kit
   *built* the engine (11 step types, a 14.5k-line test suite) and left it disconnected
   from its methodology: it dispatches the prose by name, never reads it, and ships one
   78-line workflow. GSD is *migrating enforcement out of prose* — three hard-blocking
   harness hooks, a validator that structurally forbids LLM-verdict gates from blocking
   ("non-deterministic checks may not halt the loop"), its own hook headers stating the
   thesis: "a prose backstop cannot fix a prose defect." The tradeoff also acquired a
   measured price: the portability ceiling is 3 lines of body diff between spec-kit's
   richest and thinnest compiled targets, and the *thinnest* harness's 32,768-byte
   instruction cap is reshaping GSD's core architecture (the fragment model) — the
   constraint propagates upward into framework design, not just downward into weak
   enforcement. Gate-enforcement grading formalized in the feature taxonomy
   ([ADR-0011](adrs/0011-graded-gate-enforcement.md)): no framework yet has an
   engine-graded measured or process gate. →
   [`notes/04-workflow-frameworks/gsd-core.md`](notes/04-workflow-frameworks/gsd-core.md)
   **Third shape added (2026-08-18, BMAD deep-dive):** an engine divergence datapoint that
   *inverts* GSD's thesis — BMAD ships ~2.6k lines of tested Python state tooling and
   deliberately denies it authority (every script failure licenses the LLM to "deliver
   the same outcome by best judgment"; both dedicated validators exit 0 by design; zero
   hooks — the ecosystem's hooks live in the external `bmad-loop` module). And the
   portability side of the tradeoff has a shape the "measured price" framing didn't
   predict: BMAD does **no translation at all** — one byte-identical Agent Skills
   artifact copied to 47 platform codes (22 distinct dirs; 26 share the
   `.agents/skills/` convention), so there is no degradation gradient to measure; the
   price surfaces instead as a hand-forked, runtime-stripped 6-of-29-skill
   `web-bundles/` for chat platforms, quarantined outside the mechanism. The
   same-day [bmad-loop stub](notes/04-workflow-frameworks/bmad-loop.md) completes the
   shape: the ecosystem's companion orchestrator holds the tracked category's first
   **engine-graded measured and process gates** ("No LLM in the control loop") — so
   "no framework yet has an engine-graded measured or process gate" stays true
   precisely because BMAD ships those gates outside the framework, in the escape
   hatch productized. →
   [`notes/04-workflow-frameworks/bmad-method.md`](notes/04-workflow-frameworks/bmad-method.md)
   **Reinforced (2026-08-21, gsd-core v1.11.0 release re-read):** the migration
   direction held under a 369-commit window — every enforcement movement went
   prose→code (disk-strict completion predicate, vendored RE2 for untrusted plan
   regexes, an opt-in git-hook guard below the agent altogether), none the other way, and
   the window's recurring defect class was *believed-live prose found inert* (four
   independent cases, incl. a 40KB workflow loaded by nothing) — the strongest
   evidence yet on the reliability floor of prose-graded gates. One count corrected:
   "three hard-blocking hooks" was a curated subset — a lexical exit-2 grep matches 8
   hook files at both pins. →
   [release assessment](notes/04-workflow-frameworks/gsd-core.md#release-assessment--v1110-2026-08-21-pin-fee72d55--182f60b4)
8. **Harnesses are absorbing the stack from the middle** (2026-07-30, from the hermes +
   codex deep-dives). The mechanisms adjacent categories sell are turning up *natively in
   category 2*, twice each: turn-end verification gates (hermes' `verification_stop`,
   codex's stop hooks that veto termination — the mechanism conclusion 6 credits with
   category 4's quality margin), autonomous memory loops (hermes on-by-default, codex
   stable-but-off — now the `learning loop` matrix column), programmatic tool calling
   (hermes' `execute_code`, codex's sandboxed-V8 code-mode), and plan modes everywhere.
   Consequence for the experiment arc: a category-4 framework's measured margin must be
   re-baselined against what the harness already does — recorded as a design rider on
   exp-03 in [`notes/cross-cutting/`](notes/cross-cutting/index.md). →
   [`notes/02-harnesses/hermes-agent.md`](notes/02-harnesses/hermes-agent.md),
   [`notes/02-harnesses/codex.md`](notes/02-harnesses/codex.md)
   **Third instance, and a counter-instance (2026-08-11, Warp survey; evidence upgraded
   to deep-dive 2026-08-19 — the loop is now traced).** Extended: Warp absorbs
   category-4-shaped *orchestration* — multi-agent fan-out where the harness running each
   child is a selectable field (`enum Harness { Oz, Claude, OpenCode, Gemini, Codex }`),
   with drivers and transcript parsers for its competitors. Absorption is not only
   downward and upward but *sideways*: a harness that treats rival harnesses as
   interchangeable backends. Contradicted on one leg: the **autonomous memory loop is
   absent**. Warp ships the whole store — versions, per-agent scoping, a CLI — and
   `MemorySource` has exactly one variant, `Manual`. So of three harnesses examined for
   it, one is on by default, one stable-but-off, one user-write-only. "Twice each" was
   never "always," and the `learning loop` column now has a verified ✗ to sit beside its
   ✓s. *(2026-08-19 sharpening from the deep-dive: the ✗ stands, with a fourth mechanism
   shape behind it — the agent proposes rules, the human commits them, and a deprecated
   `is_autogenerated` field shows an auto-write path was built and then removed. The
   sideways absorption also has a cost the survey couldn't see: children launch with
   their own permission gates disabled — absorption of orchestration without absorption
   of governance.)* → [`notes/02-harnesses/warp.md`](notes/02-harnesses/warp.md)
   **Counter-current (2026-08-18, memory-type reading arc).** Absorption predicts
   independent memory extensions get eaten by native loops; the arc found the opposite
   motion running concurrently. The extensions are growing *despite* native memory
   (ai-memory: 2.6k stars in 3 months sitting outside every harness), their verified
   bet is the one thing a single harness cannot absorb — cross-harness continuity —
   and they *colonize* harnesses that already absorbed the feature: memos installs
   into hermes as a `MemoryProvider`, alongside hermes' own on-by-default loop.
   Absorption and colonization are simultaneous, not sequential. **Escalated to
   displacement (2026-08-18, mem0 survey):** mem0's harness plugin ships a PreToolUse
   gate that *blocks* Claude Code's own native memory writes (MEMORY.md, exit 2) and
   redirects the model to mem0's MCP tool — the extension actively suppressing the
   absorbed feature to replace it, plus a competitor-store import script
   (cursorrules/copilot/cline/continue → mem0). Caveat from the same
   arc: the continuity mechanism is real but its automatic floor is thin (ai-memory's
   baton is first + last prompt + tool names, no LLM) — whether the bet survives
   contact with use is an open rig question. →
   [`notes/05-memory/ai-memory.md`](notes/05-memory/ai-memory.md),
   [`notes/05-memory/memos.md`](notes/05-memory/memos.md)
9. **The environments category (3) is a real category, not an axis of the harness category —
   decided by its own falsifier** (2026-08-16, decision record
   [ADR-0003](adrs/0003-environments-stay-a-rung.md)). The taxonomy pre-committed to
   demoting execution-environments unless study showed an environment fact that isn't
   just a restatement of how a harness attaches to one. For three weeks every
   environment finding *was* a harness property (the four relationship verbs —
   bundle/bind/internalize/inhabit — all live in category-2 frontmatter),
   and a gated demotion to "an axis of category 2" was written and scheduled. The first
   environment studied as a product in its own right — **E2B**, read from its open-source
   infra — fired the keep-it-a-category arm the same day: ~26 environment-facts to 6
   attachment-restatements, **every one of the 26 invisible from the SDK** (Firecracker with
   no jailer running as root; every "create" secretly a snapshot resume with no warm pool;
   the credential-injection proxy absent from the open-source build; guest `kcompactd`
   disabled for host snapshot-diff economics). One genuine population member falsifies "fails
   as a population." *Caveat refined 2026-08-21, after three more category-3 reads
   (cloudflare-sandbox-sdk, microsandbox, Daytona):* partly confirmed, partly sharpened, not
   fully closed. cloudflare-sandbox-sdk's closed isolation substrate reproduced the fear
   exactly — testimony only, no source-nameable mechanism reachable at any grade. Daytona
   (closed, but disclosure-richer than Cloudflare) split the caveat by kind: economics that
   land in tier, quota, or lifecycle policy survive closure fully documented; economics that
   land in kernel, scheduler, or tenancy internals do not survive at all. microsandbox,
   genuinely open but with no vendor in its local-first path, showed the underlying mechanism
   generalizes past vendor billing to host-resource scarcity. None of the three is the
   maximally closed case
   [issue #11](https://github.com/leandromineti/ai-assisted-coding/issues/11) actually asked
   about — a thin, uncommented client with no trust center and no advisories at all — so that
   test remains open after five reads.
   → [`notes/03-execution-environments/e2b.md`](notes/03-execution-environments/e2b.md),
   [`notes/03-execution-environments/cloudflare-sandbox-sdk.md`](notes/03-execution-environments/cloudflare-sandbox-sdk.md),
   [`notes/03-execution-environments/microsandbox.md`](notes/03-execution-environments/microsandbox.md),
   [`notes/03-execution-environments/daytona.md`](notes/03-execution-environments/daytona.md),
   [`notes/03-execution-environments/index.md`](notes/03-execution-environments/index.md)
10. **A task-level trap instrument that cannot rank same-tier runs still separates model
    tiers — and its items are not monotone in capability** (2026-08-17, measured). exp-02's
    21-check instrument, saturated against Sonnet 5 baselines (mean 19.0/21, n=5), fully
    separates Haiku 4.5 (every completed run 17/21, n=4, plus one run dead-on-arrival from
    an undeclared runtime dependency) — known-groups validity, preregistered with the
    verdict rule fixed before the runs. The reversal inside the result is the deeper
    finding: Haiku *beat* Sonnet on the truncated-archive trap (0/4 vs 3/5 failures)
    because its blanket `rc=1` error handling never lets a traceback escape, while failing
    everything that requires *distinguishing* failures; whole-family failure patterns
    (Haiku: the entire ambient-config family, every completed run), not single items,
    carried the separation. Preregistered prediction on per-item dominance was half-wrong
    and is recorded as such. →
    [`notes/cross-cutting/benchmark-survey.md`](notes/cross-cutting/benchmark-survey.md),
    [`experiments/02-spec-kit-vs-plain/log.md`](experiments/02-spec-kit-vs-plain/log.md)
11. **Intent capture steers trap behavior but does not add trap discovery** (2026-08-17,
    measured — exp-02's preregistered A/B, both predictions supported). On the same
    21-check instrument, one condition, one model: spec-kit's arm and the plain arm
    scored **identically** (19/21, the same two failures, both at the n=5 baseline
    mean), while spec-kit's *written requirements* won every rubric item (21 numbered
    criteria vs ~10 prose claims; 4/5 trap families anticipated in writing vs 2/5) at
    7.8× the cost. The mechanism is the finding: clarify surfaced exactly the right
    exit-code question and **recommended the trap-failing answer**, which its tests
    then enforced faithfully — and pinned UTC output in the passing direction before
    any code existed. A framework that never measures the domain converts ambiguity
    into *documented decisions*, not into *correct* ones; which direction it steers is
    up to the model's priors, not the process. Conclusion 6's decomposition survives
    its second framework: the quality margin lives in grounding + gates, not
    ceremony — and exp-03 now proceeds against a confirmed baseline. →
    [`experiments/02-spec-kit-vs-plain/`](experiments/02-spec-kit-vs-plain/README.md)
12. **A model tier absorbed a workflow mechanism whole — and the category-4 A/B arc closes
    on it** (2026-08-18, exp-03, preregistered two-tier ablation, saturation branch
    pre-declared). On a buried-trap corpus, a one-file "measure the domain first"
    instruction lifted Haiku's trap discovery from 4.0/9 (plain band, n=5) to 8/9 —
    while a gates-only file found just the crash-visible traps (never the silent
    miscounts, 0/3), and the two files *combined* interfered: grounding went
    checkbox-shallow in 3 of 3 runs. On our fails-closed binary instrument the
    decomposition is **grounding > gates > both** — the opposite direction from the
    published LLM-judge ablation ([`refs/2026-spec-kit-agents.md`](refs/2026-spec-kit-agents.md)),
    recorded with both candidate attributions (instrument, model). Then tier 2: **plain
    Sonnet discovered 8.3/9 unprompted** — one model tier absorbed the instruction's
    entire measured value (P5's shrink-with-capability prediction, in the limit).
    Consequence, decided with the owner: category-4 code-outcome A/Bs stop; the
    measurable subjects are the model+harness **bundle** (whose 7–14/23 run-to-run
    band is wider than most framework effects) and **artifact-level** framework value
    (conclusion 11). Caveats stated in the report: the Haiku grounding arm is n=1;
    one check (t3c) went 0/20 with satisfiability unproven. →
    [`experiments/03-minimal-harness/`](experiments/03-minimal-harness/README.md) ·
    [`notes/cross-cutting/category-2-program.md`](notes/cross-cutting/category-2-program.md)
13. **The memory extensions sell to coding agents but benchmark on chat** (2026-08-18,
    memory-type reading arc: one deep-dive, two surveys, three instrument full-reads).
    The type's verified substance is real — three distinct wagers (markdown wiki / RL
    policy database / knowledge graph), three consolidation postures (background cron /
    per-turn event cascade / agent-invoked), and cross-harness continuity as the one
    bet no single harness can absorb (conclusion 8's counter-current). *(Structured
    2026-08-19: the comparison is now an 11-key `memory_features` registry block and
    generated matrix — [ADR-0013](adrs/0013-memory-features-block.md); first cut shows
    the engineering axes converged, the identity axes split four ways, and the headline
    continuity bet resting on one verified instance.)* **Deepened (2026-08-19, mem0
    deep-dive — the type's second):** the "converged engineering axes" partly dissolved
    on source contact — two of mem0's four ✓s flipped (tiers: a metadata tag; decay:
    OSS params that raise, platform-only), sharpening the conclusion's own point: the
    coding-agent product is where the claims live, and reading client parameters as
    capabilities inflates the open tier. New instance of the pattern: the OSS SDK
    contains a 1,582-line remotely-scripted A/B upsell funnel (`notices.py`) — the
    benchmark-vs-product gap is not just marketing outside the repo, it is
    instrumentation inside it. →
    [`notes/05-memory/mem0.md`](notes/05-memory/mem0.md)
    **Third instance, inverted (2026-08-19, memos deep-dive):** the benchmark-vs-product
    gap runs the other way — memos' machinery is real and golden-tested in source, but
    the ten README numbers (five of them CODING benchmarks incl. SWE-Bench, all
    attributed to a non-vendored external repo) describe the full-evolution
    configuration, while the shipped default — verified in code, templates, and the
    published npm artifact — runs with that machinery unmounted. The type's pattern is
    now symmetric: mem0 benchmarks what the OSS artifact doesn't contain; memos
    benchmarks what the shipped default doesn't enable. →
    [`notes/05-memory/memos.md`](notes/05-memory/memos.md)
14. **Cross-harness memory continuity is real and entirely pull-shaped** (2026-08-19,
    exp-04, n=1 per arm — a probe). The memory type's headline bet, measured for the
    only tool that ships a continuity mechanism (ai-memory, pin-built): the automatic
    floor is **0/10** — the session-start baton carries the latest session's first/last
    prompts, and mid-session conversational facts never reach it (out-of-box AND with
    injection explicitly enabled) — while agent-initiated pull recovers **10/10
    verbatim across the harness boundary** (Claude Code capture → opencode recall),
    and same-harness scores identically: the harness boundary costs nothing on the
    pull path. Continuity rests entirely on the receiving agent knowing to ask.
    Incidental: the run was blocked by a live MCP-schema-vs-Anthropic-API interop seam
    whose fix ships default-off — presence≠operative, measured blocking a real run.
    **Arm C (same day): the floor is a design property, not a zero-LLM artifact** — with
    the LLM consolidation loop enabled and manually triggered, the reviewer surfaced the
    facts as candidates and rejected every one on an articulated evidence bar
    ("acknowledged but not made or refined in session; no implementation evidence") —
    the memory system refuses to mint knowledge from conversational say-so, which is
    exactly this repo's own rule 4 applied by a tool to its user. →
    [`experiments/04-memory-continuity/`](experiments/04-memory-continuity/README.md) But every
    instrument the vendors self-report on — LoCoMo, LongMemEval, BEAM — measures
    personal chat-assistant memory: no tool traces, no repo state, no code entities.
    **No coding-agent memory benchmark exists**, and the two vendor headline numbers
    checked exceed their instruments' own published scales (mem0's 92.5 vs LoCoMo's
    87.9 *human* baseline; cognee's 0.79 vs BEAM's ~0.36 best configs) — so the
    type's efficacy for coding is currently an unmeasured claim resting on
    conversational proxies. *Deepened same day by the mem0 vendor paper
    ([`refs/2025-mem0.md`](refs/2025-mem0.md), full read): mem0's own published
    comparison shows the no-memory full-context baseline beating its memory system
    on quality (J 72.90 vs 68.44) — the measured claim is latency/token efficiency —
    and the 92.5 belongs to a later rewrite whose architecture the paper doesn't
    describe.* →
    [`notes/cross-cutting/benchmark-survey.md`](notes/cross-cutting/benchmark-survey.md) §6 ·
    [`notes/05-memory/index.md`](notes/05-memory/index.md)

## License

[MIT](LICENSE). Cloned upstream sources (`upstream/`, gitignored) and cached papers
(`refs/pdf/`, gitignored) belong to their respective owners.
