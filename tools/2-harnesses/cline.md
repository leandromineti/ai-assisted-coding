---
name: cline
category: 2
surfaces: [ide, terminal]   # started as a VS Code extension; the tree carries apps/cli/
execution: local
maker: Cline
url: https://github.com/cline/cline
license: Apache-2.0
access: open-source
stack: [TypeScript, React]
version: nightly-main-20260728125218-dc175c73a8dd
commit: dc175c73a
first_commit: 2024-07-05
stars: 65138
stars_at: 2026-07-28
read_at: 2026-07-28   # drift-checked 2026-08-16 at 574b8eb45 without re-reading (rule 4b) — all claims corroborated; upstream deleted the vestigial classifier this report flagged; pin deliberately not moved
depth: survey   # prompt/context subsystem read closely; rest of the codebase skimmed
harness_features:
  mcp: true            # apps/vscode MCP configuration UI, McpPromptRow
  turn_end_gates: false  # 2026-08-18 targeted probe at pin dc175c73a: no stop-hook/should_block/turn-end machinery anywhere in src; attempt_completion's feedback loop is a HUMAN gate (process), not a native verification veto
  ptc: false             # 2026-08-18 targeted probe at pin: no execute_code/code-mode/programmatic mechanism in src
  subagents: true      # sdk .../tools/team/subagent-prompts.ts, AgentConfigLoader
  plan_mode: true      # PLAN_MODE_INSTRUCTIONS + switch_to_act_mode tool (measured)
  rules_files: true    # {{CLINE_RULES}} slot in the system prompt; filenames not yet verified
  model_agnostic: true
  evals: true          # evals/ with its own ARCHITECTURE.md
---

# Cline

Open-source IDE-embedded harness, originally a VS Code extension, bring-your-own-model.

## Drift check — 2026-08-16 (not a re-read; the pin is unchanged)

224 commits / 799 files since the read. Every claim below is corroborated, and one of them
in the strongest way available: **upstream deleted the vestigial code this report
identified as vestigial.**

- **The dismantled registry stays dismantled.** `git ls-tree | grep system-prompt` returns
  **zero** files at `dc175c73a` and zero at HEAD. No per-model prompt architecture came
  back.
- **The vestigial organ was excised.** The report called `isNextGenModelFamily` a
  "vestigial organ of the dismantled design" with no non-test callers. It now has **zero
  occurrences anywhere in the tree**, removed by `2a0dd197b` — *"chore(vscode): remove dead
  next-gen model classifier"* (#12887). Upstream reached the same conclusion the archaeology
  did, and used the same word.
- **One prompt, still no model parameter.** `buildClineSystemPrompt` survives (moved
  `:110` → `:132`) and still takes only `ClineSystemPromptOptions`.
- **A near-counterexample, checked and dismissed.** That options type carries
  `providerId`, which looks like model-conditioned prompting. It is not: `providerId` feeds
  `isClineProvider()`, which gates only whether **workspace metadata** is injected
  (`:147`, `:152`, `:187`) — a hosted-provider distinction, not a model-family branch. It
  was also present at the pin (`:107`), so it is not drift. Recorded because a reader
  scanning for "does anything vary by model?" will hit it and deserve the answer.

**Still open — the *why*.** The report left two readings of the retreat (the per-model gain
didn't pay vs. the SDK rewrite killed the variants as collateral) and noted a pickaxe query
had timed out on the blobless clone. Method note for the next attempt: `git log -S <symbol>`
scoped to `<pin>..HEAD` is cheap and works — it is the *full-history* pickaxe that is
expensive. That found the deletion commit above in seconds, but the original dismantling
predates the pin, so the question stands.

## The distinguishing bet

Model-agnostic like opencode — but it answers the per-model-prompt question the **opposite
way**, and it did so *after trying both*.

**Measured 2026-07-28 (commit `dc175c73a`):** the current system prompt is built by
`buildClineSystemPrompt` (`sdk/packages/shared/src/prompt/cline.ts:110`), which takes
**no model parameter at all**. Variation is by *mode* — default vs. YOLO
(`sdk/packages/shared/src/prompt/system.ts`), plus a plan-mode contract — never by model.
One prompt for Claude, GPT, Gemini, and everything else.

The interesting part is the archaeology. Cline **used to have a per-model-family prompt
architecture**: the deleted tree (visible at migration commit `791d23899`, "Move vscode to
apps") contained `src/core/prompts/system-prompt/` with a `PromptRegistry`, a
`PromptBuilder`, and `families/next-gen-models/gpt-5.ts`,
`families/local-models/compact-system-prompt.ts` — the same shape as opencode's nine
prompt files. Today `git ls-files | grep system-prompt` returns **zero files**, and the
family-detection helpers (`isNextGenModelFamily` in
`apps/vscode/src/utils/model-utils.ts:135`) survive with **no non-test callers** —
vestigial organs of the dismantled design.

So cline is a *directional* data point: it built opencode's bet, lived with it, and
retreated to one prompt. Two readings, both plausible: (a) the per-model gain didn't
justify the maintenance — evidence *for* model convergence; (b) the SDK rewrite favored
simplicity and the variants died as collateral. The git history could distinguish these;
the blobless clone makes that search expensive (a pickaxe query timed out), so it stays
open.

## Main features

_TODO_

## Stack & repo shape

TypeScript with React — 1977 `.ts` and 597 `.tsx` across 3429 tracked files. Notably no
longer just an extension: the tree carries `apps/cli/`, `apps/cline-hub/`, an `sdk/`, and
`evals/`. It ships **three separate `ARCHITECTURE.md` files** (`sdk/`, `evals/`, and a
desktop sidecar), which is more architectural self-documentation than anything else in the
set.

6667 commits since 2024-07-05.

## Architecture

_TODO — source unread. Start from `sdk/ARCHITECTURE.md`, which is the rare case of a repo
explaining itself._

## Bleed

_TODO_ — supports MCP (category 6). The `evals/` directory is a cross-cutting verification
concern living inside a category-2 product, which is worth documenting.

## Cost model

Open source; metered inference against whichever provider you configure.

## Surprises

1. **It un-built the per-model prompt system.** Expected either "never tried it" or
   "still has it" — found a dismantled registry with vestigial family-detectors instead.
   Retreats are rarer than adoptions in public codebases, and more informative.
2. A harness shipping its own `evals/` suite is notable given how under-served
   verification is across the field. (Whether the evals drove the prompt retreat is an
   open question worth chasing — that would be the first documented case of harness
   evals actually settling a design bet.)
3. **Reasoning capability is decided by enumerated model-id substrings, and the
   enumeration is a generation behind** (2026-08-26, verified at this report's pin
   `dc175c73a`; a targeted read for [issue #40](https://github.com/leandromineti/ai-assisted-coding/issues/40),
   not a re-read of the report). `apps/vscode/src/shared/utils/reasoning-support.ts`
   carries two predicates, and both miss the current lineup:

   - `isClaudeOpusAdaptiveThinkingModel()` matches `claude-fable-5` plus the literal
     version set `["4-6", "4.6", "4-7", "4.7", "4-8", "4.8"]`. **Claude Opus 5 and Sonnet 5
     match neither**, though both are adaptive-only models that reject
     `thinking: {type: "enabled"}` with a 400 (Anthropic's per-model configuration table;
     see [`../1-models/claude-opus-5.md`](../1-models/claude-opus-5.md) § Reasoning
     surface). Both shipped **before** this pin was read — Sonnet 5 on 2026-06-30, Opus 5
     on 2026-07-24, against a 2026-07-28 read — so this is a live gap at the pin, not
     hindsight.
   - `supportsReasoningEffortForModel()` matches `gemini`, `gpt`, `openai/o…`, `grok` —
     **no Anthropic model at all**, so no effort control is offered for any Claude.

   A third code path disagrees with cline's own front end: `buildSdkProviderConfig`
   (`apps/vscode/src/sdk/sdk-api-handler.ts`) forwards effort only when it is
   `low | medium | high`, while the CLI's `ACTIVE_REASONING_EFFORTS`
   (`apps/cli/src/utils/reasoning.ts`) accepts `xhigh` as well. **Selecting `xhigh` in the
   CLI therefore sends no effort at all** — the model silently runs at its own default.
   Neither code path has any spelling of `max`, the *default* on GLM-5.3 and Kimi K3.

   Not traced to the wire: `thinkingBudgetTokens` is handed to cline's SDK gateway as
   `reasoning.max_tokens`, and whether that becomes a 400-producing `budget_tokens` on a
   4.7-or-later Claude depends on translation code outside this clone. The predicates
   above are stated as read; the wire consequence is not claimed.

## Open questions

- What does `evals/` actually measure, and could that method be borrowed for this repo's
  own verification problem?
- An extension that grew a CLI, an SDK, a hub, and a desktop sidecar — is that convergence
  on a platform, or scope creep?
