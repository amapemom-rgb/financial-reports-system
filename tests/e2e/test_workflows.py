"""End-to-End tests - Full workflow testing"""
import pytest
from unittest.mock import patch, AsyncMock, Mock
import httpx
import time


@pytest.mark.e2e
@pytest.mark.asyncio
class TestAnalyzeReportWorkflow:
    """Test complete analyze report workflow"""
    
    async def test_full_analyze_workflow(self):
        """Test full workflow: Frontend → Orchestrator → Agents → Result"""
        
        # Step 1: Create task via Orchestrator
        with patch('httpx.AsyncClient') as mock_client:
            # Mock orchestrator response
            mock_create_response = AsyncMock()
            mock_create_response.status_code = 200
            mock_create_response.json.return_value = {
                "task_id": "test-task-123",
                "status": "pending",
                "workflow_type": "analyze_report"
            }
            mock_create_response.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_create_response
            )
            
            # Create task
            async with httpx.AsyncClient() as client:
                create_response = await client.post(
                    "http://localhost:8084/tasks",
                    json={
                        "workflow_type": "analyze_report",
                        "input_data": {
                            "query": "Analyze revenue trends"
                        }
                    },
                    timeout=30.0
                )
            
            assert create_response.status_code == 200
            task_data = create_response.json()
            task_id = task_data["task_id"]
            
            # Step 2: Wait and check task status
            mock_status_response = AsyncMock()
            mock_status_response.status_code = 200
            mock_status_response.json.return_value = {
                "task_id": task_id,
                "status": "completed",
                "workflow_type": "analyze_report",
                "output_data": {
                    "report_data": {"status": "success"},
                    "analysis": {"insights": "Revenue growing"},
                    "visualization": {"chart_id": "chart-123"}
                }
            }
            mock_status_response.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_status_response
            )
            
            async with httpx.AsyncClient() as client:
                status_response = await client.get(
                    f"http://localhost:8084/tasks/{task_id}",
                    timeout=30.0
                )
            
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["status"] == "completed"
            assert "output_data" in status_data


@pytest.mark.e2e
@pytest.mark.asyncio
class TestVoiceAnalysisWorkflow:
    """Test voice analysis workflow"""
    
    async def test_voice_to_text_to_analysis(self):
        """Test: Voice → STT → Analysis → TTS → Voice"""
        
        with patch('httpx.AsyncClient') as mock_client:
            # Mock voice analysis response
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "voice_input": {
                    "transcript": "Analyze the report",
                    "confidence": 0.95
                },
                "analysis": {
                    "insights": "Report shows growth"
                },
                "audio_response": "base64_encoded_audio"
            }
            mock_response.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            # Simulate voice input
            fake_audio = b"fake_audio_data"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8080/voice/analyze",
                    files={"audio": ("test.wav", fake_audio, "audio/wav")},
                    data={"language": "ru-RU"},
                    timeout=60.0
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"


@pytest.mark.e2e
@pytest.mark.asyncio
class TestVisualizationWorkflow:
    """Test visualization generation workflow"""
    
    async def test_create_and_retrieve_chart(self):
        """Test: Create chart → Save to storage → Retrieve"""
        
        with patch('httpx.AsyncClient') as mock_client:
            # Mock chart creation
            mock_create = AsyncMock()
            mock_create.status_code = 200
            mock_create.json.return_value = {
                "status": "created",
                "chart_id": "chart-test-123",
                "public_url": "https://storage.googleapis.com/bucket/chart.html"
            }
            mock_create.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_create
            )
            
            # Create chart
            async with httpx.AsyncClient() as client:
                create_response = await client.post(
                    "http://localhost:8083/create",
                    json={
                        "chart_type": "line",
                        "data": {
                            "labels": ["Q1", "Q2", "Q3", "Q4"],
                            "values": [100, 150, 180, 220]
                        },
                        "title": "Revenue Growth",
                        "save_to_storage": True
                    },
                    timeout=30.0
                )
            
            assert create_response.status_code == 200
            chart_data = create_response.json()
            chart_id = chart_data["chart_id"]
            
            # Mock chart retrieval
            mock_get = AsyncMock()
            mock_get.status_code = 200
            mock_get.json.return_value = {
                "chart_id": chart_id,
                "public_url": "https://storage.googleapis.com/bucket/chart.html"
            }
            mock_get.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_get
            )
            
            # Retrieve chart
            async with httpx.AsyncClient() as client:
                get_response = await client.get(
                    f"http://localhost:8083/charts/{chart_id}",
                    timeout=30.0
                )
            
            assert get_response.status_code == 200


@pytest.mark.e2e
class TestSystemHealth:
    """Test overall system health"""
    
    def test_all_services_running(self):
        """Test that all services are up and responding"""
        services = {
            "frontend": "http://localhost:8080/health",
            "report-reader": "http://localhost:8081/health",
            "logic-understanding": "http://localhost:8082/health",
            "visualization": "http://localhost:8083/health",
            "orchestrator": "http://localhost:8084/health"
        }
        
        with patch('httpx.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "healthy"}
            mock_get.return_value = mock_response
            
            results = {}
            for service_name, url in services.items():
                try:
                    response = httpx.get(url, timeout=5.0)
                    results[service_name] = response.status_code == 200
                except Exception as e:
                    results[service_name] = False
            
            # All services should be healthy
            assert all(results.values()), f"Some services are down: {results}"
