---
name: ecc
category: 6   # 4 (provisional) -> 5 at read time 2026-07-30 (no process spine; see The category verdict) -> 6 at the 2026-08-22 split (ADR-0020: Extensions renumbered 5->6; the verdict itself is unchanged)
type: config-pack   # set 2026-08-19 per ADR-0016 — the classification the deep-dive already made in prose ("a config pack at scale, with a learning runtime", The category verdict); was the bucket's only report with no type key
maker: Affaan Mustafa (affaan-m)
url: https://github.com/affaan-m/ECC
license: MIT
access: open-source
stack: [Markdown, Node]
version: v2.1.0-16-ge4e41631
commit: e4e41631
first_commit: 2026-01-17
stars: 236217
stars_at: 2026-07-30
read_at: 2026-07-30   # drift-checked 2026-08-11 at 623f2c02 without re-reading — see "Drift check"; one claim corrected, pin deliberately not moved
depth: deep-dive   # ECC has no agent loop of its own; its runtime analogs were traced in source — learning pipeline (hooks/observe.sh → agents/observer-loop.sh → scripts/instinct-cli.py), enforcement lifecycle (hooks/hooks.json + memory-persistence contract), install/portability surface. The 281-skill catalog was sampled, not read; ecc2 read at README level
harness_targets: "23 documented install invocations across ~13 named targets: Claude Code, Cursor, OpenCode, Gemini CLI, Zed, Antigravity, Qwen CLI, Hermes, OpenClaw, Kimi Code, CodeBuddy, JoyCode, plus Codex via a sync script; manual-adaptation guide for the rest. Reach ≠ parity: upstream graded these itself on 2026-08-04 (#2681) — Claude Code stable, Codex supported-sync, Cursor/OpenCode beta, Copilot instruction-only, the remaining nine experimental/minimal. Counted at e4e41631; grading recorded at the 2026-08-11 drift check"
harness_features:
  learning_loop: background  # third verified instance — hook-observed sessions → background Haiku analysis → confidence-scored instinct files; traced at the scripts, not just SKILL.md (see Architecture)
---

# ECC — everything-claude-code

Self-described "agent harness operating system": 281 skills, 67 agents, rules packs,
enforcement hooks, memory persistence, and an instinct-based learning system, installed
*into* a dozen-plus harnesses. The fastest-adopted tool in the study — 236k stars in
~6.5 months — and, as of this read, a **solo-author product**: 1,517 of 2,336 commits
(65%) from the maintainer, plus dependabot and `copilot-swe-agent[bot]` (agents
maintaining the agent-config repo). A commercial arm exists: ECC Pro, a GitHub App,
hosted badges at `api.ecc.tools` — the only tool in the set with a pricing page.

## Drift check — 2026-08-11 (not a re-read; the pin is unchanged)

`--check` reported 16 commits / 68 files of movement since the read. Checking whether the
drift touched what this report claims found that **it contradicts one claim and dates
another**, so it is recorded here rather than left to the next reader. The pin stays at
`e4e41631` and `read_at` stays 2026-07-30 — the sections below describe that commit, and
re-pointing them at a HEAD nobody has read is the failure `upstream/README.md`'s scar
warns about.

1. **The `/evolve` claim was wrong at the pin** — corrected in place under the instinct
   pipeline below, and verified against `e4e41631` rather than taken from the fix's
   commit message.
2. **`harness_targets` is now stale as a capability statement, though not as a count.**
   #2681 (2026-08-04, "honest support matrix") rewrote the README's platform tables:
   the old cross-tool *parity* table is gone, replaced by a status matrix that grades
   Cursor and OpenCode **beta**, Copilot **instruction-only**, and "Gemini, Zed,
   Antigravity, Qwen, Hermes, OpenClaw, Kimi, CodeBuddy, JoyCode" collectively as
   **experimental/minimal adapters** where "full Claude feature parity is not claimed."
   The marketing line moved from "first-class Codex support and adapters for …" to
   "a supported Codex sync path and capability-limited adapters." The ~13 named targets
   survive; what changed is that upstream now grades them, and the report's Portability
   section — which already credited the repo for honesty about degraded capability — is
   corroborated harder than it was written.
3. **A concrete instance of that degradation:** #2680 excludes ECC skills from the
   antigravity install target entirely, because antigravity's `.agent/` directory
   already receives ECC *agents* and the two collided.
4. **New, not contradictory:** the same matrix discloses open native-Windows defects in
   continuous-learning v2's observer daemon and memory-vault writes (#2489, #2626), and
   a macOS Bash 3.2 incompatibility in the GAN path (#2674). This report made no OS
   claims, so this is added scope for a re-read, not a correction.

**Unaffected:** the category verdict (5-at-the-time, 6 since the ADR-0020 renumber). Neither leg (no process spine; portability reduces
to copy-with-adaptation into convention dirs) is touched by the drift, so the taxonomy
revision this read triggered stands, as does the ~2027-01 re-promotion re-check.

**What a re-read should cost:** small. The evolve fix, the support matrix, and the
antigravity exclusion are the three places to look, plus the 281-skill catalog that was
sampled rather than audited at the original read.

## The category verdict (the question this read was preregistered to answer)

**category 5 — the extensions bucket** *(renumbered to **6** at the 2026-08-22 split, ADR-0020; the verdict itself is unchanged)*. The category-4 test — an encoded methodology, a prescribed operating loop —
fails on the source:

- The README's own guidance is *"Start with the workflow you need, not the full
  catalog."* Workflow content exists (a `tdd-workflow` skill, `security-review`,
  `mle-workflow`) but as **catalog items you opt into**, routed by a task-type table —
  not a spine like GSD's plan→execute→verify or spec-kit's specify→plan→tasks→implement.
- The nearest thing to orchestrated process — the `/multi-plan`, `/multi-execute`
  command family — requires an **external runtime** (`npx ccg-workflow`, a separate
  package) and doesn't run without it. The repo's own `workflows/` directory contains
  one file.
- What ECC *does* ship everywhere is reach and reflexes: rules, agents, skills,
  enforcement hooks, memory, learning. That's the extensions bucket's territory — what the agent can
  see and touch — delivered at unprecedented scale, with real runtime components riding
  each harness's hook system.

So the stress-test's live case resolves: **a config pack at scale, with a learning
runtime — not a methodology.** The report moved shelves accordingly (this file was
`tools/4-workflow-frameworks/ecc.md` as a stub).

## The distinguishing bet

**That agent capability accumulates in the *user's* installation, not the vendor's
harness — install reflexes, not process.**

Where hermes and codex build learning loops *into* their harnesses, ECC **retrofits
one onto any harness with hooks**: observation → background analysis → confidence-scored
"instincts" → clustering into skills. The bet has two halves: (a) performance lives in
accumulated configuration (rules, skills, learned behavior), not in following a
prescribed process — the anti-spec-kit position; and (b) that accumulation category should
be harness-independent and *yours*, portable across the dozen harnesses you might use.
235k stars in six months says the market wants at least one of those halves badly —
and the solo-author + ready-made-catalog shape suggests it's mostly (a): people install
the reflexes someone else already authored.

## Architecture

### The instinct pipeline (traced in source, per methodology 4a)

`skills/continuous-learning-v2/`:

1. **Observe** — `hooks/observe.sh`, registered on `PreToolUse`/`PostToolUse`, captures
   tool events as JSON to a project-scoped store (`ecc-homunculus/projects/<hash>/`,
   XDG-pathed; v2.1 isolates per project via git-remote hash to stop cross-project
   contamination).
2. **Analyze** — `agents/observer-loop.sh`: a background daemon (re-entrancy guard,
   60s analysis cooldown, 30-min idle timeout, session leases — the guards carry issue
   numbers from real runaway incidents, #521) spawns Haiku analysis over sampled
   observations.
3. **Write** — `scripts/instinct-cli.py` persists atomic instincts: YAML frontmatter
   (id, trigger, confidence 0.3–0.9, domain, scope, project_id) over markdown
   Action/Evidence sections.
4. **Evolve** — `/evolve` clusters related instincts into skills/commands/agents;
   `/instinct-export`/`-import` make learned behavior *shareable*; project instincts
   seen in 2+ projects get promoted to global.

   **Correction (2026-08-11) — the skills/agents half of that sentence was the
   docstring's claim, not the code's behaviour.** Verified against the pin:
   `cmd_evolve`'s own docstring says "suggest evolutions to skills/commands/agents"
   (`skills/continuous-learning-v2/scripts/instinct-cli.py:1149 @ e4e41631`), but the
   clustering two lines below keys on the *entire trigger sentence*, lowercased with
   six words stripped (`when/creating/writing/adding/implementing/testing`), and
   `skill_candidates` only accepts clusters of ≥2 (`:1178–1191`). Triggers are free-form
   sentences, so every instinct landed in its own bucket. `agent_candidates` is filtered
   *from* `skill_candidates` (`:1233`), so it was empty too — `/evolve --generate` could
   emit commands and nothing else. Upstream fixed it 2026-08-04 (#2664, overlap
   coefficient at 0.5 with a 2-keyword floor) and reported the measurement this report
   should have made: 42 instincts → 42 clusters, largest cluster size 1; after the fix,
   4 clusters. The same commit found `_generate_evolved()` silently writing only the
   first 5/5/3 candidates. **What survives:** steps 1–3 were traced at the scripts and
   stand, so this is still an autonomous learning loop and still the only
   harness-independent one — but at the read commit it accumulated instincts without
   ever promoting them into skills or agents. A rule-4a violation in the exact shape
   rule 4a describes; see the drift check above.

This is the third verified autonomous learning loop (after hermes, codex) and the only
**harness-independent** one — also the only one whose unit of learning is designed for
*exchange* (import/export, confidence scores surviving transfer).

### The enforcement runtime

`hooks/hooks.json` + `hooks/memory-persistence/`: a lifecycle contract riding Claude
Code's hook events — `SessionStart` loads bounded prior context; `PreCompact` snapshots
state before compaction; `PreToolUse` dispatchers run consolidated Bash preflight
(quality, push-protection, "GateGuard") through a Node bootstrap that resolves the
plugin root across five install layouts; **`Stop` hooks run blocking quality gates**
(format/typecheck batch, console.log audit). Verification gates delivered as
*installable extension artifacts (category 6)* — a third delivery vehicle alongside category-4 prose
(GSD) and category-2 native (hermes, codex).

### Portability: adapters, not a compiler

The stub asked whether cross-harness targeting is a spec-kit-style compile step. It
isn't: `install.sh --target <harness>` **copies-with-adaptation** into each harness's
convention directories (`.cursor/`, `.gemini/`, `.kimi/`, `.codex/` via a merge-sync
script that backs up existing config), 23 documented install invocations across ~13
named targets, plus a manual-adaptation guide that is explicitly honest about degraded
capability where hooks don't exist ("without pretending hooks or native skill discovery
are available"). The payload is files in convention dirs; the runtime parts (Node hook
scripts) ride each harness's own extension points.

### ecc2 — the category-2 bleed, confirmed

The stub predicted a runtime being grown; `ecc2/` confirms: a Rust "control-plane
scaffold" (alpha) — TUI dashboard, SQLite session store, background daemon,
worktree-aware multi-session orchestration, risk scoring. The stated goal is "the category
above individual harness installs." Same structural trajectory as spec-kit's YAML
engine and GSD's `gsd-pi` (README conclusion 7's escape-hatch pattern), aimed higher:
not enforcing one methodology, but managing fleets of sessions.

## Bleed

Category 2 (ecc2 control plane; enforcement hooks shaping harness runtime behavior),
category 4 fragments (workflow skills, the external ccg-workflow family), and a hosted
service arm (GitHub App, api.ecc.tools) that is neither category — a product ring around
the artifact bundle.

## Cost model

MIT core; inference is whatever your harness pays — note the background observer adds
a continuous Haiku spend on top of every session. ECC Pro and the GitHub App are the
paid ring. "Selective install" profiles (`minimal`/`full`, component manifests) exist
because the full catalog's standing-context cost is real — the repo's own design
acknowledges the context-budget problem (design-principle X2).

## Surprises

1. **Instincts are real machinery, not branding** — hook-observed, daemon-analyzed,
   confidence-scored, project-scoped, with runaway-protection scars (#521) that prove
   production use. The stub's skepticism ("branding over rules files?") was wrong.
2. **The process spine genuinely isn't there** — and the repo knows it: the multi-*
   orchestration commands outsource to an external runtime rather than pretending
   prose can orchestrate. A 236k-star tool whose honest shape is "toolbox + reflexes"
   is strong evidence about what adoption actually rewards at category 4/5.
3. **Solo-author at 236k stars**, with `copilot-swe-agent[bot]` in the top-5
   committers — the most extreme adoption-to-maintainer ratio in the study, and the
   supply-chain concentration question (GSD's fork lesson, F6) applies with force:
   twelve harnesses' worth of installed hooks trace to one person's repo. The README's
   own malware warning about unofficial mirrors underlines the stakes.
4. **Verification gates via installable hooks** — blocking Stop-hook quality gates as
   category-6 artifacts. The verification mechanism now exists at three delivery categories.
5. **SOUL.md at the repo root** — the identity-file convention converging across the
   set (hermes loads SOUL.md as primary identity; ECC ships one).
6. **The learning unit is designed for exchange** — instinct import/export with
   confidence scores. Nobody else's memory artifacts are built to be *traded*. If that
   catches on, "instinct marketplace" is the obvious next ring, and the standards
   question (does the instinct format standardize?) becomes live.

## Open questions

- Does instinct import actually transfer value across users/projects, or does
  confidence scoring collapse on foreign evidence? (An experiment-shaped question.)
- What do the 281 skills actually contain at quality level — the catalog was sampled,
  not audited. A skills-quality pass against the hermes authoring standards would be a
  fair cross-tool instrument.
- ecc2's trajectory: if the control plane ships, does ECC become a category-2 product
  with a config catalog attached — the full reverse of its origin?
- The GitHub App and api.ecc.tools: what leaves the machine? Same telemetry question
  as codex's `analytics`/`otel`, unanswered in both reads.
