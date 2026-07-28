# Requirements: gitwho

**Defined:** 2026-07-28
**Core Value:** One command against any git repo produces a correct, readable per-author activity summary.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Data Collection

- [x] **DATA-01**: Tool collects per-author commits, lines added, lines deleted, first and last commit date from a single `git log --numstat` invocation
- [x] **DATA-02**: Binary-file numstat markers (`-\t-`) are handled without crashing and excluded from line counts
- [x] **DATA-03**: Rename detection is explicitly pinned (`--no-renames`) so ambient git config cannot change the parse shape
- [x] **DATA-04**: Merge commits count toward commits but contribute no line stats (git's default), and this policy is documented
- [x] **DATA-05**: Non-UTF-8 author names do not crash the tool (decode with replacement)

### CLI

- [x] **CLI-01**: Repo path is a positional argument defaulting to the current directory
- [x] **CLI-02**: `--since DATE` restricts the window using git's own date parsing
- [x] **CLI-03**: `--json` emits the same data machine-readably
- [x] **CLI-04**: Output is sorted by commit count, descending
- [x] **CLI-05**: A directory that is not a git repository produces a clear error and exit code 2 (pre-flight `rev-parse`, not stderr string-matching)
- [x] **CLI-06**: A repository with no commits produces a clear error and non-zero exit

### Quality

- [x] **QUAL-01**: Tests cover the real git path via fixture repos (binary file, merge commit, non-ASCII author, empty repo, non-repo dir) — no mocked git
- [x] **QUAL-02**: README documents usage, flags, exit codes, and the merge-commit policy

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### CLI

- **CLI-07**: `--until DATE` companion flag (present in every comparable tool that has `--since`)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| `.mailmap` / author identity merging | Conflicts with "correctness = agreeing with git" for v1; revisit only on validated need |
| Non-git VCS | Tool shells out to git by design |
| Graphical/HTML output | Table + JSON cover both audiences |
| Packaging (PyPI, homebrew) | Single-file script is the deliverable |
| Third-party runtime dependencies | Stdlib-only constraint; nothing in research forced one |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DATA-01 | Phase 1 | Complete |
| DATA-02 | Phase 1 | Complete |
| DATA-03 | Phase 1 | Complete |
| DATA-04 | Phase 1 | Complete |
| DATA-05 | Phase 1 | Complete |
| CLI-01 | Phase 1 | Complete |
| CLI-04 | Phase 1 | Complete |
| CLI-05 | Phase 1 | Complete |
| CLI-06 | Phase 1 | Complete |
| CLI-02 | Phase 2 | Complete |
| CLI-03 | Phase 2 | Complete |
| QUAL-01 | Phase 2 | Complete |
| QUAL-02 | Phase 2 | Complete |

**Coverage:**

- v1 requirements: 13 total
- Mapped to phases: 13
- Unmapped: 0 ✓

---
*Requirements are hypotheses until shipped and validated.*
