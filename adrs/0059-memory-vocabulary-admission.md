# ADR-0059 — the memory vocabulary admission: four candidate keys, two values, and the ripple rows of the 2026-11 re-reads

`decided: 2026-11-08` · `status: accepted`

## Decision

Category 5's `memory_features:` block gains four keys and two enum values, in one
batched ADR (ADR-0050 and ADR-0055 style: one ADR for the whole set, the canonical
order stated once). Batching was the owner's choice over one ADR per key; the
options grammar that several of the cells depend on has its own ADR
([ADR-0060](0060-options-with-default-grammar.md)) because it crosses keys and
categories while admission does not. The same ADR records every amendment to the
existing memory vocabulary that the three deep-dive re-reads of 2026-11 left open,
and every written non-admission with its trigger.

The admissions come from the candidate vocabulary three Phases collected: ai-memory,
openviking, mempalace and agentmemory read in depth, and mem0, memos, cognee and
memori probed at their existing pins, five candidate keys over eight tools
([`tools/5-memory/README.md`](../tools/5-memory/README.md) § Candidate-key census at
existing pins). Four keys clear the two-instance bar and are admitted; the fifth, the
OKF open-format axis, does not and is argued below. No key is given a `kind_link`:
`compaction_capture` by the owner's decision, for the reason stated under it; the
other three because no category-2 key exists for them to link to.

### `compaction_capture`

Group `write-path`, `value_type: closed-enum`, values `writes-to-store`,
`reinject-only`, `false`, inserted directly after `capture_path`.

> whether the tool writes to its store from the harness's pre-compaction event:
> `writes-to-store` (a handler the tool registers, in a hook manifest, plugin or
> installer at the pin, on that event writes to the tool's store, directly or through
> its write endpoint, at once or by starting a job) | `reinject-only` (a registered
> handler only re-injects or prints context and writes nothing to the store); `false`
> = no registered pre-compaction handler. Across harnesses the strongest registered
> handler wins: `writes-to-store` over `reinject-only` over `false`.

The key is single-valued where the milestone's wording was list-valued: no tool's
handlers differ in kind across its harnesses (openviking's nine handlers all commit
and four of its twelve installer products have none; mem0's OpenCode hook writes and
then re-injects, so the stronger value holds; mempalace's Hermes handler is a no-op
beside two writing ones), so the cell comment carries per-harness counts instead of a
second value. `reinject-only` names the "not a writer, but has machinery" position,
the same regrade move as ADR-0053 to ADR-0056.

NOT this fact:

- compaction inside the store (a graph trim, an index or vector compaction, the hosted
  platform's decay);
- re-injection after a compaction at session start (mem0's post-compaction capture
  script, ai-memory's explicit reload recap);
- a handler the tool does not register (a design the docs describe and the code does
  not wire: mempalace's blocking design);
- the harness's own compaction, which is `context_compaction`.

Rhyme risks: `capture_path` (the trigger kind is not derivable from this key:
agentmemory is `hook` and `reinject-only`), `learning_loop` (who commits, not when),
`context_compaction` (the harness side of the same event) and `memory_store` (what the
store is). No `kind_link` to `context_compaction`: a memory tool that writes at the
pre-compaction event does not supply the harness's own compaction, so a link would
overstate the demand-and-supply correspondence the field exists to record.

Census row: `4 present · 3 ✗ · 1 omitted`. Instances against the bar: 4 tools write
(ai-memory, openviking, mempalace, mem0), 2 only re-inject (agentmemory, memos),
memori (a stub) is ✗ and carries no cell, cognee is omitted because its Claude Code
plugin lives in a separate repository the pin names as the handler's home.

### `llm_free_path`

Group `write-path`, `value_type: list`, list items `capture`, `consolidation`,
`recall`.

> the components, among capture, consolidation and recall (ADR-0023), whose default
> path (the shipped configuration, no provider key in the launching environment)
> makes no call to a generative model, listed in that order; `[]` when all three call
> one. A component with no default-path process counts model-free and is marked
> `(no process)` in the cell comment, and the comment names what turns the model path
> on: an explicit flag, ambient API-key presence, or always. The cell is omitted when
> any component is undecided, because a list cannot say undecided.

One list-valued key was chosen over three presence keys (one per component), which
would state one concept three times. The cell is omitted whenever any component is
undecided (openviking, memori): a list that dropped an undecided component would say
"checked and absent", and for openviking the only encodable list, `[]`, would collide
with cognee's.

NOT this fact:

- egress-free (ai-memory fetches an embedding model on first start; the zero-model
  probe of one tool was not zero-egress);
- spend-free;
- embedder-free (an embedding model is not a generative model);
- a setup command (mempalace `init`, mem0 client construction);
- a whole-tool verdict;
- the hosted route of an open engine.

Rhyme risks: `learning_loop` (who writes and commits: a switch that turns a
background writer on can also turn the model path on, so the two are read together),
`write_admission` (an extraction model's judgment is the admission), `capture_path`
(the trigger, not model use) and `deployment_mode`.

Census rows: capture `3 present · 4 ✗ · 1 omitted`, consolidation
`6 present · 1 ✗ · 1 omitted`, recall `5 present · 2 ✗ · 1 omitted`. Six tools carry
cells: ai-memory, mempalace and agentmemory `[capture, consolidation, recall]`, mem0
`[consolidation, recall]`, memos `[consolidation]`, cognee `[]`. Tallies over those six
cells are capture 3, consolidation 5 and recall 4; the census rows count more tools
because they include openviking's decided capture ✗ and memori's decided components,
which stay prose.

### `concurrent_write_safety`

Group `write-path`, `value_type: closed-enum`, values `one-process`, `one-host`,
`false`.

> the widest scope covered by the default-path guard that orders or excludes
> concurrent writes to the tool's store: `one-process` (a lock, a single-writer actor,
> a queue or an optimistic check inside one process) | `one-host` (a guard that
> several processes on one host share, such as a file lock, a lease in a shared SQLite
> file, or a write-ahead log chosen for concurrent writers); `false` = no guard found
> on the write paths searched. The scope is of the guard itself, not of who can reach
> it: a single-owner daemon that serves many clients is `one-process`. Judged on the
> default path; the mechanisms, the write paths covered and the contention behaviour
> (refuse or queue) go in the cell comment.

A scope enum, not a presence key: every census tool has such a mechanism (see the
census), so presence would not discriminate (methodology rule 5d), while the scope
does. A scope enum flattens coverage (memos' lease guards one queue, mempalace's
guard covers every default write path), so covered write paths and contention
behaviour belong in the comment. Values are minted only from observed cells:
`several-hosts` is not minted (see the non-admissions).

NOT this fact:

- a storage engine's own guarantee that the tool only relies on (the SQLite
  write-ahead log for readers, Postgres), which is the engine's;
- a routine commit;
- a job bound or semaphore;
- process-leak pid files;
- backup or replication (agentmemory's mesh sync is replication);
- access control.

Rhyme risks: `memory_store` (the engine decides much of safety), `team_sharing`
(several humans, not write ordering) and `memory_revision` (who may change a memory,
not who may write at once).

Census row: `8 present · 0 ✗ · 0 omitted`. Cells over seven tools (memori, a stub,
carries none): `one-process` 3 (ai-memory, agentmemory, mem0), `one-host` 4 (openviking,
mempalace, memos, cognee).

### `agent_coordination`

Group `integration`, `value_type: presence`.

> one agent addresses or hands work to another through the tool, exposed to agents as
> an MCP tool, a CLI command or an API: directed messages or a mailbox, a task, action
> or lease queue, signals, or a shared event log whose entries agents address or
> claim. Per-agent isolation (agent-scoped records, ownership columns, agent ids used
> as filters) and sharing between humans are not coordination.

Admitted on three independent codebases, from the three newest deep-dives: ai-memory
(a directed, claim-once mailbox, traced in source), mempalace (an append-only event
log with task, event and artifact exchange) and agentmemory (ten orchestration tools
by name), the last two at registration level with delivery semantics not traced. The
medium is the memory store, persistent and cross-harness and addressed through the
tool's own surface, which is the category's own definition (the agent-to-time edge)
and what a single harness cannot absorb. A presence value flattens delivery shape
(mailbox, event log, lease queue); the regrade trigger is under the non-admissions.

NOT this fact:

- per-agent isolation (the `memory_scope` agent axis);
- sharing between humans (`team_sharing`);
- harness-native subagent messaging (`subagents`);
- workflow task queues (`parallel_orchestration`);
- replication between instances.

Rhyme risks: `team_sharing` and `memory_scope` (who may see, not who may hand work
over), `subagents` and `parallel_orchestration` (the harness and workflow sides of the
same word). No `kind_link`: no category-2 key states the harness-side fact, and the
harness-side candidate is argued below.

Census row: `3 present · 1 ✗ · 4 omitted`. Instances against the bar: 3 present
(ai-memory, mempalace, agentmemory), memos ✗ (its code, outside markdown files and one
separate app, shows no mechanism), openviking omitted (its search left in-pin channels
and two plugins unsearched), mem0, cognee and memori omitted (an integration outside
the pin, with no coordination surface named by the pin).

### Two enum values on existing keys

Values are minted on one verified instance (the rule binds keys, not values):

- `memory_scope` gains `global` (one store-wide scope outside any single project or
  user), on ai-memory's `default/_global` scope, addressable on write and read by an
  MCP scope argument and refused in combination with a workspace or project.
- `memory_store` gains `files` (the files are the record and git is absent or only on
  request), beside `files-git`, on openviking's plain files with a derived vector index
  and a git snapshot service that is enabled by default but caller-requested.
  ai-memory's per-write git versioning stays `files-git`. The definition also states
  the query-surface rule: the value names the data model's query surface, not the
  engine.

`reinject-only` (above) is the third value, minted on two instances.

## The census

The source of record for every count here is the census in
[`tools/5-memory/README.md`](../tools/5-memory/README.md) (2026-11-06; measure: each
tool's verdict word, present, ✗ or omitted, against a presence test frozen before the
reads, once per component for `llm_free_path`; population: eight tools at named pins,
ai-memory `8c39e4e67`, openviking `178a8cdfb`, mempalace `602d796c6` and agentmemory
`c5b8ebfb3` mapped from their own committed sections, and mem0 `001c2352`, memos
`85532420`, cognee `b948f88d4` and memori `538b61f` probed at their pins; everos and
memmachine are stubs whose source was not searched, so they are unset and not ✗). The
rows, each as present · ✗ · omitted:

| Candidate | Census row |
|---|---|
| `llm_free_path`, capture | `3 present · 4 ✗ · 1 omitted` |
| `llm_free_path`, consolidation | `6 present · 1 ✗ · 1 omitted` |
| `llm_free_path`, recall | `5 present · 2 ✗ · 1 omitted` |
| `concurrent_write_safety` | `8 present · 0 ✗ · 0 omitted` |
| `compaction_capture` | `4 present · 3 ✗ · 1 omitted` |
| OKF open-format axis | `2 present · 6 ✗ · 0 omitted` |
| `agent_coordination` | `3 present · 1 ✗ · 4 omitted` |

Admission path each candidate took under the repo's assessment cycle (reassess, new key
or new value):

- **New keys on the two-instance bar:** `llm_free_path` (six cells, three component
  verdicts that split), `concurrent_write_safety` (seven cells, two scopes),
  `compaction_capture` (six cells, two values) and `agent_coordination` (three present
  tools). All four clear the bar; each is graded by the census, not by a new read.
- **New values on one verified instance:** `global` (ai-memory), `files` (openviking),
  `reinject-only` (agentmemory and memos).
- **Not admitted:** the OKF open-format axis, whose conformant instances number one
  (ai-memory); openviking's instance is a declaration of a house `OKF_VERSION`, which is
  not conformance.
- **Why presence would not do for `concurrent_write_safety`:** 8 of 8 tools carry such
  a mechanism, so a presence key would tick every column and say nothing; the scope of
  the guard splits the same tools 3 · 4 (methodology rule 5d, an instrument that
  cannot discriminate).

## Rules the verdicts were re-checked against

Three rule statements the census used implicitly are written into the admitted keys'
definitions and NOT lists, and the verdicts re-checked against them:

- **Engine per key.** The judged engine is named by each entry. mem0 is judged on its
  open Python SDK for `llm_free_path` and `concurrent_write_safety`; for
  `compaction_capture` the in-pin plugin handler is the evidence and the hosted store is
  only the write target. A hosted or closed half is never source evidence for what a
  component does. Re-check: no verdict moves.
- **Outside the pin.** An integration outside the pin turns a ✗ into omitted only when
  the pin names a surface of the key's own class that it does not contain: for
  `compaction_capture`, a plugin, hook manifest or installer the pin names as the home
  of the handler; for `agent_coordination`, an agent-facing tool registry the pin names.
  A vendor tool list that names only other-class tools is testimony and does not turn an
  omission into ✗; the test that would is a dated tool listing or a pinned read of the
  separate repository. Re-check under this container reading: no verdict moves.
- **Setup-type check.** A setup-type check counts toward a component only when that
  component's own entry point sends a generative request on its default path; a
  client-construction or key-presence check that sends none does not. Re-check: cognee
  consolidation stays ✗ (its entry point reaches a first-run connection prompt that is
  a real generative request) and mem0 recall stays present (client construction sends
  nothing); no verdict moves.

Two verdicts would move under the opposite readings, and are named so the choice is
visible. **Cognee consolidation** moves ✗ to present if setup never counts (census
6 · 1 · 1 becomes 7 · 0 · 1, and cognee's cell `[]` becomes `[consolidation]`); the
switch that removes the connection test is recorded as cognee's `llm_free_path` option
instead. **Cognee `agent_coordination`** moves omitted to ✗ under a content reading of
the outside-the-pin rule (the pin must name coordination-class tools, and cognee's
catalog describes its out-of-pin integrations as memory add and search); mem0 and memori
move with it, census 3 · 1 · 4 becoming 3 · 4 · 1. The recommended readings are the
ones above, none of the three verdicts moves, and a verdict move would land as a dated
annotation under the census, never as a silent edit.

## Enum amendments and ripple rows

A block-level convention absorbs many rows at once: a memory cell reads the shipped
capability at the pin; a capability that is built but dark carries `DEFAULT-UNMOUNTED`
or `DEFAULT-OFF` in its comment; and it becomes an `options:` record
([ADR-0060](0060-options-with-default-grammar.md)) only when the dark state has a
different legal value of the same key. Instance lists in the registry notes are
re-derived from the reports' cells by script, never hand-typed.

Every row of the three re-read ripple tables whose owner is this vocabulary pass is
decided below, 42 rows in all (15 from the ai-memory and openviking re-read, 25 from
the mempalace and agentmemory re-read, 2 from the roster census). Row ids are
`<phase>:<line>` in the phase's own table. Disposition codes: DEF registry definition
text amended; VAL a new enum value; NOTE a registry note corrected or its instance list
re-derived; OPT absorbed by the options grammar; NON a dated non-amendment, its trigger
under the non-admissions; CMT a cell-comment correction in the cells commit.
[ADR-0052](0052-team-sharing-key.md) is not edited; its posture sentence is corrected
in the `team_sharing` registry note.

| Row | Target | Strain | Disposition |
|---|---|---|---|
| 16:10 | `memory_scope` | a global scope `default/_global` outside the list; a workspace profile scope `_profile` | VAL `global` on ai-memory alone; the cell gains it in the cells commit; `_profile` stays out as a label within one tool (NON) |
| 16:11 | `team_sharing` note | "RBAC absent by design" is true of the default only; per-project grants since 2.5.0 | NOTE posture sentence qualified in the registry note, ADR-0052 left as written; OPT `acl` |
| 16:12 | `team_sharing` note | "opposite postures" compares defaults while ai-memory offers both | NOTE the default-versus-default qualifier added |
| 16:13 | `write_admission` note | the zero-LLM profile pass admits on one marked sentence; no value for the combined posture | NOTE + OPT the cell keeps `evidence-gated`, the provider path exp-04 measured, as the report's stated exception to the fresh-install rule; `unfiltered` is the recorded alternative |
| 16:14 | `learning_loop`, `team_sharing`, `memory_revision` | no form for a configuration-dependent cell | OPT the options grammar |
| 16:15 | `hybrid_retrieval` note | "RRF over 4 streams" is five at v3.3.3 | NOTE five streams |
| 16:16 | `memory_revision` note | `proposed` is reachable through `require_approval`; the profile pass supersedes with no approval | NOTE + OPT `proposed` as the alternative |
| 16:28 | the 15 memory notes | instance lists omit openviking | NOTE instance lists re-derived from cells |
| 16:29 | `learning_loop` census | "background 7" is stale | NOTE census re-derived over every report: background 10, in-loop 1, proposed 2, false 4 |
| 16:30 | `memory_scope` | tenant, peer and group axes; "natively supports" is open | DEF reading rule: an axis counts when records are partitioned by it on write and at least one shipped read path uses it; NON tenant, peer and group as labels within one tool |
| 16:31 | `memory_store` | plain files with no per-write git | VAL `files` on openviking alone; its cell becomes `[files, vector]` in the cells commit; `files-git` is files plus git on the write path |
| 16:32 | `team_sharing` | a single-principal default; grants covering one namespace | DEF `acl` covers grants on any container, even a single namespace; NON `single-principal`, the unmounted state of a designed mode |
| 16:33 | `injection_trust_boundary` | strict versus lenient reading | DEF the strict reading: the injected text itself says data not instructions or fences it as untrusted; delimiters alone or an epistemic label alone do not suffice; NON a posture enum |
| 16:34 | `hybrid_retrieval` | a default-off calibration case | NOTE third calibration case |
| 16:35 | six openviking `# options:` comments | no form for a configuration-dependent cell | OPT migrated by the cells commit |
| 17:14 | `learning_loop` | filing versus extraction | NOTE census; NON sub-typing `background`, ADR-0056's parked trigger |
| 17:15 | the 15 memory notes | instance lists omit mempalace | NOTE instance lists re-derived from cells |
| 17:16 | `memory_scope` | wing, room, source file, palace | DEF the same reading rule as 16:30; NON the labels |
| 17:17 | `memory_tiers` | loading depths versus typed tiers | DEF a loading depth over one flat store is not a tier; a typed second store counts even when it ships unmounted |
| 17:18 | `team_sharing` | self-declared attribution | DEF `attribution-only` covers authenticated, caller-supplied and server-configured attribution |
| 17:19 | `write_admission` | an opt-in extractor's 0.3 threshold with no probation | NON for the opt-in extractor, which is not the autonomous path |
| 17:20 | `hybrid_retrieval` | a re-rank over one pool | NOTE mem0's precedent already counts it; one calibration paragraph |
| 17:21 | `injection_trust_boundary` | four postures | DEF as 16:33; NON the posture enum |
| 17:22 | five mempalace `# options:` comments | no form for a configuration-dependent cell | OPT migrated by the cells commit |
| 17:23 | `memory_store` | graph versus rows over a SQLite triple table | DEF the value names the data model's query surface, not the engine |
| 17:37 | `learning_loop` | a model path mounted by ambient key presence | NOTE the key-presence fact stays a comment; no option, the cell value is the same |
| 17:38 | the 15 memory notes | instance lists omit agentmemory | NOTE instance lists re-derived from cells |
| 17:39 | `memory_store` | key-value records in an engine the tool does not own; a dark vector half | DEF key-value records are `rows`; a list names what the shipped code builds and a dark half goes in the comment |
| 17:40 | `memory_scope` | a session partition with no recall filter; agent only in isolated mode | DEF the reading rule of 16:30; agentmemory's `session` is the boundary case and is not listed |
| 17:41 | `memory_tiers` | upper tiers empty on a keyless install | DEF as 17:17 |
| 17:42 | `team_sharing` | a server-configured user id; replication is not sharing | DEF as 17:18, plus a NOT statement: instance-to-instance sync is replication |
| 17:43 | `write_admission` | a deny list, a cap and a constant confidence | DEF gates that judge nothing about worth are not admission |
| 17:44 | `decay` | expiry versus decay | NON the definition already reads an expiry, forgetting or retirement lifecycle |
| 17:45 | `recall_injection` | varies by harness; a misplaced flag; an injection whose output never reaches the model | DEF the value is the leading integration's, and an injection whose output never reaches the model is not injection; OPT the per-harness alternatives |
| 17:46 | `hybrid_retrieval` | which streams are on by default | NOTE the keyless-default streams; OPT the single-stream mode |
| 17:47 | `injection_trust_boundary` | labelled on some surfaces only | DEF as 16:33; OPT the per-harness `true` alternatives |
| 17:48 | `harness_installer` | an MCP-entry merge | NON the definition already covers a config merge and the cell took it |
| 17:49 | `rule_extraction` | store records versus host-loaded files | DEF reading (b): a derived standing-instruction or skill record in the store counts, a file a host loads is the stronger form and the comment says which |
| 17:50 | `memory_import` | one unattributed SQLite source | NOTE source-family census |
| 17:51 | five agentmemory `# options:` comments | no form for a configuration-dependent cell | OPT migrated by the cells commit |
| 18:7 | cognee frontmatter comments | `save_interaction` and `improve` are not registered MCP tools at `b948f88d4` | CMT the 10 registered tools stated as fact, "an unregistered function is not an MCP tool" kept as INFERENCE |
| 18:12 | mem0 frontmatter comments | three plugin adapters ship a dream pass | CMT the dream passes added to the `memory_revision` comment; `caller-only` stands for the open SDK |

## Argued and not admitted (with triggers)

- **The OKF open-format axis** (2026-11-08). Census `2 present · 6 ✗ · 0 omitted`,
  but one conformant instance: ai-memory's pages carry OKF v0.2 frontmatter with an
  export command and a conformance gate. openviking's instance is a declaration of a
  house `OKF_VERSION` that never cites the specification, one version behind and with no
  conformance gate; that is not conformance. The six ✗ cells each name their house format
  beside a positive control. The axis would also have to separate a conformant export from
  a conformant on-disk tree. Trigger: a second conformant OKF adopter on the roster.
- **Harness-native agent messaging** (2026-11-08). Category-2 reports mention
  agent-to-agent messaging in prose (claude-code, gemini-cli, hermes-agent, warp); none is
  traced to a cell that could state a delivery shape, and the surface searched was the
  harness and workflow reports for message, mailbox and agent-team vocabulary. Trigger: a
  second harness read whose messaging is traced in source.
- **`several-hosts` on `concurrent_write_safety`** (2026-11-08). No observed cell
  exhibits it. openviking's Redis-backed lock provider is the lead, but it is not the
  default and that it spans hosts is INFERENCE (no source line says so; not run);
  cognee's several-hosts mechanism is a migration mutex, which covers migration runs and
  not data writes. Trigger: a cell or verified option whose default guard spans hosts.
- **Tenant, peer, group, wing and room labels, and `_profile`, as `memory_scope`
  values** (2026-11-08). Each is a label within one tool. Trigger: a second tool with
  the same axis.
- **`single-principal` as a `team_sharing` value** (2026-11-08). It is the unmounted
  state of a designed mode, recorded in the cell comment, or ✗ when no team mode exists.
  Trigger: a tool whose only shipped state is single-principal and which a reader needs
  separated from ✗.
- **An injection-posture enum on `injection_trust_boundary`** (2026-11-08). Four
  postures were seen across three reports (bare, enclosed but unlabelled, provenance
  labelled, instruction-only); the strict presence reading is adopted instead. Trigger:
  the owner wants the spread as a column.
- **`write_admission` for a bare numeric threshold** (2026-11-08). mempalace's opt-in
  extractor applies a 0.3 threshold with no probation, between `scored` and `unfiltered`,
  but it is not the autonomous path. Trigger: an autonomous default path that admits on a
  bare numeric threshold.
- **Splitting expiry from decay** (2026-11-08). The definition already reads an
  expiry, forgetting or retirement lifecycle. Trigger: a census whose expiry-only and
  decay-only tools fall into two groups a reader cannot tell apart.
- **An MCP-entry merge as a separate `harness_installer` value** (2026-11-08). The
  definition covers a config merge and the cell took it. Trigger: a tool whose installer
  only offers an MCP endpoint without touching config, beside one that merges, shown to
  need separating.
- **Sub-typing `learning_loop`'s `background` by trigger** (2026-11-08). ADR-0056's
  parked trigger is not met by filing versus extraction. Trigger: ADR-0056's own.
- **A delivery-shape regrade of `agent_coordination`** (2026-11-08). Presence
  flattens mailbox, event log and lease queue. Trigger: delivery semantics traced in
  source for two tools, then a shape enum replaces the presence key.
- **Two single-instance mechanisms named in agentmemory's report**
  (`acknowledged_durability`, `index_rebuild_at_start`) (2026-11-08). One instance
  each. Trigger: a second tool with the same mechanism.
- **The milestone research's proposed value sets** (native, degraded, absent; capture,
  inject, owns; two four-value write-safety sets) (2026-11-08). They were leads to
  test, not labels to adopt, and no cell needed them. Trigger: a census read that finds a
  cell none of the minted values can state.

## Consequences

- Registry entries are committed before any cell. The four keys, the two values, the
  amended definitions and notes and the re-derived instance lists land in the registry
  commit, with the matrices regenerated; the cells are written in a separate later
  commit, so every registry state has a green lint battery.
- The category README's key count advances 15 to 19, dated, with the four keys named
  and the non-admissions above added to its open questions; its census is untouched
  (a verdict move would be a dated annotation, never a silent edit).
- The 20 frontmatter `# options:` comments migrate to the `options:` mapping in the
  cells commit ([ADR-0060](0060-options-with-default-grammar.md)), together with the
  cell-comment corrections above (18:7, 18:12).
- ADR-0052 is not edited; the team_sharing posture is corrected in its registry note.
- No decoder is needed: no prior prose used other names for these facts, and every
  amendment adds a reading rule or a value without renaming one.
- The conclusions, the standards watch note, the design principles, the root README and
  the category-taxonomy prose that should absorb these changes belong to the next phase's
  fold-in and are not edited here.
