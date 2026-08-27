---
name: aider
category: 2
surfaces: [terminal, web]   # `web` = the locally-served Streamlit GUI (`--gui`/`--browser`), added to this row 2026-08-27; it is an interaction surface, not remote execution — and it ships with the permission gate off (see § The permission gate)
execution: local
residency: session
environments: [host, container]   # host is primary; container is a published *install* image the user drives (docker run -v), not an environment the harness manages
# environment_relation deliberately UNSET — none of bundle/bind/internalize/inhabit fits, and
# the null is the finding (§ Bleed). aider ships an install image and zero confinement code:
# `git grep -niE "sandbox|seccomp|landlock|seatbelt|bwrap|firejail" -- aider/` → 0 hits;
# `git grep -niE "worktree"` over all tracked files → 0 hits. Second null case after pi, but
# a *considered* one: aider states the confinement argument in benchmark/README.md and
# scopes it to the eval.
maker: Aider-AI
url: https://github.com/Aider-AI/aider
license: Apache-2.0
access: open-source
stack: [Python]
version: v0.86.3.dev-53-g5dc9490b
commit: 5dc9490b
first_commit: 2023-04-03
stars: 48519
stars_at: 2026-08-27
read_at: 2026-08-27
depth: deep-dive   # 2026-08-27, all THREE ADR-0021 components traced at the pin by three parallel readers (loop; context assembly; permission gate + reach + provenance), load-bearing claims spot-verified in the main session before writing. Pin needed no decision: `5dc9490b` IS HEAD and origin/main — the repo has not moved in 97 days. RUN-probed the same day (published PyPI artifact 0.86.2, 54 commits behind the pin: install, repo-map measurement at three budgets, full assembled-prompt dump, zero-config lint gate). NOT traced: the Streamlit GUI beyond its permission posture, the scraper/voice/watch subsystems, the 111 .mp3 audio assets, and the polyglot corpus (a separate repo, not present at the pin — see § Evals)
harness_features:
  mcp: false           # verified absent across 8 surfaces incl. all 13,138 commit messages on all refs and every file path ever added — the ONLY `mcp` token in the tree is requirements/requirements.in:48, a comment about a dependency aider avoids
  lsp: false           # `git grep -nE "\blsp\b|language.server|pylsp|textDocument"` → 0. Tree-sitter tag extraction is not LSP: no server, no protocol, no diagnostics
  hooks: false         # no lifecycle hooks, no plugin API, no entry-points group. The one `hook` hit (args.py:495) is git's own pre-commit hooks — which aider disables by default
  turn_end_gates: engine   # --auto-lint DEFAULT TRUE (args.py:542-547): every edit runs tree-sitter parse + compile() + a real flake8 subprocess (linter.py:118-159) before the turn can end; failures become the next user message. Measured by the "ran something fresh" bar. Qualifier: the re-prompt passes through a confirm_ask defaulting to yes (base_coder.py:1603-1607), which auto-accepts under --yes-always and in every non-interactive mode
  tool_approval: true  # 7 confirm_ask sites stand between model and machine (base_coder.py:976, 1772, 2207, 2226, 2456, 2479; architect_coder.py:17). Thin and uniform — one boolean function, one modifier bit, no policy data, no tiers, no sandbox beneath
  headless_approval: allow   # FAIL-OPEN: confirm_ask's signature default is "y" (io.py:810) and no agent-loop call site overrides it; with no TTY the EOF handler treats end-of-input as "the user pressed Enter" (io.py:884-886). So `aider -m` with stdin closed auto-approves all seven gates. Inverts with the flag: --yes-always makes the SHELL gate deny (explicit_yes_required=True, io.py:866-867), so the safety flag is stricter than its absence
  skills: false        # `git grep -In -i "\bskills\?\b" -- 'aider/*.py' 'aider/coders/*.py'` → 0
  subagents: false     # architect/editor is a fixed two-stage pipeline, not spawnable: one child, fixed role, not model-requested, no fan-out, no depth recursion (architect_coder.py:11-48)
  ptc: false           # no sandbox, no runtime, no code-driven dispatch; and aider has no tool loop for code to drive
  plan_mode: false     # `grep -rniE "plan_?mode|planning_?mode"` → 0. --chat-mode selects among 13 coders — mode switching, a different axis from a plan/act split
  rules_files: false   # NO automatic standing-instruction file of any kind. AGENTS.md: 0 occurrences repo-wide. CONVENTIONS.md is documented but read by zero lines of code — it is an ordinary `/read` chat file
  model_agnostic: true # a single provider abstraction, LiteLLM (aider/llm.py:16-45); zero direct provider SDKs; 357 per-model tuning entries across 14 provider prefixes
  session_sharing: true  # PORTABLE EXPORTED ARTIFACT form, default-ON: .aider.chat.history.md, a complete human-readable transcript written unconditionally (args.py:274-289, io.py:1117-1136). The link form is manual — the share viewer is static and no in-tree code produces a URL
  evals: true          # benchmark/ — in-repo, runnable, containerized; scores code correctness AND its own edit-format adherence separately; 14 versioned result files incl. self-ablations. Corpus is a SEPARATE repo cloned at setup (§ Evals)
  learning_loop: false # no agent-authored file of any kind. .aider.chat.history.md is a human transcript with opt-in replay (--restore-chat-history default False), not memory
---

# Aider

## What it is

A terminal harness that edits files in a git repository by asking a language model for
text and parsing the reply. It predates the current harness generation by well over a
year — first commit 2023-04-03, 13,138 commits, 691 tracked files — and it is the
smallest codebase in the set by a wide margin (147 `.py` files; compare cline at 3,429
tracked files, opencode at 6,347). Two things define it: a **repo map** built from
tree-sitter tags and ranked by PageRank, and **a commit after every change**.

It is also, at this read, **dormant**. See § Provenance.

## Read scope and pin

Three ADR-0021 components traced at `5dc9490b`: the loop, context assembly, and the
permission gate. The pin required no decision — `5dc9490b` is simultaneously the clone's
HEAD, `origin/main`, and the last commit anyone made. There is no drift to check and no
rule-4b window to scope, which is itself the first finding.

## Provenance — a frozen artifact

`repo-facts.sh` and the GitHub API, 2026-08-27:

| Fact | Value | Source |
|---|---|---|
| Last commit | **2026-05-22** (`5dc9490b`) | pin = HEAD = `origin/main` |
| GitHub `pushed_at` | 2026-05-22 | API, `archived: false` |
| Days dormant at read | **97** | — |
| Stars | 48,519 (+756 since 2026-07-28) | API, `stars_at: 2026-08-27` |
| Open issues | 1,825 | API |
| Last PyPI release | **0.86.2, 2026-02-12** | PyPI JSON — 196 days before the read |
| Commits, last 12 months | **336** | `git rev-list --count --since=2025-06-01 --until=2026-05-23` |
| Commits, prior 12 months | **8,393** | same command, shifted a year |
| Top author share | **96.01%** (12,614 / 13,138) | `git shortlog -sn` |

**A 25× collapse between consecutive twelve-month windows**, and the cliff is sharp and
dated: 2025-05 = 367 commits, 2025-06 = 125, 2025-07 = 27. The peak month (2024-08,
1,617) exceeds the entire last year by 5×. 96% of all commits are one person, and the
seventh-ranked contributor has 32 commits — so the cliff is a statement about one
maintainer, not a community.

**The repo says nothing about it.** No NOTICE, no announcement post, no status line in
`README.md`, `CONTRIBUTING.md`, or `HISTORY.md`; `CONTRIBUTING.md` still reads as an
active, welcoming guide. The last 30 commits are model-registry upkeep — roughly 24 of
them add model IDs (`feat: add gpt-5.5 model settings across providers`,
`add Claude Opus 4.7 model settings for Bedrock/Vertex/OpenRouter`) or regenerate the
website.

So the honest description is neither *abandoned* nor *finished*: **a single-maintainer
project in low-energy custodial maintenance — new model IDs get registered, occasional
outside PRs get merged, no architectural work has landed since mid-2025, and nobody has
said anything.**

**Dated, falsifiable prediction** (per the gsd-core discipline — write forecasts with a
number and a date so the next read can score them): *by 2026-11-27, six months past the
pin, the repo will carry fewer than 60 additional commits, ≥80% of them model-settings or
website-regeneration changes, and still no status statement.*

### Custody appears to have moved — `cecli` *(sighted 2026-08-27, API metadata only)*

Checked after the read, when the dormancy finding invited the question *"has anyone
continued it?"*. GitHub reports [`cecli-dev/cecli`](https://github.com/cecli-dev/cecli) as
`fork: true` with `parent`/`source` = `Aider-AI/aider`: renamed, Apache-2.0, its own domain
(cecli.dev), **398 stars**, created **2025-08-02**, shipping releases — v1.3.1 merged
2026-08-23, two days before this read, against 49 forks and 23 open issues of its own.

Two things make the sighting load-bearing rather than trivia. **The timing**: the fork was
created in the same window aider's commit rate collapsed (2025-05 = 367 commits, 2025-06 =
125, 2025-07 = 27). **The subject matter**: its README carries a checklist of *upstream
aider issues it has closed*, and several are repo-map ranking issues — including
[#2405](https://github.com/Aider-AI/aider/issues/2405) *"Bias page ranking toward
active/editable files in repo map parsing"*, [#2688](https://github.com/Aider-AI/aider/issues/2688)
*"Include import information in repo map for richer context"*, and
[#2341](https://github.com/Aider-AI/aider/issues/2341) *"Handle non-unique symbols that
break down in large codebases"*.

**That is independent corroboration of this report's measured cold-start finding.** The
probe below found the ranking selecting 20 language test fixtures out of 33 files and
omitting `base_coder.py` on an empty chat; a third party hit the same weakness in practice
and made "bias ranking toward active/editable files" their headline fix. Two independent
observations of one defect, one measured here and one acted on there.

Scope of this claim, stated so it is not over-read: **API metadata and the fork's README
only.** No source was read, no pin taken, no verification that cecli is a faithful
continuation rather than a divergence. It is a dated sighting, ledgered in
[`tools/candidates.md`](../candidates.md), not an ingested tool. The prediction above is
**left exactly as written** — a forecast edited after the fact stops being an instrument —
but cecli's trajectory is now worth scoring beside it, because "the upstream stays frozen"
and "the work moved" are different worlds and only one of them is about aider.

### The unreleased fix that matters

The published artifact and the source disagree about something users hit immediately.
PyPI's `aider-chat` 0.86.2 declares `Requires-Python: >=3.10,<3.13`. The source at the
pin declares `>=3.10,<3.15` (`pyproject.toml:20`). The widening commit is `975e5a89`
*"Add experimental Python 3.14 support"* (2026-03-09, an outside contributor), 35 commits
before the pin and contained in **no tag** (`git tag --contains 975e5a89` → empty).

So **the released aider refuses Python 3.13 (shipped 2024-10) and 3.14 (2025-10)**, and
the fix has sat in `main`, unreleased, since March. This is a docs/source/run disagreement
of exactly the kind methodology rule 8 exists to catch: the install page says `pip install
aider-chat`, the source supports 3.14, and the artifact a user actually gets does not.

## The distinguishing bet

**That the model should be handed a well-chosen, statically-derived summary of the
repository and asked for text — not given tools and let loose.**

Every other harness deep-read here wagers on an agent loop: the model emits tool calls,
the harness executes them and iterates. aider wagers that if you (a) index the repo
properly, (b) let the human choose the working set, and (c) commit everything so mistakes
are cheap, the model does not need tools at all. The three components below are that bet,
implemented.

It is worth stating that the bet is **coherent, not primitive**. aider is not a
tool-dispatch harness that never got around to shipping tools; it is a different design
that reaches the same goal by other means, and in two places (context assembly, turn-end
verification) it reaches it better than harnesses five years newer.

## The loop — a bounded edit-apply-verify cycle, capped at 3

The entire turn engine is thirteen lines (`aider/coders/base_coder.py:932-944`):

```python
while message:
    self.reflected_message = None
    list(self.send_message(message))
    if not self.reflected_message:
        break
    if self.num_reflections >= self.max_reflections:
        self.io.tool_warning(f"Only {self.max_reflections} reflections allowed, stopping.")
        return
    self.num_reflections += 1
    message = self.reflected_message
```

`max_reflections = 3` is a class attribute (`base_coder.py:101`) exposed as **no CLI flag,
no config key, no environment variable** — `grep -rn "reflection" aider/args.py` returns
nothing. It can be changed only by subclassing.

**aider never sends a `tools` array.** `Model.send_completion` attaches one only when
`functions is not None` (`models.py:1006-1009`), and `functions = None` on the base coder
(`base_coder.py:96`); every coder in `coders/__init__.py` inherits that. The three classes
that set `functions` are dead — two have no importers *and* no `edit_format`, the third is
commented out of `__init__.py`. So in **every reachable configuration**, no tool schema
reaches the model.

What the model can cause is a closed set of five things, all parsed out of free-text
markdown:

| Model emits | Harness does | Gate |
|---|---|---|
| a SEARCH/REPLACE block (or udiff/whole/patch) | writes the file | `confirm_ask` only if the file isn't in the chat, or is new |
| a bare filename in prose | adds the file, **discards the whole reply**, re-prompts | `confirm_ask` |
| a ` ```bash ` fenced block | runs a shell command | `confirm_ask` with `explicit_yes_required` |
| a malformed edit | error text becomes the next user message | none — automatic |
| *(harness-initiated)* | lint/test output becomes the next user message | `confirm_ask`, defaults to yes |

There is no read tool, no grep tool, no list-dir tool. The model cannot *read* a file it
was not given; it can only *name* one and be re-prompted.

**Reflections are shared across causes.** `init_before_message()` zeroes the counter once
per user turn, and all five causes draw from the same pool of 3 — so a turn that burns two
reflections repairing malformed SEARCH/REPLACE blocks arrives at its failing test with one
round left. **Edit-format fragility directly consumes the verification budget.**

One control-flow scar worth recording: the file-mention reflection returns at
`base_coder.py:1567`, *before* `apply_updates()` at `:1585`. A reply that both names a new
file and contains valid edits has **its edits thrown away**.

### H2 — a fourth shape the tally has no bucket for

Design principle [H2](../../docs/design-principles.md) is contested at 3 guard / 2 abstain.
aider is neither, cleanly.

Repetition detection: **absent**, and the surface is wide —
`grep -rniE "repeat(ed)?_?(call|tool|action)|loop_?detect|stuck|no_?progress|identical|oscillat|thrash|livelock|infinite_?loop" --include=*.py .`
returns four hits, all irrelevant (a test comment, a docstring about string matching, two
metadata-dedup lines in a script). Iteration cap: **present, and the most aggressive in
the set at 3.**

So aider is **ceiling-without-detection** — a blanket bound that fires whether or not
progress is being made. A model working through a real cascade of lint errors is cut off
at three exactly as a looping one is, and the halt injects nothing into the model's
context: control simply returns to the human. Neither the guard pole (opencode, hermes,
gemini-cli) nor the abstain pole (codex, pi) describes this. The abstainers' shared
rationale — *a loop guard would be the only bound in a design that otherwise trusts the
model to stop* — is precisely inverted here: aider has **only** the bound.

### H6 — meters everywhere, governors nowhere

aider computes `total_cost` per response including cache-write and cache-hit multipliers
(`base_coder.py:2075-2099`) and prints it every turn. It also counts
`num_malformed_responses`, `num_exhausted_context_windows`, `num_error_outputs`, and
`num_user_asks`.

Consumer-grep on all of them: **the only readers are `benchmark/`.** There is no
comparison of `total_cost` to any threshold anywhere in the codebase — no `--max-cost`, no
budget. **Four counters and a cost meter exist to score the benchmark, not to steer the
loop.**

So the single enforced ceiling is a count of *round-trips*, indifferent to cost, tokens,
time, or files touched. One reflection may rewrite fifty files and spend $8 in a single
200k-token call and nothing objects; four cheap 400-token lint fixes are halted. Per H6 —
*if you meter something you steer the model toward whatever the meter doesn't count* —
aider meters more than most harnesses and governs less than any.

### architect/editor is not `subagents`

`architect_coder.py` is 49 lines. `reply_completed` builds a **second Coder** with the
model's `editor_model`, hands it the architect's prose, and — importantly — zeroes its
history (`cur_messages = []`, `done_messages = []`, `:38-39`), so the editor sees the plan
and nothing else.

It satisfies *isolated* and *second model*. It fails *spawnable*: there is exactly one, it
is not requested by the model, its role is fixed, there is no fan-out, no result-collection
protocol, and it cannot recurse. **`subagents: false`** — a fixed two-stage plan-then-edit
pipeline where stage two happens to be a fresh object.

**Citation trap, recorded because a grep-only read gets it backwards:** the class attribute
`architect_coder.py:9` reads `auto_accept_architect = False`, but `args.py:181` declares
`default=True`, `main.py:1005` passes it, and `base_coder.py:340,354` assigns it over the
class attribute. The architect→editor handoff has **no human checkpoint by default**.

## The permission gate — thin, uniform, and inverted at the edges

All confirmation flows through one function, `InputOutput.confirm_ask` (`io.py:807-923`).
Twenty non-test call sites; **seven** stand between the model and the machine
(`base_coder.py:976, 1772, 2207, 2226, 2456, 2479` and `architect_coder.py:17`). The rest
are setup ceremony — create a git repo, install playwright, analytics opt-in.

What runs with **no prompt at all**:

- **Writes to files already in the chat.** `allowed_to_edit` returns `True` immediately
  (`base_coder.py:2198-2200`). The core action of the harness is ungated.
- **Every commit** — `--auto-commits` default `True`.
- **Pre-emptive commits of the user's own uncommitted work** — `--dirty-commits` default
  `True` (`args.py:446-449`). To get a clean base, aider commits your work-in-progress
  first, without asking.
- **`--auto-lint` and `--auto-test` subprocesses.**

Placement against the set: aider *has* a gate, but it is a single boolean function with
one modifier bit — no policy data, no tiers, no classification, no risk model, no sandbox
beneath. It sits between pi (no gate at all) and gemini-cli (a ~12.8k-line tiered policy
engine); it is warp's six-level chain reduced to one link, **minus warp's flaw**.

### The model is an applicant, never an authority

Warp's `AgentDecided` crack — a model-authored `is_risky: false` self-authorizing — has no
analogue here. Tracing the read side of every gate input: `confirm_ask`'s decision depends
on `self.yes` (CLI), `never_prompts` (human), `group.preference` (human), `default`
(caller-hardcoded), and `explicit_yes_required` (caller-hardcoded). **No field derived
from model output reaches the decision.** The model chooses the *targets* — which commands
to propose, which paths to write — never the verdict.

Related and genuinely virtuous: the "don't ask again" grant is a bare in-memory `set()`
(`io.py:269,902-906`) and the `(A)ll` group preference is a per-batch object. Nothing
persists to disk. **In a category where accumulated escalation state is the standard
failure mode, aider's gate has no memory to poison.**

### `--yes-always` is the *safe* setting, and headless without it is fail-open

`io.py:866-869`:

```python
if self.yes is True:
    res = "n" if explicit_yes_required else "y"
elif self.yes is False:
    res = "n"
```

The sole caller passing `explicit_yes_required=True` is the shell-command gate
(`base_coder.py:2456-2462`). So **`--yes-always` turns model-authored shell commands into
an automatic "no"** — deliberate, and unit-tested at `tests/basic/test_io.py:177-189`. The
blanket approve-everything flag is explicitly carved away from the one irreversible action.

But `--message`/`--message-file` do **not** set `yes_always`; it stays `None`, taking the
interactive branch, where with no TTY `input()` raises `EOFError` and the handler treats it
as *"the user pressed Enter"* (`io.py:882-886`) — and `default` is `"y"` for all seven
agent-loop gates.

| Invocation | Edit unlisted file | Create file | Run model's shell command |
|---|---|---|---|
| `aider -m "…"` (headless, no flag) | yes | yes | **yes** |
| `aider -m "…" --yes-always` | yes | yes | **no** |

**The absence of a human is read as consent, and the safety flag is strictly safer than
its absence.** Contrast gemini-cli, which defaults DENY when headless. No other harness in
the set inverts this way.

And one shipped mode disables the gate by construction: `main.py:546-547` sets
`yes_always = True` whenever `return_coder=True`, whose only production caller is the
Streamlit GUI (`gui.py:71`), which then sets `yes=True` again at `:79`. **`aider --gui`
runs with the permission gate off, with no flag and no notice in the browser docs.**

### Invariants below the gate — essentially none

- **No path containment.** `abs_root_path` is `Path(self.root) / path` → `.resolve()`
  (`base_coder.py:566-574`, `utils.py:96-102`). Python's `/` discards the left operand when
  the right is absolute, and `.resolve()` collapses `..` silently. `allowed_to_edit`
  contains no containment predicate; the four `is_relative_to`/`commonpath` uses in the
  package are in display formatting, `/save`, a common-prefix helper, and the file watcher
  — none in the edit path. The prior deep-dives found *shipped-but-unconsumed* checkers
  (gemini-cli's zod-nulled workspace guard, pi's `--auth-token`); **aider is the other
  failure mode — no checker was ever written.**
- **No symlink policy.** The only symlink work in the repo is a crash fix
  (`utils.py:100`), recorded in `HISTORY.md:19`.
- **gitignore IS an invariant** — `allowed_to_edit` returns early with *"Skipping edits to
  {path} that matches gitignore spec"* (`base_coder.py:2202-2204`), with no prompt and no
  override, not even under `--yes-always`. Plus `.aiderignore` and `--subtree-only`.

### It disables the user's pre-commit hooks by default

`--git-commit-verify` defaults to `False`, and the consumer appends `--no-verify`
(`repo.py:277-279`). The harness whose safety story is *"everything is a commit, just
review it"* removes the one deterministic policy check the user had already installed at
commit time.

### Is the commit a gate?

aider's own framing is that git integration makes review and rollback free. Against the
taxonomy's boundary test it fails as a *gate* on four counts, and the distinction is worth
making cleanly rather than accepting the framing:

1. **It is post-hoc by construction** — `auto_commit` runs *after* `apply_edits` has
   written to disk. A gate decides; a commit records.
2. **`/undo` is one-deep and session-scoped** — it refuses if the hash isn't in this
   session's `aider_commit_hashes`, if the commit has >1 parent, or if any touched file is
   dirty. It cannot undo a shell command that ran between two edits.
3. **The child process escapes it** — `run_cmd(..., cwd=self.root)` is a plain subprocess
   as the launching user. Network calls, writes outside the repo, `pip install`, `rm` are
   all outside git's reach.
4. **It weakens a boundary the user already had** (the `--no-verify` default above).

The commit is a **recovery mechanism**, and a good one. It is not a permission boundary.

## Context assembly — the repo's standing claim falls

This is the report's headline. The category index has carried, and defended through three
deep-dives (warp, gemini-cli, qwen-code), the claim that **no tracked harness holds the
indexed-context-assembly position** — that the axis's most sophisticated retrieval
machinery always ends up on the grep side of its own line, producing a pointer the model
must follow rather than content in the prompt.

**aider breaks it.** The chain, traced end to end:

1. **A persistent on-disk symbol index.** `diskcache.Cache` at `.aider.tags.cache.v4` in
   the repo root (`repomap.py:43,217-222`), keyed by absolute filename, invalidated by
   mtime. Tags are `(rel_fname, fname, line, name, kind)` with `kind ∈ {def, ref}`,
   extracted by tree-sitter using **58 `.scm` query files** (recounted:
   `git ls-files '*.scm' | wc -l` → 58), with a pygments lexical fallback for languages
   whose queries yield defs but no refs.
2. **A real graph ranking.** `nx.pagerank(G, weight="weight", personalization=…)`
   (`repomap.py:525`, networkx pinned at 3.4.2). Nodes are **files**; edges are
   `referencer → definer`, one per (ident, referencer, definer) triple, weighted
   `mul * sqrt(num_refs)` where `mul` is ×10 for a mentioned ident, ×10 for a long
   snake/camel-cased name, ×0.1 for a leading underscore, ×0.1 if more than five files
   define it — and **×50 if the referencing file is in the chat** (`repomap.py:508-509`).
3. **A budget enforced by binary search** over the number of ranked tags
   (`repomap.py:666-706`), accepting anything within 15%.
4. **Content in the prompt.** `to_tree` → `render_tree` builds a `grep_ast.TreeContext` and
   emits **the actual source lines** of each ranked definition plus its enclosing scope
   headers, elided with `⋮` and truncated at 100 characters.
5. **Landing site:** a **user message** followed by a fabricated assistant turn
   (`base_coder.py:750-761`), assembled fresh **every turn** (`:1281`, `:1429`).

Warp's index ends in a `{name, path}` tool result with zero surrounding context lines.
gemini-cli's embedding path is dead code. **aider's ends in bytes in the prefix, sent
automatically, with no model request.** The claim is now false, and the harness that
falsifies it is the oldest and most dormant one tracked.

### Measured, not inferred

RUN probe against the published 0.86.2 artifact, on a local clone of aider itself
(691 files) — `--show-repo-map` at three budgets:

| `--map-tokens` | lines | bytes | files listed |
|---|---|---|---|
| 1024 | 368 | 7,978 | 33 |
| **4096 (default)** | 1,173 | 25,253 | **110** |
| 16384 | 5,217 | 137,760 | 213 |

The default is not a constant: `get_repo_map_tokens` computes
`min(max(max_input_tokens/8, 1024), 4096)` (`models.py:782-789`) → **4096 for any model
with ≥32k context**, doubled to **8192 when the chat is empty**
(`--map-multiplier-no-files`, default 2).

And from a full `--show-prompts` dump: the assembled prompt is 44,853 bytes, of which
**31,852 — 71% — is repo map**, on aider's own repo at defaults with no files in the chat.

### The human's `/add` is the ranking signal

The sharpest measurement. Same 1024-token budget, same repo:

- **Cold** (empty chat): 33 files selected, of which **20 are
  `tests/fixtures/languages/*` test fixtures**; `aider/coders/base_coder.py` — the
  repo's core file — is **absent**. It also picks `asciinema-player.min.js`.
- **Warm** (`--file aider/coders/base_coder.py`): collapses to **13 files, 10 of them real
  `aider/` modules** — `base_prompts.py`, `chat_chunks.py`, `commands.py`, `io.py`,
  `models.py`, `exceptions.py`. Its actual collaborators.

This is the mechanism behind aider's most-complained-about ergonomic. The human adding
files is not merely selecting a working set; it is supplying the **personalization vector**
for the PageRank (`repomap.py:383,422-445`, plus the ×50 edge multiplier). **Cold-start
ranking on aider's own repository is poor; warm ranking is sharp.** The index needs a seed,
and the human is it.

Worth noting what seeds it besides files: `get_ident_mentions` is
`set(re.split(r"\W+", text))` (`base_coder.py:678-682`) — **every word of the current user
message**, unfiltered, no stemming, no length floor. So a PageRank over a tree-sitter
symbol graph is seeded by an unfiltered bag of words. Simultaneously the most principled
and the crudest retrieval in the survey.

### A property agentic harnesses structurally cannot have

`chunks.repo` is rebuilt each turn and **never migrates into `done_messages`**
(`base_coder.py:1036-1046`). Compare any tool-result-based retrieval, where every search
result is permanently welded into history. aider's context assembly has a **bounded,
self-refreshing retrieval slot** — the map is *replaced*, not accumulated. It falls out of
the fake-turn design rather than being argued for, and nobody upstream names it as an
advantage.

### The cache collision — found and fixed three years before hermes hit it

The category index records a structural tension discovered at hermes' drift check: *a
self-modifying agent and a byte-stable prompt prefix are in structural tension*, and hermes'
flagship self-writing skills index was invalidating its own cached prefix, unnoticed by
everyone including its maintainers.

aider has exactly the same collision. Cache breakpoints are at most three
(`chat_chunks.py:28-41`), and **breakpoint 2 is the end of the repo map** — which is
recomputed every turn with a ranking personalized by the current user message. A different
question produces a different map, shattering breakpoints 2 and 3 and the entire
conversation history between them.

aider noticed. `main.py:954-955`:

```python
if args.cache_prompts and args.map_refresh == "auto":
    args.map_refresh = "files"
```

Under `files`, the cache key drops `mentioned_fnames`/`mentioned_idents` and the map
changes only when the *set* of files changes. Prefix stability restored, in two lines.

**Three honest caveats:**

1. **The fix is a silent feature downgrade.** Turning on caching disables per-query map
   personalization — the map's most sophisticated behaviour. No warning is emitted. RUN-
   confirmed on the published artifact:

   ```
   $ aider --show-repo-map                  → Repo-map: using 4096 tokens, auto refresh
   $ aider --show-repo-map --cache-prompts  → Repo-map: using 4096 tokens, files refresh
   ```

   The entire disclosure is one word in the startup banner. **The two flagship features
   are mutually exclusive in their full form, and the trade is made for the user without
   being named.**
2. Even under `files`, the prefix shatters on every `/add`, `/drop`, and **every new file
   the model creates**.
3. `files` makes the map go stale on content edits — the cache key holds no mtimes.

Position against [H5](../../docs/design-principles.md): aider has the *mechanism*
(breakpoints, a keepalive pinger, per-model `cache_control` capability data) but not the
*discipline* — `--cache-prompts` defaults to `False`, the cache meter prints only under
`--verbose`, and the prefix is byte-stable only in a mode the user is silently switched
into. Compare pi, which instruments its own cache waste with an inline dollar figure.

### Compaction — elegant on schedule, absent on demand

`ChatSummary([weak_model, main_model], …)` tries models in order, so **the weak model
summarizes first** (`history.py:114-123`). History is capped at `max_input_tokens/16`
(`models.py:355-358`) — very early. The head is summarized into a single first-person user
message; the tail is kept verbatim; system messages are dropped.

It runs on a **background thread** started after every edit-completing turn
(`base_coder.py:1011-1012`) and joined lazily at prompt-assembly time (`:1278`) — so
compaction overlaps the human's typing. That is more elegant than any synchronous
compaction in the set.

And yet **actual overflow is a terminal error**. `ContextWindowExceededError` is caught,
sets `exhausted = True`, and at `:1536-1547` appends a fake assistant *"FinishReasonLength
exception: you sent too many tokens"*, shows an error, increments a counter, and returns —
the turn ends. No auto-compaction, no retry with a smaller map, no rollover. The pre-flight
check just asks the human *"Try to proceed anyway?"*.

Against [H1](../../docs/design-principles.md) — *treat running out of context as a normal
loop outcome, not an error* — aider is **the cleanest negative instance in the set**. It
compacts beautifully on a schedule and cannot compact on demand at all. Contrast codex's
`new_context_window` tool, opencode's `"compact"` as a peer of `"stop"`, hermes'
`ContextEngine` lifecycle.

### No rules files, and the negative is clean

**`AGENTS.md`: zero occurrences repo-wide** — `git grep -In -i "AGENTS\.md" | wc -l` → 0,
across all 691 tracked files including all 149 `.md`. aider does not honor the cross-tool
convention that ≥5 harnesses now consume.

**`CONVENTIONS.md` is documented but read by no code.** Six files mention it; all are docs,
history, or test fixtures; zero `.py` hits. The documented mechanism is entirely manual —
`/read CONVENTIONS.md` or `read:` in `.aider.conf.yml`. It is an ordinary read-only chat
file with no special handling.

`ROOT_IMPORTANT_FILES` (154 entries) contains no instruction-file name of any kind, and
affects only repo-map ordering. **`rules_files: false` — aider has no automatic
standing-instruction mechanism at all.**

## H7 — an eighth position, and the only one with eval backing

The category index records seven documented positions on model divergence and closes:
*"still no eval backing for any position."* aider is a position nobody predicted and the
asterisk on that sentence.

`MODEL_SETTINGS` is a **YAML resource**, not code — `aider/resources/model-settings.yml`,
**357 entries** (recounted two ways), parsed into a 21-field dataclass at import. What
varies (recounted from the YAML):

| Field | Populated | Values in use |
|---|---|---|
| `use_repo_map` | 338 | `True` only |
| `edit_format` | 333 | `diff` 289 · `diff-fenced` 35 · `udiff` 4 · `whole` 4 · `architect` 1 |
| `weak_model_name` | 300 | **66 distinct** |
| `accepts_settings` | 233 | `[reasoning_effort]` 158 · `[thinking_tokens]` 71 · both 4 |
| `examples_as_sys_msg` | 158 | True 104 · False 54 |
| `editor_edit_format` | 137 | `editor-diff` only |
| `system_prompt_prefix` | 53 | one value: `"Formatting re-enabled. "` |
| `reminder` | 44 | `sys` 43 · `user` 1 |
| `use_system_prompt` | 11 | False only |

**And not one line of model-conditional prompt prose.** Surface: all **17**
`aider/coders/*_prompts.py` modules, grepped for `main_model|self.model|claude|gpt-|gemini|
deepseek` → **two hits, both TODO comments.**

So the eighth position is: **vary the edit format, the message shape, and the reminder
placement per model; hold the prose fixed.** Prose varies only through capability flags
read at assembly time — `lazy` appends a prompt, `overeager` appends another,
`examples_as_sys_msg` inlines few-shot examples into the system message instead of sending
real turns, `use_system_prompt: false` emits the system prompt as a user+assistant pair,
`reminder` chooses trailing-system vs spliced-into-final-user. One prompt body per edit
format, 357 models routed onto them by data.

**And aider publishes a leaderboard measuring exactly the thing it varies** — see § Evals.
That closes the standing "no eval backing" sentence with an asterisk: one harness has
published measurements of its own H7 position, and it is the position that says the
*format*, not the prose, is what differs.

Unknown models fall through 18 substring branches (`models.py:437-598`), then hit this
unconditionally (`:424-435`): every `openrouter/` model is auto-granted `thinking_tokens`
**except** `claude-opus-4.7`, spelled two ways, with the same carve-out duplicated inline
at `:537-542`. This confirms conclusion 15's 2026-08-26 characterization — capability
declared as data with an opt-in check, undermined by one reactively hardcoded id — and adds
that the hardcoding exists in **two** independent places.

## Evals — the strongest instance in the set

`benchmark/` is 22 tracked files (`git ls-files 'benchmark/*' | wc -l`), in-repo and
runnable, with its own `Dockerfile`, `docker.sh`,
per-language test runners, plus `swe_bench.py` and `refactor_tools.py` for two secondary
benchmarks.

**It scores two orthogonal things and separates them** (`benchmark.py:468-588`):

1. **Code correctness** — `pass_rate_1`/`pass_rate_2` from unit tests, across `--tries`
   (default 2): did tests pass first try, and after being shown the failures once.
2. **Edit-format success** — `pct_well_formed = 1 - num_with_malformed_responses /
   completed_tests`, plus `syntax_errors`, `indentation_errors`, `lazy_comments`,
   `exhausted_context_windows`, `test_timeouts`, `seconds_per_case`, `total_cost`.

`benchmark/README.md:12-18` is explicit that the second metric is about **aider's own
design**, not the model's coding ability: *"not just the LLM's coding ability, but also its
capacity to edit existing code and format those code edits so that aider can save the
edits."* Results are versioned in-tree — 14 files under `aider/website/_data/`, each row
carrying `commit_hash`, `versions`, `date`, `command`, `edit_format`, `total_cost` — and
**two of them (`architect.yml`, `code-in-json.yml`) are A/B ablations of aider's own
design decisions**, not model rankings.

**But the corpus is not in the repo, and that is the honest caveat.** `benchmark/README.md:53`
instructs `git clone https://github.com/Aider-AI/polyglot-benchmark tmp.benchmarks/…`;
`EXERCISES_DIR_DEFAULT = "polyglot-benchmark"` resolves at runtime. The task count is
recoverable only from result data — `polyglot_leaderboard.yml` holds **69 rows** whose
`test_cases` values are **223, 224, or 225** (recounted; not the uniform 225 the blog
implies). **The harness is reproducible at the pin; the benchmark is not pinned.** A count
that carries its measure, and the measure has a hole in it.

*(The construction methodology is separately noted at
[`references/papers/2024-aider-polyglot.md`](../../references/papers/2024-aider-polyglot.md),
`read_depth: extract`.)*

### The leaderboard runs a loop the product doesn't have

`benchmark/benchmark.py:848-907` wraps the coder in its **own** outer retry loop
(`--tries`, default 2) that runs the real unit tests and feeds failures back as fresh
instructions. The product default is `--auto-test False`. **So aider's published numbers
come from a test-feedback agent, and the shipped default is not one.** Anyone reading the
leaderboard as a measure of stock aider is reading a different configuration.

## turn_end_gates — `engine`, measured, default-on, with one qualifier

This is the finding that sits oddest with everything above. The harness that cannot call a
single tool ships **the strongest native measured turn-end gate in the set**.

`--auto-lint` defaults to **`True`** (`args.py:542-547`). The chain: `apply_updates` →
`if edited and self.auto_lint` (`base_coder.py:1599`) → `lint_edited` → `Linter.lint` per
edited file. With **no `--lint-cmd` configured at all**, Python files get three fresh
checks (`linter.py:118-134`): a tree-sitter parse for ERROR/MISSING nodes, a real
`compile(code, fname, "exec")`, and an actual subprocess —

```
python -m flake8 --select=E9,F821,F823,F831,F406,F407,F701,F702,F704,F706 \
       --show-source --isolated <file>
```

Failures are wrapped as `# Fix any errors below, if possible.` plus the offending lines
rendered in AST context, and become the next user message.

**RUN-confirmed** against the published artifact, zero configuration:

- a file with a syntax error → `SyntaxError` from `compile()` **and** `E999` from flake8;
- a **syntactically valid** file referencing an undefined name → `F821 undefined name
  'missing_symbol'`, rendered with a `█` marker on the offending line.

The second case is the load-bearing one: a *semantic* error in valid code, caught only
because a real linter ran. This clears the repo's "ran something fresh" bar without
qualification.

**The qualifier, stated rather than buried:** the re-prompt passes through
`confirm_ask("Attempt to fix lint errors?")` (`base_coder.py:1603-1607`). Interactively
that is a one-keystroke `[Yes]`; under `--yes-always` it auto-accepts; and in any
non-interactive mode the `EOFError` handler returns the default, which is `"y"`. So the
human touchpoint exists in the default interactive path and evaporates everywhere else. If
the index's *default-on measured* bar tolerates a default-yes confirm, aider is a second
entry beside the current sole holder (hermes' `verification_stop`); if it demands zero
human touchpoint interactively, aider is a near-miss that becomes a full hit under two very
common invocations.

Two ordering scars: the lint reflection `return`s at `:1607`, **skipping shell commands and
the test entirely** for that round — a turn whose edits both fail lint and break tests only
ever sees lint errors until lint is clean. And with `--auto-test` on but no `--test-cmd`,
`cmd_test` returns immediately and `test_outcome = not None = True` — **the harness records
a passing test that never ran** (confined to reporting; nothing in control flow reads it).

## MCP — absent from the product and from its entire history

The taxonomy pre-registered this exact question. §2's loop component records a strain:
reach has a claim on being a fourth component, *"not promoted because reach doesn't
currently discriminate (the `mcp` column is a uniform ✓)"*, with the trigger named as
*"verified MCP-client divergence (aider's matrix row, unread today, is the likeliest
source)"*.

**It fires.** MCP appears in the aider tree exactly once, and it is an anti-dependency
comment (`requirements/requirements.in:46-49`):

> `# The proper dependency is litellm[proxy], but it installs`
> `# mcp which is a pywin32 dependency that fails on linux CI.`

Surfaces searched, per methodology rule 1b — the negative is only as good as this list:

| Surface | Result |
|---|---|
| Every tracked file, whole-token, case-insensitive | **1 hit** (the comment above) |
| Spelled-out `model.context.protocol` | 0 |
| All 5 lock files and 7 `.in` manifests + `pyproject.toml` | 1 (same comment) |
| In-tree website — 379 files under `aider/website/` incl. docs, blog, `_posts` | 0 |
| Filenames on disk incl. gitignored | 0 |
| **All 13,138 commit messages, all refs** | **0** |
| **Every file path ever added in repo history** | **0** |

**This is not a dormancy artifact.** MCP was announced in November 2024; aider shipped
1,292 commits in March 2025 alone and remained in high-velocity development through June
2025. It shipped roughly four thousand commits during MCP's adoption window and never
wrote the acronym down.

**And the reason is architectural, which reframes the trigger.** aider has no tool registry
— edits are markdown fences parsed by regex, and native `tool_calls` are only ever read
defensively into a legacy single-function slot. **There is no socket for MCP to plug
into.** So the reach-shaped finding has a loop-shaped *cause*, and it produces a better
answer to the index's open question — *"does universal MCP support make category 6
genuinely portable in practice, or only in principle?"* — than a bare ✗ would: **MCP is
portable across tool-dispatch harnesses, and aider marks the boundary of that class.**
An edit-format harness cannot host MCP without becoming a different harness.

## Stack & repo shape

Pure Python; 691 tracked files — `md(149) py(147) mp3(111) scm(58) jpg(37) yml(28)`. One
package, no monorepo. The 58 `.scm` files are the tree-sitter queries the repo map is built
from, split across two directories: `tree-sitter-language-pack/` (31 languages, tried
first) and `tree-sitter-languages/` (27, a fallback that is vestigial — the pack is a hard
pin in `requirements.txt:422`, so the fallback branch never executes). The 111 `.mp3` files
are voice-input assets. `aider/website/` carries 379 files — the docs site and all
published benchmark results live in-tree.

## Bleed

- **category 1** — reaches every provider through **a single provider abstraction, LiteLLM**
  (`aider/llm.py:16-45`, lazily imported because `import litellm` costs 1.5 s). Zero direct
  provider SDKs; the last one was removed (`HISTORY.md:15`). 357 tuning entries across 14
  provider prefixes (openrouter 85, openai 50, azure 38, vertex_ai 25, gemini 22, …).
- **category 3** — the relation is **null, and deliberately so.** Zero sandbox code, zero
  worktree code. A published Docker image exists (`paulgauthier/aider`) but it is an
  *install* vehicle the user drives with `docker run -v $(pwd):/app`, not an environment the
  harness manages — so none of `bundle | bind | internalize | inhabit` fits and the field
  stays unset.

  What makes this a *considered* null rather than pi's silence: **aider states the
  confinement argument in its own repo and scopes it to the eval.**
  `benchmark/README.md:22-27` reasons that LLM code executing *"without any human review or
  supervision"* needs a container, and gives `sudo rm -rf /` as the example. Meanwhile the
  user-facing Docker page frames the container's isolation as a **drawback**
  (`docs/install/docker.md:56`): *"When you use the in-chat `/run` command, it will be
  running shell commands inside the docker container… which may make it tricky to `/run`
  tests."* The project understands blast radius, ships an image, and applies the reasoning
  only where it is measuring itself.
- **categories 4, 5 and 6** — no attachment surface. No hooks, no plugin API, no
  entry-points group, no MCP, no skills, no rules files. The only extension seam is `/load`
  (`commands.py:1465-1492`), which replays a file of slash-commands — scripting, not hooks.
  **aider is the least extensible harness tracked**, and the H8 reading is unusual: the
  waist is narrow because nothing was ever bolted on, not because capability was pushed to
  the edges as data. There are no edges.

## Cost model

Open source (Apache-2.0); you pay inference against whichever model you point it at. The
published artifacts are the PyPI package `aider-chat` and two Docker Hub images. Telemetry
is opt-in — `--analytics` defaults to `None`, and `analytics.py:85` refuses to send unless
`asked_opt_in`; declining sets `permanently=True`.

## Self-authorship — a headline number outliving what it measures

aider attributes its own commits: `--attribute-author`/`--attribute-committer` rewrite the
author to `"{user.name} (aider)"` (`repo.py:294`). **Recount: 3,661 of 13,138 commits
(27.9%) carry an `(aider)` author.** `scripts/blame.py` turns that into the published
"aider wrote xx% of the code" figure, and `docs/faq.md:282-289` states the measure honestly:
`git blame` per release, **source files only, not docs or prompts**.

The numbers, each with its date:

| Where | Figure | Date |
|---|---|---|
| `HISTORY.md:20` (unreleased main = the pin) | **62%** | 2026-05-22 |
| `blame.yml` last entry, `v0.86.0` | **87.75%** — 222 of **253** lines | 2025-08-09 |
| `README.md:35` badge | `🔄 Singularity 88%` | from that same v0.86.0 entry |

Read the denominators: v0.86.0's 87.75% is 222 lines out of **253 total new source lines in
an entire release** — against 1,706 lines two releases earlier. **The percentage stayed
impressive while the thing it measures nearly stopped.** This is precisely what the repo's
*"a count carries its measure"* rule exists to catch — and to aider's credit, its own FAQ
publishes the measure, which is more than most.

## Surprises

1. **The harness that cannot call a single tool runs a real verifier on every edit by
   default.** I expected `--auto-lint` to shell out to a command nobody configures. It is
   the opposite: zero-config, three fresh checks per Python edit, AST-contextualized errors
   fed back as a user message — `engine` grade, measured, default-on. Not even the 2026-era
   tool-dispatch harnesses reliably do this.

2. **`--yes-always` makes aider *safer* in the dimension that matters most.** The blanket
   approve-everything flag returns an automatic **"no"** for model-authored shell commands
   (`io.py:866-867`, unit-tested), while the *absence* of the flag in headless mode
   executes them via the EOF→default-yes path. A 2023-vintage codebase encoded "yes to
   everything must not mean yes to arbitrary execution" before the permission-subsystem
   vocabulary existed — and simultaneously left the no-human case fail-open.

3. **aider found the hermes cache bug three years early, fixed it in two lines, and the fix
   silently disables its own headline feature.** Correct diagnosis, correct fix, no
   warning: `--cache-prompts` and per-query repo-map personalization are mutually exclusive
   and the banner changes one word.

4. **`use_repo_map` — set on 338 of 357 model entries, assigned by 16 heuristic branches,
   documented — is read by exactly one unreachable line.** `base_coder.py:488` sits behind
   `if map_tokens is None`, and nothing anywhere passes `map_tokens=None` (`Coder.__init__`
   defaults it to 1024; `main` always resolves it to a positive int). Nineteen deliberately
   excluded weak models get a repo map anyway. Prior deep-dives found shipped-and-unread
   *flags*; this is the highest-cardinality instance yet — 338 populated cells feeding a
   dead branch.

5. **The browser GUI ships with the permission gate off**, by construction, with no flag
   and nothing in its docs.

6. **aider auto-commits the user's own uncommitted work without asking** to get a clean
   base — and disables the user's git pre-commit hooks by default while telling a safety
   story built on commits.

7. **Path containment was never written.** Not shipped-and-unconsumed like gemini-cli's
   zod-nulled checker or pi's `--auth-token` — simply absent, in a harness that writes
   model-chosen paths.

8. **A three-year-old off-by-one skews the ranking.** `repomap.py:309` appends the last
   captured node a second time (the statement sits outside its inner loop), duplicating one
   `Tag` per capture group per file and inflating `sqrt(num_refs)` edge weights. In a repo
   with 13,138 commits, a pinned tree-sitter stack, and a public leaderboard, the input to
   the PageRank has been subtly wrong the whole time.

9. **The map's budget is enforced against an estimate.** For text ≥200 characters,
   `token_count` samples every hundredth line and extrapolates by character ratio
   (`repomap.py:89-101`), and the binary search accepts anything within 15%. The
   "4096-token repo map" is a ±15% target measured by a 1% sample — a count that does not
   carry its measure, inside the harness whose defining feature it is.

10. **No MCP, as an explicit written refusal.** The single `mcp` token in three years of
    history is a comment explaining a dependency they avoid.

## Open questions

- **Does the default-on measured gate survive contact with a real session?** The lint gate
  is verified in source and RUN-confirmed in isolation, but the confirm-then-reflect path
  was never exercised end to end against a live model (no API call was made). A scripted
  `aider -m` run with a real key would settle whether the three-reflection budget is
  actually reached in practice and how often lint eats it.
- **Is the headless fail-open exploitable end to end?** Tract C's table is strong code
  inference; the confirming test is an `aider -m` run with stdin from `/dev/null` against a
  prepared reply containing a `bash` fence, checking whether the command executes. Not run
  (no live model call was made in this read).
- **What does the cold-start ranking weakness cost on a repo that isn't aider's?** The
  20-of-33-are-test-fixtures result is one measurement on one repository whose `tests/`
  tree is unusually fixture-heavy. Worth repeating on two unrelated repos before
  generalizing.
- **Does `--auto-test`'s untrusted-content path matter?** `cmd_test` injects subprocess
  output into the model's context on any non-zero exit with no prompt
  (`commands.py:1006,1024-1025`). Default-off, but one flag away, and the content is
  whatever the test suite prints.
