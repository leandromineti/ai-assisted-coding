# Pitfalls Research

**Domain:** Git-log parsing / shelling-out CLI tools (Python, git-analytics)
**Researched:** 2026-07-28
**Confidence:** MEDIUM (cross-referenced against official git-scm.com documentation + established community knowledge; no single authoritative "gotchas" post-mortem exists for this exact niche, so most claims are verified against primary docs rather than a single canonical source)

## Critical Pitfalls

### Pitfall 1: Binary files break naive numeric parsing of `--numstat`

**What goes wrong:**
For binary files, `git log --numstat` emits two dashes instead of numbers: `-\t-\tpath/to/image.png` (confirmed against official git-scm.com diff docs). A parser that does `added, deleted, path = line.split("\t"); int(added)` crashes with `ValueError: invalid literal for int() with base 10: '-'` the first time it hits a repo containing a committed binary file (image, PDF, compiled artifact, lockfile git treats as binary, etc.).

**Why it happens:**
Developers test against their own text-only repo, never trip the binary case, and ship. Binary files are common in the wild (README screenshots, `.png` assets, `.jar`/`.whl` files, generated PDFs) even in repos that look "code-only" at a glance.

**How to avoid:**
Explicitly branch on `added == "-" or deleted == "-"` before calling `int()`. Decide the product behavior up front — count the file as touched but contribute 0 to the lines-added/deleted totals (recommended; matches what `git log --shortstat` does for its aggregate) — and document the choice in the README so users aren't surprised their totals don't match `wc -l` on a diff.

**Warning signs:**
Works fine on the tool's own git history (Python + tests + README, no binaries) but throws on the first real-world target repo. A test fixture repo with zero binary files gives false confidence.

**Phase to address:**
Core parsing implementation — needs a dedicated unit test with a fixture commit containing a binary file.

---

### Pitfall 2: `git log` shows NO diff at all for merge commits by default

**What goes wrong:**
The intuitive assumption is "merge commits might double-count lines from both parents." The actual default behavior is the opposite and more surprising: plain `git log --numstat` (with no `-m`, `-c`, `--cc`, or `--first-parent` diff-merges override) prints **zero numstat lines** for merge commits — the commit header appears, then nothing, then the next commit. A naive line-based parser that assumes "every commit is followed by at least one numstat line, or the commit added/removed 0 lines" will silently treat merges as no-op commits, which is usually *correct* for a contributor-activity summary (avoids inflating a person's stats just because they clicked "merge") but is easy to get backwards if untested, and easy to misdiagnose as "my parser is broken" when a merge-heavy repo returns fewer numstat blocks than commit headers.

**Why it happens:**
`git diff`/`git show` default to combined-diff (`-c`) for a single merge commit, but `git log` walking a whole history defaults to **no diff shown** for merges unless you opt in — a genuine, non-obvious asymmetry between the two commands that trips up people who tested behavior with `git show <merge-sha>` and assumed `git log` behaves the same way.

**How to avoid:**
Decide explicitly and document it: for a per-author line-count summary, the standard/expected choice is to leave merges diff-less (git's default) so merge commits count toward "commits" but not toward "lines added/deleted" — this matches what most git-analytics tools (`git shortlog`, GitHub's contributor graphs) do and avoids double-counting work that already has its own dedicated commits. If a future feature wants merge-commit diffs, use `--first-parent` (also fixes topology for linear history) rather than `-m` (which duplicates the diff once per parent).

**Warning signs:**
Total lines-added across all authors doesn't match `git log --numstat` line count expectations on a repo with many merges; commit count per author looks right but line totals look "too low" on branches with lots of PR-merge commits.

**Phase to address:**
Core parsing implementation — write a fixture repo with at least one merge commit and assert the parser doesn't crash and doesn't double count.

---

### Pitfall 3: Shallow clones silently produce wrong "first commit" / commit counts

**What goes wrong:**
CI checkouts default to shallow history — GitHub Actions' `actions/checkout` uses `fetch-depth: 1` by default, giving a repo with exactly one commit of history even though the real project has thousands. `git log` on a shallow clone runs without error and returns a plausible-looking (but truncated) table: wrong "first commit date," undercounted commits per author, sometimes only one author visible at all. There is no error — this is the most dangerous kind of pitfall because the tool looks like it worked.

**Why it happens:**
The tool is developed and tested against full local clones, where this never surfaces. It only appears when someone runs the tool inside CI or against a clone made with `--depth N`.

**How to avoid:**
Check `git rev-parse --is-shallow-repository` (prints `true`/`false`) before summarizing, and either warn loudly on stderr ("warning: shallow repository, results may be incomplete — run `git fetch --unshallow`") or fail with a clear non-zero exit depending on how strict the tool wants to be. At minimum, surface it — never present shallow-clone output as if it were the full history.

**Warning signs:**
Numbers look suspiciously small/round for a repo everyone knows is old; "first commit date" for every author looks nearly identical (clustered around the shallow cutoff).

**Phase to address:**
Core parsing / error-handling phase — add the shallow-repo check alongside the "not a git repo" and "empty repo" checks, since all three are pre-flight validations of the same kind.

---

### Pitfall 4: Non-UTF-8 author names and commit messages cause decode crashes or mojibake

**What goes wrong:**
Git commit objects don't force UTF-8 — the encoding is whatever the committer's tool wrote (recorded, if at all, in the commit's `encoding` header via `i18n.commitencoding`). Old commits, commits from Windows machines with legacy locales, or commits with accented/non-Latin author names (e.g. "José", "Müller", CJK names) can be Latin-1, Shift-JIS, or arbitrary bytes. A Python `subprocess.run(..., text=True)` call without an explicit encoding decodes using the platform's default locale encoding and will raise `UnicodeDecodeError` on the first non-UTF-8 byte sequence it meets, crashing the whole tool on one bad commit out of thousands.

**Why it happens:**
Developers test on their own machine/locale where everything happens to be UTF-8, so the crash only appears against a repo with older or internationally-authored history.

**How to avoid:**
Capture subprocess output as bytes (`text=False`/no `encoding=` arg) and decode explicitly with `errors="replace"` (or `"surrogateescape"` if byte-fidelity matters), so a single malformed name degrades gracefully instead of aborting the whole run. Alternatively, force git itself to normalize by passing `--encoding=UTF-8` to `git log` (git re-encodes the log message using the recorded `commitencoding`, falling back to UTF-8) — but this only affects the log body, not necessarily author name/email which git does not re-encode.

**Warning signs:**
Tool works on every repo the author tries, then crashes on a client/legacy/open-source repo with `UnicodeDecodeError` deep in `subprocess` or `str.decode`.

**Phase to address:**
Core parsing implementation — pick and document the decode strategy once, apply it to every subprocess read.

---

### Pitfall 5: Locale-dependent git output breaks both error detection and date parsing

**What goes wrong:**
Git's diagnostic messages (`fatal: not a git repository...`, `fatal: your current branch 'main' does not have any commits yet`) and some date formats are localized based on the user's `LANG`/`LC_ALL` environment. A tool that does `if "not a git repository" in stderr` to classify errors, or that parses `--date=default` output with an English month-name regex, silently misclassifies errors or fails to parse dates on any machine set to a non-English locale (common on shared CI runners, non-US developer machines).

**Why it happens:**
Locale-dependent behavior is invisible during solo development on an English-locale machine and only manifests on other people's machines or in CI images with different locale defaults.

**How to avoid:**
Force a deterministic environment for every `git` subprocess call: pass `env={**os.environ, "LC_ALL": "C"}` (or `"C.UTF-8"` for stable UTF-8 handling) so error text and any human-readable date fields are always in the stable "C" locale. Prefer parsing errors by **exit code first**, falling back to stderr text only as a secondary signal. For dates, always request an unambiguous machine format explicitly — `--date=iso-strict` (or `%aI`/`%cI` in a `--pretty=format`) — never rely on the locale-default date string.

**Warning signs:**
Tool works in the developer's terminal but fails or misbehaves in CI, Docker containers, or a colleague's machine with a different `LANG`.

**Phase to address:**
CLI & error-handling phase — set the subprocess environment once in the git-invocation helper, used by every call site.

---

### Pitfall 6: Empty-repo and not-a-repo detection collide if done by string-matching stderr

**What goes wrong:**
Two very different situations both produce a `git log` failure with a similar-looking `fatal:` prefix: (a) the path is not a git repository at all, and (b) the path *is* a valid git repository but has zero commits (an "unborn branch" — HEAD points at a branch ref that doesn't exist yet). If both are detected by grepping stderr for a substring, small git-version differences in wording (the message text has changed across git releases) or locale (see Pitfall 5) can misroute one case into the other's error message, giving the user a confusing/wrong diagnostic for a genuinely common case (a freshly `git init`'d repo — which is exactly the state of this project's own repo before its first commit).

**Why it happens:**
Both cases surface only as a git process exit code + stderr text; there's no separate flag or exit code that distinguishes them cleanly across all git versions.

**How to avoid:**
Do explicit, purpose-built pre-flight checks instead of parsing the `git log` failure after the fact:
1. Not-a-repo check: `git -C <path> rev-parse --is-inside-work-tree` (or `--git-dir`) — non-zero exit / stderr means "not a repository."
2. Empty-repo check: `git -C <path> rev-parse --verify HEAD` — fails with a distinct, well-known exit code (128) when HEAD is unborn; succeeds (repo has ≥1 commit) otherwise.
Running these as dedicated, single-purpose commands is far more robust than trying to disambiguate free-text `git log` error output, and matches the project's own two explicit requirements ("clear error for not-a-repo" and "clear error for empty repo") — they need two different checks, not one shared string match.

**Warning signs:**
"Not a git repository" error shown for a repo that is valid but empty, or vice versa; error message wording changes (and breaks) after upgrading the system's git version.

**Phase to address:**
CLI & error-handling phase — this maps directly to two of the project's stated Active requirements.

---

### Pitfall 7: Rename detection changes the numstat column format mid-stream

**What goes wrong:**
When rename detection is active (either because the user's global/repo `diff.renames` config is set to `true`/`copies`, or because `-M`/`--find-renames` is passed), `--numstat` output for a renamed file looks like `3\t1\tarch/{i386 => x86}/Makefile` (official git docs example) instead of the plain `added\tdeleted\tpath` triple. A parser that always expects exactly 3 tab-separated fields, or that treats the third field as a literal filesystem path, gets a mangled/misleading path and — worse — this behavior is **not under the tool's control by default**, since `diff.renames` can already be `true` in a user's global gitconfig, meaning the exact same tool can behave differently on two machines with identical repo contents.

**Why it happens:**
Rename detection is a diff-generation feature, not a `git log` default the tool author necessarily thinks about, and it depends on ambient config the tool doesn't control.

**How to avoid:**
Pass `--no-renames` explicitly on every invocation to pin deterministic behavior regardless of the user's git config (this project only needs added/deleted line counts, not filenames, so there is no reason to leave rename detection on — it only adds parsing risk for zero benefit here).

**Warning signs:**
Line counts or file paths look wrong specifically for authors who did a lot of file moves/reorganization; behavior differs between two otherwise-identical clones.

**Phase to address:**
Core parsing implementation — add `--no-renames` to the fixed `git log` invocation and add a fixture commit that renames a file to prove it's neutralized.

---

### Pitfall 8: Spawning a `git` subprocess per commit instead of one streaming call

**What goes wrong:**
An intuitive-but-wrong implementation strategy: `git log --pretty=%H` to list commit hashes, then loop and call `git show <sha> --numstat` (or similar) once per commit to get its stats. Process-spawn overhead (fork/exec + git's own startup cost) dominates runtime once a repo has more than a few hundred commits, turning what should be a sub-second operation into a multi-minute one on a repo with tens of thousands of commits.

**Why it happens:**
Per-commit looping is the natural way to think about "for each commit, get its stats" when translating the requirement into code, and it's not obviously wrong until tested against a real-sized repo — small test fixtures (10-20 commits) hide the cost completely.

**How to avoid:**
Always issue exactly one `git log` invocation that already includes `--numstat` (plus a `--pretty=format:` header per commit) and stream-parse its combined stdout in a single pass. This is the standard pattern for git-analytics tooling — one process, one pass, no per-commit subprocess spawning.

**Warning signs:**
Tool feels instant on the project's own small repo but takes visibly long (seconds to minutes) on a real-world target repo with thousands of commits.

**Phase to address:**
Core parsing implementation — the chosen `git log` invocation shape is a foundational design decision, worth locking in before writing the parser.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|--------------------|-----------------|------------------|
| Split numstat lines by `str.split("\t")` assuming exactly 3 fields, no binary/rename handling | Fast to write, works on the tool's own repo | Crashes (`ValueError`) or mis-parses on binary files or renamed files in real-world repos | Never for shipped code — always at least handle the binary `-` case; combine with `--no-renames` to make the 3-field assumption safe |
| Detecting "not a repo" / "empty repo" by substring-matching `git log`'s stderr | No extra subprocess calls, quick to implement | Breaks across git versions and locales; conflates two distinct error states | Only as a temporary spike/prototype; replace with dedicated `rev-parse` pre-flight checks before the "clear error" requirements are considered done |
| Using `subprocess.run(cmd, shell=True)` with an f-string containing the repo path or `--since` value | Slightly less code than an argument list | Shell-injection risk if the path/date string ever comes from an untrusted source (e.g. wrapped in a web service later); also breaks on paths with spaces/quotes | Never — always pass a list of arguments, no `shell=True` |
| Loading the entire `git log --numstat` output into memory via `subprocess.run(capture_output=True)` before parsing | Simpler code, no streaming logic | Memory spike proportional to repo size; noticeable on huge repos (hundreds of MB of log text) | Acceptable for a v1 CLI targeting typical project-sized repos (thousands, not millions, of commits) — revisit with `Popen` + line-streaming only if profiling shows it matters |

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|-----------------|-------------------|
| `git` CLI (external binary) | Assuming `git` is always on `PATH` and any installed version supports the flags used (e.g. `--diff-merges`, some `--date=` variants are relatively recent) | Fail fast with a clear message if `git` isn't found (`shutil.which("git")` or catch `FileNotFoundError` from `subprocess`); stick to flags available since git 2.x widely-deployed versions, and note the minimum git version in the README |
| `git` CLI env/locale | Inheriting the caller's ambient `LANG`/`LC_ALL`, making output format/wording non-deterministic | Explicitly set `LC_ALL=C` (or `C.UTF-8`) in the subprocess `env` for every git invocation |
| `git` CLI encoding | Trusting Python's default text-mode decoding for subprocess stdout | Decode explicitly with a known/forced encoding and an explicit error-handling strategy (`errors="replace"`) rather than relying on locale defaults |

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|-----------------|
| Per-commit subprocess spawning (loop + `git show`/`git log` per SHA) | Feels instant on a demo repo | Single `git log --numstat` call covering the whole range; stream-parse once | Noticeable slowdown starts in the hundreds of commits; painful by a few thousand |
| Buffering full stdout via `capture_output=True` on very large repos | High memory use, slow "first output" latency | Stream via `Popen(stdout=PIPE)` and iterate lines if targeting huge (100k+ commit) repos | Repos in the tens/hundreds of thousands of commits range (e.g. monorepos, long-lived OSS projects) |
| Walking full history when only a recent window is needed | Slow runs even though `--since` is available | Always push `--since`/date-range filters down into the `git log` call itself rather than filtering in Python after the fact | Any repo where the full history is much larger than the requested window |

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Building the `git` command as a shell string with f-string interpolation of the repo path or `--since` value, run with `shell=True` | Shell/argument injection if the path or date string ever comes from an untrusted source (config file, web wrapper, etc.) | Always call `subprocess.run([...args as list...])` with `shell=False` (the default); never interpolate untrusted input into a shell string |
| Passing an untrusted/attacker-controlled path to `git -C <path>` without validating it resolves inside an expected boundary (relevant only if this CLI is ever wrapped by a service that accepts a path from a remote caller) | Path traversal reading git history from unintended locations | Out of scope for a purely local CLI invoked by the user directly; flag explicitly if a future phase adds a network-facing wrapper |

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|--------------|-------------------|
| Printing git's raw stderr (`fatal: ...`) directly as the tool's own error output | Confusing, git-jargon-heavy message instead of an actionable one; also breaks the "clear error" requirement | Catch specific pre-flight failures (not-a-repo, empty-repo, shallow-repo) and print the project's own plain-language message, reserving raw git stderr for an unexpected/unhandled case only |
| Returning an empty table silently when `--since` excludes all commits vs. when the repo truly has no commits | User can't tell "wrong date filter" from "broken tool" from "genuinely empty repo" | Distinguish the cases: empty repo → the dedicated non-zero exit error; valid repo + `--since` window with zero matching commits → a table with a header row and an explicit "no commits in this range" note, not silence |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Binary file handling:** Often missing — verify with a fixture commit that adds a binary file (e.g. a small `.png`); confirm the tool doesn't crash and produces a sane (0 or flagged) line count for it.
- [ ] **Merge commit handling:** Often missing an explicit decision — verify with a fixture repo containing at least one real merge commit (two branches merged, not just `--no-ff` of a fast-forward) and confirm line totals aren't silently wrong or the parser doesn't choke on the header-with-no-numstat-lines case.
- [ ] **Non-ASCII author names:** Often missing — verify with a commit authored using a non-ASCII name (e.g. `git commit --author="José Müller <jose@example.com>"`) and confirm no crash and no mojibake in table/JSON output.
- [ ] **Empty repository:** Often missing a *distinct* code path from "not a repo" — verify against a literal `git init`-only repo (zero commits) and confirm the exact required exit code + message, not a raw traceback.
- [ ] **Shallow clone:** Often entirely unconsidered — verify by running the tool against a `git clone --depth 1` copy of a repo with real history and confirm it warns/fails clearly rather than silently reporting truncated data as complete.
- [ ] **Rename-heavy history:** Often missing — verify with a fixture commit that renames a file (`git mv`) under both `diff.renames=true` and default config, confirming identical, non-crashing output either way (implies `--no-renames` is actually being passed).
- [ ] **Large repo performance:** Often missing until it's too late — run once against a repo with several thousand real commits (e.g. a well-known OSS project clone) before considering the tool "done," to catch spawn-per-commit or full-buffering issues.

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|-----------------|------------------|
| Binary-file `int()` crash shipped to users | LOW | Add the `"-"` guard, add a regression test with a binary fixture commit, patch release |
| Merge-commit double-count or miscount discovered after users trust the numbers | MEDIUM | Clarify and document the intended semantics (git default: no diff for merges), add a fixture test, release with a changelog note since totals may shift for merge-heavy repos |
| Shallow-clone silent wrong output already relied upon (e.g. in a CI report) | MEDIUM | Add the `--is-shallow-repository` guard, re-run affected reports after an `unshallow` fetch, flag historical reports as suspect |
| Locale-dependent error misclassification shipped | LOW | Force `LC_ALL=C` in the subprocess env, switch error detection to exit-code-first, patch release |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|-------------------|----------------|
| Binary files break numeric parsing | Core parsing implementation | Fixture repo with a committed binary file; assert no crash, defined 0/flagged line count |
| Merge commits show no diff by default | Core parsing implementation | Fixture repo with a real merge commit; assert commit is counted, lines aren't double-counted or crashed on |
| Shallow clones silently truncate history | Core parsing / error-handling phase | `git clone --depth 1` fixture; assert warning or clear failure, not silent partial data |
| Non-UTF-8 author names/messages | Core parsing implementation | Fixture commit with a non-ASCII author name; assert no `UnicodeDecodeError` |
| Locale-dependent error text and dates | CLI & error-handling phase | Run test suite with `LANG=de_DE.UTF-8` (or similar) in CI; assert identical behavior to `LC_ALL=C` run |
| Empty-repo vs not-a-repo conflated | CLI & error-handling phase | Two dedicated fixtures (bare `git init`, and a plain non-repo directory); assert distinct exit codes/messages for each — this directly verifies two of the project's stated Active requirements |
| Rename detection changes numstat columns | Core parsing implementation | Fixture commit with a `git mv` rename under `diff.renames=true`; assert identical output to the non-rename case |
| Per-commit subprocess spawning | Core parsing implementation (design decision) | Benchmark against a multi-thousand-commit repo before considering the phase done; single `git log` invocation, not a loop |

## Sources

- [git-scm.com — git-log documentation](https://git-scm.com/docs/git-log) — official; confirmed `--first-parent` changes the default `--diff-merges` behavior for merge commits (implying a distinct non-default state exists for plain `git log`).
- [git-scm.com — git-diff documentation](https://git-scm.com/docs/git-diff) — official; confirmed verbatim: "For binary files, outputs two `-` instead of saying `0 0`" and the rename-in-numstat example `3	1	arch/{i386 => x86}/Makefile`.
- [git-scm.com — diff-generate-patch documentation](https://git-scm.com/docs/diff-generate-patch) — official; confirmed combined-diff (`-c`/`--cc`) is git-show/git-diff's default for a single merge commit (distinct from `git log`'s history-walk default).
- [Atlassian — Aliasing authors in Git](https://www.atlassian.com/blog/developer/aliasing-authors-in-git) — community; `.mailmap` mechanics for author-identity merging (relevant background for the project's explicitly out-of-scope identity-merging feature).
- [GitHub — gitpython-developers/GitPython issue #237](https://github.com/gitpython-developers/GitPython/issues/237) — community bug report; concrete example of a UTF-8-encoded-name crash in a mature Python git-wrapping library, corroborating the encoding pitfall.
- General community consensus (Stack Overflow / blog posts surfaced via search, not individually authoritative but consistent across multiple independent sources): forcing `LC_ALL=C` for scripted git output; avoiding repeated subprocess spawning per commit; using `rev-parse --is-inside-work-tree` / `--verify HEAD` for repo-state pre-flight checks rather than string-matching error output.
- Shallow-clone-in-CI behavior (GitHub Actions `actions/checkout` default `fetch-depth: 1`) is treated here as established platform-documented behavior rather than a search finding — flagged MEDIUM confidence since it wasn't independently re-verified in this pass, but is high-value enough to include given this tool's likely usage in CI pipelines.

---
*Pitfalls research for: git-log parsing CLI (Python, stdlib subprocess)*
*Researched: 2026-07-28*
