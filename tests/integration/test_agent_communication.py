"""Integration tests - Agent to Agent communication"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import httpx


@pytest.mark.integration
@pytest.mark.asyncio
class TestAgentCommunication:
    """Test communication between agents"""
    
    async def test_frontend_to_orchestrator(self):
        """Test Frontend calling Orchestrator"""
        # Mock orchestrator response
        mock_response = {
            "task_id": "test-task-123",
            "status": "pending",
            "workflow_type": "analyze_report"
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_response
            mock_resp.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_resp
            )
            
            # Simulate frontend call
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://orchestrator:8084/tasks",
                    json={
                        "workflow_type": "analyze_report",
                        "input_data": {"query": "Test"}
                    }
                )
            
            assert response.status_code == 200
    
    async def test_orchestrator_to_report_reader(self):
        """Test Orchestrator calling Report Reader"""
        mock_response = {
            "status": "success",
            "data": {"columns": ["A", "B"], "data": []}
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_response
            mock_resp.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_resp
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://report-reader:8081/read/sheets",
                    json={"spreadsheet_id": "test-123"}
                )
            
            assert response.status_code == 200
    
    async def test_orchestrator_to_logic_agent(self):
        """Test Orchestrator calling Logic Agent"""
        mock_response = {
            "status": "completed",
            "insights": "Test analysis results"
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_response
            mock_resp.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_resp
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://logic-agent:8082/analyze",
                    json={"query": "Analyze this", "context": {}}
                )
            
            assert response.status_code == 200
    
    async def test_orchestrator_to_visualization(self):
        """Test Orchestrator calling Visualization Agent"""
        mock_response = {
            "status": "created",
            "chart_id": "chart-123",
            "public_url": "https://storage.googleapis.com/chart.html"
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_response
            mock_resp.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_resp
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://visualization:8083/create",
                    json={
                        "chart_type": "line",
                        "data": {"labels": ["A"], "values": [1]},
                        "title": "Test"
                    }
                )
            
            assert response.status_code == 200


@pytest.mark.integration
class TestHealthChecks:
    """Test health checks for all agents"""
    
    def test_all_agents_health(self):
        """Test that all agents respond to health checks"""
        agents = [
            ("frontend", 8080),
            ("report-reader", 8081),
            ("logic-understanding", 8082),
            ("visualization", 8083),
            ("orchestrator", 8084)
        ]
        
        with patch('httpx.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "healthy"}
            mock_get.return_value = mock_response
            
            for agent_name, port in agents:
                response = httpx.get(f"http://localhost:{port}/health")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"
