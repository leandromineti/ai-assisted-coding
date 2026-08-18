# Log Format Measurements

## File Inventory
- `/app/samples/boot.log` — 6 lines, well-formed structured logs
- `/app/samples/app_main.log` — 40000 lines total (11038 when read with encoding handling)
- `/app/samples/empty.log` — 0 lines, empty file

## Format Structure
Analyzed with regex pattern: `^(\S+)\s+(\w+)\s+([^:]+):\s*(.*)$`

### Log Line Components
Each valid log line contains:
1. **Timestamp**: ISO 8601 format (e.g., `2026-06-01T00:00:00+00:00`), first non-whitespace token
2. **Level**: Single word, uppercase (e.g., `INFO`, `ERROR`, `DEBUG`, `WARNING`, `CRITICAL`)
3. **Logger name**: Token between level and colon (e.g., `api.gw`, `boot.init`, `api.http`)
4. **Message**: Everything after the colon

### Valid Log Levels Found
- INFO (5919 occurrences in app_main.log)
- ERROR (1335 occurrences)
- DEBUG (1798 occurrences)
- WARNING (1552 occurrences)
- CRITICAL (423 occurrences)

### Malformed Content in app_main.log
The file contains intentional non-log content:
- `{unterminated json dump` (appears multiple times)
- `### log rotated ###` (marker lines)
- `2026-04-01T1` (truncated/malformed timestamps)

These lines fail the regex pattern and should be skipped (not cause errors).

### Logger Name Distribution (app_main.log Top 5)
1. api.gw: 4358
2. api.http: 3318
3. api.db: 2231
4. api.auth: 1078
5. relay.legacy: 42

## Time Span Calculation
- **boot.log**: 2026-05-31T23:58:00+00:00 to 2026-05-31T23:58:07+00:00 (7 seconds)
- **app_main.log**: 2026-06-01T00:00:00+00:00 to 2026-06-04T05:46:33+00:00 (approx 3 days, 5.7 hours)

## Encoding Handling
- Files are UTF-8 with occasional invalid byte sequences
- Robust parsing requires `errors='replace'` or similar handling
- No parsing errors should be reported for recoverable encoding issues

## Empty File Handling
- `/app/samples/empty.log` with 0 lines should:
  - Report 0 total lines
  - Report 0 for all levels
  - Report empty time span (no start/end timestamps)
  - Report no loggers

## Edge Cases Identified
1. **Malformed lines**: Should be silently skipped (appear in app_main.log)
2. **Empty files**: Should report valid output with zero counts
3. **Non-log files**: Should produce clear error message and exit code 1
4. **Encoding errors**: Should be handled gracefully with error replacement
