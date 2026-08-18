#!/bin/bash

# check.sh: Verify logpeek CLI against real input files

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SAMPLES_DIR="$SCRIPT_DIR/samples"
LOGPEEK_CMD="logpeek"

failed=0
passed=0

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Test helper
assert_exit_code() {
    local expected=$1
    local actual=$2
    local test_name=$3

    if [ "$actual" -eq "$expected" ]; then
        echo -e "${GREEN}✓${NC} $test_name (exit code $actual)"
        ((passed++))
    else
        echo -e "${RED}✗${NC} $test_name (expected exit code $expected, got $actual)"
        ((failed++))
    fi
}

assert_stdout_contains() {
    local text=$1
    local output=$2
    local test_name=$3

    if echo "$output" | grep -F -q "$text"; then
        echo -e "${GREEN}✓${NC} $test_name"
        ((passed++))
    else
        echo -e "${RED}✗${NC} $test_name"
        echo "  Expected to find: $text"
        echo "  In output: $output"
        ((failed++))
    fi
}

assert_stdout_not_contains() {
    local text=$1
    local output=$2
    local test_name=$3

    if ! echo "$output" | grep -F -q "$text"; then
        echo -e "${GREEN}✓${NC} $test_name"
        ((passed++))
    else
        echo -e "${RED}✗${NC} $test_name"
        echo "  Expected NOT to find: $text"
        echo "  In output: $output"
        ((failed++))
    fi
}

assert_stderr_contains() {
    local text=$1
    local stderr=$2
    local test_name=$3

    if echo "$stderr" | grep -F -q "$text"; then
        echo -e "${GREEN}✓${NC} $test_name"
        ((passed++))
    else
        echo -e "${RED}✗${NC} $test_name"
        echo "  Expected to find: $text"
        echo "  In stderr: $stderr"
        ((failed++))
    fi
}

echo "=== Testing logpeek CLI ==="
echo ""

# Test 1: boot.log basic analysis
echo "Test Group 1: boot.log"
output=$($LOGPEEK_CMD "$SAMPLES_DIR/boot.log")
exit_code=$?
assert_exit_code 0 $exit_code "boot.log: should succeed"
assert_stdout_contains "Total lines: 6" "$output" "boot.log: total lines"
assert_stdout_contains "By level:" "$output" "boot.log: by level header"
assert_stdout_contains "INFO: 4" "$output" "boot.log: INFO count"
assert_stdout_contains "DEBUG: 1" "$output" "boot.log: DEBUG count"
assert_stdout_contains "WARNING: 1" "$output" "boot.log: WARNING count"
assert_stdout_contains "boot.init" "$output" "boot.log: boot.init logger"
assert_stdout_contains "boot.svc" "$output" "boot.log: boot.svc logger"
assert_stdout_contains "2026-05-31T23:58:00+00:00 to 2026-05-31T23:58:07+00:00" "$output" "boot.log: time span"
echo ""

# Test 2: app_main.log basic analysis
echo "Test Group 2: app_main.log"
output=$($LOGPEEK_CMD "$SAMPLES_DIR/app_main.log")
exit_code=$?
assert_exit_code 0 $exit_code "app_main.log: should succeed"
assert_stdout_contains "Total lines: 39803" "$output" "app_main.log: total lines (ignoring malformed)"
assert_stdout_contains "By level:" "$output" "app_main.log: by level header"
assert_stdout_contains "api.gw" "$output" "app_main.log: api.gw in top loggers"
assert_stdout_contains "api.http" "$output" "app_main.log: api.http in top loggers"
echo ""

# Test 3: empty.log should fail
echo "Test Group 3: empty.log (error case)"
output=$($LOGPEEK_CMD "$SAMPLES_DIR/empty.log" 2>&1)
exit_code=$?
assert_exit_code 1 $exit_code "empty.log: should fail with exit code 1"
assert_stderr_contains "No valid log lines found" "$output" "empty.log: error message"
echo ""

# Test 4: nonexistent file
echo "Test Group 4: nonexistent file"
output=$($LOGPEEK_CMD /nonexistent/file.log 2>&1)
exit_code=$?
assert_exit_code 1 $exit_code "nonexistent file: should fail"
assert_stderr_contains "File not found" "$output" "nonexistent file: error message"
echo ""

# Test 5: level filtering
echo "Test Group 5: level filtering"
output=$($LOGPEEK_CMD --level ERROR "$SAMPLES_DIR/app_main.log")
exit_code=$?
assert_exit_code 0 $exit_code "level filter: should succeed"
assert_stdout_contains "By level:" "$output" "level filter: by level header"
assert_stdout_contains "ERROR:" "$output" "level filter: has ERROR level"
# Verify filtering reduces total lines
assert_stdout_contains "Total lines: 4830" "$output" "level filter: ERROR count is 4830 (less than 39803)"
# Full output without filter
full_output=$($LOGPEEK_CMD "$SAMPLES_DIR/app_main.log" | grep "Total lines")
filtered_output=$(echo "$output" | grep "Total lines")
if [ "$full_output" != "$filtered_output" ]; then
    echo -e "${GREEN}✓${NC} level filter: filtered result differs from full result"
    ((passed++))
else
    echo -e "${RED}✗${NC} level filter: filtering did not change result"
    ((failed++))
fi
echo ""

# Test 6: JSON output
echo "Test Group 6: JSON output"
output=$($LOGPEEK_CMD --json "$SAMPLES_DIR/boot.log")
exit_code=$?
assert_exit_code 0 $exit_code "JSON output: should succeed"
# Check if output is valid JSON by parsing it
if echo "$output" | python3 -m json.tool > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} JSON output: valid JSON"
    ((passed++))
else
    echo -e "${RED}✗${NC} JSON output: invalid JSON"
    ((failed++))
fi
assert_stdout_contains '"file":' "$output" "JSON output: contains file field"
assert_stdout_contains '"total_lines":' "$output" "JSON output: contains total_lines"
echo ""

# Test 7: Multiple files
echo "Test Group 7: multiple files"
output=$($LOGPEEK_CMD "$SAMPLES_DIR/boot.log" "$SAMPLES_DIR/app_main.log")
exit_code=$?
assert_exit_code 0 $exit_code "multiple files: should succeed"
assert_stdout_contains "$SAMPLES_DIR/boot.log" "$output" "multiple files: boot.log in output"
assert_stdout_contains "$SAMPLES_DIR/app_main.log" "$output" "multiple files: app_main.log in output"
echo ""

# Test 8: Malformed lines are skipped gracefully
echo "Test Group 8: malformed lines handling"
# Create a temp file with mixed valid and invalid lines
tmpfile=$(mktemp)
cat > "$tmpfile" << 'EOF'
2026-05-31T23:58:00+00:00 INFO boot.init: valid line
{unterminated json dump
2026-05-31T23:58:01+00:00 ERROR boot.init: another valid line
EOF
output=$($LOGPEEK_CMD "$tmpfile")
exit_code=$?
assert_exit_code 0 $exit_code "malformed lines: should succeed with mixed content"
assert_stdout_contains "Total lines: 2" "$output" "malformed lines: counts only valid lines"
rm "$tmpfile"
echo ""

# Test 9: Files are not modified
echo "Test Group 9: file integrity"
boot_md5_before=$(md5sum "$SAMPLES_DIR/boot.log" | cut -d' ' -f1)
app_md5_before=$(md5sum "$SAMPLES_DIR/app_main.log" | cut -d' ' -f1)
empty_md5_before=$(md5sum "$SAMPLES_DIR/empty.log" | cut -d' ' -f1)

# Run logpeek multiple times
$LOGPEEK_CMD "$SAMPLES_DIR/boot.log" > /dev/null 2>&1 || true
$LOGPEEK_CMD "$SAMPLES_DIR/app_main.log" > /dev/null 2>&1 || true
$LOGPEEK_CMD "$SAMPLES_DIR/empty.log" > /dev/null 2>&1 || true
$LOGPEEK_CMD --json "$SAMPLES_DIR/boot.log" > /dev/null 2>&1 || true

boot_md5_after=$(md5sum "$SAMPLES_DIR/boot.log" | cut -d' ' -f1)
app_md5_after=$(md5sum "$SAMPLES_DIR/app_main.log" | cut -d' ' -f1)
empty_md5_after=$(md5sum "$SAMPLES_DIR/empty.log" | cut -d' ' -f1)

if [ "$boot_md5_before" = "$boot_md5_after" ]; then
    echo -e "${GREEN}✓${NC} file integrity: boot.log unchanged"
    ((passed++))
else
    echo -e "${RED}✗${NC} file integrity: boot.log was modified"
    ((failed++))
fi

if [ "$app_md5_before" = "$app_md5_after" ]; then
    echo -e "${GREEN}✓${NC} file integrity: app_main.log unchanged"
    ((passed++))
else
    echo -e "${RED}✗${NC} file integrity: app_main.log was modified"
    ((failed++))
fi

if [ "$empty_md5_before" = "$empty_md5_after" ]; then
    echo -e "${GREEN}✓${NC} file integrity: empty.log unchanged"
    ((passed++))
else
    echo -e "${RED}✗${NC} file integrity: empty.log was modified"
    ((failed++))
fi
echo ""

# Summary
echo "=== Test Results ==="
echo -e "Passed: ${GREEN}$passed${NC}"
echo -e "Failed: ${RED}$failed${NC}"

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
