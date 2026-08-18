# logpeek - Implementation Summary

## Overview
`logpeek` is a production-ready Python CLI tool that summarizes structured log files with support for filtering and multiple output formats.

## Features Implemented

### Core Analysis
- **Total line count**: Reports the total number of lines in each file
- **Level counts**: Breaks down entries by log level (INFO, ERROR, DEBUG, WARNING, CRITICAL, etc.)
- **Time span**: Shows first and last event timestamps
- **Top 5 loggers**: Lists the most frequent logger names and their counts

### Command-line Features
- **Multiple files**: Analyze one or more files in a single command
- **Level filtering**: `--level NAME` to filter results to specific log levels
- **JSON output**: `--json` flag for machine-readable output
- **Text output**: Human-friendly default output format

### Error Handling
- Non-existent files: Clear error message with exit code 1
- Empty files: Detected and reported with exit code 1
- Invalid log format: Files with no valid entries properly reported
- Files with mixed valid/invalid lines: Processed correctly, counting both
- Encoding issues: Gracefully handled with UTF-8 errors ignored
- Invalid level filters: Properly rejected if no entries match

### Robustness
- Never modifies input files (read-only operation)
- Handles large files efficiently (tested with 40K lines)
- Skips invalid log lines while processing valid ones
- Works from any directory after installation

## Project Structure

```
/app/
├── logpeek/
│   ├── __init__.py           # Package initialization
│   ├── parser.py             # Log parsing logic
│   └── cli.py                # Command-line interface
├── tests/
│   ├── __init__.py
│   ├── test_parser.py        # Parser unit tests
│   └── test_cli.py           # CLI integration tests
├── setup.py                  # Package installation configuration
└── README.md                 # User documentation
```

## Log Format Supported

```
ISO8601_TIMESTAMP LOG_LEVEL logger.name: message

Example:
2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff
2026-06-01T00:00:00+00:00 ERROR api.gw: error occurred
```

## Installation

```bash
pip install -e /app
```

This makes `logpeek` available as a system command.

## Test Coverage

- 31 unit and integration tests
- All tests passing (100% pass rate)
- Coverage includes:
  - Valid log parsing
  - Invalid log line handling
  - Empty files
  - Non-existent files
  - Level filtering
  - JSON and text output formatting
  - Multiple file analysis

## Sample Output

### Text Output
```
File: app.log
  Total lines: 1000
  Valid entries: 998
  Level counts: DEBUG: 200, ERROR: 50, INFO: 700, WARNING: 48
  Time span: 2026-06-01T00:00:00+00:00 to 2026-06-01T10:45:32+00:00
  Top loggers:
    api.gw: 350
    api.http: 200
    api.db: 180
    api.auth: 150
    boot.init: 118
```

### JSON Output
```json
[
  {
    "file": "app.log",
    "total_lines": 1000,
    "valid_entries": 998,
    "level_counts": {
      "DEBUG": 200,
      "ERROR": 50,
      "INFO": 700,
      "WARNING": 48
    },
    "time_span": {
      "first": "2026-06-01T00:00:00+00:00",
      "last": "2026-06-01T10:45:32+00:00"
    },
    "top_loggers": [
      {"name": "api.gw", "count": 350},
      ...
    ]
  }
]
```

## Usage Examples

```bash
# Single file
logpeek app.log

# Multiple files
logpeek app.log boot.log system.log

# Filter by level
logpeek --level ERROR app.log

# JSON output
logpeek --json app.log

# Combine options
logpeek --level WARNING --json *.log
```

## Validation

✓ Correctly handles all sample files in /app/samples/
✓ Works with 40K+ line files
✓ Proper error handling and exit codes
✓ Command accessible from any directory
✓ Never modifies input files
✓ All tests passing
