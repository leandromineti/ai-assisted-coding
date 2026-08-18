# logpeek

A Python CLI tool that summarizes structured log files.

## Features

- Parse structured log files with ISO8601 timestamps
- Count log entries by severity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Display time span (first to last event timestamp)
- List the five most frequent logger names
- Filter by log level with `--level`
- JSON output with `--json` for machine-readable results
- Handles invalid files and encoding issues gracefully
- Never modifies input files

## Installation

```bash
pip install -e .
```

This installs the `logpeek` command, which can be run from any directory.

## Usage

### Basic usage

```bash
logpeek <file1> [file2] [file3] ...
```

Prints a summary for each log file:

```
/path/to/logfile:
  Total lines: 1000
  Levels: DEBUG (100), INFO (500), WARNING (200), ERROR (150), CRITICAL (50)
  Time span: 2026-06-01T00:00:00+00:00 to 2026-06-04T23:59:59+00:00
  Top 5 loggers:
    api.gateway: 400
    api.auth: 250
    api.database: 200
    api.http: 150
```

### Filter by log level

```bash
logpeek --level INFO /path/to/logfile
```

Only counts and displays entries at the specified level.

### JSON output

```bash
logpeek --json /path/to/logfile1 /path/to/logfile2
```

Outputs a JSON object with all results:

```json
{
  "/path/to/logfile1": {
    "total_lines": 1000,
    "levels": {
      "DEBUG": 100,
      "INFO": 500,
      "WARNING": 200,
      "ERROR": 150,
      "CRITICAL": 50
    },
    "time_span": {
      "first": "2026-06-01T00:00:00+00:00",
      "last": "2026-06-04T23:59:59+00:00"
    },
    "top_loggers": {
      "api.gateway": 400,
      "api.auth": 250
    }
  }
}
```

## Log Format

The tool expects logs in this format:

```
ISO8601_TIMESTAMP LEVEL logger_name: message
```

Example:
```
2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff
2026-05-31T23:58:01+00:00 DEBUG boot.svc: unit graph built
2026-05-31T23:58:02+00:00 WARNING boot.svc: swap disabled
```

## Error Handling

- **Non-existent files**: Displays an error and exits with code 1
- **Invalid log files** (files with no valid log entries): Displays an error and exits with code 1
- **Encoding issues**: Uses UTF-8 with error replacement to handle encoding problems
- **Empty files**: Displays a summary with all counts at zero
- **Multiple files with errors**: Displays results for valid files and errors for invalid ones, exits with code 1 if any file had an error

## Testing

Run the unit tests:

```bash
python -m unittest discover tests -v
```

Run the integration tests:

```bash
./check.sh
```

## Implementation Details

- **Parser** (`logpeek/parser.py`): Parses log files and extracts metrics
- **Formatter** (`logpeek/formatter.py`): Formats results as text or JSON
- **CLI** (`logpeek/cli.py`): Command-line interface
