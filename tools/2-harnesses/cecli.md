---
# PIN MOVED 2b8c49bf → e49b18e26 (= tag v1.6.1) at the 2026-09-24 release re-read
# (rule 4b: a pin moves only with a re-read; this was one — two Opus tracts, release
# substance + per-claim confrontation at both pins, main-session spot-verification, wheel
# probe). The 2026-09-09 survey and its run probe stay dated as such; every citation below
# was re-located at the new pin and the survey's own-pin defects corrected in place.
name: cecli
category: 2
surfaces: [terminal]   # the Textual TUI is the default surface (main.py:862: launches unless `--linear-output` or `CECLI_TUI=false`); aider's Streamlit `--gui` was not checked for survival — not claimed either way
execution: local
residency: session
environments: [host]   # docker/ install image inherited from aider, not re-checked; `host` is what the read traced
maker: cecli-dev
url: https://github.com/cecli-dev/cecli
license: Apache-2.0
access: open-source
stack: [Python]
version: v1.6.1
commit: e49b18e26
first_commit: 2023-04-03   # aider's first commit — the fork keeps the full history (13,048 shared commits with aider main; see § Stack & repo shape)
stars: 408
stars_at: 2026-09-24   # repo-facts.sh; 405 at 2026-09-09
read_at: 2026-09-24   # v1.6.1 release re-read (window 103 commits, 2b8c49bf..e49b18e26); survey 2026-09-09 @ 2b8c49bf
depth: survey   # 2026-09-09, targeted source read at the pin for ONE question — does the aider fork keep the ranked-index context-assembly bet (conclusion 17) or drift toward tool dispatch? — plus the registry keys aider carried, each re-checked at the fork's own source by grep (one Opus reader, load-bearing citations spot-verified in the main session). NOT traced: the loop end to end, the TUI, the ACP server, the Cymbal search index, the memorizer subagent's runtime. RUN probe added 2026-09-09 on the published 1.4.1 artifact (`pip install cecli-dev==1.4.1`), offline dumps only, no API call — § Run probe; the probe also caught two source misreads in the first write-up, corrected in place and listed in § Surprises RE-READ 2026-09-24 at v1.6.1 (§ Release re-read): release substance by component + every citation confronted at both pins; still survey depth — the loop end to end, the TUI, the ACP server and the Cymbal index remain untraced
harness_features:
  mcp: true            # client, three transports + OAuth: McpServerManager (cecli/mcp/manager.py:15 @ e49b18e26; :7 at the survey pin), HttpBasedMcpServer (cecli/mcp/server.py:368; was :327), `--mcp-servers` / `--mcp-servers-files` / `--mcp-transport` (args.py:484-497; was :478-491). NEW at v1.6.1: per-server `timeout` (default 2 min, mcp/server.py:348-356). And the built-in tools are themselves exposed as a synthetic MCP server named "Local" (the name is set at the instantiation site, agent_coder.py:351,365-368 — corrected 2026-09-24: `mcp/server.py:608` was the `LocalServer` class definition, and the string "Local" appears nowhere in that file; class now at mcp/server.py:654) — see § The distinguishing bet
  hooks: true          # six lifecycle types START/ON_MESSAGE/END_MESSAGE/PRE_TOOL/POST_TOOL/END (cecli/hooks/types.py:7-12 — range corrected 2026-09-24, the file is unchanged), registered as JSON via `--hooks` (args.py:425-427 @ e49b18e26; was :419-421)
  context_retrieval: ranked-index   # KEPT and invested in: rustworkx.pagerank over the weighted file-reference graph (repomap.py:1008, port from networkx 2025-12-19 8bd4550c), tags cache `.cecli/tags.cache.v9` (repomap.py:112,118), injected (integration.py:467-468 @ e49b18e26; :481-482 at the survey pin — `repomap.py` itself is BYTE-IDENTICAL at both pins, blob dbb9739d, 0 commits in the window) as a role="user" message (helpers/conversation/integration.py:481-482) by the same call in every coder incl. agent mode (base_coder.py:2543 = agent_coder.py:638). Default budget is aider's formula min(max(ctx/8,1024),4096) (models.py:1132-1139, wired main.py:1205), ×2 on an empty chat; RUN 2026-09-09 on the published 1.4.1 artifact: the map is 84% of message bytes in `diff` mode and 79% in `--agent` mode (§ Run probe). Injection is DELTA-shaped: each turn appends only files/tags not already in the conversation (repomap.py:1246-1274, integration.py:370)
  turn_end_gates: engine   # --auto-lint default True, unchanged from aider (args.py:946-951 @ e49b18e26; was :929-932); a second, default-OFF gate joined 2026-09-04 (#673): with --auto-test, failing tests abort the auto-commit and reflect the errors back (base_coder.py:2999-3008 @ e49b18e26, was :2922-2932; --auto-test default False, args.py:940-943)
  tool_approval: prompt  # confirm_ask kept as the gate shape (io.py:1283-1286); `--max-tool-calls` 25 per message (args.py:340-345 @ e49b18e26; was :334-338), multiplied ×400 in agent mode (agent_coder.py:156) — effective agent default 10,000
  gate_model_authority: none  # the gate surface is aider's verbatim (io.py byte-identical at both pins): confirm_ask, human-answered
  unbypassable_gates: false  # inherits aider's `--yes-always`; io.py unchanged across 103 commits
  headless_approval: allow   # FAIL-OPEN kept verbatim from aider: `default="y"` (io.py:1286 — off-by-one corrected 2026-09-24; `_confirm_ask`'s signature is :1283-1286) and EOF "treated as if the user pressed Enter" → `res = default` (io.py:1374, 1380, 1463). io.py is byte-identical at both pins: the gate did not move for a second release cycle
  skills: true         # Anthropic-compatible SKILL.md loader: directory scan (helpers/skills.py:280-285 @ e49b18e26; was :253-258), frontmatter name+description required (:329-343), `allowed-tools` read (:350); only NAMES sit in the always-on capabilities block (base_coder.py:1043-1049; was :984-990). NEW at v1.6.1: `.agents/skills` lookup beside `.cecli/skills` (helpers/skills.py:69-79) and a network skill installer, `/import-skill` — § Release re-read 5, bodies load on demand via ResourceManager / `/load-skill`
  subagents: true      # SubAgentCoder (coders/sub_agent_coder.py:14); Delegate tool dispatches an array of tasks in parallel (tools/delegate.py:136-143, `asyncio.gather` — call site substituted 2026-09-24 for the tool's own SCHEMA text at :24-62, which is testimony); fresh coder per subagent (helpers/agents/service.py:950-969 @ e49b18e26; was :935-954). NEW at v1.6.1: subagents start with an EMPTY file context unless `keep_files: true` (service.py:622-634, a7f4996fb 2026-09-12) — and have never received the repo map (`map_tokens=0`, service.py:618 at both pins); return path is a SUMMARY STRING (delegate.py:126-180; Yield's `summary` arg, tools/_yield.py:33-37); max_sub_agents 30 (agent_coder.py:104)
  rules_files: true    # AGENTS.md then CLAUDE.md in the coder root, auto-loaded when no explicit rules are configured, re-read from disk every turn under MessageTag.RULES (helpers/conversation/integration.py:509-515 @ e49b18e26; was :523-529). aider had none. Narrowed at v1.6.1: suppressed for the memorizer sub-agent (integration.py:500-503)
  model_agnostic: true # LiteLLM kept as the single provider abstraction; tools go on the wire as OpenAI-style `tools=` (models.py:1386, base_coder.py:3842 @ e49b18e26; were :1383/:3764). NEW at v1.6.1: a hand-written Mistral adapter beside LiteLLM (helpers/llms/providers/mistral.py, 177 lines)
  # lsp / ptc / plan_mode / context_compaction: NOT checked at this depth. The README claims compaction is now "observational memory sub agent" decision records; not traced, so no cell
---

# cecli

> **Survey, 2026-09-09.** One question, answered from source at `2b8c49bf` (= v1.4.1,
> HEAD of `main`); the pin's history is aider's own, so the report reads as a
> divergence study against the [aider deep-dive](aider.md) (pin `5dc9490b`). Promoted
> from the [candidates ledger](../candidates.md) (row added 2026-08-27).

## What it is

The continuation of aider under a new name. Forked on GitHub 2025-08-02, last commit
shared with `Aider-AI/aider` main is `7301d452` (2025-12-11, aider PR #4698); since
then **2,686 cecli-only commits against 90 aider-only** (`comm -12` over both
`rev-list`s, then `rev-list --count <shared>..HEAD` in each clone). Same license,
same Python stack, same `first_commit`. Ships: v1.4.1 on 2026-09-05; a `v1.5.0`
release branch runs 52 commits ahead of `main` with `v1.5.0rc10` tagged 2026-09-09
(`git rev-list --left-right --count 2b8c49bf...v1.5.0rc10` → `0 52` — the survey wrote
`main...`, a moving ref that gives `51 0` today; corrected 2026-09-24). ~~The release
branch is not pinned; a re-read waits for the v1.5.0 tag on `main`.~~ **It landed:**
v1.5.0 merged to `main` 2026-09-12 (`4b75620b2`, PR #675), followed by v1.5.1 the same
day, v1.6.0 (09-19) and **v1.6.1 (09-23, `e49b18e26`, this pin)** — § Release re-read.

## The distinguishing bet

**aider's bet survives the succession, and the fork doubled down on it.** The question
the candidates row asked — does the one tool holding the ranked-index position keep it
under active maintenance, or drift to the tool-dispatch consensus — has a mechanism
answer: **hybrid, with the index as the constant and the tools as an opt-in.**

- **The index is kept and improved.** The ranker is still PageRank over the
  file-reference graph, ported from `networkx` to `rustworkx` for speed
  (`repomap.py:1008`, commit `8bd4550c` 2025-12-19). The three upstream aider issues
  the README headlines are real code: the chat-file edge multiplier went ×50 → **×64**
  (`repomap.py:967-968`), every edge is gated on **same file extension**
  (`:962-963`), and weights decay with **path distance** between referencer and
  definer, `use_mul * 2 ** (-path_distance)` (`:986-988`) — that is aider issue #2405
  ("bias toward active/editable files"), the exact weakness the deep-dive measured
  (cold map picking 20 language fixtures of 33 files). Import-aware edges
  (`check_import_match`, `:572-597`, gated at `:855-856`; #2688) and a logarithmic
  down-weight of over-defined identifiers (`:925-927`; #2341) are the other two.
  Provenance by pickaxe (`git log -S '<literal>' -- aider/repomap.py cecli/repomap.py`):
  the three #2405 mechanisms landed in **two commits three weeks apart** — the extension
  gate in `50826578` (2025-10-19, subject cites cecli's own umbrella issue #45), the
  multiplier and path decay in `f079aa0b` (2025-11-07, a powers-of-2 refactor); the #2341
  down-weight is in `50826578` too. The README's one-checkbox-per-upstream-issue table is
  a retrospective mapping onto commits that were not authored per issue — the mechanisms
  are real, the tidy attribution is not.
- **The injection shape is unchanged.** The map is built into a `role="user"` message
  (`helpers/conversation/integration.py:481-482`), tagged `REPO`, and added by the same
  one-line call in the base coder and in agent mode
  (`base_coder.py:2543` = `agent_coder.py:638`). Agent mode does not shrink it: `grep
  -n "map_tokens\|use_repo_map" cecli/coders/agent_coder.py` → 0 hits, and the agent
  prompt defines `repo_content_prefix` (`prompts/agent.yml:17`), which is the gate the
  base coder uses to build a map at all (`base_coder.py:750-752`; `:809-811` @ e49b18e26). The default budget is
  aider's formula — `min(max(max_input_tokens/8, 1024), 4096)` (`models.py:1132-1139`),
  wired at `main.py:1205` (`:1232` @ e49b18e26), ×2 on an empty chat
  (`--map-multiplier-no-files`, default 2, `args.py:599-603`, applied at
  `repomap.py:291-299` — citation supplied 2026-09-24); the literal `1024` at `base_coder.py:744` is a fallback
  `main.py` never reaches (*corrected 2026-09-09 by the run probe; the first write-up
  cited the fallback as the default*). New around it: **the injection is a delta.** The
  ranker keeps a `combined_map_dict` of everything already shown and renders only
  `new_dict` — files and tags not yet in the conversation (`repomap.py:1246-1274`,
  `integration.py:369`) — as a fresh REPO-tagged user message, deduplicated by content
  hash (`manager.py:144,185-188`), the old ones left in place; once ≥20 REPO messages
  accumulate a third are purged and the combined dict reset (`integration.py:431-441`;
  the whole path is `:417-427`/`:467-478` @ e49b18e26, shifted −14 lines by hunks that do
  not touch it).
  That is the fork's answer to the caching collision the deep-dive recorded: the map
  never rewrites the cached prefix, it appends to it. The first write-up credited a
  dedicated cache breakpoint on the map (`chat_chunks.py:64-66`); that code is dead —
  see § Surprises 5.
- **Tool dispatch is added, not substituted, and it is not the default.** 22 registered
  tools (`tools/__init__.py:30-53`, entries at `:31-52` — range corrected 2026-09-24;
  `TOOL_MODULES` unchanged at v1.6.1; 23 files by `ls cecli/tools/*.py | wc -l`, one is
  `__init__.py`), sent on the wire as OpenAI-style function schemas via LiteLLM
  (`models.py:1383`), dispatched from `tool_call.function.name`
  (`agent_coder.py:839-930`). They exist only in `--agent` mode: the built-ins are
  wrapped as a synthetic MCP server named `"Local"` (`mcp/server.py:608`), and
  switching to any non-agent coder disconnects it (`base_coder.py:381-386`). A fresh
  user gets aider's per-model edit format: `--edit-format` defaults to `None`
  (`args.py:242-248`) → `main_model.edit_format` (`base_coder.py:296-301`) → `"diff"`
  (`models.py:111`); `grep -o "edit_format: [a-z-]*" resources/model-settings.yml | sort
  | uniq -c` → 315 `diff`, 164 `editor-diff`, 35 `diff-fenced`, 4 `whole`, 4 `udiff`,
  1 `architect`, **0 `agent`**.

So the fork's answer to "index or tools?" is *both, layered*: the passive index
feeds every turn regardless of mode, and model-called retrieval (`ExploreCode`, backed
by a **second**, third-party index — the Cymbal library, `tools/explore_code.py:31-35`)
sits on top when the user opts into agent mode. For conclusion 17 this is the stronger
outcome: the position was not a dormant tool's leftover; the people who picked the
code up made it their first roadmap item.

## Main features

The four absences the aider deep-dive verified (MCP, hooks, subagents, skills) are all
present at this pin, plus rules-file auto-load and an ACP server — the frontmatter
cells carry the citations. Two shapes worth naming: the subagent return path is a
**summary string** (the compact return path `docs/README.md` § Context engineering says
isolation needs), and skills follow Claude Code's progressive disclosure (names
always on, bodies on demand). `hashline` is one of sixteen
`EDIT_FORMAT_MAP` entries and one of four `store_const` edit-format shortcut flags
(`--ask`, `--architect`, `--agent`, `--hashline`; `args.py:249-276`,
`coders/__init__.py:47-64`, both counts at `2b8c49bf` — *the survey wrote "a fifth edit
format", an ordinal no measure at the pin produces; corrected 2026-09-24*). Its transform
is **not** a hash on every line (*corrected 2026-09-24 at the survey's own pin: the read
cited the wrapper's docstring, `helpers/hashline.py:22-31`, not the engine*):
`HashPos.format_content` (`helpers/hashpos/hashpos.py:117-138`) leaves blank lines bare
(`:122-124`), prefixes every line whose text occurs exactly **once** in the file with the
constant token `UNIQUE_HASH_DELIMITER = "——"` (`:7`, `:128-130`), and only for
**repeated** lines emits a Base1024 id derived from `xxhash.xxh3_64` of the line text
(`:89-90`, `:132-136`). Hashline addresses *ambiguous* lines by hash and unique lines by
their own text — a disambiguator on top of SEARCH text, not a replacement for it.

## Stack & repo shape

`repo-facts.sh` at the pin: 15,734 commits, 1,074 tracked files, 519 `.py`, 58 `.scm`
tree-sitter queries (aider's count, kept), 111 `.mp3` (aider's, kept). `grep_ast` and
the tree-sitter language pack were vendored in-tree
(`helpers/grep_ast`, `566a615d` 2026-04-25). Prompts moved from Python classes to 21
YAML files under `prompts/`; a mode's map eligibility is now data (`repo_content_prefix:
null` in `wholefile_func.yml:20`). Besides `main`, the remote carries a per-release branch for every published version plus
a handful of named experiments (`coroutine-experiment`, `domain-refactor-experiment`,
`llm-reduction`, `tui-experiment`, `subagents`; present at both pins). *Corrected
2026-09-24: the survey said "nine remote branches" with no measure; the clone shows 170
(`git branch -r | grep -v HEAD | wc -l`), almost all release branches — a bare ref count
is clone state, not a fact about the project.*

## Run probe (2026-09-09)

Published artifact `cecli-dev==1.4.1` (PyPI, = the pin's tag), offline `--show-repo-map` /
`--show-prompts` dumps with `--model gpt-4o` and no API key, on a git corpus rebuilt from
the pin's working tree (1,074 tracked files — cecli's own repo, the fork counterpart of
the deep-dive's aider-on-aider run). Byte counts, like the deep-dive's.

| `--map-tokens` | files listed | lines | bytes |
|---|---|---|---|
| 1024 | 101 | 329 | 8,148 |
| **default** (= 4096 for a 128k model, ×2 empty chat) | **252** | 1,010 | **28,047** |
| 4096 explicit | 252 | 1,001 | 27,618 |
| 16384 | 373 | 2,729 | 90,210 |

The map is no longer source lines: `--use-enhanced-map` (always on, § Surprises 1)
renders `### path` + `- name (kind, line N)` summaries, so a budget buys ~3× the files
aider's did at the same byte cost (aider at 1024: 33 files / 7,978 bytes; cecli: 101 /
8,148). Cold-ranking bias, re-measured: 43 of the default 252 files are `tests/`
fixtures-or-tests by path (`grep '^### ' | grep -c tests/`; 73 under `tests/` in all),
against the deep-dive's 20-of-33 on aider — the #2405 gating moved it, the seed
problem did not vanish.

*Corrected 2026-09-24 from source: the table's "default" and "4096 explicit" rows are the
same configuration for a 128k model. `--map-multiplier-no-files` defaults to 2
(`args.py:599-603` @ `2b8c49bf`) and `repomap.py:291-299` applies it to `max_map_tokens`
however that value was set, so both rows ran at an effective 8,192 — which is why both
list 252 files. The probe measured three budgets (2,048 / 8,192 / 32,768), not four.*

**Map share of the assembled prompt, first turn, empty chat** (`--show-prompts`,
role prefixes stripped, per-message bytes):

| Mode | messages | message bytes | map bytes | map share of messages | + tool schemas on the wire | map share of the whole |
|---|---|---|---|---|---|---|
| default (`diff`) | 7 | 32,978 | 27,558 | **83.6%** | none | 83.6% |
| `--agent` | 6 | 34,598 | 27,472 | **79.4%** | 22 schemas, 18,041 bytes (compact JSON of every `SCHEMA` in `ToolRegistry.build_registry({})`) | **52.2%** |

aider's 71% was 31,852 of 44,853 bytes (the deep-dive's own repo, 4096 default). In
agent mode the four `<context …>` blocks and the 3.6 KB system prompt take 7 KB; the
tool schemas, which `--show-prompts` does not print because they travel as `tools=`,
are the real competitor at 18 KB. The map is the largest single thing on the wire in
both modes.

**The delta mechanism, exercised offline** (`RepoMap.get_ranked_tags_map` called
directly across five simulated turns, 4096 budget, `.py` files only):

```
t1 empty chat                → combined=116 files, delta=116 files / 247 tags
t1 again, same query         → combined=116,       delta=116 (map_cache hit returns the same tuple → same hash → no second message)
t2 mention pagerank idents   → combined=116,       delta=0
t3 add base_coder.py to chat → combined=126,       delta=34 files / 73 tags
t4 mention cache_control     → combined=126,       delta=0
```

Re-ranking on mentioned identifiers alone produced no delta on this corpus; adding a
file to the chat did (the ×64 multiplier pulling 34 collaborators in). The appended
message on t3 is a fifth of the first — the prefix ahead of it untouched.

## Surprises

*(Heading restored 2026-09-24: three references — the frontmatter, § The distinguishing
bet, and `docs/design-principles.md` — pointed at a section that had never been given
its heading; the six items sat under § Run probe.)*

1. **`--use-enhanced-map` is `store_true` with `default=True` and help text reading
   "(default: False)"** (`args.py:506-510`; `:512-517` @ e49b18e26, unchanged); no `--no-` form exists. Import-aware
   ranking is on for everyone and the flag is a no-op — a docs-vs-source gap inside the
   tool's own CLI help. Two more releases went past it untouched.
2. **The gate surface is aider's, verbatim.** Same fail-open `confirm_ask`, same
   `--auto-lint` default, while the reach grew from zero tools to 22 plus MCP plus
   subagents with an effective 10,000-tool-call ceiling per message. The permission
   posture did not move with the capability. **Not a snapshot, a trend**: `io.py` is
   byte-identical at v1.6.1 while the window added a rate governor, schema introspection
   and a network skill installer (§ Release re-read).
3. **A real SQLite/FTS5 "facts" store** (`.cecli/memory.v*/cache.db`,
   `helpers/memory/db.py:44-100`), written by the `memorizer` subagent through the
   `SearchFacts` tool, whose docstring claims it is "Only accessible to the memorizer
   sub-agent" (`tools/search_facts.py:1-3`) — but the same FTS5 store is also read
   directly by a registered user command, `/search-memory`
   (`commands/search_memory.py:14-16,29,39`; registered `commands/__init__.py:76,171` at
   `2b8c49bf`), with `/auto-memory` beside it. *Corrected 2026-09-24: the survey read the
   tool's docstring as a statement about the store's reachability; the command registry
   contradicts it at the same pin — rule 4a's founding shape, inside the surprise that
   names it (5 below).* What survives: a category-5 mechanism arriving inside a
   category-2 tool with a subagent as its *writer*, not a plugin.
4. The **`Yield` tool is the "finished" tool** (`tools/_yield.py:15-24`), doing double
   duty for "wait for subagents" and "return to the user".
5. **Three cache-placement mechanisms in the tree, one live per route — and the two
   with the interesting comments are dead** (found 2026-09-09 while run-checking the
   first write-up's claim). `ChatChunks.add_cache_control_headers`
   (`coders/chat_chunks.py:48-71`, "The repo map is its own cacheable block") has no
   caller — `ChatChunks` is never instantiated (`grep -rn ChatChunks --include=*.py .`
   → the class and one "Old system" comment at `base_coder.py:3476`); its penultimate
   marker is a no-op besides (`:71` passes the `None` return of the inner call).
   `ConversationManager._add_cache_control` (`helpers/conversation/manager.py:655-748`)
   has no caller either. What runs: non-Anthropic routes hand LiteLLM three
   `cache_control_injection_points` — the system message and the last two messages
   (`models.py:1421-1426`); the Anthropic messages route requests vendor-side
   automatic caching with one top-level `cache_control` (`helpers/llms/domains/messages.py:99-104`).
   **Neither gives the map a breakpoint.** The prefix is protected by the delta
   injection above, not by block structure — the lesson for this repo is that a line
   citation must be a *call site*, not a definition: dead code has line numbers too.
6. **aider's silent `--cache-prompts` downgrade survives verbatim** (`main.py:1195-1196`:
   `auto` → `files` refresh) but is now largely vestigial — under delta injection a
   re-ranked map costs an appended delta, not a rewritten prefix, so the two lines
   trade personalization for a stability the conversation manager already provides. Not
   run-measured across live turns (no API spend at survey depth).

## Release re-read — v1.6.1 (2026-09-24; pin 2b8c49bf → e49b18e26)

Two Opus tracts (release substance + provenance; per-claim confrontation at both pins),
seven load-bearing claims re-run in the main session before writing, and the published
wheel compared to the tag file by file. Window: **103 commits**, 2026-08-02 → 2026-09-23
(`git rev-list --count 2b8c49bf..v1.6.1`); `git diff --stat` 136 files, +33,275 / −49,191,
the top two files generated model metadata (`resources/model-metadata*.json`, ~70k of the
changed lines). Tags in the window: 27, of which 21 are release candidates and 4 shipped
versions. **`e49b18e26` = `v1.6.1` = `origin/main`**, no branch ahead of it (every `v*`
release branch has right-count 0 against `main`) — the cleanest possible re-pin
condition, the opposite of 2026-09-09 when `v1.5.0` sat 52 commits ahead.

**Merge shape.** Branch-per-release, merged to `main` by the maintainer's own PR, four
times in 18 days: `4b75620b2` v1.5.0 (#675, 09-12), `17d4bc7df` v1.5.1 (#679, 09-12),
`28f0df3c1` v1.6.0 (#680, 09-19), `e49b18e26` v1.6.1 (#685, 09-23). `v1.5.0` has a git
tag but **no GitHub release** — the releases API jumps v1.4.1 → v1.5.1, whose body links
back to the v1.5.0 PR. The in-repo `CHANGELOG.md` and `HISTORY.md` are fossils, unchanged
in the window: the former still links `dwash96/aider-ce` issues, the latter tops out at
"Aider v0.86.0". GitHub Releases is the whole release-notes surface, and its four bodies
are accurate — every claim spot-checked lands in the diff.

**1. The map claims hold at blob identity.** `git rev-parse 2b8c49bf:cecli/repomap.py
e49b18e26:cecli/repomap.py` → `dbb9739d…` twice; 0 window commits touch it. So do
`io.py`, `tools/__init__.py`, `chat_chunks.py`, `conversation/manager.py`, `memory/db.py`,
`delegate.py`, `sub_agent_coder.py`, `explore_code.py`, `hashline.py`, `hashpos.py`,
`model-settings.yml` — every ranked-index and cache-placement citation in § The
distinguishing bet is verbatim at v1.6.1, line for line. The injection path in
`integration.py` moved −14 lines under hunks that do not touch it (§ 3). Issue #49's
first instruction — "re-check the map claims first" — comes back green at the strongest
standard available. The cadence finding: `repomap.py` has **8 commits in the trailing 365
days** and the last is `e992feb80`, **2026-06-21** — the fork's index investment was
front-loaded (2025-10 → 2025-12) and is now finished work. Read against the survey's "the
people who picked the code up made it their first roadmap item": true, and past tense.

**2. Every `harness_features` cell re-derives SAME at v1.6.1** (citations moved in the
cells above). Nothing flipped: `--edit-format` still `None` → `"diff"`, `--max-tool-calls`
25 ×400, `--auto-lint` True, `--auto-test` False, `--use-enhanced-map` still the no-op
flag. `cecli/args.py` changed in exactly three places in 103 commits: `--configure-provider`
added, the `--tokens-per-minute` group added, `--voice-language`'s default corrected
`"en"` → `None`. `TOOL_MODULES` is the same 22 entries; `git ls-tree` of `cecli/tools/`
gives 23 `.py` at both pins.

**3. What the window built, by component.**

- *The loop — a token-rate governor, the one new loop authority.* `--tokens-per-minute`,
  default 1,000,000, `0` disables (`args.py:588-596 @ e49b18e26`, `0601aa6a5` 2026-09-07,
  release note: "constrain absolute cost growth of long running agent loops"). Call sites,
  not docstrings: `base_coder.py:2361` (before the compaction branch in the reflection
  path) and `:3836` (immediately before `model.send_completion`), both `await
  self._rate_limit_sleep()`; the policy (`calculate_dynamic_sleep`, `:4698-4761`) keeps a
  60 s rolling per-model buffer and sleeps only when projected usage exceeds 90% of the
  limit. Default-on with a ceiling high enough to be inert in ordinary use; operative only
  for sustained agent loops; model-uninfluenceable. Also: interrupts rewritten from
  `KeyboardInterrupt` to `asyncio.CancelledError` in the lint and background-wait paths so
  an interrupt re-prompts instead of escaping the loop; the command gate now always
  reopens in a `try/finally` (`base_coder.py:2002-2008`); compaction gained a second
  trigger at 95% of `context_compaction_max_tokens` (`:2687-2690`).
- *Context assembly — closed in both directions for subagents, and a second delta
  injector.* `keep_files` (`service.py:622-634`, `a7f4996fb` 2026-09-12): spawned
  subagents now start with `fnames=[]`, `read_only_fnames=[]`,
  `read_only_stubs_fnames=[]` unless their metadata opts in — with the long-standing
  `map_tokens=0` (`service.py:618`, both pins) and the summary-string return path, a
  subagent's context is now narrow inbound and outbound. Background-command output left
  the every-turn post-message block for its own debounced injector,
  `add_background_command_output(frequency=5)` (`integration.py:988-1034`, fired from
  `agent_coder.py:655-658`), with the reason stated in-code: re-adding mutating content
  every turn "would churn the conversation tail without the usual hash-key deduplication
  catching it" — the map's prefix-stability reasoning applied to a second block, which is
  evidence the fork treats prefix stability as a principle rather than a one-off. Command
  output pages through `ResourceManager` on demand; per-message reminder shuffling was
  removed; sessions were refactored into `helpers/sessions/` with sub-agent persistence;
  skill lookup gained the `.agents/skills` convention.
- *The permission gate — structurally unchanged, reach grew again.* `io.py` byte-identical.
  Two new human-in-the-loop mechanisms, neither a gate: privileged commands
  (`^\s*(sudo|doas|runas|passwd)\b`, `tools/command.py:42`) are routed to a background PTY
  so a human can type the password (`:229-231`, `e25360e30` 2026-09-14) — routing, not
  approval; and the skill installer's audit gate (5). New model-facing introspection:
  `Orchestrate` gained `get_tool_schema` / `get_tool_signature` (`1e4c82b48`,
  2026-09-22), the first mechanism that lets the model interrogate the dispatch table
  rather than just use it.

**4. Provenance — "Your Name" is two people.** Window authors by name: Dustin Washington
75, `Your Name <you@example.com>` 25, Chris Nestrud 2, Philippe Back 1. The placeholder
is **not** a misconfigured maintainer identity: 24 of its 25 commits are `-0700` against
the maintainer's uniform `-0400`, every one reaches `main` through `szmania/*` branches,
and the v1.5.1 release notes credit **@szmania** for PRs #674 and #677 — GitHub cannot
link the account (`author.login` → `invalid-email-address`), so the release notes are the
only surface that names him. Corrected window provenance: maintainer ~74%, szmania ~23%,
two outside contributors 3% — a quarter of the window from outside the maintainer, and
v1.6.0's notes open a "New Contributors" section for the first time. Merge share 8 of 103
(four of them the maintainer merging his own release branches); the maintainer's commits
land directly on release branches, unreviewed. One trailer in 103 bodies:
`Co-authored-by: cecli (gemini/gemini-3.8-flash)` on an outside contributor's first PR
(`cccbb1a30`) — the tool writing itself, by someone other than its maintainer, model
named. Trap for the next read: the same placeholder authored six of the last eight
`repomap.py` commits, all `-0400` — those are the maintainer; disambiguate by timezone,
never by name.

**5. `/import-skill` installs executable content from the network, and its audit gate
covers the fallback source, not the primary one.** Module docstring
(`helpers/extensions/skills_importer.py:9-11`): skills "are gated on the public
security-audit endpoint … only auto-downloaded when every reported audit passes". Call
site (`:385-389`): the gate sits inside `if source.source == "skills.sh":`. The primary
route — the community registry at `raw.githubusercontent.com/cecli-dev/community-resources`
(`:27-29`) — goes straight to `download_skill_folder` (`:399`), which fetches a GitHub
tarball (`:262`) and extracts it to `.cecli/skills` (`:288`). No `confirm_ask` on the path
(`git grep confirm_ask e49b18e26 -- cecli/commands/import_skill.py` → none); the imported
name lands in the always-on capabilities block the same turn
(`commands/import_skill.py:50-51`). Rule 4a's founding shape — the docstring describes a
gate the call site scopes to the other branch. For the survey's question (index or
tools?) this is a third answer: a third-party content supply chain, which is neither.

**6. Wheel = tag.** `pip download cecli-dev==1.6.1 --no-deps`: 554 files; every `.py`
under `cecli/` byte-identical to `git show v1.6.1:<path>` (349 compared, 0 differ), the
one extra file a vcs-generated `_version.py`. Probing the release probes the pin.

**7. The re-read's own audit.** Counts stated with their measure: **8 of 8** reproduced at
the survey's own pin (the `comm -12` divergence triple, the seven-value edit-format
histogram, the 23-file tools listing, the 0-hit agent-mode grep, the `ChatChunks` grep,
all five `repo-facts.sh` numbers, the 52-commit branch count once `main` is read as the
pin, the three `tools/` files). Without a stated measure: **5 of 7** — reproduced: 22
tools, 21 prompt YAMLs, ×2 empty-chat multiplier, the 10,000 ceiling, "three weeks apart"
(19 days); failed: "nine remote branches" (170, a clone-state count) and "a fifth edit
format" (no set at the pin has five). Citation hygiene: five of 60 file:line ranges off by
one or two at their own pin, two citing a definition or a tool's self-description where a
call site exists (`LocalServer` vs `server_name = "Local"`; the Delegate SCHEMA vs
`asyncio.gather`) — the report's own Surprise 5 diagnoses exactly this and then commits
it; and one surprise (3) falsified by the command registry at its own pin. A new failure
shape for the ledger: a count recorded against a moving ref (`main...v1.5.0rc10`) that
was right when written and unreproducible a fortnight later.

**Predictions, scored at the next re-read (dated, falsifiable).**
- **P-1.** On **2026-11-24**, `git rev-parse origin/main:cecli/repomap.py` still returns
  `dbb9739d5c380997418c8bcb70d651561f63b84f` — 156 consecutive days unchanged. Basis: 8
  touches in the trailing 365 days, 0 in the last 95; betting the recent regime over the
  annual rate. Falsifier: any blob change, refactors included.
- **P-2.** On **2026-11-24**, `gh api repos/cecli-dev/cecli/releases --jq '.[0].tag_name'`
  returns **v2.0.0 or higher**. Basis: six minors in 58 days (v1.0.0 2026-07-27 → v1.6.1),
  9.7 days per minor. Both true = ships fast, done with the index; P-1 false = the index
  is live work again and conclusion 17's second instance needs re-reading.

## Scored predictions (candidates row, 2026-08-27)

- "Still shipping" — **confirmed** (v1.4.1 2026-09-05; rc branch active today). *Re-confirmed
  harder 2026-09-24: v1.5.0, v1.5.1, v1.6.0, v1.6.1 all tagged since.*
- "Renamed, Apache-2.0, own domain" — confirmed; stars 398 → 405 in 13 days
  (`repo-facts.sh`).
- The row's implicit bet that the fork might *abandon* the ranked index under active
  maintenance — **falsified**: the index is the first roadmap item and was ported for
  performance. *Falsified again 2026-09-24, and differently: `repomap.py` was not touched
  by any of the 103 window commits (blob-identical, `dbb9739d`) — the bet is kept, and
  the betting has stopped; last touch `e992feb80`, 2026-06-21.* The row's alternative, "the position's absence from the field stops
  being an artifact", does not fire.

## Open questions

- Across live turns: whether the 20-message REPO purge (`integration.py:431-441`,
  a third removed, combined dict reset) shatters the cached prefix in practice, and how
  large the appended deltas run on a real session — the run probe simulated turns
  offline (§ Run probe) and did not spend on a model.
- Cymbal vs the tags cache: two indexes, one process — shared invalidation or not
  (undecidable from these files; needs the dependency read).
- ~~Whether v1.5.0's 52-commit branch touches `repomap.py`~~ (`git diff --name-only
  2b8c49bf..v1.5.0rc10` lists 79 files, among them `base_coder.py` and exactly three under
  `cecli/tools/` — `_yield.py`, `command.py`, `resource_manager.py` — and not `repomap.py`;
  the survey's sentence read as the whole listing, corrected 2026-09-24). **Answered:**
  untouched through v1.6.1 (`git rev-list --count 2b8c49bf..e49b18e26 -- cecli/repomap.py`
  → 0).
- **Can a model reach `/import-skill`?** (added 2026-09-24) The command refuses only in
  `("agent", "subagent")` edit formats (`commands/import_skill.py:27-31`), and cecli has a
  shell `Command` tool; if any model-callable path dispatches slash commands, an ungated
  network install of executable skill content is model-reachable — a gate finding, not a
  convenience one. Not traced.
- **Did the cached-prefix question become answerable?** (added 2026-09-24) The cache-hit
  accounting bug fixed in `82e5aa577` (2026-09-08) means any Anthropic cache-hit figure
  read off cecli's own `/tokens` before that date was 0.0% regardless of reality — the
  survey's parked live probe needs the fixed instrument, and costs API spend.
