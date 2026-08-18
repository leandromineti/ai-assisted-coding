#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

PASSED=0
FAILED=0

run_test() {
    local test_name="$1"
    local expected_exit="$2"
    local check_stdout="$3"
    shift 3
    local cmd=("$@")

    echo -n "Testing: $test_name ... "

    output=$("${cmd[@]}" 2>&1)
    exit_code=$?

    local test_passed=true

    if [ "$exit_code" != "$expected_exit" ]; then
        echo -e "${RED}FAIL${NC} (exit code: expected $expected_exit, got $exit_code)"
        test_passed=false
    elif [ -n "$check_stdout" ] && ! echo "$output" | grep -q "$check_stdout"; then
        echo -e "${RED}FAIL${NC} (stdout missing: $check_stdout)"
        echo "  Got: $output" | head -3
        test_passed=false
    fi

    if [ "$test_passed" = true ]; then
        echo -e "${GREEN}PASS${NC}"
        ((PASSED++))
    else
        ((FAILED++))
    fi
}

echo "Running logpeek check script"
echo "======================================"

run_test "boot.log - total lines" 0 "Total lines: 6" \
    logpeek /app/samples/boot.log

run_test "boot.log - levels" 0 "INFO.*4" \
    logpeek /app/samples/boot.log

run_test "boot.log - time span" 0 "2026-05-31T23:58:00" \
    logpeek /app/samples/boot.log

run_test "boot.log - top loggers" 0 "boot.init\|boot.svc" \
    logpeek /app/samples/boot.log

run_test "app_main.log - total lines" 0 "Total lines: 40000" \
    logpeek /app/samples/app_main.log

run_test "app_main.log - level distribution" 0 "INFO.*21307" \
    logpeek /app/samples/app_main.log

run_test "app_main.log - contains CRITICAL" 0 "CRITICAL" \
    logpeek /app/samples/app_main.log

run_test "empty.log - zero lines" 0 "Total lines: 0" \
    logpeek /app/samples/empty.log

run_test "empty.log - exit code 0" 0 "" \
    logpeek /app/samples/empty.log

run_test "nonexistent file - error exit code 1" 1 "" \
    logpeek /app/samples/nonexistent.log

run_test "level filter - INFO only" 0 "Levels: INFO" \
    logpeek /app/samples/boot.log --level INFO

run_test "level filter - count matches" 0 "INFO.*4" \
    logpeek /app/samples/boot.log --level INFO

run_test "JSON output - is valid JSON" 0 '"file"' \
    logpeek /app/samples/boot.log --json

run_test "JSON output - contains total_lines" 0 '"total_lines": 6' \
    logpeek /app/samples/boot.log --json

run_test "JSON output - contains time_span" 0 '"time_span"' \
    logpeek /app/samples/boot.log --json

run_test "JSON output - with level filter" 0 '"INFO": 4' \
    logpeek /app/samples/boot.log --level INFO --json

run_test "multiple files" 0 "boot.log" \
    logpeek /app/samples/boot.log /app/samples/empty.log

run_test "app_main.log - top logger api.gw" 0 "api.gw" \
    logpeek /app/samples/app_main.log

run_test "app_main.log - JSON has top_loggers" 0 '"top_loggers"' \
    logpeek /app/samples/app_main.log --json

run_test "unit tests pass" 0 "Ran" \
    python -m unittest test_logpeek

echo ""
echo "======================================"
echo -e "Results: ${GREEN}$PASSED passed${NC}, ${RED}$FAILED failed${NC}"

if [ $FAILED -eq 0 ]; then
    exit 0
else
    exit 1
fi
