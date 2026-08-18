#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_count=0
pass_count=0
fail_count=0

run_test() {
    local test_name="$1"
    local cmd="$2"
    local expected_exit="$3"
    local expected_output="$4"

    test_count=$((test_count + 1))
    echo -n "Test $test_count: $test_name ... "

    # Run command and capture output and exit code
    output=$(eval "$cmd" 2>&1)
    exit_code=$?

    # Check exit code
    if [ "$exit_code" != "$expected_exit" ]; then
        echo -e "${RED}FAIL${NC}"
        echo "  Expected exit code: $expected_exit, got: $exit_code"
        echo "  Command: $cmd"
        echo "  Output: $output"
        fail_count=$((fail_count + 1))
        return 1
    fi

    # Check output if specified
    if [ -n "$expected_output" ]; then
        if ! echo "$output" | grep -q "$expected_output"; then
            echo -e "${RED}FAIL${NC}"
            echo "  Expected output to contain: $expected_output"
            echo "  Got: $output"
            fail_count=$((fail_count + 1))
            return 1
        fi
    fi

    echo -e "${GREEN}PASS${NC}"
    pass_count=$((pass_count + 1))
    return 0
}

echo "=== Testing logpeek CLI ==="
echo

# Test 1: Single file output
run_test "boot.log summary" \
    "logpeek $SCRIPT_DIR/samples/boot.log" \
    0 \
    "Total lines: 6"

# Test 2: boot.log has correct level counts
run_test "boot.log level counts" \
    "logpeek $SCRIPT_DIR/samples/boot.log" \
    0 \
    "DEBUG (1), INFO (4), WARNING (1)"

# Test 3: boot.log time span
run_test "boot.log time span" \
    "logpeek $SCRIPT_DIR/samples/boot.log" \
    0 \
    "2026-05-31T23:58:00"

# Test 4: boot.log top loggers
run_test "boot.log top loggers" \
    "logpeek $SCRIPT_DIR/samples/boot.log" \
    0 \
    "boot.init: 3"

# Test 5: app_main.log summary
run_test "app_main.log total lines" \
    "logpeek $SCRIPT_DIR/samples/app_main.log" \
    0 \
    "Total lines: 40000"

# Test 6: app_main.log levels
run_test "app_main.log level counts" \
    "logpeek $SCRIPT_DIR/samples/app_main.log" \
    0 \
    "INFO"

# Test 7: Empty file
run_test "empty.log handles empty file" \
    "logpeek $SCRIPT_DIR/samples/empty.log" \
    0 \
    "Total lines: 0"

# Test 8: Nonexistent file error
run_test "nonexistent file error" \
    "logpeek /nonexistent/file.log" \
    1 \
    "Error"

# Test 9: Invalid log file error
run_test "invalid log file error" \
    "echo 'not a log file' > /tmp/test_invalid.log && logpeek /tmp/test_invalid.log" \
    1 \
    "Error"

# Test 10: --level INFO filter
run_test "--level INFO filter" \
    "logpeek --level INFO $SCRIPT_DIR/samples/boot.log" \
    0 \
    "Total lines: 4"

# Test 11: --level ERROR on boot.log
run_test "--level ERROR on boot.log" \
    "logpeek --level ERROR $SCRIPT_DIR/samples/boot.log" \
    0 \
    "Total lines: 0"

# Test 12: --json output is valid JSON
run_test "--json output is valid JSON" \
    "logpeek --json $SCRIPT_DIR/samples/boot.log | python3 -m json.tool > /dev/null && echo 'valid'" \
    0 \
    "valid"

# Test 13: --json contains file path
run_test "--json contains file path" \
    "logpeek --json $SCRIPT_DIR/samples/boot.log" \
    0 \
    "$SCRIPT_DIR/samples/boot.log"

# Test 14: Multiple files output
run_test "Multiple files output" \
    "logpeek $SCRIPT_DIR/samples/boot.log $SCRIPT_DIR/samples/empty.log" \
    0 \
    "Total lines: 6"

# Test 15: Multiple files with one error
run_test "Multiple files with one nonexistent (exit code 1)" \
    "logpeek $SCRIPT_DIR/samples/boot.log /nonexistent.log" \
    1 \
    "Total lines: 6"

# Test 16: Invalid level argument
run_test "Invalid level argument" \
    "logpeek --level INVALID $SCRIPT_DIR/samples/boot.log" \
    1 \
    "invalid log level"

# Test 17: File is not modified
run_test "File not modified during processing" \
    "cp $SCRIPT_DIR/samples/boot.log /tmp/test_copy.log && logpeek /tmp/test_copy.log > /dev/null && diff $SCRIPT_DIR/samples/boot.log /tmp/test_copy.log > /dev/null && echo ok" \
    0 \
    "ok"

# Test 18: Empty.log with --level filter
run_test "empty.log with --level filter" \
    "logpeek --level INFO $SCRIPT_DIR/samples/empty.log" \
    0 \
    "Total lines: 0"

echo
echo "=== Test Summary ==="
echo "Total: $test_count"
echo -e "Passed: ${GREEN}$pass_count${NC}"
echo -e "Failed: ${RED}$fail_count${NC}"

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
