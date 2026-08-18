# logpeek

A Python CLI tool that summarizes structured log files.

## Features

- **Quick summaries**: Get total line count, level distribution, and time span for log files
- **Top loggers**: Identify the 5 most frequent logger names
- **Level filtering**: Filter results by log level (e.g., `--level ERROR`)
- **JSON output**: Machine-readable output with `--json`
- **Multiple files**: Analyze one or more log files in a single command
- **Error handling**: Clear error messages for malformed and empty files

## Installation

```bash
pip install -e .
```

This installs the `logpeek` command globally. You can then run it from any directory:

```bash
logpeek /path/to/log.log
```

## Usage

### Basic summary

```bash
logpeek app.log
```

Output:
```
File: app.log
Total lines: 1000
Levels: INFO: 650, ERROR: 150, WARNING: 200
Time span: 2026-06-01T00:00:00+00:00 to 2026-06-01T02:30:45+00:00
Top 5 loggers:
  api.gw: 320
  api.http: 200
  api.db: 150
  api.auth: 100
  boot.svc: 50
```

### Filter by level

```bash
logpeek app.log --level ERROR
```

Only shows entries at the specified level.

### JSON output

```bash
logpeek app.log --json
```

Returns structured JSON for programmatic use:
```json
[
  {
    "file": "app.log",
    "total_lines": 1000,
    "levels": {
      "INFO": 650,
      "ERROR": 150,
      "WARNING": 200,
      "CRITICAL": 0,
      "DEBUG": 0
    },
    "time_span": {
      "start": "2026-06-01T00:00:00+00:00",
      "end": "2026-06-01T02:30:45+00:00"
    },
    "top_loggers": [
      { "name": "api.gw", "count": 320 },
      { "name": "api.http", "count": 200 }
    ],
    "errors": []
  }
]
```

### Multiple files

```bash
logpeek app.log boot.log
```

Analyzes multiple files and outputs a summary for each.

### Combined options

```bash
logpeek app.log boot.log --level ERROR --json
```

## Log Format

Logpeek expects structured logs in the following format:

```
<ISO8601 timestamp> <LEVEL> <logger_name>: <message>
```

Example:
```
2026-06-01T00:00:00+00:00 INFO api.gw: evt 0 code 3
2026-06-01T00:00:07+00:00 ERROR api.http: Request timeout
2026-06-01T00:00:14+00:00 WARNING api.db: Slow query detected
```

Fields:
- **Timestamp**: ISO8601 format (e.g., `2026-06-01T00:00:00+00:00`)
- **Level**: Log level name (INFO, ERROR, WARNING, DEBUG, CRITICAL, etc.)
- **Logger**: Hierarchical logger name (e.g., `api.gw`, `boot.init`)
- **Message**: Log message (everything after the colon)

## Error Handling

### Empty files

```bash
$ logpeek empty.log
Error: Empty file: empty.log
```
Exit code: 1

### Missing files

```bash
$ logpeek nonexistent.log
Error: File not found: nonexistent.log
```
Exit code: 1

### Malformed lines

If a file contains lines that don't match the expected format, logpeek:
1. Skips the malformed lines
2. Processes valid lines normally
3. Reports warnings about each malformed line in the output

Example with `--json`:
```json
{
  "errors": [
    "Line 42: Invalid format (expected timestamp, level, logger)",
    "Line 89: Invalid timestamp format"
  ]
}
```

## Testing

Run the test suite:

```bash
pytest tests/
```

Tests cover:
- Parsing valid and malformed log files
- Level filtering
- Summary generation
- Top logger identification
- JSON output
- CLI argument handling
- Error cases (empty files, missing files, etc.)

## Development

The project structure:

```
logpeek/
├── __init__.py          # Package metadata
├── parser.py            # Log parsing and summarization logic
├── cli.py               # Command-line interface
samples/                 # Sample log files for testing
tests/
├── test_parser.py       # Parser unit tests
└── test_cli.py          # CLI integration tests
setup.py                 # Package configuration
README.md               # This file
```

## Implementation Notes

- Log files are never modified; all operations are read-only
- Invalid lines are logged as warnings but don't prevent processing
- Timestamps are parsed using Python's `datetime.fromisoformat()`
- Logger frequency is counted across all log entries (accounting for level filters)
- Time span is calculated from the first and last log entry after filtering
