# ADR-0017 — A fifth registry block: `environment_features` for category-3 environments

`decided: 2026-08-20` · status: **accepted**

## Decision

The feature taxonomy gains a fifth block, **`environment_features`** — eight keys assessed on
category-3 reports (`applies_to: [3]`; the generator's row filter is **`category == 3`, with no
second predicate**). Category 3 carries no `type:` field on either existing report — unlike
category 5, whose `memory_features` filter needs a second predicate (`category == 5 and type ==
"memory"`, ADR-0013). Rendered as a fifth matrix section in `comparisons/features.md`.

**The canonical key set**, in this exact order — the canonical matrix column order Phase 6
transcribes:

1. **`isolation_primitive`** — the mechanism the sandbox's isolation boundary rests on (maps
   onto the component vocabulary's *host*). Open-descriptive `family:specific` tag; family half
   closed: `hardware-virt | userspace-kernel | shared-kernel | os-native`.
2. **`egress_default`** — the network posture in effect with no explicit configuration (*host* —
   network position). Closed lattice: `open | restricted | tier-gated`.
3. **`egress_controls`** — how an explicit allow/deny rule resolves against the default (*host*).
   Closed lattice: `allow-biased | deny-wins | none-native`.
4. **`credential_model`** — how a third-party credential reaches, or is kept from, the sandboxed
   process (maps onto *principal*). Open-descriptive `family:specific` tag; family half closed:
   `broker-relayed | split-plane | plain-env-var`.
5. **`snapshot_model`** — the mechanism by which sandbox state is paused/resumed (*host*).
   Open-descriptive `family:specific` tag; family half closed: `create-is-resume |
   checkpoint-restore | explicit-backup | none`.
6. **`self_host`** — whether the environment is genuinely operable outside the vendor's own
   cloud (*host*). Closed lattice: `full | partial | none`.
7. **`warm_pool`** — whether a pool of pre-started instances exists to cut cold-start latency
   (*host*). Boolean presence-claim (omitted = not checked, `false` = checked and absent, per
   this repo's standing discipline).
8. **`filesystem_sync`** — how the working anchor gets its content into the sandbox (maps onto
   the component vocabulary's *working directory*). Closed lattice, plain enum (not
   colon-tagged — see Decision scoping rule 3 below and the cell-value grammar section):
   `mount | clone | upload`. Appended **last**, admitted via the Task 1 probe and the Task 2
   checkpoint's verdict (see the Context probe record), so its admission does not perturb the
   order of the first seven.

Enum regime per D-10: **closed lattices** for `egress_default`, `egress_controls`, `self_host`,
and `filesystem_sync` — a new value requires a registry edit with dated rationale. **Open-descriptive
family:specific** for `isolation_primitive`, `snapshot_model`, `credential_model` — a new read may
coin a kebab-case specific value, defined in the report that introduces it. `warm_pool` is a plain
boolean, outside both regimes.

**Four scoping rules:**

1. **No `kind_link` on `environment_features` entries.** A `kind_link` resolving to category 3
   would make the cross-category table's demand and supply the same two-or-three reports — the
   same self-referential-row argument ADR-0013 used for `memory_features`. Demand-side linkage
   for category 3 lives instead at bucket granularity in `comparisons/environments.md`
   (`environments:` / `environment_relation:` frontmatter, `render_environments()`);
   instance-granular linkage — wiring a harness's declared environment to this block's cells — is
   a separate, later decision, contingent on category 3 first adopting a `type:`-like vocabulary
   of its own.
2. **Descriptive enums are not grades.** Contrast explicitly with **ADR-0011**: that ADR's ladder
   — `engine | hook | script | prose | true | false` — names the *strongest verified enforcer* of
   a gate. This block's enums (`hardware-virt`, `allow-biased`, `broker-relayed`, …) name a
   **mechanism choice**, not an enforcement rank; they do not adopt ADR-0011's graded values.
3. **Two verified instances admit a key (D-01).** The bar: a key must be cell-settable from the
   existing prose of both `e2b.md` and `modal.md` at their existing read pins, where a verified
   `false` and an explicit `OPAQUE` grade **each count as an instance** — matching this repo's
   own "false is a claim" discipline and the omitted-vs-checked distinction (a dot is not a no).
   `warm_pool` is the key that exercises this bar exactly: E2B verified `false`, Modal `OPAQUE`,
   neither a positive value, and it still admits.
4. **Cells only at read pins.** Setting a cell classifies prose already present in a report at
   its existing pin; it never moves `read_at`, `commit`, `stars_at`, or `depth` (methodology rule
   4b). The one exception this phase permits is the `filesystem_sync` probe itself, which is
   read-only against the *unmoved* pin (see the Context probe record) — no report frontmatter
   changes as a result.

This partially resolves **ADR-0010**'s deferred block question in the **more-blocks** direction —
blocks continue to multiply per assessed category rather than unifying into one namespace — and
instruments the category-level decision **ADR-0003** made (execution environments stay a
category) with an actual assessed vocabulary. Both referenced, neither edited.

## Context

### Provenance and reconciliation (EVOC-02)

v2.0's milestone research (`.planning/research/FEATURES.md`, `.planning/research/ARCHITECTURE.md`
— planning-local, not committed) produced two overlapping candidate-key lists from the same two
reads (`e2b.md`, `modal.md`): a five-key list and a six-key list. This ADR reconciles them into
one canonical set via three shape rules:

- **The two credential names collapse to one key** (D-05): `credential_model` replaces
  `credential_injection` and `credential_exposure` — broad enough to hold Modal's
  control-plane/worker-JWT split, which is not an injection fact.
- **The two snapshot names collapse to one key** (D-06): `snapshot_model` replaces
  `snapshot_restore` and `snapshot_default`.
- **The single egress name splits into two keys** (D-07): `egress_default` and
  `egress_controls` replace `egress_policy`, because the two sub-axes vary independently across
  the wider category — a tier-gated default with deny-wins controls is a real combination (e.g.
  a Daytona-shaped instance) — and splitting keeps the security-relevant
  allow-biased-vs-deny-wins distinction visible in the matrix rather than collapsed into one cell.

### Rejected-to-canonical decoder

One row per rejected name, one line of rationale each. No `taxonomy.yaml` deny-list entries for
any of these — the phrases have legitimate prose uses throughout the reports, the deny-list
growth procedure warns against entries that guarantee false positives, and the generator's
unknown-key warning already catches stray frontmatter keys.

| Rejected name | Rationale |
|---|---|
| `credential_injection` | Cannot hold Modal's control-plane/worker-JWT split, which is not an injection fact. |
| `credential_exposure` | Names a consequence rather than a mechanism. |
| `snapshot_restore` | A non-discriminating boolean — both known instances tick it (✓/✓). |
| `snapshot_default` | Its poles (persistent/ephemeral/type-gated) are evidenced only by unread, LOW-graded products — against the bar's spirit. |
| `deployment_mode` | Leaves E2B's cell ambiguous where the graded `self_host` key does not. |
| `egress_policy` | Collapses two independent axes (default posture vs. control precedence) into one cell. |

### Per-key instance record

The instance *fact*, not the full evidence — per-key evidence lives in the reports and, from
Phase 6, the registry notes, exactly as ADR-0013 kept its 11 keys' instances out of the ADR body.

| Key | E2B instance | Modal instance |
|---|---|---|
| `isolation_primitive` | `hardware-virt:firecracker-microvm` [✓] | `userspace-kernel:gvisor-runsc` [✓] |
| `egress_default` | `open` (internet on by default) [✓] | `open` (egress OPEN by default) [✓] |
| `egress_controls` | `allow-biased` (an allow entry beats a deny, including beating `allowInternetAccess:false`) [✓] | `OPAQUE` — the interface (`block_network`, CIDR/domain allowlists) is verified, but no source states whether an allow entry can override a block, the axis E2B's finding turns on |
| `credential_model` | `broker-relayed:spiffe-jwt-svid` (egress-proxy-brokered SPIFFE JWT-SVID) [✓] | `split-plane` (long-lived `MODAL_TOKEN_ID`/`SECRET` control-plane only; short-lived JWT to the worker) [✓] |
| `snapshot_model` | `create-is-resume:uffd-lazy-paging` [✓] | `checkpoint-restore` (bare family; the gVisor-internals specific mechanism is Modal's own TESTIMONY, not source-verified) |
| `self_host` | `partial` (named closed components: the egress proxy, `belt`) [✓] | `none` (no infra repo; SaaS-only) |
| `warm_pool` | `false` (verified absent — `grep -rniE "prewarm\|warm.?pool"` over `packages/`, `iac/`, `docs/`) [✓] | `OPAQUE` |
| `filesystem_sync` | `clone` (Task 1 probe, dated below) | `upload` (no local execution mode; image builds stream a remote build context — `ImageJoinStreaming`, `_image.py:433-441`) [✓] |

`warm_pool` is the key that exercises D-01's bar directly (D-02): neither instance is a positive
value, and it still admits.

### Probe record — `filesystem_sync` (2026-08-20)

**Subject:** `upstream/e2b` at rev `f5d702a5` (`f5d702a520de52ac0e5d4dda3ca0d5fca01d7993`) — the
same commit `e2b.md`'s `commit:` frontmatter is pinned to. **The pin was read, not moved**; this
is a targeted probe, not a re-read, and no report frontmatter changed as a result.

**Commands run, in order, with hit count** (including zero-hit searches — an absence verified by
grep is a claim in this repo, not a silence):

1. `git -C upstream/e2b grep -n "class Filesystem" f5d702a5 -- packages/python-sdk/e2b/sandbox_sync/filesystem/filesystem.py` → 1 hit: `f5d702a5:packages/python-sdk/e2b/sandbox_sync/filesystem/filesystem.py:76`.
2. `git -C upstream/e2b grep -nE "    def [a-z_]+\(" f5d702a5 -- .../sandbox_sync/filesystem/filesystem.py` → 14 hits; 10 distinct public methods (`read` [3 overload stubs], `write`, `write_files`, `list`, `exists`, `get_info`, `remove`, `rename`, `make_dir`, `watch_dir`).
3. `git -C upstream/e2b grep -n "class Filesystem" f5d702a5 -- .../sandbox_async/filesystem/filesystem.py` → 1 hit: `f5d702a5:packages/python-sdk/e2b/sandbox_async/filesystem/filesystem.py:82`.
4. `git -C upstream/e2b grep -nE "    async def [a-z_]+\(" f5d702a5 -- .../sandbox_async/filesystem/filesystem.py` → 14 hits, the same method set, async twin.
5. `git -C upstream/e2b grep -nE "class [A-Za-z]+ServiceStub|def [A-Za-z_]+\(" f5d702a5 -- .../envd/filesystem/filesystem_connect.py` → the envd wire RPC set is exactly 9: `stat`, `make_dir`, `move`, `list_dir`, `remove`, `watch_dir`, `create_watcher`, `get_watcher_events`, `remove_watcher` (`f5d702a5:packages/python-sdk/e2b/envd/filesystem/filesystem_connect.py:29-53`). **No `upload`/`write` RPC exists at the wire level** — file content moves through the SDK's own `write`/`write_files` methods, not a dedicated envd RPC.
6. `git -C upstream/e2b grep -ncE "git clone" f5d702a5 -- packages/cli packages/js-sdk packages/python-sdk` → hits in 5 files: `js-sdk/src/sandbox/git/index.ts`, `js-sdk/tests/sandbox/git/clone.test.ts`, `python-sdk/e2b/sandbox/_git/types.py`, `python-sdk/e2b/sandbox_async/git.py`, `python-sdk/e2b/sandbox_sync/git.py`.
7. `git -C upstream/e2b grep -ncE "gitClone" f5d702a5 -- packages/cli packages/js-sdk packages/python-sdk` → hits in 3 files (`js-sdk/src/template/index.ts`, `types.ts`, a stacktrace test) — the **template-build** system's own git-source path, a separate finding from the sandbox filesystem API.
8. `git -C upstream/e2b grep -ncE "from_git" f5d702a5 -- packages/cli packages/js-sdk packages/python-sdk` → **0 hits**.
9. `git -C upstream/e2b grep -ncE "fromGit" f5d702a5 -- packages/cli packages/js-sdk packages/python-sdk` → **0 hits**.
10. `git -C upstream/e2b grep -ncE "tarball" f5d702a5 -- packages/cli packages/js-sdk packages/python-sdk` → 1 hit (`packages/cli/CHANGELOG.md` only — not code).
11. `git -C upstream/e2b grep -ncE "\.tar\.gz" f5d702a5 -- packages/cli packages/js-sdk packages/python-sdk` → 3 files, none a sandbox-creation code path (`testground/demo-basic/.gitignore`, `template/utils.ts` formatting helper, `uv.lock` dependency lock).
12. `git -C upstream/e2b grep -ncE "upload" f5d702a5 -- packages/cli packages/js-sdk packages/python-sdk` → many hits (template-build file upload + filesystem `write`/`write_files` internals — an ad hoc upload path, distinct from a git-source API).
13. `git -C upstream/e2b grep -ncE "write_files" f5d702a5 -- packages/cli packages/js-sdk packages/python-sdk` → hits in `sandbox_sync`/`sandbox_async` `filesystem.py` + tests.
14. `git -C upstream/e2b grep -ncE "writeFiles" f5d702a5 -- packages/cli packages/js-sdk packages/python-sdk` → hits in `js-sdk/src/sandbox/filesystem/index.ts` + tests.
15. `git -C upstream/e2b grep -ncE "\bmount\b" f5d702a5 -- packages/cli packages/js-sdk packages/python-sdk` → hits in schema/type-gen files, `sandboxApi.ts`, `envd/filesystem/filesystem_connect.py`, `envd/process/process_connect.py`, `volume/client*` — none expose a **host** bind-mount API to SDK users.
16. `git -C upstream/e2b grep -ncE "bind_mount" f5d702a5 -- packages/cli packages/js-sdk packages/python-sdk` → **0 hits**.
17. `git -C upstream/e2b grep -ncE "bindMount" f5d702a5 -- packages/cli packages/js-sdk packages/python-sdk` → **0 hits**.
18. `git -C upstream/e2b show f5d702a5:packages/python-sdk/e2b/sandbox_sync/git.py` (full file read) → a first-class `class Git:` (`f5d702a5:packages/python-sdk/e2b/sandbox_sync/git.py:49`) with a typed `def clone(url, path, branch, depth, username, password, ..., dangerously_store_credentials)` method at `f5d702a5:packages/python-sdk/e2b/sandbox_sync/git.py:256`.
19. `git -C upstream/e2b show f5d702a5:packages/python-sdk/e2b/sandbox_async/git.py` (full file read) → identical async twin, `class Git:` at line 49.
20. `git -C upstream/e2b show f5d702a5:packages/js-sdk/src/sandbox/git/index.ts` (full file read) → `export class Git` (`f5d702a5:packages/js-sdk/src/sandbox/git/index.ts:286`) with `async clone(url, opts?: GitCloneOpts)` at `f5d702a5:packages/js-sdk/src/sandbox/git/index.ts:296`; `GitCloneOpts` types `path`, `branch`, `depth`, `username`, `password`, `dangerouslyStoreCredentials`.
21. `git -C upstream/e2b grep -n "self.git\|self\.git =\|Git(" f5d702a5 -- packages/python-sdk/e2b/sandbox_sync/main.py packages/python-sdk/e2b/sandbox_async/main.py` → confirms wiring into the `Sandbox` class: `f5d702a5:packages/python-sdk/e2b/sandbox_sync/main.py:126: self._git = Git(self._commands)` and `f5d702a5:packages/python-sdk/e2b/sandbox_async/main.py:130: self._git = Git(self._commands)`.

**The reading:** against the probe's decision rule (resolves to `clone` if a first-class
git-source API exists; `upload` if the only paths are write/read/list/watch over the envd wire
plus an ad hoc file-write helper, with no git-source API and no host mount), a first-class,
typed, documented `Sandbox.git.clone(url, opts)` method exists in both Python SDKs and the JS
SDK, wired into the `Sandbox` class, with rich options (`branch`, `depth`, `path`, credential
handling) and its own error types (`GitAuthException`, `GitUpstreamException`). **The reading is
`clone`.**

**Mechanism nuance, carried forward regardless of the reading:** the SDK's `clone()` is
implemented by running `git clone` through the sandbox's own command runner (`Commands.run`)
rather than through a dedicated envd wire RPC — the envd filesystem service (command 5 above) has
no clone/upload RPC of its own. This is a mechanism detail, not a reclassification: the API
surface a caller uses is still first-class and typed, which is what the decision rule turns on.

**Checkpoint verdict (Task 2, human decision):** **admit** — `filesystem_sync` enters the
canonical key set as the eighth key, appended last. E2B's cell: **`clone`**, taken as-probed.

### Deferred keys (EVOC-03, D-13)

Three entries, each stating its unmet bar and a named re-entry condition. Named candidates going
stale is acceptable — an ADR is a dated record.

- **`per_call_granularity`** — one clean instance only (a harness-internal, per-tool-call
  sandbox). Needs a second per-call instance to clear the bar; candidates are other harnesses'
  internalized sandboxes (in the shape of codex's Seatbelt/Landlock/bwrap invocation-per-tool-call
  pattern, see `notes/03-execution-environments/index.md`'s relationship vocabulary).
- **`workload_identity`** — technically two instances but thin; strengthen via the Cloudflare
  Sandbox SDK read planned for Phase 8. **Vercel false-friend note, recorded now:**
  `VERCEL_OIDC_TOKEN` authenticates to Vercel's own control plane rather than federating identity
  to third-party services — it must **not** be counted as an instance when this key is
  reconsidered.
- **Isolation-mechanism depth** — the jailer / cgroup-enforcement / syscall-coverage grade of
  detail, as opposed to the primitive label `isolation_primitive` already carries. Source-gated;
  re-enters on the Cloudflare Sandbox SDK read, because that substrate is source-readable.

Nothing is migrated here, unlike **ADR-0014**: category 3 has no pre-existing top-level feature
keys to re-home — this block starts from zero.

## Cell-value grammar

This block introduces structure ADR-0013 had no equivalent of.

1. **Evidence grades attach as a suffix string inside the cell value** — a mechanism value
   followed by a parenthesised grade, and a boolean-shaped value followed by one likewise (e.g.
   `gvisor-runsc (testimony)`, `false (source)`). Grade vocabulary: `SOURCE`, `OBSERVED`,
   `TESTIMONY`, `INFERENCE`, plus `OPAQUE`. An ungraded cell defaults to `SOURCE` **only** on a
   deep-dive report; a survey-depth report must grade every cell explicitly. This anticipates the
   Phase 7 rule for Modal's cells (`depth: survey`).
2. **Enum regime is declared per key in the registry entry**, restating the closed-versus-open
   split the Decision section fixed above. Changing a closed lattice costs a registry edit with
   dated rationale; an open-descriptive family may gain a new specific value the moment a report
   verifies one.
3. **The three mechanism keys — `isolation_primitive`, `snapshot_model`, `credential_model` —
   use a structured `family:specific` colon tag.** The family half is a closed lattice; the
   specific half is open-descriptive and coined by the report that introduces it. The specific
   half is **optional per cell**: a bare family value is legal when only the shape is known — how
   a future cell avoids overclaiming when a tier's primitive is documented but not verified (e.g.
   a bare `checkpoint-restore` where the specific gVisor internals are TESTIMONY, not
   source-verified — Modal's `snapshot_model` cell above). Worked values already in evidence:
   `hardware-virt:firecracker-microvm`, `userspace-kernel:gvisor-runsc`,
   `create-is-resume:uffd-lazy-paging`, `broker-relayed:spiffe-jwt-svid`. This beat the two-key
   family-plus-label alternative: family would be a function of the label, a derivable duplicate
   that can silently drift out of agreement with it. `self_host`, `egress_default`,
   `egress_controls`, and `filesystem_sync` stay **plain enums** — D-11 names exactly three
   mechanism keys for the colon-tag grammar — with mechanism nuance living in the registry
   entry's `note`.
4. **A cell may be multi-valued** — a YAML list of tag strings — and a list means **conjunction
   only**: the product genuinely offers every listed value (e.g. a future environment
   documenting both `mount` and `upload` filesystem-sync paths). Uncertainty is never expressed
   by listing alternatives; uncertainty is carried by the grade suffix and by the bare-family
   form. Each list element carries its own grade suffix.

**Zero-renderer-change claim.** `_feature_row()` (`scripts/build-tool-index.py:330`) already
routes a string cell to the trailing `else` branch, which renders it as inline code, and already
joins a list cell with commas (`", ".join(...)`). Suffix-graded strings (`` `gvisor-runsc
(testimony)` ``) and conjunction lists therefore render correctly with **no generator change
beyond the block addition Phase 6 makes anyway.**

The colon-tag grammar is available precedent that another block **may** adopt through its own
future decision. This ADR does **not** retrofit `features`, `workflow_features`,
`memory_features`, or `model_features` — their value vocabularies were fixed by their own ADRs.

## Consequences

- `comparisons/features.md` will gain a category-3 matrix section in Phase 6; rows populate as
  reports are classified (two in Phase 7 — E2B and Modal — three more in Phase 8).
- The generator's `known_blocks` set literal at `scripts/build-tool-index.py:65` grows by one
  entry, and a new `ENVIRONMENT_FEATURE_KEYS` constant joins the derived per-block key lists
  alongside `MEMORY_FEATURE_KEYS` (line 83) and `MODEL_FEATURE_KEYS` (line 90), following the
  same registry-filter shape. **Ordering constraint:** the registry YAML entries and the
  `known_blocks` edit cannot ship independently — the registry is loaded at module import time,
  and an unregistered block name exits the generator before any command runs — so Phase 6 lands
  both in one commit.
- The render section mirrors the memory block's, with the simpler single-predicate row filter
  (`category == 3`, no `type ==` second predicate — unlike `memory_features`'s `category == 5
  and type == "memory"`).
- **`render_environments()` (`build-tool-index.py:546`) and `comparisons/environments.md` are
  NOT touched by this block.** That demand-side pipeline stays at bucket granularity; wiring it
  to instance granularity is a separate future decision, contingent on a category-3 `type:`
  vocabulary (see Decision scoping rule 1).
- Existing matrices are unaffected by construction — no report loses a row and no existing key
  changes meaning.
- Precedent recorded: a per-category supply-side block is now the pattern, and the colon-tag
  cell grammar is available to other blocks via their own future decisions.
