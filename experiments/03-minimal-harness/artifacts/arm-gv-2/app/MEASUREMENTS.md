# Measurements: logpeek log file analysis

## Sample Files

### boot.log
- **Lines:** 6 lines
- **Format:** Structured text logs, one per line
- **Character Encoding:** UTF-8, no encoding issues
- **Content:** Normal boot sequence

### app_main.log
- **Lines:** 40,000 lines
- **Format:** Structured text logs, one per line
- **Character Encoding:** UTF-8 with some non-UTF-8 bytes (byte 0xe9 at position 7425)
- **Content:** High-volume API log file

### empty.log
- **Lines:** 0 lines
- **Format:** Empty file
- **Content:** No log entries

## Log Format

All valid log lines follow this pattern:
```
TIMESTAMP LEVEL LOGGER: MESSAGE
```

**Timestamp Format:** ISO8601 with timezone (e.g., `2026-05-31T23:58:00+00:00`)
**Level:** All-caps keywords: `INFO`, `DEBUG`, `ERROR`, `WARNING`, `CRITICAL`
**Logger:** Dot-separated hierarchical name (e.g., `boot.init`, `api.gw`)
**Message:** Free-form text after colon

### Regex Pattern
```
^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2})\s+([A-Z]+)\s+([^:]+):\s+(.*)$
```

## Behavior Decisions

1. **Character Encoding:** Use `errors='replace'` when reading files to handle non-UTF-8 bytes gracefully (as seen in app_main.log)

2. **Empty Files:** Should be treated as valid logs with 0 lines, not errors. Exit code 0, all counts = 0.

3. **Non-Log Files:** Files that don't follow the format should produce an error. Error exit code 1.

4. **Invalid Lines:** Lines that don't match the format should be skipped or reported as error, depending on file context. If most lines are invalid, error. If a few lines are malformed, skip them.

5. **Log Levels:** Standard levels observed are `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. Filtering by `--level` should match exact level names.

6. **Time Span:** First timestamp to last timestamp (inclusive). If file has 0 valid lines, time span is empty/N/A.

7. **Top 5 Logger Names:** Count frequencies and report top 5. If fewer than 5 unique loggers, report all.

8. **Multiple Files:** Process each file independently and output summary for each.

9. **--level Filter:** Only include log entries matching the specified level. Exit with 0 even if no entries match filter.

10. **--json Output:** Machine-readable JSON format, one object per file.

## Data from Samples

### boot.log Statistics
- Total lines: 6
- Levels: INFO (4), DEBUG (1), WARNING (1)
- Time span: 2026-05-31T23:58:00+00:00 to 2026-05-31T23:58:07+00:00
- Loggers: boot.init (2), boot.svc (3)

### app_main.log Statistics (first/last 3 lines sample)
- Total lines: 40,000
- Time span: 2026-06-01T00:00:00+00:00 to 2026-06-04T05:46:33+00:00
- Observed loggers in sample: api.gw, api.auth, api.http, api.db
- Encoding: UTF-8 with error handling needed
