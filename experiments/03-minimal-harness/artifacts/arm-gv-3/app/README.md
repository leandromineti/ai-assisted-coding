# logpeek

A Python CLI tool that summarizes structured log files.

## Installation

```bash
pip install -e .
```

This will install the `logpeek` command globally, usable from any directory.

## Usage

```bash
logpeek <file1> [<file2> ...]
```

Analyze one or more log files and print:
- Total number of lines
- Count per log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Time span covered (first to last event)
- Five most frequent logger names

### Options

- `--level LEVEL`: Filter logs by level name (e.g., `--level ERROR`)
- `--json`: Output results in JSON format

### Examples

```bash
# Analyze a single file
logpeek app.log

# Analyze multiple files
logpeek app.log boot.log

# Filter by log level
logpeek --level ERROR app.log

# JSON output
logpeek --json app.log
```

## Supported Log Format

The tool expects structured logs in this format:

```
TIMESTAMP LEVEL LOGGER: MESSAGE
```

Example:
```
2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff
2026-06-01T00:00:00+00:00 ERROR api.gw: evt 2 code 6
```

- **TIMESTAMP**: ISO 8601 format with timezone
- **LEVEL**: One of DEBUG, INFO, WARNING, ERROR, CRITICAL
- **LOGGER**: Dot-separated name (e.g., boot.init, api.gw)
- **MESSAGE**: Free text after the colon

## Error Handling

- Non-existent files: Exit code 1, error message to stderr
- Empty files: Exit code 1 (no valid log lines found)
- Files with no valid log lines: Exit code 1, error message to stderr
- Files with mixed valid/invalid lines: Processes valid lines, ignores invalid ones
- Encoding errors: Handled gracefully (non-UTF-8 sequences replaced)

## Testing

```bash
pytest tests/
```
