# Stack Research

**Domain:** Single-purpose Python CLI (git contributor-activity summary)
**Researched:** 2026-07-28
**Confidence:** MEDIUM-HIGH (constraint-driven stack; version facts are time-sensitive web data, core mechanism verified against official git docs)

## Context Recap

`gitwho` is a single-file, stdlib-only Python CLI that shells out to `git log`, aggregates per-author commit/line stats, and prints a table or `--json`. This is not a "pick a framework" domain — the project constraint (`Python 3, standard library only unless something forces otherwise`) already answers most of the stack questions. The research below exists to (a) confirm nothing forces a dependency, (b) pin down the exact stdlib mechanisms and git invocation pattern, and (c) recommend a dev-only test stack that doesn't ship with the tool.

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.11+ floor, developed/tested on 3.14.x | Runtime | 3.14.6 is current stable as of mid-2026 (3.15 is alpha, due Oct 2026); 3.11 is a safe minimum — 3.9 is already past end-of-life and 3.10 is nearing EOL in Oct 2026, so requiring 3.11+ avoids shipping something that breaks on an EOL interpreter without over-constraining. (MEDIUM — version numbers are time-sensitive web facts, not directly fetched from python.org) |
| `argparse` | stdlib (no version to pin) | CLI argument parsing: repo path positional, `--since`, `--json` | The project constraint is stdlib-only; `argparse` is the only option among the three mainstream CLI libraries (`argparse`/`click`/`typer`) that ships with Python. It has handled positional args, optional flags, and boolean flags since Python 3.2 — more than sufficient for this tool's four options. (HIGH — official stdlib module, directly matches stated constraint) |
| `subprocess` | stdlib | Shell out to `git log` and capture stdout/stderr | This *is* the architecture per `PROJECT.md`'s "shell out to git" decision. `subprocess.run(..., capture_output=True, text=True)` is the standard modern pattern (replaces the older `Popen`/`check_output` idioms). (HIGH — official stdlib module) |
| `json` | stdlib | `--json` output mode | Directly serializes the same per-author records used for the table; no reason to reach for anything else for flat, small output. (HIGH) |
| `dataclasses` | stdlib | Per-author record type (`commits`, `lines_added`, `lines_deleted`, `first_commit`, `last_commit`) | Gives typed, self-documenting records with less boilerplate than a plain dict, without adding a dependency (available since 3.7). Keeps the aggregation code and the table/JSON renderers reading from one clear shape. (HIGH) |
| `collections` (`defaultdict`) | stdlib | Aggregate stats per author while streaming `git log` output | Accumulate into `defaultdict(lambda: ...)` keyed by author identity as you parse each commit block, then sort once at the end — avoids a second pass over the data. (HIGH) |

### Supporting Libraries (dev-only, not shipped)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pytest` | 9.1.1 (latest as of June 2026; 9.x line) | Test runner for the project's required test suite | `PROJECT.md` requires tests, but tests are a *development-time* dependency, not something the shipped single-file script imports — so recommending it doesn't violate the stdlib-only runtime constraint. `pytest`'s fixture model and plain-`assert` reporting cut a lot of boilerplate versus `unittest.TestCase` for testing subprocess-parsing logic and CLI output formatting. (MEDIUM — cross-checked against pypi.org and pytest's own release-announcement docs surfaced in search results) |
| `unittest` | stdlib | Fallback test runner if the "stdlib only" constraint is read to include dev dependencies | Use instead of `pytest` only if the project wants a genuinely zero-install clone-and-run experience (`python -m unittest`) with no `pip install` step at all, even for contributors running tests. Verbose relative to `pytest` (class-based, `self.assertEqual` instead of `assert`), but ships with Python. (HIGH — official stdlib module) |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `pytest` | Run the test suite | `pytest -q`; use `tmp_path` fixture + `subprocess.run(["git", "init", ...])` to build throwaway repos for fixtures (empty repo, single-commit repo, repo with binary files) rather than mocking `git` output — real `git log` output is the correctness target per `PROJECT.md`. |
| `ruff` (optional) | Lint/format | Not required by the project's constraints, but worth a one-line mention: a single-file script benefits from a formatter/linter more than from any runtime library. Skip if the "small, minimal" ethos should extend to tooling too — this is a nice-to-have, not a recommendation to add as a hard requirement. |

## Installation

```bash
# Shipped tool: zero installation — stdlib only, runs with any Python 3.11+
python3 gitwho.py [path] [--since DATE] [--json]

# Dev-only, for running tests
pip install pytest

# Or, if avoiding any pip install for tests too:
python3 -m unittest discover
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|--------------------------|
| `argparse` | `click` / `typer` | Only if the project scope grows to multiple subcommands, shell-completion, or a much larger option surface where `argparse`'s verbosity becomes a real cost — neither applies here, and both add a runtime dependency the project explicitly wants to avoid. |
| `subprocess` + parsing `git log` text output | `GitPython` or `pygit2` | `GitPython` itself shells out to the `git` binary under the hood (no lower-level advantage) and adds a heavyweight dependency and API surface for a task that's four `git log` flags. `pygit2` (libgit2 binding) is a compiled dependency — real overkill, and its stats semantics don't always match `git log --numstat` line-for-line, which matters because `PROJECT.md` defines correctness as "agrees with what git reports." Reach for one of these only if the tool needed to *write* to the repo or walk history structurally (not just summarize it). |
| Hand-rolled table formatting (f-strings + computed column widths) | `tabulate` / `rich` | `rich` is worth it the moment the tool wants color, progress bars, or nested/complex layouts. For a single flat table with five columns, it's a dependency to render what `str.ljust()`/`str.rjust()` already do in ~10 lines. |
| `pytest` | `unittest` | Use `unittest` if "standard library only" is meant to apply even to the dev/test toolchain, not just the shipped script — see Supporting Libraries above. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|--------------|
| `GitPython` | Adds a real dependency to shell out to the same `git` binary you'd call directly; its `Commit.stats` object does extra work and caching that obscures exactly what git reported — undermines the "correctness means agreeing with git" goal. | `subprocess.run(["git", "log", ...])` directly |
| `pygit2` (libgit2) | Compiled/binary dependency, install friction (needs libgit2 system library on some platforms), and its diff-stat computation can diverge from `git log --numstat` in edge cases (renames, binary files) — exactly the edge cases `PROJECT.md` calls out as known risks. | `subprocess` + `git log --numstat` |
| `click` / `typer` | External dependencies for a 4-flag CLI; violates the explicit stdlib-only constraint without a forcing reason. | `argparse` |
| `pandas` | Wildly oversized for aggregating a few hundred/thousand commit rows into per-author sums; adds a large, slow-to-import dependency. | `collections.defaultdict` + manual aggregation |
| `tabulate` / `rich` (for this tool's table output) | Nice-to-have polish, not needed for a fixed 5-column table; adds a dependency for cosmetic gain. | Hand-rolled column-width formatting with f-strings |
| Parsing porcelain `git log` output without a `--pretty=format` delimiter | Default `git log` output (with the commit message body) is not reliably machine-parseable — multi-line commit messages will break naive line-based parsing. | `git log --no-pager --pretty=format:"<delim>%H%x1f%an%x1f%ae%x1f%aI" --numstat` (or similar), using a control character as field separator so it can't collide with commit message content |

## Stack Patterns by Variant

**If the "stdlib only" constraint is meant strictly (including dev tooling):**
- Use `unittest` instead of `pytest`
- Because it removes the last `pip install` from the contributor workflow, matching the spirit of a genuinely zero-dependency, single-file deliverable

**If binary files or renamed files show up in `--numstat` output:**
- `git log --numstat` prints `-\t-\t<path>` for binary files (no numeric line counts) — parse defensively and either skip those lines from the added/deleted sums or count the file as touched without contributing to line totals
- Because `PROJECT.md` explicitly calls this out as a known edge case, and a naive `int()` cast on `-` will crash

**If author identity varies by case or trailing whitespace in `%an`/`%ae`:**
- Normalize (strip, and optionally lowercase email) before using as the aggregation dict key
- Because `.mailmap`-based identity merging is explicitly out of scope for v1, but basic string hygiene isn't the same thing as full identity merging and prevents obviously-wrong double-counting

## Version Compatibility

| Package | Compatible With | Notes |
|---------|------------------|-------|
| Python 3.11+ | `git` any reasonably modern version (2.x, e.g. 2.30+) | `--numstat`, `--pretty=format`, and `%aI` (strict ISO 8601 author date) have been stable in `git log` for well over a decade; no version coupling risk here. |
| `pytest` 9.x | Python 3.9+ | pytest 9.x dropped support for very old Python 3 versions; not a concern given the 3.11+ floor recommended above. |

## Sources

- WebSearch: "current stable Python 3 version release 2026" — python.org, endoflife.date, devguide.python.org surfaced as top results; confidence MEDIUM (search-engine synthesis of official sources, not a direct fetch of python.org itself)
- WebSearch: "pytest latest release version changelog" — pypi.org, docs.pytest.org (release announcements) surfaced; confirmed via `gsd-tools query classify-confidence --provider websearch --package pytest --ecosystem pypi --verified` → MEDIUM
- WebSearch: "Python argparse vs click vs typer small single-file CLI tool stdlib only" — multiple 2025/2026-dated community comparisons (CodeCut, dasroot.net, pythonsnacks), consistent conclusion: argparse is the only stdlib option among the three; confidence MEDIUM (community consensus, not official docs, but the underlying fact — argparse ships with Python, click/typer don't — is objectively verifiable and not in dispute)
- WebFetch: `https://git-scm.com/docs/git-log` (official Git documentation) — confirmed `--numstat` output format, `--pretty=format` placeholders (`%H`, `%an`, `%ae`, `%ad`, `%ai`, `%aI`), and that `--numstat` combines with a custom `--pretty=format` string for machine-parseable per-commit output; confidence HIGH (primary/official source, fetched directly)
- Project constraint (`PROJECT.md`): "Python 3, standard library only unless something forces otherwise" — treated as a hard input, not a research finding

---
*Stack research for: single-purpose git-analytics CLI (Python)*
*Researched: 2026-07-28*
