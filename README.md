# ai-assisted-coding

A personal sandbox for understanding the AI-assisted-coding tooling landscape — from
first-hand trial rather than from marketing pages.

This is a learning repo. The deliverable is notes and conclusions, not a product.

## Start here

**[`taxonomy.md`](taxonomy.md)** — the shared vocabulary. A **core triad** — models,
harnesses, execution environments, the three things a running agent cannot lack — plus
two **interfaces**: portable artifacts (a cross-layer bucket parameterizing the triad's
edges; the former layer 3, demoted by evidence 2026-07-30) and workflow frameworks (the
human⇄stack boundary: intent refined into specs and subtasks going down, research and
verified evidence coming up). Reframed 2026-08-17; numbering retained as storage keys.
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
| 3 · Portable artifacts (bucket) | [`notes/03-capability-extensions/`](notes/03-capability-extensions/index.md) | MCP servers, skills, hooks, rules files, config packs (ECC) |
| 4 · Workflow frameworks | [`notes/04-workflow-frameworks/`](notes/04-workflow-frameworks/index.md) | GSD, spec-kit |
| 5 · Execution environments | [`notes/05-execution-environments/`](notes/05-execution-environments/index.md) | worktrees, devcontainers, E2B |
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

**[`comparisons/tools.md`](comparisons/tools.md)** is the flat cross-layer index of every
tool with a report, and **[`comparisons/features.md`](comparisons/features.md)** the
harness feature matrix — both generated from the reports' frontmatter, never hand-edited,
so they can't drift from them. In the matrix, `·` means *not yet checked*, which is
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
   [PR #13](https://github.com/akitaonrails/llm-coding-benchmark/pull/13)). →
   [`notes/01-models/index.md`](notes/01-models/index.md)
3. **Layer 3 is "MCP plus vendor features," so far** (2026-07-28). Of five capability-
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
9. **Layer 5 is a real rung, not an axis of layer 2 — decided by its own falsifier**
   (2026-08-16). The taxonomy pre-committed to demoting execution-environments unless
   study showed a layer-5 fact that isn't just a restatement of how a harness attaches to
   one. For three weeks every layer-5 finding *was* a harness property (the four
   relationship verbs — bundle/bind/internalize/inhabit — all live in layer-2 frontmatter),
   and a gated demotion to "fifth axis of layer 2" was written and scheduled. The first
   environment studied as a product in its own right — **E2B**, read from its open-source
   infra — fired the keep-it-a-rung arm the same day: ~26 environment-facts to 6
   attachment-restatements, **every one of the 26 invisible from the SDK** (Firecracker with
   no jailer running as root; every "create" secretly a snapshot resume with no warm pool;
   the credential-injection proxy absent from the open-source build; guest `kcompactd`
   disabled for host snapshot-diff economics). One genuine population member falsifies "fails
   as a population." *Live caveat:* the result may be an artifact of E2B being open — a
   closed environment (Modal/Daytona/Cloudflare) might yield only testimony, which
   [issue #11](https://github.com/leandromineti/ai-assisted-coding/issues/11) exists to test.
   → [`notes/05-execution-environments/e2b.md`](notes/05-execution-environments/e2b.md),
   [`notes/05-execution-environments/index.md`](notes/05-execution-environments/index.md)
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
