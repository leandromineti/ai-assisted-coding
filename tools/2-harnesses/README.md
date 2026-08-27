# Category 2 — Harnesses

`checked: 2026-08-26`

Loop + context assembly + permission model + UI. See
[`../../docs/tool-taxonomy.md`](../../docs/tool-taxonomy.md).

The prevailing mid-2026 read: the frontier models have converged enough that **the harness
now decides most of the day-to-day experience**. That claim is worth testing here rather
than repeating.

## What we assess here

The assessed block is **`harness_features:`, 14 keys** (2026-08-26): `mcp`, `lsp`, `hooks`,
`turn_end_gates`, `tool_approval`, `skills`, `subagents`, `ptc`, `plan_mode`,
`rules_files`, `model_agnostic`, `session_sharing`, `evals`, `learning_loop`. They sort
under the category's three components — the loop (`subagents`, `plan_mode`,
`turn_end_gates`, `ptc`), context assembly (`skills`, `rules_files`, `learning_loop`), and
the permission gate (`tool_approval`) — with the rest describing reach and portability.
All are presence-claims except `turn_end_gates`, which is graded engine \| hook \| script \|
prose ([ADR-0011](../../adrs/0011-graded-gate-enforcement.md)/[0012](../../adrs/0012-layer-2-feature-set.md)),
because *who enforces* a gate turned out to matter more than whether one exists.

This is the presence half only, and the warning below applies to it: the matrix answers
"does it ship this?", never "does it pay?" — the mechanism sections further down are where
that second question is argued.

The other half is **13 transcription fields** — `maker`, `license`, `access`, `stars`,
`first_commit`, `version`, `commit`, `stack`, `surfaces`, `residency`, `execution`,
`environments`, `environment_relation` — facts copied from a dated source rather than judged.
`residency` joined 2026-08-27 (ADR-0047) when the resident-agent strain reached its second
verified instance.

Both halves are read as **seven groups** — Identity · Provenance · Shape · Environment
binding · Extension points · Control gates · Operations — each opening with what it is
about and how its keys read together: [`feature-registry.md` § Harnesses](../../comparisons/feature-registry.md#harnesses).

Definitions:
[`comparisons/feature-registry.md`](../../comparisons/feature-registry.md). Values:
[`comparisons/features.md § Harnesses`](../../comparisons/features.md#harnesses-category-2).
A key is set **only** when verified in source or official docs — omitted means "not
checked", `false` means "checked and absent", and both are claims.

## Inventory

Two axes, recorded separately — an earlier version of this index grouped by a single
"surface" bucket, which forced multi-surface tools into one label and conflated
web-as-interface with remote-as-execution:

- **Surfaces** — where you interact: terminal, IDE, desktop, web, messaging. Multi-valued,
  because the serious products are converging on all of them. `messaging` joined 2026-08-27
  (ADR-0047); the same ADR split *residency* — does the agent outlive the conversation — out
  of the execution axis, and two harnesses here are `resident`.
- **Execution** — how it runs: `local` (synchronous, on your machine, you watch) vs.
  `async-remote` (the agent runs elsewhere and reports back).

| Harness | Maker | Surfaces | Execution | One-line |
|---------|-------|----------|-----------|----------|
| [**Claude Code**](claude-code.md) | Anthropic | terminal · desktop · web · IDE | local + async (web) | Deep extension surface (skills, hooks, subagents, plan mode) — the conventions the field's category 6 descends from. **Observation-only report 2026-08-17** (closed; no source): third learning-loop mechanism shape (in-loop agent-written memory), first verified worktree cell, dual category-3 relation (binds worktrees locally, bundles cloud sandbox). |
| [**OpenCode**](opencode.md) | Anomaly | terminal · desktop · IDE | local | Open source (MIT). 75+ providers, LSP-aware, stores no code or context. Nine per-model prompts. |
| [**Codex CLI**](codex.md) | OpenAI | terminal (+ desktop launcher) | local | Vendor-native; leads Terminal-Bench 2.1. The Rust bet is *security*, not speed: OS sandboxes compiled into the binary, pre-main process hardening, PTC in sandboxed V8. WorldState diff-append context. Cloud Codex is its async-remote sibling. Deep-dived 2026-07-30. |
| [**Gemini CLI → Antigravity CLI**](gemini-cli.md) | Google | terminal · IDE (ACP) | local | Individual free tier ended 2026-06-18 during the Antigravity transition. **Deep-dived 2026-08-25** (pin moved to HEAD): the stub's long-context bet falsified — the source bets on context *conservation* (SWEBench-guarded prompt doctrine, retrieval by subagent delegation, embeddings dead code); the gate is a ~12.8k-line tiered TOML policy engine (ASK_USER default, fail-closed headless) with a one-way LLM-authored policy checker (CONSECA); hooks reproduce Claude Code's Stop-hook contract field-for-field (a shipped migrator maps Stop→AfterAgent) while `AGENTS.md` is refused; the Antigravity migration ships *inside* the product (builtin skill + uncappable server-controlled banner); commit rate −93% from the March peak yet releases daily — an agent-maintained repo in managed succession. |
| [**Aider**](aider.md) | Aider-AI | terminal · web (local Streamlit GUI) | local | Git-native: commits per change, repo-map context. Opinionated, but the opinions aren't portable — see the stress test. **Deep-dived 2026-08-27**, and it is the set's counterfactual: the oldest harness here (first commit 2023-04-03) and **dormant** — `pushed_at` 2026-05-22, 97 days before the read, 336 commits in the last 12 months against 8,393 in the prior 12, 96% by one author, and no status statement anywhere. Three findings move category rows. **(1) It falsifies axis 1's standing claim** — a persistent on-disk tree-sitter symbol index, `nx.pagerank` over a weighted file-reference graph, injected as *source lines in a user message every turn*, measured at 71% of the assembled prompt at defaults. **(2) No MCP, verified across 13,138 commit messages and every path ever added** — the first ✗ in a uniform column, and the taxonomy's pre-registered reach trigger. **(3) `turn_end_gates: engine`, default-ON and genuinely measured** — zero-config `--auto-lint` runs tree-sitter + `compile()` + a real flake8 subprocess on every edit. Not a tool-dispatch loop at all: `functions = None`, no tool schema ever sent, a 13-line turn engine capped at a hard-coded 3 reflections. |
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
| [**DeepSeek Harness** (`dsh`)](dsh.md) | DeepSeek | web (locally served UI) | local | Vendor-native, MIT, TypeScript, developer preview. **Deep-dived 2026-08-24** (issue #19 executed; 190.9k stars at read — the 2026-08-18 "created 2026-08-13" registration corrected: `first_commit` 2026-06-10, the five days is the star ramp, not the code). The "everything is a plugin" bet survives adversarial reading — the loop itself is a bundle row behind a replaceable-but-singleton factory seam. Three findings that move category rows: turn-end gating where *data decides, not listener order* (`engine` grade, a third shape); **no per-tool permission model at all** — the gate is a compiled per-call OS sandbox (own published Landlock launcher + hand-built Windows runner) with model-*initiated* one-shot escalation, `allowed-once` the only grant; and KV-cache discipline as a CI-gated README requirement. Runs competitors' hook configs (unmodified Claude Code `hooks.json`, Codex dialect) and spawns Codex/Claude Code as subagent providers. Native memory verified absent (the memos `dsh` adapter is third-party, riding the pre-step surface). |
| [**Pi**](pi.md) | Earendil Works | terminal (TUI) | local | Open source (MIT, TypeScript), created 2025-08-09. Both a harness and an SDK: the `pi-coding-agent` CLI sits on published packages (`pi-agent-core`, `pi-ai` multi-provider client, `pi-tui`) — a "self-extensible coding agent". **Deep-dived 2026-08-26** (issue #28 executed): the distinguishing bet is a narrow-waist (H8) harness taken furthest in the set — a stock loop with **zero active interception points** (78 example extensions ship, exactly one auto-loads, and it registers no hooks), no budgets or loop detection anywhere, and the class literally named `AgentHarness` is a throwing stub (operative runtime is the older `Agent`). **`tool_approval: false` — the second verified absent after dsh, but the opposite philosophy**: dsh replaces the gate with a compiled sandbox, pi with *nothing* (no permission system, no path containment, runs as the launching user). `environment_relation` is the **null case** (confinement declined, delegated to external containerization by docs). Two findings that touch standing notes: on Anthropic **OAuth** pi runs a source-labelled "stealth mode" impersonating Claude Code (identity block + renamed tools + `claude-code` beta header) — the subscription-auth-is-official-clients note from the non-vendor pole; and `--auth-token` is a **second silently-inert shipped auth control** after gemini-cli's dropped checker. Best-in-set cache discipline (clock-free prefix, default-on breakpoints, an inline dollar-denominated cache-miss meter). Sighted four times as an integration target before registration (gsd-core, haft, ai-memory, mem0). |
| [**hermes-agent**](hermes-agent.md) | Nous Research | terminal · desktop · web · IDE (ACP) · ~20 messaging platforms | local + async (gateway daemon, cron, serverless backends) | Personal agent with a coding *posture*, not a coding harness. Autonomous learning loop (interval-gated review fork + idle curator). Deepest category-3 bleed in the set (8 terminal backends). Category 2 confirmed at read time (spec-kit installs into `~/.hermes/skills`). |
| [**Qwen Code**](qwen-code.md) | Alibaba (Qwen) | terminal · IDE (VS Code, Zed, ACP) · desktop · web · 11 messaging channels | local + resident (daemon, cron, channels) | Deep-dived 2026-08-27 as a **divergence study**: forked from Gemini CLI v0.8.2, independent since, and now ahead of its parent on four keys the parent verified as absent (`lsp`, `model_agnostic`, `learning_loop`, AGENTS.md-by-default) while behind on `evals` (0 vs 37). Second verified instance of the resident shape. |

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
[`../../docs/tool-taxonomy.md`](../../docs/tool-taxonomy.md)).

## Candidates

Sighted-but-not-ingested harnesses live in the cross-category
[candidates ledger](../candidates.md) — three today: ZCode, kimi-code, orca. qwen-code was the ledger's first entry (2026-08-18) and left it by promotion on 2026-08-27, which is what promotion means (ADR-0031): the report supersedes the row.

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
   its own line. [`warp.md`](warp.md). *(2026-08-25, gemini-cli deep-dive — the claim
   survives its third test, with a boundary caveat:)* the CLI's embedding path is dead
   code (zero production callers) and retrieval is delegated to a read-only subagent —
   but a **server-side RAG index** demonstrably exists behind the Code Assist backend
   (`ragStatus`/scored snippets arrive on the response stream; the harness only observes
   them). The position is unheld *by any harness*; Google holds it at the model surface
   instead, invisible to a clone-only read. [`gemini-cli.md`](gemini-cli.md).

   ***(2026-08-27, aider deep-dive — the claim FALLS on its fourth test, and the falsifier
   is the oldest tool in the set.)*** The negative claim above was always scoped to what
   had been read, and what had not been read was the harness whose defining feature is an
   index. aider holds the position outright, and the chain ends in bytes rather than a
   pointer: a **persistent on-disk symbol index** (`.aider.tags.cache.v4`, diskcache/SQLite,
   mtime-invalidated) built by tree-sitter from 58 `.scm` query files → **real
   `nx.pagerank`** over a graph whose nodes are files and whose edges are
   `referencer → definer`, weighted `mul * sqrt(num_refs)` with ×50 for a file in the chat
   → a **budget enforced by binary search** → **the actual source lines** of each ranked
   definition, elided with `⋮`, injected as a **user message every single turn**, with no
   model request. Measured on the published artifact against aider's own 691-file repo:
   **110 files and 25,253 bytes at the 4096-token default — 71% of the whole assembled
   prompt.** Warp's index ends in a `{name, path}` tool result; aider's ends in the prefix.
   **So the axis has a genuine third position after all — statically-derived ranked
   content — and the reason nobody held it was a sampling artifact of reading only
   2025–2026 tool-dispatch harnesses.**

   Two riders, both measured, that keep the finding honest:

   - **The index needs a human seed.** At a 1024-token budget with an empty chat, the
     ranking selects 33 files of which **20 are language test fixtures**, and omits
     `base_coder.py`, the repo's own core file. Add that one file to the chat and the map
     collapses to 13 files, 10 of them its actual collaborators. The human's `/add` is not
     file selection — it is the PageRank's **personalization vector**. Cold-start ranking is
     poor; warm ranking is sharp.
   - **It collides with cache discipline, and aider resolved the collision by disabling its
     own feature.** See axis 6 below. [`aider.md`](aider.md).
2. **Permission model** — how much it does without asking, and how that's configured.
3. **Extension surface** — whether categories 4, 5, and 6 can attach at all (hooks, skills, MCP).
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

   *(2026-08-27, aider deep-dive — the tension generalizes beyond self-modifying agents,
   and one harness hit it three years earlier and fixed it.)* The structural statement
   above named the *agent's write path* as the crossing point. aider shows the wider form:
   **any volatile artifact inside the cached prefix does this**, whether the agent wrote it
   or not. aider's repo map sits at cache breakpoint 2 (`chat_chunks.py:28-41`), is
   recomputed every turn, and is ranked by personalization seeded from *every word of the
   current user message* — so a different question produces a different map and shatters
   breakpoints 2 and 3 plus the entire conversation history between them.

   aider diagnosed it and fixed it in two lines (`main.py:954-955`): enabling
   `--cache-prompts` silently flips `--map-refresh` from `auto` to `files`, dropping the
   per-query terms from the cache key. **The fix is a feature downgrade nobody is told
   about** — RUN-confirmed, the entire disclosure is one word in the startup banner
   (`auto refresh` → `files refresh`). So the two flagship features are mutually exclusive
   in their full form.

   The generalized principle for this axis: **retrieval quality and prefix stability are in
   direct conflict whenever retrieval is query-conditioned**, and every harness that adds
   per-query context assembly inherits the trade. aider is the only tracked harness that
   found it unaided — and it paid for the fix in the feature it is known for.
   [`aider.md`](aider.md).

## What category 2 has absorbed — the category-4 feature set, checked against harnesses

*(Added 2026-08-18, systematizing [conclusion 8](../../README.md). This is a mechanism
table, not a checkbox grid — the "feature lists mislead here" warning above applies to
itself. Vocabulary: the nine category-4 `workflow_features` keys from the
[feature taxonomy](../../docs/feature-taxonomy.md); grades per
[ADR-0011](../../adrs/0011-graded-gate-enforcement.md)/[0012](../../adrs/0012-layer-2-feature-set.md).)*

For each mechanism the workflow-framework category sells, what do tracked harnesses
already do natively — and who enforces it?

*Coverage caveat (2026-08-27), stated rather than left silent:* the qwen-code read added a
twelfth harness and re-scored only the two rows it actually assessed —
`context_isolation` (`subagents` verified ✓) and `retrospectives`/`learning_loop` (verified
✓). The gate rows — `measured_gates`, `process_gates`, `format_gates` — are
`workflow_features` judgements that read did **not** make, so their counts still describe
the harnesses scored before it. Incrementing them from a category-2 deep-dive would have
been a guess wearing a number.

| Category-4 key | Harness-native instances (verified) | Grade of the native form |
|---|---|---|
| `measured_gates` | **3✓ / 4✗** after the 2026-08-19 Warp deep-dive settled the probe's undecidable cell: hermes `verification_stop` (native policy, `engine`); codex stop-hook veto (`hook`); claude-code Stop-hook exit-2 (`hook` — a user-configured surface, empty by default); verified absent in opencode (4-trigger surface, none at stop), cline, continue, **and Warp** — the 2026-08-18 "loop server-side" premise was half wrong: iteration is client-side, an exhaustive turn-end sweep found only advisory chips, and the enforcement point is ungated ([warp.md](warp.md)). **dsh (2026-08-24): a fourth ✓ and a third `engine` shape** — an awaited `agent/turn-stopping` boundary where *data decides, not listener order* (objectors steer messages into the inbox; the loop re-reads it), default-empty like claude-code's Stop surface ([dsh.md](dsh.md)). **gemini-cli (2026-08-25): a fifth ✓ at `hook` grade — and it is Claude Code's Stop-hook contract reproduced field-for-field** (`AfterAgent` halt/re-prompt with `stop_hook_active`, `client.ts:973-1035`), default-armed and empty; its `engine`-grade next-speaker gate exists but is default-OFF at the pin ([gemini-cli.md](gemini-cli.md)). **aider (2026-08-27): a sixth ✓, `engine` grade, and the first that is *measured* in the strict sense** — `--auto-lint` defaults TRUE, and with zero user configuration every edited Python file gets a tree-sitter parse, a real `compile()`, and a `flake8` subprocess whose output becomes the next user message (`base_coder.py:1599-1607` → `linter.py:118-159`). RUN-confirmed on the published artifact, including `F821 undefined name` in *syntactically valid* code — a semantic error catchable only by running a real linter ([aider.md](aider.md)) | `engine` / `hook` — but these are mostly *gates*, not *measured* gates: the evidence bar is "ran something fresh", not a hidden verifier ([cross-cutting](../../docs/README.md)). **aider is the first tracked harness to clear that bar by default**, and it does so with no tool loop at all — so "runs a fresh verifier before the turn can end" turns out to be independent of, and cheaper than, agentic tool dispatch. Its one qualifier: the re-prompt passes a `confirm_ask` that defaults to yes, auto-accepts under `--yes-always`, and returns the default on `EOFError` in every non-interactive mode — a human touchpoint that exists interactively and evaporates everywhere else. Native default-on *policy* still exists in exactly one harness (hermes) |
| `process_gates` | **≥4** — permission approval at tool dispatch is universal machinery: hermes `tools/approval.py`, codex `SafetyCheck::AskUser` inside an OS sandbox, opencode `Permission.ask`, claude-code's plan-approval gate, Warp's six-level `can_autoexecute_command` chain. *(2026-08-19, Warp deep-dive — two cracks in "universal":)* Warp's `AgentDecided` path makes the **model an authority inside the gate** (a model-authored `is_risky: false` self-authorizes, and preempts the redirection guard), and the machinery stops at the process boundary — child harnesses launch with their own gates disabled ([warp.md](warp.md)). *(2026-08-24, dsh deep-dive — "universal" now has a verified counter-instance:)* **dsh ships no per-tool approval at all** — its `tools/pre-execute` default is `allow` and the only gate is a compiled per-call OS sandbox; the sole prompt in a stock run is a model-*initiated* sandbox escalation, and delegation pins children to `approval: 'never'` ([dsh.md](dsh.md)). *(2026-08-26, pi deep-dive — a second absent, no sandbox either:)* **pi ships no permission system and no sandbox** — the loop dispatches as the launching user and defers confinement to external containerization; two absents now, dsh's sandbox-instead vs pi's containment-is-your-problem ([pi.md](pi.md)). *(2026-08-25, gemini-cli deep-dive — the strongest-form instance:)* the gate is **policy data, not code paths** — 38 TOML rules on a five-tier precedence, default ASK_USER interactive / DENY headless, denied tools stripped from the model's schema, blanket session-allows refused for shell-class tools without an args pattern; plus the registry's sharpest presence≠operative specimen — a shipped workspace-confinement checker silently inert (zod dropped a mis-nested TOML key) until one day before the pin ([gemini-cli.md](gemini-cli.md)). *(2026-08-26, pi deep-dive — a SECOND verified absent, and the opposite philosophy from dsh's:)* pi ships **no permission system and no sandbox** (README states it; grep `confirm\|approve\|permission` over core tools → 0) — `bash`/`write`/`edit` dispatch unprompted as the launching user, and confinement is *declined and delegated to external containerization by docs*. So the two absents diverge: **dsh moved the gate down to a compiled sandbox; pi removed it entirely.** The axis is now firmly discriminating ([pi.md](pi.md)). *(2026-08-27, aider deep-dive — the thinnest present gate, and it inverts at the edges:)* seven `confirm_ask` sites stand between model and machine, all flowing through **one boolean function with one modifier bit** — no policy data, no tiers, no risk model, no sandbox beneath. Two properties no other tracked harness has. **(i) `--yes-always` is the SAFE setting**: `explicit_yes_required=True` on the shell gate turns approve-everything into an automatic *"no"* for model-authored commands (`io.py:866-867`, unit-tested), while headless *without* the flag executes them, because `EOFError` is read as "the user pressed Enter" and the default is `"y"` — the absence of a human is read as consent, inverting gemini-cli's headless DENY. **(ii) No escalation state survives the process**: "don't ask again" is a bare in-memory `set()`, so the standard failure mode of accumulated grants cannot occur ([aider.md](aider.md)) | `engine` — compiled chokepoints, above every tracked framework's `prose` |
| `context_isolation` | **9 ✓ / 2 ✗ of 11 checked** (12 category-2 reports; `continue` is the one unchecked). Re-derived 2026-08-27 from frontmatter after the aider read, never incremented by hand — this cell read 9/10 before that read and 7/8 before four reads earlier, which is exactly why it is re-derived each time. **aider is the second ✗, and a different shape from pi's**: its architect/editor path *is* a second model on an isolated history (`cur_messages = []`, `done_messages = []`), but it fails *spawnable* on every count — one child, fixed role, not model-requested, no fan-out, no recursion. A two-stage pipeline, not a fan-out primitive; claude-code adds per-subagent worktree isolation; hermes budgets subagents separately (50 iterations); gemini-cli adds a *structural* depth cap of exactly 1 — `Kind.Agent` tools silently dropped from every child registry (2026-08-25). **pi verified absent from the product** (2026-08-26): no Task/spawn tool in the 8 built-ins; subagents exist only as a manually-symlinked example extension (process-isolated `pi` subprocesses, no depth cap, no budget) | native machinery; frameworks can only instruct or hook it (GSD's exit-2 guard is the strongest framework-side form); pi's ✗ is a minimalist harness declining the fan-out, deferring it to the extension surface |
| `parallel_orchestration` | **3** — hermes `delegate_task` parallel batch; codex `tools/parallel.rs` + `agent-graph-store`; Warp's fan-out with *rival harnesses as selectable backends* | native; the category's frameworks either lack it (BMAD: banned; spec-kit: reverted) or drive it from outside the loop (bmad-loop, gsd) |
| `retrospectives` | **4 ✓ / 5 ✗ of 9 checked** as the `learning_loop` column (re-derived from frontmatter 2026-08-27 after the aider read; three of the twelve reports leave the key unset). qwen-code ✓ (2026-08-27: background extraction + a "dream" consolidation agent, both default-ON and auto-applying — the first ✓ that is both) — hermes on-by-default background fork, codex stable-but-off pipeline, claude-code in-loop memory, Warp verified manual-only; **dsh verified absent entirely** (2026-08-24: no store, no write path — a vendor-native harness *declining* the memory absorption, deferring to third-party MCP/plugin memory, default-off); **gemini-cli a second Warp-shaped ✗** (2026-08-25: background "confucius" extractor exists but default-off AND propose-and-commit — code-jailed `.inbox` writes, extracted skills outside the discovery path, human `/memory inbox` promotion; the deleted `save_memory` tool is an auto-write path *removed*, echoing Warp's deprecated `is_autogenerated`); **pi a fourth ✗ of yet another shape** (2026-08-26: no memory subsystem and no autonomous writer at all — yet the *highest self-authorship ceiling in the set*: an agent asked to "build a skill" writes auto-loading skills/extensions/`SYSTEM.md` to `~/.pi/agent/` with no trust gate and no permission system; human-invited, not self-initiated, so ✗ on the autonomous key but a memory-authority outlier worth the note); **aider a fifth ✗ and the plainest** (2026-08-27: no agent-authored file of any kind, no background writer, no store — its `.aider.chat.history.md` is a human-readable transcript emitted by the terminal-output code, replayed only under `--restore-chat-history` (default `False`) and immediately summarized into ordinary history. A session artifact with opt-in replay, not memory; classified by mechanism rather than by filename, which is what the key requires — [aider.md](aider.md)) | mechanism shapes diverge; enum promotion tracked in issue #13 — dsh's ✗ is absence, pi's is absence-with-a-high-authority-manual-path, aider's is a plain absence in a harness with no write path at all, none is Warp's propose-and-commit |
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
- **The H8 tension, previously unremarked.** [Design principle H8](../../docs/design-principles.md)
  says a good harness keeps its core a narrow waist and ships capability at the edges
  as data. Absorption is the counter-motion: every mechanism above is core growth. The
  tracked harnesses split visibly — codex ships gates as *hook surface* (waist-shaped:
  the mechanism is an extension point) while hermes ships `verification_stop` as *loop
  policy* (core growth). Whether absorbed mechanisms arrive as extension surfaces or as
  core code may be the next differentiation axis this list needs — it is the same
  engine-vs-prose fork, one category down.
- **The model edge is the frontier where nothing is eaten** *(added 2026-08-25,
  backfilling a synthesis first stated in the published article so it is confrontable
  at re-read)*. No tracked harness ships or trains its own weights, and no absorption
  finding in this index or conclusion 8 names the model as a target — the model stays
  the swappable component. Where the frontier is crossed, the traffic runs the other
  way: model vendors treating harnesses as **data instruments** (xAI's acquisition of
  Cursor followed by Grok 4.5 training on its session data —
  [grok-4-5 report](../1-models/grok-4-5.md); hermes' trajectory-export tooling
  openly labeled for training its maker's next models —
  [hermes report](hermes-agent.md)). Falsifier: a tracked harness shipping or
  fine-tuning its own weights would end the asymmetry — the vendor-native harnesses
  (codex, dsh, gemini-cli) are where to watch for it at drift checks.

Baseline duty (issue #17): any harness-vs-harness A/B must inventory these rows for
both arms before attributing an effect — the exp-03 rider ("net of what the category-2
harness already does") generalized from gates to the full table.

## Open questions

- Does the Cursor acquisition mean vertical integration (model tuned on harness telemetry)
  produces a durable advantage, or is it a one-off data moat?
- ~~Every harness listed supports MCP.~~ **False, and it was false before anyone noticed
  (corrected 2026-08-27).** Re-derived from frontmatter: **10 ✓ / 2 ✗, all 12 reports
  checked.** pi was recorded `mcp: false` on 2026-08-26 and this line was not updated;
  aider is the second ✗ (2026-08-27). The miss is worth recording rather than quietly
  fixing — a uniform column is exactly the kind of claim that stops being re-derived once
  it reads as settled.

  **The two absences have different causes, and the difference is the answer to the
  question this bullet was really asking.** pi *has* a tool loop and simply ships no MCP
  client, so MCP would ride an extension — it could gain the column tomorrow. aider has
  **no tool registry at all**: edits are markdown fences parsed by regex, `functions = None`,
  and no tool schema is ever sent. There is no socket for MCP to plug into. So: **MCP is
  genuinely portable across tool-dispatch harnesses, and aider marks the boundary of that
  class** — an edit-format harness cannot host MCP without becoming a different harness.
  The portability is real; its domain is narrower than "harnesses".
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
  - **gemini-cli** (added 2026-08-25) is a *sixth* position, between dsh's one and
    codex's per-slug: exactly **two full prompt bodies switched on model *family***
    (gemini-3+/custom vs legacy — `promptProvider.ts:82`; flash and pro verified
    byte-identical by md5 over the committed snapshot), with rich runtime
    conditioning inside each. Family-granular, not slug-granular, even within one
    vendor's own lineup. [`gemini-cli.md`](gemini-cli.md).
  - **pi** (added 2026-08-26) ties **dsh at the convergence pole: exactly one shared
    prompt body**, zero model/family branching, across ~9 provider API families
    (negative grep over the prompt + session + loop code). The strongest single
    convergence vote in the set — a *multi-provider* client that drives every family
    with one prompt. Two sub-prompt qualifiers, both beneath the prompt-authoring
    code and neither model-keyed: an *auth-mode*-keyed Claude Code identity block prepended on
    Anthropic OAuth (the impersonation seam), and transport-level role/placement
    variation in pi-ai. [`pi.md`](pi.md).
  - **aider** (added 2026-08-27) is an **eighth position on a different axis entirely, and
    the only one with published eval backing**. It varies neither prose nor prompt *body*:
    all **17** `coders/*_prompts.py` modules grepped for model conditionals yield **two
    hits, both TODO comments**. What varies per model is **the edit format** — a 357-entry
    YAML resource (`aider/resources/model-settings.yml`) routing models onto `diff` (289),
    `diff-fenced` (35), `udiff` (4), `whole` (4), `architect` (1) — plus the *message
    shape* (`examples_as_sys_msg` inlines few-shot examples into the system message rather
    than sending real turns; `use_system_prompt: false` emits the system prompt as a
    user+assistant pair; `reminder` chooses trailing-system vs spliced-into-final-user) and
    the *weak model* (66 distinct). **The prose is fixed; the protocol is what differs.**
    [`aider.md`](aider.md).

  **The "no eval backing" clause now carries an asterisk (2026-08-27).** Seven positions
  had none. aider's benchmark harness scores `pct_well_formed` — malformed-edit rate —
  **separately from** `pass_rate_1`/`pass_rate_2` code correctness, and its own README says
  why: it measures *"not just the LLM's coding ability, but also its capacity to edit
  existing code and format those code edits so that aider can save the edits."* Two of the
  14 in-tree result files (`architect.yml`, `code-in-json.yml`) are A/B ablations of
  aider's *own* design decisions rather than model rankings. So exactly one harness has
  published measurements of its own H7 position — and it is the position that says the
  format, not the prose, is the thing to vary. Two caveats before leaning on it: the
  corpus lives in a **separate repo** cloned at setup (not pinned, task counts recoverable
  only from result rows: 223–225 across 69 runs), and the leaderboard configuration runs
  a `--tries 2` test-feedback loop that the **shipped default does not have**
  (`--auto-test` defaults to `False`).

  My earlier framing ("if convergence were real, opencode's maintenance burden would be
  irrational") was too strong: cline paid that burden and concluded it *was* irrational.
  What would actually settle this: an eval of one model under all three regimes — which is
  exactly what [PR #13 on llm-coding-benchmark](https://github.com/akitaonrails/llm-coding-benchmark/pull/13)
  makes runnable for the opencode case.
- Is "all surfaces, both execution modes" really where every serious harness ends up? The
  inventory table above suggests so; re-check the single-surface rows in six months.
