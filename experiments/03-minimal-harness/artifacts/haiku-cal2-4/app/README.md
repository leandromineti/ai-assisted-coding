# logpeek

A Python CLI tool to summarize structured log files. Given one or more log file paths, `logpeek` prints statistics about each file including total lines, counts per log level, time span coverage, and the five most frequent logger names.

## Features

- **Parse ISO 8601 timestamps** in structured logs
- **Count log levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Track time span**: first to last event in each file
- **Identify top loggers**: shows the 5 most frequent logger names and their counts
- **Filter by level**: use `--level` to show only entries at a specific level
- **JSON output**: use `--json` for machine-readable output
- **Error handling**: clear error messages for non-log files, missing files, and malformed input
- **Never modifies input files**: read-only operation

## Installation

Install from the current directory:

```bash
pip install -e .
```

This installs the `logpeek` command globally, available from any directory.

## Usage

### Basic usage

Summarize a single log file:

```bash
logpeek /path/to/log.log
```

Output:
```
File: /path/to/log.log
Total lines: 40000
  DEBUG: 8000
  INFO: 20000
  WARNING: 8000
  ERROR: 4000
Time span: 2026-06-01T00:00:00+00:00 to 2026-06-04T05:46:33+00:00
Top 5 loggers:
  api.gw: 10000
  api.auth: 8000
  api.http: 6000
  api.db: 5000
  system.core: 5000
```

### Multiple files

Summarize multiple log files:

```bash
logpeek file1.log file2.log file3.log
```

### Filter by log level

Show only entries at a specific level:

```bash
logpeek log.log --level INFO
```

This counts and displays only INFO entries, while still reporting the time span of all valid log entries in the file.

### JSON output

Get machine-readable output:

```bash
logpeek log.log --json
```

Output:
```json
[
  {
    "file": "/path/to/log.log",
    "total_lines": 40000,
    "level_counts": {
      "DEBUG": 8000,
      "INFO": 20000,
      "WARNING": 8000,
      "ERROR": 4000
    },
    "time_span": {
      "start": "2026-06-01T00:00:00+00:00",
      "end": "2026-06-04T05:46:33+00:00"
    },
    "top_loggers": [
      {"name": "api.gw", "count": 10000},
      {"name": "api.auth", "count": 8000},
      {"name": "api.http", "count": 6000},
      {"name": "api.db", "count": 5000},
      {"name": "system.core", "count": 5000}
    ]
  }
]
```

## Log Format

The tool expects structured logs with the following format:

```
<ISO8601-TIMESTAMP> <LEVEL> <LOGGER-NAME>: <MESSAGE>
```

Example:
```
2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff
2026-06-01T00:00:14+00:00 ERROR api.gw: evt 2 code 6
```

**Required fields:**
- ISO 8601 timestamp (e.g., `2026-05-31T23:58:00+00:00`)
- Log level: one of DEBUG, INFO, WARNING, ERROR, CRITICAL
- Logger name (e.g., `boot.init`, `api.gw`): alphanumeric, dots, dashes

## Error Handling

### Non-log files

If a file contains no valid log entries:

```
$ logpeek notlog.txt
Error: File does not contain valid log entries: notlog.txt
```

Exit code: 1

### Missing files

```
$ logpeek /nonexistent.log
Error: File not found: /nonexistent.log
```

Exit code: 1

### Empty files

Empty files are valid and report 0 total lines:

```
$ logpeek empty.log
File: empty.log
Total lines: 0
```

Exit code: 0

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

Or using unittest:

```bash
python -m unittest discover tests/
```

The test suite includes:
- **Parser tests**: ISO 8601 parsing, level detection, logger name extraction
- **Processor tests**: file handling, error cases, empty files, invalid lines, filtering
- **CLI tests**: command-line argument parsing, output formatting, multiple files, exit codes
- **Integration tests**: end-to-end CLI testing with real files

## Development

The project structure:

```
logpeek/
  __init__.py        # Package initialization
  cli.py             # Command-line interface
  parser.py          # Log parsing logic
  processor.py       # File processing
  formatter.py       # Output formatting (text and JSON)
tests/
  test_parser.py     # Parser unit tests
  test_processor.py  # Processor unit tests
  test_cli.py        # CLI integration tests
setup.py             # Package configuration
README.md            # This file
```
