# Conclusions

`checked: 2026-09-03`

The repo's actual output: the running answer to "what did I actually learn?"
Numbered, dated, each traceable to a note — a conclusion without a linked note is
an assertion, and a finding that changed no note is an anecdote (methodology rule
6). Revised when evidence moves; the numbers are stable citation keys, cited as
"conclusion N" throughout the repo. Lived in `README.md` until 2026-08-26
(ADR-0028); [`../README.md`](../README.md) keeps the headline index.

---

1. **"The models have converged" is contested by the people best placed to know**
   (2026-07-28). The three portable harnesses answer the per-model-prompt question three
   different ways: opencode maintains nine bespoke prompts sharing zero substantive lines;
   cline built that architecture and *dismantled* it; continue runs ~15 lines and bets the
   prompt barely matters. Nobody's position is backed by a published eval. →
   [`tools/2-harnesses/README.md`](../tools/2-harnesses/README.md)
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
   [`tools/1-models/README.md`](../tools/1-models/README.md)
3. **The extensions bucket (category 6; numbered 5 until the 2026-08-22 split) is "MCP plus vendor features," so far** (2026-07-28). Of five capability-
   extension types, only MCP has fully standardized; rules files are converging on a
   filename convention; hooks and subagent definitions remain harness-specific.
   *Revised same day:* skills moved — spec-kit's integration registry shows `SKILL.md`
   consumed by at least four harnesses (Claude Code, Codex, Kimi, Hermes), so skills are
   now convention-level like rules files, no longer Claude-Code-shaped.
   Re-check the scoreboard ~2027-01. →
   [`docs/standards.md`](standards.md)
   **Strengthened, headline unchanged (2026-08-11, Warp survey).** Both converging types
   gained their best evidence yet, and it is a better *class* of evidence: a first-party
   implementation by a rival vendor rather than a third-party installer targeting the
   format. Warp parses `SKILL.md` natively (`crates/ai/src/skills/`, 13 bundled skills) —
   a fifth consumer — and its project-init flow offers to link seven *competitors'* rules
   files (`CLAUDE.md`, `.cursorrules`, `GEMINI.md`, `.clinerules`, `.windsurfrules`,
   Copilot instructions, `AGENT.md`) into its own. The headline still stands: both remain
   filename-plus-frontmatter conventions with no schema, and hooks and subagent
   definitions did not move. → [`tools/2-harnesses/warp.md`](../tools/2-harnesses/warp.md)
4. **Structural completeness does not predict runtime correctness** (2026-07-28, from
   llm-coding-benchmark's data): models produce complete-looking apps whose tests mock
   hallucinated APIs — green suites over dead code. Any personal eval must boot the
   artifact, not count its files. →
   [`docs/README.md`](README.md)
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
   margin? → [`experiments/01-gsd-vs-plain/`](../experiments/01-gsd-vs-plain/README.md)
   **Status 2026-07-31 — under re-examination, issue #8.** A published n=128 ablation
   separates the two ingredients this conclusion credits jointly and finds post-phase
   *validation* worth ~3× pre-phase *grounding* ([`references/papers/2026-spec-kit-agents.md`](../references/papers/2026-spec-kit-agents.md)).
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
   [`tools/4-workflow-frameworks/spec-kit.md`](../tools/4-workflow-frameworks/spec-kit.md)
   **Independently corroborated (2026-07-31):** a six-framework taxonomy study covering the
   same subjects reaches the same tradeoff — "no framework strongly covers all six dimensions
   … a structural trade-off between process depth and portability" — from documentation
   alone, where ours came from reading git history
   ([`references/papers/2026-from-prompt-to-process.md`](../references/papers/2026-from-prompt-to-process.md)). Two methods, one
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
   ([ADR-0011](../adrs/0011-graded-gate-enforcement.md)): no framework yet has an
   engine-graded measured or process gate. →
   [`tools/4-workflow-frameworks/gsd-core.md`](../tools/4-workflow-frameworks/gsd-core.md)
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
   same-day [bmad-loop stub](../tools/4-workflow-frameworks/bmad-loop.md) completes the
   shape: the ecosystem's companion orchestrator holds the tracked category's first
   **engine-graded measured and process gates** ("No LLM in the control loop") — so
   "no framework yet has an engine-graded measured or process gate" stays true
   precisely because BMAD ships those gates outside the framework, in the escape
   hatch productized. →
   [`tools/4-workflow-frameworks/bmad-method.md`](../tools/4-workflow-frameworks/bmad-method.md)
   **Reinforced (2026-08-21, gsd-core v1.11.0 release re-read):** the migration
   direction held under a 369-commit window — every enforcement movement went
   prose→code (disk-strict completion predicate, vendored RE2 for untrusted plan
   regexes, an opt-in git-hook guard below the agent altogether), none the other way, and
   the window's recurring defect class was *believed-live prose found inert* (four
   independent cases, incl. a 40KB workflow loaded by nothing) — the strongest
   evidence yet on the reliability floor of prose-graded gates. One count corrected:
   "three hard-blocking hooks" was a curated subset — a lexical exit-2 grep matches 8
   hook files at both pins. →
   [release assessment](../tools/4-workflow-frameworks/gsd-core.md#release-assessment--v1110-2026-08-21-pin-fee72d55--182f60b4)
8. **Harnesses are absorbing the stack from the middle** (2026-07-30, from the hermes +
   codex deep-dives). The mechanisms adjacent categories sell are turning up *natively in
   category 2*, twice each: turn-end verification gates (hermes' `verification_stop`,
   codex's stop hooks that veto termination — the mechanism conclusion 6 credits with
   category 4's quality margin), autonomous memory loops (hermes on-by-default, codex
   stable-but-off — now the `learning loop` matrix column), programmatic tool calling
   (hermes' `execute_code`, codex's sandboxed-V8 code-mode), and plan modes everywhere.
   Consequence for the experiment arc: a category-4 framework's measured margin must be
   re-baselined against what the harness already does — recorded as a design rider on
   exp-03 in [`docs/`](README.md). *(Reliability datum on the flagship absorbed loop,
   2026-09-04, hermes v2026.8.31 re-read: hermes' on-by-default review fork had been
   silently **starving in production** — its own tool whitelist denied `read_file`, ~142
   denials in two days on one deployment, "almost no patch landed" per the upstream
   comment that widened the whitelist. An absorbed loop can be default-on, gated, and
   doing nothing; presence≠operative applies to the absorption thesis too, and only the
   vendor's own telemetry caught it.)* →
   [`tools/2-harnesses/hermes-agent.md`](../tools/2-harnesses/hermes-agent.md),
   [`tools/2-harnesses/codex.md`](../tools/2-harnesses/codex.md)
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
   of governance.)* → [`tools/2-harnesses/warp.md`](../tools/2-harnesses/warp.md)
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
   contact with use is an open rig question *(answered 2026-08-19 by conclusion 14:
   pull-shaped)*. **The counter-current strengthened (2026-09-04, ai-memory v2.0.2
   re-read)**: 2.6k → 5.7k stars in 17 days, the file-first store now natively conforms
   to Google Cloud's Open Knowledge Format (the independent-store bet got a vendor
   standard), and 51% of the window's merged PRs came from outside contributors. →
   [`tools/5-memory/ai-memory.md`](../tools/5-memory/ai-memory.md),
   [`tools/5-memory/memos.md`](../tools/5-memory/memos.md)
9. **The environments category (3) is a real category, not an axis of the harness category —
   decided by its own falsifier** (2026-08-16, decision record
   [ADR-0003](../adrs/0003-environments-stay-a-rung.md)). The taxonomy pre-committed to
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
   → [`tools/3-execution-environments/e2b.md`](../tools/3-execution-environments/e2b.md),
   [`tools/3-execution-environments/cloudflare-sandbox-sdk.md`](../tools/3-execution-environments/cloudflare-sandbox-sdk.md),
   [`tools/3-execution-environments/microsandbox.md`](../tools/3-execution-environments/microsandbox.md),
   [`tools/3-execution-environments/daytona.md`](../tools/3-execution-environments/daytona.md),
   [`tools/3-execution-environments/README.md`](../tools/3-execution-environments/README.md)
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
    [`docs/benchmark-survey.md`](benchmark-survey.md),
    [`experiments/02-spec-kit-vs-plain/log.md`](../experiments/02-spec-kit-vs-plain/log.md)
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
    [`experiments/02-spec-kit-vs-plain/`](../experiments/02-spec-kit-vs-plain/README.md)
12. **A model tier absorbed a workflow mechanism whole — and the category-4 A/B arc closes
    on it** (2026-08-18, exp-03, preregistered two-tier ablation, saturation branch
    pre-declared). On a buried-trap corpus, a one-file "measure the domain first"
    instruction lifted Haiku's trap discovery from 4.0/9 (plain band, n=5) to 8/9 —
    while a gates-only file found just the crash-visible traps (never the silent
    miscounts, 0/3), and the two files *combined* interfered: grounding went
    checkbox-shallow in 3 of 3 runs. On our fails-closed binary instrument the
    decomposition is **grounding > gates > both** — the opposite direction from the
    published LLM-judge ablation ([`references/papers/2026-spec-kit-agents.md`](../references/papers/2026-spec-kit-agents.md)),
    recorded with both candidate attributions (instrument, model). Then tier 2: **plain
    Sonnet discovered 8.3/9 unprompted** — one model tier absorbed the instruction's
    entire measured value (P5's shrink-with-capability prediction, in the limit).
    Consequence, decided with the owner: category-4 code-outcome A/Bs stop; the
    measurable subjects are the model+harness **bundle** (whose 7–14/23 run-to-run
    band is wider than most framework effects) and **artifact-level** framework value
    (conclusion 11). Caveats stated in the report: the Haiku grounding arm is n=1;
    one check (t3c) went 0/20 with satisfiability unproven. →
    [`experiments/03-minimal-harness/`](../experiments/03-minimal-harness/README.md) ·
    [`docs/category-2-program.md`](category-2-program.md)
13. **The memory extensions sell to coding agents but benchmark on chat** (2026-08-18,
    memory-type reading arc: one deep-dive, two surveys, three instrument full-reads).
    The type's verified substance is real — three distinct wagers (markdown wiki / RL
    policy database / knowledge graph), three consolidation postures (background cron /
    per-turn event cascade / agent-invoked), and cross-harness continuity as the one
    bet no single harness can absorb (conclusion 8's counter-current). *(Structured
    2026-08-19: the comparison is now an 11-key `memory_features` registry block and
    generated matrix — [ADR-0013](../adrs/0013-memory-features-block.md); first cut shows
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
    [`tools/5-memory/mem0.md`](../tools/5-memory/mem0.md)
    **Third instance, inverted (2026-08-19, memos deep-dive):** the benchmark-vs-product
    gap runs the other way — memos' machinery is real and golden-tested in source, but
    the ten README numbers (five of them CODING benchmarks incl. SWE-Bench, all
    attributed to a non-vendored external repo) describe the full-evolution
    configuration, while the shipped default — verified in code, templates, and the
    published npm artifact — runs with that machinery unmounted. The type's pattern is
    now symmetric: mem0 benchmarks what the OSS artifact doesn't contain; memos
    benchmarks what the shipped default doesn't enable. →
    [`tools/5-memory/memos.md`](../tools/5-memory/memos.md)
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
    *(The seam was closed unconditionally at v2.0.2 — schema fixed at the source plus a
    regression fence test; run-verified 2026-09-04 at the re-read. The measurement
    stands at its own pin.)*
    **Arm C (same day): the floor is a design property, not a zero-LLM artifact** — with
    the LLM consolidation loop enabled and manually triggered, the reviewer surfaced the
    facts as candidates and rejected every one on an articulated evidence bar
    ("acknowledged but not made or refined in session; no implementation evidence") —
    the memory system refuses to mint knowledge from conversational say-so, which is
    exactly this repo's own rule 4 applied by a tool to its user. →
    [`experiments/04-memory-continuity/`](../experiments/04-memory-continuity/README.md) But every
    instrument the vendors self-report on — LoCoMo, LongMemEval, BEAM — measures
    personal chat-assistant memory: no tool traces, no repo state, no code entities.
    **No coding-agent memory benchmark exists**, and the two vendor headline numbers
    checked exceed their instruments' own published scales (mem0's 92.5 vs LoCoMo's
    87.9 *human* baseline; cognee's 0.79 vs BEAM's ~0.36 best configs) — so the
    type's efficacy for coding is currently an unmeasured claim resting on
    conversational proxies. *Deepened same day by the mem0 vendor paper
    ([`references/papers/2025-mem0.md`](../references/papers/2025-mem0.md), full read): mem0's own published
    comparison shows the no-memory full-context baseline beating its memory system
    on quality (J 72.90 vs 68.44) — the measured claim is latency/token efficiency —
    and the 92.5 belongs to a later rewrite whose architecture the paper doesn't
    describe.* →
    [`docs/benchmark-survey.md`](benchmark-survey.md) §6 ·
    [`tools/5-memory/README.md`](../tools/5-memory/README.md)


15. **Harnesses track models by name, so a model's own API drift silently disarms them**
    (2026-08-26, four harnesses read at their pins for
    [issue #40](https://github.com/leandromineti/ai-assisted-coding/issues/40)). Category 1's
    reasoning surface is not one switch: eleven models split four ways on toggleability
    and carry six distinct depth dials, one of which is a token budget rather than a level
    enum (ADR-0040). Every harness read encodes that spread as **model-id string matching
    or nothing**, and each pin already trailed models that had shipped before it was read:
    opencode matches the literal `glm-5.2`, so **GLM-5.3 falls through to an empty variant
    map and no effort parameter is sent**; cline enumerates Opus `4.6/4.7/4.8` + Fable 5,
    omitting **Opus 5 and Sonnet 5**, and its own CLI accepts an `xhigh` its SDK config
    builder drops; aider — the best architecture of the four, capability declared as data with an
    opt-in check — still auto-grants `thinking_tokens` to every OpenRouter model *except*
    `claude-opus-4.7`, the single id someone carved out reactively.
    **The failure has two shapes, and the quiet one costs money.** Sending nothing
    succeeds and lets the server apply its own default — which on GLM-5.3 and Kimi K3 is
    `max`, the sweep's only default-to-most-expensive models and precisely the two
    opencode cannot reach. Sending a deprecated parameter 400s instead: continue's
    Anthropic provider emits `thinking: {type: "enabled", budget_tokens}` with **no
    model check on the branch at all**, which Anthropic rejects on every model from 4.7
    onward — all three current frontier models.
    **This inverts the obvious defence.** Per-vendor adapters were the shape predicted to
    be immune, and continue is exactly that shape and fails hardest: adapters keep one
    vendor's surface from being mistaken for another's, and do nothing about a vendor
    deprecating its own parameter, because model *version* is not a dimension of the
    design. Conclusion 8's absorption thesis has a cost side — a harness that owns the
    model-capability decision inherits the obligation to track every vendor's deprecations,
    and none of the four is winning that race.
    **QUALIFIED 2026-08-27 by the fifth harness, which closes the gap this conclusion
    declared** ([issue #41](https://github.com/leandromineti/ai-assisted-coding/issues/41)):
    hermes-agent does not fail the Anthropic comparison, and the reason is that someone
    inverted the polarity on purpose and wrote down why. Its adapter keeps a **denylist of
    superseded Claude families and defaults unknown models to the newest contract**, because
    — in its own comment — *"an allowlist of version numbers ('4.6', '4.7', …) goes stale the
    moment a model ships without a recognized number."* Opus 5, Sonnet 5, Fable 5 and Opus 4.8
    all route correctly with no code change; 4.5-and-older correctly take the legacy budget
    path. Where the vendor's failure runs the other way it uses an allowlist for the same
    reason — on xAI, an unlisted model gets **no effort dial rather than a 400**, stated as
    *"conservative by design"*. So the defence is not an architecture, it is a **per-vendor
    choice of default direction, made from the observed failure**: default-to-newest where
    the old shape is rejected, default-to-silent where the new dial is. That is cheap, and
    the other four could have done it.
    Two things keep this a qualification rather than a refutation. Hermes carries the same
    disease wherever nobody engineered against it — its OpenRouter capability gate allowlists
    `google/gemini-2` while its own Gemini adapter, two files away, already branches on
    `gemini-3`, so a Gemini 3 model reached through OpenRouter is sent no reasoning field at
    all. And **Warp shows the cost of the escape hatch**: driving Codex as a sub-harness, it
    writes whatever effort string the user picked into `config.toml` with no model check and
    no validation, and removes the key when unset. Zero exposure of its own — and zero
    ability to detect or fix the sub-harness's, which is one of the four failures above.
    Delegation moves the obligation; it does not discharge it.
    Scope: five harnesses read closely, two (gemini-cli single-vendor, codex config-driven)
    structurally out of reach of the pattern; Warp characterised as a delegating case.
    **VALIDATED BY UPSTREAM 2026-09-04** (hermes v2026.8.31 release re-read): the exact
    hardcoded-generation-string instance the qualification flagged as "in waiting" fired
    as hermes' own issue #89503 within four weeks, and their fix commit names the same
    mechanism before replacing every per-backend hand map with declared wire
    vocabularies plus one clamp policy ("Never patch a predicate… fix its declared
    supported set (data), never add another vendor-name special case"). Meanwhile the
    denylist ran the whole 7,055-commit window byte-identical — zero code changes,
    through an adapter-splitting refactor — while the Grok allowlist needed a
    hand-extension for grok-4.6, and the OpenRouter gap was *demoted* (live catalog
    probe first, stale static list as cold-cache fallback), not fixed. The conclusion's
    cost thesis now has the vendor's own engineering as corroboration. →
    [`tools/2-harnesses/opencode.md`](../tools/2-harnesses/opencode.md) §7 ·
    [`cline.md`](../tools/2-harnesses/cline.md) §3 ·
    [`continue.md`](../tools/2-harnesses/continue.md) ·
    [`aider.md`](../tools/2-harnesses/aider.md) ·
    [`hermes-agent.md`](../tools/2-harnesses/hermes-agent.md) § Reasoning-parameter handling ·
    [`warp.md`](../tools/2-harnesses/warp.md) § Reasoning-parameter handling ·
    [ADR-0040](../adrs/0040-reasoning-replaces-thinking.md)

16. **Every model maker ships its own harness — the composability the taxonomy assumes is
    not what the market is selling** (2026-08-26, all eight makers with a tracked model
    report). Anthropic → Claude Code · OpenAI → Codex · Google → Gemini/Antigravity CLI ·
    xAI → Cursor (acquired 2026-06) · DeepSeek → dsh · Alibaba → qwen-code · Moonshot →
    kimi-code · Z.ai → ZCode. **Eight of eight, no exceptions, and the direction is
    one-way**: no harness maker in the set has trained a model and moved the other way.
    The framework's default posture — pick a model, pick a harness, pick an environment —
    describes the field's composable middle, and there *is* one; but at the point where
    the weights are made, a first-party harness always exists and it is always the one the
    model was tuned against. Conclusion 1's per-model prompts are the mechanism seen from
    the other side: opencode maintains nine bespoke prompts precisely because each maker
    has already tuned its own harness to its own weights, and a portable harness has to
    re-derive that fit per model, forever.
    **The last two instances arrived by falsifying this repo's own claims, hours apart.**
    The paragraph recording maker span said six of eight, then seven, before it said eight
    — each correction driven by a product that existed and had not been looked for. That
    failure produced [methodology rule 1b](methodology.md) and is worth more than the
    count: the two holdouts were *both* real, and the reason to doubt them was available
    the whole time.
    **What is falsifiable now.** The model→harness direction is saturated and can no
    longer surprise; the live claim is its converse — that a harness maker with no model
    (Anomaly, Cline, Continue, Earendil Works, Warp) trains or brands one. Also watch the
    business shape rather than the product: Z.ai sells the GLM Coding Plan *into* other
    people's harnesses **and** ships ZCode, so first-party-harness and sell-into-everyone
    are not alternatives — which is the reading that would have to break for this
    conclusion to weaken. →
    [`docs/tool-taxonomy.md`](tool-taxonomy.md) § Maker span ·
    [`tools/candidates.md`](../tools/candidates.md) (kimi-code, ZCode) ·
    [`tools/2-harnesses/claude-code.md`](../tools/2-harnesses/claude-code.md) ·
    [ADR-0041](../adrs/0041-vendors-matrix-removed.md)

17. **The context-assembly position everyone assumed nobody held was held all along, by the
    oldest and most dormant tool in the set** (2026-08-27,
    [aider deep-dive](../tools/2-harnesses/aider.md), all three ADR-0021 components traced
    at `5dc9490b`). Since 2026-08-11 this repo has tracked a claim across three deep-dives —
    warp, gemini-cli, qwen-code — that **no tracked harness assembles context from an
    index**: warp's embedding index turned out to back a single search tool whose chain ends
    in a `{name, path}` pointer with zero surrounding context lines; gemini-cli's embedding
    path is dead code with zero production callers; retrieval is delegated to a subagent or
    to grep everywhere it was looked for. The claim survived every test it was given.
    **It was false, and the falsifier was never read.** aider ships a persistent on-disk
    symbol index (`.aider.tags.cache.v4`, diskcache/SQLite, mtime-invalidated) built by
    tree-sitter from 58 query files, ranks it with real `nx.pagerank` over a weighted
    file-reference graph, enforces a token budget by binary search, and injects **the actual
    source lines** of each ranked definition into a **user message every single turn**, with
    no model request. Measured on the published artifact against aider's own 691-file repo:
    110 files and 25,253 bytes at the 4096-token default — **71% of the entire assembled
    prompt**. Warp's index ends in a pointer; aider's ends in the prefix.
    **The error was a sampling artifact, and that is the transferable part.** Every harness
    read closely between 2026-07 and 2026-08 was a 2025–2026 tool-dispatch design, where
    retrieval is necessarily a tool the model calls and therefore necessarily a pointer. The
    claim generalized correctly over what had been read and silently assumed the sample was
    the field. The tool that broke it is the one nobody prioritized *because* it is old and
    dormant — the same reasoning that made it low-priority made it the only member of the
    other class. **A negative claim about a category is only as good as the diversity of the
    sample, not just the size of the search** — [rule 1b](methodology.md) says an absence is
    only as good as the surface you searched; this adds that a surface can be wide and still
    be one kind of place.
    **Two riders keep it from being read as a straight win**, both measured. The index needs
    a human seed: at a 1024-token budget with an empty chat it selects 33 files of which 20
    are language test fixtures and omits `base_coder.py`, the repo's own core file — add
    that one file and the map collapses to 13, 10 of them its real collaborators, because
    files in the chat carry a ×50 edge multiplier. The human's `/add` *is* the PageRank's
    personalization vector. And the index collides with prompt caching: aider diagnosed the
    collision three years before the same shape surfaced at hermes, fixed it in two lines,
    and the fix silently disables per-query personalization — RUN-confirmed, the whole
    disclosure being one word in the startup banner. →
    [`tools/2-harnesses/README.md`](../tools/2-harnesses/README.md) axes 1 and 6 ·
    [`docs/design-principles.md`](design-principles.md) H5 ·
    [`warp.md`](../tools/2-harnesses/warp.md) · [`gemini-cli.md`](../tools/2-harnesses/gemini-cli.md)

18. **A harness with no tool loop ships the strongest native verification gate in the set —
    so "runs something fresh before the turn ends" is independent of agentic dispatch**
    (2026-08-27, [aider deep-dive](../tools/2-harnesses/aider.md)). aider never sends a tool
    schema: `functions = None` on the base coder, the only three classes that would attach
    one are dead code with no importers, and the whole turn engine is 13 lines capped at a
    hard-coded 3 reflections. It cannot call a tool. Yet `--auto-lint` **defaults to true**,
    and with *zero* user configuration every edited Python file gets a tree-sitter parse, a
    real `compile()`, and a `flake8` subprocess whose failures are rendered in AST context
    and fed back as the next user message. RUN-confirmed on the published artifact,
    including `F821 undefined name` in **syntactically valid** code — a semantic error
    catchable only by actually running a linter.
    **This is the first tracked harness to clear the repo's "ran something fresh" bar by
    default**, and it clears it without any of the machinery the bar was assumed to require.
    Across the other eleven category-2 reports, turn-end gating is `hook`-grade surfaces
    that ship empty (claude-code, codex, gemini-cli, qwen-code), `engine` policy that is
    default-off or default-empty (dsh, gemini-cli's next-speaker), verified absent
    (opencode, cline, continue, warp), or default-on in exactly one product (hermes).
    Conclusion 8's absorption thesis holds that harnesses ate the workflow frameworks'
    mechanisms; aider shows the *measured-gate* leg was never a function of that absorption —
    it needs a linter and a place to put the output, not a tool registry.
    **The qualifier is stated rather than buried**: the re-prompt passes through a
    `confirm_ask` that defaults to yes, auto-accepts under `--yes-always`, and returns its
    default on `EOFError` in every non-interactive mode. The human touchpoint exists in the
    default interactive path and evaporates everywhere else — so aider is unambiguously
    default-on and measured, and ambiguously *unattended*.
    **Falsifier**: a harness shipping a default-on verifier that re-prompts with no human
    touchpoint at all would move aider from "strongest" to "second"; the vendor-native three
    (codex, dsh, gemini-cli) already ship the surface and would only need to arm it. →
    [`tools/2-harnesses/README.md`](../tools/2-harnesses/README.md) § absorption table,
    `measured_gates` · [ADR-0011](../adrs/0011-graded-gate-enforcement.md)
19. **The served API outranks its own documentation, and the tiebreak costs nothing**
    (2026-08-31, the issue-#42 probe campaign — eight makers, thin HTTP client, no SDK,
    total spend under $0.02). Category-1 facts were being verified against vendor *pages*
    (dated-docs grade); the first campaign that verified them against the *wire* found the
    pages wrong, silent, or misleading five independent ways in one day:
    the Qwen3.8 model pages advertise Batch cards for two models the Batch API rejects by
    name (`model_not_found` — the marketing surface contradicted by the serving surface);
    Qwen states its flagship's thinking default nowhere, and one paramless request answers
    it (`default-on`, closing the sweep's only deliberately-blank enum cell);
    Moonshot **accepts `enable_thinking: false` and silently ignores it** — three vendors
    now span reject-with-error (Z.ai, whose refusal names its own level set), honor
    (Qwen), and swallow (Moonshot) for the same parameter intent;
    Anthropic's fast-mode waitlist framing did not gate a plain pay-as-you-go key (stated
    access process ≠ enforced one); and OpenAI's priority→fast rename is input-side only —
    the response still reports `"priority"`, so a caller reading the field would conclude
    the rename never happened (conclusion 15's name-drift problem, from the response side).
    The economics are the point: **rejected requests bill nothing**, so the highest-grade
    evidence for absence claims is also the cheapest — three of the five findings cost $0.
    Where behavior is observable, docs-grade cells should escalate to probes; vocabulary
    markers for vendor silence (`not-stated`) remain right only for facts no request can
    reach (cutoffs, dates). Bonus specimen, same sitting: Grok bills 497 prompt tokens on
    a three-word message and is the sweep's only API whose responses price themselves
    (`cost_in_usd_ticks`) — billed-input-per-request is a cost-axis fact no list price
    carries. →
    [`tools/1-models/README.md`](../tools/1-models/README.md) · the OBSERVED cell notes in
    [`qwen3.8-max`](../tools/1-models/qwen3.8-max.md),
    [`qwen3.8-flash`](../tools/1-models/qwen3.8-flash.md),
    [`kimi-k3`](../tools/1-models/kimi-k3.md), [`glm-5.3`](../tools/1-models/glm-5.3.md),
    [`grok-4-5`](../tools/1-models/grok-4-5.md) § Probed,
    [`claude-opus-5`](../tools/1-models/claude-opus-5.md) § Probed ·
    [issue #42](https://github.com/leandromineti/ai-assisted-coding/issues/42)
    **Confirmed on the wire, and a second instance (2026-09-03, BHV-06).** This
    conclusion's own OpenAI finding above is about a VALUE renamed between request and
    response (`priority`→`fast`); a different fact in the same asymmetry class is now
    confirmed directly, at a different maker — this one is about WHICH FIELD PATH the
    response reports a value under, not what the value is called. Anthropic's documented
    `service_tier` request field is never mirrored to the response's top level: every one
    of `claude-haiku-4-5`'s own non-trap audit cells shows the field present only at
    `usage.service_tier`, absent at the top level
    (`claude-haiku-4-5--service-tier-audit--auto--default--613638b0`), and the asymmetry
    carries its own trap — sending the response-vocabulary word `standard` as a request
    value is rejected outright, HTTP 400, naming the field
    (`claude-haiku-4-5--service-tier-audit--trap--default--8fc20f53`) — so the "caller
    reads the wrong field" hazard this conclusion's own title predicts is not
    hypothetical. Gemini, with no shared code, exhibits the structurally identical shape —
    request field `serviceTier` at the top level, response field `usageMetadata.serviceTier`
    nested — across all 5 of its own audit cells
    (`gemini-3-1-pro--service-tier-audit--flex--default`), suggesting the shape follows
    from nesting billing metadata under a usage envelope rather than from one maker
    copying another. →
    [`docs/parameter-patterns.md`](parameter-patterns.md) § The service-tier
    field-location asymmetry, twice ·
    [`probes/classified/behavioral.yaml`](../probes/classified/behavioral.yaml) BHV-06

20. **Determinism is nearly absent on the live wire, and only two models show any of it**
    (2026-09-03, ADR-0050's `seed_determinism` + `sampling_repeatability` keys). Requesting
    the same `seed` across five repeats produces zero matches at every one of the 8 models
    with a request-side `seed` field — 0/5 same-seed pairs, uniformly. Requesting
    `temperature: 0` (or, at the 5 models that reject `temperature` outright in default
    mode, the model's own default sampling) repeats at only 2 of the 12 tracked models:
    `claude-haiku-4-5` (4/4 repeat pairs, the sweep's only fully deterministic cell) and
    `gemini-3-1-pro` (2/4, partial); the remaining 10 show 0/4. A caller who sends `seed`
    or `temperature: 0` and receives a 200 has purchased acceptance, not reproducibility,
    almost everywhere this sweep reaches. →
    [`docs/parameter-patterns.md`](parameter-patterns.md) § Sampling determinism ·
    [`adrs/0050-wire-behavior-promotion.md`](../adrs/0050-wire-behavior-promotion.md)
21. **The compat dialect outlived its author, and the sweep's own harness papers over the
    evidence for it** (2026-09-03, `probes/PREREGISTRATION.md:340-344`). `gpt-5-6-sol` —
    OpenAI's own model — rejects the shared `openai_compat` family's `max_tokens` field
    outright, the exact name every third-party sibling (`grok-4-5`, `kimi-k3`,
    `deepseek-v4`, `glm-5.3`, `qwen3.8-max`, `qwen3.8-flash`) still accepts, because each
    copied OpenAI's own legacy Chat Completions field name when building its own compat
    surface. No classified row carries this fact: the harness applies a per-model
    field-rename override before firing (`probes/harness/models.yaml:73-79`), so every
    fired `max-tokens` cell already reads uniform `accepted-honored` — a reader who goes
    looking for a contradicting cell will not find one, because the override masks the
    split before any probe fires, not because the split isn't real. A harness author
    copying a sibling vendor's field name from a shared adapter cannot assume the origin
    vendor still accepts it. →
    [`docs/parameter-patterns.md`](parameter-patterns.md) § The compat dialect finding ·
    [`probes/PREREGISTRATION.md`](../probes/PREREGISTRATION.md)
22. **Where the wire had anything to say, it disagreed with the docs more than a quarter
    of the time** (2026-09-03, `comparisons/docs-vs-wire.md`, 612 pairs). 79 of the 612
    `(param, model)` pairs the sweep classified are contradicted by the vendor's own
    documentation. Read over pairs the wire actually tested — 288, i.e. excluding the 324
    `docs-untested` pairs no probe ever fired — the rate is 79/288 = 27.4%; read over all
    612 pairs regardless of whether the wire had anything to say, it is 79/612 = 12.9%.
    This document uses the narrower 288-pair denominator as its headline, because "how
    often did the tested surface disagree" is the actionable question for a caller
    deciding how much to trust a vendor's page; the wider 612-pair reading answers a
    different, less actionable one. A caller should weight documentation below a caller's
    own probe wherever a probe is affordable, at roughly 1-in-4 odds of being contradicted
    at the surface this sweep actually reached. →
    [`docs/parameter-patterns.md`](parameter-patterns.md) § The docs-versus-wire
    confrontation ·
    [`comparisons/docs-vs-wire.md`](../comparisons/docs-vs-wire.md)
23. **Every settled harness compacts, and every one that compacts summarizes with an
    LLM — the discriminator is what stands beside the summarizer** (2026-09-04, the
    ADR-0055 probe-pass at existing pins: 11 of 12 category-2 cells settled, warp an
    honest omit because its compaction is entirely server-side). Going in, issue #33
    proposed `none` as a candidate value; the probe found **zero instances** — no
    tracked harness ships without a compaction path, and `llm-summarize` appears in
    all 11 settled cells. So the column's information is not whether but *what else*:
    a deterministic pruner beside the summarizer in 4 (dsh; opencode and hermes-agent
    shipped off; claude-code's docs put it first in line), and a hard non-LLM
    `truncate` in 3 — for three different reasons to avoid the model (gemini-cli falls
    back to it after a *failed* summarization attempt rather than retry the LLM;
    codex's opt-in `token_budget` feature installs a fresh window instead of
    summarizing; cline falls back when the model can't support its summarizer). Two
    implications. Compaction quality rides the model everywhere, so at context
    pressure every harness silently spends model calls on its own bookkeeping — a
    background token bill no list price names. And the near-universal shape means the
    real design positions live in the *stack and its defaults*, which is exactly the
    per-mechanism fact the cells' comments carry and the enum deliberately does not. →
    [ADR-0055](../adrs/0055-context-assembly-group.md) ·
    [`comparisons/features.md § Harnesses`](../comparisons/features.md) ·
    [`tools/2-harnesses/README.md`](../tools/2-harnesses/README.md) § What we assess here
24. **Every memory vendor's learning loop auto-applies; propose-and-commit exists only
    as a harness posture** (2026-09-04, the ADR-0056 census across three categories).
    When `learning_loop` became a mechanism enum, the cross-category split was already
    sitting in the cells: harnesses span the whole range — `background` (hermes-agent,
    codex, qwen-code), `in-loop` (claude-code), `proposed` (warp and gemini-cli, both
    of which *built* autonomous write paths and then put a human commit gate in front,
    warp going as far as deprecating a shipped auto-write path) — while the memory
    products occupy exactly one position: every set category-5 cell, plus ecc in
    category 6, is `background`, auto-applying out-of-loop (ai-memory auto-approves
    its own wiki edits by default; mem0 extracts with no human in the loop; memos'
    cascade auto-applies when mounted). The asymmetry has a clean incentive reading:
    an independent memory product that required human commits would surrender the
    "your agent just remembers" pitch that is the type's entire sales surface, so
    write governance concentrates in the layer whose product does not depend on
    writes happening — the harness. Corollary for anyone running the supply side:
    with auto-apply universal among vendors, `write_admission` (evidence-gated ·
    scored · unfiltered) is the only control standing between a session and the
    store, which is why that key and `injection_trust_boundary` carry the category's
    security weight (conclusions 8 and 13's governance thread, now with a
    population-level census behind it). →
    [ADR-0056](../adrs/0056-learning-loop-mechanism-enum.md) ·
    [`tools/5-memory/README.md`](../tools/5-memory/README.md) § Open questions ·
    [issue #13](https://github.com/leandromineti/ai-assisted-coding/issues/13)
