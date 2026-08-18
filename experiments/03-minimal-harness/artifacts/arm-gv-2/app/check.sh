#!/bin/bash

FAILURES=0

# Helper function to check exit code
check_exit_code() {
    local expected="$1"
    local actual="$2"
    if [ "$actual" -eq "$expected" ]; then
        echo "  ✓ PASS"
        return 0
    else
        echo "  ✗ FAIL (Expected exit code $expected, got $actual)"
        return 1
    fi
}

# Helper function to check output contains string
check_output_contains() {
    local output="$1"
    local expected="$2"
    if echo "$output" | grep -q "$expected"; then
        echo "  ✓ PASS"
        return 0
    else
        echo "  ✗ FAIL (Expected to contain: $expected)"
        return 1
    fi
}

# Helper function to check exit code and output
check_exit_and_output() {
    local expected_exit="$1"
    local expected_output="$2"
    shift 2
    local output
    output=$("$@" 2>&1)
    local actual_exit=$?

    if [ "$actual_exit" -ne "$expected_exit" ]; then
        echo "  ✗ FAIL (Expected exit code $expected_exit, got $actual_exit)"
        return 1
    fi

    if ! echo "$output" | grep -q "$expected_output"; then
        echo "  ✗ FAIL (Expected output to contain: $expected_output)"
        return 1
    fi

    echo "  ✓ PASS"
    return 0
}

echo "============================================"
echo "logpeek Check Suite"
echo "============================================"
echo ""

# Test 1: boot.log basic analysis
echo "Test 1: boot.log basic analysis"
output=$(logpeek /app/samples/boot.log)
echo "  Checking total lines..."
check_output_contains "$output" "Total lines: 6" || FAILURES=$((FAILURES + 1))
echo "  Checking INFO level count..."
check_output_contains "$output" "INFO: 4" || FAILURES=$((FAILURES + 1))
echo "  Checking DEBUG level count..."
check_output_contains "$output" "DEBUG: 1" || FAILURES=$((FAILURES + 1))
echo "  Checking WARNING level count..."
check_output_contains "$output" "WARNING: 1" || FAILURES=$((FAILURES + 1))
echo "  Checking time span..."
check_output_contains "$output" "Time span:" || FAILURES=$((FAILURES + 1))
echo "  Checking top loggers..."
check_output_contains "$output" "Top loggers:" || FAILURES=$((FAILURES + 1))

echo ""

# Test 2: app_main.log analysis
echo "Test 2: app_main.log analysis"
output=$(logpeek /app/samples/app_main.log)
echo "  Checking entries exist..."
check_output_contains "$output" "Total lines:" || FAILURES=$((FAILURES + 1))
echo "  Checking levels exist..."
check_output_contains "$output" "Levels:" || FAILURES=$((FAILURES + 1))
echo "  Checking time span..."
check_output_contains "$output" "Time span:" || FAILURES=$((FAILURES + 1))
echo "  Checking top loggers..."
check_output_contains "$output" "Top loggers:" || FAILURES=$((FAILURES + 1))

echo ""

# Test 3: empty.log
echo "Test 3: empty.log handling"
output=$(logpeek /app/samples/empty.log)
exit_code=$?
echo "  Checking exit code..."
check_exit_code 0 $exit_code || FAILURES=$((FAILURES + 1))
echo "  Checking total lines is 0..."
check_output_contains "$output" "Total lines: 0" || FAILURES=$((FAILURES + 1))
echo "  Checking no levels..."
check_output_contains "$output" "Levels: (none)" || FAILURES=$((FAILURES + 1))

echo ""

# Test 4: Level filtering
echo "Test 4: Level filtering"
output=$(logpeek --level INFO /app/samples/boot.log)
echo "  Checking filtered output has INFO..."
check_output_contains "$output" "INFO:" || FAILURES=$((FAILURES + 1))

echo ""

# Test 5: JSON output
echo "Test 5: JSON output"
output=$(logpeek --json /app/samples/boot.log)
echo "  Checking valid JSON..."
if echo "$output" | python3 -m json.tool > /dev/null 2>&1; then
    echo "  ✓ PASS"
else
    echo "  ✗ FAIL (Invalid JSON)"
    FAILURES=$((FAILURES + 1))
fi
echo "  Checking file path in JSON..."
check_output_contains "$output" "/app/samples/boot.log" || FAILURES=$((FAILURES + 1))
echo "  Checking total_lines in JSON..."
check_output_contains "$output" "total_lines" || FAILURES=$((FAILURES + 1))
echo "  Checking levels in JSON..."
check_output_contains "$output" "levels" || FAILURES=$((FAILURES + 1))
echo "  Checking time_span in JSON..."
check_output_contains "$output" "time_span" || FAILURES=$((FAILURES + 1))
echo "  Checking top_loggers in JSON..."
check_output_contains "$output" "top_loggers" || FAILURES=$((FAILURES + 1))

echo ""

# Test 6: Multiple files
echo "Test 6: Multiple files"
output=$(logpeek /app/samples/boot.log /app/samples/empty.log)
echo "  Checking first file in output..."
check_output_contains "$output" "boot.log" || FAILURES=$((FAILURES + 1))
echo "  Checking second file in output..."
check_output_contains "$output" "empty.log" || FAILURES=$((FAILURES + 1))

echo ""

# Test 7: Non-existent file error
echo "Test 7: Non-existent file error"
output=$(logpeek /nonexistent/file.log 2>&1)
exit_code=$?
echo "  Checking exit code is 1..."
check_exit_code 1 $exit_code || FAILURES=$((FAILURES + 1))
echo "  Checking error message..."
check_output_contains "$output" "Error:" || FAILURES=$((FAILURES + 1))

echo ""

# Test 8: Non-log file error
echo "Test 8: Non-log file error"
tmpfile=$(mktemp)
echo "This is not a log file" > "$tmpfile"
output=$(logpeek "$tmpfile" 2>&1)
exit_code=$?
echo "  Checking exit code is 1..."
check_exit_code 1 $exit_code || FAILURES=$((FAILURES + 1))
echo "  Checking error message..."
check_output_contains "$output" "Error:" || FAILURES=$((FAILURES + 1))
rm "$tmpfile"

echo ""

# Test 9: All sample files together
echo "Test 9: All sample files together"
output=$(logpeek /app/samples/boot.log /app/samples/app_main.log /app/samples/empty.log 2>&1)
exit_code=$?
echo "  Checking exit code is 0..."
check_exit_code 0 $exit_code || FAILURES=$((FAILURES + 1))
echo "  Checking boot.log in output..."
check_output_contains "$output" "boot.log" || FAILURES=$((FAILURES + 1))
echo "  Checking app_main.log in output..."
check_output_contains "$output" "app_main.log" || FAILURES=$((FAILURES + 1))
echo "  Checking empty.log in output..."
check_output_contains "$output" "empty.log" || FAILURES=$((FAILURES + 1))

echo ""

# Test 10: JSON with multiple files
echo "Test 10: JSON with multiple files"
output=$(logpeek --json /app/samples/boot.log /app/samples/empty.log)
exit_code=$?
echo "  Checking valid JSON..."
if echo "$output" | python3 -m json.tool > /dev/null 2>&1; then
    echo "  ✓ PASS"
else
    echo "  ✗ FAIL (Invalid JSON)"
    FAILURES=$((FAILURES + 1))
fi
echo "  Checking is array..."
check_output_contains "$output" "\[" || FAILURES=$((FAILURES + 1))

echo ""

# Test 11: Verify file is never modified
echo "Test 11: Verify files are never modified"
original_boot=$(sha256sum /app/samples/boot.log | awk '{print $1}')
logpeek /app/samples/boot.log > /dev/null
current_boot=$(sha256sum /app/samples/boot.log | awk '{print $1}')
if [ "$original_boot" = "$current_boot" ]; then
    echo "  ✓ PASS (boot.log unchanged)"
else
    echo "  ✗ FAIL (boot.log was modified)"
    FAILURES=$((FAILURES + 1))
fi

original_app=$(sha256sum /app/samples/app_main.log | awk '{print $1}')
logpeek /app/samples/app_main.log > /dev/null
current_app=$(sha256sum /app/samples/app_main.log | awk '{print $1}')
if [ "$original_app" = "$current_app" ]; then
    echo "  ✓ PASS (app_main.log unchanged)"
else
    echo "  ✗ FAIL (app_main.log was modified)"
    FAILURES=$((FAILURES + 1))
fi

echo ""
echo "============================================"
if [ $FAILURES -eq 0 ]; then
    echo "All tests passed!"
    exit 0
else
    echo "$FAILURES test(s) failed"
    exit 1
fi
