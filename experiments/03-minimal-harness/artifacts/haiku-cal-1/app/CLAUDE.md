# logpeek - Structured Log Summarizer

## Project Overview

`logpeek` is a Python CLI tool that summarizes structured log files. It parses log lines, extracts metadata, and provides human-readable and machine-readable summaries.

## Architecture

### Modules

- **`logpeek/parser.py`**: Parses individual log lines
  - `parse_iso_timestamp()`: Parse ISO 8601 timestamps with timezone
  - `parse_unix_timestamp()`: Parse Unix timestamps (seconds since epoch)
  - `parse_log_line()`: Parse a complete log line into (timestamp, level, logger, message)

- **`logpeek/analyzer.py`**: Analyzes log files
  - `LogAnalyzer`: Class that reads and analyzes a single file
  - Computes: total lines, level counts, time span, top loggers

- **`logpeek/cli.py`**: Command-line interface
  - Handles multiple files, filtering, and output formats
  - Generates human-readable and JSON output

## Log Format Support

The tool handles two timestamp formats:

1. **ISO 8601 with timezone**: `2026-06-10T09:00:00+00:00 LEVEL logger: message`
2. **Unix timestamp**: `1735689600 LEVEL logger: message`

Invalid lines (non-logs, marks, malformed) are silently skipped during analysis.

## Error Handling

- **Empty file**: Treated as invalid with message "empty file"
- **No valid log lines**: Treated as invalid with message "not a log file"
- **Missing file**: Caught with "Cannot read file" message
- **Exit codes**: 0 on success, 1 if any errors

## Key Implementation Details

### Timestamp Normalization

Mixed ISO and Unix timestamps are handled by normalizing both to naive UTC datetimes for comparison. The output uses:
- ISO 8601 with "Z" suffix for naive datetimes (from Unix)
- Original ISO format (with ±HH:MM offset) for aware datetimes

### Parser Logic

The log line parser:
1. Rejects empty lines and markers (`--`, `[`)
2. Splits on whitespace: `timestamp level logger:message`
3. Validates timestamp can be parsed (ISO or Unix)
4. Extracts logger name and message from `logger:message` format

### File-level Analysis

`LogAnalyzer` tracks:
- All parsed timestamps (for time span calculation)
- Level counts (for distribution)
- Logger names (for top-N frequency)
- Parse error count (lines that looked like logs but failed)

## Testing

Unit tests in `tests/` cover:
- ISO and Unix timestamp parsing
- Log line parsing with various formats and errors
- File analysis (valid, empty, non-log)
- Time span calculation
- Top logger extraction
- Mixed timestamp handling

Run tests: `python -m unittest discover tests/`

## Installation

```bash
pip install -e .
```

This creates a console script entry point at `/usr/local/bin/logpeek`.
