# Roadmap: gitwho

## Overview

Two phases carry gitwho from nothing to a shippable v1. Phase 1 builds and wires
the whole correctness-critical path in one pass: the `git log --numstat` pipeline
(parse, aggregate) plus the CLI entry point, sorted table output, and pre-flight
error handling — this is where the Core Value ("the default table for a normal
repo must be right") lives, and where the known correctness traps (binary files,
merge commits, renames, non-UTF-8 names) get handled from the start rather than
retrofitted. Phase 2 layers on the remaining v1 surface — date filtering, JSON
output — and closes the loop with the fixture-driven test suite and README that
prove Phase 1's correctness claims hold and let a new user operate the tool
without reading source.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Core Summary Command** - Running gitwho against a real repo produces a correct, sorted per-author table, with clear errors for invalid input.
- [ ] **Phase 2: Filtering, JSON Output, and Release Readiness** - `--since` and `--json` round out the CLI; a real-fixture test suite and README make it trustworthy and usable.

## Phase Details

### Phase 1: Core Summary Command

**Goal**: Running gitwho against a real git repository produces a correct, sorted per-author summary table, with clear pre-flight errors for invalid inputs.
**Depends on**: Nothing (first phase)
**Requirements**: DATA-01, DATA-02, DATA-03, DATA-04, DATA-05, CLI-01, CLI-04, CLI-05, CLI-06
**Success Criteria** (what must be TRUE):

  1. Running `gitwho [path]` (defaulting to the current directory) prints a table with commits, lines added, lines deleted, first commit date, and last commit date per author, sorted by commit count descending.
  2. Repos containing binary file changes and merge commits are summarized without crashing — binary changes are excluded from line counts, and merge commits are counted per the documented policy (commit counted, no line stats).
  3. Authors with non-UTF-8 names appear in the output without crashing the tool.
  4. Running gitwho against a directory that is not a git repository prints a clear error and exits with code 2.
  5. Running gitwho against a git repository with no commits prints a clear error and exits non-zero.

**Plans**: 1 plan

Plans:

- [x] 01-01-PLAN.md — Build `gitwho.py` (tracer: one git log call to a sorted per-author table), prove the binary/merge/rename/non-UTF-8 traps against a deterministic fixture repo, and add the pre-flight validation slice with the 0/1/2 exit-code contract

### Phase 2: Filtering, JSON Output, and Release Readiness

**Goal**: Users can narrow results by date and consume output programmatically, and can trust the tool's correctness from its tests and documentation.
**Depends on**: Phase 1
**Requirements**: CLI-02, CLI-03, QUAL-01, QUAL-02
**Success Criteria** (what must be TRUE):

  1. `--since DATE` restricts the summary to commits within git's own date window.
  2. `--json` prints the same per-author data as the table, as valid, machine-readable JSON.
  3. The test suite exercises real git fixture repos (binary file, merge commit, non-ASCII author, empty repo, non-repo directory) with no mocked git calls, and passes.
  4. README documents usage, all flags, exit codes, and the merge-commit line-stats policy.

**Plans**: 1/1 plans executed

Plans:

- [x] 02-01-PLAN.md — Wire `--since` and `--json` through every layer (tracer), prove the whole surface with a stdlib unittest suite against real git fixture repos, and document the contract in a README

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Core Summary Command | 0/1 | Planned | - |
| 2. Filtering, JSON Output, and Release Readiness | 1/1 | In Progress|  |
