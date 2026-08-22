---
name: microsandbox
category: 3
vendor: superradcompany (open-source project; formerly at microsandbox/microsandbox, which now
  redirects here — checked 2026-08-21 via `gh api repos/microsandbox/microsandbox
  --jq .full_name`, one canonical repository reached via two slugs, not two repos)
url: https://github.com/superradcompany/microsandbox
license: Apache-2.0
open_source: true
stack: [Rust, TypeScript, Python, Go]   # Rust-dominant (605 tracked .rs files); TS/Py/Go are SDK bindings — see repo-facts.sh output
version: v0.6.12-3-g0191b03
commit: 0191b03
first_commit: 2024-10-03
stars: 7829
stars_at: 2026-08-21
read_at: 2026-08-21
depth: deep-dive   # isolation mechanism, network defaults, and filesystem/credential model traced in source (three parallel Opus reads, orchestrator-dispatched; load-bearing claims independently spot-verified at the pin by this executor session and flagged [✓]). NOT run — /dev/kvm absent on this host 2026-08-21; every behavioural claim is static-source-derived, never OBSERVED.
environment_features:   # ADR-0017 block, set 2026-08-21 from the deep-dive read at 0191b03 — not a re-read
  isolation_primitive: hardware-virt:msb-krun-vmm   # Isolation mechanism — the spine, step 9 + lattice verdict; KVM/HVF/WHP fail-closed on all 3 host OSes, no C libkrun FFI (0 hits repo-wide), VMM is the project's own Rust crate msb_krun (Cargo.toml:91, =0.1.31 exact pin)
  egress_default: open   # Blast radius section; crates/network/lib/policy/types.rs:724-727 (from_profiles([Public])) + config/types.rs:171-177 (enabled: true) — carve-out: metadata/private/loopback/multicast/host denied by the same default, destination.rs:35-124
  egress_controls: allow-biased   # Blast radius section; policy/types.rs:453 (first-match-wins, not deny-overrides — a caveat this cell can't hold, see report prose)
  credential_model: broker-relayed:tls-proxy-placeholder-substitution   # Credential exposure section; crates/network/lib/network.rs:406-408,446-449 (guest holds "$MSB_<VAR>", real value substituted only at the host TLS proxy for allow-listed hosts) — coined specific value, no existing registry precedent for this mechanism
  snapshot_model: explicit-backup:sparse-upper-copy   # Cell notes section; sdk/rust/lib/snapshot/create.rs:200-205 (scope: SnapshotScope::Disk, sparse-aware copy of the writable upper.ext4) — user-invoked `msb snapshot save`, not automatic; Resumable variant reserved in the schema (manifest.rs:77-82) but constructed only in tests
  self_host: full   # No open-core seam section; crates/utils/lib/lib.rs:19,156-172 (everything under one operator-controlled $MSB_HOME, no daemon, no telemetry beacon)
  warm_pool: false   # Cell notes section — verified absent, zero hits across three independent pattern sets (prewarm/prestart/preboot/prespawn/standby over crates/; "warm pool"/"vm pool"/"sandbox pool" over docs/; warm.?pool/pre.?warm over sdk/ packages/); idle sandboxes are torn down, not parked (crates/runtime/lib/vm.rs:1223,1251)
  filesystem_sync: [mount, upload]   # Cell notes section — conjunction: both genuinely first-class (mount: 4 types across CLI+all SDKs, crates/cli/lib/commands/common.rs:131,135; upload: sdk/rust/lib/sandbox/fs.rs:466 copy_from_host over the command channel); no default anchor either way — nothing is mounted unless the caller explicitly asks (current_dir() absent from every mount-path grep scope); no `clone` (git-clone) surface exists anywhere in this codebase
# environments: / environment_relation: DELIBERATELY UNSET. Those keys describe how a
# *harness* relates to an environment; microsandbox *is* the environment — the thing on
# the far side of a caller's `bind`, same reasoning as e2b.md. It has no relation-to-an-
# environment of its own, so it does not appear in comparisons/environments.md.
---

# microsandbox

Category 3's fourth read, and the first that is neither a remote metered service nor
borrowed container infrastructure: a **local-first, embeddable microVM library**, distributed
as a Rust crate with Python/TypeScript/Go bindings and a CLI built on the same library. It
fills the seed inventory's empty local-VM-grade row and is the honest test of whether
ADR-0017's eight keys describe execution environments in general or describe hosted SaaS in
particular — a subject with no control plane, no metering, and (in the local path) no
network hop between caller and guest.

## What it is

A microVM runtime and SDK you link into your own process, not a service you call. `Sandbox`
handles in Python, TypeScript, Go, and Rust all resolve to the same Rust library
(`sdk/rust/lib`), which either spawns a local hardware-virtualized VM as a child process of
the caller (`LocalBackend`) or, opt-in only, talks HTTP to a hosted `microsandbox cloud`
control plane whose server implementation is **not in this clone**
(`sdk/rust/lib/backend/cloud/http.rs:83-84,99`). Everything in this report is the local
path unless a section says otherwise.

**Two deliberate deviations from this category's usual report shape, stated rather than
silently absorbed, per this plan's design:** unlike e2b/modal/cloudflare-sandbox-sdk, there
is no vendor cloud to contrast self-hosting against — the local path *is* the product, not a
downgraded fallback from a hosted default (see "No open-core seam to describe" below). And
there is no remote control plane between caller and guest to trace: the SDK is a compiled
native extension linked into the caller's own process (pyo3 for Python, napi-rs for
TypeScript), not an HTTP client. Where e2b.md and cloudflare-sandbox-sdk.md have a "the wire
protocol" or "API client" section, this report has none — there is no wire between the SDK
call and the spawned VM.

Guest kernel provenance is a forked, pinned `libkrunfw` — not `containers/libkrunfw` but a
fork under the project's own GitHub org, on a non-default branch (`.gitmodules:1-4`,
`url = https://github.com/superradcompany/libkrunfw.git`, `branch = krunfw`), version-pinned
in two places kept in sync by hand (`justfile:1-3`, `crates/utils/lib/lib.rs:89-93`, both
`5.6.1`). One kernel image is shared by every sandbox on a host — installed once, not
per-sandbox (`crates/utils/lib/lib.rs:176-207`). The submodule is uninitialized in this
clone, so the kernel `.config` and any delta versus the unforked upstream are not readable at
this pin.

The VMM itself is a Rust crate family, `msb_krun = "=0.1.31"` (`Cargo.toml:91`, exact pin, not
a caret range), **not a C `libkrun` FFI wrapper** — see "Isolation mechanism" below for why
this overturns the obvious first guess.

## The distinguishing bet

**That isolation should be a library call, not a service** — that the caller's own process
can own the hypervisor boundary directly, with no daemon, no broker, and (locally) no
network in between. README states the intended consequence plainly:

> `README.md:37` (DOC) — "**Embeddable**: Spawn VMs right within your code. No setup server.
> No long-running daemon."
> `README.md:127` (DOC) — "`Sandbox::builder("...").create()` boots a microVM as a child
> process. No infrastructure required."

Everything distinctive follows: the trade for owning the boundary directly is that the
*caller's own machine* must be KVM/HVF/WHP-capable (see "Run-probe record" below — this is
exactly the wall this read hit), and there is no server-side warm pool to hide a cold boot
behind, because there is no server. The isolation strength is decoupled from the service
architecture entirely — a genuine counter-instance to any framing that assumes hosted
execution needs a service boundary to be strong.

## Isolation mechanism — the spine

Traced from a library call to a running guest. Spot-verified at the pin (`0191b03`) where
flagged **[✓]**. **Exactly one process boundary and one hypervisor boundary separate the
caller from the guest** — no daemon, no broker, no local network hop.

1. **SDK call, in-process — boundary: Python/JS → native extension, no network.** The Python
   SDK is a stub over a compiled pyo3 extension (`sdk/python/microsandbox/__init__.py:5`),
   the TypeScript SDK the same shape via napi-rs (`sdk/node-ts/src/internal/napi.ts:14`), and
   the CLI a peer consumer of the identical library, not a server above it
   (`crates/cli/lib/commands/start.rs:47`). All four bindings resolve to
   `microsandbox::sandbox::Sandbox::start` (`sdk/python/src/sandbox.rs:267`,
   `sdk/node-ts/native/sandbox.rs:93`), which is a workspace path dependency, not a separate
   product: `Cargo.toml:78` — `microsandbox = { version = "=0.6.12", path = "sdk/rust",
   default-features = false }`.
2. **Backend dispatch is a Rust trait, not a wire protocol.** `sdk/rust/lib/backend/mod.rs:65-70`
   distinguishes `Local` ("Spawns microVMs on the calling host") from `Cloud` ("talking to an
   msb-cloud control plane over HTTP") as two implementations of one trait — the Local/Cloud
   split lives entirely in-process.
3. **The typed launch config is serialized off `argv` and handed across an inherited file
   descriptor**, deliberately to keep secrets out of `ps`/`/proc/<pid>/cmdline`
   (`crates/runtime/lib/launch.rs:1-9`; fixed constant `CONFIG_FD = 96`,
   `crates/runtime/lib/vm.rs:74`).
4. **PROCESS BOUNDARY — the `msb` binary re-execs itself as the per-sandbox VM process. [✓]**
   `sdk/rust/lib/runtime/spawn.rs:525` — `let mut cmd = Command::new(&msb_path);`; `spawn.rs:627`
   — `match cmd.spawn() {`. The subcommand is hidden from the CLI surface
   (`crates/cli/bin/main.rs:78-80`, `#[command(hide = true)]`) — an internal re-entry point,
   never a user command.
5. **Sandbox process entry point never returns.** `crates/runtime/lib/vm.rs:493` — `pub fn
   enter(config: Config) -> ! {` **[✓]** — starts the agent relay, heartbeat, and idle timeout,
   configures the VMM, and hands the process to it.
6. **VMM configuration via a Rust builder, not a C ABI.** `crates/runtime/lib/vm.rs:1417` —
   `let mut builder = VmBuilder::new()`, sized from typed fields: default 1 vCPU, 512 MiB,
   hard-capped by the VMM at build time. **[✓]** `packages/microsandbox-types/rust/lib/domain.rs:22,25`
   — `DEFAULT_SANDBOX_CPUS: u8 = 1`, `DEFAULT_SANDBOX_MEMORY_MIB: u32 = 512`.
7. **Guest kernel is selected by host process → `libkrunfw` shared object**, with the raw
   kernel command line kept deliberately internal to avoid a general boot-argument escape
   hatch (`crates/runtime/lib/vm.rs:1448-1452`).
8. **Root filesystem attach — three mutually exclusive forms**: a bind rootfs, a `layered`
   OCI image (read-only base image + writable overlay, joined by overlayfs *inside the
   guest*), or an EROFS "flat" reflink-cloned base. **For the default OCI path, no host
   directory is mapped into the guest at all** — the `/dev/root` virtiofs tag is backed by a
   deliberately empty temp directory. **[✓]** `crates/runtime/lib/vm.rs:1468-1480` —
   `tempfile::tempdir()` feeding `PassthroughConfig { root_dir: trampoline_path, … }`.
9. **HYPERVISOR BOUNDARY (not readable at this pin).** `vm.enter()` hands the process to
   `msb_krun`'s `Vm::enter()`, which creates vCPU threads and runs the guest. The crate is a
   binary crates.io dependency with no vendored source and no `[patch]` override
   (`Cargo.lock:4324-4327`), so vCPU start and the virtio device model are out of scope for a
   source read of this repo — the last citable step on the microsandbox side is
   `vm.rs:1301` (`match vm.enter()`).
10. **GUEST SIDE — the kernel execs an init binary the host synthesized.** A virtual,
    read-only `/init.krun` appears at the root of every filesystem backend, containing the
    `agentd` binary compiled into `msb` itself (`crates/filesystem/lib/backends/shared/init_binary.rs:1-6`,
    `crates/filesystem/lib/agentd.rs:8` — `include_bytes!`).
11. **Guest PID 1 (`agentd`) mounts filesystems and either stays PID 1 or hands off to the
    image's own init** (`crates/agentd/lib/config.rs:88-89`). The overlayfs join happens here,
    not on the host — `crates/agentd/lib/init.rs:360-361`: `format!("lowerdir={lower_dir},
    upperdir={upper_dir},workdir={work_dir}")`.

**Overturns the obvious first guess: there is no C `libkrun` FFI in this repository. [✓]**
Repo-wide search for the C API surface (`krun_create_ctx|krun_set_vm_config|
krun_start_enter|krun_set_root|krun_set_exec|libkrun\.so|libkrun\.dylib|-lkrun`) returns
**zero hits**. The VMM is `msb_krun`, a Rust crate family the project itself publishes to
crates.io, driven through a Rust builder API — a **libkrun re-implementation in Rust**
(`kvm-ioctls`, `msb_krun_hvf` all present in `Cargo.lock:4328-4341`), not a wrapper around
the C project. The README's own phrasing — "made microsandbox possible" (`README.md:456`,
DOC) — reads as lineage, not linkage, and this report follows that reading rather than the
"through the libkrun VMM" phrasing `docs/security/isolation.mdx:14` (DOC) uses. Only
`libkrunfw`, the guest kernel bundle, is genuinely vendored (as a Git submodule) and is
itself a fork (see "What it is").

**There is no daemon and no server anywhere in this trace. [✓]** Older public descriptions of
this project mention a JSON-RPC `msb server`; at this pin it does not exist. Repo-wide,
`jsonrpc|json-rpc|JSON-RPC` returns zero hits; `axum|Router::new|hyper::server|actix|warp::`
returns hits only in unit tests, a guest-network port publisher, an SSH port-forward, and one
cloud test stub — none a control-plane router. `ls crates/cli/lib/commands/ | grep -i server`
is empty. A reader coming from an older README or a memory of the project would place a
server hop in this trace that no longer exists.

**Isolation-primitive lattice verdict (ADR-0017): `hardware-virt`, on all three host
platforms, no second tier.** Every host path fails closed with no software fallback: Linux
requires `/dev/kvm` to exist and be openable **[✓]**
(`sdk/rust/lib/setup/linux.rs:19,74-78` — `const KVM_DEVICE = "/dev/kvm"`, `if !kvm.exists()`);
macOS requires Apple silicon plus a code-signed hypervisor entitlement **[✓]**
(`msb-entitlements.plist:5-6` — `com.apple.security.hypervisor`); Windows requires WHP to
report `HypervisorPresent` **[✓]** (`sdk/rust/lib/setup/windows.rs:20-22` —
`WINHV_PLATFORM_DLL`, `WHV_CAPABILITY_CODE_HYPERVISOR_PRESENT`). The opt-in "restricted"
guest security profile (drops `CAP_SYS_ADMIN`, forces `nosuid,nodev`,
`crates/agentd/lib/config.rs:137-142`) is in-guest hardening *above* this boundary, not a
second family — it does not change the cell.

## The five category-3 axes

**Blast radius.** Host-facing, the device model is a fixed virtio set (console, net, fs,
blk, rng) with no general-purpose passthrough (DOC, `docs/security/isolation.mdx:30-40`), and
for the default OCI boot path the code goes further than the doc claims: no host directory is
mapped at all (step 8 above). Network egress is **open by default**, but with a real
carve-out that changing the cell's family alone would lose. The default policy is
`from_profiles([NetworkProfile::Public])` **[✓]** (`crates/network/lib/policy/types.rs:724-727`),
reached only when the caller passes no network flags **[✓]** (`crates/cli/lib/commands/common.rs:2336-2344`,
`if no_flags { return Ok(None); }`), and `NetworkConfig::default()` has `enabled: true` **[✓]**
(`crates/network/lib/config/types.rs:171-177`). Under that default a guest reaches the whole
public internet on any port or protocol — but cloud metadata (`169.254.169.254`, classified
ahead of the broader link-local range **[✓]**, `crates/network/lib/policy/destination.rs:115-124`),
RFC1918/ULA/CGNAT private space, loopback, multicast, and the sandbox's own gateway are all
denied by the same default, deliberately (`crates/network/lib/policy/destination.rs:35-37`
names the CGNAT/ULA ordering rationale explicitly). DNS-rebind protection is on by default
too, closing the obvious bypass of the private-range denial. One IPv6 gap: `is_metadata` is
IPv4-only (`destination.rs:115-121`), so AWS's IPv6 metadata endpoint is not classified
`Metadata` — it is still denied under the *default* profile because it falls inside the
broader `fc00::/7` `Private` range, but a caller who opts into `--net private` for LAN access
silently re-opens it.

Egress evaluation is **first-match-wins, not deny-overrides [✓]**
(`crates/network/lib/policy/types.rs:453`, "Returns the action from the first matching rule");
a `deny` placed after an `allow` never fires, a real footgun the codebase itself only
mitigates with a build-time shadow-rule warning. Published ports bind host loopback by
default, not `0.0.0.0` (`crates/network/lib/config/types.rs:206-208`) — but `default_ingress`
carries two opposite defaults depending on construction path: `Allow` in the programmatic
profile builder, `Action::deny` in the serde default for a hand-written policy file
(`crates/network/lib/policy/types.rs:54,328`) — the same field, opposite failure mode,
depending on how the config was built. Host loopback is reachable from the guest, but only
via `host.microsandbox.internal`/the gateway IP rewrite, and only if the caller opts into
`--net host` — the default profile grants no allow rule for the `Host` destination group.
Sandbox-to-sandbox network isolation is **structural, not documented**: each sandbox gets a
private `/30` (v4) / `/64` (v6), no bridging construct exists anywhere in the codebase, and
the peer's address is never assigned to a host interface — but the docs never state a
cross-sandbox network guarantee, so this report records it as inference from four independent
structural facts, not a vendor promise.

**Fidelity.** Thinnest axis this read produced evidence for — deliberately not overclaimed.
OCI images boot as block devices (read-only base + per-sandbox writable overlay, joined by
guest-side overlayfs, step 8/11 above), which is architecturally closer to a real VM boot
than a container unpack. Whether arbitrary Docker images run genuinely unmodified, whether
Docker-in-sandbox is possible (the guest has its own kernel, unlike e2b's Firecracker, which
structurally cannot nest), and whether particular distro families are rejected the way e2b
rejects RHEL — none of this was traced in this read. Recorded as unverified rather than
guessed, per methodology rule 4a's absence discipline.

**Parallelism.** A type-level `DeploymentProfile` dial exists — `SingleTenant` (default) vs.
opt-in `MultiTenant`, "platform-owned isolation floors" (`packages/microsandbox-types/rust/lib/domain.rs:246-252`)
— but is a policy dial over the same isolation primitive, not a second tier. Sandboxes share
no kernel, writable disk, network namespace, or process tree, but they **do** share a
host-global dirty-page writeback credit pool arbitrated fairly across live VMs and a CPU
placement-lease directory (`crates/runtime/lib/launch.rs:52-53,82-84`) — a real resource
coupling the isolation-mechanism docs' own "share no…" list does not mention. Default
concurrent-connection cap is 256 per sandbox, max 4096, with bandwidth/packet-rate limits
unlimited by default (`crates/network/lib/config/types.rs:67-73`).

**Startup cost.** The published claim — "boot times under 100 milliseconds" — is scoped
narrower than the headline: `README.md:467` (DOC), a footnote, states this is **guest boot
only, on an M1 Mac**, excluding every host-side step in the trace above (config
serialization, process spawn, root-image setup, VMM build) and saying nothing about
Linux/KVM hosts. No in-repo benchmark backs the number. The real latency levers are caching
and copy-on-write, **not pooling**: OCI base images are converted once into content-addressed
EROFS artifacts in a global cache and referenced without copying
(`crates/image/lib/cache/store.rs:241-244`), and the "flat" mode reflink-clones a prebuilt
ext4 base for genuine host-kernel copy-on-write (`sdk/rust/lib/sandbox/flat_rootfs.rs:1,108-114`).
There is **no warm pool** — see "Cell notes" below — so every start is a cold boot; the
optimization budget went entirely into caching and cloning instead of pre-booted standby VMs.

**Credential exposure.** The strongest axis this read produced, and materially different from
e2b's or cloudflare's shape. Locally, there is **no authentication on the sandbox-start
path** — containment is uid plus filesystem permissions (`0o700` on the agent relay socket
directory, `crates/runtime/lib/ipc.rs:229,246`, host owner uid captured explicitly at
`relay.rs:274`), not a credential check. A separate, opt-in `msb ssh serve` surface refuses to
start with no authorized key and accepts public-key auth only (no password/no-auth path
found, `sdk/rust/lib/sandbox/ssh.rs:2019-2023`). For third-party secrets, the mechanism is the
sharpest finding in the tract: **the guest never holds the real value.** `--secret
OPENAI_API_KEY@api.openai.com` puts the literal string `$MSB_OPENAI_API_KEY` in the guest's
environment **[✓]** (`crates/utils/lib/secret.rs:8-9` — `format!("$MSB_{env_var}")`); the
real value is substituted only at the host's own TLS-intercepting proxy, only for requests to
allow-listed hosts, gated on verified TLS identity by default **[✓]**
(`crates/network/lib/network.rs:406-408,446-449` — "Real secret values stay in the host-side
network handler and never enter this payload"). Egress is scanned for *placeholders*, never
for real secret values — the struct scanned on the wire carries no value field at all
(`crates/network/lib/secrets/handler.rs:242-246`), a structural absence, not a policy choice.
Violation default is fail-closed with a log **[✓]** (`packages/microsandbox-types/rust/lib/domain.rs:2138-2141`
— `#[default] BlockAndLog`), and even the opt-in `Passthrough` action degrades to
`BlockAndLog` rather than allow on a non-match. The trade for this strength: it **requires
MITM of the guest's own TLS**, and adding any secret silently enables interception on port
443 even if the caller never asked for it (`sdk/rust/lib/sandbox/builder.rs:863-866`). Registry
credentials for pulling images take a five-tier chain including an OS keyring
(`crates/image/lib/auth.rs:9-17`). The hosted cloud path is a different trust model entirely
— `MSB_API_KEY` is an *outbound* bearer credential to `microsandbox cloud`'s own control
plane, and does not by itself select that backend: the precedence order in
`sdk/rust/lib/backend/profile.rs:3-12` is explicit that an ambient `MSB_API_KEY` alone falls
through to `LocalBackend`.

## No open-core seam to describe

e2b's report and cloudflare-sandbox-sdk's each spend a section on the gap between the open
repository and the vendor's production deployment. There is no equivalent seam here to find:
the local path *is* the shipped product, not a downgraded substitute for a hosted default —
`self_host: full` is not a strong reading of an ambiguous case, it is the plain fact that
everything in the local path (the VMM invocation, the guest agent, the filesystem backends,
the network stack including its TLS proxy, the SQLite state store, the image cache, volumes,
snapshots) runs under one directory the operator controls, `~/.microsandbox` or `$MSB_HOME`
(`crates/utils/lib/lib.rs:19,156-172`), with no daemon (`docs/cloud/overview.mdx:11`, DOC:
"there is no daemon or separate client") and no telemetry beacon (only a user-configured
OpenTelemetry exporter exists, `crates/metrics-collector/lib/exporters/otel.rs:46-56` —
nothing phones home to the vendor). A separate hosted product, `microsandbox cloud`, exists
in private beta (`docs/cloud/overview.mdx:8`, DOC) sharing the same SDK surface, but its
server implementation is not in this clone (`sdk/rust/lib/backend/cloud/http.rs:83-84` names
routes it targets, `/v1/sandboxes/*`, that are source-silent here) — every cloud-side claim in
this report is omitted-with-reason rather than assumed to mirror the local path. Two honest
qualifiers that keep `full` from overclaiming: OCI base images are still pulled from ordinary
registries (Docker Hub by convention, any registry by config) though cached locally and
optionally bundled fully offline (`msb snapshot save --with-image`,
`docs/sandboxes/snapshots.mdx:232-234`, DOC); and first install/upgrade fetches `libkrunfw`
and `agentd` binaries from GitHub Releases (`crates/utils/lib/lib.rs:195-228`) — neither is
per-sandbox runtime coupling to a vendor.

## Cell notes (transcribed into the frontmatter's ADR-0017 block above)

D-03's audit order keeps this reasoning in report prose, transcribed into the frontmatter's
`environment_features:` block in the same commit as this section — the anchor comments on
each cell point back here:

- **`isolation_primitive`** — `hardware-virt`, well-evidenced on all three host platforms; see
  the lattice verdict above. No tier falls outside the four ADR-0017 families.
- **`egress_default`** — the default reaches the whole public internet on any port; `open` is
  the honest family, with the metadata/private/loopback/multicast/host carve-out recorded as
  prose rather than folded into the cell (the "Blast radius" section above).
- **`egress_controls`** — allowlist-shaped (`default_egress: Deny` plus explicit allow rules),
  `allow-biased`; the first-match-wins ordering nuance (not classic deny-overrides) is a
  prose caveat, not a different family.
- **`credential_model`** — the guest holds a placeholder, never the value; substitution
  happens at the host's own TLS-intercepting proxy for allow-listed hosts only. This is a
  broker sitting between the guest and the real credential, structurally closer to e2b's
  `broker-relayed` family than to `plain-env-var` or `split-plane`. The specific mechanism
  (host-proxy placeholder substitution under TLS interception) has no existing specific-half
  precedent in the registry; the cell coins `tls-proxy-placeholder-substitution` for it.
- **`snapshot_model`** — creation is hardcoded to disk scope at the one construction site
  (`sdk/rust/lib/snapshot/create.rs:205` — `scope: SnapshotScope::Disk` **[✓]**); the schema
  separately *reserves* a `Resumable` variant "Disk, memory, and device state that can resume
  execution" (`crates/image/lib/snapshot/manifest.rs:77-82`) that **[✓]** is never constructed
  outside unit tests (`sdk/rust/tests/snapshot_artifact.rs:55,550,566`) — every non-test
  reference to it is a serialization arm, not a capability. Restore explicitly refuses
  anything but disk/file state (`sdk/rust/lib/sandbox/builder.rs:1232-1242`). This is an
  explicit, user-invoked, disk-only backup — `msb snapshot save` — not an automatic
  create-is-resume path and not a live checkpoint/restore: the family that fits is
  `explicit-backup`, with the memory/device reservation recorded as a deliberate forward-compat
  slot nothing fills at this pin, not an oversight.
- **`self_host`** — `full`; see "No open-core seam to describe" above.
- **`warm_pool`** — verified absent, not merely unchecked. Zero hits across three independent
  pattern sets: `prewarm|pre-warm|pre_warm|prestart|preboot|prespawn|standby` over `crates/`;
  `warm pool|vm pool|sandbox pool|pool of` over `docs/`; `warm.?pool|pre.?warm|sandbox pool|vm
  pool` over `sdk/ packages/`. An idle sandbox is torn down, not parked
  (`crates/runtime/lib/vm.rs:1223,1251` — "Reclaims the sandbox"), the structural inverse of a
  pool. The high-frequency word `pool` itself resolves to four unrelated senses in this
  codebase (a SQLite connection pool, an IP-address pool, a dirty-page writeback credit pool,
  and `spool`/`spooled` substring hits) — none of them a VM pool; the word "warm" resolves
  only to warm image-cache language and a docs page literally titled "warm workers" that is a
  disk-snapshot workflow, not a standby tier.
- **`filesystem_sync`** — no default working anchor exists at all: nothing from the host is
  mounted into the guest unless the caller explicitly asks (`current_dir()` never appears on
  a mount path across the CLI/SDK spawn and builder code, and the only two mount-list
  push sites are inside explicit builder mount methods). Two genuinely first-class paths
  compete for the cell — a native `mount` surface across four mount types (bind, named
  volume, disk-image, tmpfs), documented by the project as the faster and preferred path for
  anything beyond ad hoc reads/writes, and a command-channel `upload` API
  (`sb.fs().copy_from_host(...)`, `sdk/rust/lib/sandbox/fs.rs:466`) that the same docs rank
  explicitly second for bulk transfer. No `clone` (repo-cloning) surface exists anywhere in
  this codebase — the one grep hit for `clone` in this codebase means reflink/copy-on-write
  file cloning, never `git clone`. The cell records the conjunction `[mount, upload]` — ADR-0017's
  list-means-conjunction rule applies cleanly, since both are genuinely, independently offered,
  not alternate uncertain readings of one capability. The honest prose point either way: **no
  mount is ever implicit** — this environment has no notion of a default working directory at
  all, the sharpest specimen of the component vocabulary's "working directory" element this
  category has produced.

## Bleed

- **← category 2 (harnesses).** microsandbox is one of hermes-agent's eight swappable
  `bind` backends (see `notes/03-execution-environments/index.md`'s relationship vocabulary)
  — the same category as e2b, modal, and cloudflare-sandbox-sdk in that vocabulary, reached
  by a harness that binds to it rather than bundling or internalizing it.
- **→ category 6 (extensions).** An MCP server package (`microsandbox-mcp`) is referenced as a
  Git submodule but is **uninitialized and empty at this pin** (`.gitmodules`) — this clone
  cannot answer anything about its auth posture or design; a separate clone would be needed.
- **Independent-distribution: confirmed.** The local path has zero coupling to any AI
  framework or harness — it is a general-purpose microVM library whose SDK surface is
  process/filesystem/network primitives, not agent-specific verbs. The one coupling outward
  is the optional hosted control plane, itself vendor-neutral in shape (an SDK-selectable
  backend, not the default).

## Run-probe record

D-13's conditional run probe. `/dev/kvm` was checked before any probe was attempted or
described, per the plan's precondition:

```
$ ls -l /dev/kvm
ls: cannot access '/dev/kvm': No such file or directory
```

Checked 2026-08-21 00:04 UTC (Task 1, re-confirmed at Task 2 start, same result). **The device
is absent on this host.** Per D-13, the run probe degrades to source-only: nothing was
installed, built, or executed from `upstream/microsandbox` as a substitute. This is directly
corroborated by the source itself — `sdk/rust/lib/setup/linux.rs:19,74-78` makes `/dev/kvm`'s
presence a hard precondition the library checks and fails closed on, with remediation text
that explicitly covers the container/CI case (`linux.rs:81`: "in containers or CI, the host
must expose /dev/kvm to this environment"). Every claim in this report carrying no explicit
grade is **SOURCE**, per the deep-dive default (methodology rule 1a); none is **OBSERVED**.
Specifically unverified by execution: that a defaults-run guest actually reaches the public
internet and is actually denied the metadata/private ranges; that published ports actually
bind loopback only; that the guest-boot time is anywhere near the README's M1 figure on any
platform this host could test. These are strong source-level claims, not run evidence.

## E1-E4 confrontation

- **E1 (blast radius sets the autonomy ceiling) — CONFIRMS, with a sharpened edge.**
  microsandbox reaches `hardware-virt` isolation with no vendor, no control plane, and no
  daemon at all — the isolation strength is fully decoupled from any service architecture,
  since there is no service. This is code-verified, not README rhetoric: the SDKs are
  in-process native extensions (step 1), no HTTP/JSON-RPC server exists anywhere in the local
  path, and the library call spawns the VM as a direct child of the caller's own process (step
  4). The cost of buying that isolation strength is moved onto the host — the caller must own
  a KVM/HVF/WHP-capable machine, exactly the wall this read's own run-probe hit — and onto
  latency, since there is no warm pool to hide a cold boot behind.
- **E2 (isolation without fidelity produces category-2-looking failures) — CONFIRMS, in the
  purest form this category has produced.** The worktree/gitignore trap this index documents
  is a *partial* absence — some gitignored paths missing from a checkout. microsandbox
  generalizes it to a *total* absence: by default, **nothing** from the host reaches the
  guest, not even a working directory concept. `current_dir()` never appears on any mount
  path in the SDK or CLI spawn code, and the only two sites that push a host mount are both
  inside explicit, caller-invoked builder methods. An agent pointed at a bare
  `Sandbox::start()` would find an empty machine, not a container missing a few dotfiles — the
  same class of failure the trap names, at its logical extreme, and a strong argument that
  "isolation is only half the design; the other half is what you deliberately let back in" (E2's
  own closing line) generalizes past containers to microVMs cleanly.
- **E3 (relationship verb: bundle/bind/internalize/inhabit, plus abstention) — not
  applicable, matching e2b/modal/cloudflare-sandbox-sdk's precedent.** microsandbox *is* the
  environment a harness would relate to (hermes-agent's `bind` reaches it as one of eight
  backends), not a harness itself; `environment_relation` stays deliberately unset here for
  the same reason it does on every other category-3 report.
- **E4 (environment economics leak upward into kernel/scheduler choices) — CONTRADICTS as
  literally stated, but sharpens into a broader reading worth carrying forward.** There are no
  *vendor* economics anywhere in the local path — no pricing, no quota, no metered tenancy;
  the nearest analog is a type-level dial (`DeploymentProfile`) that defaults to the weaker
  `SingleTenant`. Any formulation of E4 that assumes a metered vendor boundary simply does not
  bind on a library with no vendor in its execution path. But the *shape* of E4's insight
  still shows up, sourced from a different kind of economics: **host resource constraints**,
  not vendor billing, drive a kernel-adjacent design choice — the dirty-page writeback credit
  pool and CPU placement-lease directory arbitrated fairly across every live VM sharing one
  host (`crates/runtime/lib/launch.rs:52-53,82-84`). That is E4's mechanism (economics →
  kernel/scheduler-adjacent choices) with the "vendor" premise stripped out — a candidate
  generalization of the principle, not adopted into `design-principles.md` here (plan 08-04
  collects verdicts across all three of this phase's reads).

## Surprises

1. **The obvious guess about the isolation mechanism is wrong.** "libkrun-based" reads as "a
   Rust wrapper calling into the C libkrun library." It is not: the C API surface is entirely
   absent (zero hits, repo-wide), and the VMM is a Rust re-implementation the project itself
   publishes to crates.io. "Made microsandbox possible" is the more honest framing than
   "runs on libkrun."
2. **There is no server, contradicting older descriptions of the project.** A prior JSON-RPC
   `msb server` does not exist at this pin — the SDK is a native in-process extension, full
   stop. A reader working from memory or an older README would place a network hop in the
   trace that has been architected away.
3. **The credential model is the strongest in this category so far, and it costs mandatory TLS
   interception to get there.** The guest never holds a real secret value under any
   circumstance the source could find — not because it is warned not to, but because the
   struct scanned on the wire has no field to hold one. The price is that using any secret at
   all silently turns on MITM of the guest's own HTTPS traffic on port 443, whether the
   caller asked for interception or not.
4. **The most extreme "no default working directory" this category has documented.** Every
   other environment this category has read (E2B, Modal, Cloudflare Sandbox SDK) has some
   notion of an uploaded or mounted anchor as part of normal use. microsandbox has none by
   default — the caller must explicitly wire in every path the guest can see, which is either
   the cleanest security posture in the category or the sharpest version of the worktree trap,
   depending on how a caller uses it.
5. **The same struct field has opposite defaults depending on how it's constructed.**
   `default_ingress` is `Allow` when built through the profile builder and `deny` when the
   serde default fires on an omitted field in a hand-written policy file — a genuine footgun
   the codebase does not flag anywhere in its own documentation.

## Open questions

- Does the fidelity axis hold up under actual testing — do arbitrary Docker images boot
  unmodified, and is Docker-in-sandbox structurally possible the way it is structurally
  impossible for e2b's Firecracker (no nested virtualization)? This microVM has its own
  kernel; the answer plausibly differs from e2b's, but this read did not trace it.
- What does `microsandbox cloud`'s hosted control plane actually implement against the
  `/v1/sandboxes/*` routes the SDK's cloud backend targets? Source-silent in this clone by
  design (private beta, separate repository).
- Does the `microsandbox-mcp` submodule (uninitialized here) reveal an MCP-server auth
  posture worth a future targeted read, the way this category has now checked that surface
  for other tools?
- The successor question this category has been tracking since 2026-08-16 — does an
  agent-native environment yield findings that are not restatements of harness attachment —
  is not this report's live question the way it was e2b's: microsandbox is open source with
  no closure ceiling at all, so this read is closer to a second data point for "open
  infrastructure yields audit-grade facts" than to a new legibility test. The still-open
  member of that successor question, a wholly closed environment with no open client at all,
  remains untested (issue #11).

## What was not verified

- **Nothing was executed.** `/dev/kvm` is absent on this host (checked 2026-08-21); no
  sandbox was ever booted. Every mechanism claim above is static source inference, not
  observed behavior — see "Run-probe record."
- **vCPU creation and the hypervisor entry itself.** `msb_krun`'s `Vm::enter()` internals are
  a binary crates.io dependency with no vendored source at this pin — the KVM/HVF/WHP ioctl
  sequence, the virtio device model, and the exact device list are not readable from this
  repository. The last citable step on the microsandbox side is `vm.rs:1301`.
- **The guest kernel bundle's contents.** `vendor/libkrunfw` is a pinned but uninitialized Git
  submodule in this clone — kernel `.config`, guest Linux version, and any delta versus the
  unforked `containers/libkrunfw` project are not established here. Initializing that one
  submodule is a cheap, KVM-free follow-up if a future read wants it.
- **`microsandbox cloud`'s server implementation and feature parity claims.** Not in this
  clone; every cloud-side statement above is either DOC-cited (`retrieved:` implicit in the
  `docs/` tree at this pin) or explicitly marked omitted-with-reason.
- **The fs-API's ≈3 MiB streaming chunk size and the exact removal-scope ("what `msb rm`
  keeps") table.** Both rest on in-repo docs (`docs/sandboxes/filesystem.mdx:87`,
  `docs/sandboxes/lifecycle.mdx:325-334`) that were not independently spot-verified against
  the delete implementation in this session; flagged by the tract reads as spot-verify
  candidates this report did not have budget to chase further.
