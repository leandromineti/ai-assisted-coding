# logpeek

A Python CLI tool for analyzing and summarizing structured log files.

## Features

- **Log file parsing** — Supports multiple timestamp formats:
  - ISO 8601 with timezone offsets (e.g., `2026-06-10T09:00:00+00:00`)
  - Unix timestamps (seconds since epoch)
- **Comprehensive statistics**:
  - Total line count
  - Counts per log level (INFO, DEBUG, WARNING, ERROR, etc.)
  - Time span (first to last event)
  - Top 5 most frequent logger names
- **Filtering** — Filter logs by level with `--level NAME`
- **Machine-readable output** — JSON output with `--json` flag
- **Error handling** — Clear errors for invalid or empty files with proper exit codes
- **Non-invasive** — Never modifies input files

## Installation

```bash
pip install -e .
```

After installation, `logpeek` will be available as a command from any directory.

## Usage

### Basic usage

```bash
logpeek path/to/logfile.log
```

### Multiple files

```bash
logpeek file1.log file2.log file3.log
```

### Filter by log level

```bash
logpeek logfile.log --level ERROR
```

Only logs with the specified level will be counted in the output.

### JSON output

```bash
logpeek logfile.log --json
```

Outputs structured JSON for programmatic consumption.

## Log Format Support

logpeek recognizes log lines in the following format:

```
<TIMESTAMP> <LEVEL> <LOGGER>: <MESSAGE>
```

Where:
- **TIMESTAMP**: ISO 8601 (with timezone, e.g., `2026-06-10T09:00:00+00:00`) or Unix timestamp (e.g., `1735689600`)
- **LEVEL**: Log level name (INFO, DEBUG, WARNING, ERROR, etc.)
- **LOGGER**: Logger name, can contain dots (e.g., `app.main`, `daemon.loop`)
- **MESSAGE**: Log message (anything after the colon)

Special lines:
- Lines starting with `--` are treated as markers and ignored
- Empty lines are skipped
- Lines that don't match the expected format cause the file to be rejected as invalid

## Examples

### Example 1: Analyze a web API log

```bash
$ logpeek samples/web_api.log
samples/web_api.log:
  Total lines: 5
  Level counts: {'INFO': 2, 'DEBUG': 1, 'WARNING': 1}
  Time span: 2026-06-10T09:00:00+00:00 to 2026-06-10T09:02:00-03:00
  Top loggers: api.http, api.auth, api.db
```

### Example 2: Check for errors

```bash
$ logpeek samples/web_api.log --level ERROR
samples/web_api.log:
  Total lines: 5
  Level counts: {}
  Time span: N/A
  Top loggers: []
```

### Example 3: JSON output

```bash
$ logpeek samples/web_api.log --json
[
  {
    "file": "samples/web_api.log",
    "valid": true,
    "total_lines": 5,
    "level_counts": {
      "INFO": 2,
      "DEBUG": 1,
      "WARNING": 1
    },
    "time_span": "2026-06-10T09:00:00+00:00 to 2026-06-10T09:02:00-03:00",
    "top_loggers": [
      "api.http",
      "api.auth",
      "api.db"
    ]
  }
]
```

## Error Handling

### Empty file

```bash
$ logpeek samples/empty.log
samples/empty.log:
  Total lines: 0
  Error: Empty file
```

Exit code: **1**

### Invalid log file

```bash
$ logpeek some_text_file.txt
some_text_file.txt:
  Total lines: 3
  Error: Not a valid log file
```

Exit code: **1**

### Nonexistent file

```bash
$ logpeek /nonexistent/file.log
/nonexistent/file.log:
  Total lines: 0
  Error: Not a valid log file
```

Exit code: **1**

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

Or using unittest:

```bash
python -m unittest discover tests/
```

## Development

The package is structured as:

- `logpeek/` — Main package
  - `__init__.py` — Package metadata
  - `parser.py` — Log parsing logic
  - `cli.py` — Command-line interface
- `tests/` — Test suite
  - `test_parser.py` — Parser unit tests
  - `test_cli.py` — CLI integration tests
- `samples/` — Example log files
