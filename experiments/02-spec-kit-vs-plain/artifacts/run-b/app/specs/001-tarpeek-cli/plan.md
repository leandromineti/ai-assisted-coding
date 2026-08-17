# Implementation Plan: Tarpeek CLI (Tar Archive Summarizer)

**Branch**: `001-tarpeek-cli` | **Date**: 2026-08-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-tarpeek-cli/spec.md`

## Summary

`tarpeek` is a Python CLI that reads a tar archive's member metadata (via the standard-library
`tarfile` module, in read-only streaming/random-access mode) and prints a size-sorted summary
table — name, type, size, last-modified — without ever extracting or writing to disk. It supports
`--min-size` filtering and `--json` output, and is packaged with a `pyproject.toml` console-script
entry point so `pip install` places `tarpeek` on PATH, runnable from any directory.

## Technical Context

**Language/Version**: Python 3.9+ (uses only standard library: `tarfile`, `argparse`, `json`,
`datetime`, `dataclasses`)

**Primary Dependencies**: None at runtime (standard library only). Dev/test: `pytest`.

**Storage**: N/A — the tool is strictly read-only against the input archive and MUST NOT write,
extract, or create any file/dir/symlink on the filesystem (FR-007).

**Testing**: `pytest`, with tar fixtures built in-memory/in-tmp-dir at test time (via `tarfile`
itself) rather than committed binary fixtures, so tests stay deterministic and inspectable.

**Target Platform**: Any OS with Python 3.9+ (Linux, macOS, Windows) — pure standard library, no
platform-specific code paths.

**Project Type**: Single-project Python CLI, packaged for `pip install`.

**Performance Goals**: Not throughput-critical; must handle archives with thousands of members by
reading headers only (`TarFile.getmembers()`), never reading member file contents into memory.

**Constraints**: Zero filesystem writes under any code path, including error paths (FR-007);
single generic non-zero exit code for all error conditions (FR-011a); deterministic output order
(size desc, name asc tiebreak).

**Scale/Scope**: Single-command CLI, three user stories (list, filter, JSON output), no
persistence, no network, no concurrency.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Code Quality**: PASS. Scope is small enough for a flat module layout (cli / archive /
  output) with single-responsibility modules; no premature abstraction needed. Public functions
  (the `main()` entry point, the archive-reading function, the formatters) will be documented at
  definition. Linting via `ruff` (or equivalent) planned in tasks.
- **II. Testing Standards (NON-NEGOTIABLE)**: PASS. Spec FR-013 already enumerates the required
  test scenarios (listing, filtering, JSON, missing path, non-tar path, empty archive); these map
  directly to pytest cases planned in Phase 1 contracts and executed in `/speckit-tasks`.
- **III. User Experience Consistency**: PASS. Single command, consistent snake_case JSON keys,
  one error-message style, one exit-code convention — all fixed by the spec's clarifications, so
  there is one voice to maintain from the start.
- **IV. Clear Error Behavior**: PASS. Spec already distinguishes user errors (bad path, bad
  `--min-size`, not-a-tar-file) from being silently swallowed — each gets a specific message and
  the same non-zero exit code (FR-008–FR-011a). No internal stack traces will be shown to the user
  (caught exceptions re-raised as clean CLI error messages).

No violations identified. Complexity Tracking section is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/001-tarpeek-cli/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── cli-interface.md
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
pyproject.toml           # PEP 621 metadata + console_scripts entry point (tarpeek -> tarpeek.cli:main)
README.md                # FR-014: what it does, install, usage per option

src/
└── tarpeek/
    ├── __init__.py
    ├── cli.py           # argparse setup, main() entry point, error-to-exit-code mapping
    ├── archive.py       # tarfile reading, member classification, filtering, sorting
    └── output.py        # table renderer and JSON renderer

tests/
├── test_archive.py      # member classification, filtering, sort order, empty-archive detection
├── test_cli.py          # end-to-end invocations: exit codes, table output, --json, error paths
└── test_output.py       # table formatting and JSON schema/field-naming checks
```

**Structure Decision**: Single-project Python package using the `src/` layout (`src/tarpeek/`),
packaged via `pyproject.toml` with a `[project.scripts]` console-script entry point named
`tarpeek`. This is Option 1 (single project) from the template, adapted for standard Python
packaging conventions instead of a generic `src/models|services|cli|lib` split, because the
feature is one cohesive CLI tool, not a multi-layer application — three small modules
(`cli`, `archive`, `output`) match the natural read → filter/sort → render pipeline without
introducing unneeded layers.

## Complexity Tracking

*No violations — section not applicable.*
