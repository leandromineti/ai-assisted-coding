# Layer 5 — Execution environments

`checked: 2026-07-28`

Where the agent's code actually runs, and what it can damage. See
[`../../taxonomy.md`](../../taxonomy.md).

The most-ignored layer, because it's invisible until it fails.

## Seed inventory

| Environment | One-line | Isolation | Setup cost |
|-------------|----------|-----------|------------|
| **Host machine** | No isolation. The default, and the reason people are nervous about autonomy. | None | Zero |
| **git worktrees** | Parallel checkouts of one repo; lets several agents work without collision. | Filesystem only — same machine, same network, same credentials | Low |
| **Devcontainers** | Declarative dev environment in a container; reproducible toolchain. | Process + filesystem | Medium |
| **Docker** | General container isolation, hand-rolled. | Process + filesystem + network | Medium |
| **E2B** | Remote sandboxes purpose-built for agent code execution. | Full VM/remote | Low, metered |
| **Modal** | Serverless remote compute, used as an agent sandbox. | Full remote | Low, metered |
| **Cloudflare Sandbox SDK** | Sandboxed execution on Workers; preview URLs, code interpreter. | Full remote | Low, metered |
| **Bundled (Devin, cloud Codex, Claude Code web)** | The harness ships its own sandbox; not separately selectable. | Vendor-defined | None — and no choice |

## The trap worth documenting first

Isolation that hides files the agent needs is a **layer-5 problem that presents as a
layer-2 bug**.

`git worktree add` checks out only *tracked* files. Anything gitignored — `node_modules/`,
build output, `.env*`, and (on GSD-convention projects) `.planning/` and `CLAUDE.md` — is
simply absent from a fresh worktree. The agent then can't see its own plan or run the
project's tooling, and a well-behaved one refuses rather than fabricating.

The instinct to fix it by un-ignoring things is wrong — secrets and build artifacts must
stay ignored, and un-ignoring the planning directory alone still leaves a worktree whose
tooling can't run. Two fixes that hold up:

1. **Disable worktrees.** Executors run sequentially against the main checkout, which sees
   everything. Simplest; costs intra-wave parallelism.
2. **Bootstrap each worktree.** As the agent's first action, link the gitignored
   dependencies in from the main checkout — `node_modules`, build output, `.env*`, the
   planning directory, the rules file. Keeps parallelism.

Two caveats found the hard way on fix 2 (personal experience, mid-2026):

- **Symlinked `node_modules` breaks `next dev`.** Turbopack rejects it outright — *"Symlink
  node_modules is invalid, it points out of the filesystem root."* To run a dev server from
  a worktree, use a hardlink clone instead: `cp -al ../main/node_modules ./node_modules` —
  instant, no duplicate disk. Symlinks remain fine for `tsc`, `vitest`, and Prisma.
- **The linked directories must be *fully* untracked.** One stray committed file inside
  them and the checkout shadows your symlink with a partial directory.

This is the clearest evidence I have that the layer is real: nothing about the harness or
the model was broken.

## Axes that matter

- **Blast radius** — what can it destroy? Files, the repo, the machine, production?
- **Fidelity** — does the project's tooling actually run in there, unmodified?
- **Parallelism** — can N agents work at once without colliding?
- **Startup cost** — per-run overhead, in seconds and in dollars.
- **Credential exposure** — what secrets are reachable from inside?

## Open questions

- Isolation and fidelity trade off directly. Where's the useful middle?
- Does parallel multi-agent work actually pay, once the environment-bootstrap tax is
  counted honestly?
- How much autonomy would a genuinely disposable environment justify? Is sandboxing the
  real unlock for hands-off agents, rather than better models?
