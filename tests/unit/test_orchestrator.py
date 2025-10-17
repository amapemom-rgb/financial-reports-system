"""Unit tests for Orchestrator Agent"""
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime


@pytest.fixture
def test_db():
    """Create test database"""
    from agents.orchestrator_agent.main import Base
    
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return TestingSessionLocal()


@pytest.fixture
def sample_task_data():
    """Sample task data for testing"""
    return {
        "workflow_type": "analyze_report",
        "input_data": {
            "spreadsheet_id": "test-sheet-123",
            "query": "Test analysis"
        }
    }


class TestDatabaseFunctions:
    """Test database operations"""
    
    def test_create_task(self, test_db):
        """Test task creation"""
        from agents.orchestrator_agent.main import create_task, WorkflowType
        
        task = create_task(
            test_db,
            WorkflowType.ANALYZE_REPORT,
            {"query": "Test"}
        )
        
        assert task.id is not None
        assert task.workflow_type == "analyze_report"
        assert task.status.value == "pending"
    
    def test_update_task_status(self, test_db):
        """Test updating task status"""
        from agents.orchestrator_agent.main import (
            create_task, 
            update_task_status,
            WorkflowType,
            TaskStatus
        )
        
        task = create_task(test_db, WorkflowType.ANALYZE_REPORT, {})
        
        updated_task = update_task_status(
            test_db,
            task.id,
            TaskStatus.COMPLETED,
            output_data={"result": "success"}
        )
        
        assert updated_task.status == TaskStatus.COMPLETED
        assert updated_task.output_data["result"] == "success"


class TestAPI:
    """Test API endpoints"""
    
    def test_health_endpoint(self):
        """Test health check"""
        from agents.orchestrator_agent.main import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["agent"] == "orchestrator"
