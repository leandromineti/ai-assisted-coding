# logpeek

A Python CLI tool that summarizes structured log files. Given one or more log files, logpeek prints:
- Total number of lines
- Count per log level (INFO, ERROR, DEBUG, WARNING, CRITICAL, etc.)
- Time span covered (first to last event)
- Five most frequent logger names

## Installation

Install the package:

```bash
pip install -e .
```

This installs the `logpeek` command, making it available from any directory.

## Usage

Analyze a single log file:
```bash
logpeek /path/to/logfile.log
```

Analyze multiple files:
```bash
logpeek file1.log file2.log file3.log
```

Filter by log level:
```bash
logpeek --level ERROR logfile.log
```

Output as JSON:
```bash
logpeek --json logfile.log
logpeek --json file1.log file2.log
```

Combine options:
```bash
logpeek --json --level WARNING logfile.log
```

## Output Format

### Text Output (default)

```
File: /path/to/logfile.log
Total lines: 6
Levels: INFO: 3, DEBUG: 1, WARNING: 1
Time span: 2026-05-31T23:58:00+00:00 to 2026-05-31T23:58:07+00:00
Top loggers: boot.init (3), boot.svc (2), ...
```

### JSON Output

```json
[
  {
    "file": "/path/to/logfile.log",
    "total_lines": 6,
    "levels": {
      "INFO": 3,
      "DEBUG": 1,
      "WARNING": 1
    },
    "time_span": {
      "start": "2026-05-31T23:58:00+00:00",
      "end": "2026-05-31T23:58:07+00:00"
    },
    "top_loggers": [
      {"name": "boot.init", "count": 3},
      {"name": "boot.svc", "count": 2}
    ]
  }
]
```

## Supported Log Format

logpeek expects structured logs with the following format:

```
<ISO8601-TIMESTAMP> <LEVEL> <LOGGER-NAME>: <MESSAGE>
```

Example:
```
2026-06-01T00:00:00+00:00 INFO api.gw: evt 0 code 3
2026-05-31T23:58:02+00:00 DEBUG boot.svc: unit graph built
2026-06-04T05:46:33+00:00 WARNING api.http: evt 39999 code 9
```

Supported log levels: `INFO`, `ERROR`, `DEBUG`, `WARNING`, `CRITICAL`

### Handling Edge Cases

- **Empty files**: Reports 0 total lines and empty time span
- **Malformed lines**: Silently skipped; parsing continues
- **Encoding issues**: Gracefully handled with UTF-8 error replacement
- **Non-log files**: Detected and reported with error message (exit code 1)
- **Missing files**: Reported with error message (exit code 1)

## Error Handling

- Non-existent files: Reports `File not found` and exits with code 1
- Non-log files: Reports `does not appear to be a log file` and exits with code 1
- Permission denied: Reports the error and exits with code 1

## Testing

Run the test suite:

```bash
pytest tests/
```

Tests cover:
- Log parsing and format validation
- Empty files and missing files
- Malformed lines and encoding issues
- CLI text and JSON output
- Level filtering
- Multiple file processing
