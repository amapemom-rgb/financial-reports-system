#!/bin/bash
# Quick test runner - unit tests only

set -e

echo "🧪 Quick Test Run (Unit Tests Only)"
echo "===================================="

# Install dependencies
pip install -q -r requirements-test.txt

# Run unit tests with coverage
pytest tests/unit/ -v --cov=agents --cov-report=term-missing --cov-fail-under=70

echo ""
echo "✅ Unit tests passed with >70% coverage!"
