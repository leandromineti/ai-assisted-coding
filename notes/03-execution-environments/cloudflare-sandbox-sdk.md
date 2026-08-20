---
name: cloudflare-sandbox-sdk
category: 3
vendor: Cloudflare, Inc.
url: https://github.com/cloudflare/sandbox-sdk
license: Apache-2.0   # root LICENSE file at the pin states Apache-2.0; gh api repos/cloudflare/sandbox-sdk reports license.spdx_id NOASSERTION — the repo's own LICENSE file is authoritative, not the API label (see What it is)
open_source: true
stack: [TypeScript, Cloudflare Workers]   # turbo monorepo; ts(447) is the dominant extension count per repo-facts.sh
version: "@cloudflare/sandbox@0.12.7-2-g6abf639"
commit: 6abf639   # this is what build-tool-index --check validates
# SECOND PIN, prose-recorded (a report carries one machine-checked commit): artifact-fs,
# Cloudflare's separate filesystem-sync primitive, lives at cloudflare/artifact-fs @ 2b87a48
# (read 2026-08-20), cited only if the SDK's own filesystem story leads there (D-14, e2b.md's
# two-pin idiom). Re-check drift with: repo-facts.sh artifact-fs
first_commit: 2025-06-22
stars: 1108
stars_at: 2026-08-20
read_at: 2026-08-20
depth: deep-dive   # category 3's third deep-dive; three-tract source read (D-15), load-bearing claims spot-verified at the pin by the main session before writing (08-01-PLAN.md Task 2)
environment_features:   # ADR-0017 block, set 2026-08-20 from the deep-dive read at 6abf639 (and artifact-fs @ 2b87a48 for filesystem_sync) — Task 3 gate outcome: no lattice extension needed (see 08-01-SUMMARY.md); Dynamic Workers is a sibling platform binding with zero SDK surface and gets no cell (D-01's two-instance bar unmet by one sighting)
  isolation_primitive: hardware-virt (testimony)   # bare family — vendor states "its own VM" three times, no hypervisor/VMM named anywhere reachable (COV-01; What it is / Isolation mechanism); @cloudflare/containers pinned but not vendored in this clone
  egress_default: open (testimony)   # SDK assigns no default (enableInternet read-only in packages/sandbox/src, zero assignments — sandbox.ts:242,7807,7882); base-class default per vendor docs, retrieved 2026-08-20 (Blast radius)
  egress_controls: allow-biased (testimony)   # deniedHosts unused anywhere in the SDK (zero hits); the exercised pattern — allowedHosts overriding enableInternet:false, examples/claude-code/src/index.ts:5-12 — mirrors e2b's allow-biased finding; platform evaluation order stated only in vendor docs, retrieved 2026-08-20 (Blast radius)
  credential_model: plain-env-var (source)   # default path: setEnvVars -> real OS env vars via shell export, packages/sandbox-container/src/services/session-manager.ts:1128-1130 (Credential exposure); broker-relayed Worker-side injection is a verified opt-in alternative, not the default — examples/claude-code/src/index.ts:56-63
  snapshot_model: explicit-backup:squashfs-r2-overlay (source)   # opt-in createBackup()/restoreBackup(), mksquashfs on create + squashfuse/fuse-overlayfs on restore, R2-backed; restore is explicitly ephemeral, sandbox.ts:7274-7275 (Fidelity / snapshot_model cell assessment); NOT create-is-resume — every sandbox starts from the bare image (docs/ARCHITECTURE.md:153-155)
  self_host: partial   # container half genuinely portable (docs/STANDALONE_BINARY.md); control half is a Durable Object, no infra repo, no self-host/on-prem path anywhere in the clone (Self-hosting reality & the open-core seam)
  warm_pool: true   # SDK-shipped WarmPool Durable Object, packages/sandbox/src/bridge/warm-pool.ts:1-9; user-space, bridge-only (core Sandbox DO has zero references), default off (warmTarget: 0, warm-pool.ts:85) — contrast e2b's platform-level verified false (Surprises)
  filesystem_sync: clone   # git.checkout() shells `git clone --filter=blob:none` into /workspace/<repo> by default, packages/sandbox-container/src/managers/git-manager.ts:45-49 — structurally identical to e2b's clone evidence; upload (bridge hydrate endpoint) and mount (backup restore only) also exist in source but clone is the SDK's own first-class, working-anchor-scoped API (What it is / filesystem_sync cell assessment)
# environments: / environment_relation: DELIBERATELY UNSET. Those keys describe how a
# *harness* relates to an environment; the Cloudflare Sandbox SDK *is* the environment —
# same reasoning as e2b.md. It has no relation-to-an-environment of its own, so it does not
# appear in comparisons/environments.md. That absence is correct, not a gap.
---

# Cloudflare Sandbox SDK

The third category-3 deep-dive, and the first read against a **split-openness** subject: the
client-and-container half is open (`cloudflare/sandbox-sdk`), the substrate that actually
enforces isolation is not readable from any artifact this repo can reach — a stronger closure
than Modal's, whose leaky proto at least named a runtime string. Read via a three-tract split
(sandbox lifecycle/isolation; egress/credentials; filesystem/snapshot), each tract's load-bearing
claims spot-verified at the pin below before being written here. `[✓]` marks a claim
independently re-derived by this session's own `git grep`/`git show`, not merely reported by a
tract.

## What it is

A TypeScript SDK, `@cloudflare/sandbox` (`packages/sandbox/`), that wraps Cloudflare's Container
product behind a Durable Object: `Sandbox` is a Durable Object class that **extends `Container`
from `@cloudflare/containers`** `[✓]` (`packages/sandbox/src/sandbox.ts:1011`, confirmed
`extends Container<Env>`) — every lifecycle method the SDK exposes is an override of a
dependency it does not vendor. There is no `POST /sandboxes` and no create call: a sandbox is
name-addressed — `getContainer(ns, id)` `[✓]` (`sandbox.ts:780`) resolves a Durable Object stub
by name, and the container starts lazily on first use. This is a structurally different shape
from both prior category-3 reads: E2B's sandbox-ID *is* the microVM, Modal's task *is* the
serverless invocation; here the sandbox's logical identity (`sandbox-lifetime.ts:3-9`,
"changes only when the sandbox is explicitly destroyed") outlives any one running container
generation beneath it.

Root `LICENSE` at the pin states **Apache-2.0**; `gh api repos/cloudflare/sandbox-sdk` reports
`license.spdx_id: NOASSERTION` — the repo's own file is authoritative, and Apache-2.0 is what is
recorded in frontmatter. Two open-source repos feed this read (D-14's two-pin idiom):

- **`cloudflare/sandbox-sdk`** (`6abf639`) — the SDK, the in-container agent
  (`packages/sandbox-container/`), and ~30 example integrations (`examples/`, `bridge/`,
  `devin/`). This is the primary, machine-checked pin.
- **`cloudflare/artifact-fs`** (`2b87a48`) — a separate, Cloudflare-authored Go FUSE daemon that
  lazily mounts git repositories; cited below only where the SDK's own filesystem story leads
  there (D-14) — which turns out to be nowhere in the SDK's own dependency graph (Absence A4,
  tract 3), only in a demo the artifact-fs repo ships *about* this SDK.

**The isolation boundary itself is outside both clones.** The SDK's own architecture skill states
this in the first person: *"Container isolation — handled at the Cloudflare platform level (VMs),
not by SDK code"* `[✓]` (`.agents/skills/architecture/SKILL.md:122`). A repo-wide anchored sweep
for every named isolation substrate this repo has previously found elsewhere — `firecracker`,
`gvisor`, `runsc`, `microvm`, `seccomp`, `runc`/`crun`/`containerd` — returns **zero real hits**
`[✓]` (re-run at the pin; the unanchored form of `runsc` false-positives on `BrowserRunScreenshot`
in a generated `.d.ts` file, confirming the anchoring caveat tract 1 flagged). E2B at least had a
second, readable infra repo; Modal's client at least leaked a runtime string on the wire. Here,
nothing readable names a mechanism at all — this is the more extreme case E4's own falsification
clause anticipated by name.

## The distinguishing bet

**That isolation is someone else's problem, and the SDK should spend its entire security budget
on the one boundary it can see: its own control channel.** The container-side security service
states its philosophy outright — `packages/sandbox-container/src/security/security-service.ts:3-10`
`[✓]`:

```
// **Security Model**: Trust container isolation, only protect SDK control plane
//
// Philosophy:
// - Container isolation handles system-level security
// - Users have full control over their sandbox (it's the value proposition!)
// - Only protect port 3000 (SDK control plane) from interference
// - Format validation only (null bytes, length limits)
// - No content restrictions (no path blocking, no command blocking, no URL allowlists)
```

Reinforced per-method: *"No command blocking (users can run bash, sudo, rm -rf - it's their
sandbox!)"* (`:135`); *"No directory traversal blocking (container isolation handles this)"*
(`:23`). The SDK performs **zero** in-guest restriction by design, and the shipped image
confirms it is not compensating elsewhere: of 24 `Dockerfile*` in the clone, exactly **one**
carries a `USER` directive `[✓]` (`bridge/worker/Dockerfile:49`) — the canonical shipped image
(`packages/sandbox/Dockerfile`) runs as root. A kernel-level isolation control the project once
shipped — PID-namespace isolation, guarding the control plane's own processes from sandboxed
code — is now dead code the public type still advertises: `packages/sandbox-container/src/session.ts:158`
`[✓]` (`/** Legacy isolation flag (ignored - kept for compatibility) */`) against
`packages/shared/src/types.ts:445` `[✓]` (`/** Enable PID namespace isolation (requires
CAP_SYS_ADMIN) */`), with `unshare`/`CLONE_NEWPID`/`setns` returning zero hits anywhere in
`packages/`. A caller reading the type signature will believe they are enabling a security
control the container silently discards.

## Isolation mechanism — what can and cannot be traced

Traced against the container and the Durable Object; the substrate below both is testimony-only.

1. **A session is a bash process, not an isolation boundary — sessions share filesystem and
   process space by design.** `tests/e2e/session-state-isolation-workflow.test.ts:26` `[✓]`:
   *"Sessions provide isolated shell state (env, cwd, functions) but share file system and
   process space - that's by design!"* One shared PID 1 across all sessions:
   `docs/SESSION_EXECUTION_DEEP_DIVE.md:86` describes orphaned children surviving a session
   kill, and `:563` states the fix (`setsid` + process-group signaling) is **not**
   implemented. Combined with the dead PID-namespace flag above, the blast radius of any code
   executed in a sandbox is the entire container: every session's files, every session's
   processes, and the control plane on port 3000 — protected by nothing but a port-number
   check (`packages/sandbox/src/security.ts:29-46`, enforced at `sandbox.ts:1002-1004`).
2. **The Durable Object does not serialize concurrent traffic into one container.**
   `docs/CONCURRENCY.md:111-118`: *"Multiple `exec()` calls can be 'in flight' simultaneously
   at the DO level"*; the repo's own test suite deliberately shares one container across its
   suite for speed (`CONTRIBUTING.md:169`). One-sandbox-per-tenant is advisory, not enforced.
3. **The strongest in-repo substrate claim is "VM," asserted three times, never mechanised.**
   `docs/ARCHITECTURE.md:149`: *"VM-based isolation: Each sandbox runs in its own VM."* A code
   comment at `sandbox.ts:1108-1110` references "launch VM" in a timeout-tuning context, and one
   peripheral example (`devin/wrangler.jsonc:4-5`) calls it "an isolated Linux VM." All three are
   assertions about a dependency the clone does not contain — `@cloudflare/containers@0.3.5` is
   pinned in `package.json` but not vendored, and the blobless clone has no `node_modules`. The
   repo is not even internally consistent about the word: `packages/sandbox/README.md:175` says
   *"its own container"* against `ARCHITECTURE.md:149`'s *"its own VM."*
4. **Vendor documentation settles the family, not the mechanism (TESTIMONY, `retrieved:
   2026-08-20`).** `https://developers.cloudflare.com/containers/platform-details/architecture/`:
   *"Each container instance runs inside its own VM, which provides strong isolation from other
   workloads running on Cloudflare's network."* The family is named — hardware virtualization —
   but no specific hypervisor, VMM, or kernel is ever stated, on this page or any page either
   session-reading agent reached. This is the shape ADR-0017 calls a legal **bare-family** value:
   the shape is known, the specific half is not, and coining one (`firecracker`, `cloud-hypervisor`,
   anything) would be inventing evidence no source or vendor statement supports.

## COV-01 — the isolation-primitive-per-tier question

**The SDK exposes exactly one sandbox tier, and it is the container tier traced above.** The
per-tier mapping this requirement asks for resolves to a single row: the container tier's family
is `hardware-virt`, known only from vendor testimony (§ above), with the specific mechanism
**not stated anywhere reachable from this pin** — not source, not docs. This is not the
undecidable-mapping case D-10 anticipated (multiple tiers, ambiguous per-tier assignment); it is
a single tier whose family is known and whose specific mechanism is simply unpublished. The
honest cell is a bare family value graded testimony, exactly Modal's `checkpoint-restore (bare
family)` precedent.

### Dynamic Workers — the isolate sibling, and why it does not get a cell

Dynamic Workers is a **separate Cloudflare platform binding**, not an SDK tier, and it is recorded
here rather than as a second report per COV-01's explicit instruction. Evidence for both halves of
that claim:

- **Zero SDK surface.** `worker_loaders`/`WorkerLoader`/"Dynamic Worker" return zero hits
  anywhere in `packages/` `[✓]` (re-verified). The construct appears in exactly one example,
  declared as a platform binding in `wrangler.jsonc` (`examples/typescript-validator/wrangler.jsonc:32-36`,
  `worker_loaders: [{ binding: "LOADER" }]`) and invoked via `this.env.LOADER.get(...)`
  (`examples/typescript-validator/worker/compiler.ts:176-180`) — never through any `Sandbox`
  method. The application composes the two tiers itself, in sequence (build in the container,
  execute in the isolate): `compiler.ts:134` creates a `Sandbox`, `:169` destroys it, `:176`
  reaches for the isolate — three independent statements, not one API.
- **The vendor's own framing contrasts it against a hardware VM (TESTIMONY,
  `https://blog.cloudflare.com/dynamic-workers/`, `retrieved: 2026-08-20`):** *"An isolate is an
  instance of the V8 JavaScript execution engine, the same engine used by Google Chrome... Hardening
  an isolate-based sandbox is tricky, as it is a more complicated attack surface than hardware
  virtual machines."* And, sharpest of all for blast radius: *"One-off Dynamic Workers usually run
  on the same machine — the same thread, even — as the Worker that created them."*

**Why this does not trigger a lattice extension.** ADR-0017's `isolation_primitive` cell on this
report describes the SDK's own tier — the thing `cloudflare-sandbox-sdk` actually implements and
that a caller of this SDK gets. Dynamic Workers is a sibling platform capability the SDK neither
wraps, calls, nor exposes; an application can compose the two, but the composition lives in
application code, outside the SDK boundary this report classifies. A V8-isolate *is* a real gap in
ADR-0017's closed family — it is genuinely none of `hardware-virt`, `userspace-kernel`,
`shared-kernel`, or `os-native` (no syscall interception, no kernel-level namespacing, no
Seatbelt/Landlock analogue; memory-safety enforced by a language runtime inside a shared OS
process) — but D-01's admission bar needs **two independent verified instances**, and this is one
sighting of a construct this SDK does not itself implement. The gap is recorded here, dated, as a
named future re-entry candidate rather than acted on. See the Task 3 gate outcome in the plan
SUMMARY for the explicit no-extension verdict this reasoning produced.

## The five category-3 axes

**Blast radius.** Egress is **open by default** — the SDK never assigns `enableInternet`; the
three occurrences in `packages/sandbox/src` are a type declaration and two reads
(`sandbox.ts:242,7807,7882`) `[✓]`, and the SDK's own test asserts the forwarded value is
`undefined` when unset (`packages/sandbox/tests/r2-egress-mount.test.ts:1055-1058`). The base
class's default is TESTIMONY only (`@cloudflare/containers` is not vendored in this clone):
*"By default, a Sandbox allows internet access"* (`developers.cloudflare.com/sandbox/guides/outbound-traffic/`,
`retrieved: 2026-08-20`). `deniedHosts`, the deny-list primitive vendor docs describe as
evaluated first, is **never used anywhere in this repo** `[✓]` (zero hits, re-verified). The
control surface that exists is `allowedHosts` (a deny-by-default allowlist once set) plus a pair
of user-authored proxy handlers — `outboundByHost` (per-host) and `outbound` (catch-all) — that
run **inside the Worker isolate** and return a `Response`; this is a proxy running in the
application, not a packet filter. One example demonstrates the same allow-overrides-default shape E2B's read
found: `examples/claude-code/src/index.ts:5-12` sets `enableInternet = false` *and*
`allowedHosts = ['github.com', 'api.anthropic.com']`, with the code comment stating
`allowedHosts` gates the outbound path *even when* internet is globally off. Two of the SDK's own
five example subclasses (`authentication`, `opencode`) leave egress completely unrestricted while
still doing credential injection — egress restriction and credential injection are orthogonal
opt-ins, and the shipped examples ship both postures. In-container the story is total openness by
design (§ distinguishing bet): no path blocking, no command blocking, no URL allowlists, DNS left
unrestricted by the SDK's own admission (`examples/codex-app-server/README.md:147`).

**Fidelity.** State is explicitly ephemeral — `docs/ARCHITECTURE.md:153-155` `[✓]`: *"Sandbox
lifecycle: Starting → Running → Sleeping (state lost) → Destroyed... files and processes exist
only while the container is active."* The working anchor is `/workspace`, a plain `mkdir`'d
directory in the image with no volume backing it `[✓]` (`packages/sandbox-container/src/config.ts:53`,
`DEFAULT_CWD = '/workspace'`); sessions fall back to `$HOME` only if that path is missing. Fidelity
is engineered back in three ways, each with a fidelity seam of its own: (1) an opt-in
squashfs-over-R2 backup/restore, whose restore is explicitly **ephemeral** — it re-mounts a view
that evaporates at the next sleep, not a persistent extraction `[✓]` (`sandbox.ts:7274-7275`,
*"This is an ephemeral restore, not a persistent extraction"*, independently corroborated by
current vendor docs); (2) `git.checkout()`, which shells `git clone --filter=blob:none` into
`/workspace/<repo>` by default; (3) local development, which runs a genuine Docker container but
an emulated control plane — restore silently switches mechanism from a FUSE overlay mount in
production to a plain `unsquashfs` extraction locally (`packages/shared/src/types.ts:1178-1183`),
and a dedicated error-hint exists purely because that mismatch once looked like nothing at all
(`sandbox.ts:6415-6422`). The Alpine/musl image variant cannot snapshot at all — `squashfs-tools`,
`squashfuse`, and `fuse-overlayfs` are installed only on the default Ubuntu target
(`packages/sandbox/Dockerfile:151-163` vs `:308`), a capability gap with no type-level signal.

**Parallelism.** The Durable Object does not serialize requests into one container (§ isolation,
above) — concurrent `exec()` calls to the same sandbox name execute concurrently, by platform
design. Account ceilings are the only hard numbers in-repo: 400 GiB concurrent memory, 100
concurrent vCPU (`docs/ERROR_HANDLING.md:160-161`); everything else — placement, per-account
container caps — is deferred to vendor documentation the SDK does not surface
(`docs/ARCHITECTURE.md:157`).

**Startup cost.** The SDK's own defaults reveal it does not trust the base class's numbers:
`instanceGetTimeoutMS` is tripled to 30s from an `@cloudflare/containers` default of 8s
("too short for cold starts"), and `portReadyTimeoutMS` to 90s from 20s
(`sandbox.ts:1103-1118`). A dedicated fail-fast RPC path uses an 8s timeout for a different
purpose (`RPC_START_INSTANCE_GET_TIMEOUT_MS`, `:418`). Idle sleep defaults to 10 minutes, set in
SDK code and fully overridable/suppressible (`sandbox.ts:1013`, `1531-1535`, `3606-3616`). Two
independent warm-pool constructs exist and neither is a platform default (see `warm_pool`
below and the E4 subsection).

**Credential exposure.** The default path is the weak one: `setEnvVars` writes secrets as real OS
environment variables inside the container via a literal shell `export` `[✓]`
(`packages/sandbox-container/src/services/session-manager.ts:1128-1130`), readable by any process
via `env` or `/proc/self/environ`. A stronger, opt-in primitive exists — Worker-side credential
injection, where the container receives a sentinel string (`'proxy-injected'`) and the real value
is attached to outbound requests inside the Worker isolate
(`examples/claude-code/src/index.ts:56-63,21-26`; 8 files carry the `proxy-injected` sentinel, all
under `examples/`). **The verified property is that the container cannot *read* the secret, not
that it cannot *use* it** — the outbound handler forwards the injected header to any path/method
on the allowed host with no restriction (`examples/codex-app-server/src/index.ts:46-53`), a
confused-deputy surface the repo's own test only checks from the read side
(`test-egress.mjs:143-149`). Bucket mounts have three distinct credential postures funnelling
through one writer (`sandbox.ts:2626-2637`, `createPasswordFile`): the **default** mode (no
`credentialProxy`) writes a real, long-lived `bucket:accessKeyId:secretAccessKey` file into the
container filesystem; `credentialProxy: true` substitutes a dummy pair with Worker-side re-signing;
the R2-binding egress path is fully credential-less. "The container never sees credentials" is
true for two of three shipped modes and false for the default one. `CLOUDFLARE_API_TOKEN` stays
Worker-side for the tunnels subsystem, but one core-SDK path (the opencode integration,
`packages/sandbox/src/opencode/opencode.ts:224-226`) writes it into the container when a developer
opts in — the unqualified claim "never" is false for that one path.

## Self-hosting reality & the open-core seam

**Partial**, structurally similar to E2B for a different reason: the container half is genuinely
portable — a plain `linux/amd64` OCI image running a self-contained supervisor binary, explicitly
designed to drop into *any* Docker image (`docs/STANDALONE_BINARY.md`) — but the control half is
not. `Sandbox` is a Durable Object; there is no self-hostable control plane in the repo
(`packages/sandbox-container/src/control-plane/README.md:1-8` names the boundary, not an
alternative to it), no infra repo, and no on-prem/air-gap path anywhere in the clone (zero hits
for `self_host`/`selfhost`/`on-prem`/`air-gap`). Local development is a real substrate, not a
simulator — `npm run dev` boots an actual Docker container — but a degraded one: no FUSE, no
presigned URLs, miniflare-emulated R2, and the restore mechanism itself changes shape (§
fidelity). This matters for `self_host` scoring the same way E2B's Terraform-only self-host did:
real, but partial, and the partiality is visible as dead seams rather than asserted in prose.

## Bleed

- **← category 2 (harnesses).** The example tree ships first-party adapters for four harnesses —
  `examples/claude-code/`, `examples/codex/`, `examples/codex-app-server/`, `examples/opencode/`,
  plus `packages/sandbox/src/opencode/` and `packages/sandbox/src/openai/` living in core SDK
  source, not merely `examples/`. An environment shipping adapters for four harnesses is the
  counterpart, from the environment side, to hermes-agent's eight swappable backends.
- **A second, unrelated snapshot construct sits one directory over.** `devin/` implements its own
  tar+zstd whole-workspace checkpoint to R2, explicitly stating it *"does not require the Sandbox
  SDK package at runtime"* (`devin/README.md:3-5`) — a different model (whole-rootfs, persistent
  across restart) from the SDK's own per-directory squashfs overlay (ephemeral). The two must not
  be conflated when reading this report's `snapshot_model` cell.
- **A Cloudflare "Artifacts" git-hosting binding** appears as a first-class `wrangler.jsonc`
  binding type (`examples/git-repo-per-sandbox/wrangler.jsonc:10-15`) — a managed git remote the
  sandbox can push to directly. This is a *different* Cloudflare product from `artifact-fs` (the
  Go FUSE driver), though the two belong to the same product family: Artifacts is the
  git-speaking service, artifact-fs is its optional client-side mount driver
  (`upstream/artifact-fs` `README.md:18-19`).
- **artifact-fs's relationship to this SDK runs one way, and thin.** The SDK has zero references
  to artifact-fs anywhere in its clone; artifact-fs's own example tree carries a `devDependency`
  on `@cloudflare/sandbox` to demonstrate mounting a git repository at
  `/workspace/mnt/<repo>` — an optional add-on demonstrated on top of the SDK, not a dependency
  of it, and pinned to an older SDK version (`0.12.5`) than this read's pin (`0.12.7`). Read
  cross-tract: the artifact-fs example needs `/dev/fuse` and declares no explicit capability
  request in its `wrangler.jsonc`, which — combined with this SDK's own production restore
  depending on `squashfuse`/`fuse-overlayfs` inside the container and a passing e2e suite that
  exercises it — is the strongest available evidence that Cloudflare Containers grant usable FUSE
  without an operator-visible flag (inference, not a source statement).

## Surprises

1. **The platform declares container-snapshot primitives the SDK never calls.** The generated
   Workers runtime types vendor `snapshotContainer()`, `snapshotDirectory()`, and a
   `containerSnapshot`/`directorySnapshots` boot option on the `Container` interface
   (`examples/authentication/worker-configuration.d.ts:3270-3313`) — a create-is-resume-shaped
   primitive at the platform. The SDK calls neither, anywhere `[✓]` (zero hits across
   `packages/*/src`, `bridge/worker/src`, `devin/src`, `examples/*/src`; the identifiers exist
   only in eight generated `.d.ts` files). Either the platform capability postdates the SDK's
   own backup feature or it is gated/unreleased — the source does not say which. The SDK's
   squashfs-over-R2 mechanism reads as a user-space re-implementation of something the substrate
   may already offer natively.
2. **Two independent warm-pool constructs exist, and the platform apparently offers neither.**
   `packages/sandbox/src/bridge/warm-pool.ts` ships a `WarmPool` Durable Object, explicitly
   adapted from a third-party community project (`:1-9`, crediting
   `github.com/mikenomitch/cf-container-warm-pool`), keeping N pre-started containers on
   standby — default **off** (`warmTarget: 0`) and bridge-only: the core `Sandbox` Durable
   Object has zero references to it `[✓]` (`grep -c 'WarmPool\|warmPool' packages/sandbox/src/sandbox.ts`
   → 0). This is the sharpest contrast with E2B, where the absence of a warm pool was a platform
   design decision visible in infra source; here, a *user* of the platform had to build one in
   application code, complete with a comment admitting it "auto-learns" the platform's real
   concurrency ceiling reactively from errors (`warm-pool.ts:26-31`) — evidence of a ceiling the
   client cannot see, encoded as scar tissue rather than as a documented number.
3. **The security model is stated as a philosophy, not merely practiced.** Most tools performing
   zero in-guest restriction do so by omission; this one states it as the value proposition in a
   module-header comment (§ distinguishing bet). It is the most explicit first-person E1 argument
   this repo's category-3 reads have found.
4. **Two credential models ship side by side with opposite defaults.** The bucket-mount default
   writes real long-lived keys into the container filesystem; the R2-binding egress path is fully
   credential-less by construction. Neither is universal, and the marketing-shaped claim
   ("the container never sees credentials") is true for exactly two of three shipped modes.

## Open questions

- Does the platform's declared-but-unused `snapshotContainer()`/`snapshotDirectory()` capability
  ship before the next drift check, and would it change the `snapshot_model` cell if the SDK
  started calling it? Flagged as the most likely near-term change to this report.
- Is the container's FUSE grant (inferred cross-tract from the artifact-fs example plus this
  SDK's own restore path) ever stated by the vendor directly, rather than inferred from two
  independent pieces of behavior? Not settled at this pin.
- Does `interceptHttps` actually default to `true` at the base-class version this SDK pins
  (`@cloudflare/containers@0.3.5`), or only in whatever version current vendor docs describe? The
  SDK's own source reads the field (`sandbox.ts:1471`, `[✓]` — a correction to an earlier tract
  draft that reported zero reads in `packages/sandbox/src`; there is one, though still no
  assignment) but never declares or defaults it, and the base class is not vendored in this
  clone. Unsettled — flag any future claim about this default as testimony until the base class
  can be read directly.

## What was not verified

- **Nothing was executed.** No sandbox created, no container started; every claim above is static
  source inference at the pins, or dated vendor testimony where labelled.
- **`@cloudflare/containers@0.3.5` — the one dependency that could name the isolation
  substrate — is pinned but not vendored in either blobless clone.** This is the load-bearing
  absence of this whole read: the isolation mechanism is not merely undisclosed by the vendor, it
  is architecturally outside the boundary a source read of this repo can ever cross.
- The evaluation order between `deniedHosts`, `allowedHosts`, and the per-instance/class outbound
  handlers is vendor documentation only (`egress_controls` axis) — `deniedHosts` itself is unused
  anywhere in this SDK, so the documented precedence is a platform fact this SDK's own surface
  never exercises.
- Whether the FUSE grant inferred in Bleed above is a stable platform guarantee or an
  observation specific to this pin's image build is not something a source read alone can settle.

## Confronting design-principles.md (E1-E4)

- **E1 — CONFIRMS**, and unusually explicitly. *"Blast radius sets the autonomy ceiling — buy
  autonomy with isolation, not model quality."* The security-service module header states this as
  a first-person design philosophy (§ distinguishing bet): zero in-guest restriction, the entire
  security budget spent on a boundary the SDK cannot itself inspect. The backup/restore feature
  is marketed by the vendor in exactly E1's terms — `examples/time-machine/README.md:3-5`, "run
  dangerous commands without fear," with an explicit agent use-case: "Checkpoint before AI makes
  changes, restore if wrong." The twist this read adds: the ceiling here is set by a boundary the
  tool cannot see (`@cloudflare/containers` unvendored) — autonomy bought on credit, from a vendor,
  sight unseen.
- **E2 — CONFIRMS**, and is the sharpest fit of the four here. *"Isolation without fidelity
  produces category-2-looking failures — engineer the fidelity back explicitly."* Production
  restore is a FUSE overlay mount; local restore silently becomes an `unsquashfs` extraction —
  same API, different persistence semantics, and a dedicated in-source error hint exists solely
  because a presigned-URL-vs-miniflare mismatch once looked like nothing at all
  (`sandbox.ts:6415-6422`). A `localBucket` flag exists purely to paper over this fidelity gap
  (`packages/shared/src/types.ts:1178-1183`), and the musl image variant drops the entire snapshot
  toolchain with no type-level signal (`Dockerfile:151-163` vs `:308`) — a second, independent
  fidelity seam in the same subsystem.
- **E3 — not applicable, and correctly so**, matching both prior category-3 reports. Cloudflare
  *is* the environment; it does not relate to one. `environments:`/`environment_relation:` stay
  DELIBERATELY UNSET.
- **E4 — CONFIRMS, and this read is E4's own named falsification test.** E4's clause states: *"if
  a closed environment read (Modal/Daytona/Cloudflare) yields only testimony, E4 is real but
  legible only when the environment is open."* Every one of E4's E2B-shaped facts — kernel-tuning
  choices, scheduler internals, page-fault strategy, working-set computation — is structurally
  unreachable here; the isolation mechanism itself is not vendored, let alone its internals.
  **One genuine refinement, flagged rather than acted on:** the platform's economics still leak,
  just sideways rather than downward — into user-space compensating machinery a closed substrate
  forces the SDK's own authors to write. The warm pool's comment admitting it "auto-learns" the
  real concurrency ceiling reactively from platform errors (`warm-pool.ts:26-31`) is a scheduler
  fact made legible not by reading the environment's source, but by reading the scar tissue in
  client code that had to probe for it blind. This is a candidate amendment to E4's stated form —
  a second, weaker legibility channel alongside "the environment is open" — and is recorded here
  as a flag for a future explicit revision decision (methodology rule 5), not applied to
  `design-principles.md` in this plan (plan 08-04 collects the three verdicts).

## `workload_identity` re-entry check (D-11)

**Not met.** The one candidate in the clone that superficially resembles federation —
`examples/s3-mount`'s AWS credential broker — is a confirmed D-11 false friend on inspection:

- The AWS call is `Action: 'AssumeRole'` `[✓]` (`examples/s3-mount/src/credentials.ts:68`), not
  `AssumeRoleWithWebIdentity` (zero hits anywhere in the clone).
- The trust anchor is a **long-lived static IAM secret** (`BROKER_AWS_ACCESS_KEY_ID`/`SECRET`),
  not an identity token — the example's own README calls it out: *"This is the only long-lived
  secret in the system; its access key goes into the Worker"* (`README.md:127`).
- No OIDC issuance for the sandboxed workload exists anywhere: zero hits for `federat`, `spiffe`,
  `jwks`, `audience`, `idToken`, `IRSA`, `iam.gserviceaccount`. The two `id_token` hits in the
  entire clone are a fabricated placeholder JWT used to satisfy a client-side mode check
  (`examples/codex/src/index.ts:80,85`), not an issued or verified token.
- `CLOUDFLARE_API_TOKEN` — the one real Cloudflare-facing token this SDK handles — is exactly the
  D-11 archetype: it authenticates the Worker to **Cloudflare's own** control plane to provision
  tunnels, is not held by the sandboxed process (with one core-SDK exception, the opencode
  integration, which is developer opt-in), and per D-11 must not be counted as workload identity
  federation to a third party.

A sandbox holds no cryptographic identity of its own — it is addressed by a `sandboxId` string
that is explicitly non-secret (embedded lowercase in preview hostnames). Any credential a sandbox
can use was placed there, or is injected on its behalf, by the Worker. Per D-11 this evidence
stays in this prose; no registry key is touched. **A GitHub issue should be opened noting this
condition remains unmet at this pin** (recorded in the plan SUMMARY, not the registry).
</content>
