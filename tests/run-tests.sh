#!/usr/bin/env bash
# Run all workflow tests

set -e

WORKFLOW_ROOT="${WORKFLOW_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "$WORKFLOW_ROOT"

echo "════════════════════════════════════════════════════════════"
echo "  🧪 Workflow Test Suite"
echo "════════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TOTAL=0
PASSED=0
FAILED=0

run_test_suite() {
    local name=$1
    local cmd=$2
    
    echo -e "${YELLOW}▶ Running $name...${NC}"
    echo ""
    
    if eval "$cmd"; then
        echo -e "${GREEN}✅ $name passed${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ $name failed${NC}"
        ((FAILED++))
    fi
    ((TOTAL++))
    echo ""
    echo "────────────────────────────────────────────────────────────"
    echo ""
}

# Unit Tests
run_test_suite "Unit Tests" "python3 -m unittest discover tests/unit -v 2>&1"

# Integration Tests
run_test_suite "Integration Tests" "python3 -m unittest tests.integration.test_workflow_integration -v 2>&1"

# Summary
echo "════════════════════════════════════════════════════════════"
echo "  📊 Test Summary"
echo "════════════════════════════════════════════════════════════"
echo ""
echo -e "  Total suites:  $TOTAL"
echo -e "  ${GREEN}Passed:        $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "  ${RED}Failed:        $FAILED${NC}"
else
    echo -e "  Failed:        $FAILED"
fi
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}💥 Some tests failed${NC}"
    exit 1
fi
