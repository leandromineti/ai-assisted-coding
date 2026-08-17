# tarpeek

A lightweight CLI tool to summarize tar archive contents without extracting them.

## Features

- **No extraction**: Read archive metadata without decompressing or writing to disk
- **Per-member table**: Display name, type (file/dir/symlink), size, and last-modified date
- **Filtering**: Filter members by minimum size with `--min-size`
- **Machine-readable output**: JSON format with `--json`
- **Sorted by size**: Results sorted by size in descending order
- **Error handling**: Clear errors for invalid archives and empty files with non-zero exit codes

## Installation

```bash
pip install -e .
```

This creates a `tarpeek` command available from any directory.

## Usage

### Basic usage

```bash
tarpeek archive.tar
```

Output:
```
Name                  Type      Size (bytes)  Last-Modified
────────────────────  ────────  ────────────  ──────────────────────
mydir/file_large.txt  file      12345         2026-08-17 10:30:45
mydir/file.txt        file      156           2026-08-17 10:30:45
mydir/                dir       0             2026-08-17 10:30:44
```

### Filter by minimum size

```bash
tarpeek archive.tar --min-size 1000
```

Only shows members with size ≥ 1000 bytes.

### JSON output

```bash
tarpeek archive.tar --json
```

Output:
```json
[
  {
    "name": "mydir/file_large.txt",
    "type": "file",
    "size": 12345,
    "mtime": "2026-08-17T10:30:45"
  },
  {
    "name": "mydir/file.txt",
    "type": "file",
    "size": 156,
    "mtime": "2026-08-17T10:30:45"
  },
  {
    "name": "mydir/",
    "type": "dir",
    "size": 0,
    "mtime": "2026-08-17T10:30:44"
  }
]
```

### Combine filters and formats

```bash
tarpeek archive.tar --min-size 1000 --json
```

## Error Handling

- **Invalid archive**: Prints `Error: Not a valid tar archive: <path>` and exits with code 1
- **Missing file**: Prints `Error: Archive not found: <path>` and exits with code 1
- **Empty archive**: Prints `Error: Archive is empty` and exits with code 1
- **No matches after filtering**: Prints `Error: No members found.` and exits with code 1

## Testing

```bash
pip install pytest pytest-cov
pytest
```

Run with coverage:
```bash
pytest --cov=tarpeek
```

## Requirements

- Python 3.8+
- `tabulate` (for pretty table formatting)

The standard library `tarfile` module handles all archive operations.
