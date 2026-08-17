# tarpeek

A Python CLI tool that summarizes the contents of a tar archive without extracting it.

## Features

- **No extraction**: Read archive metadata without touching the filesystem
- **Detailed summary**: For each member, shows name, type (file/dir/symlink), size in bytes, and last-modified date
- **Filtering**: Use `--min-size BYTES` to filter members by minimum size
- **Machine-readable output**: Use `--json` for programmatic access
- **Sorted by size**: Results are sorted largest-first by default
- **Clear error handling**: Validates input and exits cleanly on errors

## Installation

```bash
pip install -e .
```

This installs `tarpeek` as a command-line tool available from any directory.

## Usage

### Basic usage

```bash
tarpeek archive.tar
```

Output is displayed as a formatted table:

```
Name                Type      Size       Modified
--------------------  ----  ----------  -------------------
bigfile.bin           file  5000B       2023-08-18T12:00:00
file.txt              file  100B        2023-08-18T12:00:00
mydir/                dir   0B          2023-08-18T12:00:00
link                  symlink 0B        2023-08-18T12:00:00
```

### Filter by minimum size

```bash
tarpeek archive.tar --min-size 1000
```

Only members with at least 1000 bytes are shown.

### JSON output

```bash
tarpeek archive.tar --json
```

Returns machine-readable output:

```json
[
  {
    "name": "bigfile.bin",
    "type": "file",
    "size": 5000,
    "modified": "2023-08-18T12:00:00"
  },
  {
    "name": "file.txt",
    "type": "file",
    "size": 100,
    "modified": "2023-08-18T12:00:00"
  }
]
```

### Combined options

```bash
tarpeek archive.tar --min-size 500 --json
```

## Error Handling

### Not a tar archive

```
$ tarpeek nottar.txt
Error: Not a valid tar archive: [details]
```

Exit code: 1

### File not found

```
$ tarpeek missing.tar
Error: File not found: missing.tar
```

Exit code: 1

### Empty archive

```
$ tarpeek empty.tar
Error: Archive is empty
```

Exit code: 1

## Testing

Run the test suite:

```bash
pytest tests/
```

Or with coverage:

```bash
pytest tests/ --cov=tarpeek
```

## Development

The project structure:

```
.
├── setup.py              # Package configuration
├── README.md             # This file
├── tarpeek/
│   ├── __init__.py
│   └── cli.py            # Main CLI implementation
└── tests/
    ├── __init__.py
    └── test_tarpeek.py   # Test suite
```

## Implementation notes

- Uses Python's built-in `tarfile` module for reading archives
- Supports all tar formats (tar, tar.gz, tar.bz2, etc.) via `tarfile.open(..., "r:*")`
- Never writes to the filesystem
- Uses ISO 8601 format for timestamps
- Byte sizes are shown as raw integers, not human-readable (use `--json` for programmatic parsing)
