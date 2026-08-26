---
name: claude-code
category: 2
surfaces: [terminal, desktop, web, ide]   # in-product statement + docs; terminal OBSERVED directly (this report was written from inside one)
execution: both   # local CLI observed; cloud sessions + claude.ai/code web are the async-remote side (the local client can list/message its own cloud sessions — observed in the session-management tool surface)
environments: [host, worktree, remote-sandbox]   # host + worktree OBSERVED (worktrees are first-class: EnterWorktree/ExitWorktree tools, plus per-agent `isolation: worktree`); remote-sandbox = cloud sessions/web (bundle). Devcontainer support is docs testimony — left unclaimed
environment_relation: bundle   # the web/cloud side ships its own sandbox, not separately selectable (the taxonomy's Devin verb). The LOCAL side also *binds* worktrees natively — one product, two relations; bundle recorded as primary because it is the non-obvious one, the worktree bind is noted in Bleed
vendor: Anthropic
url: https://github.com/anthropics/claude-code
license: proprietary   # the GitHub repo (141,660 stars) is issues + distribution + examples, NOT source; no license file on the repo at check date
open_source: false
stack: [TypeScript, Node]   # distribution observable (npm package, bundled); internals not readable — this is packaging fact, not architecture claim
version: 2.1.233   # `claude --version`, observed 2026-08-17 — NOT a git pin; there is no clone, so nothing here is machine-checked (--check skips: no commit field)
stars: 141660
stars_at: 2026-08-17   # of the issues/distribution repo — measures community gravity, not source adoption
read_at: 2026-08-17
depth: survey   # OBSERVATION-ONLY (issue #12): daily use + live-session instrumentation of v2.1.233 + platform docs. There is no source; every architecture claim below is behavior, config-surface, or testimony — graded inline. This can never honestly reach deep-dive: the loop and context assembly are not readable
harness_features:
  mcp: true              # OBSERVED: .mcp.json convention, mcp__<server>__<tool> namespacing, MCP server management in-product
  hooks: true            # OBSERVED: deterministic lifecycle hooks configured in settings.json (the harness executes them, not the model)
  turn_end_gates: hook   # OBSERVED in official hooks docs (retrieved 2026-08-18): Stop hook exit-2 "prevents Claude from stopping, continues the conversation" — a turn-end veto at hook grade. NOTE: a user-configured SURFACE, empty by default (exp-03 rig verified no gates configured), unlike hermes' always-on loop policy
  tool_approval: true    # docs-route (proprietary): permission prompts at tool dispatch + plan approval, permission-modes docs; set 2026-08-25 per the category-2 index absorption table, daily-use corroborated
  skills: true           # OBSERVED: SKILL.md convention, ~/.claude/skills + .claude/skills + plugin skills, /name invocation, description-based triggering
  ptc: false             # checked in official docs (retrieved 2026-08-18): no code-mode/programmatic-tool-calling mechanism documented; tool use is chat-loop only
  subagents: true        # OBSERVED: Agent tool with named types (general-purpose, Explore, Plan, custom .claude/agents/*.md definitions), per-agent model/tool overrides, worktree isolation
  plan_mode: true        # OBSERVED: an actual MODE with enforced read-only state + plan-file workflow + user approval gate — not a prompt convention
  rules_files: [CLAUDE.md]   # OBSERVED: global ~/.claude/CLAUDE.md + project CLAUDE.md, both loaded; the convention the whole field's rules-file story descends from
  model_agnostic: false  # checked and absent BY DESIGN: Anthropic models only (opus/sonnet/haiku/fable). Multi-provider transport exists (API/Bedrock/Vertex) but that is model ACCESS (type 1b), not model agnosticism
  session_sharing: true  # OBSERVED: claude.ai/code session URLs; sessions resumable/shareable across surfaces
  learning_loop: true    # OBSERVED — but a THIRD mechanism shape the matrix column doesn't name: agent-written persistent memory (memory/ dir + MEMORY.md index), harness-prompted, written IN-LOOP by the main agent — not hermes' background fork, not codex's spawned pipeline, not Warp's manual-only store. See Surprises 1
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
a bundled TypeScript/Node application; the 141k-star GitHub repo is an issue tracker and
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
`model_agnostic: false` is not a gap; it is the bet's other half — and the vendor-span
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
- **→ vendor span (the reason this report exists)**: Anthropic now shows tracked
  coverage at categories 1 (four model reports) **and 2** (this report), with category-6
  conventions and the bundled category-3 sandbox as bleed. The generated floor
  (`comparisons/vendors.md`) narrows against the taxonomy's hand-kept table accordingly:
  the span is co-designed — the harness is tuned to the models and the models to the
  harness (TESTIMONY: Anthropic's own model-migration guidance ships Claude-Code-derived
  prompt patterns) — which is exactly the co-variance the vendor-span section warns
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
   vocabulary (background / in-loop / manual), not a boolean.
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
- The `learning_loop` column vocabulary: promote to background/in-loop/manual? Needs
  issue #2's two-instance rule applied to the *mechanism* distinction.

## What was not verified

- **Everything below the API line**: the agent loop, context assembly, compaction
  policy, cloud sandbox isolation. No source exists to check; claims above are graded
  and none should be cited as architecture.
- The `version:` field is a CLI-reported version, not a git pin — nothing in this report
  is machine-checked by `--check`, and drift checks (rule 4b) do not apply; the analog
  is re-observing against a newer version and re-dating.
- Docs testimony (Managed Agents mechanics, pricing) was retrieved 2026-08-16/17 and
  rots on Anthropic's schedule, not the repo's.
