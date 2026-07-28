# upstream/

Read-only study copies of open-source tools. **Everything here is gitignored** except this
file and `repos.txt` — the clones belong to their own projects and would bury this repo's
history in someone else's commits.

Nothing in here is ever edited. If you want to try a modification, that's an experiment —
it goes in `experiments/`, not here.

## Usage

```sh
./scripts/sync-upstream.sh     # clone what's missing, fast-forward the rest
```

Idempotent. To add a tool, append a `layer|name|url` line to
[`repos.txt`](repos.txt) and re-run.

Clones are **blobless** (`--filter=blob:none`): full commit history and file listings, with
file contents fetched on demand. That keeps `git log`, `git blame`, and
`git log --follow` usable — which matters, because *when* a design appeared is often more
informative than the design itself.

## Where the analysis goes

**Not here.** The clone is the raw material; the writing lives in `notes/`:

| Artifact | Path | Purpose |
|---|---|---|
| Survey entry | `notes/0N-<layer>/<tool>.md` | What it is, its distinguishing bet — from [`notes/_template.md`](../notes/_template.md) |
| Architecture deep-dive | `notes/0N-<layer>/<tool>-architecture.md` | How it's built — from [`notes/_template-architecture.md`](../notes/_template-architecture.md) |

Keeping the two separate matters: the survey entry is what you'd tell someone choosing a
tool; the deep-dive is what you'd tell someone rebuilding it. Different readers, different
half-lives.

## Method

Reading a 100k-star repo end to end is not a plan. What has actually worked:

1. **Entry point first.** Find `main()` / the CLI entry and trace one full request to
   completion. One trace teaches more than a week of browsing.
2. **Then the agent loop.** Every harness has one. Locate it and read it closely — that
   function *is* the product.
3. **Then context assembly.** What gets loaded, when, what's dropped under pressure. This
   is where tools differ most and document themselves least.
4. **Then the boundaries.** Tool definitions, permission checks, sandbox calls — the seams
   where the taxonomy's layers show up in real code.
5. **Read `git log` on the loop file.** The commit that introduced a retry, a guard, or a
   truncation is usually a bug report in disguise.

Record what surprised you. Confirmations of what you already assumed aren't worth the disk
space.

## Note on closed tools

Claude Code, Cursor, Windsurf, Devin, and Copilot can't be cloned. They're studied by
observation — behavior, docs, telemetry, and what leaks through their config surfaces. Say
so explicitly in any comparison: an architecture claim about a closed tool is inference,
and belongs marked as such.
