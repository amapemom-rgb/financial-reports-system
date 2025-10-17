#!/bin/bash
# Quick test run - simple tests that definitely work

echo "🧪 Running Simple Tests"
echo "======================"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "📦 Installing pytest..."
    pip install -q pytest pytest-cov
fi

echo ""
echo "Running unit tests..."
pytest tests/unit/test_logic_simple.py -v
pytest tests/unit/test_viz_simple.py -v  
pytest tests/unit/test_reader_simple.py -v

echo ""
echo "✅ Simple tests complete!"
echo ""
echo "To run with coverage:"
echo "  pytest tests/unit/test_*_simple.py --cov --cov-report=term"
