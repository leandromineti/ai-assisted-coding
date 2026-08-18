#!/bin/bash
# Validation script for logpeek CLI
# Tests the tool against sample files and asserts expected behavior

PASSED=0
FAILED=0

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=== logpeek CLI Validation ==="
echo

# Test 1: boot.log should parse successfully
echo -n "Test 1: Parse boot.log ... "
output=$(logpeek samples/boot.log 2>&1)
exit_code=$?
if [ $exit_code -eq 0 ] && \
   echo "$output" | grep -q "Total lines: 6" && \
   echo "$output" | grep -q "INFO: 4" && \
   echo "$output" | grep -q "DEBUG: 1" && \
   echo "$output" | grep -q "WARNING: 1" && \
   echo "$output" | grep -q "boot.init" && \
   echo "$output" | grep -q "boot.svc"; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    echo "Output: $output (exit code: $exit_code)"
    ((FAILED++))
fi

# Test 2: app_main.log should parse successfully
echo -n "Test 2: Parse app_main.log (40K lines) ... "
output=$(logpeek samples/app_main.log 2>&1)
exit_code=$?
if [ $exit_code -eq 0 ] && \
   echo "$output" | grep -q "Total lines: 40000" && \
   echo "$output" | grep -q "INFO:" && \
   echo "$output" | grep -q "api.gw"; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    echo "Output: $output (exit code: $exit_code)"
    ((FAILED++))
fi

# Test 3: empty.log should parse gracefully
echo -n "Test 3: Parse empty.log (0 lines) ... "
output=$(logpeek samples/empty.log 2>&1)
exit_code=$?
if [ $exit_code -eq 0 ] && echo "$output" | grep -q "Total lines: 0"; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    echo "Output: $output (exit code: $exit_code)"
    ((FAILED++))
fi

# Test 4: JSON output for boot.log
echo -n "Test 4: JSON output (--json flag) ... "
output=$(logpeek samples/boot.log --json 2>&1)
if echo "$output" | grep -q '"file"' && \
   echo "$output" | grep -q '"total_lines"' && \
   echo "$output" | grep -q '"level_counts"' && \
   echo "$output" | grep -q '"time_span"' && \
   echo "$output" | grep -q '"top_loggers"'; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    echo "Output: $output"
    ((FAILED++))
fi

# Test 5: Level filter (--level INFO)
echo -n "Test 5: Level filter (--level INFO) ... "
output=$(logpeek samples/boot.log --level INFO 2>&1)
if echo "$output" | grep -q "INFO: 4" && \
   ! echo "$output" | grep -q "DEBUG: 1"; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    echo "Output: $output"
    ((FAILED++))
fi

# Test 6: Multiple files
echo -n "Test 6: Multiple files ... "
output=$(logpeek samples/boot.log samples/empty.log 2>&1)
if echo "$output" | grep -q "boot.log" && \
   echo "$output" | grep -q "empty.log" && \
   echo "$output" | grep -q "Total lines: 6" && \
   echo "$output" | grep -q "Total lines: 0"; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    echo "Output: $output"
    ((FAILED++))
fi

# Test 7: Non-existent file should error
echo -n "Test 7: Non-existent file (error handling) ... "
output=$(logpeek /nonexistent/file.log 2>&1)
exit_code=$?
if [ $exit_code -ne 0 ] && echo "$output" | grep -q "Error"; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    echo "Exit code: $exit_code, Output: $output"
    ((FAILED++))
fi

# Test 8: Invalid level filter should error
echo -n "Test 8: Invalid level filter (error handling) ... "
output=$(logpeek samples/boot.log --level INVALID 2>&1)
exit_code=$?
if [ $exit_code -ne 0 ] && echo "$output" | grep -q "Invalid log level"; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    echo "Exit code: $exit_code, Output: $output"
    ((FAILED++))
fi

# Test 9: Non-log file should error
echo -n "Test 9: Non-log file (error handling) ... "
temp_file=$(mktemp)
echo "This is not a log file" > "$temp_file"
echo "Just some text" >> "$temp_file"
output=$(logpeek "$temp_file" 2>&1)
exit_code=$?
rm "$temp_file"
if [ $exit_code -ne 0 ] && echo "$output" | grep -q "not a valid log file"; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    echo "Exit code: $exit_code, Output: $output"
    ((FAILED++))
fi

# Test 10: Verify tool never modifies input
echo -n "Test 10: Tool never modifies input files ... "
temp_file=$(mktemp)
echo "2026-01-01T00:00:00+00:00 INFO app: test" > "$temp_file"
original_checksum=$(md5sum "$temp_file" | cut -d' ' -f1)
logpeek "$temp_file" > /dev/null 2>&1
final_checksum=$(md5sum "$temp_file" | cut -d' ' -f1)
rm "$temp_file"
if [ "$original_checksum" = "$final_checksum" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    ((FAILED++))
fi

# Test 11: Time span output
echo -n "Test 11: Time span output (first to last event) ... "
output=$(logpeek samples/boot.log 2>&1)
if echo "$output" | grep -q "Time span:" && \
   echo "$output" | grep -q "2026-05-31T23:58:00" && \
   echo "$output" | grep -q "2026-05-31T23:58:07"; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    echo "Output: $output"
    ((FAILED++))
fi

# Test 12: Top 5 loggers (or fewer if less exist)
echo -n "Test 12: Top loggers output ... "
output=$(logpeek samples/boot.log 2>&1)
if echo "$output" | grep -q "Top loggers:" && \
   echo "$output" | grep -q "boot.init" && \
   echo "$output" | grep -q "boot.svc"; then
    echo -e "${GREEN}PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    echo "Output: $output"
    ((FAILED++))
fi

echo
echo "=== Summary ==="
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
