# logpeek Quick Start

## Installation

Already done! The package is installed via `pip install -e /app`.

The `logpeek` command is available globally.

## Basic Usage

### Summarize a log file
```bash
logpeek /path/to/logfile.log
```

Output:
```
File: /path/to/logfile.log
Total lines: 40000
Log levels: DEBUG: 6494, INFO: 21307, WARNING: 5602, ERROR: 4830, CRITICAL: 1570
Time span: 2026-06-01T00:00:00+00:00 to 2026-06-04T05:46:33+00:00
Top loggers: api.gw (15958), api.http (11939), api.db (7917), api.auth (3989)
```

## Common Commands

### Filter by log level
```bash
logpeek logfile.log --level ERROR
```

### Get JSON output
```bash
logpeek logfile.log --json
```

### Analyze multiple files
```bash
logpeek file1.log file2.log file3.log
```

### Combine options
```bash
logpeek logfile.log --level ERROR --json
```

## Test the Installation

Run all tests:
```bash
bash check.sh                              # Integration tests (12 tests)
python -m unittest test_logpeek.py -v     # Unit tests (16 tests)
```

Test against sample files:
```bash
logpeek samples/boot.log
logpeek samples/app_main.log
logpeek samples/empty.log
```

## Valid Log Levels

When using `--level`, use one of:
- `DEBUG`
- `INFO`
- `WARNING`
- `ERROR`
- `CRITICAL`

## Log File Format

Expected format:
```
TIMESTAMP LEVEL LOGGER: MESSAGE
```

Example:
```
2026-06-01T00:00:00+00:00 INFO api.gw: Request received
2026-06-01T00:00:07+00:00 ERROR api.db: Connection timeout
```

## Exit Codes

- **0**: Success
- **1**: Error (file not found, non-log file, invalid arguments, etc.)

## Troubleshooting

### Command not found
If `logpeek` is not available, install it:
```bash
pip install -e /app
```

### Non-log file error
Make sure your file is in the format: `TIMESTAMP LEVEL LOGGER: MESSAGE`

### Invalid level error
Check that you're using uppercase: INFO, ERROR, WARNING, DEBUG, or CRITICAL

## Documentation

For more details, see:
- [README.md](README.md) - Full user guide
- [MEASUREMENTS.md](MEASUREMENTS.md) - Technical format specifications
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Implementation details
