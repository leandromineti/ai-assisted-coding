#!/bin/bash
# Demo script showing logpeek functionality

echo "=========================================="
echo "logpeek Demo"
echo "=========================================="
echo ""

echo "1. Basic usage - analyze boot.log:"
echo ""
logpeek /app/samples/boot.log
echo ""

echo "=========================================="
echo ""

echo "2. Analyze large file - app_main.log:"
echo ""
logpeek /app/samples/app_main.log
echo ""

echo "=========================================="
echo ""

echo "3. Filter by level - only CRITICAL events:"
echo ""
logpeek --level CRITICAL /app/samples/app_main.log
echo ""

echo "=========================================="
echo ""

echo "4. Multiple files:"
echo ""
logpeek /app/samples/boot.log /app/samples/empty.log
echo ""

echo "=========================================="
echo ""

echo "5. JSON output:"
echo ""
logpeek --json /app/samples/boot.log | head -15
echo "   ... (truncated)"
echo ""

echo "=========================================="
echo ""

echo "6. Error handling - non-log file:"
echo ""
echo "test" > /tmp/test.txt
logpeek /tmp/test.txt 2>&1
echo ""

echo "7. Error handling - missing file:"
echo ""
logpeek /nonexistent/file.log 2>&1
echo ""

echo "=========================================="
