# Log File Format Measurements

## File Inventory

### boot.log
- Size: 339 bytes
- Lines: 6 newline characters (6 valid log lines)
- Encoding: UTF-8 compatible
- Format: Plain text, structured logs

### app_main.log
- Size: 2,301,478 bytes (~2.3 MB)
- Lines: 40,000 newline characters (40,000 lines)
- Encoding: Latin-1 (contains UTF-8 with some non-UTF-8 sequences like `café` at position ~867585)
- Format: Mostly structured logs, with 1 malformed JSON line (`{unterminated json dump` at line 8)

### empty.log
- Size: 0 bytes
- Lines: 0
- Is truly empty

## Log Line Structure

All valid log lines follow the format:
```
TIMESTAMP LEVEL LOGGER: MESSAGE
```

Example: `2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff`

Parsing breakdown:
- **TIMESTAMP**: ISO 8601 format with timezone (e.g., `2026-05-31T23:58:00+00:00`)
- **LEVEL**: One of {`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`}
- **LOGGER**: Dot-separated name (e.g., `boot.init`, `api.gw`, `api.auth`, `api.http`, `api.db`)
- **MESSAGE**: Free text after the colon and space

## Encoding Handling

- `boot.log`: Pure UTF-8, no issues
- `app_main.log`: Primarily UTF-8 but contains at least one non-UTF-8 sequence (Latin-1 byte `0xe9` in "café")
- Tool must read `app_main.log` with encoding error handling (e.g., `errors='replace'` or `errors='ignore'`)

## Malformed Lines

- `app_main.log` line 8: `{unterminated json dump` — does not follow the standard format
- Decision: Malformed lines (not matching timestamp-level-logger pattern) should be skipped or reported as non-log lines
- Empty.log: Should not cause an error; should report 0 lines

## Behavior Decisions

### Format Acceptance
- Accept lines matching: `TIMESTAMP LEVEL LOGGER: MESSAGE` pattern (min 3 space-separated parts)
- Skip malformed lines (e.g., lines starting with `{`, lines without proper structure)
- Handle encoding errors by replacing/ignoring invalid bytes (Latin-1 fallback or error replacement)

### Log Levels
- Accept levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- `--level` flag: Filter logs by level name; support case-sensitive matching

### Logger Names (Top 5)
- Extract logger name from the third component (before the colon)
- Count unique logger names
- Report top 5 by frequency (or all if fewer than 5 exist)

### Time Span
- First event: Earliest timestamp in the file
- Last event: Latest timestamp in the file
- Handle files with only 1 event (start == end)

### Edge Cases
- Empty files: Report 0 lines, 0 per level, empty time span, no loggers
- Non-log files: Try to parse; if no valid log lines found, exit with error code 1
- Unreadable files: Exit with error code 1 and report to stderr
