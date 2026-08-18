#!/bin/bash

set -e
set -o pipefail

FAILED=0

run_test() {
    local test_name="$1"
    local expected_exit="$2"
    shift 2
    local cmd=("$@")

    echo "Testing: $test_name"

    set +e
    output=$("${cmd[@]}" 2>&1)
    actual_exit=$?
    set -e

    if [ "$actual_exit" -ne "$expected_exit" ]; then
        echo "  FAILED: Expected exit code $expected_exit, got $actual_exit"
        echo "  Output: $output"
        FAILED=$((FAILED + 1))
    else
        echo "  PASSED"
    fi
}

run_test_output() {
    local test_name="$1"
    local expected_exit="$2"
    local expected_content="$3"
    shift 3
    local cmd=("$@")

    echo "Testing: $test_name"

    set +e
    output=$("${cmd[@]}" 2>&1)
    actual_exit=$?
    set -e

    if [ "$actual_exit" -ne "$expected_exit" ]; then
        echo "  FAILED: Expected exit code $expected_exit, got $actual_exit"
        echo "  Output: $output"
        FAILED=$((FAILED + 1))
    elif ! echo "$output" | grep -q "$expected_content"; then
        echo "  FAILED: Output does not contain expected content: $expected_content"
        echo "  Output: $output"
        FAILED=$((FAILED + 1))
    else
        echo "  PASSED"
    fi
}

echo "=========================================="
echo "Running logpeek CLI tests"
echo "=========================================="

# Test 1: boot.log basic summary
run_test_output "boot.log summary" 0 "Total lines: 6" \
    logpeek /app/samples/boot.log

# Test 2: boot.log contains level counts
run_test_output "boot.log levels" 0 "INFO: 4" \
    logpeek /app/samples/boot.log

# Test 3: boot.log contains time span
run_test_output "boot.log time span" 0 "2026-05-31T23:58:00" \
    logpeek /app/samples/boot.log

# Test 4: boot.log top loggers
run_test_output "boot.log top loggers" 0 "boot.init" \
    logpeek /app/samples/boot.log

# Test 5: app_main.log summary
run_test_output "app_main.log summary" 0 "Total lines: 40000" \
    logpeek /app/samples/app_main.log

# Test 6: app_main.log contains multiple levels
run_test_output "app_main.log levels" 0 "INFO:" \
    logpeek /app/samples/app_main.log

# Test 7: app_main.log time span
run_test_output "app_main.log time span" 0 "2026-06-01T00:00:00" \
    logpeek /app/samples/app_main.log

# Test 8: app_main.log top loggers
run_test_output "app_main.log top loggers" 0 "api.gw" \
    logpeek /app/samples/app_main.log

# Test 9: Empty file error
run_test "empty.log error" 1 \
    logpeek /app/samples/empty.log

# Test 10: Non-existent file error
run_test "non-existent file error" 1 \
    logpeek /app/samples/nonexistent.log

# Test 11: Level filter
run_test_output "filter by level" 0 "Total lines: 4" \
    logpeek /app/samples/boot.log --level INFO

# Test 12: JSON output has valid structure
run_test_output "JSON output" 0 '"files"' \
    logpeek /app/samples/boot.log --json

# Test 13: JSON output contains summary data
run_test_output "JSON output data" 0 '"total_lines": 6' \
    logpeek /app/samples/boot.log --json

# Test 14: Multiple files
run_test_output "multiple files" 0 "Total lines: 6" \
    logpeek /app/samples/boot.log /app/samples/empty.log 2>&1

# Test 15: Check that files are not modified
BOOT_CHECKSUM_BEFORE=$(md5sum /app/samples/boot.log | cut -d' ' -f1)
logpeek /app/samples/boot.log > /dev/null 2>&1 || true
BOOT_CHECKSUM_AFTER=$(md5sum /app/samples/boot.log | cut -d' ' -f1)

if [ "$BOOT_CHECKSUM_BEFORE" != "$BOOT_CHECKSUM_AFTER" ]; then
    echo "FAILED: Input files were modified"
    FAILED=$((FAILED + 1))
else
    echo "Testing: Input files not modified"
    echo "  PASSED"
fi

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="

if [ $FAILED -eq 0 ]; then
    echo "All tests PASSED!"
    exit 0
else
    echo "$FAILED test(s) FAILED"
    exit 1
fi
