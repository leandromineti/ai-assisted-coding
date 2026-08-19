# The feature taxonomy

`created: 2026-08-18` · decision record: [ADR-0010](../../adrs/0010-two-taxonomies.md)

This repo carries **two taxonomies**. The [tool taxonomy](../../taxonomy.md) classifies
what a tool *is* (the layers, plus sub-categories like layer 5's `kind` and layer 4's
poles). This file is the **feature taxonomy**: every characteristic we assess on tools,
defined **once**, with an applicability map saying which layers it can occur in. The
generator (`scripts/build-tool-index.py`) reads the YAML block below as its single
source of truth for valid frontmatter keys — the per-layer (and per-kind) matrices in
[`comparisons/features.md`](../../comparisons/features.md) and its cross-layer table
are derived from here plus report frontmatter. **Do not add a key anywhere else.**

Conventions:

- A feature is a **presence-claim** verified in source or docs (omitted = not checked,
  `false` = checked and absent) — the same discipline as everywhere in this repo.
  Whether a present feature *pays* is a mechanism question (see each layer's index).
- New keys follow **issue #2's two-verified-instances rule**: a key enters the
  registry only after the characteristic is verified in at least two tools.
- `block` names the frontmatter block that carries the key (`features` for harnesses,
  `workflow_features` for layer 4, `memory_features` for layer-5 `kind: memory` reports
  — ADR-0013). `applies_to` lists tool-taxonomy layers; per-kind blocks additionally
  scope by the report's `kind`.
- `kind_link` records the **demand↔supply correspondence**: a harness feature (demand
  side) whose supply side is an installable layer-5 artifact kind. This is the bleed —
  quantified in the generated cross-layer table.
- "Vocabulary" remains the mechanism phrase for this closed key list; the *concept* is
  the feature taxonomy (naming settled 2026-08-18, ADR-0010).

```yaml
features:
  # --- harness block (`features:`), applies to layer 2 ---
  - id: mcp
    block: features
    applies_to: [2]
    definition: MCP client support
    kind_link: mcp-server
  - id: lsp
    block: features
    applies_to: [2]
    definition: language-server integration
  - id: hooks
    block: features
    applies_to: [2]
    definition: deterministic lifecycle hooks / plugin triggers
    kind_link: hook
    note: "supply side also carries layer-4 verification mechanisms — ECC finding: gates can arrive as installable Stop hooks"
  - id: turn_end_gates
    block: features
    applies_to: [2]
    definition: "native turn-end verification/stop gate — the harness can veto or re-prompt the model's attempt to end its turn; GRADED per ADR-0011/0012: engine | hook | script | prose | true | false"
    kind_link: hook
    note: "added 2026-08-18 per ADR-0012 (hermes verification_stop = engine; codex run_turn_stop_hooks should_block = hook) — conclusion 8's core leg, previously column-less; graded because harness gates at engine/hook vs framework gates at prose/script IS the absorption finding"
  - id: skills
    block: features
    applies_to: [2]
    definition: on-demand packaged instructions
    kind_link: skill
  - id: subagents
    block: features
    applies_to: [2]
    definition: spawnable isolated agents
    kind_link: subagent-def
  - id: ptc
    block: features
    applies_to: [2]
    definition: programmatic tool calling — model-emitted code drives tools in a sandboxed runtime instead of chat-loop tool calls
    note: "added 2026-08-18 per ADR-0012, resolving issue #3 (hermes execute_code, iteration-refunded; codex code-mode in sandboxed V8); open mechanism question: do models actually use it?"
  - id: plan_mode
    block: features
    applies_to: [2]
    definition: built-in plan/act split
    note: "shape diverges across verified instances — enforced MODE (claude-code, opencode, cline) · tool (codex) · bundled skill (hermes) — but only `mode` has ≥2 instances, so the enum promotion is deferred (ADR-0012, tracked with issue #13)"
  - id: rules_files
    block: features
    applies_to: [2]
    definition: standing-instruction files (value may list filenames)
    kind_link: rules-file
  - id: model_agnostic
    block: features
    applies_to: [2]
    definition: bring-your-own-model by design
  - id: session_sharing
    block: features
    applies_to: [2]
    definition: shareable session links/artifacts
  - id: evals
    block: features
    applies_to: [2]
    definition: ships its own evaluation suite
  - id: learning_loop
    block: features
    applies_to: [2]
    definition: AUTONOMOUS agent-written memory/skills (background/spawned write path) — distinct from `skills` and from user-curated memory files
    kind_link: memory
    note: "added 2026-07-30 per issue #2's two-verified-instances rule (hermes, codex); note default-on vs default-off when setting"
  # --- layer-4 block (`workflow_features:`) ---
  - id: intent_pipeline
    block: workflow_features
    applies_to: [4]
    definition: staged requirements→implementation artifact pipeline (the SDD spine)
  - id: deterministic_engine
    block: workflow_features
    applies_to: [4]
    definition: a program — not prose — parses/validates/advances workflow state
  - id: format_gates
    block: workflow_features
    applies_to: [4]
    definition: "artifact-structure gates; GRADED value = strongest verified enforcer: engine | hook | script | prose | true (present, unclassified) | false (ADR-0011)"
    note: "calibration lesson 2026-08-18: spec-kit's ✓ flipped to ✗ at deep-dive; same day GSD's deep-dive showed a four-rung enforcement ladder — hence the grading. A bare `true` is an unanswered who-enforces question"
  - id: measured_gates
    block: workflow_features
    applies_to: [4]
    definition: "acceptance criteria with measured expected values (behavior, not format); GRADED per ADR-0011: engine | hook | script | prose | true | false"
    kind_link: hook
    note: "the ECC finding — deliverable as installable layer-5 Stop hooks, independent of any framework. GSD deep-dive 2026-08-18: even the layer's best measured-gate machinery enforces the MEASUREMENT in code but the VERDICT via LLM — its hooks guard files and dispatch, never verification verdicts. bmad-loop stub 2026-08-18: first engine-graded value in the registry — policy-defined verify commands executed and judged by the orchestrator (verify.py:2661, engine.py:2037-2040); in BMAD's companion orchestrator, not the framework"
  - id: process_gates
    block: workflow_features
    applies_to: [4]
    definition: "human approval checkpoints encoded in the flow; GRADED per ADR-0011: engine | hook | script | prose | true | false"
  - id: context_isolation
    block: workflow_features
    applies_to: [4]
    definition: fresh/right-sized agent context per unit of work, by design
    note: "supply side is layer-2 machinery (subagents, fresh sessions). 2026-08-18 correction: 'a framework can only instruct it' was falsified by GSD's deep-dive — its agent-isolation-guard ENFORCES it as a hard-blocking harness hook (exit 2)"
  - id: parallel_orchestration
    block: workflow_features
    applies_to: [4]
    definition: concurrent agents/work-packages machinery (worktrees, fan-out)
  - id: state_store
    block: workflow_features
    applies_to: [4]
    definition: "where workflow state lives: repo-files | database"
  - id: retrospectives
    block: workflow_features
    applies_to: [4]
    definition: encoded learning step feeding completed work back into the process
    note: "the framework-side cousin of the harness `learning_loop`"
  # --- layer-5 memory block (`memory_features:`), kind: memory reports only (ADR-0013) ---
  # Descriptive enums per the layer-4 `state_store` precedent — mechanism choices, not
  # ADR-0011 enforcement grades. No kind_link on these entries by design: layer-5
  # supply participation flows through `learning_loop`'s kind_link above.
  - id: memory_store
    block: memory_features
    applies_to: [5]
    definition: "what the store is: files-git | vector | graph | rows (list allowed for hybrids, primary first)"
    note: "added 2026-08-19 per ADR-0013; instances: ai-memory (git-versioned markdown wiki), mem0 (vector+BM25), memos (SQLite rows+vectors), cognee (graph+vector+relational)"
  - id: capture_path
    block: memory_features
    applies_to: [5]
    definition: "how sessions become memory: hook | adapter | agent-invoked"
    note: "added 2026-08-19 per ADR-0013; instances: ai-memory + mem0 (harness hooks), memos (in-process adapter cascade), cognee (agent-invoked MCP tools — the learning_loop: false pole)"
  - id: recall_injection
    block: memory_features
    applies_to: [5]
    definition: "how memory reaches the next session: auto | pull-only | both"
    note: "added 2026-08-19 per ADR-0013; instances: ai-memory (auto baton + pull-only wiki = both), memos (turn-start auto, bounded), mem0 (session-start/prompt-submit auto), cognee (pull-only)"
  - id: memory_scope
    block: memory_features
    applies_to: [5]
    definition: "scoping axes the store natively supports (list): project | agent | user | session"
    note: "added 2026-08-19 per ADR-0013; instances: ai-memory, mem0, memos, cognee"
  - id: memory_tiers
    block: memory_features
    applies_to: [5]
    definition: typed memory tiers rather than one flat store (working/episodic/semantic, traces/policies, session/permanent)
    note: "added 2026-08-19 per ADR-0013; instances: ai-memory, memos, cognee — WAS 'all four' until mem0's deep-dive (2026-08-19) flipped its cell: procedural_memory is a metadata tag on one collection, not a tier"
  - id: hybrid_retrieval
    block: memory_features
    applies_to: [5]
    definition: multi-stream retrieval fusion (RRF/MMR/reranker over lexical+vector+structural)
    note: "added 2026-08-19 per ADR-0013; instances: ai-memory (RRF over 4 streams), memos (RRF+MMR), mem0 (additive fusion, NOT RRF). Calibration (mem0 deep-dive): presence ≠ operative — mem0's ✓ silently degrades to pure vector search on a bare install (spaCy/fastembed are optional extras); ask what the DEFAULT install does before reading a ✓"
  - id: decay
    block: memory_features
    applies_to: [5]
    definition: expiry/forgetting/retirement lifecycle on stored memories
    note: "added 2026-08-19 per ADR-0013; instances: ai-memory (exponential retention + forget sweep), mem0 (expiration_date), memos (time-decayed value, candidate→active→retired)"
  - id: memory_revision
    block: memory_features
    applies_to: [5]
    definition: "who can change an existing memory once stored: auto (the system revises/supersedes/retires on its own) | proposed (system proposes, human approves) | caller-only (only explicit API calls)"
    note: "added 2026-08-19 from the mem0 deep-dive's central finding; instances: ai-memory (auto — background consolidation auto-approves wiki edits, require_approval=false), memos (auto — three live demotion paths, candidate→active→archived; confirmed in source at deep-dive but default-UNMOUNTED under lightweight mode), mem0 (caller-only — no auto-supersession anywhere; the prompt's linking mechanism is parsed and discarded). The kind's sharpest trust axis: what happens when a memory is WRONG"
  - id: injection_trust_boundary
    block: memory_features
    applies_to: [5]
    definition: injected memory is delimited/framed as untrusted data, not instructions
    note: "added 2026-08-19 per ADR-0013; instances: ai-memory, memos. mem0 SETTLED ✗ at its 2026-08-19 deep-dive — bare-markdown injection, and its openclaw recall protocol actively inverts the boundary (memories as authoritative rules). Security-relevant: memory injection is a prompt-injection vector"
  - id: deployment_mode
    block: memory_features
    applies_to: [5]
    definition: "self-host | cloud | both"
    note: "added 2026-08-19 per ADR-0013; instances: mem0 (OSS vs platform; plugin defaults platform), cognee (direct vs API mode — with a BEHAVIOR difference: rule extraction skipped in API mode), ai-memory (localhost daemon)"
  - id: harness_installer
    block: memory_features
    applies_to: [5]
    definition: ships an installer that mutates the harness's own config (settings/hooks) rather than only offering an MCP endpoint
    note: "added 2026-08-19 per ADR-0013; instances: ai-memory (install-hooks --apply rewrites settings.json), mem0 (hooks.json bundle, 6 harnesses), memos (one-command installer + adapters)"
  - id: rule_extraction
    block: memory_features
    applies_to: [5]
    definition: synthesizes standing instructions/rules from sessions (memory that mints layer-5 artifacts of another kind)
    note: "added 2026-08-19 per ADR-0013; instances: ai-memory (_rules/ + procedures/ proposals), cognee (coding_agent_rules NodeSet, direct mode only); cross-kind echo: ECC instincts"
```
