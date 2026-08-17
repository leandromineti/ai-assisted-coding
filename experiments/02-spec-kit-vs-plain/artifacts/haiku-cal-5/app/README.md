# tarpeek

A lightweight Python CLI tool to inspect and summarize tar archive contents without extracting them.

## Features

- **No extraction**: Inspect archives safely without writing to disk
- **Rich metadata**: View filename, type (file/dir/symlink), size, and modification date
- **Size filtering**: Use `--min-size` to show only members above a threshold
- **Machine-readable output**: Export as JSON with `--json`
- **Sorted by size**: Results ordered by size descending by default
- **Error handling**: Clear errors for invalid archives and missing files

## Installation

Install from the repository:

```bash
pip install -e .
```

Or install directly:

```bash
pip install .
```

After installation, run `tarpeek` from any directory:

```bash
tarpeek /path/to/archive.tar
```

## Usage

### Basic usage

```bash
tarpeek archive.tar
```

Output:
```
Name                Type    Size Last Modified
--------------------------------
dir/file2.txt       file     2400 2026-08-17T12:34:56
file1.txt           file       13 2026-08-17T12:34:56
dir/                dir         0 2026-08-17T12:34:56
link                symlink     0 2026-08-17T12:34:56
```

### Filter by minimum size

Show only members 1 KB or larger:

```bash
tarpeek archive.tar --min-size 1024
```

### JSON output

Export as JSON for scripting:

```bash
tarpeek archive.tar --json
```

Output:
```json
[
  {
    "name": "dir/file2.txt",
    "type": "file",
    "size": 2400,
    "mtime": "2026-08-17T12:34:56"
  },
  ...
]
```

### Combine options

```bash
tarpeek archive.tar --min-size 1024 --json
```

## Exit Codes

- **0**: Success
- **1**: Error (invalid archive, file not found, or unexpected error)

## Error Messages

- `Not a valid tar archive`: The file is not a valid tar archive
- `Archive not found`: The specified archive path does not exist
- `Empty archive.`: The archive contains no members (success case)

## Testing

Run the test suite:

```bash
python -m pytest test_tarpeek.py -v
```

Or using unittest directly:

```bash
python -m unittest test_tarpeek -v
```

## Implementation Details

- Supports all tar formats (gzip, bzip2, xz via tarfile auto-detection with `r:*`)
- Member types: file, dir, symlink, other
- Sizes are in bytes; use standard tools like `du` to convert
- Never writes to the filesystem—only reads from the tar archive
- Efficient streaming: processes members without loading entire archive into memory

## Author

Claude
