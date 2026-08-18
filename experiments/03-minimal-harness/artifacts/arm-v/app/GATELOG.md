# Check.sh Test Log

## Run 1: Initial test - All tests passed
- **Date**: 2026-08-18
- **Result**: PASSED
- **Output**: All 15 tests passed
- **Command**: `./check.sh`

### Summary
- boot.log summary: PASSED
- boot.log levels: PASSED
- boot.log time span: PASSED
- boot.log top loggers: PASSED
- app_main.log summary: PASSED
- app_main.log levels: PASSED
- app_main.log time span: PASSED
- app_main.log top loggers: PASSED
- empty.log error: PASSED
- non-existent file error: PASSED
- filter by level: PASSED
- JSON output: PASSED
- JSON output data: PASSED
- multiple files: PASSED
- Input files not modified: PASSED

## Deliberate Bug Test

Testing that check.sh can fail by introducing a bug:

### Run 2: Introduce bug - exit code handling broken
- **Date**: 2026-08-18
- **Change**: Modified logpeek/cli.py line 114 to always exit 1
- **Expected**: Tests should fail
- **Result**: FAILED (12 failures detected)

Modified cli.py to introduce bug:
```python
sys.exit(1)  # BUG: Always exit with error code
```

Test failures detected:
```
Testing: boot.log summary
  FAILED: Expected exit code 0, got 1
Testing: boot.log levels
  FAILED: Expected exit code 0, got 1
Testing: boot.log time span
  FAILED: Expected exit code 0, got 1
Testing: boot.log top loggers
  FAILED: Expected exit code 0, got 1
Testing: app_main.log summary
  FAILED: Expected exit code 0, got 1
Testing: app_main.log levels
  FAILED: Expected exit code 0, got 1
Testing: app_main.log time span
  FAILED: Expected exit code 0, got 1
Testing: app_main.log top loggers
  FAILED: Expected exit code 0, got 1
Testing: filter by level
  FAILED: Expected exit code 0, got 1
Testing: JSON output
  FAILED: Expected exit code 0, got 1
Testing: JSON output data
  FAILED: Expected exit code 0, got 1
Testing: multiple files
  FAILED: Expected exit code 0, got 1

Test Summary
12 test(s) FAILED
```

✓ Check.sh can successfully detect failures!

### Run 3: Revert bug and re-test
- **Date**: 2026-08-18
- **Change**: Reverted cli.py to correct exit code handling
- **Result**: PASSED
- **Output**: All 15 tests passed

Reverted to original logic:
```python
sys.exit(1 if has_fatal_error else 0)
```

Final test output:
```
Testing: boot.log summary
  PASSED
Testing: boot.log levels
  PASSED
Testing: boot.log time span
  PASSED
Testing: boot.log top loggers
  PASSED
Testing: app_main.log summary
  PASSED
Testing: app_main.log levels
  PASSED
Testing: app_main.log time span
  PASSED
Testing: app_main.log top loggers
  PASSED
Testing: empty.log error
  PASSED
Testing: non-existent file error
  PASSED
Testing: filter by level
  PASSED
Testing: JSON output
  PASSED
Testing: JSON output data
  PASSED
Testing: multiple files
  PASSED
Testing: Input files not modified
  PASSED

Test Summary
All tests PASSED!
```

## Conclusion

The check.sh test suite is working correctly:
- ✓ It passes when the CLI implementation is correct
- ✓ It fails when the CLI implementation is broken
- ✓ All sample files (boot.log, app_main.log, empty.log) are tested
- ✓ Error handling is tested (empty files, non-existent files)
- ✓ Feature testing is complete (filtering, JSON output, multiple files)
- ✓ Input files are never modified
