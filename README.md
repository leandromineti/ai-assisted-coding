# ai-assisted-coding

A personal sandbox for understanding the AI-assisted-coding tooling landscape — from
first-hand trial rather than from marketing pages.

This is a learning repo. The deliverable is notes and conclusions, not a product.

## Start here

**[`taxonomy.md`](taxonomy.md)** — the shared vocabulary. A **core triad** — models,
harnesses, execution environments (layers 1–3), the three things a running agent cannot
lack — plus two **interfaces**: workflow frameworks (4 — the human⇄stack boundary:
intent refined into specs and subtasks going down, research and verified evidence coming
up) and extensions (5 — a cross-layer bucket parameterizing the triad's edges;
portability is conferred by adoption, not intrinsic, so the name doesn't claim it). How
the taxonomy reached this shape — demotions, adjudications, the 2026-08-19
renumbering — is one dated decision record each in [`adrs/`](adrs/README.md).
With a boundary rule, a bleed/vendor-span distinction, and a stress test for the many
tools that straddle the divisions. Everything else in the repo declares where it belongs.

**[`methodology.md`](methodology.md)** — how work is done here: verification and honesty
rules, generated indexes, preregistered experiments, the upstream-reporting gate. Every
rule earned its place by catching a real mistake; the anti-goal section keeps it from
growing rigor for rigor's sake.

**[`design-principles.md`](design-principles.md)** — the synthesis layer: design
principles derived from the documented tools, per taxonomy layer, each carrying a
confidence marker (convergent / single-instance / contested) and its evidence citations.
Hypotheses under revision, not best practices — every new deep-dive or experiment must
confirm, contradict, or note silence.

| Layer | Index | Examples |
|-------|-------|----------|
| 1 · Models | [`notes/01-models/`](notes/01-models/index.md) | Opus 5, Fable 5, Grok 4.5, Kimi K3 |
| 2 · Harnesses | [`notes/02-harnesses/`](notes/02-harnesses/index.md) | Claude Code, OpenCode, Codex CLI, Cursor |
| 3 · Execution environments | [`notes/03-execution-environments/`](notes/03-execution-environments/index.md) | worktrees, devcontainers, E2B |
| 4 · Workflow frameworks | [`notes/04-workflow-frameworks/`](notes/04-workflow-frameworks/index.md) | GSD, spec-kit |
| 5 · Extensions (bucket) | [`notes/05-capability-extensions/`](notes/05-capability-extensions/index.md) | MCP servers, skills, hooks, rules files, config packs (ECC) |
| ✕ Cross-cutting | [`notes/cross-cutting/`](notes/cross-cutting/index.md) | context engineering, verification, cost |
| ✕ Standards | [`notes/standards/`](notes/standards/index.md) | MCP, `AGENTS.md` convention |

## Layout

| Path | Holds |
|------|-------|
| `CLAUDE.md` | How the repo works: where things go, the ingest/lint operations, the honesty columns |
| `taxonomy.md` | The layer definitions and boundary rule — the canonical reference |
| `methodology.md` | The working rules — verification, honesty markers, experiment protocol |
| `design-principles.md` | Design principles derived from the reports, per layer, confidence-marked |
| `notes/` | One index per layer, plus one file per tool, written while using it |
| `refs/` | One note per **source read** — papers and benchmarks — each carrying its own `read_depth`. See [`refs/README.md`](refs/README.md) |
| `upstream/` | Cloned open-source sources to read — **gitignored**, see [`upstream/README.md`](upstream/README.md) |
| `experiments/` | Small self-contained trials — ideally the *same* task, different tools |
| `comparisons/` | Side-by-side matrices distilled from the notes and experiments |
| `scripts/` | `sync-upstream.sh` (clone/update), `repo-facts.sh` (verified frontmatter facts), `build-tool-index.py` and `build-refs-index.py` (regenerate the indexes) |
| `articles/` | Public-facing writing drawn from the findings — drafted next to the evidence, every claim linked and dated. See [`articles/README.md`](articles/README.md) |

**[`comparisons/tools.md`](comparisons/tools.md)** is the flat cross-layer index of every
tool with a report, **[`comparisons/features.md`](comparisons/features.md)** the
harness feature matrix, and **[`comparisons/models.md`](comparisons/models.md)** the
layer-1 matrix (thinking control, caching economics, batch pricing — the API surface
that drifts fastest) — all generated from the reports' frontmatter, never hand-edited,
so they can't drift from them. In the matrices, `·` means *not yet checked*, which is
deliberately distinct from ✗ *verified absent*.

Tools queued for assessment but not yet cloned live as **GitHub issues on this repo**
([issue #1](https://github.com/leandromineti/ai-assisted-coding/issues/1) is the
pattern) — candidates already weighed and passed over are recorded in the relevant
layer index's "considered, not added" table instead.

One report per tool, following
[`notes/_template-tool-report.md`](notes/_template-tool-report.md). Its **"distinguishing
bet"** field is the one that matters — what does this tool believe that its competitors
don't? — and **`depth`** is the honesty marker: `stub` (facts collected, source unread),
`survey` (used or skimmed), `deep-dive` (agent loop and context assembly actually traced).

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
3. **The extensions bucket (layer 5) is "MCP plus vendor features," so far** (2026-07-28). Of five capability-
   extension kinds, only MCP has fully standardized; rules files are converging on a
   filename convention; hooks and subagent definitions remain harness-specific.
   *Revised same day:* skills moved — spec-kit's integration registry shows `SKILL.md`
   consumed by at least four harnesses (Claude Code, Codex, Kimi, Hermes), so skills are
   now convention-level like rules files, no longer Claude-Code-shaped.
   Re-check the scoreboard ~2027-01. →
   [`notes/standards/index.md`](notes/standards/index.md)
   **Strengthened, headline unchanged (2026-08-11, Warp survey).** Both converging kinds
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
   *validation* worth ~3× pre-phase *grounding* ([`refs/spec-kit-agents.md`](refs/spec-kit-agents.md)).
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
7. **A layer-4 framework's portability and its enforcement power are the same tradeoff**
   (2026-07-28, spec-kit source read). Cross-harness portability is cheap because every
   harness converged on "slash command = prompt file" — but that lowest common
   denominator means the framework's runtime *is* the model reading prose. spec-kit's git
   history shows the consequence: hook execution was fixed twice by rewriting
   instructions more forcefully (#2901, #2713 — enforcement by typography), the
   constitution went eight months unenforced during implementation (#2460), and the one
   attempt at real context isolation was reverted after compounding-context freezes
   (#3185). Both frameworks studied grew deterministic engines (spec-kit's `workflows/`
   YAML runner, GSD's `gsd-pi`) as the escape hatch — layer-2 bleed as a structural
   symptom, not a coincidence. →
   [`notes/04-workflow-frameworks/spec-kit.md`](notes/04-workflow-frameworks/spec-kit.md)
   **Independently corroborated (2026-07-31):** a six-framework taxonomy study covering the
   same subjects reaches the same tradeoff — "no framework strongly covers all six dimensions
   … a structural trade-off between process depth and portability" — from documentation
   alone, where ours came from reading git history
   ([`refs/from-prompt-to-process.md`](refs/from-prompt-to-process.md)). Two methods, one
   shape. Its GSD scores are also where our *run* evidence contradicts a docs-only reading.
8. **Harnesses are absorbing the stack from the middle** (2026-07-30, from the hermes +
   codex deep-dives). The mechanisms adjacent layers sell are turning up *natively in
   layer 2*, twice each: turn-end verification gates (hermes' `verification_stop`,
   codex's stop hooks that veto termination — the mechanism conclusion 6 credits with
   layer 4's quality margin), autonomous memory loops (hermes on-by-default, codex
   stable-but-off — now the `learning loop` matrix column), programmatic tool calling
   (hermes' `execute_code`, codex's sandboxed-V8 code-mode), and plan modes everywhere.
   Consequence for the experiment arc: a layer-4 framework's measured margin must be
   re-baselined against what the harness already does — recorded as a design rider on
   exp-03 in [`notes/cross-cutting/`](notes/cross-cutting/index.md). →
   [`notes/02-harnesses/hermes-agent.md`](notes/02-harnesses/hermes-agent.md),
   [`notes/02-harnesses/codex.md`](notes/02-harnesses/codex.md)
   **Third instance, and a counter-instance (2026-08-11, Warp survey — weaker evidence
   than the two deep-dives above; the loop was not traced).** Extended: Warp absorbs
   layer-4-shaped *orchestration* — multi-agent fan-out where the harness running each
   child is a selectable field (`enum Harness { Oz, Claude, OpenCode, Gemini, Codex }`),
   with drivers and transcript parsers for its competitors. Absorption is not only
   downward and upward but *sideways*: a harness that treats rival harnesses as
   interchangeable backends. Contradicted on one leg: the **autonomous memory loop is
   absent**. Warp ships the whole store — versions, per-agent scoping, a CLI — and
   `MemorySource` has exactly one variant, `Manual`. So of three harnesses examined for
   it, one is on by default, one stable-but-off, one user-write-only. "Twice each" was
   never "always," and the `learning loop` column now has a verified ✗ to sit beside its
   ✓s. → [`notes/02-harnesses/warp.md`](notes/02-harnesses/warp.md)
9. **The environments layer (3) is a real rung, not an axis of the harness layer —
   decided by its own falsifier** (2026-08-16, decision record
   [ADR-0003](adrs/0003-environments-stay-a-rung.md)). The taxonomy pre-committed to
   demoting execution-environments unless study showed an environment fact that isn't
   just a restatement of how a harness attaches to one. For three weeks every
   environment finding *was* a harness property (the four relationship verbs —
   bundle/bind/internalize/inhabit — all live in layer-2 frontmatter),
   and a gated demotion to "an axis of layer 2" was written and scheduled. The first
   environment studied as a product in its own right — **E2B**, read from its open-source
   infra — fired the keep-it-a-rung arm the same day: ~26 environment-facts to 6
   attachment-restatements, **every one of the 26 invisible from the SDK** (Firecracker with
   no jailer running as root; every "create" secretly a snapshot resume with no warm pool;
   the credential-injection proxy absent from the open-source build; guest `kcompactd`
   disabled for host snapshot-diff economics). One genuine population member falsifies "fails
   as a population." *Live caveat:* the result may be an artifact of E2B being open — a
   closed environment (Modal/Daytona/Cloudflare) might yield only testimony, which
   [issue #11](https://github.com/leandromineti/ai-assisted-coding/issues/11) exists to test.
   → [`notes/03-execution-environments/e2b.md`](notes/03-execution-environments/e2b.md),
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
12. **A model tier absorbed a workflow mechanism whole — and the layer-4 A/B arc closes
    on it** (2026-08-18, exp-03, preregistered two-tier ablation, saturation branch
    pre-declared). On a buried-trap corpus, a one-file "measure the domain first"
    instruction lifted Haiku's trap discovery from 4.0/9 (plain band, n=5) to 8/9 —
    while a gates-only file found just the crash-visible traps (never the silent
    miscounts, 0/3), and the two files *combined* interfered: grounding went
    checkbox-shallow in 3 of 3 runs. On our fails-closed binary instrument the
    decomposition is **grounding > gates > both** — the opposite direction from the
    published LLM-judge ablation ([`refs/spec-kit-agents.md`](refs/spec-kit-agents.md)),
    recorded with both candidate attributions (instrument, model). Then tier 2: **plain
    Sonnet discovered 8.3/9 unprompted** — one model tier absorbed the instruction's
    entire measured value (P5's shrink-with-capability prediction, in the limit).
    Consequence, decided with the owner: layer-4 code-outcome A/Bs stop; the
    measurable subjects are the model+harness **bundle** (whose 7–14/23 run-to-run
    band is wider than most framework effects) and **artifact-level** framework value
    (conclusion 11). Caveats stated in the report: the Haiku grounding arm is n=1;
    one check (t3c) went 0/20 with satisfiability unproven. →
    [`experiments/03-minimal-harness/`](experiments/03-minimal-harness/README.md) ·
    [`notes/cross-cutting/layer-2-program.md`](notes/cross-cutting/layer-2-program.md)
