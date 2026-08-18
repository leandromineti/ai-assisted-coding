# logpeek

A Python CLI tool to summarize structured log files with support for multiple timestamp formats and log levels.

## Features

- **Parse multiple log formats**: Supports ISO 8601 timestamps (e.g., `2026-06-10T09:00:00+00:00`) and Unix timestamps
- **Count by log level**: Aggregates entries by DEBUG, INFO, WARNING, ERROR, and CRITICAL
- **Time span analysis**: Reports the first and last event timestamps from the log file
- **Top loggers**: Identifies the five most frequent logger names
- **Level filtering**: Filter output to a specific log level using `--level`
- **JSON output**: Machine-readable JSON format with `--json`
- **Batch processing**: Analyze multiple files in one command
- **Robust parsing**: Gracefully skips malformed lines and special markers
- **Clear error handling**: Helpful error messages for empty files and non-log files

## Installation

Install from the current directory:

```bash
pip install -e .
```

This makes the `logpeek` command available system-wide.

## Usage

### Basic usage

Summarize a single log file:

```bash
logpeek samples/web_api.log
```

Output:
```
File: samples/web_api.log
  Total lines: 17
  Levels: DEBUG=2, INFO=5, WARNING=2, ERROR=2, CRITICAL=1
  Time span: 2026-06-10T09:00:00+00:00 to 2026-06-10T09:12:00+00:00
  Top loggers: api.http:(5), api.auth:(2), api.db:(2), api.cache:(1)
```

### Multiple files

Analyze several files at once:

```bash
logpeek samples/web_api.log samples/legacy_daemon.log samples/mixed_ingest.log
```

### Filter by level

Show statistics only for entries matching a specific level:

```bash
logpeek --level ERROR samples/web_api.log
```

### JSON output

Get machine-readable output:

```bash
logpeek --json samples/web_api.log
```

Output:
```json
{
  "file": "samples/web_api.log",
  "total_lines": 17,
  "levels": {
    "DEBUG": 2,
    "INFO": 5,
    "WARNING": 2,
    "ERROR": 2,
    "CRITICAL": 1
  },
  "time_span": {
    "first": "2026-06-10T09:00:00+00:00",
    "last": "2026-06-10T09:12:00+00:00"
  },
  "top_loggers": {
    "api.http:": 5,
    "api.auth:": 2,
    "api.db:": 2,
    "api.cache:": 1
  }
}
```

### Multiple files with JSON

When processing multiple files with `--json`, output is an array:

```bash
logpeek --json samples/*.log
```

## Log Format

logpeek expects lines with the following format:

```
<timestamp> <level> <logger>: [message]
```

- **timestamp**: Either ISO 8601 (e.g., `2026-06-10T09:00:00+00:00`) or Unix timestamp (seconds since epoch)
- **level**: One of DEBUG, INFO, WARNING, ERROR, CRITICAL
- **logger**: Logger name (typically dot-separated like `api.http`)

Examples:
```
2026-06-10T09:00:00+00:00 INFO api.http: listening on :8080
1735689600 DEBUG daemon.loop: gc
2026-02-01T12:00:00+05:30 ERROR ingest.a: parse fail row 88
```

## Behavior

- **Empty files**: Raises an error (non-zero exit code)
- **Non-log files**: Raises an error if no valid log entries found
- **Malformed lines**: Skipped silently; reported in line count
- **Timestamps**: Lines without valid timestamps are not included in time-span calculation
- **File modification**: The tool never modifies input files

## Error Handling

The tool exits with code 1 if:
- Any requested file is empty
- Any requested file contains no valid log entries
- A file cannot be read (permissions, doesn't exist)

For partial failures (e.g., processing multiple files where one fails), the summary is printed for valid files and exit code 1 is returned.

## Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

Or using unittest:

```bash
python -m unittest discover tests -v
```

## Project Structure

```
logpeek/
  __init__.py       # Package metadata
  cli.py            # Command-line interface
  parser.py         # Log parsing and summarization logic
tests/
  test_parser.py    # Parser and summarization tests
  test_cli.py       # CLI integration tests
setup.py            # Package installation configuration
samples/            # Example log files
```
