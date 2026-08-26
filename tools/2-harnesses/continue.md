---
name: continue
category: 2
surfaces: [ide]   # VS Code + JetBrains over a shared core
execution: local
maker: Continue
url: https://github.com/continuedev/continue
license: Apache-2.0
access: open-source
stack: [TypeScript, React]
version: v1.3.40-vscode-11-g5522c6f44
commit: 5522c6f44
first_commit: 2023-05-23
stars: 35166
stars_at: 2026-07-28
read_at: 2026-07-28
depth: survey   # prompt/context subsystem read closely; rest of the codebase skimmed
harness_features:
  mcp: true
  turn_end_gates: false  # 2026-08-18 targeted probe at pin 5522c6f44: no stop-hook/should_block/turn-end machinery in core/
  ptc: false             # 2026-08-18 targeted probe at pin: no PTC mechanism in core/ (only vendored-model noise matched)          # core/context/mcp/MCPConnection.ts
  plan_mode: true    # DEFAULT_PLAN_SYSTEM_MESSAGE (measured)
  rules_files: true  # core/llm/rules/getSystemMessageWithRules.ts
  model_agnostic: true
---

# Continue

Open-source IDE-embedded harness for VS Code and JetBrains, bring-your-own-model.

## The distinguishing bet

**Portability across IDEs** (no other tool in the set maintains two IDE extensions over a
shared core) — and, on the prompt question, the most radical position measured here:
**the system prompt barely matters**.

**Measured 2026-07-28 (commit `5522c6f44`):** one default system message per *mode* —
chat / agent / plan — in `core/llm/defaultSystemMessages.ts` (91 lines for all three; the
agent message is ~15 lines of codeblock-formatting rules). No model conditioning anywhere
in the prompt path: `getSystemMessageWithRules.ts` contains **zero** references to the
model, and grep finds no `model.includes(...)` branching in message construction. The
defaults are user-overridable config (`baseAgentSystemMessage`, `core/llm/index.ts:151`)
and the file even ships its own GitHub URL as a constant, inviting users to read and
replace it.

The three-way contrast with its portable peers is the finding: opencode maintains nine
bespoke per-model prompts (~1,256 lines); cline runs one ~35-line prompt per mode after
*dismantling* a per-family registry; continue runs ~15 lines and delegates the rest to
user-space rules. Same problem, three deliberate answers.

## Main features

_TODO_

## Stack & repo shape

TypeScript with React — 1429 `.ts`, 345 `.tsx` across 3058 tracked files. The tree splits
`extensions/vscode/` from `extensions/intellij/` over a shared core, plus a `binary/` package
with per-platform builds (darwin/linux, arm64/x64), implying a compiled sidecar process that
both IDEs talk to.

**21569 commits since 2023-05-23** — the most commits and second-oldest project in the set.

## Architecture

_TODO — source unread. The core/host boundary is the interesting part: it's the only place
in this set where a harness had to abstract its own UI._

## Bleed

_TODO_ — supports MCP (category 6). The `binary/` sidecar is arguably a category-3 concern
(process isolation) solved incidentally.

## Cost model

Open source; metered inference against whichever provider you configure.

## Surprises

**How little prompt there is.** ~15 lines of agent system message where opencode spends
95–155 per model and Claude Code spends far more. Continue is betting that tool
definitions, rules files, and retrieval do the work the others do with prose — or that
the prose never did much work at all. Either way it's the null hypothesis of the
per-model-prompt debate, running in production.

**The Anthropic provider sends deprecated extended thinking unconditionally** (2026-08-26,
verified at this report's pin `5522c6f44`; a targeted read for
[issue #40](https://github.com/leandromineti/ai-assisted-coding/issues/40), not a re-read).
`core/llm/llms/Anthropic.ts` `convertArgs()`:

```ts
thinking: options.reasoning
  ? { type: "enabled" as const,
      budget_tokens: options.reasoningBudgetTokens ?? DEFAULT_REASONING_TOKENS }
  : undefined,
```

There is **no model-id check on this branch at all** — every Anthropic model gets
`thinking: {type: "enabled", budget_tokens: N}` whenever reasoning is switched on. Per
Anthropic's per-model configuration table (read 2026-08-26, cited in
[`../1-models/claude-opus-5.md`](../1-models/claude-opus-5.md) § Reasoning surface),
`"enabled"` is **rejected with a 400 on Claude 4.7 and later** — which is Fable 5, Opus 5,
Opus 4.8, Opus 4.7, and Sonnet 5, i.e. all three current frontier models. It remains
correct for the 4.5-era models (Haiku 4.5, Sonnet 4.5) where extended thinking is the only
mode, and works-but-deprecated on the 4.6 pair.

This is the sharpest instance of the pattern in [issue #40](https://github.com/leandromineti/ai-assisted-coding/issues/40)
and it inverts the going assumption: **continue is a per-vendor-adapter harness, the shape
predicted to be structurally immune.** Per-vendor adapters do protect against confusing one
vendor's surface for another's — they do nothing about a vendor deprecating its own
parameter, because there is no model-version dimension in the design at all. opencode and
cline at least *look* at the model id and get the version wrong; this branch never looks.

Every affected model shipped before the 2026-07-28 read (Fable 5 2026-06-09, Sonnet 5
2026-06-30, Opus 5 2026-07-24), so it is a live gap at the pin. Not traced: whether a
default config reaches this branch without the user explicitly enabling reasoning.

## Open questions

- What exactly lives in the shared core vs. the per-IDE extension? That boundary is the
  clearest available evidence of what a harness *is*, minus its UI.
- Why a compiled binary sidecar rather than running in-process?
- 21.5k commits and it's still a category-2 tool — where did that volume go?
