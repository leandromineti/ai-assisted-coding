# Phase 0 Research: Tarpeek CLI

All items from the spec's Clarifications session were already resolved before planning began
(exit code strategy, timestamp format, JSON shape, tie-break sort, fallback type label). The
research below covers the remaining implementation-level decisions needed to fill in the
Technical Context, none of which required external clarification.

## 1. Reading tar archives without extracting

- **Decision**: Use the standard-library `tarfile` module, opened with mode `"r:*"` (auto-detects
  and transparently decompresses gzip/bz2/xz/plain-tar based on content), and enumerate members
  via `TarFile.getmembers()`. Only header metadata (`TarInfo` objects) is touched — member file
  contents are never read or extracted.
- **Rationale**: `tarfile` is the only tool needed; it natively distinguishes member types
  (`isfile()`, `isdir()`, `issym()`) and exposes `size`, `mtime`, and `name` directly on
  `TarInfo`, with zero extraction. It also already supports every compressed tar variant named in
  the spec's Assumptions (`.tar.gz`, `.tar.bz2`, `.tar.xz`) via the same `"r:*"` mode.
- **Alternatives considered**:
  - Shelling out to the system `tar` binary — rejected: adds a subprocess dependency, invites
    parsing fragile CLI output, and is not more capable than the stdlib module.
  - `tarfile` streaming mode (`"r|*"`) — rejected: streaming mode disallows random access and
    complicates "read all headers, then sort," with no benefit for this tool's read-header-only
    use case.

## 2. Detecting "not a tar archive" vs "missing path" vs "permission denied"

- **Decision**: Check path existence and readability explicitly before opening (distinguishing
  `FileNotFoundError` from `PermissionError`), then attempt `tarfile.open(...)` inside a
  `try/except tarfile.ReadError` block to catch "exists but isn't a valid tar archive." Map each
  distinct exception to its own clear message, all funneled to the same generic non-zero exit
  code per FR-011a.
- **Rationale**: `tarfile.open()` on a non-tar file raises `tarfile.ReadError`, which is already
  distinct from the OS-level `FileNotFoundError`/`PermissionError` raised by an explicit
  pre-check (or by `tarfile.open` itself for a missing path) — no custom sniffing logic needed.
- **Alternatives considered**: Using `tarfile.is_tarfile(path)` as a pre-check — rejected as the
  sole mechanism because it re-opens/re-reads the file and still requires separate handling for
  missing-path/permission-denied, so the explicit try/except approach is simpler and covers all
  cases in one pass.

## 3. Packaging so `tarpeek` runs from any directory after `pip install`

- **Decision**: `pyproject.toml` using PEP 621 project metadata and `setuptools` as the build
  backend, with a `src/` layout and:
  ```toml
  [project.scripts]
  tarpeek = "tarpeek.cli:main"
  ```
- **Rationale**: This is the standard, tool-agnostic way to get a console script placed on PATH
  by `pip install .` (or `pip install -e .` for development) — satisfies FR-012 and SC-006 with
  no custom install scripting. `setuptools` with `pyproject.toml` requires no extra config beyond
  `[tool.setuptools.packages.find] where = ["src"]`, and is the most broadly familiar backend.
- **Alternatives considered**:
  - `hatchling` — a fine alternative backend with similar simplicity; not chosen only because
    `setuptools` is more ubiquitous and this project has no packaging needs that would benefit
    from Hatch-specific features.
  - A standalone script on PATH (no packaging) — rejected: the spec explicitly favors
    `pip install`-based distribution as the primary path ("e.g. `pip install` the project"), and
    packaging also gives dependency management and versioning for free.

## 4. Timestamp conversion

- **Decision**: `TarInfo.mtime` is a Unix epoch integer (UTC by definition); render it as
  `datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")`.
- **Rationale**: Matches the clarified format exactly (`2026-08-17T14:32:05Z`), and epoch-to-UTC
  conversion needs no timezone-database dependency.
- **Alternatives considered**: `datetime.utcfromtimestamp()` — deprecated in favor of the
  timezone-aware `fromtimestamp(..., tz=timezone.utc)` form; avoided to prevent a deprecation
  warning under Principle I's zero-unaddressed-warnings rule.

## 5. Table rendering

- **Decision**: Fixed-width, left-aligned plain-text columns built with `str.format`/f-strings
  (name, type, size, last_modified), no external table-formatting dependency.
- **Rationale**: Keeps runtime dependencies at zero, matches Principle I's "minimal" guidance, and
  the spec does not require any particular table styling — only that name/type/size/date are all
  present and readable.
- **Alternatives considered**: A third-party table library (e.g. `tabulate`, `rich`) — rejected
  to keep the tool dependency-free and avoid an abstraction the small output doesn't need.

**Output**: All unknowns resolved; no `NEEDS CLARIFICATION` markers remain in Technical Context.
