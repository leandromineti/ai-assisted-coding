---
# PIN MOVED dc175c73a → 787ad1b07 (= tag v4.1.21, the VS Code extension's train) at the
# 2026-09-24 release re-read (rule 4b: two Opus tracts — release substance + provenance,
# per-claim confrontation at both pins — main-session spot-verification; window 761 commits).
# Five release trains share one monorepo tag stream (VS Code v4.1.21, CLI 3.0.65, SDK 0.0.86,
# desktop 0.0.35): the tag names one of them. Own-pin defects corrected in place.
name: cline
category: 2
surfaces: [ide, terminal]   # started as a VS Code extension; the tree carries apps/cli/
execution: local
maker: Cline
url: https://github.com/cline/cline
license: Apache-2.0
access: open-source
stack: [TypeScript, React]
version: v4.1.21   # the VS Code extension; the CLI at this tag is `cline@3.0.65` on npm (apps/cli/package.json names `@cline/cli`, a build-time name the publish script renames — publish-npm.ts:33), SDK 0.0.86, desktop 0.0.35
commit: 787ad1b07
first_commit: 2024-07-05
stars: 69228
stars_at: 2026-09-24   # gh api; 65,138 at 2026-07-28
read_at: 2026-09-24   # v4.1.21 release re-read (§ Release re-read); survey 2026-07-28 @ dc175c73a, drift-checked 2026-08-16 at 574b8eb45 (a 2026-08-06 commit) without re-reading (rule 4b) — all claims corroborated; upstream deleted the vestigial classifier this report flagged; pin deliberately not moved
depth: survey   # prompt/context subsystem read closely; rest of the codebase skimmed
harness_features:
  mcp: true            # apps/vscode MCP configuration UI, McpPromptRow
  context_retrieval: model-driven  # ADR-0055, cell set 2026-09-04 probe-pass at the pin: the historic tree-sitter definition-lister is gone from live source (only a CHANGELOG fossil and an unrelated lockfile entry — git grep -li tree-sitter @ dc175c73a over sdk/+apps/ → 0); search is a ripgrep-backed tool executor (sdk/packages/core/src/extensions/tools/executors/search.ts) the model calls; file-indexer.ts is a filename-only cache feeding that tool's scope and @mention autocompletion, never ranked content RE-CHECKED 2026-09-24: the tree-sitter grep now returns 1 file, apps/cli/src/tui/components/chat-entry.tsx (TUI syntax highlighting, not retrieval) — cell holds, the zero does not
  context_compaction: [llm-summarize, truncate]  # ADR-0055, cell set 2026-09-04 probe-pass at the pin: Auto Compact (default-on) is LLM summarization (agentic-compaction.ts, default strategy "agentic", compaction.ts:277); for models that don't support it the SDK falls back automatically to basic-compaction.ts, which folds history into a templated block "without a summarizer model" — upstream docs call it rule-based context truncation (docs/features/auto-compact.mdx) SURFACE NOTE 2026-09-24: "default-on" is a surface property — the SDK refuses to build a compactor unless `enabled === true` (compaction.ts:291); both shipped surfaces set it (compaction-mode.ts:36-37, sdk-compaction.ts:70). Same library-plus-front-ends shape as the approval gate
  turn_end_gates: engine  # REGRADED false → engine 2026-09-24, and the old cell was wrong AT ITS OWN PIN (rule-1b vocabulary miss: the 08-18 probe searched other harnesses' words — should_block, stop hooks — on a subject that spells it `completionPolicy`). Call site sdk/packages/agents/src/agent-runtime.ts:908-914 @ 787ad1b07 (:689-694 @ dc175c73a): when a model turn produces zero tool calls, `getCompletionReminderMessages()` can inject a [SYSTEM] re-prompt and `continue` the run instead of `finishRun`. Two producers, both auto-mounted by cline's own runtime-builder.ts:804-849: `requireCompletionTool` (when `submit_and_exit`, the aliased `attempt_completion`, is in the tool set — yolo preset) and a `teamCompletionGuard` ("Do NOT stop until all tasks are completed") when `enableAgentTeams` — ON in the CLI (apps/cli/src/main.ts:1090 `!isYoloMode`), OFF in VS Code (cline-session-factory.ts:1088) and ACP. Qualification: it re-prompts on obligation bookkeeping (unfinished team tasks / missing terminal tool), never on work quality — weaker than hermes' verification_stop at the same grade. Surface-split like the approval gate, in the OPPOSITE direction. The old note stands for what it measured: attempt_completion's feedback loop is a HUMAN gate (process), not a native verification veto
  ptc: false             # 2026-08-18 targeted probe at pin: no execute_code/code-mode/programmatic mechanism in src
  tool_approval: policy  # 2026-08-27 targeted probe at pin dc175c73a (issue #35): a real dispatch gate in the SDK — agent-runtime.ts:1403-1412 routes any tool whose policy says `autoApprove === false` through requestToolApproval before execution, with terminal and desktop-IPC front ends (apps/cli/src/utils/approval.ts:102). The qualification belongs on the cell: the check is `=== false`, and the SDK's own default is to leave it UNSET — "the SDK defaults unlisted tools to auto-approved" (apps/vscode/src/sdk/sdk-tool-policies.ts:7, upstream's words). The gate exists because each surface turns it on: VS Code forces autoApprove:false for the read/edit/command/web/MCP families (same file, :25-37); the CLI does NOT — `defaultToolAutoApprove = true` (apps/cli/src/main.ts:868), so a stock CLI run prompts for nothing until the user toggles it RE-READ 2026-09-24: the split is FOUR surfaces, not two, and 2–2 — VS Code ON (sdk-tool-policies.ts:25-28 forces autoApprove:false), CLI TTY OFF (main.ts:892 defaultToolAutoApprove = true, now resolved through a persisted-settings term, startup-settings.ts:21-31), CLI ACP mode ON (acpAgent.ts:785-786), desktop ("Cline Code", 29 tagged releases in the window, still under apps/examples/) OFF (constants.ts:35 autoApproveTools: true); all four postures were already true at dc175c73a. Engine unchanged: agent-runtime.ts:2390 `=== false`, presets.ts:142 `{}` unless yolo, "The SDK defaults unlisted tools to auto-approved" verbatim across 761 commits. Hooks shipped in the window (9 file-config points) and are STOP-ONLY: every SDK hook routes through applyStopControl, whose body is `throw new ControlledStopError` (:2681-2691); afterRun discards its return — a hook can end a run, never veto a stop
  headless_approval: deny  # 2026-08-27, same probe and pin. Fail-closed twice over: no TTY on stdin OR stdout returns `approved: false` before any prompt is drawn (apps/cli/src/utils/approval.ts:68-73), and the SDK denies again when no approval callback is configured at all (agent-runtime.ts:1429-1434). Distinct from the CLI's auto-approve default above, which is not headless-conditioned — cline answers the same way in a TTY, so this cell reads the gate's resolution, not the stock run's behaviour MOVED at 787ad1b07: approval.ts:72-77, agent-runtime.ts:2416-2421, byte-identical
  subagents: true      # sdk .../tools/team/subagent-prompts.ts, AgentConfigLoader
  plan_mode: mode      # PLAN_MODE_INSTRUCTIONS + switch_to_act_mode tool (measured)
  rules_files: true    # {{CLINE_RULES}} slot in the system prompt; filenames not yet verified FILENAMES VERIFIED 2026-09-24: `.clinerules` and `AGENTS.md` (user-instruction-config-loader.ts:550-561, :674 @ 787ad1b07)
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

## Permission gate — targeted probe 2026-08-27 (not a re-read; the pin is unchanged)

Executed for [issue #35](https://github.com/leandromineti/ai-assisted-coding/issues/35).
`tool_approval: policy` (*label corrected 2026-09-24; the body carried the pre-ADR-0053 boolean*), but the interesting fact is *where the gate lives*, because cline is
the only harness here that ships its loop as a library and therefore has to answer the
question twice.

**The SDK's default is auto-approve, and it says so.** `agent-runtime.ts:1398-1412` resolves
a per-call policy (`*` merged with the tool's own entry) and calls `requestToolApproval`
only when `policy.autoApprove === false`. Strict equality against an *optional* field: an
unset policy is not a gate. `createToolPoliciesWithPreset` returns `{}` for every preset
except `yolo` (`sdk/packages/core/src/extensions/tools/presets.ts:137-142`), so an embedder
who configures nothing gets a loop with no permission model. Upstream states the
consequence in its own comment — *"The SDK defaults unlisted tools to auto-approved"*
(`apps/vscode/src/sdk/sdk-tool-policies.ts:7`).

**The gate is therefore a property of each surface, not of the engine.** The two shipped
surfaces disagree:

- **VS Code turns it on.** `buildToolPolicies()` forces `autoApprove: false` across the
  read, edit, command, web-fetch and per-server MCP tool families (`:25-37`), routing them
  into the approval callback, which re-reads the AutoApproveBar settings live so a
  mid-task toggle takes effect on the next call.
- **The CLI turns it off.** `const defaultToolAutoApprove = true`
  (`apps/cli/src/main.ts:868`) becomes `{"*": {autoApprove: true}}`, and the TUI reads that
  same cell back as "yolo enabled" (`runtime/format.ts:30`). A stock `cline` run prompts
  for nothing until the user flips the toggle, which then re-derives the policy table from
  a hardcoded safe-list of seven read-only tools
  (`runtime/tool-policies.ts:3-11`, `:30-48`).

**`headless_approval: deny`, fail-closed twice over.** When the gate *is* on and no human
can answer, `requestTerminalToolApproval` returns `approved: false` before drawing anything
if either stdin or stdout is not a TTY (`apps/cli/src/utils/approval.ts:68-73`), and the
SDK denies independently when no approval callback was configured at all
(`agent-runtime.ts:1429-1434`) — the embedder who half-configures a policy without a
front end gets refusal, not execution.

Worth keeping the two facts apart, because collapsing them would give the wrong cell.
Cline's CLI auto-approves by default **in a TTY too**; that is a product default, not a
headless decision. Continue's, probed the same day, is the opposite on both counts: its
gate is on by default and its wildcard is rewritten `ask → allow` *because* the run is
headless. Same key, same category, opposite failure modes — which is the pair the key was
admitted for.

## Release re-read — v4.1.21 (2026-09-24; pin dc175c73a → 787ad1b07)

Two Opus tracts at survey scale, load-bearing claims re-run at both pins. Window
`git rev-list --count dc175c73a..v4.1.21` = **761**, 0 merges, 646 subjects PR-suffixed;
`git diff --stat` 1,996 files, +411,114 / −81,169; tracked files 3,429 → 4,116. Authors 35,
top three 80% (the lead 60%); `apps/examples` is the #2 directory by churn (482 files, above
`apps/vscode`) because the shipped desktop product lives there. Five release trains under one
tag stream: 191 tags in the window (22 VS Code `v4.1.*`, 19 `cli-v`, 36 `desktop-v`, 105 SDK).
The premise that the CLI had stopped publishing was a naming hole: `@cline/cli` is renamed to
`cline` at publish (`publish-npm.ts:33`), `cline@3.0.65` shipped 2026-09-24T05:55Z with six
platform binary packages; the extension is `4.x`, the CLI `3.x`.

**1. The bet holds, and the one prompt now varies by host.** `buildClineSystemPrompt` still
takes no model parameter (`prompt/cline.ts:155-157`); `isNextGenModelFamily` is still gone; the
dismantled registry stayed dismantled; `isClineProvider` still gates only workspace metadata.
`sdk/packages/shared/src/prompt/system.ts` no longer exists — it split into `system/{act,yolo}.ts`,
the mode variation made literal (a MOVED that a cold citation check would misread as rot).
New: `ClineSystemPromptOptions.planModeSwitchTool` (`cline.ts:146-152`, default true, set false
only by `apps/vscode/src/sdk/cline-session-factory.ts:987`) selects between two plan-mode
texts — cline refuses to vary the prompt by model and has started varying it by surface, the
same axis as the permission finding arriving in a second subsystem. Archaeology corrected at
the pin: the per-model registry's real surface at `791d23899` was `system-prompt/variants/`
(**12** model-family directories), not the two `families/…` files, which sat in the sibling
`system-prompt-legacy/` — the corrected evidence is stronger.

**2. The loop grew a recovery tier; the gate did not move.** `agent-runtime.ts` 1,805 → 2,825
lines, 17 methods added, 0 removed: provider-error retry, context-overflow recovery, and
`retryTruncatedTurnWithCompaction` (the v4.1.21 note's "long replies on local models now
compact and retry once" — a clean note↔diff match). The turn-end gate the old cell denied is
in the `turn_end_gates` cell; the approval engine is byte-identical in its load-bearing lines.

**3. Own-pin corrections.** Four wording defects (a "families" for "variants" path, "the TUI"
for the mistake-limit handler at `runtime/format.ts:17,30` — where the permission wildcard
doubles as an error-recovery policy, "read-only" for a seven-tool `SAFE_AUTO_APPROVE_TOOL_NAMES`
list that includes two user prompts, `submit_and_exit` and `fetch_web_content`, and a body
`tool_approval: true` twenty days after the cell became `policy`); one contradicted inference:
"selecting `xhigh` in the CLI sends no effort" joined two accurate readings through a code path
that does not exist — `buildSdkProviderConfig` is VS Code-only (7 hits, all under
`apps/vscode/src/sdk/`), the CLI passes `xhigh` intact (`reasoning.ts:34-64`), and the real
extension-side gap was closed at `4fa42771a` on **2026-07-29, one day after the pin**
(`sdk-api-handler.ts:92` now accepts `xhigh`). Meanwhile the two model-classifying predicates in
`reasoning-support.ts:8-19` are byte-identical across 761 commits — Opus 5 and Sonnet 5 still
match neither while the same release moved eleven providers' default to Opus 5.5; and a third
path minted since the pin normalises `max` → `xhigh` (`portable-reasoning.ts:48`, absent at
dc175c73a). Audit: with-measure counts 5/5; without 8/9 (the miss was an adjective). Agent
trailers 58 of 761 (7.6%): Claude 27, Cursor 17, Cline 15 — cline's maintainers ship more
Cursor-attributed than Cline-attributed commits, and a workflow strips agent badges.

**Predictions (dated, falsifiable).** **P-1** by 2026-12-24 `apps/examples/desktop-app/` is no
longer the home of the shipped `@cline/code` (moved out, or no `desktop-v*` tag after
2026-11-24) — 60%. **P-2** no npm package `cline@4.x` exists by 2026-12-24 (the trains stay
independent) — 90%. Open, cheap: does the CLI's turn-end gate fire in a stock `npx cline` run?
(rule 8b; `[SYSTEM] You still have team obligations` after a no-tool turn.) Next trigger: the
next `cli-v` minor, or 2026-12-24.

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
