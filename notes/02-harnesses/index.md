# Category 2 — Harnesses

`checked: 2026-08-19`

Loop + context assembly + permission model + UI. See
[`../../taxonomy.md`](../../taxonomy.md).

The prevailing mid-2026 read: the frontier models have converged enough that **the harness
now decides most of the day-to-day experience**. That claim is worth testing here rather
than repeating.

## Inventory

Two axes, recorded separately — an earlier version of this index grouped by a single
"surface" bucket, which forced multi-surface tools into one label and conflated
web-as-interface with remote-as-execution:

- **Surfaces** — where you interact: terminal, IDE, desktop, web. Multi-valued, because
  the serious products are converging on all of them.
- **Execution** — how it runs: `local` (synchronous, on your machine, you watch) vs.
  `async-remote` (the agent runs elsewhere and reports back).

| Harness | Maker | Surfaces | Execution | One-line |
|---------|-------|----------|-----------|----------|
| [**Claude Code**](claude-code.md) | Anthropic | terminal · desktop · web · IDE | local + async (web) | Deep extension surface (skills, hooks, subagents, plan mode) — the conventions the field's category 5 descends from. **Observation-only report 2026-08-17** (closed; no source): third learning-loop mechanism shape (in-loop agent-written memory), first verified worktree cell, dual category-3 relation (binds worktrees locally, bundles cloud sandbox). |
| [**OpenCode**](opencode.md) | Anomaly | terminal · desktop · IDE | local | Open source (MIT). 75+ providers, LSP-aware, stores no code or context. Nine per-model prompts. |
| [**Codex CLI**](codex.md) | OpenAI | terminal (+ desktop launcher) | local | Vendor-native; leads Terminal-Bench 2.1. The Rust bet is *security*, not speed: OS sandboxes compiled into the binary, pre-main process hardening, PTC in sandboxed V8. WorldState diff-append context. Cloud Codex is its async-remote sibling. Deep-dived 2026-07-30. |
| [**Gemini CLI → Antigravity CLI**](gemini-cli.md) | Google | terminal | local | Individual free tier ended 2026-06-18 during the Antigravity transition. |
| [**Aider**](aider.md) | open source | terminal | local | Git-native: commits per change, repo-map context. Opinionated, but the opinions aren't portable — see the stress test. |
| **Grok Build** | xAI | terminal | local | Ships Grok 4.5 in a first-party CLI. |
| **Cursor** | Anysphere → **SpaceX/xAI** | IDE · terminal (Cursor CLI) | local + async (Cloud Agent handoff) | Being acquired for $60B (announced 2026-06-16, closing Q3 2026). ~$2.6B ARR. Grok 4.5 was trained on its session data. The sharpest example of category 1↔2 consolidation. *(2026-08-19, docs-route — closed source)* Cursor CLI widens the row on both axes: a terminal agent (Agent/Plan/Ask modes) with a non-interactive mode for scripts/CI and handoff of a running session to Cloud Agents — the vendor joins the all-surfaces-both-modes convergence below. |
| **Windsurf** | — | IDE | local | IDE-embedded agent. |
| [**Cline**](cline.md) | open source | IDE · terminal | local | Started as a VS Code extension; grew `apps/cli/`, an SDK, and its own `evals/` suite. BYO model. |
| [**Continue**](continue.md) | open source | IDE (VS Code + JetBrains) | local | Two IDEs over a shared core — the only harness here forced to abstract its own UI. BYO model. |
| **GitHub Copilot** | GitHub/Microsoft | IDE · web | local + async (coding agent) | The incumbent; agent mode moved it from completion to loop. |
| **Devin** | Cognition | web | async-remote | Autonomous agent that bundles its own execution environment (category-3 bleed). |
| **Jules** | Google | web | async-remote | Async repo-level agent. |
| **Cloud Codex** | OpenAI | web | async-remote | Hosted counterpart to the CLI. |
| [**Warp**](warp.md) | Warp (warpdotdev) | terminal · desktop · web (wasm) | local + async (cloud runs) | A terminal that became a harness — and then an orchestrator of other harnesses: Claude Code, Codex, Gemini CLI, and OpenCode are selectable backends for its child agents. AGPL-3.0, source-opened 2026-04-28. **Deep-dived 2026-08-19**: the embedding index turned out to back a single tool, not context assembly (axis 1 below, answered); the loop is client-iteration/server-policy — even BYOK keys ship to Warp's backend; child harnesses launch with their guardrails disabled (`--dangerously-*` across the board) while Warp's own commands face a six-level permission chain. |
| **DeepSeek Harness** (`dsh`) | DeepSeek | web (locally served UI) | local | Registered 2026-08-18, README level only — no report yet. Vendor-native, open source (MIT, TypeScript), in *developer preview*: "everything is a plugin" on the Cordis framework, launched as a local web UI (`npx @deepseek-ai/dsh web`). 159.6k stars in **five days** (created 2026-08-13; fetched 2026-08-18) — the fastest adoption ramp in the study. Already a memory-type install target (memos ships a `dsh` plugin with background capture + auto-recall, per its stub). Backlog: issue #19. |
| **Pi** (`earendil-works/pi`) | Earendil Works | terminal (TUI) | local | Registered 2026-08-19, README + GitHub-API level — no report yet. Open source (MIT, TypeScript), created 2025-08-09; 93.8k stars *(fetched 2026-08-19)*. Both a harness and an SDK: the `pi-coding-agent` CLI sits on published packages (`pi-agent-core` runtime, `pi-ai` multi-provider client, `pi-tui`) — a "self-extensible coding agent" atop an agent toolkit. Distinctive position: **ships no built-in permission system**, recommending container isolation instead — axis 2 below deliberately collapsed into axis 4. Sighted four times as an integration target of tracked tools before ever being registered here: gsd-core install target, haft experimental adapter, ai-memory hooks+MCP support, mem0's dedicated `pi-agent-plugin` (all at those reports' pins in [`comparisons/tools.md`](../../comparisons/tools.md)). Backlog: issue #28. |
| [**hermes-agent**](hermes-agent.md) | Nous Research | terminal · desktop · web · IDE (ACP) · ~20 messaging platforms | local + async (gateway daemon, cron, serverless backends) | Personal agent with a coding *posture*, not a coding harness. Autonomous learning loop (interval-gated review fork + idle curator). Deepest category-3 bleed in the set (8 terminal backends). Category 2 confirmed at read time (spec-kit installs into `~/.hermes/skills`). |

Star counts live in [`comparisons/tools.md`](../../comparisons/tools.md) — measured via
the GitHub API and dated (`stars_at`), never hand-kept here where they'd drift.

Note what the two-axis view surfaces that the old buckets hid: **every major vendor
harness now spans multiple surfaces and both execution modes** (Claude Code and Copilot
already do; Codex does via its cloud sibling). Convergence on "all surfaces, both modes"
looks like the trajectory — the single-surface rows are either young, niche, or
deliberately minimal.

A harness's *environment bindings* — which category-3 environments it can attach to (host,
worktree, container, remote sandbox) — are recorded in each report's frontmatter as
`environments`. That's bleed, not merger: the environments themselves stay independently
distributed category-3 entities (see the scope note in
[`../../taxonomy.md`](../../taxonomy.md)).

## Candidates

Sighted-but-not-ingested harnesses live in the cross-category
[candidates ledger](../candidates.md) (first entry: qwen-code, 2026-08-18).

## What actually differentiates a harness

Feature lists mislead here. The axes that seem to matter:

1. **Context assembly** — what gets loaded, when, and what gets dropped. Reportedly Claude
   Code's edge is loading *less* but using it better. *(2026-08-11)* Warp is the first
   surveyed harness to build a real **embedding index** of the codebase (semantic and naive
   chunkers, incremental re-index on changed files) rather than relying on grep and
   model-driven search — an outlier worth a deep-dive, since whether that index actually
   feeds the prompt is the difference between a genuine counter-position and a search tool.
   *(2026-08-19, deep-dive: it's the search tool.)* The traced chain ends in a tool result —
   the only automatic contribution is a `{name, path}` pointer, and retrieved chunks carry
   zero surrounding context lines. **No tracked harness holds the indexed-context-assembly
   position**; the axis's most sophisticated retrieval machinery sits on the grep side of
   its own line. [`warp.md`](warp.md).
2. **Permission model** — how much it does without asking, and how that's configured.
3. **Extension surface** — whether category 5 and 4 can attach at all (hooks, skills, MCP).
4. **Isolation story** — which category-3 environment it assumes.
5. **Failure behavior** — what it does when it's wrong, which is where the real cost lives.
6. **Cache economics as a design constraint** *(added 2026-07-30)* — whether prompt-cache
   discipline is an optimization or the architecture's governing rule. Evidence it
   deserves its own axis: exp-01 found cache reads *dominating* framework spend (30–50×
   baseline, invisible in aggregates), and hermes-agent designs its entire prompt around
   cache warmth — three explicit cache tiers, date-only timestamps, a git snapshot that's
   allowed to go stale rather than shatter the prefix, mode flips deferred to next
   session ("per-conversation prompt caching is sacred" is its stated design law).
   Correctness-vs-cache-warmth tradeoffs are a harness position, not an implementation
   detail.

   *(2026-08-12, from hermes' drift check — the axis gains a structural tension, not
   just an exemplar.)* Upstream moved the **skills index out of the stable band** on
   2026-08-03, because the agent writes and patches its own skills mid-session, so every
   autonomous skill write was invalidating the entire cached prefix in front of it. The
   harness that states cache sacredness as a design law had its *own flagship feature*
   breaking that law, unnoticed at our read and theirs. Generalize it: **a self-modifying
   agent and a byte-stable prompt prefix are in structural tension**, and it surfaces
   wherever the agent's write path crosses its own cache tiers. Any harness pairing an
   autonomous learning loop with cache discipline inherits the problem — which makes
   "where does the agent's own output land in the prompt?" a design question worth asking
   of every tool on this axis, not a hermes quirk.
   [`hermes-agent.md`](hermes-agent.md).

## What category 2 has absorbed — the category-4 feature set, checked against harnesses

*(Added 2026-08-18, systematizing [conclusion 8](../../README.md). This is a mechanism
table, not a checkbox grid — the "feature lists mislead here" warning above applies to
itself. Vocabulary: the nine category-4 `workflow_features` keys from the
[feature taxonomy](../cross-cutting/feature-taxonomy.md); grades per
[ADR-0011](../../adrs/0011-graded-gate-enforcement.md)/[0012](../../adrs/0012-layer-2-feature-set.md).)*

For each mechanism the workflow-framework category sells, what do tracked harnesses
already do natively — and who enforces it?

| Category-4 key | Harness-native instances (verified) | Grade of the native form |
|---|---|---|
| `measured_gates` | **3✓ / 4✗** after the 2026-08-19 Warp deep-dive settled the probe's undecidable cell: hermes `verification_stop` (native policy, `engine`); codex stop-hook veto (`hook`); claude-code Stop-hook exit-2 (`hook` — a user-configured surface, empty by default); verified absent in opencode (4-trigger surface, none at stop), cline, continue, **and Warp** — the 2026-08-18 "loop server-side" premise was half wrong: iteration is client-side, an exhaustive turn-end sweep found only advisory chips, and the enforcement point is ungated ([warp.md](warp.md)) | `engine` / `hook` — but these are *gates*, not *measured* gates: the evidence bar is "ran something fresh", not a hidden verifier ([cross-cutting](../cross-cutting/index.md)). And the probe shows the leg does NOT generalize: native default-on policy exists in exactly one tracked harness |
| `process_gates` | **≥4** — permission approval at tool dispatch is universal machinery: hermes `tools/approval.py`, codex `SafetyCheck::AskUser` inside an OS sandbox, opencode `Permission.ask`, claude-code's plan-approval gate, Warp's six-level `can_autoexecute_command` chain. *(2026-08-19, Warp deep-dive — two cracks in "universal":)* Warp's `AgentDecided` path makes the **model an authority inside the gate** (a model-authored `is_risky: false` self-authorizes, and preempts the redirection guard), and the machinery stops at the process boundary — child harnesses launch with their own gates disabled ([warp.md](warp.md)) | `engine` — compiled chokepoints, above every tracked framework's `prose` |
| `context_isolation` | **6/6** checked harnesses ship `subagents: true`; claude-code adds per-subagent worktree isolation; hermes budgets subagents separately (50 iterations) | native machinery; frameworks can only instruct or hook it (GSD's exit-2 guard is the strongest framework-side form) |
| `parallel_orchestration` | **3** — hermes `delegate_task` parallel batch; codex `tools/parallel.rs` + `agent-graph-store`; Warp's fan-out with *rival harnesses as selectable backends* | native; the category's frameworks either lack it (BMAD: banned; spec-kit: reverted) or drive it from outside the loop (bmad-loop, gsd) |
| `retrospectives` | **3✓ / 1✗** as the `learning_loop` column — hermes on-by-default background fork, codex stable-but-off pipeline, claude-code in-loop memory, Warp verified manual-only | mechanism shapes diverge; enum promotion tracked in issue #13 |
| `state_store` | universal at **session** scope — codex rollout + WorldState replay, hermes FTS5 session store, opencode event-sourced inputs, Warp versioned memory store | native, but session-scoped: no harness ships *workflow*-scoped state (sprint boards, epic ledgers) — that remains framework territory |
| `intent_pipeline` | **thin** — plan artifacts exist (codex collaboration-mode templates, claude-code plan files with an approval gate) but no staged requirements→implementation pipeline | **not absorbed** — the SDD spine remains category 4's own |
| `format_gates` | **1** — codex `apply_patch` with a formal grammar; below the two-instance bar | **not absorbed** (yet) |
| `deterministic_engine` | trivially true of every harness — the loop *is* a program | non-discriminating at category 2; the key only separates tools within category 4 |

Three readings of the table:

- **The enforcement inversion.** The category-4 arc's headline question was "who enforces
  the gate?", and its answer was: almost always the model ([ADR-0011](../../adrs/0011-graded-gate-enforcement.md) —
  every tracked framework's gates grade `prose` or `script`; the only `engine`-graded
  measured/process gates live in bmad-loop, *outside* its framework). The harness rows
  above grade `engine`/`hook` natively. The framework category's hardest problem is the
  harness category's default posture.
- **What is NOT absorbed is a coherent remainder, not a lag.** The three unabsorbed
  keys are exactly the SDD spine — staged intent artifacts, artifact-structure gates,
  workflow-scoped state machines. Harnesses absorb *mechanisms* (gates, isolation,
  memory, fan-out) and leave *methodology* (what artifact comes next and why) alone.
  Conclusion 8 claimed the four absorbed legs and never these — the table confirms the
  boundary sits where the prose said it did.
- **The H8 tension, previously unremarked.** [Design principle H8](../../design-principles.md)
  says a good harness keeps its core a narrow waist and ships capability at the edges
  as data. Absorption is the counter-motion: every mechanism above is core growth. The
  tracked harnesses split visibly — codex ships gates as *hook surface* (waist-shaped:
  the mechanism is an extension point) while hermes ships `verification_stop` as *loop
  policy* (core growth). Whether absorbed mechanisms arrive as extension surfaces or as
  core code may be the next differentiation axis this list needs — it is the same
  engine-vs-prose fork, one category down.

Baseline duty (issue #17): any harness-vs-harness A/B must inventory these rows for
both arms before attributing an effect — the exp-03 rider ("net of what the category-2
harness already does") generalized from gates to the full table.

## Open questions

- Does the Cursor acquisition mean vertical integration (model tuned on harness telemetry)
  produces a durable advantage, or is it a one-off data moat?
- Every harness listed supports MCP. Does that make category 5 genuinely portable in practice,
  or only in principle?
- Is "the harness decides the experience" true, or a claim that survives because nobody
  benchmarks the model independently of the harness?
- ~~Have the frontier models really converged?~~ **The portable harnesses split three ways
  (measured 2026-07-28), so treat this as genuinely contested, not settled either way:**
  - **opencode** maintains nine bespoke per-model prompts (~1,256 lines, zero shared
    substantive lines between the Anthropic and GPT variants; one variant exists solely to
    forbid parallel tool calls) — implicit claim: models differ enough to need different
    driving. [`opencode.md`](opencode.md).
  - **cline** runs one ~35-line prompt per *mode*, model-independent — **after building
    and dismantling a per-family prompt registry** (deleted `families/next-gen-models/`
    tree, vestigial `isNextGenModelFamily` with no callers). A retreat is directional
    evidence that the per-model gain didn't pay — though the SDK rewrite is a confound.
    [`cline.md`](cline.md).
  - **continue** runs ~15 lines per mode and delegates to user-space rules — the null
    hypothesis: the system prompt barely matters. [`continue.md`](continue.md).
  - **hermes-agent** (added 2026-07-30) stakes out a *fourth* position: one shared
    prompt plus small per-family appendices (~4.4KB — tool-use enforcement for
    `gpt/codex/gemini/gemma/grok/glm/qwen/deepseek`, plus OpenAI/Grok and Google
    execution-discipline blocks; `agent/prompt_builder.py:309–470`). Notably, the
    patch list covers every major family *except* Anthropic's — the appendices
    correct deviations from Claude-default behavior.
    [`hermes-agent.md`](hermes-agent.md).
  - **codex** (added 2026-07-30) is the *fifth* data point, from the vendor-native
    pole: model instructions swap per model slug inside its WorldState — per-model
    prompting applied to one vendor's own model family. Even where portability isn't
    the goal, "one prompt fits all models" isn't what the vendor itself practices.
    [`codex.md`](codex.md).

  My earlier framing ("if convergence were real, opencode's maintenance burden would be
  irrational") was too strong: cline paid that burden and concluded it *was* irrational.
  What would actually settle this: an eval of one model under all three regimes — which is
  exactly what [PR #13 on llm-coding-benchmark](https://github.com/akitaonrails/llm-coding-benchmark/pull/13)
  makes runnable for the opencode case.
- Is "all surfaces, both execution modes" really where every serious harness ends up? The
  inventory table above suggests so; re-check the single-surface rows in six months.
