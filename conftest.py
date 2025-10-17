"""Pytest configuration and fixtures"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add agents to path
agents_path = project_root / "agents"
sys.path.insert(0, str(agents_path))

import pytest
from unittest.mock import Mock, MagicMock

# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )

# Common fixtures
@pytest.fixture
def mock_google_client():
    """Mock Google Cloud clients"""
    return MagicMock()

@pytest.fixture
def mock_vertexai():
    """Mock Vertex AI"""
    with pytest.mock.patch('vertexai.init'):
        yield

@pytest.fixture
def sample_financial_data():
    """Sample financial data for testing"""
    return {
        "revenue": [100000, 120000, 150000, 180000],
        "costs": [70000, 80000, 90000, 100000],
        "labels": ["Q1", "Q2", "Q3", "Q4"]
    }
