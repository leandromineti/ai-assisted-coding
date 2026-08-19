---
name: modal
category: 3
vendor: Modal Labs
url: https://github.com/modal-labs/modal-client
license: Apache-2.0   # the CLIENT only; the infrastructure is closed and has no public repo
open_source: false   # the PRODUCT is closed — only the client SDK is open. This is the point of the read; see What it is
stack: [Python, Go, TypeScript]   # modal-client monorepo; Python is the reference SDK
version: py/v1.5.4-7-g59e6e618
commit: 59e6e618   # the open modal client (cloned as upstream/modal); --check guards this pin even though the PRODUCT is closed — see the generator's decouple note (2026-08-16)
first_commit: 2021-07-09
stars: 502   # the client repo only — not a measure of the product's reach
stars_at: 2026-08-16
read_at: 2026-08-16
depth: survey   # client source (proto + shipped container agent) read closely; the ENVIRONMENT ITSELF is closed and characterized from (a) the wire contract and (b) dated vendor testimony — NOT from infra source. That grade cap IS the finding. Not run.
# environments: / environment_relation: DELIBERATELY UNSET — same as e2b. Modal IS the
# environment, not a harness that relates to one, so it does not appear in the
# environments matrix.
---

# Modal

The second layer-3 report, and it exists to answer the question E2B's read left open
([issue #11](https://github.com/leandromineti/ai-assisted-coding/issues/11)): **was E2B's
gate pass an artifact of E2B being open source?** E2B let me read its *infrastructure*, which
is where 26 of its 26 gate-winning environment-facts lived. Modal is the control: its client
SDK is open (Apache-2.0), its **infrastructure is closed** (no infra repo exists). If a closed
environment collapses to vendor marketing, the rung is "real only when legible." It does not
collapse — but *how* it stays legible, and what closure permanently removes, is the finding.

Read from two instruments, kept at distinct evidence grades throughout:

- **Client source** — `modal-labs/modal-client` @ `59e6e618`, read closely (the Python SDK,
  the `modal_proto/` gRPC contract, and the *shipped in-container agent* under `py/modal/_runtime/`).
  This is **VERIFIED** evidence, file:line.
- **Vendor testimony** — Modal's engineering blog and docs, `retrieved: 2026-08-16`. This is
  **TESTIMONY**: mechanism-level, but Modal's word, uncheckable against code. Labelled inline.

## What it is

A serverless-compute platform whose sandbox product runs untrusted / agent code. Its
isolation primitive is **gVisor (`runsc`)** — a userspace kernel intercepting guest syscalls
— **not** a hardware-virtualized microVM. That single fact is the sharpest *environment-level*
contrast with E2B (Firecracker), and it is recoverable: the client's proto exposes a
`runtime` override of exactly `"runc"` or `"gvisor"` [✓ `modal_proto/api.proto:1908, 2641,
3434`] and pins a `runsc_runtime_version` per snapshot [✓ `api.proto:945, 3432`].

## The client/infra boundary — the proto is a leaky contract

The decisive structural finding, and the reason closure does not win here: **a closed vendor
still has to name every capability its clients configure, and those names live in the wire
contract.** `modal_proto/api.proto` (≈5,000 lines) and `task_command_router.proto` leak infra
vocabulary in field names and comments that no marketing page would volunteer. The proto is a
confession, not a proof.

Two structural facts fall straight out of it, both VERIFIED:

1. **Two-tier data plane.** Create returns a `command_router_access` [✓ `api.proto:3512-3518`];
   exec/stdio/filesystem then bypass the control plane and connect **directly to the worker
   host's public IPv4**, with a deliberate note: *"clients should connect directly to this IP
   while still using the URL's hostname for TLS SNI and the HTTP/2 :authority header"* [✓
   `api.proto:3533-3535`]. Workers have public IPs and terminate TLS for a hostname that isn't
   their address — the closest analog to E2B's network-seam finding, and it came from a proto
   comment.
2. **The client ships the in-container agent.** `py/modal/_runtime/` is not a stub — it is the
   code that runs *inside* the sandbox, and it is the richest verifiable environment source in
   the repo. `_runtime/gpu_memory_snapshot.py` shells out to NVIDIA's **`cuda-checkpoint
   --toggle --pid`** [✓ cites `github.com/NVIDIA/cuda-checkpoint`] to snapshot GPU state. That
   is a concrete, checkable mechanism recovered without any infra repo.

There is **no local execution mode** [✓ — the only `subprocess` in `sandbox.py` is a docstring;
image builds stream remotely via `ImageJoinStreaming`, `_image.py:433-441`]. Control plane is
an active-active failover pair `api.modal.com,api.modal2.com` [✓ `config.py:109-110`].

## Environment-facts recovered, by evidence grade

The honest core of this read is that Modal's environment-facts sort into three grades, and the
grade distribution — not the count — is what answers the successor question.

**Bucket A — VERIFIED from client source (~9 facts):** gVisor/runc client-selectable runtimes;
gVisor version-pinned memory snapshots; GPU snapshot via `cuda-checkpoint`; two-tier
direct-to-worker data plane with SNI spoofing; memory-snapshot restore **pinned to the original
instance type** [✓ `api.proto:3457-3460`]; egress default **OPEN** with an
open/blocked/allowlist(CIDR+domain) model mutable at runtime [✓ `sandbox.py:248`,
`api.proto:2983-2993`]; a sandbox is a *task* that can host multiple named sub-containers [✓
`task_command_router.proto:68-102`]; multi-cloud incl. OCI [✓ `api.proto:104`]; a "new
scheduler" with fine-grained placement that replaced an experimental one [✓ `api.proto:1947-1950`].

**Bucket A′ — TESTIMONY, mechanism-level (Modal's engineering blog, `retrieved: 2026-08-16`):**
memory snapshots use **gVisor's built-in checkpoint/restore, not CRIU directly** — "gVisor's
core `kernel.go` … and at least eighteen system components implement checkpoint/restore"
([modal.com/blog/mem-snapshots]); the process memory is a "pages" file (100 MiB–10 GiB), live
network and NVIDIA GPU state excluded; the read-only lower layer is a **FUSE-based lazy-loading
file server** over OverlayFS that aggressively preloads the pages file; restore page-faults
cost "10s of milliseconds" worst case. Scheduler: "control plane backed by a database as source
of truth" but the "scheduler operates over an in-memory view of cluster state," with a partition
bottleneck acknowledged at scale ([amplifypartners.com/…/behind-the-scenes-of-modal-sandboxes]).

**Bucket C — OPAQUE, and this is the load-bearing part.** The specific *genre* of fact that made
E2B's read valuable is unreachable. E2B's five signature findings and their Modal status:

| E2B signature finding | Modal analog |
|---|---|
| Firecracker runs with **no jailer** (verified in source) | **OPAQUE** — the sandbox launch/isolation path is not in the client |
| host cgroups **account but never limit** (zero `cpu.max` writes) | **OPAQUE** — client sends `Resources{memory_mb, milli_cpu}` [`api.proto:3335`]; enforcement invisible |
| guest **`kcompactd` disabled** for snapshot economics | **OPAQUE** — no kernel/tuning surface exists in the client at all |
| the credential-injection **proxy is closed** (dead seam in open code) | **OPAQUE** — Modal *has* a proxy [`Sandbox.proxy_id`, `api.proto:3418`]; internals invisible, and there is no open build to find a seam in |
| **`ARCHITECTURE.md` overclaims** the code contradicts | **STRUCTURALLY IMPOSSIBLE** — no code to contradict the docs |

Four of five have no recoverable analog; the fifth (claim-vs-code discrepancy) *cannot exist*
for a closed environment, because catching a vendor being wrong requires a source to check the
claim against. **Closure does not remove environment-facts — it removes the *audit grade*.**

## The five axes (grades in brackets)

- **Blast radius** [VERIFIED interface / OPAQUE enforcement] — egress OPEN by default, inbound
  off, no workspace-resource access ("blast radius … limited to the Sandbox container itself",
  docs TESTIMONY). Controls: `block_network`, `outbound_cidr_allowlist`,
  `outbound_domain_allowlist` (beta, **TLS/443 only**). That 443-only domain restriction is the
  *same shape* as E2B's SNI-inspecting firewall — a convergent layer-3 design fact across two
  independently-built environments.
- **Fidelity** [VERIFIED] — remote image build; full GPU enumeration in the client
  (T4…H200, `api.proto:229-241`). gVisor means the fidelity ceiling is *syscall coverage*, not
  E2B's *kernel-module absence* — a different ceiling from a different isolation primitive,
  though the exact unsupported-syscall set is OPAQUE.
- **Parallelism** [VERIFIED primitives / OPAQUE limits] — `.map()`/`.spawn()`, `SchedulerPlacement`,
  `max_concurrent_gpus`; pool sizes and per-account caps server-side. Testimony: "50,000+
  concurrent sessions."
- **Startup cost** [VERIFIED surface / TESTIMONY mechanism] — `enable_snapshot` (memory+fs),
  restore is a create-shaped RPC `SandboxRestoreV2`, instance-type-pinned; "3–10× faster" and
  ">50% cold-start reduction" are TESTIMONY. No latency number is checkable.
- **Credential exposure** [VERIFIED] — long-lived `MODAL_TOKEN_ID/SECRET` are control-plane
  only [✓ `client.py:51-57`], never sent to the worker (which uses a short-lived JWT). **Ephemeral
  secret values transit the create RPC** as inline `ephemeral_secrets` [✓ `sandbox.py:1062`,
  `api.proto:3507`] — plaintext-over-TLS to Modal's backend. Optional OIDC identity token for
  AWS/GCP federation. Whether secrets land as env vars vs tmpfs inside the guest is OPAQUE.

## Cross-environment contrast — the value that needed two reads

The rung's strongest evidence is not either environment alone but the **variation between them**,
which a harness-attachment study could never produce because it never looks at the environment:

| | E2B | Modal |
|---|---|---|
| Isolation primitive | Firecracker **microVM** (hardware virt) | **gVisor `runsc`** (userspace syscall intercept) |
| "Secure by default" means | VM boundary; wire default *unauthenticated* | container boundary; no inbound, no workspace access |
| Sandbox model | flat: one microVM = one sandbox | a *task* on the serverless-function substrate; multiple sub-containers |
| Snapshot | uffd lazy paging + build-time prefetch trace | gVisor built-in C/R, "pages" file, FUSE preload |
| Fidelity ceiling | no kernel modules, no SELinux (kernel-level) | syscall-coverage-level (gVisor reimplements the kernel) |
| Domain egress control | SNI-inspecting firewall, 443 | `outbound_domain_allowlist`, TLS/443 (**convergent**) |
| Legible via | **open infra source** | **open client + leaky proto + vendor testimony** |

Two agent-native environments, two fundamentally different isolation primitives, one convergent
egress-control shape. That is a **population with internal variation**, not a monoculture — which
is exactly what "layer 3 is a real rung" needed and what the E2B-only read could not establish.

## The successor-question verdict (issue #11)

**The rung survives closure, with a precise caveat on evidence grade.** A closed environment is
studiable to the depth of *(its wire contract) + (its published engineering)* — for Modal, that
is substantial: ~9 source-verified environment-facts plus mechanism-level testimony, enough to
place Modal firmly beside E2B as a second population member and to surface a real cross-environment
contrast. So the demotion that E2B already blocked stays blocked; Modal reinforces it.

**But closure caps the grade at "declared / cited," never "audited."** The two finding-classes
that made E2B's read sharp — *mechanism below the API line* and *discrepancy between claim and
code* — are respectively opaque and impossible for Modal. The refined claim for the layer:
**an execution environment is legible in proportion to (client-contract richness + vendor
disclosure), and only open infrastructure yields audit-grade facts.** Modal is unusually
disclosure-rich (a commented proto, a shipped in-container agent, honest engineering blogs); a
tighter-lipped closed environment would fall further toward Bucket C. n=2 for the rung, n=1 for
"closed but disclosure-rich" — a maximally-closed environment is still untested.

## Surprises

1. **The proto out-discloses the Python.** Field names and comments (`runsc_runtime_version`,
   "pin gVisor version", the SNI-spoofing note, `_restore_instance_type`, "new scheduler") leak
   more real infra than any source file. For a closed vendor this is a large, probably
   underappreciated disclosure surface — the generated wire contract is where the environment
   confesses.
2. **The client ships the in-container agent**, so `cuda-checkpoint --toggle` is readable as a
   literal subprocess call. The richest *verifiable* environment-facts live in the code that runs
   *inside* the sandbox, not in the SDK that calls it.
3. **A Modal sandbox is a thin specialization of its serverless-function substrate** (shared
   `runtime`/`checkpointing_enabled` fields, sub-containers, function-style scheduling), where an
   E2B sandbox is a purpose-built flat microVM. Two products solving the same layer-3 problem from
   opposite starting substrates.
4. **You cannot catch Modal being wrong.** E2B's most valuable findings were places its own docs
   over-claimed relative to its code. For Modal there is no code to convict the docs — the read
   can only report what Modal says, dated and labelled. That asymmetry, not any single fact, is
   the true cost of closure.

## Open questions

- The successor question is answered for a *disclosure-rich* closed environment. The sharper
  test remains: a closed environment with a **thin, uncommented client and no engineering blog**
  (some of Daytona's or Cloudflare's surfaces may qualify). If that falls to mostly Bucket C, the
  refined law holds; if it too leaks via its proto, wire contracts are a more robust disclosure
  floor than expected. Kept on issue #11.
- Does Modal's gVisor syscall-coverage fidelity ceiling actually bite agent workloads in practice
  (some tools need syscalls gVisor doesn't implement)? Unanswerable from the client; a behavioral
  test, not a source read.

## What was not verified

- **Nothing was executed**; no sandbox created. All VERIFIED claims are client-source reads at
  `59e6e618`; all mechanism claims about the closed infra are **TESTIMONY** (Modal's blog/docs,
  `retrieved: 2026-08-16`), not independently checkable — that uncheckability is the report's
  subject, not a gap in it.
- The infra has **no pin** — there is no infra repo. Unlike E2B (where a second prose-recorded
  pin covered readable infra source), Modal's environment claims cannot drift-check against
  anything; they can only be re-retrieved from Modal's docs and re-dated.
- `depth: survey`, deliberately not `deep-dive`: the client was read closely, but an environment
  whose isolation, scheduler, and kernel are closed cannot be deep-dived by definition. Calling
  this a deep-dive would claim a depth the closure forbids.
