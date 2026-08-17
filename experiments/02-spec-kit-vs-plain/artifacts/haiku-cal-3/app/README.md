# tarpeek

A lightweight Python CLI tool that summarizes the contents of tar archives without extracting them.

## Features

- **Non-destructive**: Never writes to the filesystem
- **Multiple formats**: View results as a formatted table or machine-readable JSON
- **Flexible filtering**: Filter members by minimum size
- **Smart sorting**: Always sorts results by size in descending order
- **Type detection**: Identifies files, directories, symlinks, and other member types
- **Clear error handling**: Provides helpful error messages for invalid archives or missing files
- **Cross-platform**: Works on any system with Python 3.8+

## Installation

### From source

```bash
pip install -e .
```

This installs the `tarpeek` command globally on your system.

## Usage

### Basic usage

```bash
tarpeek archive.tar
```

Displays a formatted table with member information:

```
╒════════════════════╤══════╤══════════════╤════════╤──────────────────────────╕
│ Name               │ Type │ Size (bytes) │ Size   │ Modified                 │
╞════════════════════╪══════╪══════════════╪════════╪══════════════════════════╡
│ large_file.bin     │ file │       102400 │ 100KB  │ 2026-08-17T12:34:56      │
├────────────────────┼──────┼──────────────┼────────┼──────────────────────────┤
│ data/config.json   │ file │        2048  │ 2KB    │ 2026-08-17T10:20:30      │
├────────────────────┼──────┼──────────────┼────────┼──────────────────────────┤
│ scripts/           │ dir  │           0  │ 0B     │ 2026-08-17T09:15:00      │
╘════════════════════╧══════╧══════════════╧════════╧══════════════════════════╛
```

### Supports all tar formats

Works with `.tar`, `.tar.gz`, `.tar.bz2`, `.tar.xz`, and other formats:

```bash
tarpeek archive.tar.gz
tarpeek archive.tar.bz2
tarpeek archive.tar.xz
```

### JSON output

For machine-readable output:

```bash
tarpeek --json archive.tar
```

Example output:

```json
[
  {
    "name": "large_file.bin",
    "type": "file",
    "size": 102400,
    "modified": "2026-08-17T12:34:56"
  },
  {
    "name": "data/config.json",
    "type": "file",
    "size": 2048,
    "modified": "2026-08-17T10:20:30"
  }
]
```

### Filter by minimum size

Show only members at least 1 KB in size:

```bash
tarpeek --min-size 1024 archive.tar
```

### Combine options

```bash
tarpeek --json --min-size 10240 archive.tar.gz
```

## Exit codes

- `0`: Success
- `1`: Error (invalid archive, file not found, empty archive after filtering)
- `130`: Interrupted by user (Ctrl+C)

## Error handling

The tool provides clear error messages for common issues:

- **"Archive not found"**: The specified file doesn't exist
- **"Invalid tar archive"**: The file exists but isn't a valid tar format
- **"Archive is empty"**: The archive contains no members
- **"No members match filter"**: All members were filtered out by `--min-size`

## Member types

The tool recognizes the following member types:

- `file`: Regular file
- `dir`: Directory
- `symlink`: Symbolic link
- `hardlink`: Hard link
- `other`: Other types (rare)

## Building from source

Requirements:
- Python 3.8 or later
- `tabulate` package (for table formatting)

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest tests/
```

## Project structure

```
tarpeek/
├── src/tarpeek/
│   ├── __init__.py
│   ├── core.py        # Core archive reading logic
│   └── cli.py         # Command-line interface
├── tests/
│   ├── test_core.py   # Unit tests for core functionality
│   └── test_cli.py    # Integration tests for CLI
├── setup.py
└── README.md
```

## Examples

### Analyze a large archive

```bash
$ tarpeek myproject.tar.gz
╒═══════════════════════════════════╤════════╤═════════════╤═══════╤════════════════════╕
│ Name                              │ Type   │ Size (bytes)│ Size  │ Modified           │
╞═══════════════════════════════════╪════════╪═════════════╪═══════╪════════════════════╡
│ data/big_database.db              │ file   │   536870912 │ 512MB │ 2026-08-15T14:22:11│
├───────────────────────────────────┼────────┼─────────────┼───────┼────────────────────┤
│ src/app.py                        │ file   │       45823 │ 44KB  │ 2026-08-17T10:30:00│
├───────────────────────────────────┼────────┼─────────────┼───────┼────────────────────┤
│ lib/                              │ dir    │           0 │ 0B    │ 2026-08-10T08:00:00│
╘═══════════════════════════════════╧════════╧═════════════╧═══════╧════════════════════╛
```

### Find only large files

```bash
$ tarpeek --json --min-size 1048576 archive.tar | jq '.[] | select(.type == "file")'
{
  "name": "data/big_database.db",
  "type": "file",
  "size": 536870912,
  "modified": "2026-08-15T14:22:11"
}
```

### Integration with other tools

```bash
# Count files in archive
tarpeek --json archive.tar | jq 'length'

# Total size of all files
tarpeek --json archive.tar | jq '[.[] | select(.type == "file") | .size] | add'

# List only symlinks
tarpeek --json archive.tar | jq '.[] | select(.type == "symlink")'
```

## License

MIT
