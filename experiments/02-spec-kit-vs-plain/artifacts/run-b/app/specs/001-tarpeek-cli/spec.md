# Feature Specification: Tarpeek CLI (Tar Archive Summarizer)

**Feature Branch**: `[001-tarpeek-cli]`

**Created**: 2026-08-17

**Status**: Draft

**Input**: User description: "Build `tarpeek`, a Python CLI that summarizes the contents of a tar archive without extracting it. Given an archive path, print a per-member table: name, type (file/dir/symlink), size in bytes, and last-modified date. Support `--min-size BYTES` to filter members and `--json` for machine-readable output. Sort by size descending. Handle a path that isn't a tar archive, and an empty archive, with clear errors and non-zero exit codes. The tool must never write to the filesystem. Include tests and a README. Name the command `tarpeek` and install it so it runs from any directory (e.g. `pip install` the project or place an executable script on PATH)."

## Clarifications

### Session 2026-08-17

- Q: When the tool fails, should different failure reasons (missing path, not-a-tar-file, empty archive, permission denied, bad `--min-size`) each produce their own distinct exit code, or is a single generic non-zero exit code enough? → A: Single generic non-zero exit code for all error conditions; scripts distinguish the cause via the printed message text, not the exit code value.
- Q: What date/time format and precision should the "last-modified" value use in both the table and JSON output? → A: ISO 8601 timestamp in UTC with seconds precision (e.g. `2026-08-17T14:32:05Z`), including both date and time.
- Q: What JSON field naming convention and top-level structure should `--json` output use? → A: A top-level JSON array of objects, each with snake_case keys: `name`, `type`, `size`, `last_modified`.
- Q: How should members with equal size be ordered relative to each other, since sorting is by size descending? → A: Secondary sort by member name in ascending (alphabetical) order, to keep output deterministic and reproducible.
- Q: What label should be used for tar member types outside file/dir/symlink (e.g. hardlink, device, FIFO)? → A: Use the fallback type label `"other"`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inspect an archive's contents at a glance (Priority: P1)

A user who has received or downloaded a tar archive wants to know what is inside it — file names, whether each entry is a file, directory, or symlink, how large each entry is, and when it was last modified — without extracting anything to disk.

**Why this priority**: This is the core value of the tool. Without this, there is no product. Every other capability (filtering, JSON output) builds on top of this base listing.

**Independent Test**: Run `tarpeek <archive.tar>` against a known, valid tar archive containing files, a directory, and a symlink. Verify every member appears exactly once in the printed output, with correct type, size in bytes, and last-modified date, and that no files were written or extracted to disk.

**Acceptance Scenarios**:

1. **Given** a valid tar archive with multiple files of different sizes, **When** the user runs `tarpeek <archive>`, **Then** the tool prints a table listing every member's name, type, size in bytes, and last-modified date, sorted by size descending.
2. **Given** a valid tar archive containing a regular file, a directory, and a symlink, **When** the user runs `tarpeek <archive>`, **Then** each member's type is correctly reported as "file", "dir", or "symlink" respectively.
3. **Given** any valid tar archive, **When** the user runs `tarpeek <archive>` from any working directory, **Then** no new files, directories, or extracted content appear anywhere on the filesystem as a result of running the command.

---

### User Story 2 - Filter members by minimum size (Priority: P2)

A user investigating disk usage or looking for unexpectedly large files inside an archive wants to narrow the listing to only members at or above a size threshold.

**Why this priority**: This is a natural, high-value refinement once basic listing works, but the tool is still useful without it.

**Independent Test**: Run `tarpeek <archive> --min-size <N>` against an archive with members of known sizes above and below `N`. Verify only members with size >= `N` bytes appear in the output.

**Acceptance Scenarios**:

1. **Given** a valid archive with members of varying sizes, **When** the user runs `tarpeek <archive> --min-size 1000`, **Then** only members with a size of 1000 bytes or greater are listed, still sorted by size descending.
2. **Given** a valid archive where no member meets the size threshold, **When** the user runs `tarpeek <archive> --min-size <N>` with `N` larger than every member, **Then** the tool prints an empty result set (no members) and exits successfully, since the archive itself is valid and simply has no matches.

---

### User Story 3 - Consume archive contents programmatically (Priority: P3)

A user or script integrating `tarpeek` into a larger workflow (e.g. a build pipeline or audit tool) wants the archive summary as structured data instead of a human-readable table.

**Why this priority**: Extends the tool's reach to automation use cases; valuable but secondary to the interactive listing and filtering capabilities.

**Independent Test**: Run `tarpeek <archive> --json` and verify the output is valid JSON that a standard JSON parser can load, containing the same information (name, type, size, last-modified date) as the table output, in the same sorted order.

**Acceptance Scenarios**:

1. **Given** a valid archive, **When** the user runs `tarpeek <archive> --json`, **Then** the tool prints a single JSON document (no extra non-JSON text) representing the list of members, sorted by size descending.
2. **Given** a valid archive and a `--min-size` filter, **When** the user runs `tarpeek <archive> --min-size <N> --json`, **Then** the JSON output contains only the filtered members.

---

### Edge Cases

- What happens when the given path does not exist at all? The tool MUST report a clear, specific error and exit with a non-zero status.
- What happens when the given path exists but is not a valid tar archive (e.g. a plain text file, a corrupted archive, or a different archive format)? The tool MUST report a clear, specific error distinguishing this from a missing-file error, and exit with a non-zero status.
- What happens when the given path is a valid tar archive that contains zero members? The tool MUST report a clear message that the archive is empty and exit with a non-zero status.
- What happens when `--min-size` filtering removes every member from an otherwise valid, non-empty archive? The tool MUST treat this as a successful run with an empty result set (not an error), since the archive itself is valid.
- What happens when the user lacks permission to read the given path? The tool MUST report a clear error distinguishing this from "not a tar archive" and exit with a non-zero status.
- What happens when `--min-size` is given a negative number or non-numeric value? The tool MUST reject the input with a clear error and non-zero exit status before attempting to read the archive.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The tool MUST accept a required path argument identifying the tar archive to summarize.
- **FR-002**: For a valid, non-empty archive, the tool MUST list every member exactly once, including its name, type, size in bytes, and last-modified date.
- **FR-003**: The tool MUST classify each member's type as one of "file", "dir", or "symlink" based on the member's recorded type in the archive; any other tar member type (e.g. hardlink, device, FIFO) MUST be classified with the fallback label "other" rather than failing the run.
- **FR-004**: The default output MUST be a human-readable table sorted by size in descending order, with members of equal size secondarily sorted by name in ascending (alphabetical) order for deterministic output. The last-modified value MUST be rendered as an ISO 8601 UTC timestamp with seconds precision (e.g. `2026-08-17T14:32:05Z`).
- **FR-005**: The tool MUST support a `--min-size BYTES` option that restricts the listing to members whose size is greater than or equal to `BYTES`.
- **FR-006**: The tool MUST support a `--json` flag that emits the same information as valid, machine-parseable JSON instead of the human-readable table, preserving the same sort order and filtering behavior. The JSON output MUST be a top-level array of objects, each with snake_case keys `name`, `type`, `size`, and `last_modified` (the same ISO 8601 UTC timestamp format used in the table output).
- **FR-007**: The tool MUST NOT write, extract, or otherwise create any file, directory, or symlink on the filesystem under any code path, including error paths.
- **FR-008**: When the given path does not exist or cannot be read due to permissions, the tool MUST print a clear, specific error message and exit with a non-zero status code.
- **FR-009**: When the given path exists but is not a readable tar archive, the tool MUST print a clear, specific error message (distinct from a missing-path error) and exit with a non-zero status code.
- **FR-010**: When the archive is valid but contains zero members, the tool MUST print a clear message indicating the archive is empty and exit with a non-zero status code.
- **FR-011**: When `--min-size` filtering results in zero matching members from an otherwise valid, non-empty archive, the tool MUST exit with a successful (zero) status and print an empty result set.
- **FR-011a**: All error conditions (FR-008, FR-009, FR-010, and invalid `--min-size` input) MUST exit with the same generic non-zero status code; the printed message text, not the exit code value, is what distinguishes the cause of failure.
- **FR-012**: The command MUST be invocable as `tarpeek` from any working directory after installation, without requiring the user to reference the source checkout location.
- **FR-013**: The project MUST include automated tests covering: successful listing, size filtering, JSON output, non-existent path, non-tar-archive path, and empty-archive handling.
- **FR-014**: The project MUST include a README documenting what the tool does, how to install it, and how to use each option.

### Key Entities

- **Archive Member**: A single entry recorded inside the tar archive. Attributes: name (path within the archive), type (file, dir, symlink, or other), size in bytes, last-modified date/time (ISO 8601 UTC timestamp, seconds precision).
- **Archive Summary**: The ordered collection of Archive Members produced for a given invocation, after any `--min-size` filtering has been applied, sorted by size descending with ties broken by name ascending.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can obtain a complete, correctly typed listing of a tar archive's contents in a single command invocation, with zero files written or extracted to disk as a result.
- **SC-002**: 100% of members present in a valid, non-empty archive appear exactly once in the tool's output, each with the correct type, size, and last-modified date.
- **SC-003**: Filtering by `--min-size` returns exactly the set of members meeting or exceeding the given threshold, with no false inclusions or omissions, verified against archives with known member sizes.
- **SC-004**: JSON output produced by the tool can be loaded successfully by a standard JSON parser 100% of the time, with no extraneous non-JSON output mixed in.
- **SC-005**: Every identified error scenario (missing path, non-tar file, empty archive, unreadable file, invalid `--min-size` value) produces a distinct, human-readable message and the same non-zero exit code, allowing scripts to reliably detect that a failure occurred via exit status, and to distinguish the specific cause via the message text.
- **SC-006**: A new user can install the tool and successfully run `tarpeek` from any directory within one installation step, without additional configuration.

## Assumptions

- "Type" classification is limited to the three categories named in the request: file, dir, symlink, plus a fallback "other" label (see Clarifications) for any other tar member type (e.g. block/character devices, FIFOs, hard links), so the run never fails solely due to an unrecognized member type.
- "Last-modified date" refers to the modification timestamp recorded in the archive's per-member metadata (not the archive file's own filesystem timestamp).
- An archive that is valid but has zero members is treated as an error condition (clear message, non-zero exit), per the explicit request to "handle... an empty archive... with clear errors and non-zero exit codes."
- A `--min-size` filter that legitimately excludes all members of an otherwise valid, non-empty archive is a successful run with an empty result set, not an error, since the archive itself is valid and the user's filter simply matched nothing.
- Compressed tar variants (e.g. `.tar.gz`, `.tar.bz2`, `.tar.xz`) are treated as supported "tar archives" since they are read via standard tar tooling without requiring extraction to disk.
- Installation is expected to follow standard Python packaging conventions (e.g. a package installable with a console-script entry point), making `tarpeek` available on the user's PATH after installation; no specific packaging tool is mandated by this specification.
