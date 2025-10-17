"""Unit tests for Visualization Agent"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def sample_chart_data():
    """Sample chart data for testing"""
    return {
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "values": [100, 150, 180, 220]
    }


@pytest.fixture
def sample_multi_series_data():
    """Sample multi-series data for testing"""
    return {
        "labels": ["Jan", "Feb", "Mar", "Apr"],
        "series": {
            "Revenue": [100, 120, 140, 160],
            "Costs": [70, 80, 90, 100]
        }
    }


class TestChartGeneration:
    """Test chart generation functions"""
    
    def test_create_line_chart(self, sample_chart_data):
        """Test line chart creation"""
        from agents.visualization_agent.main import create_line_chart
        
        fig = create_line_chart(
            data=sample_chart_data,
            title="Test Line Chart",
            x_label="Quarter",
            y_label="Revenue"
        )
        
        assert fig is not None
        assert fig.layout.title.text == "Test Line Chart"
        assert fig.layout.xaxis.title.text == "Quarter"
        assert fig.layout.yaxis.title.text == "Revenue"
    
    def test_create_bar_chart(self, sample_chart_data):
        """Test bar chart creation"""
        from agents.visualization_agent.main import create_bar_chart
        
        fig = create_bar_chart(
            data=sample_chart_data,
            title="Test Bar Chart"
        )
        
        assert fig is not None
        assert fig.layout.title.text == "Test Bar Chart"
    
    def test_create_pie_chart(self, sample_chart_data):
        """Test pie chart creation"""
        from agents.visualization_agent.main import create_pie_chart
        
        fig = create_pie_chart(
            data=sample_chart_data,
            title="Test Pie Chart"
        )
        
        assert fig is not None
        assert fig.layout.title.text == "Test Pie Chart"
    
    def test_create_scatter_chart(self, sample_chart_data):
        """Test scatter chart creation"""
        from agents.visualization_agent.main import create_scatter_chart
        
        fig = create_scatter_chart(
            data=sample_chart_data,
            title="Test Scatter Chart"
        )
        
        assert fig is not None
        assert fig.layout.title.text == "Test Scatter Chart"
    
    def test_create_area_chart(self, sample_chart_data):
        """Test area chart creation"""
        from agents.visualization_agent.main import create_area_chart
        
        fig = create_area_chart(
            data=sample_chart_data,
            title="Test Area Chart"
        )
        
        assert fig is not None
        assert fig.layout.title.text == "Test Area Chart"
    
    def test_multi_series_line_chart(self, sample_multi_series_data):
        """Test multi-series line chart"""
        from agents.visualization_agent.main import create_line_chart
        
        fig = create_line_chart(
            data=sample_multi_series_data,
            title="Multi-Series Chart"
        )
        
        assert fig is not None
        assert len(fig.data) == 2  # Two series


class TestAPI:
    """Test API endpoints"""
    
    def test_health_endpoint(self):
        """Test health check"""
        from agents.visualization_agent.main import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["agent"] == "visualization"
        assert "capabilities" in data
        assert "chart_types" in data["capabilities"]
    
    def test_create_chart_endpoint(self, sample_chart_data):
        """Test chart creation endpoint"""
        from agents.visualization_agent.main import app
        
        client = TestClient(app)
        
        with patch('agents.visualization_agent.main.upload_to_storage') as mock_upload:
            mock_upload.return_value = (
                "gs://bucket/chart.html",
                "https://storage.googleapis.com/bucket/chart.html"
            )
            
            response = client.post(
                "/create",
                json={
                    "chart_type": "line",
                    "data": sample_chart_data,
                    "title": "Test Chart",
                    "save_to_storage": True
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "created"
            assert "chart_id" in data
    
    def test_invalid_chart_type(self, sample_chart_data):
        """Test invalid chart type handling"""
        from agents.visualization_agent.main import app
        
        client = TestClient(app)
        response = client.post(
            "/create",
            json={
                "chart_type": "invalid_type",
                "data": sample_chart_data,
                "title": "Test Chart"
            }
        )
        
        assert response.status_code == 400
    
    def test_create_line_endpoint(self, sample_chart_data):
        """Test quick line chart endpoint"""
        from agents.visualization_agent.main import app
        
        client = TestClient(app)
        
        with patch('agents.visualization_agent.main.upload_to_storage') as mock_upload:
            mock_upload.return_value = (None, None)
            
            response = client.post(
                "/create/line",
                params={"title": "Quick Line Chart", "save": False},
                json=sample_chart_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "created"
            assert "html" in data


class TestCloudStorage:
    """Test Cloud Storage integration"""
    
    def test_upload_to_storage_mock(self):
        """Test upload with mocked storage"""
        from agents.visualization_agent.main import upload_to_storage
        
        with patch('agents.visualization_agent.main.bucket') as mock_bucket:
            mock_blob = MagicMock()
            mock_blob.public_url = "https://storage.googleapis.com/test/chart.html"
            mock_bucket.blob.return_value = mock_blob
            
            html_content = "<html><body>Test Chart</body></html>"
            chart_id = "test-chart-123"
            
            storage_url, public_url = upload_to_storage(html_content, chart_id)
            
            assert "gs://" in storage_url
            assert "https://" in public_url
