# GATELOG.md - Validation Test Runs

## Run 1: Initial Test (with Exit Code Bug)

**Date**: 2026-08-18
**Objective**: Prove that check.sh can detect failures
**Deliberate Bug**: Changed exit code logic from `sys.exit(1 if has_error else 0)` to `sys.exit(0 if has_error else 1)` to invert exit codes

**Command**:
```bash
bash check.sh
```

**Result**: FAILED (as expected)
```
Test 1: Parse boot.log ... [0;31mFAIL[0m
  Output: File: samples/boot.log ... (exit code: 1)
Test 2: Parse app_main.log (40K lines) ... [0;31mFAIL[0m
  Output: File: samples/app_main.log ... (exit code: 1)
Test 3: Parse empty.log (0 lines) ... [0;31mFAIL[0m
  Output: File: samples/empty.log ... (exit code: 1)

=== Summary ===
Passed: 9
Failed: 3

Some tests failed!
```

**Details**: Tests 1-3 failed because they now correctly check exit codes. The tool exited with code 1 on successful parsing (due to the inverted exit code), which violated the assertions.

---

## Run 2: After Bug Fix

**Date**: 2026-08-18
**Objective**: Verify all tests pass after fixing the bug
**Fix**: Reverted to correct exit code logic: `sys.exit(1 if has_error else 0)`

**Command**:
```bash
bash check.sh
```

**Result**: PASSED (100%)
```
Test 1: Parse boot.log ... PASS
Test 2: Parse app_main.log (40K lines) ... PASS
Test 3: Parse empty.log (0 lines) ... PASS
Test 4: JSON output (--json flag) ... PASS
Test 5: Level filter (--level INFO) ... PASS
Test 6: Multiple files ... PASS
Test 7: Non-existent file (error handling) ... PASS
Test 8: Invalid level filter (error handling) ... PASS
Test 9: Non-log file (error handling) ... PASS
Test 10: Tool never modifies input files ... PASS
Test 11: Time span output (first to last event) ... PASS
Test 12: Top loggers output ... PASS

=== Summary ===
Passed: 12
Failed: 0

All tests passed!
```

**Details**: All 12 tests now pass. The tool correctly:
- Parses all sample files (boot.log, app_main.log, empty.log)
- Returns exit code 0 on success
- Returns exit code 1 on errors
- Filters by log level
- Outputs JSON when requested
- Handles multiple files
- Rejects non-log files with appropriate error messages
- Never modifies input files
- Reports time spans and top loggers correctly

---

## Check Script Coverage

The `check.sh` script validates:

1. **File Parsing**: boot.log (6 lines), app_main.log (40K lines), empty.log (0 lines)
2. **Output Formats**: Human-readable text, JSON
3. **Filtering**: --level flag with valid levels
4. **Error Handling**:
   - Non-existent files (proper error message, exit code 1)
   - Invalid level filters (proper error message, exit code 1)
   - Non-log files (proper error message, exit code 1)
5. **Data Integrity**: Confirms tool never modifies input files
6. **Output Correctness**: Validates time spans and top loggers

---

## Test Results Summary

| Test | Description | Status |
|------|-------------|--------|
| 1 | Parse boot.log | ✓ |
| 2 | Parse app_main.log (40K lines) | ✓ |
| 3 | Parse empty.log (0 lines) | ✓ |
| 4 | JSON output (--json flag) | ✓ |
| 5 | Level filter (--level INFO) | ✓ |
| 6 | Multiple files | ✓ |
| 7 | Non-existent file error handling | ✓ |
| 8 | Invalid level filter error handling | ✓ |
| 9 | Non-log file error handling | ✓ |
| 10 | Tool never modifies input files | ✓ |
| 11 | Time span output (first to last event) | ✓ |
| 12 | Top loggers output | ✓ |

**Final Status**: ✓ All tests pass
