# GATELOG: logpeek

## Run 1: Initial check.sh execution

**Command**: `./check.sh`

**Result**: PASSED

All 18 tests passed on the first run. The test script validates:
- Basic file summaries (boot.log, app_main.log, empty.log)
- Correct level counts and timestamps
- Top logger identification
- Error handling for nonexistent and invalid files
- Filtering with `--level`
- JSON output format
- Multiple file processing
- File integrity (no modifications)

**Test Summary**:
```
Total: 18
Passed: 18
Failed: 0
```

---

## Run 2: Proving check.sh can fail

**Test**: Introduced deliberate bug - set `has_errors = True` at startup in `cli.py`

**Command**: `./check.sh` (with bug in place)

**Result**: FAILED as expected

13 tests failed with exit code 1, proving the check script correctly detects bugs:
- Tests expecting exit code 0 now get exit code 1
- Tests expecting successful output now get error output

This validates that check.sh is not a false-positive test suite.

---

## Run 3: Final verification after bug revert

**Command**: Reverted the bug and ran `./check.sh`

**Result**: PASSED

All 18 tests passed again, confirming the tool works correctly.

**Test Summary**:
```
Total: 18
Passed: 18
Failed: 0
```

---

## Test Coverage

The check.sh script validates:

1. **Single file processing**: boot.log, app_main.log, empty.log
2. **Error handling**:
   - Nonexistent files (exit 1)
   - Invalid log files (exit 1)
   - Invalid level arguments (exit 1)
3. **Output formats**:
   - Human-readable text output
   - JSON output with valid structure
4. **Filtering**:
   - `--level` flag with various levels
   - Filtering on empty files
5. **Multiple files**:
   - Processing multiple files together
   - Partial failures (one valid, one invalid)
6. **Data integrity**:
   - Files are never modified by logpeek
7. **Output correctness**:
   - Total line counts
   - Level counts
   - Logger names
   - Time spans

All sample files in `samples/` are tested:
- `boot.log` (6 lines, 5 log levels represented)
- `app_main.log` (40,000 lines, all 5 log levels)
- `empty.log` (0 lines)
