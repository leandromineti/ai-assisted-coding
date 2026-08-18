# logpeek

A Python CLI tool to summarize structured log files. Given one or more log file paths, `logpeek` prints:
- Total number of lines
- Count per log level
- Time span (first to last event)
- Five most frequent logger names

## Installation

Install the tool so it runs from any directory:

```bash
pip install -e .
```

This creates a `logpeek` command available globally.

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
logpeek --level ERROR logfile.log
```

### JSON output

```bash
logpeek --json logfile.log
```

## Examples

```bash
$ logpeek samples/boot.log
File: samples/boot.log
  Total lines: 6
  Levels: {'INFO': 4, 'DEBUG': 1, 'WARNING': 1}
  Time span: 2026-05-31T23:58:00+00:00 to 2026-05-31T23:58:07+00:00
  Top loggers:
    boot.init: 2
    boot.svc: 2

$ logpeek --json samples/boot.log
[
  {
    "file": "samples/boot.log",
    "total_lines": 6,
    "levels": {
      "INFO": 4,
      "DEBUG": 1,
      "WARNING": 1
    },
    "time_span": {
      "start": "2026-05-31T23:58:00+00:00",
      "end": "2026-05-31T23:58:07+00:00"
    },
    "top_loggers": [
      {
        "name": "boot.init",
        "count": 2
      },
      {
        "name": "boot.svc",
        "count": 2
      }
    ]
  }
]

$ logpeek --level INFO samples/boot.log
File: samples/boot.log
  Total lines: 4
  Levels: {'INFO': 4}
  Time span: 2026-05-31T23:58:00+00:00 to 2026-05-31T23:58:07+00:00
  Top loggers:
    boot.init: 2
    boot.svc: 2
```

## Log Format

The tool expects logs in this format:

```
TIMESTAMP LEVEL LOGGER: MESSAGE
```

Where:
- `TIMESTAMP`: ISO 8601 format (e.g., `2026-05-31T23:58:00+00:00`)
- `LEVEL`: Log level (e.g., `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)
- `LOGGER`: Logger name, typically dotted (e.g., `boot.init`, `api.gw`)
- `MESSAGE`: The log message (can contain spaces)

Example:
```
2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff
2026-05-31T23:58:01+00:00 ERROR api.gw: connection timeout
```

## Error Handling

- **Empty file**: Prints error and exits with code 1
- **Invalid log lines**: Prints error with line number and exits with code 1
- **Nonexistent file**: Prints error and exits with code 1
- **No entries after filtering**: Returns error in JSON output

All errors are printed to stderr.

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

Or using unittest directly:

```bash
python -m unittest discover tests/
```

Tests cover:
- Log line parsing with various formats
- File parsing and error handling
- Analysis features (counts, time span, top loggers)
- CLI arguments and output formats
- Edge cases (empty files, invalid lines, etc.)
