# CLI Interface Contract: `tarpeek`

`tarpeek` has no network/API surface — its contract is its command-line invocation, output
formats, and exit codes. This document is the contract that `tests/test_cli.py` and
`tests/test_output.py` validate against.

## Invocation

```text
tarpeek PATH [--min-size BYTES] [--json]
```

| Argument      | Required | Type   | Description |
|---------------|----------|--------|-------------|
| `PATH`        | Yes      | string | Path to the tar archive to summarize (any `tarfile`-supported variant: `.tar`, `.tar.gz`, `.tar.bz2`, `.tar.xz`). |
| `--min-size`  | No       | int    | Minimum size in bytes (inclusive); only members with `size >= BYTES` are shown. Must be a non-negative integer. |
| `--json`      | No       | flag   | Emit JSON instead of the human-readable table. |

## Successful output — table (default)

- Printed to stdout.
- One row per member, columns: name, type, size (bytes), last-modified (ISO 8601 UTC).
- Sorted by size descending, ties broken by name ascending.
- If `--min-size` filtering yields zero members, prints an empty result (e.g. header only, or a
  clear "no members matched" line) and exits `0` — this is success, not an error (FR-011).

Example (illustrative column layout, not a fixed-width spec beyond "all four fields present and
readable"):

```text
NAME                TYPE     SIZE  LAST_MODIFIED
big.log             file     4096  2026-08-10T09:15:00Z
notes.txt           file      512  2026-08-01T00:00:00Z
docs                dir         0  2026-07-15T12:00:00Z
```

## Successful output — `--json`

- Printed to stdout as a single JSON document, no extra non-JSON text mixed in (SC-004).
- Top-level value: a JSON array of objects.
- Each object has exactly these snake_case keys: `name`, `type`, `size`, `last_modified`.
- Same sort order and same `--min-size` filtering as the table output.
- Empty result (after filtering) → `[]`.

```json
[
  {"name": "big.log", "type": "file", "size": 4096, "last_modified": "2026-08-10T09:15:00Z"},
  {"name": "notes.txt", "type": "file", "size": 512, "last_modified": "2026-08-01T00:00:00Z"},
  {"name": "docs", "type": "dir", "size": 0, "last_modified": "2026-07-15T12:00:00Z"}
]
```

## Exit codes

| Condition | Exit code | stdout/stderr |
|-----------|-----------|----------------|
| Success (including empty result after `--min-size` filtering) | `0` | Table or JSON on stdout |
| Path does not exist | non-zero (same generic code as all errors below) | Clear "path not found" message on stderr |
| Path exists but not readable (permissions) | non-zero (same code) | Clear "permission denied" message on stderr, distinct text from not-found |
| Path exists, readable, not a valid tar archive | non-zero (same code) | Clear "not a valid tar archive" message on stderr, distinct text |
| Archive is valid but has zero members | non-zero (same code) | Clear "archive is empty" message on stderr |
| `--min-size` is non-numeric or negative | non-zero (same code) | Clear "invalid --min-size" message on stderr, validated before opening the archive |

Per FR-011a, all error conditions share one generic non-zero exit code; only message text (on
stderr) distinguishes the cause. No stack traces or internal paths are shown (Principle IV).

## Filesystem guarantee

Under every code path — success or error — `tarpeek` MUST NOT create, write, or modify any file,
directory, or symlink on the filesystem (FR-007). This is verified in tests by snapshotting a
temp working directory's contents before and after each invocation and asserting no diff.
