#!/bin/bash
# Script to run TradeKing API tests

set -e  # Exit on error

echo "========================================="
echo "TradeKing API Testing Suite"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Warning: No virtual environment detected${NC}"
    echo "Consider activating a virtual environment first:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate  # Linux/Mac"
    echo "  venv\\Scripts\\activate     # Windows"
    echo ""
fi

# Parse command line arguments
TEST_TYPE="${1:-all}"
VERBOSE=""
COVERAGE=""

for arg in "$@"; do
    case $arg in
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -c|--coverage)
            COVERAGE="--cov=backend --cov=trade_agent --cov-report=html --cov-report=term"
            shift
            ;;
    esac
done

# Function to run tests
run_tests() {
    local test_path=$1
    local description=$2

    echo -e "${YELLOW}Running ${description}...${NC}"
    pytest $test_path $VERBOSE $COVERAGE

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ ${description} passed${NC}"
    else
        echo -e "${RED}✗ ${description} failed${NC}"
        exit 1
    fi
    echo ""
}

# Main test execution
case $TEST_TYPE in
    all)
        echo "Running all tests..."
        run_tests "tests/" "All Tests"
        ;;
    api)
        run_tests "tests/api/" "API Tests"
        ;;
    integration)
        run_tests "tests/integration/" "Integration Tests"
        ;;
    health)
        run_tests "tests/api/test_health.py" "Health Check Tests"
        ;;
    decisions)
        run_tests "tests/api/test_decisions.py" "Decisions API Tests"
        ;;
    models)
        run_tests "tests/api/test_models.py" "Models API Tests"
        ;;
    portfolio)
        run_tests "tests/api/test_portfolio.py" "Portfolio API Tests"
        ;;
    quick)
        echo "Running quick tests (API only, no coverage)..."
        pytest tests/api/ -v --tb=short
        ;;
    *)
        echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
        echo ""
        echo "Usage: $0 [TEST_TYPE] [OPTIONS]"
        echo ""
        echo "Test Types:"
        echo "  all          - Run all tests (default)"
        echo "  api          - Run API endpoint tests only"
        echo "  integration  - Run integration tests only"
        echo "  health       - Run health check tests"
        echo "  decisions    - Run decisions API tests"
        echo "  models       - Run models API tests"
        echo "  portfolio    - Run portfolio API tests"
        echo "  quick        - Quick test run (no coverage)"
        echo ""
        echo "Options:"
        echo "  -v, --verbose   - Verbose output"
        echo "  -c, --coverage  - Generate coverage report"
        echo ""
        echo "Examples:"
        echo "  $0 all -v -c              # All tests with coverage"
        echo "  $0 api -v                 # API tests verbose"
        echo "  $0 quick                  # Quick API test"
        exit 1
        ;;
esac

# Show coverage report if generated
if [ ! -z "$COVERAGE" ]; then
    echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
    echo "Open it with: xdg-open htmlcov/index.html  # Linux"
    echo "          or: open htmlcov/index.html      # Mac"
fi

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}All tests completed successfully!${NC}"
echo -e "${GREEN}=========================================${NC}"
