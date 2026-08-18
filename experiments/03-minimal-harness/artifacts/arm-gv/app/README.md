# logpeek

A Python CLI tool to summarize structured log files. Quickly analyze log files to understand their contents, log level distribution, time spans, and frequent logger names.

## Features

- **Parse structured logs**: Handles ISO 8601 formatted log files with log levels and logger names
- **Summary statistics**: Total line count, log level distribution, time span (first to last event)
- **Top loggers**: Identifies the five most frequently used logger names
- **Filtering**: Filter results by log level with `--level`
- **Multiple files**: Summarize multiple files in a single command
- **JSON output**: Machine-readable output with `--json` flag
- **Robust error handling**: Clear errors for malformed or non-log files

## Installation

```bash
pip install -e .
```

This installs the `logpeek` command globally, making it available from any directory.

## Usage

### Basic Usage

Summarize a single log file:
```bash
logpeek path/to/logfile.log
```

Output:
```
File: path/to/logfile.log
Total lines: 40000
Log levels: DEBUG: 6494, INFO: 21307, WARNING: 5602, ERROR: 4830, CRITICAL: 1570
Time span: 2026-06-01T00:00:00+00:00 to 2026-06-04T05:46:33+00:00
Top loggers: api.gw (15958), api.http (11939), api.db (7917), api.auth (3989)
```

### Multiple Files

Summarize multiple files at once:
```bash
logpeek file1.log file2.log file3.log
```

Each file's summary is printed separately with blank lines between them.

### Filter by Log Level

Show only counts for a specific log level:
```bash
logpeek logfile.log --level INFO
```

Valid log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

### JSON Output

Get machine-readable JSON output:
```bash
logpeek logfile.log --json
```

Output:
```json
[
  {
    "file": "logfile.log",
    "total_lines": 40000,
    "level_counts": {
      "DEBUG": 6494,
      "INFO": 21307,
      "WARNING": 5602,
      "ERROR": 4830,
      "CRITICAL": 1570
    },
    "time_span": {
      "start": "2026-06-01T00:00:00+00:00",
      "end": "2026-06-04T05:46:33+00:00"
    },
    "top_loggers": [
      {"name": "api.gw", "count": 15958},
      {"name": "api.http", "count": 11939},
      {"name": "api.db", "count": 7917},
      {"name": "api.auth", "count": 3989}
    ]
  }
]
```

### Combine Options

Filter by log level and output as JSON:
```bash
logpeek logfile.log --level ERROR --json
```

## Log File Format

logpeek expects structured log files in this format:

```
TIMESTAMP LEVEL LOGGER: MESSAGE
```

Where:
- **TIMESTAMP**: ISO 8601 format with timezone (e.g., `2026-06-01T00:00:00+00:00`)
- **LEVEL**: One of `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`
- **LOGGER**: Dotted name, e.g., `api.gw`, `boot.init`
- **MESSAGE**: Any text following the colon

Example:
```
2026-06-01T00:00:00+00:00 INFO api.gw: Request received
2026-06-01T00:00:07+00:00 ERROR api.db: Connection timeout
2026-06-01T00:00:14+00:00 DEBUG api.auth: Token validated
```

## Error Handling

### Non-existent file
```bash
$ logpeek nonexistent.log
Error: File not found: nonexistent.log
```
Exit code: 1

### Non-log file (no valid log lines)
```bash
$ logpeek text.txt
Error: text.txt is not a valid log file (no valid log lines found)
```
Exit code: 1

### Invalid log level
```bash
$ logpeek file.log --level INVALID
Error: Invalid log level 'INVALID'. Valid levels are: CRITICAL, DEBUG, ERROR, INFO, WARNING
```
Exit code: 1

### Empty file
Empty files are handled gracefully and return a summary with all counts as zero:
```bash
$ logpeek empty.log
File: empty.log
Total lines: 0
Log levels: (none)
Time span: (none)
Top loggers: (none)
```
Exit code: 0

## Testing

Run the test suite:
```bash
python -m unittest test_logpeek.py -v
```

Or use the validation script:
```bash
bash check.sh
```

## Module API

logpeek can also be imported and used as a Python module:

```python
from logpeek import parse_log_file, get_summary
from pathlib import Path

# Parse a file and get raw counts
total_lines, level_counts, logger_counts, timestamps = parse_log_file(Path('app.log'))

# Get a formatted summary
summary = get_summary(Path('app.log'), level_filter='ERROR')
print(summary)
```

## Exit Codes

- **0**: Success (all files processed successfully)
- **1**: Error (file not found, non-log file, invalid arguments, or other issues)

## Implementation Details

- Malformed log lines are skipped silently; they count toward total lines but don't contribute to statistics
- Files with encoding issues are handled gracefully using UTF-8 with error replacement
- The tool never modifies input files
- Time span is calculated from the first and last valid log entries, ignoring malformed lines
- Logger names are extracted with the pattern `[\w.]+` (word characters and dots)
