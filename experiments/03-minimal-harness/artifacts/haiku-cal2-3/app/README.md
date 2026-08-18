# logpeek

A Python CLI tool for summarizing structured log files. Given one or more log files, `logpeek` analyzes each file and outputs:

- Total number of log lines
- Count of entries per log level
- Time span (first to last event)
- The five most frequent logger names

## Features

- **Flexible input**: Process one or multiple log files at once
- **Level filtering**: Use `--level NAME` to filter logs by severity
- **JSON output**: Use `--json` for machine-readable output
- **Robust parsing**: Handles malformed lines gracefully while extracting valid entries
- **Error handling**: Clear error messages for invalid files, empty files, and missing files
- **Non-destructive**: Never modifies input files

## Installation

### Using pip (from the project directory)

```bash
pip install -e .
```

After installation, the `logpeek` command will be available globally.

### Running tests

```bash
python -m pytest tests/
```

Or with unittest:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

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
logpeek --level ERROR mylog.log
```

### JSON output

```bash
logpeek --json mylog.log
```

### Combine filters and formats

```bash
logpeek --level WARNING --json app.log
```

## Log Format

The tool expects logs in the following format:

```
TIMESTAMP LEVEL LOGGER_NAME: message
```

Example:
```
2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff
2026-05-31T23:58:01+00:00 DEBUG boot.svc: unit graph built
2026-06-01T00:00:14+00:00 ERROR api.gw: evt 2 code 6
```

- **TIMESTAMP**: ISO 8601 format with timezone (e.g., `2026-05-31T23:58:00+00:00`)
- **LEVEL**: Log severity level (INFO, DEBUG, WARNING, ERROR, CRITICAL, etc.)
- **LOGGER_NAME**: Name of the logger component
- **message**: Log message (may contain colons and special characters)

## Output Formats

### Text Output (default)

```
/path/to/logfile.log
============================================================
Total lines: 40000
Level counts:
  CRITICAL: 500
  DEBUG: 8000
  ERROR: 4500
  INFO: 25000
  WARNING: 2000
Time span: 2026-06-01T00:00:00+00:00 to 2026-06-04T05:46:33+00:00
Top 5 loggers:
  api.gw: 15000
  api.http: 10000
  api.auth: 8000
  api.db: 5000
  api.cache: 2000
```

### JSON Output

```json
{
  "file": "/path/to/logfile.log",
  "total_lines": 40000,
  "level_counts": {
    "CRITICAL": 500,
    "DEBUG": 8000,
    "ERROR": 4500,
    "INFO": 25000,
    "WARNING": 2000
  },
  "time_span": {
    "first": "2026-06-01T00:00:00+00:00",
    "last": "2026-06-04T05:46:33+00:00"
  },
  "top_loggers": [
    {"name": "api.gw", "count": 15000},
    {"name": "api.http", "count": 10000},
    {"name": "api.auth", "count": 8000},
    {"name": "api.db", "count": 5000},
    {"name": "api.cache", "count": 2000}
  ]
}
```

## Error Handling

The tool handles errors gracefully with clear messages and appropriate exit codes:

- **Empty file**: `Error: No valid log entries found in <filepath>`
- **Non-log file**: `Error: No valid log entries found in <filepath>`
- **File not found**: `Error: Cannot read file <filepath>: [No such file or directory]`
- **Invalid encoding**: `Error: File <filepath> is not valid UTF-8 text`

When processing multiple files, the tool continues processing remaining files even if one fails, but exits with a non-zero exit code (1) if any file had an error.

## Exit Codes

- `0`: Success (all files processed without errors)
- `1`: One or more files had errors

## Testing

The project includes comprehensive unit tests covering:

- Log entry parsing and validation
- Log summary aggregation
- Level filtering (including case-insensitive matching)
- Output formatting (text and JSON)
- CLI functionality (single/multiple files, filters, error cases)
- Edge cases (empty files, malformed lines, missing files)

Run tests with:

```bash
python -m pytest tests/ -v
```

Or:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## Project Structure

```
logpeek/
├── __init__.py           # Package initialization
├── cli.py               # Command-line interface
├── parser.py            # Log parsing and aggregation
└── formatter.py         # Output formatting
tests/
├── __init__.py
├── test_cli.py          # CLI tests
├── test_formatter.py    # Formatter tests
└── test_parser.py       # Parser and log entry tests
setup.py                # Package configuration
README.md              # This file
```

## Design Notes

- **Robust parsing**: Malformed lines within a log file don't cause failure; the tool skips them and continues parsing valid entries. Only files with no valid entries raise an error.
- **Case-insensitive level filtering**: The `--level` filter works case-insensitively (e.g., `--level error` matches `ERROR` entries).
- **Time span precision**: The time span is based on the first and last parsed entries, preserving the original timestamp format.
- **Logger name counting**: The tool counts exact logger name matches and returns the top 5 (or fewer if there are fewer unique names).
