# Layer 2 — Harnesses

`checked: 2026-07-28`

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
| [**Codex CLI**](codex.md) | OpenAI | terminal | local | Vendor-native OpenAI loop; leads Terminal-Bench 2.1. The only Rust harness in the set. Cloud Codex is its async-remote sibling. |
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
| **hermes-agent** | Nous Research | terminal | local *(unverified)* | "The agent that grows with you" — self-improving, skills-based. Backlogged for assessment: [issue #1](https://github.com/leandromineti/ai-assisted-coding/issues/1) (2026-07-28); layer-2 classification to confirm at read time. |

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
   Code's edge is loading *less* but using it better.
2. **Permission model** — how much it does without asking, and how that's configured.
3. **Extension surface** — whether layer 3 and 4 can attach at all (hooks, skills, MCP).
4. **Isolation story** — which layer-5 environment it assumes.
5. **Failure behavior** — what it does when it's wrong, which is where the real cost lives.

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

  My earlier framing ("if convergence were real, opencode's maintenance burden would be
  irrational") was too strong: cline paid that burden and concluded it *was* irrational.
  What would actually settle this: an eval of one model under all three regimes — which is
  exactly what [PR #13 on llm-coding-benchmark](https://github.com/akitaonrails/llm-coding-benchmark/pull/13)
  makes runnable for the opencode case.
- Is "all surfaces, both execution modes" really where every serious harness ends up? The
  inventory table above suggests so; re-check the single-surface rows in six months.
