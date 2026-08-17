---

description: "Task list for Tarpeek CLI (Tar Archive Summarizer)"
---

# Tasks: Tarpeek CLI (Tar Archive Summarizer)

**Input**: Design documents from `/specs/001-tarpeek-cli/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-interface.md

**Tests**: Included — FR-013 explicitly requires automated tests covering listing, filtering, JSON output, and all error paths.

**Organization**: Tasks are grouped by user story (spec.md priorities P1/P2/P3) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Maps task to US1, US2, or US3
- File paths are exact, per the `src/` layout defined in plan.md

## Path Conventions

Single-project Python package, `src/` layout, per plan.md:

- `src/tarpeek/{__init__.py, cli.py, archive.py, output.py}`
- `tests/{test_archive.py, test_cli.py, test_output.py}`
- `pyproject.toml`, `README.md` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and packaging scaffold

- [X] T001 Create project skeleton: `src/tarpeek/__init__.py` (empty, with `__version__ = "0.1.0"`), empty `src/tarpeek/cli.py`, `src/tarpeek/archive.py`, `src/tarpeek/output.py`, and empty `tests/__init__.py`, `tests/test_archive.py`, `tests/test_cli.py`, `tests/test_output.py`
- [X] T002 Create `pyproject.toml` at repo root with PEP 621 `[project]` metadata (name `tarpeek`, version, description, requires-python `>=3.9`), `[build-system]` using `setuptools`, `[tool.setuptools.packages.find] where = ["src"]`, `[project.scripts] tarpeek = "tarpeek.cli:main"`, and `pytest` under `[project.optional-dependencies].dev`
- [X] T003 [P] Add `ruff` lint configuration (`[tool.ruff]` section in `pyproject.toml`) targeting `src/` and `tests/`

**Checkpoint**: `pip install -e .` succeeds and `tarpeek` resolves on PATH (even though it does nothing yet)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared data types, exceptions, and CLI scaffold that every user story builds on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 In `src/tarpeek/archive.py`, define the `ArchiveMember` dataclass (`name: str`, `type: str`, `size: int`, `last_modified: str`) per data-model.md, and define exception classes `PathNotFoundError`, `PathPermissionError`, `NotATarFileError`, `EmptyArchiveError`, `InvalidMinSizeError` (all subclassing a common `TarpeekError` base)
- [X] T005 In `src/tarpeek/archive.py`, implement `validate_path(path: str) -> None` which raises `PathNotFoundError` if the path does not exist and `PathPermissionError` if it exists but is not readable (checked via `os.access`/explicit `open()` probe before any `tarfile` call)
- [X] T006 In `src/tarpeek/cli.py`, add the `EXIT_ERROR = 1` constant, an `argparse.ArgumentParser` skeleton accepting only the required `PATH` positional argument, and a `main()` function that catches `TarpeekError` subclasses, prints `str(exception)` to stderr, and returns `EXIT_ERROR` (per FR-011a: one generic exit code, message text is what differs)

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - Inspect an archive's contents at a glance (Priority: P1) 🎯 MVP

**Goal**: `tarpeek <archive>` prints a size-sorted table of every member (name, type, size, last-modified), and reports clear errors for missing path, non-tar path, and empty archive — all without writing to the filesystem.

**Independent Test**: Run `tarpeek <archive.tar>` against a known archive with files, a directory, and a symlink; verify every member appears once with correct type/size/date, sorted by size descending (ties by name), and that no files are written or extracted (see quickstart.md steps 1–3, 6).

### Tests for User Story 1 ⚠️

> Write these tests FIRST, ensure they FAIL before implementation

- [X] T007 [P] [US1] In `tests/test_archive.py`, write tests for `TarInfo` → `ArchiveMember` type classification (dir/symlink/file/fallback "other", per FR-003) and for epoch `mtime` → `YYYY-MM-DDTHH:MM:SSZ` UTC conversion, using in-memory tar fixtures built with `tarfile`
- [X] T008 [P] [US1] In `tests/test_archive.py`, write tests for member sort order (`(-size, name)` per FR-004) and for empty-archive detection (an archive built with zero members raises `EmptyArchiveError`)
- [X] T009 [P] [US1] In `tests/test_output.py`, write tests for the table renderer: all four columns (name, type, size, last_modified) present and readable for a small member list
- [X] T010 [P] [US1] In `tests/test_cli.py`, write an end-to-end test: build a tar fixture with a file, dir, and symlink, run the CLI against it, assert exit code `0` and correct table contents in size-descending order
- [X] T011 [P] [US1] In `tests/test_cli.py`, write end-to-end tests for the three error paths: non-existent path, a plain (non-tar) file, and a zero-member tar archive — each asserting the same non-zero exit code and a distinct, non-empty stderr message (FR-008, FR-009, FR-010, FR-011a)
- [X] T012 [P] [US1] In `tests/test_cli.py`, write a filesystem-write guarantee test: snapshot a temp directory's contents before and after a `tarpeek` invocation (success and error cases) and assert no diff (FR-007)

### Implementation for User Story 1

- [X] T013 [US1] In `src/tarpeek/archive.py`, implement `_member_from_tarinfo(info: tarfile.TarInfo) -> ArchiveMember`, classifying type via `isdir()`/`issym()`/`isfile()` (in that order) with fallback `"other"`, and converting `info.mtime` via `datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")` (depends on T004)
- [X] T014 [US1] In `src/tarpeek/archive.py`, implement `read_archive(path: str) -> list[ArchiveMember]`: call `validate_path`, open with `tarfile.open(path, "r:*")` inside `try/except tarfile.ReadError` (re-raise as `NotATarFileError`), call `getmembers()`, map each via `_member_from_tarinfo`, and raise `EmptyArchiveError` if the resulting list is empty (depends on T005, T013)
- [X] T015 [US1] In `src/tarpeek/archive.py`, implement `sort_members(members: list[ArchiveMember]) -> list[ArchiveMember]` returning members sorted by `(-size, name)` (depends on T014)
- [X] T016 [US1] In `src/tarpeek/output.py`, implement `render_table(members: list[ArchiveMember]) -> str` producing fixed-width, left-aligned columns for name/type/size/last_modified (depends on T004)
- [X] T017 [US1] In `src/tarpeek/cli.py`, wire `main()`: parse `PATH`, call `read_archive` → `sort_members` → `render_table`, print result to stdout, return `0`; ensure all `TarpeekError` subclasses raised anywhere in this path are caught by the existing exception-to-exit-code handling from T006 (depends on T006, T015, T016)

**Checkpoint**: `tarpeek <archive>` fully works standalone — basic listing and all three core error paths are correct and independently testable

---

## Phase 4: User Story 2 - Filter members by minimum size (Priority: P2)

**Goal**: `tarpeek <archive> --min-size N` restricts the table to members with `size >= N`, validates `N` before opening the archive, and treats an all-filtered-out result as success.

**Independent Test**: Run `tarpeek <archive> --min-size N` against an archive with members above and below `N`; verify only qualifying members appear, still sorted by size descending (quickstart.md step 4).

### Tests for User Story 2 ⚠️

- [X] T018 [P] [US2] In `tests/test_archive.py`, write unit tests for `filter_by_min_size(members, min_size)`: members below the threshold are excluded, members at exactly the threshold are included, and filtering to zero members returns `[]` without raising
- [X] T019 [P] [US2] In `tests/test_cli.py`, write end-to-end tests for `--min-size`: only qualifying members are listed and still sorted correctly; `--min-size` larger than every member yields exit code `0` with an empty result; a non-numeric or negative `--min-size` value is rejected with a non-zero exit code and clear message before the archive is opened (FR-011, FR-011a)

### Implementation for User Story 2

- [X] T020 [US2] In `src/tarpeek/archive.py`, implement `filter_by_min_size(members: list[ArchiveMember], min_size: int) -> list[ArchiveMember]`, keeping members where `size >= min_size` (depends on T014)
- [X] T021 [US2] In `src/tarpeek/cli.py`, add the `--min-size` argument (parsed/validated as a non-negative integer, raising `InvalidMinSizeError` on non-numeric or negative input, validated before `read_archive` is called), and insert `filter_by_min_size` into the pipeline between `read_archive` and `sort_members` (depends on T017, T020)

**Checkpoint**: User Stories 1 AND 2 both work independently; `--min-size` filtering is correct and validated up front

---

## Phase 5: User Story 3 - Consume archive contents programmatically (Priority: P3)

**Goal**: `tarpeek <archive> --json` emits the same member data as a single JSON array of snake_case objects, respecting the same sort order and `--min-size` filtering as the table output.

**Independent Test**: Run `tarpeek <archive> --json` (with and without `--min-size`) and verify the output parses as JSON with exactly the expected keys and content (quickstart.md step 5).

### Tests for User Story 3 ⚠️

- [X] T022 [P] [US3] In `tests/test_output.py`, write tests for `render_json`: output parses via `json.loads`, is a top-level array, and each object has exactly the keys `name`, `type`, `size`, `last_modified` with correct value types
- [X] T023 [P] [US3] In `tests/test_cli.py`, write end-to-end tests for `--json`: valid JSON with no extraneous stdout text, same sort order as the table, empty-result case (`[]`) after a fully-excluding `--min-size`, and combined `--min-size --json` returning only the filtered members

### Implementation for User Story 3

- [X] T024 [US3] In `src/tarpeek/output.py`, implement `render_json(members: list[ArchiveMember]) -> str` using `json.dumps` on a list of `{"name", "type", "size", "last_modified"}` dicts (depends on T004)
- [X] T025 [US3] In `src/tarpeek/cli.py`, add the `--json` flag; when set, call `render_json` instead of `render_table` on the same filtered/sorted member list, printing only the JSON document to stdout (depends on T021, T024)

**Checkpoint**: All three user stories are independently functional — basic listing, filtering, and JSON output all work standalone and together

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and final verification across all stories

- [X] T026 [P] Write `README.md` at repo root: what `tarpeek` does, install instructions (`pip install .`), and usage/examples for `PATH`, `--min-size`, and `--json` (FR-014)
- [X] T027 [P] Run `ruff check src/ tests/` and fix any reported issues (Constitution Principle I: zero-unaddressed-warnings)
- [X] T028 Execute quickstart.md end-to-end by hand (install, build sample archive, run all three user-story scenarios plus all four error scenarios, confirm matching exit codes and zero filesystem writes)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational only
- **User Story 2 (Phase 4)**: Depends on Foundational; implementation (T021) depends on US1's T017 (extends the same CLI pipeline)
- **User Story 3 (Phase 5)**: Depends on Foundational; implementation (T025) depends on US2's T021 (extends the same CLI pipeline)
- **Polish (Phase 6)**: Depends on all three user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies on other stories — fully standalone
- **User Story 2 (P2)**: Reuses US1's `read_archive`/`sort_members`/CLI pipeline; independently testable via its own `--min-size` behavior
- **User Story 3 (P3)**: Reuses US1/US2's pipeline; independently testable via its own `--json` behavior

### Within Each User Story

- Tests (T007–T012, T018–T019, T022–T023) are written first and must fail before their corresponding implementation tasks
- `archive.py` logic before `output.py` rendering before `cli.py` wiring
- Story complete and checkpointed before moving to the next priority

### Parallel Opportunities

- T001–T003 (Setup) can overlap; T003 is independent of T001/T002's content
- All Foundational tasks (T004–T006) are sequential (T005 depends on T004's exceptions; T006 depends on nothing but is small) — T004 must land first
- Within US1: T007, T008, T009, T010, T011, T012 (all test-writing, different files/scenarios) run in parallel
- Within US2: T018, T019 run in parallel
- Within US3: T022, T023 run in parallel
- T026 and T027 (Polish) run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all US1 tests together (different files/scenarios, all currently failing):
Task: "Type classification + mtime conversion tests in tests/test_archive.py"
Task: "Sort order + empty-archive detection tests in tests/test_archive.py"
Task: "Table renderer format tests in tests/test_output.py"
Task: "End-to-end successful listing test in tests/test_cli.py"
Task: "End-to-end error-path tests (missing/non-tar/empty) in tests/test_cli.py"
Task: "Filesystem-write guarantee test in tests/test_cli.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (blocks everything)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: `tarpeek <archive>` lists correctly and all three core error paths work, with zero filesystem writes
5. This alone is a shippable, useful tool (basic listing)

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. Add User Story 1 → validate independently → MVP
3. Add User Story 2 (`--min-size`) → validate independently
4. Add User Story 3 (`--json`) → validate independently
5. Polish: README, lint, full quickstart pass

---

## Notes

- [P] tasks touch different files/scenarios and have no unresolved dependencies among themselves
- [Story] label maps each task to US1/US2/US3 for traceability
- All error conditions share one generic non-zero exit code (FR-011a) — tests must assert message text differs, not exit code value
- Verify each story's tests fail before implementing that story
- Commit after each task or logical group
- Stop at any checkpoint to validate a story independently before proceeding
