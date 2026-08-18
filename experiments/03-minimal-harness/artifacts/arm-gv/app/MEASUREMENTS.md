# Measurements: logpeek CLI Input Analysis

## Sample Files Enumeration

| File | Size | Type | Status |
|------|------|------|--------|
| `samples/boot.log` | 339 bytes | Valid structured log | Text |
| `samples/app_main.log` | 2,301,478 bytes | Valid structured log | Text (with encoding issues) |
| `samples/empty.log` | 0 bytes | Empty file | Valid but empty |

## Probe Results

### boot.log
- **Command**: `head -20 /app/samples/boot.log`
- **Output**:
  ```
  2026-05-31T23:58:00+00:00 INFO boot.init: kernel handoff
  2026-05-31T23:58:01+00:00 INFO boot.init: mounts ready
  2026-05-31T23:58:02+00:00 DEBUG boot.svc: unit graph built
  2026-05-31T23:58:03+00:00 INFO boot.svc: api starting
  2026-05-31T23:58:05+00:00 WARNING boot.svc: swap disabled
  2026-05-31T23:58:07+00:00 INFO boot.init: boot complete
  ```
- **Format**: `TIMESTAMP LEVEL LOGGER: MESSAGE`
- **Total Lines**: 6
- **Line Count**: `wc -l` returns 6

### app_main.log
- **Command**: `wc -l /app/samples/app_main.log` → 40000 lines
- **Sample lines** (first 20):
  ```
  2026-06-01T00:00:00+00:00 INFO api.gw: evt 0 code 3
  2026-06-01T00:00:07+00:00 INFO api.auth: evt 1 code 3
  2026-06-01T00:00:14+00:00 ERROR api.gw: evt 2 code 6
  2026-06-01T00:00:21+00:00 DEBUG api.auth: evt 3 code 9
  2026-06-01T00:00:28+00:00 WARNING api.http: evt 4 code 3
  2026-06-01T00:00:35+00:00 CRITICAL api.gw: evt 5 code 3
  2026-06-01T00:00:42+00:00 ERROR api.http: evt 6 code 9
  {unterminated json dump          <-- Malformed line (line 8)
  2026-06-01T00:00:56+00:00 CRITICAL api.gw: evt 8 code 0
  ...
  ```
- **Last lines** (tail -10):
  ```
  2026-06-04T05:45:30+00:00 ERROR api.db: evt 39990 code 9
  2026-06-04T05:45:37+00:00 INFO api.gw: evt 39991 code 9
  2026-06-04T05:45:44+00:00 INFO api.http: evt 39992 code 3
  2026-06-04T05:45:51+00:00 INFO api.gw: evt 39993 code 2
  2026-06-04T05:46:05+00:00 INFO api.gw: evt 39995 code 5
  2026-06-04T05:46:12+00:00 INFO api.gw: evt 39996 code 7
  2026-06-04T05:46:19+00:00 DEBUG api.auth: evt 39997 code 12
  2026-06-04T05:46:26+00:00 INFO api.db: evt 39998 code 4
  2026-06-04T05:46:33+00:00 WARNING api.http: evt 39999 code 9
  ```
- **Format**: `TIMESTAMP LEVEL LOGGER: MESSAGE` (same as boot.log)
- **Encoding**: UTF-8 with error at byte 867585 (valid log lines unaffected)
- **Malformed Lines**: 197 out of 40000 (lines that don't match log pattern)
- **Valid Log Lines**: 39,803

#### Detailed Analysis of app_main.log
- **Python probe command**:
  ```python
  import re
  with open('/app/samples/app_main.log', 'r', encoding='utf-8', errors='replace') as f:
      lines = f.readlines()
  pattern = re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+\-]\d{2}:\d{2})\s+(\w+)\s+([\w.]+):', re.MULTILINE)
  ```
- **Log Levels Found**:
  - INFO: 21,307
  - DEBUG: 6,494
  - WARNING: 5,602
  - ERROR: 4,830
  - CRITICAL: 1,570
- **Loggers** (only 4 unique, not 5 as observed):
  - api.gw: 15,958 (most frequent)
  - api.http: 11,939
  - api.db: 7,917
  - api.auth: 3,989
- **Time Span**: 2026-06-01T00:00:00+00:00 to 2026-06-04T05:46:33+00:00 (about 3.24 days)

### empty.log
- **Command**: `wc -l /app/samples/empty.log` → 0 lines
- **Size**: 0 bytes
- **Content**: Empty file (no lines)
- **Behavior**: Should be handled gracefully

## Format Specification

### Valid Log Line Format
```
TIMESTAMP LEVEL LOGGER: MESSAGE
```

Where:
- **TIMESTAMP**: ISO 8601 format with timezone (e.g., `2026-06-01T00:00:00+00:00`)
- **LEVEL**: One of: INFO, DEBUG, WARNING, ERROR, CRITICAL
- **LOGGER**: Dotted name (e.g., `api.gw`, `boot.init`)
- **MESSAGE**: Anything after the colon and space

### Regex Pattern
```
^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+\-]\d{2}:\d{2})\s+(\w+)\s+([\w.]+):
```

## Behavior Decisions Required

1. **Invalid/Malformed Lines**: How to handle lines that don't match the format?
   - **Decision**: Skip malformed lines when counting; report them as parsed log lines = total - malformed count
   - **Measurement**: app_main.log has 197 malformed lines out of 40,000

2. **Empty Files**: How to handle files with 0 lines?
   - **Decision**: Output summary with all counts as 0, no time span
   - **Measurement**: empty.log is a valid file with 0 bytes and 0 lines

3. **File Encoding**: How to handle non-UTF-8 encoded files?
   - **Decision**: Use UTF-8 with `errors='replace'` to continue processing
   - **Measurement**: app_main.log has UTF-8 decode error at byte 867585 but logs remain mostly valid

4. **Non-Log Files**: How to detect and reject non-log files?
   - **Decision**: If a file has 0 valid log lines and is not empty, report as error
   - **Measurement**: Not yet tested; will validate in implementation

5. **Log Level Filtering**: How to case-handle `--level`?
   - **Decision**: Use exact case matching (INFO, DEBUG, WARNING, ERROR, CRITICAL)
   - **Measurement**: All observed levels are uppercase

6. **Top 5 Loggers**: What if fewer than 5 loggers exist?
   - **Decision**: Return fewer entries if fewer than 5 loggers exist
   - **Measurement**: app_main.log has only 4 unique loggers (api.gw, api.http, api.db, api.auth)
