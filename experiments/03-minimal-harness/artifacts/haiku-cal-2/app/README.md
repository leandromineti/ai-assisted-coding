# logpeek

A Python CLI tool to summarize structured log files with support for multiple timestamp formats and log levels.

## Features

- Parse structured log files with ISO 8601 and Unix timestamp formats
- Display summary statistics:
  - Total number of lines
  - Count of log entries per level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Time span covered (first to last event)
  - Five most frequent logger names
- Filter logs by level with `--level`
- Machine-readable JSON output with `--json`
- Handle edge cases gracefully (empty files, invalid files, corrupted lines)
- Non-zero exit codes on errors

## Installation

```bash
pip install .
```

After installation, the `logpeek` command will be available system-wide.

## Usage

```bash
# Summarize a single log file
logpeek samples/web_api.log

# Summarize multiple files
logpeek samples/web_api.log samples/legacy_daemon.log

# Filter by log level
logpeek --level INFO samples/web_api.log

# Output as JSON
logpeek --json samples/web_api.log

# Combine filters and JSON output
logpeek --json --level ERROR samples/web_api.log
```

## Log Format

The tool supports two timestamp formats:

### ISO 8601 with timezone
```
2026-06-10T09:00:00+00:00 INFO api.http: listening on :8080
2026-06-10T09:02:00-03:00 WARNING api.db: slow query 300ms
```

### Unix timestamp (32-bit)
```
1735689600 INFO daemon.boot: first light
1735693200 DEBUG daemon.loop: gc
```

Each log line must have:
1. Timestamp (ISO 8601 or Unix)
2. Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
3. Logger name
4. Optional message

## Error Handling

- **File not found**: Prints error message and exits with code 1
- **Invalid log file**: Prints error message and exits with code 1
- **Empty file**: Prints error message and exits with code 1
- **Directory instead of file**: Prints error message and exits with code 1
- **Read errors**: Prints error message and exits with code 1

When processing multiple files, the tool processes all files and exits with code 1 if any encountered errors.

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Or use unittest
python -m unittest discover tests/

# Run specific test file
python -m unittest tests.test_parser
python -m unittest tests.test_analyzer
python -m unittest tests.test_cli
python -m unittest tests.test_integration
```

## Development

The project structure:

- `logpeek/` - Main package
  - `cli.py` - Command-line interface
  - `parser.py` - Log line parsing logic
  - `analyzer.py` - Analysis and statistics
  - `__init__.py` - Package initialization
- `tests/` - Test suite
- `samples/` - Example log files for testing
- `pyproject.toml` - Project configuration and dependencies
