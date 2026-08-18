# logpeek Implementation Summary

## What was built

A production-quality Python CLI tool for summarizing structured log files. The tool parses ISO 8601 timestamps and standard log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) from log files and provides:

- **Total line count** including parse errors
- **Level distribution** with counts per level
- **Time span** from first to last event
- **Top 5 loggers** by frequency

## Key Features

✅ Parses ISO 8601 timestamps with timezone offsets
✅ Detects all standard log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
✅ Extracts logger names (supports dots and dashes: `api.gw`, `boot-init`)
✅ Handles empty files gracefully
✅ Filters by log level with `--level NAME`
✅ JSON output with `--json` flag
✅ Clear error messages for non-log files and missing files
✅ Non-zero exit codes on errors
✅ Never modifies input files (read-only)
✅ Works with arbitrarily large files (40K+ lines tested)
✅ Runs from any directory after installation

## Project Structure

```
logpeek/
  __init__.py        - Package initialization
  cli.py             - Command-line interface and main entry point
  parser.py          - Log parsing logic (ISO8601, levels, extraction)
  processor.py       - File I/O and error handling
  formatter.py       - Output formatting (text and JSON)

tests/
  test_parser.py     - 13 parser unit tests
  test_processor.py  - 11 processor unit tests  
  test_cli.py        - 11 CLI integration tests
  
setup.py             - Package configuration for pip install
README.md            - User documentation
IMPLEMENTATION.md    - This file
```

## Test Coverage

**42 tests** covering:
- Valid log parsing (all levels, loggers, messages)
- Invalid/malformed input (missing fields, bad timestamps)
- Empty files
- Files with mixed valid/invalid lines
- Non-log files
- Missing files
- Directories instead of files
- Level filtering
- UTF-8 error handling
- File immutability
- CLI argument parsing
- JSON output format
- Multiple file handling
- Error reporting and exit codes

All tests pass: `Ran 42 tests in 0.682s - OK`

## Sample Files

Tested against all provided samples:
- `boot.log` - 6 lines, mix of DEBUG/INFO/WARNING across 2 loggers
- `app_main.log` - 40,000 lines, 3-day time span, 5 log levels, 4 loggers
- `empty.log` - 0 lines (empty file)

## Installation & Usage

**Install globally:**
```bash
pip install -e .
```

**Basic usage:**
```bash
logpeek /path/to/log.log
```

**Multiple files:**
```bash
logpeek file1.log file2.log file3.log
```

**Filter by level:**
```bash
logpeek log.log --level INFO
```

**JSON output:**
```bash
logpeek log.log --json
```

**Help:**
```bash
logpeek --help
```

## Error Handling Examples

**Non-log file:**
```
$ logpeek notlog.txt
Error: File does not contain valid log entries: notlog.txt
Exit code: 1
```

**Missing file:**
```
$ logpeek /nonexistent.log
Error: File not found: /nonexistent.log
Exit code: 1
```

**Empty file (valid):**
```
$ logpeek empty.log
File: empty.log
Total lines: 0
Exit code: 0
```

## Design Decisions

1. **Parser robustness**: Regex-based parsing of ISO 8601 timestamps and log levels. Returns `None` for unparseable lines rather than raising exceptions.

2. **Counting strategy**: `total_lines` counts both valid entries and parse errors separately, giving users insight into log quality. Level-filtered output still reports time span of all valid entries.

3. **Logger name extraction**: Alphanumeric with dots and dashes, extracted by looking for a colon after the level. Defaults to "unknown" if not found.

4. **Empty file handling**: Valid and reportable; users can distinguish between "no log data" and "not a log file" based on the error message.

5. **JSON structure**: Single JSON array with one object per file, enabling pipeline processing of multiple files.

6. **File safety**: Opens in read-only mode with explicit `errors='replace'` for encoding issues. Files are never truncated, written to, or deleted.

7. **Error strategy**: File errors are caught early. Invalid log files cause a clear error message and exit code 1. Partial success (one file valid, one invalid) reports errors and exits with code 1.
