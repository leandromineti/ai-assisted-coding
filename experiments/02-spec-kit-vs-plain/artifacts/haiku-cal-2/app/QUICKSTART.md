# tarpeek Quick Start

## Installation

The package is already installed via `pip install -e .`. The `tarpeek` command is available on your PATH.

```bash
tarpeek --help
```

## Common usage patterns

### Basic summary
```bash
tarpeek archive.tar
```
Shows all members in a table, sorted by size (largest first).

### Filter by size
```bash
tarpeek archive.tar --min-size 10000
```
Only shows members >= 10,000 bytes.

### Machine-readable output
```bash
tarpeek archive.tar --json
```
Output as JSON for scripting.

### Combine filters and options
```bash
tarpeek archive.tar --min-size 1000000 --json
```

## Supported formats

- `.tar` (uncompressed)
- `.tar.gz` (gzip)
- `.tar.bz2` (bzip2)
- `.tar.xz` (xz/lzma)

## Error handling

| Scenario | Exit code | Message |
|----------|-----------|---------|
| File doesn't exist | 1 | "File not found: ..." |
| Invalid tar archive | 1 | "Not a valid tar archive: ..." |
| Empty archive | 1 | "Archive is empty" |

## Running tests

```bash
pytest tests/
```

All 11 tests pass.
