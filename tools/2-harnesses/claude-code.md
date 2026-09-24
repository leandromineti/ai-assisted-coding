---
name: claude-code
category: 2
surfaces: [terminal, desktop, web, ide, messaging]   # messaging ADDED 2026-09-24, docs-route: "How Claude Code works" § Interfaces lists Slack beside terminal, desktop, IDE, claude.ai/code, Remote Control and CI/CD (retrieved 2026-09-24) — the ADR-0047 value, third instance after hermes-agent and qwen-code. Original: in-product statement + docs; terminal OBSERVED directly (this report was written from inside one)
execution: both   # local CLI observed; cloud sessions + claude.ai/code web are the async-remote side (the local client can list/message its own cloud sessions — observed in the session-management tool surface)
environments: [host, worktree, remote-sandbox]   # host + worktree OBSERVED (worktrees are first-class: EnterWorktree/ExitWorktree tools, plus per-agent `isolation: worktree`); remote-sandbox = cloud sessions/web (bundle). Devcontainer support is docs testimony — left unclaimed
environment_relation: bundle   # the web/cloud side ships its own sandbox, not separately selectable (the taxonomy's Devin verb). The LOCAL side also *binds* worktrees natively — one product, two relations; bundle recorded as primary because it is the non-obvious one, the worktree bind is noted in Bleed
maker: Anthropic
url: https://github.com/anthropics/claude-code
license: proprietary   # the GitHub repo (141,660 stars) is issues + distribution + examples, NOT source; no license file on the repo at check date 147,932 stars at 2026-09-24 (`gh api`), still no license file
access: closed-source   # the public repo (see `license:` above) is issues + distribution + examples, not source — a public repo is not source access
stack: [TypeScript, Node]   # distribution observable (npm package, bundled); internals not readable — this is packaging fact, not architecture claim
version: 2.1.281   # `claude --version`, observed 2026-09-24 (2.1.233 at the 2026-08-17 read; latest GitHub release v2.1.281, 2026-09-23) — NOT a git pin; there is no clone, so nothing here is machine-checked (--check skips: no commit field)
stars: 147932
stars_at: 2026-09-24   # of the issues/distribution repo — measures community gravity, not source adoption
read_at: 2026-09-24   # re-observation at 2.1.281 (§ Re-observation); first read 2026-08-17 at 2.1.233 — the observation route's version of a re-read, no pin to move
depth: survey   # OBSERVATION-ONLY (issue #12): daily use + live-session instrumentation of v2.1.233 + platform docs. There is no source; every architecture claim below is behavior, config-surface, or testimony — graded inline. This can never honestly reach deep-dive: the loop and context assembly are not readable RE-OBSERVED 2026-09-24 at 2.1.281: every cell re-derived from the live CLI + docs retrieved that day; auto mode itself was NOT exercised (the observing session was not in it) — the classifier is docs testimony
harness_features:
  mcp: true              # OBSERVED: .mcp.json convention, mcp__<server>__<tool> namespacing, MCP server management in-product
  hooks: true            # OBSERVED: deterministic lifecycle hooks configured in settings.json (the harness executes them, not the model) RE-OBSERVED 2026-09-24: the hooks reference (retrieved 2026-09-24) documents 32 events — SessionStart, Setup, UserPromptSubmit, PreToolUse, PermissionRequest, PermissionDenied, PostToolUse, PostToolBatch, SubagentStart/Stop, Stop, StopFailure, FileChanged, WorktreeCreate/Remove, PreCompact/PostCompact, PreModelSwitch/PostModelSwitch, Elicitation… — and hook handlers now span shell commands, HTTP endpoints, MCP tool calls, LLM prompts and subagents; seven event names OBSERVED in a live settings file. Same slot, wider surface
  context_retrieval: model-driven  # ADR-0055, cell set 2026-09-04, docs-route (retrieved 2026-09-04): "How Claude Code works" describes retrieval entirely as agentic tool use — a Search tool category (pattern find + regex content search) the model dispatches mid-loop — with no index/embeddings/repo-map named there or in Best practices; the one piece of the context-assembly mechanism the docs commit to in writing (the rest stays dark per this report's grading) HOLDS 2026-09-24 (same page, retrieved 2026-09-24): retrieval is still the Search tool category ("Find files by pattern, search content with regex"); code intelligence (type errors, go-to-definition) arrives via plugins, not an index
  context_compaction: [prune, llm-summarize]  # ADR-0055, cell set 2026-09-04, docs-route (retrieved 2026-09-04), both stages automatic: "It clears older tool outputs first, then summarizes the conversation if needed" (how-claude-code-works, § When context fills up); the summary stage is a genuine LLM call — "a separate request with the same system prompt, tools, and history... plus a summarization instruction" (prompt-caching, § Compacting the conversation). The older "microcompact" term no longer appears in current docs HOLDS 2026-09-24: "It clears older tool outputs first, then summarizes the conversation if needed" verbatim in the current page; NEW: auto-compaction now stops after a few attempts with a thrashing error instead of looping when one artifact refills the window
  turn_end_gates: hook   # OBSERVED in official hooks docs (retrieved 2026-08-18): Stop hook exit-2 "prevents Claude from stopping, continues the conversation" — a turn-end veto at hook grade. NOTE: a user-configured SURFACE, empty by default (exp-03 rig verified no gates configured), unlike hermes' always-on loop policy HOLDS 2026-09-24: Stop exit-2 "Prevents Claude from stopping, continues the conversation" verbatim in the current reference; a StopFailure event was added beside it
  tool_approval: policy  # docs-route (proprietary): permission prompts at tool dispatch + plan approval, permission-modes docs; set 2026-08-25 per the category-2 index absorption table, daily-use corroborated. RE-OBSERVED 2026-09-24 at 2.1.281 — still `policy`, but the gate gained a MODEL-AUTHORED stage: **auto mode**, "a second model, the classifier, reviews actions instead of you" (permission-modes docs, retrieved 2026-09-24; Claude Sonnet 5 by default, server-configurable), the built-in STARTING mode for interactive terminal/VS Code sessions on Pro/Max/Team plans (`-p` and the SDK start in Manual on every plan), opt-out via `disableAutoMode`. Decision order is fixed: operator allow/ask/deny rules resolve first (deny rules block in every mode, bypassPermissions included), read-only actions and working-directory edits auto-approve, then the classifier decides the rest — it APPROVES what Manual mode would have prompted on (approve-capable, unlike qwen-code's block-only clamp) and blocks a shipped deny-set (`claude auto-mode defaults`: 17 allow, 70 soft_deny, 1 hard_deny, 21 environment rules, OBSERVED); no verdict → deny (fails closed); 3 consecutive or 20 total blocks pause auto mode back to prompting. It also reviews every SendMessage to another agent and every subagent's task at spawn and report at finish. This is ADR-0053's parked second axis (model authority in the gate) in its strongest form yet — recorded in the cell, NOT admitted as vocabulary; the owner gate stands
  skills: true           # OBSERVED: SKILL.md convention, ~/.claude/skills + .claude/skills + plugin skills, /name invocation, description-based triggering
  ptc: false             # checked in official docs (retrieved 2026-08-18): no code-mode/programmatic-tool-calling mechanism documented; tool use is chat-loop only RE-CHECKED 2026-09-24: still no PTC. The NEW `Workflow` tool (OBSERVED in-session at 2.1.281) executes a model-emitted JavaScript script that orchestrates SUBAGENTS deterministically (`agent()`/`parallel()`/`pipeline()` primitives) — model-emitted code driving *agents*, not the harness's own tool dispatch: the sharpened definition's near-miss shape, recorded here, cell unchanged
  subagents: true        # OBSERVED: Agent tool with named types (general-purpose, Explore, Plan, custom .claude/agents/*.md definitions), per-agent model/tool overrides, worktree isolation RE-OBSERVED 2026-09-24: plus background SESSIONS — `claude --bg` starts a session in the background in its own worktree, managed by the new `agents`/`attach`/`logs`/`respawn`/`rm`/`stop` subcommands (`claude --help`, 2.1.281); `rm` deletes the session "and its worktree when that is safe"
  plan_mode: mode        # OBSERVED: an actual MODE with enforced read-only state + plan-file workflow + user approval gate — not a prompt convention
  rules_files: [CLAUDE.md]   # OBSERVED: global ~/.claude/CLAUDE.md + project CLAUDE.md, both loaded; the convention the whole field's rules-file story descends from
  model_agnostic: false  # checked and absent BY DESIGN: Anthropic models only (opus/sonnet/haiku/fable). Multi-provider transport exists (API/Bedrock/Vertex) but that is model ACCESS (type 1b), not model agnosticism
  session_sharing: true  # OBSERVED: claude.ai/code session URLs; sessions resumable/shareable across surfaces
  learning_loop: in-loop # OBSERVED — but a THIRD mechanism shape the matrix column doesn't name: agent-written persistent memory (memory/ dir + MEMORY.md index), harness-prompted, written IN-LOOP by the main agent — not hermes' background fork, not codex's spawned pipeline, not Warp's manual-only store. See Surprises 1 Column vocabulary settled 2026-09-09 by ADR-0056 (background | in-loop | proposed) — Surprises 1 and the third open question are answered. RE-OBSERVED 2026-09-24: auto memory is still harness-prompted and agent-written in-loop; docs now state the load budget — "The first 200 lines or 25KB of MEMORY.md, whichever comes first, load at the start of each session" (how-claude-code-works, retrieved 2026-09-24)
  headless_approval: deny  # SET 2026-09-24, docs-route (headless page, retrieved 2026-09-24): "In a `-p` run with no host, these requests are denied either way" — anything that permission rules, PermissionRequest hooks, or the mode leave unresolved is denied when nobody can answer; `-p` starts in Manual on every plan; `--permission-prompts none` (v2.1.259+) additionally tells the model not to retry. Fail-closed, gemini-cli's value and aider's opposite. Corroborated by the 2026-09-09 superpowers live probe, which hit repeated permission denials in print mode ([superpowers.md](../4-workflow-frameworks/superpowers.md) § Run probe)
  gate_model_authority: approve  # DOCS-ROUTE (permission-modes page, retrieved 2026-09-24): auto mode — "a second model, the classifier, reviews actions instead of you" (Sonnet 5 by default), default starting mode on Pro/Max/Team interactive sessions, approves what Manual would prompt on, bounded by operator deny rules, no verdict → deny
  unbypassable_gates: true  # DOCS-ROUTE (same page): "actions no mode auto-approves" plus the critical-path rm/rmdir circuit breaker that no allow rule or PreToolUse hook can approve, even in bypassPermissions
---

# Claude Code

The first closed-*spanner* report (issue #12), and the repo's most-cited absent tool
finally gets an entry. **Method note up front:** there is no source. This report is built
from three instruments, graded inline throughout — **OBSERVED** (behavior and config
surfaces of a live v2.1.233 installation, 2026-08-17 — including the session this report
was written in, which is itself the subject; product-level surfaces only, nothing
installation-specific), **TESTIMONY** (Anthropic platform docs, dated), and **INFERENCE**
(marked). Under the legibility law from the Modal read, Claude Code sits unusually high
for a closed product: no source, but a rich public config surface, extensive docs, an
SDK, and the fact that observing it costs nothing — you are inside it.

## What it is

Anthropic's agentic coding harness: one agent core surfaced as a terminal CLI, a desktop
app, claude.ai/code on the web, and IDE extensions, with local execution plus cloud
sessions as the async-remote side (a local session can list and message its own cloud
sessions — OBSERVED in the product's session-management surface). Distributed via npm as
a bundled TypeScript/Node application; the 141k-star (148k at 2026-09-24) GitHub repo is an issue tracker and
distribution point, not source.

## The distinguishing bet

**That the harness is a platform, and the extension surface is the product.** Every
category-4, category-5, and category-6 mechanism this repo tracks separately ships *natively and
first-party* here — and most of the field's conventions for them descend from this
product's:

- **Rules files**: `CLAUDE.md` is the convention the entire rules-file story started from
  — Warp links it, hermes reads it, `AGENTS.md` is its cross-vendor successor
  (standards note).
- **Skills**: the `SKILL.md` format that spec-kit compiles to, Warp implements natively,
  and OpenSpec calls "canonical" originated here.
- **Hooks**: deterministic lifecycle hooks the *harness* executes (OBSERVED: configured
  in `settings.json`, explicitly not model-interpreted) — the mechanism conclusion 7
  found category-4 frameworks failing to replicate in prose.
- **Subagents**: first-class, with named types, per-agent model/tool/isolation overrides,
  and user-defined agents as frontmatter markdown files (OBSERVED).
- **Plan mode**: an enforced *mode* — read-only state, a plan file, an explicit user
  approval gate — not a prompt asking the model to plan (OBSERVED). This is the
  category-4-mechanism-as-harness-feature case the taxonomy's boundary rule cites.

The wager, stated against its rivals: opencode bets on model-agnosticism, codex bets on
compiled security, Warp bets on owning the surface — Claude Code bets that **a
single-vendor model paired with the deepest extension surface beats all three**, because
the ecosystem (skills, hooks, agents, MCP servers, plugins) accumulates on the platform.
`model_agnostic: false` is not a gap; it is the bet's other half — and the maker-span
half is below.

## Main features (grade per claim)

- **Context assembly** — the one load-bearing area that stays dark. The category-2 index
  repeats the claim that Claude Code's edge is "loading less but using it better";
  OBSERVED behavior is consistent (rules files + on-demand skill loading + tool-search
  deferral of MCP schemas + compaction on long sessions), but the assembly itself is
  unreadable. INFERENCE only, and flagged as such.
- **Permission model** (OBSERVED): per-tool-call approval with a user-selected permission
  mode; allowlists in `settings.json`; hooks can intercept tool calls; plan mode as a
  structurally read-only state. The check gates the *call*, after the model decides —
  same slot as opencode's `Permission.ask`.
- **Worktrees are first-class** (OBSERVED): the harness ships native enter/exit-worktree
  operations, and subagents can be launched into their own worktree (auto-cleaned if
  unchanged). See Surprises 2 — this is the environments matrix's first verified
  `worktree` cell.
- **Memory** (OBSERVED): a persistent per-project memory directory with an index file
  (`MEMORY.md`) the harness loads each session; the *agent* authors entries in-loop,
  prompted by the harness rather than the user. See Surprises 1.
- **Cloud/web execution** (OBSERVED surface + TESTIMONY mechanics): sessions run
  remotely and report back; the sandbox is vendor-provisioned — the taxonomy's `bundle`
  verb. Platform docs (retrieved 2026-08-16) describe the adjacent Managed Agents
  infrastructure as per-session containers with `unrestricted`/`limited` egress and
  credential substitution *at the egress proxy* so secrets never enter the sandbox;
  isolation primitive: not disclosed. Maximally closed at the mechanism level.
- **Table stakes done natively**: MCP client with OAuth; session sharing/resumption
  across surfaces; IDE integration; a task system; remote control from mobile. All
  OBSERVED.

## Bleed

The heaviest bleed profile in the tracked set — which is the point of the entry:

- **→ category 6**: ships skills, hooks, subagent definitions, MCP client, plugins — and
  *originated* the file conventions (CLAUDE.md, SKILL.md) that category 6's independence
  story is measured against. When conclusion 3 says "MCP plus vendor features," the
  vendor is, mostly, this product.
- **→ category 4**: plan mode as an enforced harness mode — the strongest form of the
  category-4-absorption pattern (conclusion 8), stronger than prose frameworks can build
  (conclusion 7's enforcement-by-exit-code vs -typography distinction, settled at the
  harness level).
- **→ category 3**: dual relation. Locally it **binds** worktrees as a native operation;
  the web/cloud side **bundles** a vendor sandbox. One product exhibiting two of the four
  relationship verbs is itself vocabulary evidence.
- **→ maker span (the reason this report exists)**: Anthropic now shows tracked
  coverage at categories 1 (four model reports) **and 2** (this report), with category-6
  conventions and the bundled category-3 sandbox as bleed. (A generated `vendors.md` used
  to track that narrowing; removed 2026-08-26, ADR-0041 — the taxonomy's hand-kept table
  is now the only maker-span surface.) The span is co-designed — the harness is tuned to the models and the models to the
  harness (TESTIMONY: Anthropic's own model-migration guidance ships Claude-Code-derived
  prompt patterns) — which is exactly the co-variance the maker-span section warns
  category-choice reasoning about.

## Cost model

Subscription (Pro/Max) or metered API — both first-party (TESTIMONY, drifts fast; check
current pricing pages rather than this file). The shape matters more than the number: the
subscription pushes toward heavy interactive use; the same harness on metered API prices
every token. Cloud sessions bill separately from local API use.

## Surprises

1. **A third learning-loop mechanism the matrix column doesn't name.** The column was
   defined on hermes (background fork, on by default) and codex (spawned pipeline,
   default off); Warp gave it a verified ✗ (manual-only store). Claude Code is none of
   these: the *agent* writes persistent memory, but **in-loop** — the harness prompts
   the write path during the session rather than forking a background reviewer. The
   `learning_loop` column now spans three mechanism shapes plus one absence; per issue
   #2's own rule, that heterogeneity is approaching the point where the column needs a
   vocabulary (background / in-loop / manual), not a boolean. *Answered 2026-09-09: ADR-0056
   regraded the column to background | in-loop | proposed; this report is the `in-loop` instance.*
2. **The first verified `worktree` cell in the environments matrix.** The category-3 index
   asks why nobody had verified worktree support anywhere despite the worktree/gitignore
   trap being the category's founding scar. First answer, and it's ironic: the harness with
   native worktree operations is the *closed* one — observed from product surface, not
   source. The trap and the first-class support belong to the same ecosystem.
3. **The distribution repo out-stars every tracked tool.** 141,660 stars on a repo that
   contains no product source — more than ECC (236k excepted), more than any open
   harness except hermes and opencode's class. Stars measure gravity, not code.
4. **Self-observation works better than expected as an instrument.** Config surfaces,
   tool inventory, mode behavior, and conventions were all confirmable from a live
   session at zero cost — a closed product's *client-side* half is significantly more
   legible than the Modal read's client-only floor, because here the observer operates
   the product rather than reading its SDK. The dark half (loop, context assembly,
   cloud sandbox internals) stays dark, same as Modal's infra.

## Open questions

- Context assembly is the field-defining claim ("loads less, uses it better") and the
  least verifiable part of the product. Is there any behavioral experiment — token
  accounting across controlled sessions — that could test it from outside? (That is an
  instrument question, exp-shaped.)
- Does the in-loop memory write path change what the memory contains, versus hermes'
  background fork? (In-loop writes compete with the task for attention; background
  writes see the whole transcript cold. A comparable-corpus comparison would be novel.)
- ~~The `learning_loop` column vocabulary: promote to background/in-loop/manual? Needs
  issue #2's two-instance rule applied to the *mechanism* distinction.~~ **Answered
  2026-09-09 (ADR-0056)**: background | in-loop | proposed — the third value is not
  "manual" but a proposal-only loop, which warp and gemini-cli supplied.
- **Does the auto-mode classifier change what the gate *is*?** (added 2026-09-24) The
  registry's `tool_approval` enum describes who decides *when to ask*; auto mode adds a
  second model that decides *instead of asking*, bounded by operator deny rules. ADR-0053
  parked model-authority-in-the-gate pending "a third widen-capable gate" — warp's
  AgentDecided was the first; whether this is the second or the third depends on how
  continue's tighten-only evaluator is counted. Owner question, argued from the record.

## Re-observation — 2.1.281 (2026-09-24; no pin, version re-dated)

The observation route's version of a re-read: 48 patch versions after the first read
(2.1.233 → 2.1.281, `claude --version` both times), every frontmatter cell re-derived from
the live CLI and from the four docs pages retrieved 2026-09-24 (how-claude-code-works,
hooks reference, permissions, permission-modes, headless). Method unchanged — OBSERVED /
TESTIMONY / INFERENCE, graded inline. The observing session was not in auto mode, so the
one headline change below is testimony, not observation.

**Per-claim confrontation.** Every cell HOLDS at 2.1.281 except as noted:

| cell | verdict | note |
|---|---|---|
| `surfaces` | CHANGED (+`messaging`) | docs list Slack as an interface; third ADR-0047 instance |
| `tool_approval: policy` | HOLDS, with a new stage | auto mode — a second model in the gate, default starting mode on subscription plans (below) |
| `headless_approval` | SET (`deny`) | was unset; the headless page states the no-host case verbatim |
| `hooks` | HOLDS | 32 documented events, five handler kinds; seven names OBSERVED in a live settings file |
| `turn_end_gates: hook` | HOLDS | Stop exit-2 wording verbatim; `StopFailure` added |
| `context_retrieval`, `context_compaction` | HOLD | verbatim sentences unchanged; compaction now fails loud on thrash |
| `ptc: false` | HOLDS | the new `Workflow` tool is a near-miss (orchestrates subagents, not tool dispatch) |
| `subagents`, `plan_mode`, `skills`, `mcp`, `rules_files`, `session_sharing`, `model_agnostic` | HOLD | all OBSERVED in the session that wrote this section (plan mode: this section's own work ran through EnterPlanMode → ExitPlanMode) |
| `learning_loop: in-loop` | HOLDS | vocabulary question closed by ADR-0056 |
| `stars` | re-measured | 141,660 → 147,932 (`gh api`, +4.4% in 38 days) |

**1. The permission gate now has a model in it (TESTIMONY, permission-modes page).** Auto
mode: "a second model, the classifier, reviews actions instead of you" — Claude Sonnet 5 by
default, server-overridable — and "On Pro, Max, and Team plans, the built-in starting
permission mode is auto mode" for interactive terminal and VS Code sessions, while `-p`
and the SDK start in Manual. The decision order is fixed and operator-first: allow/ask/deny
rules resolve immediately (deny rules block in every mode), read-only actions and
working-directory edits auto-approve, and the classifier decides what is left, approving
what Manual would have prompted on and blocking a shipped deny-set (`curl | bash`,
secrets to external endpoints, production deploys, force push, IAM grants, irreversible
deletion of pre-session files). Failure mode is closed: no verdict → denied; 3 consecutive
or 20 total blocks pause auto mode back to prompting; in a `-p` run there is nothing to
fall back to and the action simply does not run. The classifier also reviews every
`SendMessage` between agents and every subagent's task at spawn and report at finish.
OBSERVED half: `claude auto-mode defaults` prints the shipped rule sets (17 allow, 70
soft_deny, 1 hard_deny, 21 environment rules at 2.1.281), and `claude auto-mode
config|critique|reset` manage them — the rules are operator-editable data, the verdict is
the model's. For the registry this is the strongest instance yet of ADR-0053's parked axis
(model authority in the gate): approve-capable like warp's AgentDecided, bounded by
operator deny rules unlike it, and default-on for the product's largest user population.
Recorded in the cell and in Open questions; not admitted as vocabulary here.

**2. Headless resolution is stated, so the cell is set.** "In a `-p` run with no host,
these requests are denied either way" — `headless_approval: deny`, gemini-cli's value and
aider's opposite. Also new: `--bare` (skips hooks, skills, agents, plugins, MCP, auto
memory and CLAUDE.md; "will become the default for `-p` in a future release") and
`--permission-prompts none` (v2.1.259+).

**3. Background sessions bind worktrees natively (OBSERVED, `claude --help`).** `claude
--bg` starts a session in its own worktree; `agents`, `attach`, `logs`, `respawn`, `rm`
("Delete a background session, and its worktree when that is safe") and `stop` manage
them. Surprises 2's "first verified `worktree` cell" is now a product-level lifecycle,
not just an enter/exit pair.

**4. A PTC near-miss, recorded (OBSERVED in-session).** The `Workflow` tool runs a
model-emitted JavaScript script with `agent()`, `parallel()` and `pipeline()` primitives
that orchestrates subagents deterministically. Under the 2026-08-27 sharpening of `ptc`
("the test is whether the emitted code drives the harness's OWN tool dispatch") this is
not PTC: the script drives *agents*, each of which still makes chat-loop tool calls. Cell
unchanged; the shape is the closest any tracked harness has come from the orchestration
side rather than the tool side.

**5. Docs now name three execution environments** (Local, Cloud on "Anthropic-managed
VMs, or self-hosted environments your organization operates", Remote Control) — the
`bundle` verb holds for cloud, and self-hosted environments are a docs-route hint that the
bundled sandbox can be operator-supplied; not verified beyond the sentence.

**Prediction, scored at the next re-observation (dated, falsifiable).** By **2026-12-31**
`--bare` is the default for `claude -p` (the headless page says so in a Note dated by this
retrieval), and the hooks reference documents **≥ 36** events (32 today; 2026-08-18's
retrieval predates FileChanged/Worktree*/PostCompact, so the surface is still growing).

## What was not verified

- **Everything below the API line**: the agent loop, context assembly, compaction
  policy, cloud sandbox isolation. No source exists to check; claims above are graded
  and none should be cited as architecture.
- The `version:` field is a CLI-reported version, not a git pin — nothing in this report
  is machine-checked by `--check`, and drift checks (rule 4b) do not apply; the analog
  is re-observing against a newer version and re-dating.
- Docs testimony (Managed Agents mechanics, pricing) was retrieved 2026-08-16/17 and
  rots on Anthropic's schedule, not the repo's. The 2026-09-24 re-observation re-fetched
  the permission, hooks, headless and how-it-works pages, not the Managed Agents or
  pricing pages — those two carry their 2026-08 dates still.
- **Auto mode was not exercised** (2026-09-24): the classifier's approve/deny behavior,
  its model, and its thresholds are docs testimony. A cheap probe exists — `claude -p
  --permission-mode auto` against a scratch repo with a `curl | bash` step, read from the
  stream-json `permission_denied` events — and needs an owner sign-off because it spends.
