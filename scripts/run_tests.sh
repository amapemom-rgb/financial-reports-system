#!/bin/bash
# Run all tests with coverage

set -e

echo "🧪 Running Financial Reports System Tests"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Install test dependencies
echo -e "${YELLOW}📦 Installing test dependencies...${NC}"
pip install -r requirements-test.txt

# Run unit tests
echo -e "\n${YELLOW}🔬 Running Unit Tests...${NC}"
pytest tests/unit/ -v -m unit --cov=agents --cov-report=term-missing

# Run integration tests
echo -e "\n${YELLOW}🔗 Running Integration Tests...${NC}"
pytest tests/integration/ -v -m integration

# Run E2E tests (skip if services not running)
echo -e "\n${YELLOW}🌐 Running E2E Tests...${NC}"
if docker-compose ps | grep -q "Up"; then
    pytest tests/e2e/ -v -m e2e
else
    echo -e "${RED}⚠️  Skipping E2E tests - Docker services not running${NC}"
    echo "Run 'docker-compose up -d' to enable E2E tests"
fi

# Generate coverage report
echo -e "\n${YELLOW}📊 Generating Coverage Report...${NC}"
pytest tests/ --cov=agents --cov-report=html --cov-report=term

# Display coverage summary
echo -e "\n${GREEN}✅ Tests Complete!${NC}"
echo "Coverage report generated in: htmlcov/index.html"
echo ""
echo "Open with: open htmlcov/index.html (Mac) or xdg-open htmlcov/index.html (Linux)"
