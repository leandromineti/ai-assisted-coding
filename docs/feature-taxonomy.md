# The feature taxonomy

`created: 2026-08-18` · decision record: [ADR-0010](../adrs/0010-two-taxonomies.md)

This repo carries **two taxonomies**. The [tool taxonomy](../taxonomy.md) classifies
what a tool *is* (the categories, plus types like category 6's `type` and category 4's
poles). This file is the **feature taxonomy**: every characteristic we assess on tools,
defined **once**, with an applicability map saying which categories it can occur in. The
generator (`scripts/build-tool-index.py`) reads the YAML block below as its single
source of truth for valid frontmatter keys — the per-category (and per-type) matrices in
[`comparisons/features.md`](../comparisons/features.md) and its cross-category table
are derived from here plus report frontmatter. **Do not add a key anywhere else.**

The YAML block below is machine-read and renders on GitHub as a raw code block — for
*reading* the registry, use the generated
[`comparisons/feature-registry.md`](../comparisons/feature-registry.md) (added
2026-08-26), which re-renders it as linked tables. Same rule-3 relationship as every
matrix: this file is the editable source, that one is derived.

Conventions:

- A feature is a **presence-claim** verified in source or docs (omitted = not checked,
  `false` = checked and absent) — the same discipline as everywhere in this repo.
  Whether a present feature *pays* is a mechanism question (see each category's index).
- New keys follow **issue #2's two-verified-instances rule**: a key enters the
  registry only after the characteristic is verified in at least two tools.
- `block` names the frontmatter block that carries the key (`harness_features` for
  category 2 — renamed from the original bare `features` 2026-08-21, ADR-0018,
  `workflow_features` for category 4, `memory_features` for category-5 `type: memory` reports
  — ADR-0013, `model_features` for category 1 — ADR-0014, `environment_features` for
  category 3 — ADR-0017). `applies_to` lists tool-taxonomy categories; per-type blocks
  additionally scope by the report's `type`.
- The `environment_features` block's cells carry a grammar the other four blocks
  don't: evidence-grade suffixes inside the cell value, a `family:specific` colon tag
  on three of its eight keys, and lists that mean conjunction only — see
  [ADR-0017](../adrs/0017-environment-features-block.md) for the full grammar.
- **What belongs where** (the placement test, recorded 2026-08-19): a fact with an
  external ground truth we transcribe (stars, license, context window, pricing) is a
  **top-level frontmatter field** — mechanically collected, dated, and at most
  *rendered* into matrices as a column, never duplicated as a key. A capability we
  **assessed by reading**, comparable across tools under one definition, is a
  **registry key** and a cell (omitted = not checked, `false` = checked-absent — both
  claims). A finding, mechanism, or single-instance differentiator stays in **body
  prose** until issue #2's second instance lands. The load-bearing boundary is
  transcription vs assessment: the first drifts when the world changes, the second
  only when someone reads again. *Since 2026-08-26 the transcription half is
  enumerated too* — the `transcription_fields:` list in the YAML block below — so the
  whole assessment surface renders in one place and the generator can refuse an id
  that appears in both lists. An extension within ADR-0010's design, not a revision:
  the registry of assessed keys remains `features:`, and the enumeration adds no keys.
- `kind_link` records the **demand↔supply correspondence**: a harness feature (demand
  side) whose supply side is an installable artifact: the `memory` kind supplies from
  category 5 (Memory), every other kind from category 6 (Extensions) — the ADR-0020
  split. This is the bleed —
  quantified in the generated cross-category table.
- "Vocabulary" remains the mechanism phrase for this closed key list; the *concept* is
  the feature taxonomy (naming settled 2026-08-18, ADR-0010).

```yaml
features:
  # --- harness block (`harness_features:`), applies to category 2 ---
  - id: mcp
    block: harness_features
    applies_to: [2]
    definition: MCP client support
    kind_link: mcp-server
  - id: lsp
    block: harness_features
    applies_to: [2]
    definition: language-server integration
  - id: hooks
    block: harness_features
    applies_to: [2]
    definition: deterministic lifecycle hooks / plugin triggers
    kind_link: hook
    note: "supply side also carries category-4 verification mechanisms — ECC finding: gates can arrive as installable Stop hooks"
  - id: turn_end_gates
    block: harness_features
    applies_to: [2]
    definition: "native turn-end verification/stop gate — the harness can veto or re-prompt the model's attempt to end its turn; GRADED per ADR-0011/0012: engine | hook | script | prose | true | false"
    kind_link: hook
    note: "added 2026-08-18 per ADR-0012 (hermes verification_stop = engine; codex run_turn_stop_hooks should_block = hook) — conclusion 8's core leg, previously column-less; graded because harness gates at engine/hook vs framework gates at prose/script IS the absorption finding"
  - id: tool_approval
    block: harness_features
    applies_to: [2]
    definition: "per-tool human approval at dispatch — the harness can ask before executing a tool call; distinct from sandbox bounds (the environment_relation field) and from turn gates (turn_end_gates)"
    note: "added 2026-08-25 after the dsh deep-dive supplied the first verified absent (its tools/pre-execute default is allow; the sole prompt in a stock run is a model-initiated sandbox escalation) — the axis discriminates: 6 present / 2 absent as of 2026-08-26, all transcribed from the category-2 index's absorption table at their pins. Warp's present carries the AgentDecided caveat (a model-authored is_risky:false self-authorizes). The two absents (dsh, pi) take OPPOSITE philosophies and that is the discriminating finding: dsh moves the gate down a level to a compiled per-call OS sandbox; pi removes it entirely (no permission system, no sandbox, runs as the launching user, confinement delegated to external containerization by docs — pi.md, 2026-08-26). gemini-cli's present is the strongest form: a tiered TOML policy engine, ASK_USER default, plus a one-way LLM-authored checker (CONSECA)"
  - id: skills
    block: harness_features
    applies_to: [2]
    definition: on-demand packaged instructions
    kind_link: skill
  - id: subagents
    block: harness_features
    applies_to: [2]
    definition: spawnable isolated agents
    kind_link: subagent-def
  - id: ptc
    block: harness_features
    applies_to: [2]
    definition: programmatic tool calling — model-emitted code drives tools in a sandboxed runtime instead of chat-loop tool calls
    note: "added 2026-08-18 per ADR-0012, resolving issue #3 (hermes execute_code, iteration-refunded; codex code-mode in sandboxed V8); open mechanism question: do models actually use it?"
  - id: plan_mode
    block: harness_features
    applies_to: [2]
    definition: built-in plan/act split
    note: "shape diverges across verified instances — enforced MODE (claude-code, opencode, cline) · tool (codex) · bundled skill (hermes) · per-query FLAG (warp, 2026-08-19: /plan sets UserQueryMode::Plan on that one submission, no sticky state, planning_enabled always on server-side) — but only `mode` has ≥2 instances, so the enum promotion is deferred (ADR-0012, tracked with issue #13)"
  - id: rules_files
    block: harness_features
    applies_to: [2]
    definition: standing-instruction files (value may list filenames)
    kind_link: rules-file
  - id: model_agnostic
    block: harness_features
    applies_to: [2]
    definition: bring-your-own-model by design
  - id: session_sharing
    block: harness_features
    applies_to: [2]
    definition: "a session leaves the machine as a shareable link (implies a hosted surface) or a portable exported artifact — the report's cell comment says which form"
    note: "definition sharpened 2026-08-25 — dsh forced the call (ZIP export + resume present, share links verified absent); the old 'links/artifacts' disjunction hid exactly that distinction"
  - id: evals
    block: harness_features
    applies_to: [2]
    definition: "ships its own model/agent evaluation harness — task-success or output-quality scoring; software test suites and coverage gates do not count"
    note: "sharpened 2026-08-25 — the dsh near-misfire: 872 unit specs and per-file 100% coverage but zero model evals; the old wording did not exclude software tests"
  - id: learning_loop
    block: harness_features
    applies_to: [2]
    definition: AUTONOMOUS agent-written memory/skills (background/spawned write path) — distinct from `skills` and from user-curated memory files
    kind_link: memory
    note: "added 2026-07-30 per issue #2's two-verified-instances rule (hermes, codex); note default-on vs default-off when setting. 2026-08-19: four mechanism shapes now verified — hermes background fork (on) · codex pipeline (off) · claude-code in-loop · warp propose-and-commit (a verified ✗ whose write path is agent-proposed, human-committed; deprecated is_autogenerated shows an auto-write path removed) — promotion spec ready, issue #13"
  # --- category-1 block (`model_features:`), ADR-0014 — free-text values (vendor economics
  # differ structurally); verified against the report's `url` on its `checked` date ---
  - id: thinking
    block: model_features
    applies_to: [1]
    definition: "reasoning generation + control style: adaptive | extended | none, in the vendor's terms"
    note: "folded from the hardcoded MODEL_FEATURE_KEYS list 2026-08-19 (ADR-0014); keys added 2026-08-17"
  - id: effort_control
    block: model_features
    applies_to: [1]
    definition: effort/reasoning-level parameter — default and control surfaces
    note: "folded 2026-08-19 (ADR-0014)"
  - id: prompt_caching
    block: model_features
    applies_to: [1]
    definition: write/read economics + TTLs, in the vendor's own terms
    note: "folded 2026-08-19 (ADR-0014)"
  - id: batch_discount
    block: model_features
    applies_to: [1]
    definition: async batch pricing, if offered
    note: "folded 2026-08-19 (ADR-0014)"
  # --- category-4 block (`workflow_features:`) ---
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
    note: "the ECC finding — deliverable as installable category-6 Stop hooks, independent of any framework. GSD deep-dive 2026-08-18: even the category's best measured-gate machinery enforces the MEASUREMENT in code but the VERDICT via LLM — its hooks guard files and dispatch, never verification verdicts. bmad-loop stub 2026-08-18: first engine-graded value in the registry — policy-defined verify commands executed and judged by the orchestrator (verify.py:2661, engine.py:2037-2040); in BMAD's companion orchestrator, not the framework"
  - id: process_gates
    block: workflow_features
    applies_to: [4]
    definition: "human approval checkpoints encoded in the flow; GRADED per ADR-0011: engine | hook | script | prose | true | false"
  - id: context_isolation
    block: workflow_features
    applies_to: [4]
    definition: fresh/right-sized agent context per unit of work, by design
    note: "supply side is category-2 machinery (subagents, fresh sessions). 2026-08-18 correction: 'a framework can only instruct it' was falsified by GSD's deep-dive — its agent-isolation-guard ENFORCES it as a hard-blocking harness hook (exit 2)"
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
  # --- category-5 memory block (`memory_features:`), kind: memory reports only (ADR-0013) ---
  # Descriptive enums per the category-4 `state_store` precedent — mechanism choices, not
  # ADR-0011 enforcement grades. No kind_link on these entries by design: category-5
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
  - id: write_admission
    block: memory_features
    applies_to: [5]
    definition: "what earns AUTONOMOUS storage: evidence-gated (enactment/outcomes required) | scored (reward/confidence thresholds with probation) | unfiltered (assertion suffices)"
    note: "added 2026-08-19 post exp-04 arm C (conclusion 14): the write-side half of the injection story injection_trust_boundary tells on the read side — unfiltered admission + authoritative recall = the injection-to-authority pipeline. Instances: ai-memory (evidence-gated — 12 verbatim rejections archived, 'no implementation evidence'), memos (scored — gain thresholds + probation, golden-tested), mem0 (unfiltered — ADD-only extraction from say-so, verified opposite pole). Explicit/deliberate write paths (write-page, add_memory) are NOT gated by this key — it classifies the autonomous path only"
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
    definition: synthesizes standing instructions/rules from sessions (memory that mints category-6 artifacts of another kind)
    note: "added 2026-08-19 per ADR-0013; instances: ai-memory (_rules/ + procedures/ proposals), cognee (coding_agent_rules NodeSet, direct mode only); cross-kind echo: ECC instincts"
  # --- category-3 environment block (`environment_features:`), category == 3 only (ADR-0017) ---
  # Mechanism choices, not ADR-0011 enforcement grades — contrast explicit per ADR-0017
  # scoping rule 2. No kind_link on these entries by design: category-3 demand-side
  # linkage lives at bucket granularity in comparisons/environments.md, not here.
  - id: isolation_primitive
    block: environment_features
    applies_to: [3]
    definition: "the mechanism the sandbox's isolation boundary rests on; open-descriptive family:specific tag, family closed: hardware-virt | userspace-kernel | shared-kernel | os-native; specific half open-descriptive, optional per cell"
    note: "added 2026-08-20 per ADR-0017; instances: e2b (hardware-virt:firecracker-microvm), modal (userspace-kernel:gvisor-runsc)"
  - id: egress_default
    block: environment_features
    applies_to: [3]
    definition: "the network posture in effect with no explicit configuration; closed lattice: open | restricted | tier-gated"
    note: "added 2026-08-20 per ADR-0017; instances: e2b open (internet on by default), modal open (egress OPEN by default)"
  - id: egress_controls
    block: environment_features
    applies_to: [3]
    definition: "how an explicit allow/deny rule resolves against the default; closed lattice: allow-biased | deny-wins | none-native"
    note: "added 2026-08-20 per ADR-0017; instances: e2b allow-biased (an allow entry beats a deny, including beating allowInternetAccess:false), modal OPAQUE — the interface (block_network, CIDR/domain allowlists) is verified, but no source states whether an allow entry can override a block, the axis E2B's finding turns on"
  - id: credential_model
    block: environment_features
    applies_to: [3]
    definition: "how a third-party credential reaches, or is kept from, the sandboxed process; open-descriptive family:specific tag, family closed: broker-relayed | split-plane | plain-env-var; specific half open-descriptive, optional per cell"
    note: "added 2026-08-20 per ADR-0017; instances: e2b broker-relayed:spiffe-jwt-svid (egress-proxy-brokered SPIFFE JWT-SVID), modal split-plane (long-lived MODAL_TOKEN_ID/SECRET control-plane only; short-lived JWT to the worker)"
  - id: snapshot_model
    block: environment_features
    applies_to: [3]
    definition: "the mechanism by which sandbox state is paused/resumed; open-descriptive family:specific tag, family closed: create-is-resume | checkpoint-restore | explicit-backup | none; specific half open-descriptive, optional per cell"
    note: "added 2026-08-20 per ADR-0017; instances: e2b create-is-resume:uffd-lazy-paging, modal checkpoint-restore (bare family — the gVisor-internals specific mechanism is Modal's own testimony, not source-verified)"
  - id: self_host
    block: environment_features
    applies_to: [3]
    definition: "whether the environment is genuinely operable outside the vendor's own cloud; closed lattice: full | partial | none"
    note: "added 2026-08-20 per ADR-0017; instances: e2b partial (named closed components: the egress proxy, belt), modal none (no infra repo; SaaS-only)"
  - id: warm_pool
    block: environment_features
    applies_to: [3]
    definition: "whether a pool of pre-started instances exists to cut cold-start latency; boolean presence-claim outside both enum regimes (omitted = not checked, false = checked and absent)"
    note: "added 2026-08-20 per ADR-0017; instances: e2b false (verified absent — grep for prewarm/warm-pool patterns over packages/, iac/, docs/), modal OPAQUE"
  - id: filesystem_sync
    block: environment_features
    applies_to: [3]
    definition: "how the working anchor gets its content into the sandbox; closed lattice, plain enum: mount | clone | upload"
    note: "added 2026-08-20 per ADR-0017; instances: e2b clone (Task 1 probe, dated 2026-08-20, at the unmoved pin f5d702a5 — a first-class Sandbox.git.clone() API in both Python SDKs and the JS SDK, run through the sandbox's own command runner rather than a dedicated envd wire RPC), modal upload (no local execution mode; image builds stream a remote build context — ImageJoinStreaming, _image.py:433-441)"
# --- transcription fields (added 2026-08-26) — the OTHER half of the placement test ---
# Facts with an external ground truth, transcribed and dated: top-level frontmatter
# fields, never duplicated as registry keys. Enumerated here so the whole assessment
# surface is visible in one place (rendered in comparisons/feature-registry.md); an id
# appearing in both this list and features[] is a generator ERROR — the placement test,
# enforced. Verification vocabulary: dated-docs (verified against the report's url on
# its checked date — for vendor-defined facts like a price or a context window the docs
# ARE the ground truth, the one place rule 1a's source-beats-testimony ordering
# inverts) · mechanical (script-collected — repo-facts.sh / GitHub API — never
# hand-typed) · source-or-docs (read in the pinned clone or official docs, the same
# discipline as feature cells). Honesty/meta columns (depth, checked, read_at) and
# tool-taxonomy classification fields (category, type) are deliberately absent: rule 2
# and taxonomy.md govern those, and they are not facts about the subject.
transcription_fields:
  - id: vendor
    applies_to: [1, 2, 3, 4, 5, 6]
    definition: "who maintains (or trains) it; the exact string is the grouping key for vendors.md, so spelling drift splits a vendor's row"
    verification: source-or-docs
    rendered_in: [tools.md, vendors.md]
  - id: license
    applies_to: [1, 2, 3, 4, 5, 6]
    definition: "SPDX id or 'proprietary'; for category 1 the WEIGHTS license — unverifiable until weights are published, and recorded as such rather than assumed from a predecessor"
    verification: source-or-docs
    rendered_in: [tools.md, features.md]
  - id: stars
    applies_to: [2, 3, 4, 5, 6]
    definition: "GitHub stars via the API, carrying their own stars_at date (stars drift daily); describes the CURRENT repo only — a fork or org move strands the predecessor's stars"
    verification: mechanical
    rendered_in: [tools.md]
  - id: first_commit
    applies_to: [2, 3, 4, 5, 6]
    definition: "the public repo's first commit date — the public history's start, which postdates the product where a tool open-sourced later"
    verification: mechanical
    rendered_in: [tools.md]
  - id: version
    applies_to: [2, 3, 4, 5, 6]
    definition: "git describe --tags --always of the clone at read time; omitted for closed source"
    verification: mechanical
    rendered_in: [tools.md]
  - id: commit
    applies_to: [2, 3, 4, 5, 6]
    definition: "the ONE machine-checked pin per report — build-tool-index --check verifies it still resolves in upstream/<name>; secondary pins are prose-recorded (see the tool template)"
    verification: mechanical
    rendered_in: []
  - id: stack
    applies_to: [2, 3, 4, 5, 6]
    definition: "[Language, Runtime/Framework] of the subject"
    verification: source-or-docs
    rendered_in: [tools.md]
  - id: surfaces
    applies_to: [2]
    definition: "where you interact — terminal | ide | desktop | web (multi-valued)"
    verification: source-or-docs
    rendered_in: [tools.md]
  - id: execution
    applies_to: [2]
    definition: "how it runs — local | async-remote | both"
    verification: source-or-docs
    rendered_in: [tools.md]
  - id: environments
    applies_to: [2]
    definition: "category-3 bindings (the bleed): which environments the tool can run its agent in — list only what is verified"
    verification: source-or-docs
    rendered_in: [environments.md]
  - id: environment_relation
    applies_to: [2]
    definition: "HOW the tool relates to the environment — bundle | bind | internalize | inhabit; left unset when none of the four fits, and that null case is data"
    verification: source-or-docs
    rendered_in: [environments.md]
  - id: harness_targets
    applies_to: [4, 5, 6]
    definition: "which harnesses the tool officially installs into — verified-only; a list, or a short string for large sets"
    verification: source-or-docs
    rendered_in: [tools.md]
  - id: model_id
    applies_to: [1]
    definition: "exact API model id / HF repo id — the purchasable name, which routes and aggregators may not preserve"
    verification: dated-docs
    rendered_in: []
  - id: release_mode
    applies_to: [1]
    definition: "api-only | open-weights | both — verified on both surfaces before 'both' is claimed"
    verification: dated-docs
    rendered_in: []
  - id: released
    applies_to: [1]
    definition: "first-availability date PLUS lifecycle stage in the vendor's own vocabulary (GA / Preview / beta) — stages don't align across vendors, so the stage word is part of the fact"
    verification: dated-docs
    rendered_in: [models.md]
  - id: context_window
    applies_to: [1]
    definition: "advertised input tokens; usable-vs-advertised is a category-1 axis, measured in report evidence cells, not here"
    verification: dated-docs
    rendered_in: [models.md, features.md]
  - id: max_output
    applies_to: [1]
    definition: "maximum output tokens, with vendor caveats carried in the value (defaults vs settable ceilings, visible-output-only counts)"
    verification: dated-docs
    rendered_in: [models.md]
  - id: pricing
    applies_to: [1]
    definition: "$in / $out per MTok, with any time-limited or tiered pricing dated and its tier boundaries stated"
    verification: dated-docs
    rendered_in: [models.md]
  - id: knowledge_cutoff
    applies_to: [1]
    definition: "vendor-stated only; absence is recorded as 'not stated', dated — third-party ship-date inference is not a cutoff"
    verification: dated-docs
    rendered_in: [models.md]
```
