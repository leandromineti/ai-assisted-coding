# logpeek

A Python CLI tool that summarizes structured log files, providing a quick overview of log content without parsing the entire file into memory.

## Features

- **Total line count**: Reports the total number of lines in each log file
- **Log level distribution**: Counts log entries by level (INFO, ERROR, DEBUG, etc.)
- **Time span**: Shows the first and last event timestamp
- **Top loggers**: Displays the 5 most frequent logger names
- **Level filtering**: Filter results to a specific log level using `--level`
- **JSON output**: Machine-readable output with `--json`
- **Error handling**: Clear error messages for invalid or empty files with non-zero exit codes

## Installation

Install from the project directory:

```bash
pip install -e .
```

Or build and install:

```bash
pip install .
```

## Usage

### Basic usage - analyze a single file:

```bash
logpeek /path/to/logfile.log
```

### Analyze multiple files:

```bash
logpeek file1.log file2.log file3.log
```

### Filter by log level:

```bash
logpeek --level ERROR app.log
```

### JSON output for scripting:

```bash
logpeek --json app.log
```

### Combine options:

```bash
logpeek --level WARNING --json *.log
```

## Log Format

The tool expects structured logs in the following format:

```
ISO8601_TIMESTAMP LOG_LEVEL logger.name: message
```

Example:
```
2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff
2026-05-31T23:58:01+00:00 ERROR api.gw: request failed
```

## Output

### Text Output (default)

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
      {"name": "api.http", "count": 200},
      {"name": "api.db", "count": 180},
      {"name": "api.auth", "count": 150},
      {"name": "boot.init", "count": 118}
    ]
  }
]
```

## Error Handling

- **Non-existent file**: Prints error and exits with code 1
- **Empty file**: Prints error and exits with code 1
- **Invalid log format**: Prints error and exits with code 1
- **Permission denied**: Prints error and exits with code 1

The tool never modifies input files.
