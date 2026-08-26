---
name: e2b
category: 3
vendor: FoundryLabs, Inc. (E2B)
url: https://github.com/e2b-dev/E2B
license: Apache-2.0   # root LICENSE on both repos; note the SDK package.json/pyproject declare MIT — unresolved mismatch, see What it is
open_source: true
stack: [Python, TypeScript, Go]   # SDK/CLI clone is Py+TS; the infra clone (isolation machinery) is Go
version: "@e2b/python-sdk@2.39.1"
commit: f5d702a5   # the e2b SDK/CLI clone; this is what build-tool-index --check validates
# SECOND PIN, prose-recorded (a report carries one machine-checked commit): the isolation
# machinery lives in e2b-dev/infra @ fcc2edbc9 (read 2026-08-16). Every server-side claim
# below is dated to that pin. Re-check drift with: repo-facts.sh e2b-infra
# Drift check 2026-08-20: current e2b-infra HEAD 7c417f485, 48 commits ahead of fcc2edbc9
# (297 files changed). Assessment: drift touches cell-bearing claims. packages/orchestrator/
# pkg/sandbox/sandbox.go and .../fc/process.go (isolation_primitive) both changed; the uffd/
# subtree (uffd.go, memory_backend.go, userfaultfd/) plus new snapshot_template handlers in
# packages/api and packages/db (snapshot_model) changed heavily; packages/orchestrator/pkg/
# proxy/, packages/orchestrator/pkg/tcpfirewall/, and packages/shared/pkg/sandbox-network/
# firewall.go (egress_default, egress_controls) also changed. No spiffe/jwt-named path
# changed (credential_model's SPIFFE JWT-SVID claim unaffected by name). iac/ and
# docs/ARCHITECTURE.md changed too. Per D-07 the cells are set from pin-state prose anyway;
# a dated drift caveat is attached at the affected cells in plan 07-02.
first_commit: 2023-03-04   # e2b SDK repo; the infra repo's 2019 root is an imported fossil — see History
stars: 13423
stars_at: 2026-08-16
read_at: 2026-08-16
depth: deep-dive   # for a non-harness: isolation mechanism, sandbox lifecycle, and multi-tenancy traced in source across both repos (three parallel Opus reads), 10 load-bearing claims spot-verified at the pins by the main session. NOT run — no sandbox created; wire-level claims are strong code inference, labelled where they are not demonstrated
environment_features:   # ADR-0017 block, set 2026-08-20 from the existing deep-dive read at f5d702a5 (and e2b-infra @ fcc2edbc9) — not a re-read
  isolation_primitive: hardware-virt:firecracker-microvm   # each sandbox is a Firecracker microVM (What it is); no jailer/chroot/uid-drop, fc/process.go:196 — drift 2026-08-20: sandbox.go/fc/process.go changed since fcc2edbc9; cell set from pin-state prose per D-07
  egress_default: open   # internet on by default at wire+SDK (Blast radius; sandbox_api.py/sandboxApi.ts:1455) — drift 2026-08-20: proxy/tcpfirewall/firewall.go changed since fcc2edbc9; cell set from pin-state prose per D-07
  egress_controls: allow-biased   # an allow entry beats a deny, incl. allowInternetAccess:false (Blast radius; tcpfirewall/handlers.go:152-196) — drift 2026-08-20: tcpfirewall/ changed since fcc2edbc9; cell set from pin-state prose per D-07
  credential_model: broker-relayed:spiffe-jwt-svid   # guest never holds the credential; SPIFFE JWT-SVID brokered at the egress proxy (Credential exposure; js-sdk/src/sandbox/iam.ts:41-50)
  snapshot_model: create-is-resume:uffd-lazy-paging   # every create dispatches to Resume/RebootSandbox (sandboxes.go:242,255); uffd lazy paging + prefetch (sandbox.go:885) — drift 2026-08-20: uffd/ subtree + snapshot_template handlers changed since fcc2edbc9; cell set from pin-state prose per D-07
  self_host: partial   # closed components: the credential-injecting egress proxy, belt (Self-hosting reality & the open-core seam)
  warm_pool: false   # verified absent — grep -rniE "prewarm|warm.?pool" over packages/, iac/, docs/ (The distinguishing bet)
  filesystem_sync: clone   # ADR-0017 probe record, 2026-08-20 — first-class Sandbox.git.clone(url, opts) wired into Sandbox, both Python SDKs + JS SDK (no anchor in e2b.md's own prose)
# environments: / environment_relation: DELIBERATELY UNSET. Those keys describe how a
# *harness* relates to an environment; E2B *is* the environment — the thing on the far side
# of hermes' `bind`. It has no relation-to-an-environment of its own, so it does not appear
# in comparisons/environments.md. That absence is correct, not a gap.
---

# E2B

The first category-3 report, and the one commissioned to answer a specific question: **issue
#11's gate.** The 2026-08-16 adjudication concluded category 3 "survives as an analytic lens
and fails as a population" — real, but only ever seen as a *property of a category-2 tool*,
never studied as an entity. The gate to keep it a category: read one agent-native environment
as a product in its own right and see whether it yields findings that are **not**
restatements of "how a harness attaches to it." This is that read. **The gate passes**
(verdict section below), which falsifies the pending verdict — the intended, recorded
outcome of a falsifiable claim.

## What it is

A remote-sandbox service for running untrusted / agent-generated code: each sandbox is a
**Firecracker microVM**, created from a Docker-image-derived template, reachable over the
network through a guest daemon (`envd`). Two open-source repos were read:

- **`e2b-dev/E2B`** (`f5d702a5`) — the client side: JS SDK, Python SDK, CLI. Verified to be
  **an API client with no local execution mode** — every operation begins with
  `POST https://api.e2b.app/sandboxes` (`packages/python-sdk/e2b/sandbox_sync/sandbox_api.py:280`,
  URL derivation `connection_config.py:212-216`).
- **`e2b-dev/infra`** (`fcc2edbc9`) — the isolation machinery: 1,720 Go files, the
  orchestrator, the Firecracker integration, network/firewall handling, Terraform for GCP
  and AWS. This is where the substance is.

Licence is Apache-2.0 on both repo roots, but the SDK's `package.json`/`pyproject.toml`
declare **MIT** — an unresolved mismatch, recorded not resolved.

## The distinguishing bet

**That the unit of isolation should be a microVM you can snapshot, not a container you keep
running** — and that the whole product is then an exercise in making VM snapshots cheap
enough to treat as ephemeral.

Everything distinctive follows from that one bet. There is **no warm pool** of live VMs
(verified absent, scope: `grep -rniE "prewarm|warm.?pool"` over `packages/`,`iac/`,`docs/`).
Instead, *every* "create" is internally a **snapshot resume** — the request path dispatches
only to `ResumeSandbox`/`RebootSandbox`, and the fresh-boot `CreateSandbox` is unreachable
from it, called only by the template builder (`packages/orchestrator/pkg/server/sandboxes.go:242,255`;
`docs/ARCHITECTURE.md:287-288` states it, code confirms). Cheap resume is bought with
userfaultfd lazy paging plus a prefetch working-set — and the working-set is itself
computed by **resuming the template twice at build time and keeping only the pages touched
in both runs** (`packages/orchestrator/pkg/template/build/phases/optimize/prefetch.go:12-50`,
`prefetchIterations = 2` at `optimize/builder.go:35`).

## Isolation mechanism — the spine

Traced server-side, request to running VM. Spot-verified at the pin where flagged **[✓]**.

1. `POST /sandboxes` → placement by **best-of-K** (K=3, overcommit ratio R=4, α=0.5;
   `placement/placement_best_of_K.go:25-59`), CPU-only score — **RAM is carried but never
   scored** (verified absent: no RAM admission check in `orchestrator/pkg`).
2. Team concurrency reserved first, in **Redis via a Lua compare-and-reserve** (not a DB
   count), default tier = 20 concurrent (`reservations/redis/scripts.go:35-64`; tier seed
   `db/migrations/…20231220…sql:5`); over-limit → HTTP 429.
3. Orchestrator gRPC `Create` → dispatch on snapshot kind → **`ResumeSandbox`**
   (`sandbox/sandbox.go:885`): uffd memory handler, network slot, NBD rootfs overlay, memory
   serving — built concurrently — then cgroup, then Firecracker.
4. **Firecracker runs as root under `unshare -m` + a netns + a cgroup. No jailer, no chroot,
   no uid drop. [✓]** (`fc/process.go:196`; `jailer` returns zero non-comment hits in
   `orchestrator/pkg`). FC's own built-in seccomp still applies; the jailer's chroot/uid-drop
   do not. This contradicts standard Firecracker deployment guidance and is the single most
   important isolation fact.
5. **Firecracker is a private fork** — `e2b-dev/e2b-firecracker`, clone-gated behind
   `FIRECRACKER_REPO_TOKEN` **[✓]** (`firecracker/fc-versions/build.sh:3-5`) — carrying
   snapshot-correctness patches upstream lacks (virtio-disk flush on snapshot, memfd backing,
   sync write-protect, balloon free-page hinting). The guest **kernel is also patched** (6.1.x
   only, one balloon-hinting patch in-tree). Self-hosters get the fork's *binary* from a public
   bucket, not its source. "E2B runs Firecracker" is true and badly underspecifies.
6. Rootfs = read-only template device + per-sandbox copy-on-write cache, served to FC as an
   in-process **userspace NBD** overlay (`rootfs/nbd.go:34-49`, `block/overlay.go:33-76`).
7. Guest agent `envd` is **baked into the template rootfs at build time**; identity is
   delivered via **MMDS carrying only a token *hash*** (`envd/internal/host/mmds.go:34-39`),
   never the token itself.

## The five category-3 axes

**Blast radius.** Internet is **on by default** at both wire and SDK
(`sandbox_api.py`/`sandboxApi.ts:1455`, `allow_internet_access ?? true`). Lateral movement
(sandbox→sandbox, sandbox→host) and cloud-metadata (`169.254.169.254`) are blocked — but as
a *side effect of the addressing plan*: sandbox host IPs sit in `10.11.0.0/16`, inside a
hardcoded `DeniedSandboxCIDRs` deny set (`shared/pkg/sandbox-network/firewall.go:19-31`), not
through per-tenant rules. All TCP egress is terminated and re-originated by a **userspace Go
proxy on the host** doing SNI/Host inspection but **no TLS interception** (`CABundle()==""`),
with DNS-rebinding defeated by a pre-`connect()` private-IP check (`tcpfirewall/handlers.go:152-196`).
Egress policy is **allow-biased**: an allow entry beats a deny, including beating
`allowInternetAccess:false`. A deliberate hole to the host survives full internet denial — a
`192.0.2.1` (RFC-5737 TEST-NET) channel to hyperloop/NFS/portmapper, authenticated purely by
SNAT-assigned source IP.

**Fidelity.** Docker image → bootable VM across five distro families with **real init**
(systemd on debian/rhel/arch, OpenRC on alpine, a NixOS shim). The sharpest fidelity
statement in either repo is a **hard rejection of RHEL/Oracle/Amazon Linux [✓]** — because
E2B's kernel means `/lib/modules` is empty and SELinux is off, "most of what RHEL … [is]
chosen for (kABI, signed kmods, UEK)" (`template/build/phases/base/distro/distro.go:70-78`).
**No kernel modules, no SELinux, ever.** Distroless/scratch rejected by name.
**Docker-in-sandbox is structurally impossible** (Firecracker doesn't nest; no `/dev/kvm`
into the guest). **GPU is absent, not limited** — the only `gpu` hits are test fixtures for a
generic node-label placement filter.

**Parallelism.** Per-team concurrency in Postgres tiers, enforced in Redis; node cap 200
sandboxes, **concurrent *starts* per node capped at 3** by semaphore, with an asymmetry:
resumes block up to 15s on it, cold creates fail fast. Rate limiting exists but ships with
**no code defaults** — an absent LaunchDarkly flag means no limit, fail-open. `fork(count)`
caps at 100.

**Startup cost.** The code's own cold-vs-warm ratio is **6×** — `rebootEnvdTimeout = 60s`
("a cold boot needs a longer window than a memory resume") vs a 10s resume readiness budget.
The tightest constant in the tree is a **50 ms** per-attempt `/init` poll, retried every 5 ms
to a 10 s deadline. **No repo contains a marketing latency number** (verified absent across
all READMEs/docs) and **no test asserts a latency bound** — the two benchmarks report
percentiles without thresholds.

**Credential exposure.** The **team API key never enters the sandbox** (verified absent in
the `/init` payload). The envd access token is a **deterministic HMAC of the sandbox ID [✓]**
under one cluster-wide seed (`sandbox_envd_secret.go:27-29`) — not random, no expiry, one seed
compromise derives the fleet. Its strongest design: **workload identity is brokered at the
egress proxy**, so the guest never holds the third-party credential — SPIFFE `JWT-SVID`
placeholders the proxy substitutes per request, "the secret itself never leaves the platform"
(`js-sdk/src/sandbox/iam.ts:41-50`; proto `orchestrator.proto:70-86` states the API mints
nothing). Can sandboxed code exfiltrate the keys that made it? **No** — it can recover only
its own envd token, which authorizes only itself.

**The default-open / default-closed split [✓].** At the wire, `secure` is opt-in
(`sandbox_create.go:186`) and unset ⇒ envd auth falls through ⇒ a **REST-created sandbox is
an unauthenticated root `/files` API on a public URL**, guarded only by ~103-bit sandbox-ID
entropy (conditional on `uniuri.UUIDLen==20`, unverified — module not vendored). The official
SDKs close it: `secure = True` / `secure ?? true`. Read only the SDK and you conclude
sandboxes are authenticated by default; read only the API and you conclude they are not. Both
are correct. This is the cleanest example of a fact invisible above the SDK.

## Self-hosting reality & the open-core seam

Apache-2.0, genuinely operable outside E2B's cloud — but only on **GCP (supported) or AWS
(beta, not at parity)**, via Terraform + Nomad + Consul, never Kubernetes (the K8s discovery
code points at an `iac/k8s/job-orchestrator` dir that does not exist). LaunchDarkly, billing,
and core-API auth degrade to working no-ops offline; **dashboard-api hard-requires Ory** but
defaults to zero instances.

Two load-bearing pieces are **closed**, and both are visible as dead seams in the open code:

- **The egress proxy that injects credentials is not in either repo.** `SandboxNetworkTransform`
  is defined end-to-end — SDK types, OpenAPI, DB, proto — yet `GetTransform()`/`GetHeaders()`
  have **zero consumers [✓]**; the in-repo proxy returns `SupportsBYOP()==false` and rejects
  with `Unimplemented`. E2B's most security-critical data-path component is not open.
- **`belt`, the persistent-volume content API, is a separate private repo** — this repo mints
  the JWT and returns a domain but serves no volume bytes.

So the shipped open-source orchestrator is **provably not the one E2B runs** — a cleaner,
more honest open-core boundary than most, but a real one.

## Bleed

Category 3 is the whole subject, so "bleed" runs the other way — into what depends on E2B:

- **← category 2 (harnesses).** E2B is the concrete thing on the far side of hermes-agent's
  `bind` verb (hermes ships a `modal`/`daytona`/`vercel_sandbox` backend set; E2B is the same
  category). It is what `bundle` (Devin) hides and what `internalize` (codex) replaces with an
  in-process sandbox. This report is the first time the repo has looked at that far side
  directly rather than through a harness's frontmatter.
- **→ Standards (MCP).** The SDK ships a hand-maintained **catalog of ~300 third-party MCP
  servers** as generated type definitions and can launch an `mcp-gateway` in-sandbox — but
  there is **no MCP client or server implementation** (`grep modelcontextprotocol` → zero),
  and server-side MCP is an opaque map used only for analytics. E2B positions the sandbox as
  an MCP *host*; it does not implement the protocol.
- **Independent-distribution: confirmed, strongly.** Zero AI-framework dependencies in either
  lockfile (`langchain|openai|anthropic|crewai|@ai-sdk` → 0); the wire protocol is generic
  Linux (`Process`/`Filesystem` services). The one real coupling is to E2B's own control
  plane, not to any harness. This is exactly the category-3 independence test, and E2B passes it
  cleanly — which is *why* it was a fair gate specimen.

## The gate verdict — issue #11

**The gate passes, and not narrowly.** Classifying every finding as either *(a) a fact about
the environment itself* (true whether or not any AI harness existed — for a CI runner, a
notebook backend, an untrusted-code service) or *(b) a restatement of harness-attachment*:
roughly **26 (a) findings against 6 (b)**, and the asymmetry is worse than the count — the
(b) items are shallow (a method list, an opaque passthrough, connection limits) while the (a)
items include mechanisms no outside observer would guess:

- a throwaway VM booted after every pause, network-denied, purely to record which memory
  pages the *next* resume will fault (`prefetch_harvest.go`);
- an in-VM agent that **upgrades itself at the same PID** via `syscall.Exec`, carrying a frozen
  tenant workload's file descriptors across the exec;
- a hard refusal to support RHEL stated in terms of kernel modules the platform will never
  have;
- `kcompactd` disabled in every guest because host-side hugepage backing would make page
  migration dirty the snapshot diff for no workload benefit — **guest kernel tuning driven by
  host snapshot economics.**

**The clean discriminator: every (a) finding is invisible from the SDK.** A study of "how a
harness attaches to E2B" produces the six (b) items and stops. It never learns that internet
is on by default, that the wire leaves a root file API unauthenticated, that RAM is never
scheduled on, that there is no warm pool, or that the credential-injection component is
closed-source.

**Two honest qualifications, carried into the adjudication:**

1. The axes are **not equally productive.** Blast radius, fidelity, and credentials each
   produced multiple non-obvious findings; **parallelism and startup produced mostly numbers**
   — real and citable, but closer to datasheet material. The category's justification rests on
   the first three, not on all five.
2. **This is one instance, and an unusually favourable one.** E2B open-sources its
   infrastructure, which is what made the (a) list reachable at all. A closed environment
   (Modal, Daytona, Cloudflare Sandboxes) would yield mostly testimony, and the same gate run
   against it could fail for reasons of *access* rather than *substance*. The category's status
   should not be generalized from E2B alone — but E2B is sufficient to defeat the "fails as a
   population" verdict, because one genuine population member is all that claim needed to be
   wrong.

## Surprises

1. **The open build is not the production build**, and you can see the seam: `GetTransform`
   has no callers, `SupportsBYOP` is hardcoded false. Most open-core hides this; E2B leaves
   the socket visible.
2. **Default-open wire, default-closed client** — the security posture inverts depending on
   which half you read.
3. **No warm pool.** Given "start almost instantly," I expected pre-resumed VMs. The latency
   is entirely snapshot-resume + lazy paging + build-time prefetch traces.
4. **The 2019 git root is a fossil** — Carlos Neira's independent `firecracker-task-driver`
   Nomad plugin, subtree'd in by *Devbook* (E2B's pre-rebrand identity) in 2022 and deleted
   five months later. The product line is Devbook (2022) → E2B (2023); `first_commit` on the
   SDK repo (2023-03-04) is the honest product date. The infra repo's 2019 root is three
   products removed from what it is now.
5. **Two `ARCHITECTURE.md` claims the code does not support** at this pin: workload identity is
   described as acted-upon but `GetIam()` has zero non-generated callers (a declared contract,
   no implementation); and "never a host-kernel mount of the tenant image" is true for the
   *resume* path but false for the *build* path, which loop-mounts tenant-derived ext4 with the
   host kernel. A different, unacknowledged trust posture on build nodes vs sandbox nodes.

## Open questions

- Does the gate result **generalize**, or is it E2B-specific? The honest test is a *second*
  category-3 read against a **closed** environment (Modal/Daytona/Cloudflare). If that yields only
  testimony, the finding is "the category is real but only legible when the environment is open"
  — a sharper and more useful claim than either current pole.
- Production-build delta: does E2B's real orchestrator carry the CA-injecting egress proxy, the
  BYOP dialer, the `iam` executor? Unverifiable from these repos; only the *absence* in the
  open build is established.
- Is the unauthenticated-`/files`-by-default wire posture a real exposure in practice, or fully
  mitigated by sandbox-ID entropy and the SDK default? Code-level inference only — not
  demonstrated, and should not be repeated as if it were.

## What was not verified

- **Nothing was executed.** No sandbox created; all wire-level claims are static code inference,
  labelled where not demonstrated (esp. the `/files` default).
- `uniuri.UUIDLen` — module not vendored in the blobless clones; the ~103-bit entropy figure is
  conditional on it being 20.
- `e2b-dev/belt` and `e2b-dev/e2b-firecracker` — private, not readable; conclusions rest on their
  absence plus in-repo references.
- The **infra pin (`fcc2edbc9`) is prose-recorded, not machine-checked** — a report carries one
  frontmatter `commit`, and it points at the SDK clone. Drift on the infra claims must be
  checked manually (`repo-facts.sh e2b-infra`). This is a small strain the one-pin-per-report
  model puts on a multi-repo subject; recorded rather than worked around.
