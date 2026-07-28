# Project Research Summary

**Project:** gitwho
**Domain:** Single-purpose Python CLI (git contributor-activity summary)
**Researched:** 2026-07-28
**Confidence:** MEDIUM-HIGH

## Executive Summary

`gitwho` is a single-file, stdlib-only Python CLI that shells out to `git log --numstat` and aggregates per-author commit/line stats into a table or JSON output. This is a well-trodden niche -- `git shortlog`, `git-fame`, `git-quick-stats`, and `onefetch` all solve adjacent versions of the same problem -- so the research converges on a narrow, high-confidence recommendation rather than open questions: use `argparse` + `subprocess` + `dataclasses`/`collections` from the standard library (no runtime dependencies at all), pull everything from one `git log --numstat` invocation with a control-byte record format, and structure the code as a short pipeline of pure functions (`parse_log` -> `aggregate` -> `render_*`) around a single impure I/O boundary (`run_git`).

The recommended approach is architecturally simple but has a long tail of correctness traps that every comparable tool has hit: binary files report `-`/`-` instead of numbers in `--numstat` and crash naive `int()` parsing; merge commits emit no diff at all by default (not double-counted, just absent) and trip up parsers that assume every commit has numstat lines; rename detection can silently change the numstat column shape depending on ambient `diff.renames` config; and non-UTF-8 author names/locale-dependent git output will crash a tool tested only on the author's own machine. None of these require an architecture change -- they require deliberate handling (`--no-renames`, explicit `-` sentinel checks, forced `LC_ALL=C`, explicit decode-with-`errors="replace"`) baked into the core parsing step from the start, plus dedicated pre-flight checks (`rev-parse --is-inside-work-tree`, `rev-parse --verify HEAD`) rather than string-matching git's stderr.

The MVP scope defined in PROJECT.md (per-author table, `--since`, `--json`, sorted by commit count, non-zero exit on bad input) already matches table-stakes features identified across all four comparable tools, with first/last-commit-date-per-author as gitwho's one clear point of differentiation (none of the surveyed tools surface it). The main risk to manage is not "what to build" (well-scoped) but "build it correct against real-world repos" -- binary files, merges, renames, and non-ASCII authors are near-certain in any repo of nontrivial age, so the fixture-driven test suite matters as much as the feature list.

## Key Findings

### Recommended Stack

The stack is entirely Python standard library, driven directly by PROJECT.md's "stdlib only unless something forces otherwise" constraint -- nothing in the research surfaced a forcing reason to add a dependency. Target Python 3.11+ (safe floor given 3.9 is EOL and 3.10 nears EOL), with dev-only `pytest` (or `unittest` if the stdlib-only ethos should extend to tooling).

**Core technologies:**
- `argparse` (stdlib): CLI parsing (repo path, `--since`, `--json`) -- the only stdlib-native option among argparse/click/typer
- `subprocess`: shells out to `git log --numstat`; this IS the architecture per PROJECT.md's design decision
- `dataclasses` + `collections.defaultdict`: typed per-author records and single-pass aggregation, no dependency needed
- `json` (stdlib): powers `--json` output as a second renderer over the same aggregate data

### Expected Features

Feature research surveyed `git shortlog`, `git-fame`, `git-quick-stats`, and `onefetch`. gitwho's PROJECT.md scope is a minimal, opinionated subset of `git-fame`'s feature set with `git shortlog`'s simplicity -- every in-scope feature is already table stakes across comparables; nothing needs to be added to hit parity.

**Must have (table stakes) -- already in PROJECT.md scope:**
- Per-author commit count, sorted descending
- Lines added/deleted per author (via `--numstat`)
- `--since DATE` filtering
- `--json` structured output
- Repo path argument (default cwd)
- Clear error + non-zero exit for not-a-repo and empty-repo

**Should have (differentiator) -- already in scope:**
- First/last commit date per author -- none of the four comparables lead with this; it's gitwho's clearest point of novelty

**Defer (v2+, deliberately not building):**
- `.mailmap` identity merging -- conflicts with the "correctness = agrees with what git reports" principle; opt-in only if ever added
- `--until DATE`, distribution/percentage column, extra export formats (CSV/MD) -- cheap v1.x adds if real usage demands them
- COCOMO-style cost estimation, interactive TUI, decorative/branded output -- explicitly out of scope, contradicts Core Value

### Architecture Approach

No framework or layered architecture applies at this scale. The right shape is a pipeline of pure functions around exactly one impure boundary: `run_git()`/`validate_repo()`/`fetch_log()` (impure, single subprocess choke point) feed raw text into `parse_log()` (pure, text->records), `aggregate()` (pure, records->per-author stats dict), and `render_table()`/`render_json()` (pure, stats->string). This stays as one file with clearly separated internal sections, not a package -- matching PROJECT.md's single-file constraint while keeping each stage independently unit-testable with literal string fixtures (no git binary needed for `parse_log`/`aggregate`/`render_*` tests).

**Major components:**
1. `run_git`/`validate_repo`/`fetch_log` -- the only place subprocess is called; single `git log --numstat` invocation with a control-byte (`\x1e`/`\x1f`) record format, `--no-renames` pinned explicitly
2. `parse_log` -- pure text->structured-record parsing; the function most worth exhaustive unit testing (binary markers, merge commits with no body, unicode author names)
3. `aggregate` -- pure fold of records into per-author `dict`/dataclass stats (commits, lines, first/last date via running min/max of `%at` epoch timestamps)
4. `render_table`/`render_json` -- pure formatting; both consume the same aggregate dict so the two output modes can't drift out of sync

### Critical Pitfalls

1. **Binary files break naive `int()` parsing** -- `--numstat` emits `-`/`-` for binary files; guard explicitly before casting, treat as 0 lines but still count the commit.
2. **Merge commits show zero numstat lines by default** -- not double-counting, just absence; count commits by header records seen, not by numstat lines present, or merge-only authors silently vanish from commit counts.
3. **Rename detection silently reshapes numstat output** (`3\t1\tpath/{old => new}`) depending on ambient `diff.renames` config the tool doesn't control -- always pass `--no-renames` explicitly.
4. **Non-UTF-8 author names/commit messages crash naive text-mode decoding** -- capture as bytes and decode explicitly with `errors="replace"`, or the tool crashes on any repo with legacy/international commit history.
5. **Empty-repo vs. not-a-repo conflated if detected by stderr string-matching** -- use dedicated `rev-parse --is-inside-work-tree` and `rev-parse --verify HEAD` pre-flight checks instead; this directly maps to two of PROJECT.md's stated Active requirements.
6. **Shallow clones silently produce truncated-but-plausible-looking output** -- no error, just wrong data (common in CI via `actions/checkout`'s default `fetch-depth: 1`); check `rev-parse --is-shallow-repository` and warn/fail explicitly.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Core git-log pipeline (fetch, parse, aggregate)
**Rationale:** Everything else (CLI flags, output formats, error handling) is a thin wrapper around this pipeline; getting the `git log --numstat` invocation shape and parsing correctness right first avoids rework later. This is also where nearly every critical pitfall lives.
**Delivers:** `run_git`/`fetch_log` (single invocation, control-byte format, `--no-renames`), `parse_log` (records), `aggregate` (per-author stats dict with commits/lines/first-last-date)
**Addresses:** Per-author commit count, lines added/deleted, first/last commit date (FEATURES.md table stakes + differentiator)
**Avoids:** Binary-file `int()` crash, merge-commit line-drop, rename-format surprises, per-commit subprocess spawning (performance trap)

### Phase 2: CLI, error handling, and pre-flight validation
**Rationale:** Depends on Phase 1's pipeline existing to wire into; error handling needs dedicated pre-flight checks (a design decision, not an afterthought) rather than being bolted onto the parser later.
**Delivers:** `argparse` CLI (repo path, `--since`, `--json`), `validate_repo` pre-flight (not-a-repo / empty-repo / shallow-repo checks), locale/encoding hardening (`LC_ALL=C`, explicit decode strategy), `main()` wiring with exit-code mapping
**Uses:** `argparse`, `subprocess` env forcing (STACK.md)
**Implements:** Impure I/O boundary component (ARCHITECTURE.md)
**Avoids:** Empty-repo/not-a-repo conflation, locale-dependent misclassification, shallow-clone silent truncation

### Phase 3: Output rendering (table + JSON) and test suite
**Rationale:** Rendering is the lowest-risk, most mechanical piece and depends on Phase 1's stable aggregate shape; the test suite (fixture repos covering binary/merge/rename/non-ASCII/shallow cases) is what proves the pitfall mitigations actually work end-to-end, so it belongs alongside -- not before -- the full pipeline existing.
**Delivers:** `render_table`/`render_json` (both consuming the same aggregate dict), full pytest suite (`test_parse.py`, `test_aggregate.py`, `test_render.py`, `test_cli.py` with real fixture repos)
**Addresses:** `--json` output, sorted table output (FEATURES.md table stakes)

### Phase Ordering Rationale

- Core parsing must come first because it's where the architecture's one impure boundary and the majority of correctness risk (5 of 6 critical pitfalls) both live -- everything downstream assumes it's already correct.
- CLI/error-handling comes second because it wraps the pipeline rather than being independent of it, and PROJECT.md's two explicit error requirements (not-a-repo, empty-repo) map directly to pre-flight checks that need the pipeline's exception types to already exist.
- Rendering and the fixture-driven test suite come last/alongside because they're the verification layer proving the earlier phases' pitfall mitigations actually hold against real git output (binary files, merges, renames, non-ASCII names, shallow clones).

### Research Flags

Phases likely needing deeper research during planning:
- **None strongly flagged.** This is a well-documented, narrow domain -- official git-scm.com docs plus a directly-read production implementation (`git-fame`) cover the mechanism in detail.

Phases with standard patterns (skip research-phase):
- **Phase 1 (core pipeline):** Control-byte record format, `--no-renames`, binary-marker handling, and the pure-function pipeline shape are all directly sourced from official git docs and a real production tool's source -- standard, well-verified pattern.
- **Phase 2 (CLI/error handling):** `rev-parse --is-inside-work-tree` / `--verify HEAD` pre-flight pattern and `LC_ALL=C` locale-forcing are established, low-ambiguity conventions.
- **Phase 3 (rendering/tests):** Plain stdlib formatting and pytest fixture-repo patterns (`tmp_path` + `git init`) are standard, no novel research needed.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM-HIGH | Constraint-driven (stdlib-only is a hard project input); version facts (Python 3.14 current, pytest 9.x) are time-sensitive web data, MEDIUM; core subprocess/argparse mechanism is HIGH (official docs) |
| Features | MEDIUM | Cross-tool synthesis of 4 comparable tools' official repos/docs (each individually MEDIUM); scope already matches PROJECT.md almost exactly, so little inference required |
| Architecture | MEDIUM | Verified against official git-log docs plus a direct source read of a real production implementation (`git-fame`); not cross-checked against a second independent implementation |
| Pitfalls | MEDIUM | Cross-referenced against official git-scm.com docs (binary markers, merge-diff defaults, rename syntax) plus established community consensus; no single canonical "gotchas" source exists for this exact niche |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **`--until DATE` companion flag:** PROJECT.md scopes only `--since`, but every comparable tool that has `--since` also has `--until`. Not a blocker -- flagged as a natural v1.x addition, not a v1 gap to resolve now.
- **Exact minimum git version:** Research confirms `--numstat`/`--pretty=format`/`%aI` have been stable "for well over a decade" but doesn't pin an exact minimum version number; low risk, worth a one-line README note during Phase 2 rather than further research.
- **`.mailmap` behavior when present but unused by the tool:** Research notes git already resolves `.mailmap` for `git log` if present, but this wasn't independently verified -- worth a quick manual check during Phase 1 implementation rather than a dedicated research pass.

## Sources

### Primary (HIGH confidence)
- [git-scm.com -- git-log documentation](https://git-scm.com/docs/git-log) -- `--numstat`, `--pretty=format` placeholders, merge-diff default behavior
- [git-scm.com -- git-diff documentation](https://git-scm.com/docs/git-diff) -- binary-file `-`/`-` marker, rename-in-numstat format
- [git-scm.com -- git-shortlog documentation](https://git-scm.com/docs/git-shortlog) -- baseline comparable tool behavior

### Secondary (MEDIUM confidence)
- [casperdcl/git-fame source (`gitfame/_gitfame.py`)](https://github.com/casperdcl/git-fame/blob/main/gitfame/_gitfame.py) -- direct read; prefix-sentinel parsing, binary-line stripping, rename-brace regex, commit-count cross-check pattern
- [git-fame on PyPI](https://pypi.org/project/git-fame/) -- feature surface, export formats
- [git-quick-stats GitHub README + Debian manpages](https://github.com/git-quick-stats/git-quick-stats) -- comparable feature survey
- [onefetch GitHub README](https://github.com/o2sh/onefetch) -- comparable feature survey
- WebSearch synthesis: Python version currency, pytest version, argparse-vs-click-vs-typer, locale/encoding/shallow-clone gotchas -- cross-checked across two-or-more independent result sets per claim
- [Atlassian -- Aliasing authors in Git](https://www.atlassian.com/blog/developer/aliasing-authors-in-git) -- `.mailmap` background
- [GitHub -- GitPython issue #237](https://github.com/gitpython-developers/GitPython/issues/237) -- corroborates encoding-crash pitfall

### Tertiary (LOW confidence)
- Cross-tool feature synthesis (FEATURES.md) -- individual per-tool sources are authoritative; the synthesis itself is interpretive
- Shallow-clone-in-CI default behavior (`actions/checkout` `fetch-depth: 1`) -- treated as established platform behavior, not independently re-verified this pass

---
*Research completed: 2026-07-28*
*Ready for roadmap: yes*
