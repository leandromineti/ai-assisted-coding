# tarpeek

Inspect a tar archive's contents — name, type, size, and last-modified time for every
member — without extracting anything to disk.

## Install

```bash
pip install .
```

This places the `tarpeek` command on your `PATH`.

## Usage

```bash
tarpeek PATH [--min-size BYTES] [--json]
```

| Argument     | Required | Description |
|--------------|----------|-------------|
| `PATH`       | Yes      | Path to the tar archive to summarize (`.tar`, `.tar.gz`, `.tar.bz2`, `.tar.xz`). |
| `--min-size` | No       | Only show members with size >= `BYTES` (non-negative integer). |
| `--json`     | No       | Emit a JSON array instead of a table. |

### Examples

List every member, sorted by size descending:

```bash
tarpeek archive.tar
```

Only show members at least 4096 bytes:

```bash
tarpeek archive.tar --min-size 4096
```

Emit JSON for scripting:

```bash
tarpeek archive.tar --json
```

```json
[
  {"name": "big.log", "type": "file", "size": 4096, "last_modified": "2026-08-10T09:15:00Z"}
]
```

## Behavior

- Never writes, extracts, or modifies anything on disk — read-only against the input archive.
- All error conditions (missing path, unreadable path, non-tar file, empty archive, invalid
  `--min-size`) exit with the same non-zero status; the stderr message text tells you which one
  occurred.
