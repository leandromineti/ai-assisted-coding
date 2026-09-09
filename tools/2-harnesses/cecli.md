---
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
version: v1.4.1
commit: 2b8c49bf
first_commit: 2023-04-03   # aider's first commit — the fork keeps the full history (13,048 shared commits with aider main; see § Stack & repo shape)
stars: 405
stars_at: 2026-09-09
read_at: 2026-09-09
depth: survey   # 2026-09-09, targeted source read at the pin for ONE question — does the aider fork keep the ranked-index context-assembly bet (conclusion 17) or drift toward tool dispatch? — plus the registry keys aider carried, each re-checked at the fork's own source by grep (one Opus reader, load-bearing citations spot-verified in the main session). NOT traced: the loop end to end, the TUI, the ACP server, the Cymbal search index, the memorizer subagent's runtime. RUN probe added 2026-09-09 on the published 1.4.1 artifact (`pip install cecli-dev==1.4.1`), offline dumps only, no API call — § Run probe; the probe also caught two source misreads in the first write-up, corrected in place and listed in § Surprises
harness_features:
  mcp: true            # client, three transports + OAuth: McpServerManager (cecli/mcp/manager.py:7), HttpBasedMcpServer (cecli/mcp/server.py:327), `--mcp-servers` / `--mcp-servers-files` / `--mcp-transport` (args.py:478-491). And the built-in tools are themselves exposed as a synthetic MCP server named "Local" (mcp/server.py:608) — see § The distinguishing bet
  hooks: true          # six lifecycle types START/ON_MESSAGE/END_MESSAGE/PRE_TOOL/POST_TOOL/END (cecli/hooks/types.py:6-11), registered as JSON via `--hooks` (args.py:419-421)
  context_retrieval: ranked-index   # KEPT and invested in: rustworkx.pagerank over the weighted file-reference graph (repomap.py:1008, port from networkx 2025-12-19 8bd4550c), tags cache `.cecli/tags.cache.v9` (repomap.py:112,118), injected as a role="user" message (helpers/conversation/integration.py:481-482) by the same call in every coder incl. agent mode (base_coder.py:2543 = agent_coder.py:638). Default budget is aider's formula min(max(ctx/8,1024),4096) (models.py:1132-1139, wired main.py:1205), ×2 on an empty chat; RUN 2026-09-09 on the published 1.4.1 artifact: the map is 84% of message bytes in `diff` mode and 79% in `--agent` mode (§ Run probe). Injection is DELTA-shaped: each turn appends only files/tags not already in the conversation (repomap.py:1246-1274, integration.py:370)
  turn_end_gates: engine   # --auto-lint default True, unchanged from aider (args.py:929-932); a second, default-OFF gate joined 2026-09-04 (#673): with --auto-test, failing tests abort the auto-commit and reflect the errors back (base_coder.py:2922-2932; --auto-test default False, args.py:940-943)
  tool_approval: prompt  # confirm_ask kept as the gate shape (io.py:1283-1286); `--max-tool-calls` 25 per message (args.py:334-338), multiplied ×400 in agent mode (agent_coder.py:156) — effective agent default 10,000
  headless_approval: allow   # FAIL-OPEN kept verbatim from aider: `default="y"` (io.py:1285) and EOF "treated as if the user pressed Enter" → `res = default` (io.py:1372-1374, 1461-1463)
  skills: true         # Anthropic-compatible SKILL.md loader: directory scan (helpers/skills.py:253-258), frontmatter name+description required (:302-316), `allowed-tools` read (:323); only NAMES sit in the always-on capabilities block (base_coder.py:984-990), bodies load on demand via ResourceManager / `/load-skill`
  subagents: true      # SubAgentCoder (coders/sub_agent_coder.py:14); Delegate tool dispatches an array of tasks in parallel (tools/delegate.py:24-62); fresh coder per subagent (helpers/agents/service.py:935-954); return path is a SUMMARY STRING (delegate.py:126-180; Yield's `summary` arg, tools/_yield.py:33-37); max_sub_agents 30 (agent_coder.py:104)
  rules_files: true    # AGENTS.md then CLAUDE.md in the coder root, auto-loaded when no explicit rules are configured, re-read from disk every turn under MessageTag.RULES (helpers/conversation/integration.py:523-529). aider had none
  model_agnostic: true # LiteLLM kept as the single provider abstraction; tools go on the wire as OpenAI-style `tools=` (models.py:1383, base_coder.py:3764)
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
(`git rev-list --left-right --count main...v1.5.0rc10` → `0 52`). The release
branch is not pinned; a re-read waits for the v1.5.0 tag on `main`.

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
  base coder uses to build a map at all (`base_coder.py:750-752`). The default budget is
  aider's formula — `min(max(max_input_tokens/8, 1024), 4096)` (`models.py:1132-1139`),
  wired at `main.py:1205`; the literal `1024` at `base_coder.py:744` is a fallback
  `main.py` never reaches (*corrected 2026-09-09 by the run probe; the first write-up
  cited the fallback as the default*). New around it: **the injection is a delta.** The
  ranker keeps a `combined_map_dict` of everything already shown and renders only
  `new_dict` — files and tags not yet in the conversation (`repomap.py:1246-1274`,
  `integration.py:369`) — as a fresh REPO-tagged user message, deduplicated by content
  hash (`manager.py:144,185-188`), the old ones left in place; once ≥20 REPO messages
  accumulate a third are purged and the combined dict reset (`integration.py:431-441`).
  That is the fork's answer to the caching collision the deep-dive recorded: the map
  never rewrites the cached prefix, it appends to it. The first write-up credited a
  dedicated cache breakpoint on the map (`chat_chunks.py:64-66`); that code is dead —
  see § Surprises 5.
- **Tool dispatch is added, not substituted, and it is not the default.** 22 registered
  tools (`tools/__init__.py:30-51`; 23 files by `ls cecli/tools/*.py | wc -l`, one is
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
always on, bodies on demand). `hashline` is a fifth edit format
(`--hashline`, `args.py:270-276`; `coders/hashline_coder.py:20-25`): every line
prefixed with a content hash by `helpers/hashline.py:22-33`, so edits address lines by
hash instead of SEARCH text.

## Stack & repo shape

`repo-facts.sh` at the pin: 15,734 commits, 1,074 tracked files, 519 `.py`, 58 `.scm`
tree-sitter queries (aider's count, kept), 111 `.mp3` (aider's, kept). `grep_ast` and
the tree-sitter language pack were vendored in-tree
(`helpers/grep_ast`, `566a615d` 2026-04-25). Prompts moved from Python classes to 21
YAML files under `prompts/`; a mode's map eligibility is now data (`repo_content_prefix:
null` in `wholefile_func.yml:20`). Nine remote branches, several named as experiments
(`coroutine-experiment`, `domain-refactor-experiment`, `llm-reduction`).

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


1. **`--use-enhanced-map` is `store_true` with `default=True` and help text reading
   "(default: False)"** (`args.py:506-510`); no `--no-` form exists. Import-aware
   ranking is on for everyone and the flag is a no-op — a docs-vs-source gap inside the
   tool's own CLI help.
2. **The gate surface is aider's, verbatim.** Same fail-open `confirm_ask`, same
   `--auto-lint` default, while the reach grew from zero tools to 22 plus MCP plus
   subagents with an effective 10,000-tool-call ceiling per message. The permission
   posture did not move with the capability.
3. **A real SQLite/FTS5 "facts" store** (`.cecli/memory.v*/cache.db`,
   `helpers/memory/db.py:44-100`), reachable only through the `memorizer` subagent
   (`tools/search_facts.py:1-3`) — a category-5 mechanism arriving inside a category-2
   tool by way of a subagent, not a plugin.
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

## Scored predictions (candidates row, 2026-08-27)

- "Still shipping" — **confirmed** (v1.4.1 2026-09-05; rc branch active today).
- "Renamed, Apache-2.0, own domain" — confirmed; stars 398 → 405 in 13 days
  (`repo-facts.sh`).
- The row's implicit bet that the fork might *abandon* the ranked index under active
  maintenance — **falsified**: the index is the first roadmap item and was ported for
  performance. The row's alternative, "the position's absence from the field stops
  being an artifact", does not fire.

## Open questions

- Across live turns: whether the 20-message REPO purge (`integration.py:431-441`,
  a third removed, combined dict reset) shatters the cached prefix in practice, and how
  large the appended deltas run on a real session — the run probe simulated turns
  offline (§ Run probe) and did not spend on a model.
- Cymbal vs the tags cache: two indexes, one process — shared invalidation or not
  (undecidable from these files; needs the dependency read).
- Whether v1.5.0's 52-commit branch touches `repomap.py` (`git diff --name-only
  main..v1.5.0rc10` lists `base_coder.py` and three `tools/` files, not `repomap.py`).
