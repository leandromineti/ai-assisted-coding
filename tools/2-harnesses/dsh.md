---
name: dsh
category: 2
surfaces: [web]
execution: local
environments: [host, remote-sandbox]  # remote-sandbox = the e2b POC packages, verified in source, opt-in, no shipped bundle. DRIFT 2026-09-24 (pin unchanged): the e2b packages were retired upstream by c49db8bc8c (2026-09-11) and replaced the same day by an SSH family (`packages/ssh/{ssh,fs-ssh,subprocess-ssh,sandbox-ssh}`) in the same opt-in, no-bundle posture — the value survives in kind, the implementation named here is gone at HEAD; see § Drift check
environment_relation: internalize
maker: DeepSeek
url: https://github.com/deepseek-ai/deepseek-harness
license: MIT
access: open-source
stack: [TypeScript, Node.js]
version: dsh-v0.1.1-rc.2
commit: b150a551b8
first_commit: 2026-06-10
stars: 190941
stars_at: 2026-08-24
read_at: 2026-08-24
depth: deep-dive
harness_features:
  mcp: true              # client only, tools-only bridge, NOT default-mounted ("each server command is trusted executable code outside the agent sandbox", apps/cli/reference/README.md:93)
  lsp: true              # agent-consumed `lsp` tool, 4 read-only ops; diagnostics explicitly discarded (lsp-stdio/src/connection.ts:254); not in any shipped bundle
  hooks: true            # typed engine events default-on; PLUS bridges that run unmodified Claude Code hooks.json / Codex hook configs (packages/hooks/*) — bridges in no shipped bundle
  context_retrieval: model-driven  # ADR-0055, cell set 2026-09-04 probe-pass at the pin: no index anywhere in the tree; content search is a plain ripgrep-backed grep tool (packages/fs/tool-fs-search/src/grep.ts:322, runRipgrep) the model dispatches like any other — consistent with body § context assembly, where rules files, skill digests and compaction are the only automatic injections
  context_compaction: [llm-summarize, prune]  # ADR-0055, cell set 2026-09-04 from the deep-dive: default-on compaction pipeline, LLM summary + deterministic prune, thresholds in source (body § context assembly — the KV-cache-discipline bet rides on it)
  turn_end_gates: engine # agent/turn-stopping serial boundary, "data decides" (agent-loop/src/agent.ts:294-300); hook grade also reachable via the CC-bridge Stop mapping
  tool_approval: sandbox # regraded ✗→sandbox 2026-09-04 per ADR-0053 (same evidence, 2026-08-24 deep-dive): no ask-gate — tools/pre-execute default is allow (core/tools/src/index.ts:1477) — but the compiled per-call OS sandbox stands in its place; the sole prompt in a stock run is a model-initiated one-shot sandbox escalation
  gate_model_authority: approve  # DEFAULT-OFF: `experimental/auto-review` (new at 477b4f4205, in the CLI dependency closure) has "the current agent's provider and model assess the pending action; an allowed call executes with Full access, and a denied call asks the user" — shipped switched off, opt-in from the Web sidebar; the default composition stays sandbox-only (§ Drift check 2026-09-24, 10)
  unbypassable_gates: false  # `danger-full-access` mode skips `ctx.sandbox.confine` entirely (ptc-runtime-node/src/index.ts:224 @ 477b4f4205; the same policy switch at the pin, § Environment)
  skills: true           # SKILL.md convention, 6-root precedence, digest-gated catalog; on in standard/code/cordis presets
  subagents: true        # 6 providers incl. real Codex and Claude Code children; spawn/fork in base bundle, depth cap 3 (bypassed via workflow/ralph — host.ts:352)
  ptc: true              # run_code in a Node worker thread, tools bound as typed fns from the live registry; default mode `native`, opt-in via DSH_TOOLS_MODE or the shipped "PTC 模式" preset DRIFT 2026-09-24 (pin unchanged): the worker-thread runtime was replaced by `packages/ptc-runtime/ptc-runtime-node` (7c9bb5914c, 35af8698c2, 2026-09-12/13), which confines each run_code as a fresh Node process through the same `ctx.sandbox.confine` as bash (ptc-runtime-node/src/index.ts:224 @ 477b4f4205) — the mechanism described here is gone at HEAD, the presence claim holds; see § Drift check 2
  plan_mode: mode        # sticky LOGGED session state + prompt section + exit tool; deliberately NOT a tool restriction (plan-mode/src/index.ts:1-7)
  rules_files: ["AGENTS.md", "CLAUDE.md", "AGENTS.local.md", "CLAUDE.local.md"]  # + user-global ~/.dsh/AGENTS.md; per-preset (the `minimal` preset omits the loader entirely)
  model_agnostic: true   # llm seam + pi-ai adapter (3 wire protocols); DeepSeek privileged in every default (agent-default-model → deepseek-v4-flash) DRIFT 2026-09-24: the default model string is `deepseek-flash` at 477b4f4205 (cordis.patch.yml:86); the posture is unchanged
  session_sharing: true  # export/artifact only: session ZIP export + resume; share LINKS verified absent (no shareUrl anywhere; loopback-bound server)
  evals: false           # checked and absent: no model/agent benchmark harness anywhere (find over eval|bench dirs → empty); 872 unit specs + transcript-replay snapshots are software tests, not evals
  learning_loop: false   # checked and absent: no native agent-written memory or store; agent-instructions is a pure reader; vendor ships default-off third-party MCP memory examples with "no memory server is present in the shipped composition"
---

# dsh (DeepSeek Harness)

Deep-dive 2026-08-24, three readers at the pin, one tract per ADR-0021 component —
**all three components traced**: the loop, context assembly, and the permission gate.
Claims below carry file:line at `b150a551b8` (v0.1.1-rc.2, 2026-08-21). Registered
2026-08-18 at README level ([issue #19](https://github.com/leandromineti/ai-assisted-coding/issues/19));
this read executes that ticket. One registration correction: the repo was *published*
2026-08-13 but `first_commit` is 2026-06-10 — the five-day figure is the star ramp
(159.6k at +5d; 190.9k at +11d), not the code's age.

## What it is

DeepSeek's vendor-native harness: a TypeScript plugin container (vendored Cordis, 227
packages counted by `ls -d packages/*/*/ | wc -l`) that composes an agent from ordered
YAML patch overlays over an **empty root**, launched as a locally served web UI
(`npx @deepseek-ai/dsh web`, 127.0.0.1:3080) or a headless profile. Developer preview,
breaking-changes warning, `SESSION_FORMAT_VERSION: 0` with no compatibility promise.

## The distinguishing bet

**"Everything is a plugin" — and at this pin the claim is structurally true and
mechanically checkable, including for the agent loop itself.** The loop is row ~~65~~ **76** of 78 (CORRECTED 2026-09-24 at the pin itself: `git show b150a551b8:packages/bundle/base/cordis.patch.yml | grep -nE '^    - id: '` — 78 rows, `agent-loop` the 76th; the ordinal had been stated without its measure. Row 90 of 93 at 477b4f4205)
in the base bundle patch (`packages/bundle/base/cordis.patch.yml:436-439`), loaded with
the same two keys as `tool-bash`; it publishes itself through an `AgentFactory` seam
(`agent-loop/src/index.ts:350`) that a six-line user patch could fill with a different
implementation, and stub factories in the product's own tests prove the seam. Three
honest qualifications, all from dsh's own source: the factory is a **singleton** (a
second registration throws, `core/agent/src/index.ts:373-374`) — replaceable, not
stackable; editing it is governed by policy ("Plugins, not loop changes", root
AGENTS.md) — a plugin by construction, a de-facto kernel by convention; and its
internals are sealed (the concrete `ReactLoopAgent` is not exported). The intended
extension path is interception: five published decision points (`agent/pre-step`,
`agent/request`, `agent/request-error`, `agent/turn-stopping`, and the tool-result
channel), 59 typed events in a generated, CI-gated producer/consumer census (a count with no stated measure — 2026-09-24: `grep -cE '^\| `'` over docs/event-producer-consumer.md gives 63 at the pin and 89 at 477b4f4205; the direction is checkable, the ordinal is not)
(`docs/event-producer-consumer.md`).

A second bet rides on the first: **KV-cache discipline as an enforced, repo-wide design
constraint** — see Context assembly.

## Stack & repo shape

13,147 commits · 7,903 tracked files · `md(2506) ts(2472) yaml(1154)` (repo-facts.sh,
2026-08-24). pnpm workspaces: `packages/<group>/<pkg>` (227), `vendor/` (Cordis, pinned
source copies with an upstream-SHA manifest), `native/landlock-run` (a static C sandbox
launcher published as its own npm family), `python/` (SDK driving a bundled Node
runtime), `apps/cli`, `apps/web`. Two shipped profiles: `web` = base+web-app bundles,
`headless` = base+headless (`boot/app-boot/src/profile.ts:113-117`). Four shipped agent
presets: `standard` (default), `code` ("PTC 模式"), `minimal`, `cordis`. Test posture:
per-file **100%** coverage thresholds in CI, 872 `.spec.ts`, 136 `.e2e.ts`, 22
boot-the-real-binary transcript-replay snapshot suites — and **zero model evals**.

## Drift check — 2026-09-24 (not a re-read; the pin is unchanged)


6,875 commits / 14,742 files in 34 days — and unlike every other drift check in this repo,
the regime has to be characterised before any of it can be read. **Median 184 commits/day,
peak 363 (2026-08-31), no day below 38 after 2026-08-18**; 56 distinct authors with the top
two at 1,096 and 1,092 commits and no author above 16% of the window; **31% merges**
(2,146 of 6,875), 724 distinct merge sources, **all from `deepseek-harness/` — zero fork
merges**. Subjects are conventional-commit typed (`fix:` 1,813, `test:` 1,034, `docs:` 572,
`feat:` 514 of 4,729 non-merge commits; 83 non-conforming). One agent trailer and one
"generated with" line in 6,875 bodies. The tell is branch naming: **193 merges come from
`deepseek-harness/worktree/<topic>` branches** (`worktree/issue-5003-review-a73e0a`,
`worktree/pin-official-deepseek-first`), the branch shape dsh's own `workflow`/worktree
tooling produces. This is a large human team on a per-topic worktree workflow at release
cadence, not a bot flood: 19 tags were cut in the window (`dsh-v0.1.2-alpha.1` 2026-08-28
through `dsh-v0.1.7-rc.2` 2026-09-24, six minors, 0.1.4 skipped entirely), all still
alpha/rc — **dsh has never cut a stable tag** (`git tag -l 'dsh-v*' | grep -vE 'alpha|rc'`
→ empty, across all 23 tags). Tracked files went 7,903 → 13,850; packages 227 → 312.

**509 non-merge commits touch a file this report cites** (31 paths, incl. the `packages/hooks`
directory; `git log --no-merges --format=%h b150a551b8..477b4f4205 -- <31 paths> | wc -l`),
which is the set that was checked. Heaviest: `docs/event-producer-consumer.md` (151),
`scripts/verify-package-readme-model-experience.ts` (79), `docs/tool-catalog.md` (56),
`AGENTS.md` (47), `packages/hooks/` (46). Exactly one cited path no longer exists at HEAD
(`workflow-worker-thread/src/host.ts`, renamed — see 3); `packages/bundle/web-app/src/startup.ts`
is byte-identical (`git rev-parse <rev>:<path>` matches at both revs).

Five contradictions, and the first two were falsified within **one day** and **eighteen days**
of the read.

**1. CONTRADICTED — the local server now authenticates. The claim died the day after the read.**
The report states: *"the local server has **no inbound authentication**, saying so twice in
source (a DNS-rebinding fence 'explicitly not authentication'…)"*, and cites
`web-app/src/startup.ts:74-76`. Both source statements are gone.
`git grep -n 'not authentication' 477b4f4205 -- packages/` returns **zero hits**;
at the pin it returned `packages/client/connection/README.md:9` ("The fence is a reachability
policy, not authentication; the Web carrier provides no authentication [stage]") and
`packages/client/connection/src/index.ts:77` ("DNS-rebinding fence, explicitly not
authentication"). At HEAD the same package ships `src/browser-auth.ts` (**absent at the pin** —
`git cat-file -e b150a551b8:packages/client/connection/src/browser-auth.ts` → "exists on disk,
but not in b150a551b8"), `inject = ['credentials']` on the Connection config
(`packages/client/connection/src/index.ts:89`), a `connection/request` waterfall typed
*"Authenticated incoming HTTP request"* (`:67`), and an `OperatorPeer` every admitted request
speaks for (`README.md:45`). The mechanism is a signed host-bound cookie whose secret is the
`client-connection/browser-session` grant in `ctx.credentials`, persisted in
`$DSH_HOME/.credentials.yaml`, `HttpOnly`/`SameSite=Strict`, 30-day default
(`packages/client/connection/README.md:41 @ 477b4f4205`). The trust fence survives beside it,
demoted to what it always was: *"These checks defend DNS rebinding and cross-site browser
requests; **they never establish identity**. A failed Host/Origin check returns 403, while a
trusted but unauthenticated request returns 401"* (`README.md:43`). Landing commit:
**`3e24087bfa` (2026-08-25) `fix(web): authenticate the browser Host API`** — *one day after
the 2026-08-24 read* — with a dated in-repo decision record,
`.agents/notes/implemented/architecture/2026-08-24-browser-token-authentication.md`, itself
absent at the pin. The report's claim was true when written and false 24 hours later.
`--host 0.0.0.0` is still refused (`packages/bundle/web-app/src/startup.ts:75`, byte-identical
file), so the *surface* claim holds; the *no-auth* claim does not.

**2. CONTRADICTED — Code Mode is no longer a privilege door. The PTC runtime now runs under the
same OS sandbox as `bash`.** The report's permission-model section names *"two shipped, labelled
doors"* through which the model reaches privilege, the first being: *"Code Mode runs model
TypeScript in a worker thread with full Node globals — 'containment, not a security boundary',
strictly more privileged than the Landlock-confined `bash` beside it"*. That was exact at the pin:
`packages/code-runtime/code-runtime-worker-thread/src/index.ts:1-5 @ b150a551b8` opens *"This is
containment, not a security boundary: model code has bash-equivalent trust"*, and
`git grep -c sandbox b150a551b8 -- packages/code-runtime/code-runtime-worker-thread/src/` returns
**zero hits**. The whole `packages/code-runtime/` group is gone at HEAD, replaced by
`packages/ptc-runtime/{ptc-runtime,ptc-runtime-node}`, and the replacement confines:
`confined = policy.mode === 'danger-full-access' ? undefined : await this.ctx.sandbox.confine(argv, { ...policy, mode: policy.mode }, signal)`
(`packages/ptc-runtime/ptc-runtime-node/src/index.ts:224 @ 477b4f4205`), with
`static inject = ['fs', 'subprocess', 'sandbox', 'sandboxPolicy']` (`:53`) under the header
*"Node provider; direct file effects use the same sandbox service as Bash"* (`:51`). The
dated decision record —
`.agents/notes/implemented/architecture/2026-09-11-sandboxed-node-ptc-runtime.md` — states the
defect this report recorded, in dsh's own words: *"A Node worker isolates JavaScript state but
does not apply the calling Session's OS sandbox policy. Model code can import filesystem and
subprocess APIs directly, bypassing the tool-policy path even when nested `tools.*` calls receive
the correct checks."* Each `run_code` is now one fresh Node **process**, confined through
`ctx.sandbox`, with lifetime owned by `ctx.subprocess`; the VM is explicitly demoted to
ergonomics — *"**The VM is not a security boundary** — withheld globals guide script authors;
**OS policy governs code that reaches Node**"* (`packages/workflow/workflow-ptc/README.md:159`).
This closes door one. The frontmatter `ptc: true` comment ("run_code in a Node worker thread")
is now wrong on mechanism; the **Surprises 3** framing ("the gate is the sandbox; the honest
comparator is Codex") is *strengthened*, since the last unsandboxed model-code lane closed.

**3. CONTRADICTED — the Ralph tool no longer ships on.** The report: *"The Ralph technique
ships as a native default-on tool (`tool-ralph`, `maxRounds: 64`, ceiling 256)"*. At HEAD the
base bundle row carries `disabled: true`
(`packages/bundle/base/cordis.patch.yml:446-451 @ 477b4f4205`), as do the `standard`, `ptc`
and `cordis` preset rows. Commit **`73985344cd` (2026-09-13) `feat(presets): disable ralph in
the default compositions`**, with the note
`.agents/notes/implemented/simplification/2026-09-12-ralph-off-in-shipped-defaults.md`, whose
reasoning is another dsh-publishes-its-own-negative-results entry: *"A default session
therefore carried a tool whose own description told the model not to reach for it, and the
default profile's catalog advertised a capability the Harness does not yet stand behind."*
The package, contract and tests remain; `maxRounds: 64` is unchanged. The **depth-cap bypass
this report found still exists** — see 5.

**4. CONTRADICTED — the E2B packages are gone; `environments: [host, remote-sandbox]` needs
re-deciding.** The report's environment section: *"**`bind` available, not default**: the `e2b`
POC packages swap `ctx.fs`/`ctx.subprocess` for E2B adapters"*, and the frontmatter comment
*"remote-sandbox = the e2b POC packages, verified in source, opt-in, no shipped bundle"*. The
`packages/e2b/` group (`e2b`, `fs-e2b`, `subprocess-e2b`) is deleted at HEAD by
**`c49db8bc8c` (2026-09-11) `refactor(e2b): retire remote execution providers`**; the only
surviving mention in the tree is its own retirement note,
`.agents/notes/implemented/simplification/2026-09-11-remove-e2b-providers.md` — *"The
repository excludes the E2B sandbox owner, filesystem provider and subprocess provider… It
supplies **no E2B execution backend**."* The cause is the very change in 2: PTC's confined
child needs a control descriptor the pinned `e2b@2.29.1` SDK could not carry. A replacement
family arrived the same day: `packages/ssh/{ssh,fs-ssh,subprocess-ssh,sandbox-ssh}`, per
`.agents/notes/implemented/architecture/2026-09-11-posix-ssh-runtime.md`, in the **same
posture** the report recorded for e2b — opt-in, in no shipped bundle
(`git grep -n 'fs-ssh|subprocess-ssh|sandbox-ssh' 477b4f4205 -- packages/bundle/ apps/cli/package.json`
→ empty, exactly as `e2b` was at the pin). So `remote-sandbox` survives *in kind* with a
different implementation; the sentence and the frontmatter comment naming e2b do not.

**5. CONTRADICTED (citation only) — the depth-cap bypass is intact, but its address moved.**
The report cites `workflow-worker-thread/src/host.ts:352-365` for *"children started via
`workflow`/`ralph` pass no `maxDepth`… escaping the subagent depth cap of 3"*. That package
no longer exists: `7c9bb5914c` (2026-09-12) `refactor(ptc): align runtime packages and services
with PTC naming` and `35af8698c2` (2026-09-13) `fix(workflow): execute orchestration in the
sandboxed PTC runtime` renamed it to `packages/workflow/workflow-ptc/`. **The bypass itself
reproduces at HEAD**: the sole `subagents.start` call in `packages/workflow/` is
`packages/workflow/workflow-ptc/src/host.ts:200 @ 477b4f4205`, and its request object still
carries only `prompt`/`parent`/`signal`/`outputSchema`/`agentOptions` — no `maxDepth` field
(`git grep -n 'subagents.start' 477b4f4205 -- packages/workflow/` → one hit). Correct the
address, keep the finding.

**6. CORROBORATED — all three headline claims, verbatim, in the contributor policy at HEAD.**
`git show 477b4f4205:AGENTS.md` (151 → 182 lines, 47 commits in window):
*"DeepSeek Harness is an **all-plugin** Cordis agent harness"* (`AGENTS.md:3`);
*"**Model-visible ⟺ logged**: anything that reaches a model request must be reconstructable
from the session log; a new model-visible input requires a session event"* (`:136`);
*"**Plugins, not loop changes**: new behavior goes on documented extension points; changing
`agent-loop` requires updating docs/architecture.md"* (`:137`). The report's headline is
policy-corroborated at HEAD, not just at the pin.

**7. CORROBORATED — and the plugin bet survives an 85-package expansion structurally.**
Packages 227 → **312** (`git ls-tree -r --name-only <rev> packages/ | grep -c '^packages/[^/]*/[^/]*/package.json$'`);
base-bundle rows 78 → **93**. `agent-loop` is still a plain bundle row with the same two keys
as any other (`packages/bundle/base/cordis.patch.yml:510-513 @ 477b4f4205`, now row 90 of 93),
`AgentLoop extends Service implements AgentFactory`
(`packages/core/agent-loop/src/index.ts:330 @ HEAD`, was `:296` at the pin), and the
singleton qualification the report insisted on is intact — `if (this.factory !== undefined)
throw new Error('an agent factory is already registered')`
(`packages/core/agent/src/index.ts:360 @ HEAD`, was `:373-374`). Group churn: **removed**
`code-runtime`, `e2b`, `examples`; **added** `ptc-runtime`, `ssh`, `browser-use`,
`computer-use`, `document`, `deliverables`, `webhook`. Everything new arrived as packages.

**8. CORROBORATED — the whole loop section, unchanged in substance.** Turn-end gate still a
serial boundary (`await this.dispatch.serial('agent/turn-stopping', { turn, signal })`,
`packages/core/agent-loop/src/agent.ts:343 @ HEAD`, was `:294-300`); *"Data decides, so listener
order cannot change the outcome"* still at `packages/core/agent/src/runtime-types.ts:369`
(was `:269`); **no iteration budget** — `git grep -nE 'maxSteps|maxTurns|maxIterations'
477b4f4205 -- 'packages/*/*/src'` returns **zero hits**, and the README's deliberate statement
survives with a pointer added: *"**No built-in turn budget** — … a policy that bounds runaway
turns must cancel from an existing lifecycle extension point such as `agent/turn-stopping`"*
(`packages/core/agent-loop/README.md:202`). Six subagent providers intact; the `standard`
preset still ships `subagent_codex` and `subagent_claude_code` rows `disabled: true`
(`packages/bundle/web-app/presets/standard.patch.yml:103-118`). Sandbox still fails closed —
*"refusing to run the command unconfined"* (`packages/sandbox/sandbox/src/index.ts:136`, was
`:131-144`). Permission waterfall default still `allow`
(`packages/core/tools/src/index.ts:1507 @ HEAD`, was `:1477`), and `allowed-once` is still the
only grant: *"`'allowed-once'` is the only grant"*
(`packages/interaction/user-approval/src/index.ts:211`); a HEAD-wide grep for
`allow.always|always.allow|remember.*approval|persistent grant` over `packages/*/*/src`
returns zero. The second privilege door is untouched: a host-only dynamic Cordis plugin still
activates with no approval request (`packages/extensions/cordis-host-runner/src/index.ts:274-279`,
the `plan.definition.clientCode === undefined` branch — the approval arm guards the *client*
half, and did so at the pin too, `index.ts:278 @ b150a551b8`).

**9. CORROBORATED — context assembly, including both registry cells set by the 2026-09-04
probe-pass.** `context_retrieval: model-driven` holds: content search is still a plain
ripgrep dispatch (`runRipgrep` at `packages/fs/tool-fs-search/src/grep.ts:323 @ HEAD`, was
`:322`), and a HEAD-wide `git grep -ilE 'embedding|vector.?(store|db|index)|semantic.?search'`
over `packages/*/*/src` returns **zero hits** — no index appeared in 85 new packages.
`context_compaction: [llm-summarize, prune]` holds, with the summarizer's cache rationale
verbatim at `packages/compaction/compaction-basic/src/summarizer.ts:30` (was `:24-30`). The
CI-gated `#### KV Cache effect` requirement is not just alive but *scaled*:
`scripts/verify-package-readme-model-experience.ts:17` still owns the heading constant (79
commits in window), and package READMEs carrying it went **223 → 305**
(`git grep -l '#### KV Cache effect' <rev> -- packages/ | grep -cE '^packages/[^/]+/[^/]+/README\.md$'`).
*Note for a re-read:* the report's "30+ packages" is true but reads as an order of magnitude
low — it was 223 at its own pin. "No per-model prompts" holds (`prefix: You are a coding agent
powered by the {{model}} model.`, `packages/bundle/web-app/presets/cordis.patch.yml:17-18`). The
anonymous-UUID header holds and was hardened into its own package: the header is emitted at
`packages/llm/llm-deepseek/src/adapter.ts:128` (was `:519-530`) from
`getOrCreateAnonymousUserId()` (`src/host.ts:25`), now `packages/identity/anonymous-user-id`,
whose README states *"**Random, never derived.** The id comes from `crypto.randomUUID()`"*
(`:66`).

**10. REFINED — a shipped, default-off *model-driven* permission stage now exists, so the
"only ask/deny producers are the unmounted hook bridges" sentence is out of date.**
`packages/experimental/auto-review` is new (absent at the pin) and emits `kind: 'deny'` /
`kind: 'ask'` on the pre-execute waterfall (`src/index.ts:643,660,672 @ 477b4f4205`). It is a
real third producer and it is **in the CLI's dependency closure** —
`apps/cli/package.json:103` lists `"@deepseek-ai/dsh-experimental-auto-review": "workspace:*"` —
unlike the hook bridges, which remain in no bundle. Its own README keeps the report's
qualifier alive: *"Before each native or PTC inner tool call, the current agent's provider and
model assess the pending action; an allowed call executes with **Full access**, and a denied
call asks the user. The dsh installation **ships this [stage] switched off**; default Web keeps
its three permission modes until it is switched on from the Web sidebar's Plugins page… Auto
review is experimental: it can allow unsafe actions, deny useful work, and spend additional
tokens."* Landed `55e53907ab` (2026-09-09) `feat(permission): add experimental Auto review`,
with ~12 follow-up fixes through 2026-09-17. **The report's boundary test — "mechanically no,
*in the default composition*" — still holds exactly as written**, and this is the first
tracked instance of dsh shipping an LLM-judge permission gate at all. Worth a `tool_approval`
re-think at the re-read, not a regrade now: the shipped default is still sandbox-only.

**11. REFINED — the KV-cache bet's founding constraint has been *relaxed for one model*, by
model change rather than harness change.** The report's second bet rides on "changing facts
land as user-role messages after retained history… so switching policy does not rewrite the
stable system-prompt cache prefix" — and that exact comment survives verbatim
(`packages/interaction/user-approval/src/index.ts:161 @ HEAD`, was `:201-203`). But
`c988a6796f` (2026-09-07) `feat(agent-loop): append system prompt changes on capable routes`
adds a second mode, documented at
`.agents/notes/implemented/feature/2026-09-02-in-history-system-prompt-replacement.md`:
*"A DeepSeek model… accepts a `system` message at any position of the conversation and treats
the latest one as the complete effective system prompt… the harness can append the new prompt
after the cached history instead of rewriting message 0, and the prefix stays warm."* It is a
per-route capability (`SystemPromptUpdate = 'in-history'`), declared by exactly one catalog
entry — the default model — and every `dsh-llm-pi-ai` route keeps the rewrite behaviour. The
discipline is unchanged; the *reason for one of its mechanisms* is now conditional. This is
the single most re-read-worthy change in the context tract: the note says in its own words
that the runtime-context snapshot design "exists precisely because moving a changing fact out
of the prompt was the only way to keep the prefix stable" — and that premise now has an
exception.

**12. REFINED — shipped-surface and preset vocabulary moved under the report's frontmatter.**
The `code` preset ("PTC 模式") is now `ptc`; the four shipped presets are `standard`, `ptc`,
`minimal`, `cordis` (`packages/bundle/web-app/presets/*.patch.yml @ HEAD`). The default model
string went `deepseek-v4-flash` → `deepseek-flash`
(`packages/bundle/base/cordis.patch.yml:86`), so the `model_agnostic` frontmatter comment
needs one token changed. The `tool-subagent-report` package was dropped. The event census the
report cites as "59 typed events" (`docs/event-producer-consumer.md`, the window's most-churned
cited file at 151 commits) does not reproduce under any measure I could state —
`grep -cE '^\| \`'` gives **63** at the pin and **89** at HEAD; the direction (growth) is what
matters, the ordinal is not re-checkable. Vendor metadata: stars **190,941 → 235,052**
(`gh api repos/deepseek-ai/deepseek-harness --jq .stargazers_count`, 2026-09-24).

**13. SCORED — the report's dated prediction landed in seven days, and landed sideways.**
The open question reads: *"The convergence prediction from the roster registration stands:
multi-surface expansion (TUI/IDE) from the current single web surface — `execution: local` +
no-inbound-auth make a hosted/async-remote shape a large step. **Falsifiable by ~2027-01**."*
Scored the way a preregistered forecast should be:

- **Direction: right, and early.** dsh is no longer single-surface. `apps/desktop` and
  `apps/desktop-host` are new in the window; first commit **`19444907f0` (2026-08-31)
  `feat: electron 打包`** — *seven days after the read*, ~4 months ahead of the stated
  falsification horizon. `apps/desktop/package.json` is versioned `0.1.7-rc.2` in lockstep
  with the tag, with mac code-signing/notarisation and a Windows build in the same week.
- **Specific form: wrong.** The prediction named **TUI/IDE**; what shipped is an **Electron
  desktop shell** — still no TUI (`git ls-tree -r -d 477b4f4205 packages/ apps/` shows no
  TUI/ink package). The desktop app is "an Electron shell around the complete dsh Web
  application" (`apps/desktop/README.md`) — a second *carrier* over the same web surface,
  which is a cheaper move than the report priced.
- **The named blocker was removed, not routed around.** The report reasoned that
  "`execution: local` + no-inbound-auth make a hosted/async-remote shape a large step."
  Both halves moved: inbound auth shipped the day after the read (1), and the desktop
  carrier ships DeepSeek **account** sign-in — `packages/credentials/deepseek-account` and
  `packages/credentials/deepseek-account-platform` are both new (pin had only
  `authorization`, `credentials`, `credentials-local`), directly against the report's
  *"no keychain, **no vendor account login mounted**"*. A hosted shape is now a materially
  smaller step than the report judged.
- **Verdict:** the prediction's *falsifiable core* (multi-surface by ~2027-01) resolved
  **TRUE, early**; its *mechanism* (TUI/IDE, blocked by local+no-auth) resolved **false**.
  Calibration note: the report priced a harness's surface expansion by its architectural
  blockers, and the vendor removed the blockers in under a month.

**Not re-probed:** the run probe's finding (npx OOM on an 8 GB host, >10 min install, 296 MB
closure at `@deepseek-ai/dsh@0.1.1-rc.2`) was explicitly flagged "worth re-probing at the next
drift check". This triage is source-only and installs nothing, so that item is **carried
forward, unresolved**, and belongs to the re-read. It is now a moving target: 85 new packages
and an Electron shell all landed since.

**What a re-read should cost:** high, and higher than codex's. The three ADR-0021 components
the deep-dive traced come out asymmetrically — the **loop tract reproduces almost entirely**
(8) and could be spot-checked rather than re-read; the **context tract needs one real
re-read** for the in-history prompt mode (11); the **permission tract needs a full re-trace**,
because two of its three load-bearing findings (the Code Mode door, the no-auth server) are
dead and a shipped LLM-judge stage appeared (2, 1, 10). On top of that sit three genuinely
new surfaces the deep-dive never saw — desktop/Electron + account credentials, the SSH
execution family, and `browser-use`/`computer-use` — on a tree 75% larger (7,903 → 13,850
files, 227 → 312 packages). Shape: the proven three-tract pattern **plus a fourth reader for
the new surfaces**, i.e. ≈1.3× the 2026-08-24 deep-dive, with the cheap loop tract paying for
part of it. Do not re-read at a rate above one minor version: at 184 commits/day the clone is
~1,300 commits stale by the end of a week's work.

## Architecture — the traced loop *(deep-dive 2026-08-24)*

- **Turn-end gate, grade `engine`, and a novel shape.** `agent/turn-stopping` is a
  serial boundary awaited before a turn may close (`agent-loop/src/agent.ts:294-300`);
  an objecting listener does not return a veto — it **steers real messages into the
  inbox**, and the loop re-reads the inbox after all listeners settle: *"Data decides,
  so listener order cannot change the outcome"* (`core/agent/src/runtime-types.ts:269`).
  Every boolean-returning Stop hook in the tracked set is order-dependent; dsh made
  multiple stop-blockers compose by construction.
- **No iteration budget, stated on purpose.** `grep` for
  `maxSteps|maxTurns|maxIterations` over non-test source → 0 product hits;
  `agent-loop/README.md:134`: *"No built-in turn budget — … a policy that bounds
  runaway turns must cancel from an existing lifecycle extension point."* One found
  bypass: children started via `workflow`/`ralph` pass no `maxDepth`
  (`workflow-worker-thread/src/host.ts:352-365`), escaping the subagent depth cap of 3.
  *(Path moved upstream 2026-09-12/13 to `packages/workflow/workflow-ptc/src/host.ts:200 @ 477b4f4205`; the bypass reproduces there — § Drift check 5.)*
- **Bounded auto-continuation with split authority.** `goal-round-driver` (default-on)
  re-prompts an idle agent toward an armed goal; the **model proposes** `maxGoalRounds`
  via the goal tools, a **human arms** the goal (direct-human root authority,
  `docs/tool-catalog.md`). The Ralph technique ships as a native default-on tool
  (`tool-ralph`, `maxRounds: 64`, ceiling 256; **default-OFF since 73985344cd, 2026-09-13** — the row carries `disabled: true` at 477b4f4205, § Drift check 3): one fresh structured-output child per
  round, 16 KiB bounded handoff. Exactly one leaf tool in the repo can end a turn
  (`structured_output.concludeTurn()`); a *failed* tool result can never conclude.
- **`ptc`**: `run_code` is a reserved name outside the filterable registry tiers;
  model TypeScript is type-stripped and run in a fresh Node **worker thread** with all
  other tools bound as typed functions generated from the live registry (a Python
  flavour exists); sub-calls re-enter the full guarded executor and are logged without
  re-entering model history. Default presentation is `native`; the `code` preset flips
  it, collapsing the wire schema to `run_code` alone.
- **Dispatch**: parallel-capable, fail-closed exclusive (`isConcurrencySafe` must
  return exact `true`; only 8 tools opt in — `glob`/`grep` notably do not), cap 10,
  live-editable as a user setting; results always commit in model order; cancelled
  calls get synthetic `ABORTED_BEFORE_DISPATCH` results so replay stays valid.
- **Subagents**: deliberately thin schema (description/prompt/background only — no
  model, tools, or type choice for the model); six providers — in-process spawn/fork
  plus **real Codex (`app-server --stdio`), the official Claude Agent SDK, ACP, and a
  second dsh over stdio**. The `standard` preset carries `subagent_codex` and
  `subagent_claude_code` rows shipped `disabled: true`.
- **Hooks**: lifecycle hooks are just plugins on the typed events — and dsh ships
  bridges that run **unmodified Claude Code `hooks.json` and Codex hook configs**
  (`packages/hooks/hooks-{claude-code,codex}`), mapping `PreToolUse`→`tools/pre-execute`
  `deny/ask`, `Stop`→`agent/turn-stopping` steering, with durable
  `hook/invoked`/`hook/result` audit events. Bridges are in no shipped bundle.
- **`evals: false` is a verified absence with an interesting shape**: BENCHMARK.md is
  3 lines addressed to *external* benchmark drivers; the rigor budget went entirely to
  determinism (transcript replay, failure-injection LLM server, 100% coverage), none
  to capability scoring.

## Context assembly — cache discipline as architecture *(deep-dive 2026-08-24)*

- **The `PromptSection` / `PromptContext` split.** The system prompt is a composed,
  ordered registry (28 section call sites; assembly re-runs every step); *changing*
  facts are deliberately registered as `PromptContext` and land as **user-role messages
  after retained history** — documented at the registration sites as a cache decision
  (`user-approval/src/index.ts:201-203`: switching policy "does not rewrite the stable
  system-prompt cache prefix"). Runtime-context snapshots re-emit **only when changed**
  (`agent-loop/src/runtime-context.ts:64-75`).
- **Compaction is engineered to hit the warm cache.** Default-on LLM summarization
  (threshold 0.8 × contextWindow, plus overflow-retry) whose auxiliary call replays the
  conversation's own system prompt, tools, and message prefix and appends only the
  directive — *"a genuine prefix of the last routed request, so the provider's KV cache
  is reused instead of invalidated"* (`compaction-basic/src/summarizer.ts:24-30`). Two
  further reducers: a model-free tool-result pruner and an execution-time spill stage
  (oversized results → session artifact + head/tail preview; `read` excluded to avoid a
  re-read loop).
- **The discipline is CI-enforced prose**: every package README must carry a
  `#### KV Cache effect` section (append-only / prefix-stable / replacing / independent,
  with exact invalidation conditions), gated by
  `scripts/verify-package-readme-model-experience.ts:17`. 30+ packages carry it (RE-COUNTED 2026-09-24: **223** at the pin, 305 at 477b4f4205 — `git grep -l '#### KV Cache effect' <rev> -- packages/ | grep -cE '^packages/[^/]+/[^/]+/README\.md$'`; "30+" was true and an order of magnitude shy). This is
  a *process* control on context assembly — no other tracked harness has one.
- **Rules files with versioned reconciliation.** Candidates `AGENTS.md`/`CLAUDE.md`
  (+`.local`, + user-global `~/.dsh/AGENTS.md`), `.git`-rooted walk, injected as a
  `<system-reminder>`-framed user message under a 64 KiB budget with a deterministic
  degradation sequence (binary-search truncation; omissions stated to the model with
  byte counts). Touched files are tracked by `FsVersion`: the model is told *"This file
  changed after it was loaded. Use the following content instead"* / *"Instructions
  removed: … no longer apply."* (`agent-instructions/src/render.ts:171-184`).
- **No per-model prompts** — one interpolated persona string (`{{model}}`, `{{cwd}}`);
  greps for model-family branching in prompt code come back empty. The exact opposite
  of opencode's nine bespoke prompts, on the same edge.
- **Skills**: SKILL.md convention (two shapes), six watched roots with rank precedence
  (`.dsh/skills`, `.agents/skills`, custom, `~/.dsh/skills`, `~/.agents/skills`,
  bundled), catalog injected as a digest-gated user message, bodies pulled via a
  `skill` tool or a `/name` gesture. dsh dogfoods it (`.agents/skills/` in-repo).
- **Session log as epistemics**: "Model-visible ⟺ logged" is an enforced invariant
  (every frozen request reconstructable from the append-only log; a runtime invariant
  checks it), and every prompt/tool-schema change lands as a durable `request/header`
  event with reason `initial|resume|change` — prompt drift and cache invalidation are
  *auditable from the session log alone*. For anyone studying harnesses, this is the
  most instrumentable loop in the tracked set.

## Permission model — a sandbox, not a prompt *(deep-dive 2026-08-24)*

**dsh has no per-tool permission system.** The `tools/pre-execute` waterfall's terminal
default is `allow` (`core/tools/src/index.ts:1477`); the only `ask`/`deny` producers in
the whole repo are the (unmounted) Claude Code/Codex hook bridges. In a stock run,
`bash`, `write`, `web_fetch`, and `subagent` dispatch **unprompted**. The gate is a
**compiled OS sandbox invoked per tool call**: modes `read-only` /
`workspace-write` (default) / `danger-full-access`, enforced by argv-wrapping at spawn
(bwrap → Landlock on Linux, Seatbelt on macOS, a hand-built restricted-token runner on
Windows that self-reports `partial` and says exactly why) plus an in-process path fence
for the fs tools derived from the same allow-list. Fail-closed: no usable backend →
refuse to run unconfined (`sandbox/src/index.ts:131-144`). **File effects are the whole
policy vocabulary — network is never confined**, stated in the README's limitations.

- **The escalation is inverted relative to every tracked harness**: the *model* raises
  the prompt. On a sandbox denial, `bash`/`write`/`edit` expose `sandbox_permissions` +
  `justification` for a one-shot same-turn retry, and the tool description instructs
  the model that detouring through chat is wrong — "the approval prompt raised by that
  retry is how the user consents" (`tool-bash/src/index.ts:82-92`). Fail-closed chain:
  strict-widening check against per-call truth before anyone is prompted; missing
  approver/agent/answerer, rogue returns, and throws all resolve to denial
  (`sandbox/src/escalation.ts:157-189`).
- **`allowed-once` is the only grant in the vocabulary** — no allow-always, no
  persistent grant ledger anywhere; every ask/decision pair is a durable
  `approval/asked`/`approval/decided` event. No other tracked harness ships without
  remembered approvals.
- **Boundary test (can the model influence the gate?): mechanically no, in the default
  composition.** No risk field, no auto-approve heuristic, no model-callable path to
  the mode/policy setters, no permission field on delegation (a written design note
  says so). The Warp-style `is_risky:false` analogue does not exist. *Rhetorically
  yes*: the model-authored `justification` reaches the human verbatim inside the
  approval reason. *Architecturally yes, through two shipped, labelled doors*: Code
  Mode runs model TypeScript in a worker thread with full Node globals — "containment,
  not a security boundary", strictly more privileged than the Landlock-confined `bash`
  beside it — and the shipped `cordis` preset lets the model define and mount
  host-plane plugins whose host half activates **with no approval request**
  (`cordis-host-runner/src/index.ts:266-272`; the preset's own header: "Treat a session
  on this preset as shell access").
- **The gate survives process boundaries asymmetrically, by design.** The *sandbox*
  survives completely (Landlock rulesets + `no_new_privs` inherit across `execve`;
  bwrap namespaces; the token binds the tree) — the Warp child-harness crack does not
  reproduce here. The *approval* gate tightens at the in-process agent boundary:
  delegated children inherit only the parent's explicit sandbox override and are
  **pinned to `approval: 'never'`** — a decision reversing an earlier shipped design
  after observing invisible blocked children, recorded as a dated in-repo design note
  (`.agents/notes/implemented/feature/2026-08-10-subagent-approval-pinned-never.md` — path CORRECTED 2026-09-24; the deep-dive wrote `.agents/tools/…`, which exists at neither pin) —
  the publish-your-own-negative-results epistemics this repo credits. At *foreign*
  harness boundaries the parent fixes the child's native permission mode as deployment
  config (codex default `never`, claude-code default `dontAsk`), with no model-visible
  field to change it. Escapes: MCP server processes spawn outside `ctx.sandbox`; the
  two model-code doors above.
- Small novel invariant: a live persistent PTY **freezes the sandbox mode** — a
  mid-session re-scope under an open shell throws (`terminal-bash/src/index.ts:47-52`).

## Environment relationship & surfaces

**Primary verb: `internalize`** — confinement is a hard dependency of the shipped
composition, mounted by default in both profiles, invoked per tool call at the argv
boundary (Codex-shaped, plus the in-process fs fence Codex lacks). **With a mild
`bundle` streak**: the Landlock launcher is *published as its own npm product family*
(`@deepseek-ai/node-addon-landlock-run` + per-platform binaries) with a CLI contract
document and release pipeline — nobody else in the set ships their sandbox as a
separately versioned product. **`bind` available, not default**: the `e2b` POC packages
swap `ctx.fs`/`ctx.subprocess` for E2B adapters (local confinement off — the VM is the
boundary); four out-of-process subagent backends attach foreign harnesses. **`inhabit`
absent** (no container self-detection anywhere; greps empty).

Surfaces: **web only** (locally served; browser is a pure client over 52 POST methods
+ two downlink-only WebSockets; model keys never reach the browser) and headless/SDK
embedding (TypeScript and Python SDKs spawn a *local* child process). **No TUI.**
Execution is 100% `local`: `--host 0.0.0.0` is a hard usage error — *"it would expose
remote code execution to the network"* (`web-app/src/startup.ts:74-76`) — and the local
server has **no inbound authentication** (TRUE AT THE PIN, FALSE ONE DAY LATER — 3e24087bfa, 2026-08-25, "authenticate the browser Host API": a signed host-bound cookie, `packages/client/connection/src/browser-auth.ts`; § Drift check 1), saying so twice in source (a DNS-rebinding
fence "explicitly not authentication"; privileged methods loopback-pinned with a
documented gap for `session.create`).

Credentials: BYO `DEEPSEEK_API_KEY` (env > `~/.dsh/.credentials.yaml` chmod-600-refused
otherwise > `.env`); no keychain, no vendor account login mounted. **An anonymous
random UUID rides every DeepSeek model request** as `x-deepseek-harness-user-id`
(`llm-deepseek/src/adapter.ts:519-530`) — genuinely random, never machine-derived, but
**independent of the telemetry switch** (OTel is mounted-but-disabled by default,
separately killable).

## Run probe — 2026-08-24

Probe target: the published npm artifact `@deepseek-ai/dsh@0.1.1-rc.2` — the version
string exactly matches the pinned tag, so probing the release probes the pin. Node
v22.23.2 (engines: `^22.19.0 || >=24`); success read from the served page, not exit
status (5e).

**Result: boots and serves.** `node_modules/.bin/dsh web --no-open` printed
`dsh web: http://127.0.0.1:3080` within 45 s of launch; `curl` returned HTTP 200 with
14,556 bytes of the web client's HTML (`<!doctype html>…__ModuleLoader__` bootstrap).
Loopback binding confirmed as read (`ss`: `127.0.0.1:3080`, not `0.0.0.0`).

**The install itself was the probe's finding.** The documented `npx` launch path
**OOM'd on this 8 GB host**: `npm exec` died in V8
(`FatalProcessOutOfMemory` during dependency resolution, ~2.4 GB VSZ at death) before
dsh ever ran, and a raised-heap plain `npm install` then needed **>10 minutes** to
finish (completed on a resumed run; `NODE_OPTIONS=--max-old-space-size=5120`). Final
footprint: 296 MB across 187 top-level `node_modules` entries — the entry package is
120 KB; the closure is where the cost lives. So the one-line install pitch
(`npx @deepseek-ai/dsh web`) carries an undocumented resource floor that a default
npm heap on a mid-size VPS does not clear. Dated 2026-08-24; worth re-probing at the
next drift check — a preview-stage packaging behavior, likely to change.

## Bleed

- **category 1↔2 consolidation**: DeepSeek joins Anthropic/OpenAI/Google/xAI in
  shipping a first-party harness; defaults are DeepSeek-wired everywhere
  (`agent-default-model` → `deepseek-v4-flash`, web search via DeepSeek API) while the
  seam stays genuinely provider-agnostic (three wire protocols, honest exclusions for
  auth shapes the config can't express).
- **Absorption, sideways and inward** (conclusion 8's territory): dsh *consumes
  competitors' extension surfaces* — unmodified Claude Code `hooks.json` and Codex hook
  configs run against dsh's typed events — and *delegates to competitor harnesses* as
  subagent providers (Codex, Claude Agent SDK). Warp orchestrates rivals as backends;
  dsh does both directions cheaper, as bridges.
- **Memory (category 5)**: verified **no native learning loop and no store** — the
  vendor's stance is third-party MCP memory examples, default-off ("no memory server is
  present in the shipped composition"). The memos-on-dsh adapter the memos deep-dive
  verified rides the plugin/pre-step surface. A vendor-native harness *declining* the
  memory absorption is a data point against treating conclusion 8's memory leg as
  universal gravity.
- **category 3**: the internalize + published-launcher combination above.

## Surprises

1. "Everything is a plugin" survives adversarial reading — with the singleton-factory
   and policy-kernel qualifications recorded above.
2. Turn-end gating where **data decides, not listener order** — a third engine-grade
   shape after hermes' policy and codex's stop-hooks.
3. A harness with **no per-tool permission model at all** — the gate is the sandbox;
   the honest comparator is Codex, not Claude Code. And the escalation prompt is
   *model-initiated by instruction*.
4. KV-cache discipline as a **CI-gated documentation requirement** across 30+ packages (223 at the pin, re-counted 2026-09-24).
5. It runs **competitors' hook configs** and spawns **competitors as subagents**.
6. No iteration budget anywhere, deliberately — with a real depth-cap bypass via
   `workflow`/`ralph` (`host.ts:352`).
7. `first_commit` 2026-06-10 vs published 2026-08-13: two months of private history
   released at once; the "five-day" phenomenon is adoption, not development.
8. The anonymous-UUID request header outside the telemetry opt-out.
9. A dated, in-repo **negative result about their own design** (subagent approvals
   pinned `never` after invisible-blocked-children), plus frozen "Agent Notes" as
   decision records — a vendor running the same epistemics this repo does.

## Open questions

- Does the plugin-first bet survive contact with an ecosystem? (Cordis plugin authoring
  is the contested surface; the `dsh plugin add` path and the dormant hook bridges are
  where third-party supply would land. Re-check at the next drift check.)
- The convergence prediction from the roster registration stands: multi-surface
  expansion (TUI/IDE) from the current single web surface — `execution: local` +
  no-inbound-auth make a hosted/async-remote shape a large step. Falsifiable by ~2027-01.
  **Scored 2026-09-24 (§ Drift check 13): the falsifiable core resolved TRUE seven days
  after the read — `apps/desktop` (Electron, first commit 19444907f0, 2026-08-31) — while
  the named form (TUI/IDE) and the named blockers (local + no-auth) both resolved false:
  inbound auth shipped the next day and vendor-account login packages followed. The
  forecast priced the expansion by its architectural blockers; upstream removed them.**
- Does Code Mode actually get used by the default model tier (ADR-0012's open ptc
  question), given it ships behind a preset?
