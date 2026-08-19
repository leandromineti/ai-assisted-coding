---
name: <tool>
layer: <1-5>
# The next three fields are for layer-2 (harness) reports; omit where not meaningful.
surfaces: [<terminal | ide | desktop | web>]   # where you interact — multi-valued
execution: <local | async-remote | both>        # how it runs
environments: [<host | worktree | container | remote-sandbox>]  # layer-3 bindings (bleed) — only list what's verified
# environment_relation: HOW the tool relates to the environment, not just which ones it
# reaches. One of: bundle (ships its own sandbox, not separately selectable — Devin) ·
# bind (attaches to independently-distributed environments — hermes' 8 backends) ·
# internalize (sandbox compiled into the harness binary — codex) · inhabit (detects the
# environment it is already inside — Warp). Defined in notes/03-execution-environments/.
# Set ONLY when verified, and **leave it unset if none of the four fits** — a harness that
# just runs on the host has no relationship to layer 3, and that null case is data.
environment_relation: <bundle | bind | internalize | inhabit>
vendor: <who maintains it>
url: <repo or product URL>
license: <SPDX id, or "proprietary">
open_source: <true | false>
stack: [<Language>, <Runtime/Framework>]
version: <git describe --tags --always — omit if closed source>
commit: <short SHA — omit if closed source>
# ONE machine-checked pin per report — this `commit:` is what build-tool-index --check
# validates against upstream/<name>. A multi-repo subject (e.g. an SDK repo plus an infra
# repo) records secondary pins in a PROSE comment right here in the frontmatter, naming
# the clone and the SHA read, and its Drift-check sections must re-check those by hand
# (`repo-facts.sh <clone>`). Precedent: e2b.md (SDK pin machine-checked, infra pin
# prose-recorded). Don't invent a second commit: field — the checker reads only one.
# The next three come from scripts/repo-facts.sh — never hand-typed. Omit if closed source.
first_commit: <YYYY-MM-DD — first commit in the public repo; postdates the product if open-sourced later>
stars: <integer, GitHub API>
stars_at: <YYYY-MM-DD the star count was fetched — stars drift daily, so they carry their own date>
read_at: <YYYY-MM-DD>
depth: <stub | survey | deep-dive>
# kind: layer-5 (extensions) reports only — one of the bucket's kind vocabulary:
# mcp-server | skill | hook | subagent-def | rules-file | config-pack | memory
kind: <see comment>
# harness_targets: layer-4 (and layer-5) reports only — which harnesses the tool
# officially installs into. Same discipline as features: set ONLY when verified in
# source or official docs; omitted means "not yet checked". Either a list of harness
# names, or a short string for large sets (e.g. "44 integrations incl. …").
harness_targets: [<Harness>, <Harness>]
# workflow_features: layer-4 reports only — same verified-only discipline as features:
# (omitted = not checked, false = checked and absent). A feature is a structural
# PRESENCE-claim; whether it pays is the mechanism table's question. Definitions live
# in the feature taxonomy — notes/cross-cutting/feature-taxonomy.md (ADR-0010), the
# single source of valid keys; the generator warns on and drops keys not registered there.
workflow_features:
  intent_pipeline: <true | false>
  deterministic_engine: <true | false>
  format_gates: <engine | hook | script | prose | true | false>    # GRADED, ADR-0011
  measured_gates: <engine | hook | script | prose | true | false>  # GRADED, ADR-0011
  process_gates: <engine | hook | script | prose | true | false>   # GRADED, ADR-0011
  context_isolation: <true | false>
  parallel_orchestration: <true | false>
  state_store: <repo-files | database>
  retrospectives: <true | false>
# memory_features: layer-5 `kind: memory` reports only — same verified-only discipline.
# Values are descriptive enums (mechanism choices), NOT ADR-0011 grades. Definitions
# live in the feature taxonomy (ADR-0013); the generator warns on unregistered keys.
memory_features:
  memory_store: <files-git | vector | graph | rows | [list, for, hybrids]>
  capture_path: <hook | adapter | agent-invoked>
  recall_injection: <auto | pull-only | both>
  memory_scope: [<project | agent | user | session>]
  memory_tiers: <true | false>
  hybrid_retrieval: <true | false>
  decay: <true | false>
  injection_trust_boundary: <true | false>
  deployment_mode: <self-host | cloud | both>
  harness_installer: <true | false>
  rule_extraction: <true | false>
# features: set a key ONLY when verified in source or official docs — omitted means
# "not yet checked", false means "checked and absent". Both are claims; only one is safe
# to guess, and neither should be. Keep the vocabulary to this fixed set so the generated
# matrix stays comparable — don't add vendor pet names:
features:
  mcp: <true | false>              # MCP client support
  lsp: <true | false>              # language-server integration
  hooks: <true | false>            # deterministic lifecycle hooks / plugin triggers
  turn_end_gates: <engine | hook | script | prose | true | false>  # native turn-end stop/verification gate, GRADED (ADR-0012)
  skills: <true | false>           # on-demand packaged instructions
  subagents: <true | false>        # spawnable isolated agents
  ptc: <true | false>              # programmatic tool calling in a sandboxed runtime (ADR-0012)
  plan_mode: <true | false>        # built-in plan/act split
  rules_files: <true | false | [FILENAMES]>  # standing-instruction files; list names if known
  model_agnostic: <true | false>   # bring-your-own-model by design
  session_sharing: <true | false>  # shareable session links/artifacts
  evals: <true | false>            # ships its own evaluation suite
  learning_loop: <true | false>    # AUTONOMOUS agent-written memory/skills (background/spawned write path) — distinct from `skills` (packaged instructions exist) and from user-curated memory files. Added 2026-07-30 per issue #2's two-verified-instances rule (hermes, codex); note default-on vs default-off in the comment
---

# <Tool>

> Fill the frontmatter from `./scripts/repo-facts.sh <name>`. Never hand-type a SHA —
> `build-tool-index.py --check` compares it against the clone's HEAD, and a stale pin
> silently invalidates every architecture claim below it.
>
> `depth` is a promise to your future self: **stub** = facts collected, source unread ·
> **survey** = used it or skimmed it · **deep-dive** = the agent loop and context assembly
> were actually traced. Never raise it out of optimism. Closed subjects cap at `survey`
> and grade every claim inline per methodology rule 1a: SOURCE · OBSERVED · TESTIMONY ·
> INFERENCE (strictly ordered; only SOURCE supports architecture claims).
>
> Relative links below are written for a report's destination, `notes/0N-<layer>/<tool>.md`
> — they resolve once copied there, not from this file's own location.

## Drift check — YYYY-MM-DD (not a re-read; the pin is unchanged)

*Added when `build-tool-index.py --check` reports this report behind and the drift is
checked (methodology rule 4b) — not part of the initial read; delete this section when
writing a fresh report.* Scope the check to commits touching files this report cites
(`git log <pin>..HEAD -- <cited files>`), verify at both ends, and record every claim as
**contradicted** (correct in place, citing the pin), **corroborated** (say so — silence
reads as unchecked), or **untouched** (one line). The pin never moves — a drift check is
not a re-read. Stamp the `read_at:` line with a trailing comment naming the check date and
HEAD. A report that cites no source files cannot be drift-checked (the gsd-core lesson) —
cite files even at `survey` depth.

## What it is

One paragraph. Plain description, no marketing language, no feature list.

## The distinguishing bet

What does this tool believe that its competitors don't? Every serious tool wagers on some
claim about how AI-assisted coding should work. Find the wager. If you can't name one its
rivals would dispute, it's a commodity — and that is itself the finding worth recording.

## Main features

The handful that matter for comparison, not the marketing page. For each, note whether it's
genuinely distinctive or table stakes everyone ships.

## Stack & repo shape

Languages, runtime, frameworks, and how the repo is organized (monorepo? packages?). Include
the file-extension distribution — it reveals what a project actually *is* faster than its
README does.

## Architecture

*Deep-dive only. Leave the subsections marked `_TODO_` until the source has been read —
an empty section is honest, a guessed one is worse than nothing.*

### Entry point → one full trace

Follow a single invocation from CLI entry to completion, naming real files and functions.
This is the spine; if it's vague, nothing below it can be trusted.

### The agent loop

Where it lives, what one iteration does, what terminates it (task completion? step budget?
token budget? error?). What happens when a tool call fails — retry, surface, abandon?

### Context assembly

What enters the model call, in what order, and what's dropped under pressure. The least
documented and most differentiating part of any harness. How are files selected — repo map,
embeddings, grep, or the model asking? What does compaction silently lose? Is the prompt
structured so caching can work?

### Tool surface & permissions

How tools are defined and described to the model, how dispatch works, and whether the
permission check happens *before* or *after* the model decides.

### Layer boundaries in the code

Where the taxonomy's seams show up concretely. Is the model provider swappable, and at what
cost? Is there an execution-environment abstraction, or does it shell out to the host? Can
layer-5 extensions attach, and where?

## Bleed

Which other taxonomy layers this tool reaches into, and how. See
[`../../taxonomy.md`](../taxonomy.md) — the bleed is signal, not noise.

## Cost model

Subscription, per-token, open-source-but-you-pay-inference, free. Note the *shape*, not just
the number: a flat subscription and a metered bill push behavior in opposite directions.

## Surprises

What contradicted your expectations. **The most valuable section in the document.** If it's
empty, you either skimmed or already knew this tool — say which.

## Open questions

- 
