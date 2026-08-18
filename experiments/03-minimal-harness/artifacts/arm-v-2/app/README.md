# logpeek

A Python CLI tool that summarizes structured log files.

## Features

- **Line counts**: Total lines in each log file
- **Level distribution**: Count of entries per log level (INFO, DEBUG, ERROR, etc.)
- **Time span**: First and last event timestamps
- **Top loggers**: Five most frequent logger names
- **Filtering**: Filter by log level with `--level`
- **JSON output**: Machine-readable output with `--json`
- **Error handling**: Clear error messages for invalid files and non-log content

## Installation

```bash
pip install -e .
```

This installs the `logpeek` command globally on your system.

## Usage

```bash
# Summarize a single log file
logpeek samples/boot.log

# Summarize multiple files
logpeek samples/boot.log samples/app_main.log

# Filter by log level
logpeek samples/app_main.log --level ERROR

# Output as JSON
logpeek samples/app_main.log --json

# Filter and output as JSON
logpeek samples/app_main.log --level INFO --json
```

## Output Format

### Text Output (default)

```
samples/boot.log:
  Total lines: 6
  Levels: DEBUG (1), INFO (4), WARNING (1)
  Time span: 2026-05-31T23:58:00+00:00 to 2026-05-31T23:58:07+00:00
  Top loggers: boot.init (3), boot.svc (3)
```

### JSON Output (--json)

```json
[
  {
    "file": "samples/boot.log",
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
      ["boot.init", 3],
      ["boot.svc", 3]
    ]
  }
]
```

## Log Format

logpeek expects structured logs in the following format:

```
TIMESTAMP LEVEL logger.name: message
```

Example:
```
2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff
2026-05-31T23:58:01+00:00 DEBUG boot.svc: unit graph built
```

## Error Handling

- **Non-existent files**: Clear error message and exit code 1
- **Empty files**: Handled gracefully with zero counts
- **Non-log files**: Lines that don't match the log format are counted as invalid
- **Read errors**: File permission and encoding errors are reported

## Exit Codes

- `0`: Success
- `1`: One or more files had errors
