# logpeek

A Python CLI tool that summarizes structured log files, providing quick analysis of log volume, level distribution, time spans, and frequently-seen loggers.

## Installation

Install directly from the current directory:

```bash
pip install -e .
```

After installation, `logpeek` will be available as a command-line tool.

## Usage

Analyze a single log file:

```bash
logpeek samples/web_api.log
```

Analyze multiple files:

```bash
logpeek samples/web_api.log samples/legacy_daemon.log
```

Filter by log level:

```bash
logpeek --level WARNING samples/web_api.log
```

Output as JSON:

```bash
logpeek --json samples/web_api.log
```

Combine options:

```bash
logpeek --level ERROR --json samples/web_api.log samples/legacy_daemon.log
```

## Output

For each file, logpeek displays:

- **Total lines**: Number of valid log entries parsed
- **Levels**: Count of entries per log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Time span**: Earliest and latest timestamps in the file
- **Top loggers**: The 5 most frequently-appearing logger names

### Example Output

```
File: samples/web_api.log
  Total lines: 13
  Levels: DEBUG=2, INFO=5, WARNING=2, ERROR=2, CRITICAL=1
  Time span: 2026-06-10T09:00:00 to 2026-06-10T09:12:00
  Top loggers:
    api.http: 5
    api.db: 3
    api.auth: 3
    api.cache: 1
```

### JSON Output

With `--json`, output is a JSON array with structured data suitable for parsing:

```json
[
  {
    "file": "samples/web_api.log",
    "total_lines": 13,
    "level_counts": {
      "DEBUG": 2,
      "INFO": 5,
      "WARNING": 2,
      "ERROR": 2,
      "CRITICAL": 1
    },
    "time_start": "2026-06-10T09:00:00",
    "time_end": "2026-06-10T09:12:00",
    "top_loggers": [
      {"name": "api.http", "count": 5},
      {"name": "api.db", "count": 3},
      ...
    ]
  }
]
```

## Supported Log Formats

logpeek supports structured logs with timestamp, level, logger, and message:

- **ISO 8601 timestamps**: `2026-06-10T09:00:00+00:00` or `2026-06-10T09:00:00`
- **Unix timestamps**: `1735689600`
- **Valid levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

Example log line:

```
2026-06-10T09:00:00+00:00 INFO api.http: listening on :8080
```

## Error Handling

logpeek provides clear error messages and non-zero exit codes for:

- **File not found**: Specified file does not exist
- **Empty log file**: File exists but contains no valid entries
- **No valid entries**: File contains content but no parseable log lines
- **Invalid level filter**: Unknown log level specified

When processing multiple files, logpeek will report errors for problematic files while continuing to analyze others. The tool exits with code 1 if any file failed.

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

Or using unittest:

```bash
python -m unittest discover tests/
```

## Implementation Details

- **Robust parsing**: Handles malformed lines gracefully, skipping non-log content like markers and reload messages
- **Multiple timestamp formats**: Automatically detects and parses both ISO 8601 and Unix timestamps
- **Read-only**: Never modifies input files
- **Memory efficient**: Processes files line-by-line
