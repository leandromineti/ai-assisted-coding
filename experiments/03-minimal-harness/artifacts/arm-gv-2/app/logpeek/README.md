# logpeek

A Python CLI tool to summarize structured log files.

## Features

- Analyzes one or more log files
- Counts total lines and log levels
- Reports time span (first to last event)
- Lists the five most frequent logger names
- Filters by log level with `--level`
- Machine-readable JSON output with `--json`
- Graceful error handling for non-log and empty files

## Installation

From the project directory:

```bash
pip install -e .
```

This installs the `logpeek` command globally.

## Usage

### Basic usage

```bash
logpeek path/to/log.log
```

Output:
```
File: path/to/log.log
Total lines: 6
Levels: DEBUG: 1, INFO: 4, WARNING: 1
Time span: 2026-05-31T23:58:00+00:00 to 2026-05-31T23:58:07+00:00
Top loggers: boot.init, boot.svc
```

### Multiple files

```bash
logpeek file1.log file2.log file3.log
```

### Filter by level

```bash
logpeek --level INFO log.log
```

Only counts and displays entries with INFO level. Time span and logger names reflect filtered entries.

### JSON output

```bash
logpeek --json log.log
```

Output:
```json
[
  {
    "file": "log.log",
    "total_lines": 6,
    "levels": {
      "DEBUG": 1,
      "INFO": 4,
      "WARNING": 1
    },
    "time_span": {
      "start": "2026-05-31T23:58:00+00:00",
      "end": "2026-05-31T23:58:07+00:00"
    },
    "top_loggers": [
      "boot.init",
      "boot.svc"
    ]
  }
]
```

## Log Format

The tool expects structured logs in the following format:

```
TIMESTAMP LEVEL LOGGER: MESSAGE
```

- **TIMESTAMP:** ISO8601 format with timezone (e.g., `2026-05-31T23:58:00+00:00`)
- **LEVEL:** All-caps keywords: `INFO`, `DEBUG`, `ERROR`, `WARNING`, `CRITICAL`
- **LOGGER:** Dot-separated hierarchical name (e.g., `boot.init`, `api.gw`)
- **MESSAGE:** Free-form text after the colon

Example:
```
2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff
2026-05-31T23:58:01+00:00 DEBUG boot.svc: unit graph built
2026-05-31T23:58:02+00:00 ERROR api.gw: connection failed
```

## Error Handling

- **Non-existent files:** Error message and exit code 1
- **Non-log files:** Error message if file contains no valid log lines and exit code 1
- **Empty files:** Treated as valid logs with 0 lines, exit code 0
- **Files with mixed valid/invalid lines:** Skips invalid lines and processes valid ones
- **Non-UTF-8 encoding:** Replaced with Unicode replacement character, processing continues

## Testing

```bash
pytest logpeek/tests/
```

## Exit Codes

- `0`: Success
- `1`: Error (file not found, not a log file, or other I/O error)
