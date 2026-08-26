---
name: daytona
category: 3
maker: Daytona Platforms, Inc.
url: https://github.com/daytonaio/daytona
license: AGPL-3.0   # the repository's own LICENSE file at the freeze pin (4ee2c6365, 2026-06-19); the GitHub API reports no SPDX license for the repository today (checked 2026-08-21) — the before/after split shows up in this field first
open_source: false   # describes the product's state TODAY: public and AGPL-3.0-licensed at the freeze pin (source, 4ee2c6365, 2026-06-19); GitHub API reports no SPDX license for the repository today (checked 2026-08-21) — treated as closed for this report, which is the closure event this study is built around
stack: [TypeScript, Go, Python]   # apps/api is TS; apps/cli + apps/daemon are Go; broad Python surface too — see repo-facts.sh extensions (ts:1385, go:820, py:808, java:733, rb:386, tsx:362)
version: v0.189.0-9-g4ee2c6365
commit: 4ee2c6365   # the FREEZE PIN, derived via: git -C upstream/daytona rev-list -1 --before=2026-06-23 origin/main — NOT the branch tip. Cross-checked against planning's 2026-08-20 GitHub API observation (4ee2c6365) — match, no discrepancy. The clone is checked out --detach at this SHA and must stay there for build-tool-index.py --check to stay green; do not fast-forward it via sync-upstream.sh.
closed_source_pin_note: pre-closure pin   # 2026-08-21, CR-01 fix: `open_source: false` above describes the product's state TODAY, not an absence of pinnable source — this field tells build-tool-index.py to render `commit` (as "4ee2c6365 (pre-closure pin)") in comparisons/tools.md's Version read column instead of the generic `closed source` literal used for genuinely unpinnable proprietary products. Opt-in and Daytona-specific by design; do not copy onto modal.md or pilot-shell.md without the same "closure event" narrative reason
first_commit: 2024-02-06
stars: 71943
stars_at: 2026-08-21   # TODAY, post-closure — describes the repository now, not at the freeze pin. `commit:` above describes the freeze pin; `stars`/`stars_at` describe the repository today. Two different dates on one frontmatter block, which is the whole shape of this report.
read_at: 2026-08-21
depth: deep-dive   # SPLIT DEPTH DECLARATION (D-06), written 2026-08-21 BEFORE any finding is read: frozen-source claims are earned against the pinned source (4ee2c6365, 2026-06-19) and capped there — SOURCE grade, never higher. Every current-state claim is capped at TESTIMONY via the documentation route, each carrying its own retrieved: date, describing a product roughly two months past the freeze pin. Two ceilings, one per side, declared up front — neither side may borrow the other's grade.
environment_features:   # ADR-0017 block, set 2026-08-21, hybrid-sourced per key (D-07). Mechanism
  # keys (isolation_primitive, credential_model, snapshot_model, filesystem_sync) are set from the
  # frozen source at the freeze pin (4ee2c6365, 2026-06-19) and SOURCE-graded, each with a dated
  # post-closure caveat where current documentation indicates the mechanism changed. Cloud-policy
  # keys (egress_default, egress_controls, self_host, warm_pool) are set from current documentation
  # as TESTIMONY, retrieved 2026-08-21. See the report's "Cell-sourcing" evidence in each finding
  # section and the per-axis legibility table for the frozen/current split behind every value here.
  isolation_primitive: shared-kernel:docker-container (source)   # Docker Engine API container, Privileged: true by default (container_configs.go:205); CONTAINER_RUNTIME has no code default, sysbox-runc named only in frozen in-repo docs (runners.mdx:888), zero Go/TS hits; no userns config anywhere (daytona.md, "Isolation boundary"). POST-CLOSURE CAVEAT (2026-08-21): today's docs add VM/Windows classes with their own kernel, already declared as enum values at the pin (sandbox-class.enum.ts:7,10) and unimplemented in the open runner — read as a seam closing, not a new mechanism; the shared-kernel container class itself is unnamed in current docs (no runtime/hypervisor named on /docs/isolation), corroborated only by a surviving pre-closure CVE advisory naming "the Sysbox runtime boundary"
  egress_default: tier-gated (testimony)   # retrieved 2026-08-21, https://www.daytona.io/docs/en/network-limits/ — Tier 1-2 restricted and non-overridable at the sandbox, Tier 3-4 open by default, essential-services allowlist at every tier. NOT a post-closure artifact: the same tier structure is already in the frozen in-repo docs (network-limits.mdx:12,14, verified at 4ee2c6365) — continuous across closure. The entity/runner default at the pin is unconditioned open (networkBlockAll = false, sandbox.entity.ts:129, source); a self-hoster with no tier sees that value as the whole truth
  egress_controls: deny-wins (testimony)   # retrieved 2026-08-21 — organization-level network restrictions override sandbox-level settings even when a sandbox specifies its own allow list (/docs/en/network-limits/). Frozen-source mechanism agrees: blockAll evaluated first, wins over any allow list (network.go:36-40, source) — inverse of E2B's allow-biased. Shape lost in a bare enum value: sandbox-level params (networkAllowList/domainAllowList/networkBlockAll) are mutually exclusive, HTTP 400 on conflict, and networkBlockAll clears rather than stacking on top of the allow lists; domainAllowList is post-pin (0 hits at 4ee2c6365)
  credential_model: plain-env-var (source)   # third-party credentials reach the sandbox as plain Docker env vars end to end (container_configs.go:65-89,171); zero hits for dtn_secret/secretRef/SecretsManager/vault at the pin; guest toolbox API has no auth middleware (server.go, verified). POST-CLOSURE CAVEAT (2026-08-21): current documentation describes a materially different, newer model — placeholder substitution (dtn_secret_<random>) at an outbound proxy with response scrubbing (/docs/secrets, testimony) — that did not exist in any form at the pin (no secrets.mdx in the frozen docs set); the plain-env route this cell describes is dated to the freeze pin, not current-state
  snapshot_model: explicit-backup:container-commit (source)   # a "backup" is docker commit with Pause: false (container_commit.go:24) then a registry push — filesystem only, no quiescing; CRIU absent tree-wide. POST-CLOSURE CAVEAT (2026-08-21): pause/resume and hot (filesystem+memory) snapshots are documented today (/docs/persistence, /docs/snapshots, testimony), scoped to the VM/Windows classes exactly as the frozen API's own gate scoped them (includeMemory "only supported for Windows sandboxes", sandbox.service.ts:1317) — read as the declared-but-unimplemented pause seam (sandbox.go:106, "pause is not supported for sandbox type") closing, not new capability from nothing
  self_host: partial (testimony)   # retrieved 2026-08-21, https://www.daytona.io/docs/bring-your-own-compute — customer-operated runner nodes only, "while using Daytona's control plane"; Elastic License 2.0 Helm charts, sales-gated; /docs/installation/ 404s. Same label as the frozen-source read (also partial, at the pin: everything open, pause + Windows-class features declared-but-unimplemented) but for a different reason — historically the missing pieces were features on an open stack; today the control plane itself is structurally reserved. The open/closed seam moved from the code to the commercial contract, it did not close
  warm_pool: true (testimony)   # retrieved 2026-08-21, https://www.daytona.io/docs/en/warm-pools/ — documented first-class feature, gated ("must be enabled for your organization. Contact support@daytona.io"), claim-matched on snapshot/region/resources/OS-user with no custom env vars/volumes/secrets. Source-corroborated at the pin (SOURCE, not this cell's grade per D-07): a real DB entity, 10s reconciliation cron, mechanism is a database ownership transfer of an already-STARTED container under a sentinel zero-UUID org with createdAt rewritten on assignment (sandbox.constants.ts:6, sandbox-warm-pool.service.ts:133) — the docs disclose the claim predicate exactly, not the tenancy mechanism
  filesystem_sync:   # source, at the freeze pin (4ee2c6365) — a conjunction: all three primitives are independently first-class, not an either/or
    - upload (source)   # toolbox HTTP filesystem API, SDK-primary and README-first
    - clone (source)   # git clone executed inside the sandbox by the daemon itself, via go-git, never a shell-out (daemon/pkg/git/clone.go)
    - mount (source)   # S3 buckets FUSE-mounted on the runner HOST with --allow-other --file-mode 0666 --dir-mode 0777, using the platform's own AWS credentials, then bind-mounted in (volumes_mountpaths.go:229,249) — POST-CLOSURE CAVEAT (2026-08-21): current docs describe only "S3-compatible object storage" (/docs/en/volumes/, testimony); the host-FUSE mechanism and its permissive modes are undocumented today, the mount capability itself is not gone
# environments: / environment_relation: DELIBERATELY UNSET — same as e2b.md and modal.md.
# Daytona IS the environment, not a harness that relates to one, so it does not appear in
# comparisons/environments.md.
---

# Daytona

The fifth category-3 report (2026-08-21 correction, WR-03 — cloudflare-sandbox-sdk and
microsandbox both predate this read and are also category-3 reports), and the first structured
as a before/after study across a vendor's own closure event — a different kind of read than
E2B or Modal, the category's two prior closed/open-comparison studies: not a single
snapshot of one product, but the same product read twice across a real closure event. On
2026-06-11 Daytona announced its production codebase was moving private, citing security —
"AI can now be pointed at an open source repository and systematically search it for
exploitable flaws" — while committing to keep the pre-closure repository public. The last
commit before that boundary is `4ee2c6365` (2026-06-19); two same-day commits titled
"daytona maintenance notice" land on 2026-06-23. This report reads both sides: the frozen
source at the mechanically derived pin, and the current product through the documentation
route two months later, `retrieved: 2026-08-21`. The question issue #11 filed after the Modal
and Cloudflare Sandbox SDK reads was whether the category survives a **maximally** closed
subject. Daytona is not that subject — see the closing verdict — but holding one product on
both sides of its own closure produced a sharper result than a single closed read could.

## Read from two instruments — three, once the frozen docs are counted separately

Two ceilings, declared before either side was read (D-06): frozen-source claims are earned
against the pinned source (`4ee2c6365`, 2026-06-19) and capped at **SOURCE**; every
current-state claim is capped at **TESTIMONY**, dated `retrieved: 2026-08-21`, from the
documentation route. Neither side borrows the other's grade.

- **Frozen source** — `4ee2c6365`, the Go/TypeScript/Python implementation at
  `apps/runner`, `apps/daemon`, `apps/api`. **SOURCE**, file:line, verified at the pin.
- **Frozen docs** — `apps/docs/src/content/docs/en/**/*.mdx`, a documentation site **checked
  into the frozen repo itself**. This is a third instrument, distinct from both the code and
  today's vendor docs: it is **TESTIMONY**, not SOURCE — a docs page asserting a mechanism is
  never proof the mechanism exists — but it is dated and versioned exactly like the code
  beside it, which is what makes it useful: it lets this report ask whether a docs claim and a
  code fact *agreed at the pin*, something neither E2B's nor Modal's single-sided reads could
  ask. Cited as **[frozen docs]**.
- **Current documentation** — `daytona.io/docs`, the trust center, and vendor advisories,
  `retrieved: 2026-08-21`. **TESTIMONY**, exactly as `modal.md` treats Modal's blog: dated,
  vendor's word, uncheckable against code that no longer exists in this study's reach.

Every load-bearing frozen-source claim below was spot-verified at the pin by this session,
independent of the tract drafts that first surfaced it, and is flagged **[✓]** with the exact
`git grep` that produced it.

## What it is

A sandbox product for AI-generated code, sold on both sides of the closure event as "full
composable computers for AI agents." At the pin, a Daytona sandbox is a **Docker container**
created and driven entirely through the Docker Engine API — `ContainerCreate`, `ContainerStart`,
`ContainerCommit`, `ContainerStop` — with the container named for the sandbox ID
(`apps/runner/pkg/docker/create.go`, `container_configs.go:168`). Today's documentation
describes four sandbox classes — Container (default), Linux VM, Windows, GPU — where the frozen
API already declared `linux-vm` and `windows` as class enum values
(`apps/api/src/sandbox/enums/sandbox-class.enum.ts:7,10` **[✓]**
`git -C upstream/daytona grep -n "LINUX_VM\|WINDOWS" 4ee2c6365 -- apps/api/src/sandbox/enums/sandbox-class.enum.ts`)
with no runner implementation behind either at the pin. That single fact governs how this
report reads most of the frozen/current deltas below: several look like new capability but are
better read as **a declared seam closing**, not a new product (see "The two-months caveat").

## Isolation boundary

**At the pin.** Non-GPU sandboxes are created `Privileged: true` **[✓]**
(`git -C upstream/daytona grep -n "Privileged: gpuIndex == nil" 4ee2c6365 -- apps/runner` →
`apps/runner/pkg/docker/container_configs.go:205`), with the product's own comment stating the
reasoning: *"Non-GPU sandboxes still need privileged for their current workloads."* Privileged
is the default; GPU sandboxes are the exception that opts *out*. `CONTAINER_RUNTIME`, the knob
that would swap in a non-default runtime, is declared with **no code default** — unlike its
neighbour on the very next config line — so unset means the Docker daemon's stock runtime
**[✓]** (`git -C upstream/daytona grep -n "CONTAINER_RUNTIME" 4ee2c6365` → exactly two hits,
`apps/runner/cmd/runner/config/config.go:33` with no `default:` tag, and
`apps/docs/src/content/docs/en/runners.mdx:888` **[frozen docs]**, which is the *only* place
`sysbox-runc` is named as the intended value). `sysbox` occurs in exactly 4 lines across 3
files at the pin, **zero of them Go or TypeScript**. `userns`/`user_namespace`/`remap-user`
match zero files tree-wide.

Meanwhile the frozen docs assert a boundary the frozen code does not implement:
`security-exhibit.mdx:98` **[frozen docs]** — *"Daytona uses Sysbox as its container runtime to
provide VM-level isolation without hardware virtualization overhead"* — and `:101` — *"Sysbox
enforces Linux user-namespaces on all sandboxes, ensuring that the root user inside a sandbox
maps to a fully unprivileged user on the host."* Both claims are testimony even at the pin
(they are docs, not code), but they are testimony the pin's own code contradicts on both counts:
no code default selects `sysbox-runc`, and no user-namespace configuration exists anywhere in
the tree. This is the read's discriminator finding, and it survives closure in an unusual
shape (see "Isolation boundary" in the per-axis table below).

The runner itself is Docker-in-Docker, running its own daemon
(`apps/runner/Dockerfile:66`, `FROM docker:28.5.2-dind-alpine3.22`), and the shipped self-host
compose runs both the runner and the API `privileged: true`. No hardware virtualization
exists anywhere in the isolation path at the pin: `firecracker`, `kata`, `gvisor`, and
whole-word `runsc` each match zero files; the only `/dev/kvm` mount in the tree is an
Android-emulator workload capability behind a default-`false` flag, not a sandbox boundary.

**Today.** [`/docs/isolation`](https://www.daytona.io/docs/isolation) `retrieved: 2026-08-21`
describes the Container class as *"Isolated container with dedicated namespaces and enforced
resource limits. Code runs as root inside the sandbox without affecting the runner"* and a
separate VM class as *"Full virtual machine with its own kernel."* No hypervisor, runtime, or
runtime name appears anywhere on that page — not gVisor, Firecracker, KVM, QEMU, runc, or
Kata. The Sysbox name is not gone from the public record, but it no longer lives in the docs:
it survives only in a still-live pre-closure incident advisory,
[`security-update-cve-2026-31431-copy-fail`](https://www.daytona.io/dotfiles/updates/security-update-cve-2026-31431-copy-fail)
(dated **2026-04-30**, before closure, still reachable today) — *"The Sysbox runtime boundary
itself was not breached in our testing"* — and the trust center it points readers toward,
[`trust.daytona.io`](https://trust.daytona.io/) `retrieved: 2026-08-21`, which repeats the
phrase but lists no "Security Exhibit" document. `/docs/en/sandboxes/` also states each sandbox
gets *"a dedicated kernel"*, which contradicts `/docs/isolation`'s own container-vs-VM split —
a live, uncorrected internal contradiction in today's docs, both pages `retrieved: 2026-08-21`.

## Credentials

**At the pin.** Third-party credentials reach the sandbox as plain Docker environment
variables — no broker, no proxy substitution **[✓]**
(`git -C upstream/daytona grep -n "envVars = append" 4ee2c6365 -- apps/runner/pkg/docker/container_configs.go`
resolves the loop at `container_configs.go:65-89` feeding straight into `container.Config{Env:
envVars}`). `dtn_secret`, `secretRef`, `SecretsManager`, and `vault` all match zero hits over
`apps/api/src`, `apps/runner`, and the whole Go tree. The sandbox's own auth token is POSTed
into the guest over plain HTTP (`apps/runner/pkg/docker/daemon.go:152`,
`http://%s:2280/init`), and inside the guest that token authenticates nothing — its only other
read is a telemetry header (`apps/daemon/pkg/toolbox/telemetry.go:46`). The guest toolbox API
itself has **no authentication middleware at all** and binds every interface on port 2280
**[✓]** — verified directly at the pin: the router's full middleware stack is
`Recovery()`, an otel wrapper, `sloggin`, and an error handler
(`git -C upstream/daytona show 4ee2c6365:apps/daemon/pkg/toolbox/server.go` lines ~136-158) —
no auth check anywhere in it. The only "Bearer" hits in the daemon are generated Swagger
documentation strings, not wired middleware. Registered on that unauthenticated router:
`/process/execute`, `/process/code-run`, PTY connect, the full `/files` group including upload
and delete, and `/git/clone` / `/git/push`. Auth exists only upstream, as one static shared
token per runner — not per-sandbox, not per-tenant — so anyone holding a runner's token drives
every sandbox on it. The one careful exception is git credential handling, guest-side: a
`GIT_ASKPASS` shim, a stripped credential helper, and hooks disabled, specifically to stop a
hostile cloned repo's hooks from exfiltrating the git token — a defended threat model that sits
beside every other secret being handed over in the clear.

**Today.** [`/docs/secrets`](https://www.daytona.io/docs/secrets) `retrieved: 2026-08-21`
documents a different model entirely: *"Secrets are organization-scoped, encrypted credentials
that Daytona injects into a sandbox's outbound HTTPS traffic without ever placing the plaintext
inside the sandbox."* The mechanism is placeholder substitution at an outbound proxy — a
secret becomes an opaque `dtn_secret_<random>` token inside the sandbox, and *"an outbound
proxy replaces the placeholder with the real value before the request reaches its destination,
and only when the request goes to a host you have allowed"* — with response scrubbing if a
secret value ever comes back in an upstream reply. This is genuinely new: `dtn_secret` and
`secrets.mdx` do not exist anywhere at the pin. **This is the read's sharpest falsification of
"closure means uniform darkening."** Today's docs are *more* mechanism-rich on credentials than
the frozen source ever was — but every finding about the *old* env-var route's danger (the
cleartext token POST, the toolbox API's total absence of auth, the single shared runner token)
has no surface anywhere in today's corpus, at any depth. That is not new-model-replaces-old —
the plain-env route is still how a sandbox's ordinary `env` map works today (a warm-pool claim
still fails when the request carries custom env vars, per `/docs/warm-pools`) — it is that the
old route's specific dangers went dark exactly when the new route's design got a page.

## Pause, resume, and snapshots

**At the pin.** A "backup" is a Docker commit with `Pause: false` **[✓]**
(`git -C upstream/daytona grep -n "Pause:     false" 4ee2c6365` →
`apps/runner/pkg/docker/container_commit.go:24`) followed by a registry push — the filesystem
is captured while the sandbox's own processes keep running, with no torn-write guarantee.
`criu` matches zero files tree-wide; there is no memory capture anywhere in the open runner.
Pause is the sharpest structural seam in the whole read: it is declared end-to-end — a public
REST operation, an SDK method, an interface contract, a job type, three DB states, billing
constants that treat `PAUSING`/`RESUMING` as compute-consuming — and **unconditionally errors**
at the one place that would execute it **[✓]**
(`git -C upstream/daytona grep -n "pause is not supported" 4ee2c6365` → exactly one hit,
`apps/runner/pkg/runner/v2/executor/sandbox.go:106`,
`return nil, fmt.Errorf("pause is not supported for sandbox type")`). This is the same shape as
E2B's `GetTransform()`-with-zero-consumers seam: a fully wired public surface with a stub
underneath. A related seam: `includeMemory` is gated to Windows sandboxes at the API boundary and
never reaches `apps/runner` or `apps/daemon` — it does reach the runner's own generated wire
contract (`libs/runner-proto/proto/runner/v1alpha1/job.proto`), which strengthens rather than
weakens the finding: the parameter is in the contract and unimplemented behind it.

**Today.** [`/docs/persistence`](https://www.daytona.io/docs/persistence)
`retrieved: 2026-08-21` documents pause/resume as a working feature, scoped to the VM class —
*"Pausing freezes the VM with filesystem and memory intact; resuming continues all processes
from the point they were frozen"* — with a 60-minute auto-pause default.
[`/docs/snapshots`](https://www.daytona.io/docs/snapshots) documents hot snapshots via
`includeMemory` for the VM and Windows classes, matching the frozen gate's class scoping
exactly. Read together with the enum evidence above, this is very likely the declared seam
closing, not disclosure loss — see the two-months table. What is unambiguously gone is the
seam itself (the exact string, the seven wired-but-stubbed pieces of it) and the fact that a
"backup" never quiesced the container it committed.

## Working anchor

All three primitives — `upload`, `clone`, `mount` — are first-class at the pin, which the
`mount | clone | upload` vocabulary does not force a single choice among: `upload` is the SDK's
primary, README-first filesystem route through the toolbox HTTP API; `clone` is a git clone
executed *inside* the sandbox by the daemon itself, via go-git, never a shell-out; `mount` is
an S3 bucket FUSE-mounted on the **runner host** with `--allow-other --file-mode 0666
--dir-mode 0777`, using the **platform's own** AWS credentials rather than the tenant's, then
bind-mounted into the container and re-established on every start. The daemon binary itself is
bind-mounted read-only from the host into every sandbox and made the container entrypoint — the
guest agent is injected at run time, the opposite of E2B's build-time-baked `envd`.

Today's docs recover `upload` (single/bulk/streaming) and `clone` unusually well —
[`/docs/git-operations`](https://www.daytona.io/docs/git-operations) states clone happens
*"through the Daytona API, allowing direct repository management without installing Git
clients or executing shell commands inside the sandbox,"* which describes the frozen
implementation's distinguishing property precisely. `mount` survives only as "S3-compatible
object storage"
([`/docs/en/volumes/`](https://www.daytona.io/docs/en/volumes/) `retrieved: 2026-08-21`) — the
host-level FUSE mechanism, its permissive modes, and whose credentials perform it are
unrecoverable at any depth.

## Warm pools — the clean inversion of E2B

**At the pin.** E2B's entire design bet is that there is no warm pool — every "create" is a
snapshot resume. Daytona's frozen source shows the opposite bet, fully built: a first-class
warm-pool DB entity, a 10-second reconciliation cron, and a candidate cap defaulting to 300
**[✓]** (`git -C upstream/daytona grep -n "SANDBOX_WARM_POOL_UNASSIGNED_ORGANIZATION" 4ee2c6365`
→ `apps/api/src/sandbox/constants/sandbox.constants.ts:6`, consumed at
`apps/api/src/sandbox/services/sandbox-warm-pool.service.ts:133`). The mechanism is a database
ownership transfer of an **already-running container**: pool members are real sandboxes in
state `STARTED`, parked under a sentinel organization — the literal zero UUID — selected at
random under a lock, and a "create" that claims one simply rewrites the row, including
`createdAt: now`. Two consequences no create-path caller can see: a "new" sandbox may have run
for an arbitrary period before it was theirs, sharing a runner and kernel with whatever ran
before it; and `createdAt` is not the container's age, so any audit or billing timeline built on
it is wrong by construction. A sandbox's own custom `env` is part of the pool's exact-match
key, so a request carrying credentials structurally cannot claim a warm sandbox.

**Today.** Daytona is the first environment in this repo's category-3 reports to **document** a
warm pool as a product feature — [`/docs/warm-pools`](https://www.daytona.io/docs/warm-pools)
`retrieved: 2026-08-21`, a page with no counterpart at the pin. It states the config surface
(`snapshot`, `pool` size, `target` region) and, remarkably, the *exact claim predicate* the
frozen source enforces — no custom env vars, volumes, or secrets — more cheaply than the pin
required a source reader to derive it. It is explicitly gated: *"Warm pools must be enabled for
your organization. Contact support@daytona.io."* Gone entirely: the sentinel-org ownership
transfer, the `createdAt` rewrite, the reconciliation interval, and idle-pool billing, which no
page states. Reading E2B and Daytona side by side gives category 3's E4 principle a second,
independently-argued instance: both products face the identical pressure — make "create" cheap
— and resolve it with opposite mechanisms (snapshot-resume-plus-lazy-paging vs. a warm pool
whose "create" is a tenancy-record rewrite on a live container). See E1-E4 confrontation below.

## Network posture and blast radius

**At the pin.** The sandbox entity's own default is unconditioned open egress —
`networkBlockAll = false`, `networkAllowList` nullable — enforced by a per-sandbox `iptables`
chain of allow entries terminated by an unconditional deny, where **an explicit block always
wins over any allow list** **[✓]**
(`apps/runner/pkg/netrules/network.go:36-40`: `switch { case blockAll: … ; case hasAllowList:
… }`, deny evaluated first). That is the inverse of E2B, where an allow entry beats a deny.
Combined with the guest toolbox API's total absence of authentication, and inter-sandbox
networking defaulting to **on** in code **[✓]**
(`git -C upstream/daytona grep -rn "INTER_SANDBOX_NETWORK_ENABLED" 4ee2c6365` →
`apps/runner/cmd/runner/config/config.go:35`, `default:"true"`), the code-level default lets one
sandbox reach an unauthenticated `POST /process/execute` and a full read/write `/files` API on
a co-tenant sharing the same runner — stated as code-level inference, not demonstrated. A third
in-repo contradiction on this exact value: the frozen docs and the shipped compose both say
`INTER_SANDBOX_NETWORK_ENABLED` defaults to `false` **[frozen docs]**
(`apps/docs/src/content/docs/en/oss-deployment.mdx:283,285,505`, and
`docker/docker-compose.yaml:146`), while the Go code's own `default:"true"` disagrees — and the
docs page explicitly contemplates deploying runners **outside** the shipped compose, which is
exactly the case that would silently invert the documented posture.

**A finding this report can make only by reading both sides at once:** the frozen source is
*not* simply "open by default," and the frozen docs already carried the tier structure that
today governs cloud egress. `apps/docs/src/content/docs/en/network-limits.mdx:12,14` **[frozen
docs]**, verified at the pin, states organizations are tiered by verification and spend, that
Tier 1–2 network access "cannot be overridden at the sandbox level," and that "organization-level
network restrictions take precedence over sandbox-level settings" — the same policy today's
docs describe. Tract A's `open` reading and the current docs' `tier-gated` reading are not in
conflict: they read two different levels of one product at one moment. The **entity/runner**
default genuinely is unconditioned open egress; the **cloud control plane** genuinely overlays
an organization tier policy on top of it, and did so already at the pin. A self-hoster, who has
no tier, sees the entity default as the whole truth; a cloud customer sees the tier policy.

**Today.** [`/docs/en/network-limits/`](https://www.daytona.io/docs/en/network-limits/)
`retrieved: 2026-08-21`: Tier 1 (email-verified) and Tier 2 (card-linked, $25 top-up) get
"network access restricted and cannot be overridden at the sandbox level"; Tier 3 ($500
lifetime top-up) and Tier 4 ($2,000/30 days) get "full internet access... by default." An
essential-services allowlist — package registries, git hosts, cloud provider endpoints, and
model APIs — applies at every tier, so the "restricted" floor is not deny-all. At the
sandbox level, exactly three parameters exist (`networkAllowList`, `domainAllowList`,
`networkBlockAll`), at most one non-empty — a conflicting combination returns HTTP 400 rather
than resolving — and `networkBlockAll: true` clears the stored allow lists rather than layering
over them. Where a precedence rule does exist, it is organization-over-sandbox and it is
deny-wins: the organization's restriction applies "even with `networkAllowList` or
`domainAllowList` specified when creating a sandbox." No page states where enforcement runs, or
anything about inter-sandbox reachability. What survives from the frozen source's blast-radius
finding is the security-exhibit text still live today asserting "network segmentation
preventing lateral movement between sandboxes" — the opposite claim from the code default — but
about the cloud product, whose actual runner configuration is unknowable from either side of
this study; the shipped self-host compose, notably, sets the isolating value the code lacks.

## Self-hosting — the seam moved, not closed

**At the pin.** `LICENSE` is AGPL-3.0. The shipped `docker/docker-compose.yaml` is a complete,
vendor-SaaS-free stack — API, proxy, runner, SSH gateway, OIDC, Postgres, Redis, an internal
registry, object storage — and `oss-deployment.mdx` documents deploying it. Two capabilities
are declared in the open API and unimplemented in the open runner: pause/resume and memory
snapshots (the Windows sandbox class). On the same argument that gives E2B `partial`, this
report grades Daytona `partial` at the pin too — but for a materially different reason: E2B's
missing piece was security-critical (the credential-injecting proxy); Daytona's missing pieces
were feature surfaces on an otherwise complete, runnable stack.

**Today.** [`/docs/bring-your-own-compute`](https://www.daytona.io/docs/bring-your-own-compute)
`retrieved: 2026-08-21` grants customer-operated **runner nodes only** — "while using Daytona's
control plane to manage them" — via Elastic License 2.0 (source-available, not OSI-open) Helm
charts, sales-gated per the pricing page. `/docs/installation/` 404s; there is no documented
route to a self-hosted control plane. The only full-stack self-host route left is the frozen,
now-unmaintained repository this report's own pin sits inside.

Both eras land on the same `partial` label for opposite reasons, which makes the label a false
friend if read as continuity: at the pin, the whole stack was open and two *features* were
missing; today, the whole *control plane* is structurally reserved and the compute plane is
sales-gated. The open/closed seam did not disappear between the two reads — it moved from the
code (visible only to a source reader, at the pin) to the commercial contract (visible only to
a docs reader, today). One mechanical, dated fact from the pinned clone itself, stated without
inferring intent: `LICENSE` exists at the tip tree of `4ee2c6365` but is **absent** from
`origin/main`'s current tip, which holds three files total — while the GitHub README still
tells readers the repository remains usable "under the LICENSE." A second, independent
catchable discrepancy, on top of the isolation one above.

## The per-axis legibility table

This is the deliverable D-08 asks for: per mechanism axis, what the frozen source showed, what
today's documentation shows, and whether a docs-only reader in 2026-08 could still recover the
frozen finding. **RECOVERABLE** = the finding, or its essential shape, is still derivable from
current public documentation alone. **WEAKENED** = the shape survives, the load-bearing detail
does not. **GONE** = no trace in the current corpus at any depth. **INVERTED** = the current
claim reads as the frozen finding's opposite (recorded, not adjudicated, where the delta may be
genuine product change rather than disclosure loss — see the two-months note in each cell).

| Axis | Frozen-source finding (`4ee2c6365`, 2026-06-19) | Current-docs status (`retrieved: 2026-08-21`) | Legibility verdict |
|---|---|---|---|
| Isolation boundary | Docker container, `Privileged: true` by default; `CONTAINER_RUNTIME` has no code default; `sysbox`/`userns` are zero-hit in code | "Isolated container with dedicated namespaces"; no runtime, hypervisor, or userns named anywhere in the docs proper | **WEAKENED** — the family (shared-kernel container) survives; privileged-by-default and zero-userns-config do not. The runtime name survives only via a surviving pre-closure CVE advisory, not the docs |
| Pause/resume & snapshots | `docker commit` with `Pause: false`; no CRIU anywhere; pause fully wired end-to-end and unconditionally errors at the runner | Container = filesystem-only "cold snapshots"; VM/Windows support pause/resume and hot snapshots via `includeMemory`, matching the frozen API's declared-but-unimplemented gate | **RECOVERABLE (class split) / GONE (mechanism + seam)** — today's docs state the exact class boundary the frozen code enforced; the C/R mechanism and the declared-but-erroring seam are unrecoverable |
| Credentials | Plain env-var passthrough end to end; guest toolbox API has zero auth middleware; sandbox token shipped in cleartext and authenticates nothing | Placeholder substitution at an outbound proxy with response scrubbing; nothing anywhere about daemon auth, token delivery, or the toolbox API | **GONE** for the load-bearing findings — an entirely new, more mechanism-rich model is documented, but it is dated to today, not a recovery of the old one; the old model's specific dangers have no surface at any depth |
| Working anchor | All three of `upload`/`clone`/`mount` first-class; `mount` = host FUSE with `0666`/`0777` modes and platform AWS keys; daemon binary bind-mounted `:ro` from host | `upload` and `clone` fully documented, arguably better than the frozen prose; `mount` survives only as "S3-compatible object storage" | **WEAKENED** — `upload`/`clone` recoverable in full; the host-FUSE mechanism, its permissions, and the host-injected daemon binary are GONE |
| Warm pools | First-class DB entity; a "create" is an ownership transfer of an already-`STARTED` container under a sentinel zero-UUID org; `createdAt` rewritten on assignment | Existence, config surface, and the exact claim predicate (no custom env/volumes/secrets) are all documented; idle billing undisclosed | **WEAKENED** — the disclosed shape is unusually complete for a post-closure page; the sentinel-org ownership transfer and the `createdAt` rewrite are GONE |
| Network default & blast radius | Entity default open; `blockAll` wins over any allow list; inter-sandbox networking `default:"true"` in code, contradicting both the frozen docs and the shipped compose; unauthenticated toolbox API on a shared runner | Tier-gated default with an essential-services carve-out, deny-wins across organization/sandbox scope, mutually-exclusive sandbox params; nothing on enforcement location or cross-sandbox reachability | **RECOVERABLE (policy) / GONE (enforcement + cross-sandbox mechanism)** — and the policy is continuous across closure, already present in the frozen in-repo docs, not new |
| Self-hosting | Full stack open, AGPL-3.0, vendor-SaaS-free compose; `partial` only because pause and the Windows class were declared-but-unimplemented | `partial` again — but the control plane is now structurally reserved to Daytona; compute-plane charts are Elastic-licensed, sales-gated; `/docs/installation/` 404s | **Same label, opposite content** — an announced product change, not a disclosure loss; the open/closed seam moved from the code to the commercial contract |
| Blast radius (isolation claim vs. reality) | Docs assert Sysbox user-namespace isolation; code has zero userns configuration and defaults to privileged | Docs assert only "dedicated namespaces"; the Sysbox/userns claim survives, word for word, in a pre-closure advisory the docs no longer link from | **INVERTED (checkability)** — the claim itself is essentially unchanged; what changed is whether anyone can check it. At the pin this was refutable by one grep. Today the same claim is unfalsifiable |

## The two-months caveat

The frozen source is roughly two months older than the docs read. Several deltas above read as
disclosure loss but are better classified as **product change**, verifiable because the frozen
API already declared the class enums (`linux-vm`, `windows`) the open runner never implemented:
VM-class sandboxes existing today, pause/resume now working (scoped to VM, exactly the class the
frozen runner could not serve), hot snapshots via `includeMemory`, the placeholder-substitution
secrets model, and `domainAllowList` are all **plausible product change**, several of them
provably so. Two deltas run in the *unexpected* direction — **disclosure gain**, not loss: warm
pools existed at the pin with zero frozen-docs coverage and are documented in detail today; the
credentials page documents a materially richer model than existed in any form at the pin. One
delta is **continuity**, not a closure effect at all: the tier-gated network policy is already
present in the frozen in-repo docs, not a post-closure commercial artifact. What remains
**unambiguous disclosure loss** is a specific set: privileged-by-default, zero user-namespace
configuration, the unauthenticated guest toolbox API, the single static per-runner auth token,
the host-level world-writable FUSE volume mount using platform credentials, the `createdAt`
rewrite, and the DinD nesting — implementation facts about a running system that were never a
capability to add or remove, and the current documentation has no surface for any of them. The
honest headline is not "closure darkened the product." It is: **closure darkened the
implementation while the documented capability surface got richer.**

## Closing verdict — does the category survive a maximally closed subject?

**No, and this read cannot answer that question, because Daytona does not fill that slot.**
The category's refined law (this index, `checked: 2026-08-20`) predicts legibility from
client-contract richness plus vendor disclosure. Daytona scores **moderate on both**: a rich
client contract survives at `github.com/daytona` (multi-language SDKs, a documented REST API),
plus a public trust center, a public CVE advisory that names the isolation runtime, and — unlike
Modal or Cloudflare Sandbox SDK — a frozen-but-still-public source tree that answers real
questions about the product's implementation before closure. A maximally closed environment
would have none of that: a thin, uncommented client, no trust center, no advisories, no source
lineage at all. Daytona is not that environment, and issue #11's live question — whether the
category survives a subject with **no** disclosure surface at any depth — remains open.

What this read adds is sharper than a positive or negative on that question. **Closure does not
primarily remove facts; it removes the ability to convict a claim.** Counted directly from this
read: of the frozen source's plain capability-or-shape findings, most are recoverable or
weakened today, because vendors re-document capabilities as they ship them — that is the
warm-pool and credentials evidence above. But every frozen finding that was a **contradiction
between two instruments held at once** — docs asserting user-namespace isolation the code never
configured; the code's own inter-sandbox-networking default disagreeing with its own docs and
its own shipped compose; a public API declaring pause while the runner stubs it; docs claiming
"filesystem and memory" snapshots the runner could not produce; resource limits described as
enforced while the shipped compose disables them outright — has a **zero** survival rate.
Each one required the source and the docs simultaneously; closure removed the source, and the
half that is still public is unfalsifiable without it. The sharpest sentence available: at the
pin, "Sysbox enforces Linux user-namespaces on all sandboxes" was refutable by one grep in
ninety seconds. Today, the same claim, in nearly the same words, from the same vendor, is
unfalsifiable. Nothing about the claim changed. Only its checkability did.

**Stated so it could be wrong:** if a future before/after read of another closed vendor finds a
frozen-era contradiction still detectable from public sources after closure — or finds capability
facts vanishing at a higher rate than contradictions — this refinement is false. The maximally
closed slot itself stays named and open on issue #11.

## E1-E4 confrontation

- **E1 (blast radius sets the autonomy ceiling) — CONFIRMS, and adds a mechanism the earlier
  reads didn't have.** Daytona sells isolation as the product, and the closure post makes the
  logic explicit: the codebase was closed *because* "for infrastructure whose only purpose is to
  contain hostile code, an open codebase is an unacceptable risk" — E1's argument pushed up into
  the disclosure decision itself. New here: the ceiling is priced by billing tier. A restricted,
  non-overridable network posture becomes open internet access purely as a function of how much
  an organization has spent — $500 of lifetime top-up buys a materially wider blast radius, with
  no code involved.
- **E2 (isolation without fidelity produces category-2-looking failures) — CONFIRMS, in the
  opposite direction from E2B.** E2B *rejects* fidelity to protect its boundary (no kernel
  modules, no SELinux, Docker-in-sandbox structurally impossible). Daytona *spends* its boundary
  to buy fidelity, and says so in its own code comments: non-GPU sandboxes stay privileged
  because "current workloads" need it; `/dev/kvm` passes through for Android emulation; GPUs pass
  through via CDI with a fixed slice. Same principle, opposite sign — a genuinely useful paired
  instance. The secrets redesign is the sharpest post-closure example of the same move: rather
  than choosing between a credential inside the sandbox (fidelity, no isolation) or none at all
  (isolation, no fidelity), a placeholder sits inside and the real value sits at the network
  boundary.
- **E3 (relationship verb: bundle/bind/internalize/inhabit, plus abstention) — SILENT, and
  correctly so, matching E2B/Modal/Cloudflare Sandbox SDK's precedent.** Daytona *is* the
  environment a harness would relate to — it ships adapters outward (an opencode plugin, CLI MCP
  tools) rather than reaching inward for one — so `environment_relation` stays deliberately
  unset here, for the same reason it does on every other category-3 report.
- **E4 (environment economics leak upward into choices no harness can see) — CONFIRMS, upgraded
  from single-instance to convergent-across-two, and amended with a disclosure-forced sibling
  clause.** E2B and Daytona face the identical pressure — make "create" cheap — and resolve it
  with opposite mechanisms: snapshot-resume plus lazy paging vs. a warm pool released by
  rewriting the owning organization on an already-running container. The two instances converge
  on the *principle* and diverge on the *mechanism* — Daytona's leak lands in the tenancy model
  (a sentinel zero-UUID organization owning running containers; a creation timestamp that is not
  the container's age) rather than in kernel or scheduler tuning. Separately, this read amends
  E4's own scope: its "invisible from any SDK" clause holds, but "legible only when the
  environment is open" is too strong as originally stated. Where an environment's economics land
  in tier, quota, gating, or lifecycle policy, they are **disclosure-forced** — a vendor must
  publish what a customer bought for the product to be sellable — and stay legible after closure;
  Tract C's frozen-docs cross-check confirms this was never source-dependent for Daytona in the
  first place, since the tier structure was already documented at the pin. Where the economics
  land in kernel, scheduler, or tenancy internals, closure still removes them completely. E4
  should read: *closure hides the mechanism by which an environment's economics were
  implemented; it does not hide the economics themselves where the product must disclose them to
  be sold.*

## Surprises

1. **Closure did not uniformly darken the product.** The credentials page and the warm-pool page
   are both more mechanism-rich today than the frozen docs ever were — a placeholder-substitution
   secrets model and an exact warm-pool claim predicate, neither of which existed in any form at
   the pin. Any narrative of "closed source, closed disclosure" is falsified by this axis alone.
2. **The frozen docs already carried the finding Tract B thought was new.** The tier-gated
   network default — the sharpest thing the current-docs read surfaced, with "no analog in E2B
   or Modal" — turns out to already be in the frozen in-repo docs, unchanged in substance across
   the closure boundary. Reading only the current side would have mis-dated a two-month-old
   policy as a closure-era one.
3. **The isolation claim that most needed checking is the one that became uncheckable.** "Sysbox
   enforces Linux user-namespaces on all sandboxes" was a ninety-second grep away from refutation
   at the pin and is, word for word, still quotable from the vendor today — just no longer from
   a page a source reader could check it against.
4. **A closed vendor can still be convicted from the web alone, twice over, and a third time by
   holding both eras at once.** The homepage's still-live "Open-Source Transparency... No Black
   Boxes" section sits beside the vendor's own closure announcement; `/docs/en/sandboxes/`'s
   "dedicated kernel" contradicts `/docs/isolation`'s own container-vs-VM split; and the GitHub
   README's "under the LICENSE" sits beside a tip tree that no longer contains one. Modal's read
   concluded "you cannot catch a closed vendor being wrong — there is no code to convict the
   docs." That conclusion needs amending, not restating: docs-against-code dies at closure;
   docs-against-docs, docs-against-announcement, and docs-against-repo-state do not.

## Open questions

- The maximally closed slot named on issue #11 — thin uncommented client, no trust center, no
  advisories, no source lineage at all — is still unfilled. Daytona's rich client contract and
  surviving trust surface make it a moderate-disclosure instance, not the extreme case.
- Does the refutation-capacity framing generalize? A second before/after read of a different
  closed vendor, holding a real pre-closure source snapshot against its current docs, is the only
  way to test whether the zero-survival-rate for docs-against-code contradictions holds beyond
  n=1.
- Whether BYOC container images are publicly pullable without a Daytona contract is undocumented
  and decisive for whether the current self-host route is operable at all outside a sales
  conversation — unresolved by either instrument.
- The advertised "<90ms" creation figure has no published methodology and no visible relationship
  to the frozen cold-create path's undefaulted start timeouts; unresolved without a live probe
  against the current API, which this read does not run.

## What was not verified

- **Nothing was executed.** No sandbox created, no live API called against the current product;
  every current-state claim is documentation and advisory testimony, `retrieved: 2026-08-21`,
  never independently checkable — which is this report's subject, not a gap in it.
- The trust center and CVE advisory are **residual pre-closure publication**, not current
  documentation — the security-exhibit page they point toward already 301s into a portal that no
  longer lists the document itself. This channel is real today and observed decaying in front of
  the read; a reader in six months may not have it.
- `llms-full.txt` (a generated full-docs dump dated 2026-08-18) was fetched but not reliably
  searchable through this session's fetch tooling; it was not used to support any GONE verdict
  above, and a local `curl` + grep pass against it is the natural next check before trusting any
  negative claim about the current docs corpus at greater depth than this report reaches.
- The GPU sandbox class, the Windows sandbox class in detail, and the region/routing surface named
  in `/docs/architecture` were read only at the level Tract B and Tract C's briefs covered; none
  were independently re-verified by this session beyond the citations above.
