---
name: continue
category: 2
surfaces: [ide, terminal]   # VS Code + JetBrains over a shared core; `terminal` CORRECTED 2026-08-27 (issue #35 probe) — `extensions/cli/` ships `@continuedev/cli`, bin `cn`, with its own permissions/ subsystem and a headless mode, and it is present AT THE PIN (package.json, 5522c6f44). The 2026-07-28 survey read the prompt path and missed it; the pin does not move (rule 4b)
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
  tool_approval: policy  # 2026-08-27 targeted probe at pin 5522c6f44 (issue #35). The strongest shape in the set after gemini-cli's, and a THREE-value policy — disabled > allowedWithPermission > allowedWithoutPermission, hierarchy stated in source (gui/src/redux/thunks/evaluateToolPolicies.ts:55). Base policy resolves user setting → the tool's own `defaultToolPolicy` → `DEFAULT_TOOL_SETTING = "allowedWithPermission"` (gui/src/redux/slices/uiSlice.ts:34), then every call is re-evaluated against its PARSED ARGUMENTS via a `tools/evaluatePolicy` round trip into core (packages/terminal-security for shell, core/tools/policies/fileAccess.ts for reads). Two properties worth the words: the dynamic result is CLAMPED so it can only tighten, never loosen (:59-64), and an evaluator error resolves to `disabled` (:46-49) — fail-closed. One carve-out reads the other way: edit tools short-circuit to allowedWithoutPermission before any lookup (:26-28), the gate delegated to the diff-review UI
  headless_approval: allow  # 2026-08-27, same probe and pin — and the most literal instance of the key yet, because the flip is conditioned on nothing but the absence of a human: `getDefaultToolPolicies(isHeadless)` pushes `{tool:"*", permission:"allow"}` plus Bash-allow in headless where the TUI branch pushes `ask` for both (extensions/cli/src/permissions/defaultPolicies.ts:30-37); upstream states it in prose (permissions/README.md:16). NOT total, and the qualification is a THIRD mechanism the enum does not name: Edit/MultiEdit/Write stay pinned `ask` by first-match-wins, and headless does not decide them — it WITHDRAWS them, filtering ask-tools out of the schema sent to the model (stream/handleToolCalls.ts:187-190). An `ask` that still arrives (only via dynamic evaluation) is denied (stream/streamChatResponse.helpers.ts:124-127). So: fail-open for everything the model can still call, by making the rest uncallable
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

## Permission gate — targeted probe 2026-08-27 (not a re-read; the pin is unchanged)

Executed for [issue #35](https://github.com/leandromineti/ai-assisted-coding/issues/35),
which asked only whether `tool_approval` was present. It is, and the probe returned two
things the survey had missed.

**The gate is three-valued, argument-aware, and clamped.** `disabled >
allowedWithPermission > allowedWithoutPermission`, with the hierarchy written down in
source (`gui/src/redux/thunks/evaluateToolPolicies.ts:55`). Each tool ships its own
`defaultToolPolicy` — reads, globs, greps and `viewDiff` are `allowedWithoutPermission`;
edits, `runTerminalCommand`, `fetchUrlContent` are `allowedWithPermission` — and a user
setting overrides it, falling back to `DEFAULT_TOOL_SETTING = "allowedWithPermission"`
(`gui/src/redux/slices/uiSlice.ts:34`). Then every call is re-evaluated against its *parsed
arguments* over an IPC round trip into core (`tools/evaluatePolicy`), which is where
`packages/terminal-security` inspects the actual command string and
`core/tools/policies/fileAccess.ts` inspects the actual path.

Two properties are worth stating separately, because they are the ones the
[`tool_approval` registry note](../../comparisons/feature-registry.md#harnesses) says
decide whether a dynamic evaluator is a strength or a hole:

- **The dynamic result can only tighten.** A base policy of `allowedWithPermission` cannot
  be widened to `allowedWithoutPermission` by the evaluator, and `disabled` cannot be
  overridden at all (`:56-64`). Same monotonic-clamp property as qwen-code's, arrived at
  independently and for a non-model evaluator.
- **An evaluator failure resolves to `disabled`** (`:46-49`) — fail-closed on its own
  error path, the condition most likely to be reached in practice.

One carve-out runs the other way and is easy to miss: **edit tools short-circuit to
`allowedWithoutPermission` before any policy lookup happens** (`:26-28`). The gate is not
absent for edits, it is relocated — into the diff-review UI, which is a human gate of a
different species (process, not dispatch) and the same substitution aider makes for a
different reason.

**Headless flips the wildcard, and that is the whole finding.**
`getDefaultToolPolicies(isHeadless)` builds one list and appends one of two endings: in a
TUI, `Bash: ask` and `*: ask`; headless, `Bash: allow` and `*: allow`
(`extensions/cli/src/permissions/defaultPolicies.ts:30-37`). Nothing else about the
invocation changes — the absence of a human is itself the condition. Upstream states it in
prose one directory up (`permissions/README.md:16`).

It is not a blanket open door, and the qualification is a mechanism the `deny | allow` enum
has no word for. `Edit`, `MultiEdit` and `Write` stay pinned `ask` by first-match-wins, and
headless mode does not *decide* them — it **withdraws** them, filtering every `ask` tool out
of the schema sent to the model (`stream/handleToolCalls.ts:187-190`). An `ask` that still
arrives (reachable only through dynamic evaluation, per the source's own comment) is denied
(`stream/streamChatResponse.helpers.ts:124-127`). So the cell reads `allow`: fail-open for
everything the model can still call, achieved by making the rest uncallable. Neither
aider's fail-open-by-EOF-default nor gemini-cli's fail-closed-by-policy-default works this
way.

**And the probe found a surface.** `extensions/cli/` ships `@continuedev/cli`, bin `cn`,
with `permissions/`, `serve`, and `review` commands — present at this report's pin
(`package.json`, `5522c6f44`), not drift. The 2026-07-28 survey read the prompt path and
recorded `surfaces: [ide]`; corrected to `[ide, terminal]` above, pin unmoved. The row now
matches cline's exactly: **both IDE-origin harnesses in the set grew a CLI**, and the two
took opposite headless decisions once they had one.

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
