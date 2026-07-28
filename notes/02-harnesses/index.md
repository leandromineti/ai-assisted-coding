# Layer 2 — Harnesses

`checked: 2026-07-28`

Loop + context assembly + permission model + UI. See
[`../../taxonomy.md`](../../taxonomy.md).

The prevailing mid-2026 read: the frontier models have converged enough that **the harness
now decides most of the day-to-day experience**. That claim is worth testing here rather
than repeating.

## Terminal

| Harness | Maker | One-line |
|---------|-------|----------|
| **Claude Code** | Anthropic | CLI + desktop + web + IDE extensions. Deep extension surface (skills, hooks, subagents, plan mode). ~135k GitHub stars. |
| **Codex CLI** | OpenAI | Vendor-native OpenAI loop; leads Terminal-Bench 2.1. ~94k stars. |
| **OpenCode** | Anomaly | Open source (MIT), ~180k stars — the most-starred agent. 75+ providers via Models.dev, LSP-aware, multi-session, shareable sessions, stores no code or context. |
| **Gemini CLI → Antigravity CLI** | Google | ~105k stars. Individual free tier ended 2026-06-18 during the Antigravity transition. |
| **Aider** | open source | Git-native: commits per change, repo-map context. Opinionated, but the opinions aren't portable — see the stress test. |
| **Grok Build** | xAI | Ships Grok 4.5 in a first-party CLI. |

## IDE-embedded

| Harness | Maker | One-line |
|---------|-------|----------|
| **Cursor** | Anysphere → **SpaceX/xAI** | Being acquired for $60B (announced 2026-06-16, closing Q3 2026). ~$2.6B ARR. Grok 4.5 was trained on its session data. The sharpest example of layer 1↔2 consolidation. |
| **Windsurf** | — | IDE-embedded agent. |
| **Cline** | open source | VS Code extension; BYO model. |
| **Continue** | open source | VS Code / JetBrains; BYO model. |
| **GitHub Copilot** | GitHub/Microsoft | The incumbent; agent mode moved it from completion to loop. |

## Async / cloud

| Harness | Maker | One-line |
|---------|-------|----------|
| **Devin** | Cognition | Autonomous agent that bundles its own execution environment (layer 5). |
| **Jules** | Google | Async repo-level agent. |
| **Cloud Codex** | OpenAI | Hosted counterpart to the CLI. |
| **Claude Code on web** | Anthropic | Hosted sessions from the browser. |

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
