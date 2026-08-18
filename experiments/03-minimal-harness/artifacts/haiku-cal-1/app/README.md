# logpeek

A Python CLI tool to summarize structured log files.

## Installation

Install the package with pip:

```bash
pip install -e .
```

This makes the `logpeek` command available from any directory.

## Usage

Summarize one or more log files:

```bash
logpeek <file> [<file> ...]
```

### Options

- `--level NAME`: Filter results to show only logs at the specified level (e.g., `--level INFO`)
- `--json`: Output results as machine-readable JSON

### Examples

```bash
# Summarize a single log file
logpeek app.log

# Summarize multiple files
logpeek app.log daemon.log

# Filter to INFO level only
logpeek app.log --level INFO

# Output as JSON
logpeek app.log --json

# Combine options
logpeek app.log --level ERROR --json
```

## Output Format

For each valid log file, the tool prints:

- **total lines**: Count of all lines in the file
- **level counts**: Number of logs at each level (e.g., `DEBUG=5, INFO=10, ERROR=2`)
- **time span**: ISO 8601 timestamps of the first and last events
- **top loggers**: Five most frequent logger names with their counts

### Sample Output

```
app.log
  total lines: 17
  level counts: CRITICAL=1, DEBUG=2, ERROR=2, INFO=6, WARNING=2
  time span: 2026-06-10T09:00:00+00:00 to 2026-06-10T09:12:00+00:00
  top loggers: api.http(6), api.db(3), api.auth(2), api.cache(1)
```

### JSON Output

With `--json`, the output is a JSON object with a `files` array:

```json
{
  "files": [
    {
      "file": "app.log",
      "total_lines": 17,
      "level_counts": {
        "INFO": 6,
        "DEBUG": 2,
        "WARNING": 2,
        "ERROR": 2,
        "CRITICAL": 1
      },
      "time_span": {
        "first": "2026-06-10T09:00:00+00:00",
        "last": "2026-06-10T09:12:00+00:00"
      },
      "top_loggers": [
        {"name": "api.http", "count": 6},
        {"name": "api.db", "count": 3},
        {"name": "api.auth", "count": 2}
      ]
    }
  ],
  "errors": false
}
```

## Supported Log Formats

The tool handles structured logs with two timestamp formats:

1. **ISO 8601 with timezone**: `2026-06-10T09:00:00+00:00 LEVEL logger: message`
2. **Unix timestamp**: `1735689600 LEVEL logger: message`

Lines that are not valid log entries (malformed, empty, markers like `-- MARK --` or `[reload]`) are silently skipped during analysis.

## Error Handling

The tool handles invalid inputs gracefully:

- **Empty file**: Exits with error: `error: {file}: empty file`
- **Non-log file**: Exits with error: `error: {file}: not a log file`
- **Missing file**: Exits with error: `error: {file}: Cannot read file: ...`

Exit code is 0 on success, 1 if any errors occurred.

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

Or use unittest:

```bash
python -m unittest discover tests/
```
