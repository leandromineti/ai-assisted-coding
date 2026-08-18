# logpeek

A Python CLI tool that summarizes structured log files.

## Features

- Parse structured log files with timestamp, level, logger name, and message
- Display total line count
- Count log entries by level
- Show time span covered (first to last event)
- List the five most frequent logger names
- Filter by log level with `--level`
- Machine-readable JSON output with `--json`
- Handles encoding issues gracefully
- Clear error messages for empty or invalid files

## Installation

```bash
pip install -e .
```

This installs the `logpeek` command, which can be run from any directory.

## Usage

### Basic summary
```bash
logpeek path/to/logfile.log
```

### Filter by level
```bash
logpeek path/to/logfile.log --level ERROR
```

### JSON output
```bash
logpeek path/to/logfile.log --json
```

### Multiple files
```bash
logpeek file1.log file2.log file3.log
```

## Example Output

```
File: samples/boot.log
Total lines: 6
Levels: DEBUG: 1, INFO: 4, WARNING: 1
Time span: 2026-05-31T23:58:00+00:00 to 2026-05-31T23:58:07+00:00
Top loggers: boot.init: 3, boot.svc: 3
```

## Log Format

The tool expects logs in the following format:
```
TIMESTAMP LEVEL logger.name: message
```

Example:
```
2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff
2026-05-31T23:58:01+00:00 ERROR api.gw: connection failed
```

## Error Handling

- **Empty files**: Prints error to stderr with exit code 1
- **File not found**: Prints error to stderr with exit code 1
- **Malformed lines**: Tracks parse errors in output; still processes valid lines
- **Encoding issues**: Uses UTF-8 with error replacement for robustness

## Testing

Run the unit tests:
```bash
pip install pytest
python -m pytest tests/ -v
```

## Development

The project structure:
- `logpeek/cli.py` - Command-line interface
- `logpeek/parser.py` - Log parsing logic
- `tests/test_parser.py` - Unit tests
