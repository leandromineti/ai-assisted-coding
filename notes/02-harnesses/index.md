# Layer 2 — Harnesses

`checked: 2026-08-12`

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
| **Claude Code** | Anthropic | terminal · desktop · web · IDE | local + async (web) | Deep extension surface (skills, hooks, subagents, plan mode). |
| [**OpenCode**](opencode.md) | Anomaly | terminal · desktop · IDE | local | Open source (MIT). 75+ providers, LSP-aware, stores no code or context. Nine per-model prompts. |
| [**Codex CLI**](codex.md) | OpenAI | terminal (+ desktop launcher) | local | Vendor-native; leads Terminal-Bench 2.1. The Rust bet is *security*, not speed: OS sandboxes compiled into the binary, pre-main process hardening, PTC in sandboxed V8. WorldState diff-append context. Cloud Codex is its async-remote sibling. Deep-dived 2026-07-30. |
| [**Gemini CLI → Antigravity CLI**](gemini-cli.md) | Google | terminal | local | Individual free tier ended 2026-06-18 during the Antigravity transition. |
| [**Aider**](aider.md) | open source | terminal | local | Git-native: commits per change, repo-map context. Opinionated, but the opinions aren't portable — see the stress test. |
| **Grok Build** | xAI | terminal | local | Ships Grok 4.5 in a first-party CLI. |
| **Cursor** | Anysphere → **SpaceX/xAI** | IDE | local | Being acquired for $60B (announced 2026-06-16, closing Q3 2026). ~$2.6B ARR. Grok 4.5 was trained on its session data. The sharpest example of layer 1↔2 consolidation. |
| **Windsurf** | — | IDE | local | IDE-embedded agent. |
| [**Cline**](cline.md) | open source | IDE · terminal | local | Started as a VS Code extension; grew `apps/cli/`, an SDK, and its own `evals/` suite. BYO model. |
| [**Continue**](continue.md) | open source | IDE (VS Code + JetBrains) | local | Two IDEs over a shared core — the only harness here forced to abstract its own UI. BYO model. |
| **GitHub Copilot** | GitHub/Microsoft | IDE · web | local + async (coding agent) | The incumbent; agent mode moved it from completion to loop. |
| **Devin** | Cognition | web | async-remote | Autonomous agent that bundles its own execution environment (layer-5 bleed). |
| **Jules** | Google | web | async-remote | Async repo-level agent. |
| **Cloud Codex** | OpenAI | web | async-remote | Hosted counterpart to the CLI. |
| [**Warp**](warp.md) | Warp (warpdotdev) | terminal · desktop · web (wasm) | local + async (cloud runs) | A terminal that became a harness — and then an orchestrator of other harnesses: Claude Code, Codex, Gemini CLI, and OpenCode are selectable backends for its child agents. AGPL-3.0, source-opened 2026-04-28. The only indexed context assembly in the set (embedding chunkers, consent-gated). Surveyed 2026-08-11. |
| [**hermes-agent**](hermes-agent.md) | Nous Research | terminal · desktop · web · IDE (ACP) · ~20 messaging platforms | local + async (gateway daemon, cron, serverless backends) | Personal agent with a coding *posture*, not a coding harness. Autonomous learning loop (interval-gated review fork + idle curator). Deepest layer-5 bleed in the set (8 terminal backends). Layer 2 confirmed at read time (spec-kit installs into `~/.hermes/skills`). |

Star counts live in [`comparisons/tools.md`](../../comparisons/tools.md) — measured via
the GitHub API and dated (`stars_at`), never hand-kept here where they'd drift.

Note what the two-axis view surfaces that the old buckets hid: **every major vendor
harness now spans multiple surfaces and both execution modes** (Claude Code and Copilot
already do; Codex does via its cloud sibling). Convergence on "all surfaces, both modes"
looks like the trajectory — the single-surface rows are either young, niche, or
deliberately minimal.

A harness's *environment bindings* — which layer-5 environments it can attach to (host,
worktree, container, remote sandbox) — are recorded in each report's frontmatter as
`environments`. That's bleed, not merger: the environments themselves stay independently
distributed layer-5 entities (see the scope note in
[`../../taxonomy.md`](../../taxonomy.md)).

## What actually differentiates a harness

Feature lists mislead here. The axes that seem to matter:

1. **Context assembly** — what gets loaded, when, and what gets dropped. Reportedly Claude
   Code's edge is loading *less* but using it better. *(2026-08-11)* Warp is the first
   surveyed harness to build a real **embedding index** of the codebase (semantic and naive
   chunkers, incremental re-index on changed files) rather than relying on grep and
   model-driven search — an outlier worth a deep-dive, since whether that index actually
   feeds the prompt is the difference between a genuine counter-position and a search tool.
2. **Permission model** — how much it does without asking, and how that's configured.
3. **Extension surface** — whether layer 3 and 4 can attach at all (hooks, skills, MCP).
4. **Isolation story** — which layer-5 environment it assumes.
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

## Open questions

- Does the Cursor acquisition mean vertical integration (model tuned on harness telemetry)
  produces a durable advantage, or is it a one-off data moat?
- Every harness listed supports MCP. Does that make layer 3 genuinely portable in practice,
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
