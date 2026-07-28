# Feature Research

**Domain:** Git contributor-activity summary CLI
**Researched:** 2026-07-28
**Confidence:** MEDIUM

## Feature Landscape

Four comparable tools were surveyed, each occupying a different niche of the same
underlying idea ("summarize who did what in this git repo"):

- **`git shortlog`** — built into git itself; the baseline every git user already knows.
- **`git-quick-stats`** — bash, interactive menu, broad stat surface (time-of-day, reviewers, branch tree).
- **`git-fame`** — Python/PyPI, closest sibling to gitwho: per-author LOC/commits/files table with multiple export formats.
- **`onefetch`** — Rust, single-shot "neofetch for git repos"; a stylized project dashboard, not a data table.

gitwho's PROJECT.md scope (per-author commits/lines-added/lines-deleted/first-last-date
table, `--since`, `--json`, sorted by commit count, non-zero exit on bad input) sits
squarely inside what `git shortlog` and `git-fame` already do — it is a minimal,
opinionated subset of git-fame's feature set with git shortlog's simplicity.

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Per-author commit count | Every tool surveyed leads with this; it's the atomic unit of "contributor activity" (`git shortlog -sn`, git-fame `coms` column) | LOW | Already in scope: PROJECT.md's per-author table |
| Sort by activity (descending) | `git shortlog -n` and git-fame's default table both sort by contribution, not alphabetically — users scan top-down for "who's doing the most" | LOW | Already in scope: sorted by commit count descending |
| Date-range filtering (`--since`/`--until`) | Present in `git shortlog`, `git-quick-stats` (`_GIT_SINCE`/`_GIT_UNTIL`), and implicitly supported by git-fame via git's own log filtering — a fixed all-time view is rarely what users want for "recent activity" questions | LOW | Already in scope: `--since DATE`. Note git-fame and `git-quick-stats` both expose `--since` AND `--until`; PROJECT.md scopes only `--since` — flag this as a possible v1.x gap, not a v1 blocker |
| Machine-readable output (JSON) | git-fame ships Markdown/YAML/JSON/CSV/TSV; onefetch ships JSON/YAML — every tool that isn't `git shortlog` itself treats structured output as non-negotiable for scripting/CI use | LOW | Already in scope: `--json` |
| Lines added/deleted per author | This is git-fame's headline differentiator over plain `git shortlog` (which only counts commits) — a "contributor activity" tool that can't show code volume reads as strictly worse than git-fame | MEDIUM | Already in scope. Sourced from `git log --numstat`; binary files report `-`/`-` and must be handled (noted as a known edge case in PROJECT.md) |
| Non-git-repo / empty-repo error handling | Every CLI wrapping `git` must handle "not a repo" and "no commits yet" gracefully — git itself errors loudly (`fatal: not a git repository`) and a summary tool inherits the same class of failure | LOW | Already in scope: clear error + non-zero exit for both cases |
| Repo path argument (default: cwd) | `git-fame`, `git-quick-stats`, and `onefetch` all default to the current directory but accept a path/argument for pointing at another repo — this is the standard git-CLI-adjacent convention | LOW | Already in scope |

### Differentiators (Competitive Advantage)

Features that set the product apart from `git shortlog`. Not required for gitwho's stated
Core Value, but worth naming so they're consciously deferred rather than accidentally
missed.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| First/last commit date per author | Neither `git shortlog` nor `git-fame`'s default table surfaces this — it answers "is this person still active?" / "how long have they contributed?", a genuinely useful angle none of the four surveyed tools leads with | LOW | Already in scope — this is gitwho's one clear point of novelty vs. the comparables |
| Distribution / percentage-of-total column | git-fame's `distribution` column (e.g. `68.6/74.0/37.3`) shows relative share of loc/commits/files — useful for "how concentrated is this codebase's ownership" questions | LOW | Not in scope; cheap to add later (just a derived column over existing per-author totals) |
| Multiple export formats (CSV/TSV/Markdown/YAML) | git-fame supports 5 formats; useful for pasting into docs or spreadsheets | LOW–MEDIUM | Not in scope; `--json` covers the scripting use case, which is the highest-value one |
| Cost/effort estimation (COCOMO person-months, person-hours) | git-fame's most advanced feature — estimates "how much did this cost" from LOC or commit-time deltas | HIGH | Not in scope; speculative accuracy, scope creep away from Core Value ("correct, readable summary") |
| Interactive menu / TUI | `git-quick-stats` is built entirely around an interactive terminal menu (detailed stats, changelogs, branch tree, reviewer suggestions) | HIGH | Not in scope; PROJECT.md is explicitly a single-command table/JSON tool, not an explorer |
| Visual "fetch card" branding (logo, colors, ASCII art) | `onefetch`'s whole identity — a shareable, decorative terminal summary | MEDIUM–HIGH | Not in scope; PROJECT.md explicitly excludes graphical/HTML output, and a fetch-card aesthetic is a different product goal (branding/sharing vs. correctness/analysis) |
| Suggested reviewers / recent-file-owner lookup | `git-quick-stats`'s `-r` flag suggests who to ask for review based on file history | MEDIUM | Not in scope; different use case (code review routing vs. activity summary) |
| Branch tree / ASCII commit graph | `git-quick-stats`'s `-b` option visualizes branch history | MEDIUM | Not in scope; orthogonal to contributor summary |
| Contribution-by-time-of-day/weekday/month | `git-quick-stats` breaks activity down by hour, weekday, month, year | LOW–MEDIUM | Not in scope; interesting but not part of the stated per-author table |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems for a tool this size — or that PROJECT.md has
already explicitly ruled out. Listed here so the roadmap doesn't accidentally reopen them.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|------------------|-------------|
| Author identity merging (`.mailmap`, dedupe by heuristic name/email matching) | Real pain point — git-fame's own docs note the same person appears multiple times across name/email changes without `.mailmap` | High complexity, ambiguous heuristics (fuzzy name matching produces false merges), and PROJECT.md explicitly scopes this out for v1 | Document that `--json`/table output is per raw author identity as git reports it; let users pre-configure `.mailmap` themselves (git already resolves it for `git log` if present — worth confirming behavior in implementation, not adding merge logic) |
| Supporting other VCS (Mercurial, SVN) | "Just abstract the backend" seems reusable | Different data models per VCS; PROJECT.md is explicit the tool shells out to `git` by design | None needed — out of scope is correct |
| Interactive TUI / menu system (à la git-quick-stats) | Feels more "powerful" / discoverable | Contradicts Core Value: "One command... produces a correct, readable summary" — adds a whole interaction paradigm and dependency surface for a stdlib-only single-file script | Keep it a single non-interactive command; if exploration is wanted later, it's a new tool, not a flag on this one |
| COCOMO-style cost/effort estimation | Managers like a dollar/hour number | Model accuracy is contested even in git-fame's own space; risks being read as authoritative when it's a rough heuristic, and pulls scope toward "estimation tool" away from "activity summary" | If ever wanted, ship as a clearly-labeled experimental flag in a future milestone, not v1 |
| Decorative/branded terminal output (ASCII art, logos, color themes) | onefetch's popularity shows people like a nice terminal card | PROJECT.md explicitly excludes graphical/HTML output; decorative output also complicates the `--json` parity guarantee (two renderers to keep correct) | Plain table is the deliverable; users who want visuals can pipe JSON into their own renderer |
| Packaging for PyPI/Homebrew | Natural "make it easy to install" instinct | PROJECT.md explicitly scopes this out — single-file script is the deliverable for v1 | `pip install`-style distribution is a fine v2 concern once the tool is validated |

## Feature Dependencies

```
Per-author commit count (table stakes)
    └──requires──> git log parsing (author, date per commit)

Lines added/deleted per author (table stakes)
    └──requires──> git log --numstat parsing
                       └──requires──> binary-file edge case handling (numstat reports "-" "-")

First/last commit date per author (differentiator, in-scope)
    └──requires──> git log parsing (author, date per commit)
    └──shares data source with──> Per-author commit count

--since DATE filter (table stakes)
    └──enhances──> all of the above (scopes the git log window before aggregation)

--json output (table stakes)
    └──requires──> stable internal per-author data structure
                       (same structure table rendering consumes — one aggregation, two renderers)

Non-repo / empty-repo error handling (table stakes)
    └──must run BEFORE──> any git log invocation (fail fast, not mid-parse)

Author identity merging (.mailmap) [OUT OF SCOPE]
    └──conflicts with──> "raw git output = source of truth" principle (PROJECT.md: "correctness means agreeing with what git reports")
```

### Dependency Notes

- **Lines added/deleted requires `git log --numstat` parsing:** this is a materially
  different data source from the plain commit-count path (`git shortlog` or `git log
  --pretty`), and it's the one place PROJECT.md already flags a known edge case (binary
  files report `-` instead of a number). Plan for this as its own parsing step with its
  own test cases, not a trivial extension of commit counting.
- **`--json` shares its aggregation with the table renderer:** both git-fame and onefetch
  treat JSON as a second view over one internal data model, not a separate code path. Build
  the per-author aggregate once; render it two ways. This avoids the two outputs drifting
  out of sync — a correctness risk given Core Value is "the default table... must be right."
- **Error handling must run before aggregation, not after:** a common pitfall in git-wrapper
  CLIs is discovering "no commits" or "not a repo" partway through parsing `git log` output
  (e.g., empty stdout is ambiguous between "no commits" and "some other failure"). Detect
  both conditions with a dedicated pre-check (e.g. `git rev-parse --is-inside-work-tree`,
  `git rev-parse HEAD`) before running the real aggregation.
- **`.mailmap`/identity merging conflicts with the "agree with what git reports" principle:**
  note this isn't just complexity — it's a philosophical tension. Merging identities means
  the tool's output no longer directly matches `git shortlog -sn`'s raw output, which
  undermines the "correctness = agreeing with git" contract in PROJECT.md. If this is ever
  added, it should be an explicit opt-in flag, not default behavior.

## MVP Definition

### Launch With (v1)

Minimum viable product — matches PROJECT.md's Active requirements exactly; no additions
recommended.

- [x] Per-author table: commits, lines added, lines deleted, first commit date, last commit date — this is the whole Core Value
- [x] Repo path argument, defaulting to cwd — standard convention across all comparables
- [x] `--since DATE` — table-stakes filtering, present in every comparable tool
- [x] `--json` — table-stakes structured output, present in git-fame and onefetch
- [x] Sorted by commit count, descending — matches `git shortlog -n` / git-fame convention
- [x] Clear error + non-zero exit: not-a-repo — required for scriptability and basic robustness
- [x] Clear error + non-zero exit: empty repo — same

### Add After Validation (v1.x)

Features to add once the core table is proven correct and useful. None are urgent; add
only if real usage surfaces the need.

- [ ] `--until DATE` — companion to `--since`; every comparable tool that has `--since` also has `--until`. Cheap addition, natural pairing. Trigger: a user wants a closed date window, not just "since X."
- [ ] Distribution/percentage column — trigger: users start eyeballing "what % of this codebase is mine," which the raw counts don't answer directly.
- [ ] Additional export formats (CSV/Markdown) — trigger: someone wants to paste results into a doc or spreadsheet without hand-converting JSON.

### Future Consideration (v2+)

Features to defer until the core tool has validated demand — and in most cases,
deliberately never build (see Anti-Features).

- [ ] `.mailmap`-based identity merging — defer until users report the "same person, two emails" problem is actually hurting them, and treat it as opt-in even then.
- [ ] Cost/effort estimation (COCOMO-style) — defer indefinitely; different product goal (estimation vs. summary), contested methodology.
- [ ] Interactive/TUI mode — defer indefinitely; contradicts the single-command Core Value.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|----------------------|----------|
| Per-author commit table | HIGH | LOW | P1 |
| Lines added/deleted | HIGH | MEDIUM | P1 |
| First/last commit date | MEDIUM | LOW | P1 |
| `--since` filter | HIGH | LOW | P1 |
| `--json` output | HIGH | LOW | P1 |
| Sorted output | MEDIUM | LOW | P1 |
| Non-repo/empty-repo errors | HIGH | LOW | P1 |
| `--until` filter | MEDIUM | LOW | P2 |
| Distribution/percentage column | LOW | LOW | P3 |
| Extra export formats (CSV/MD) | LOW | LOW | P3 |
| `.mailmap` identity merging | MEDIUM | HIGH | P3 (opt-in only, if ever) |
| Cost/effort estimation | LOW | HIGH | Do not build |
| Interactive TUI | LOW | HIGH | Do not build |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | git shortlog | git-fame | git-quick-stats | onefetch | gitwho's approach |
|---------|--------------|----------|------------------|----------|--------------------|
| Per-author commit count | Yes (`-sn`) | Yes (`coms`) | Yes | Yes (top contributors) | Yes — table stakes, in scope |
| Lines added/deleted | No | Yes (`loc`, aggregate) | Yes (via detailed stats) | No (LOC total only, not per-author breakdown) | Yes — added/deleted split, in scope |
| First/last commit date per author | No | No | Partial (via changelogs, not a table column) | No (repo creation date only) | Yes — this is gitwho's clearest point of differentiation |
| Date-range filter | Yes (`--since/--until`) | Via git log filtering | Yes (`_GIT_SINCE/_GIT_UNTIL`) | No | `--since` only in scope; `--until` is a natural v1.x add |
| JSON output | No | Yes (+ YAML/CSV/TSV/MD) | No | Yes (+ YAML) | `--json` only, in scope — matches the highest-value structured format |
| Identity merging (mailmap) | Partial (git-native mailmap support) | Notes the problem, doesn't auto-fix | No | No | Explicitly out of scope for v1 |
| Interactive UI | No | No | Yes (menu-driven) | No | Out of scope — single command by design |
| Decorative/branded output | No | No | No | Yes (its whole identity) | Out of scope — table/JSON only |
| Distribution %/cost estimation | No | Yes (both) | No | No | Out of scope for v1; distribution % is a plausible v1.x add |

## Sources

- [git-scm.com — git-shortlog official documentation](https://git-scm.com/docs/git-shortlog) (HIGH — primary/official)
- [git-quick-stats GitHub README](https://github.com/git-quick-stats/git-quick-stats) (MEDIUM — official repo, cross-checked against manpages)
- [git-quick-stats Debian/Ubuntu manpages](https://manpages.debian.org/bullseye/git-quick-stats/git-quick-stats.1.en.html) (MEDIUM — packaged docs, cross-checked against GitHub README)
- [git-fame on PyPI](https://pypi.org/project/git-fame/) (MEDIUM — official package listing)
- [git-fame GitHub repository (casperdcl/git-fame)](https://github.com/casperdcl/git-fame) (MEDIUM — official source)
- [onefetch GitHub README (o2sh/onefetch)](https://github.com/o2sh/onefetch) (MEDIUM — official repo, the maintained fork)
- Cross-tool synthesis derived from the above four (LOW confidence as a standalone claim — treat the individual per-tool sources as authoritative, this synthesis as interpretive)

---
*Feature research for: Git contributor-activity summary CLI*
*Researched: 2026-07-28*
