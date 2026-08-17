# tarpeek

A Python CLI tool to summarize the contents of a tar archive without extracting it.

## Features

- **Non-destructive**: Never writes to the filesystem, only reads the archive
- **Quick overview**: View archive contents in a clean table format
- **Filtering**: Filter members by minimum size with `--min-size`
- **Structured output**: Export results as JSON with `--json`
- **Sorted**: Members displayed sorted by size (largest first)
- **Comprehensive**: Identifies file types (file, dir, symlink, hardlink, etc.)
- **Robust error handling**: Clear error messages with appropriate exit codes

## Installation

Install from the project directory:

```bash
pip install .
```

This makes the `tarpeek` command available globally.

## Usage

### Basic usage

```bash
tarpeek /path/to/archive.tar.gz
```

Output:
```
Name                Type       Size  Modified
-------------------------------------------------------
data.csv            file    1024000  2026-08-17 10:23:45
docs/                dir           0  2026-08-17 10:20:12
docs/guide.md       file      45230  2026-08-17 10:21:30
config.yaml         file        256  2026-08-17 10:19:45
```

### Filter by minimum size

```bash
tarpeek archive.tar --min-size 10000
```

Only shows members with size >= 10000 bytes.

### JSON output

```bash
tarpeek archive.tar --json
```

Output:
```json
[
  {
    "name": "data.csv",
    "type": "file",
    "size": 1024000,
    "mtime": "2026-08-17T10:23:45"
  },
  {
    "name": "docs/",
    "type": "dir",
    "size": 0,
    "mtime": "2026-08-17T10:20:12"
  }
]
```

### Combine options

```bash
tarpeek archive.tar.gz --min-size 5000 --json
```

## Exit Codes

- `0`: Success
- `1`: Error (invalid archive, file not found, empty archive, etc.)

## Architecture

- **`tarpeek/core.py`**: Core logic for reading and processing tar archives
- **`tarpeek/cli.py`**: Command-line interface
- **`test_tarpeek.py`**: Comprehensive test suite using pytest

## Testing

Run the test suite:

```bash
pytest test_tarpeek.py -v
```

Tests cover:
- Reading valid archives
- Sorting by size
- Type detection
- JSON output format
- Size filtering
- Error handling (nonexistent files, invalid archives, empty archives)
- Symlink detection
- Output formatting

## Requirements

- Python 3.7+
- No external dependencies (uses only stdlib: `tarfile`, `json`, `argparse`)
