"""Unit tests for Logic Understanding Agent"""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestFinancialMetrics:
    """Test financial metrics calculations"""
    
    def test_calculate_roi(self):
        """Test ROI calculation"""
        from agents.logic_understanding_agent.main import calculate_financial_metrics_impl
        
        result = calculate_financial_metrics_impl(
            metric_type="roi",
            values={"revenue": 150000, "investment": 100000}
        )
        
        assert result["metric"] == "ROI"
        assert result["value"] == 50.0
        assert result["unit"] == "%"
    
    def test_calculate_profit_margin(self):
        """Test profit margin calculation"""
        from agents.logic_understanding_agent.main import calculate_financial_metrics_impl
        
        result = calculate_financial_metrics_impl(
            metric_type="profit_margin",
            values={"revenue": 1000000, "costs": 700000}
        )
        
        assert result["metric"] == "Profit Margin"
        assert result["value"] == 30.0
        assert result["unit"] == "%"
    
    def test_calculate_growth_rate(self):
        """Test growth rate calculation"""
        from agents.logic_understanding_agent.main import calculate_financial_metrics_impl
        
        result = calculate_financial_metrics_impl(
            metric_type="growth_rate",
            values={"revenue": 120000, "previous_value": 100000}
        )
        
        assert result["metric"] == "Growth Rate"
        assert result["value"] == 20.0
        assert result["unit"] == "%"
    
    def test_calculate_debt_ratio(self):
        """Test debt ratio calculation"""
        from agents.logic_understanding_agent.main import calculate_financial_metrics_impl
        
        result = calculate_financial_metrics_impl(
            metric_type="debt_ratio",
            values={"costs": 400000, "revenue": 1000000}
        )
        
        assert result["metric"] == "Debt Ratio"
        assert result["value"] == 0.4
        assert result["unit"] == "ratio"
    
    def test_invalid_metric_type(self):
        """Test handling of invalid metric type"""
        from agents.logic_understanding_agent.main import calculate_financial_metrics_impl
        
        result = calculate_financial_metrics_impl(
            metric_type="invalid_metric",
            values={"revenue": 100000}
        )
        
        assert "error" in result


class TestTrendAnalysis:
    """Test trend analysis functions"""
    
    def test_analyze_growing_trend(self):
        """Test analysis of growing trend"""
        from agents.logic_understanding_agent.main import analyze_trend_impl
        
        result = analyze_trend_impl(
            data_points=[100, 120, 140, 160, 180],
            period="monthly"
        )
        
        assert result["trend"] == "growing"
        assert result["change_percent"] > 0
        assert result["period"] == "monthly"
        assert result["data_points_analyzed"] == 5
    
    def test_analyze_declining_trend(self):
        """Test analysis of declining trend"""
        from agents.logic_understanding_agent.main import analyze_trend_impl
        
        result = analyze_trend_impl(
            data_points=[180, 160, 140, 120, 100],
            period="quarterly"
        )
        
        assert result["trend"] == "declining"
        assert result["change_percent"] > 0
        assert result["period"] == "quarterly"
    
    def test_analyze_stable_trend(self):
        """Test analysis of stable trend"""
        from agents.logic_understanding_agent.main import analyze_trend_impl
        
        result = analyze_trend_impl(
            data_points=[100, 105, 98, 102, 101],
            period="yearly"
        )
        
        assert result["trend"] == "stable"
    
    def test_insufficient_data(self):
        """Test handling of insufficient data"""
        from agents.logic_understanding_agent.main import analyze_trend_impl
        
        result = analyze_trend_impl(
            data_points=[100],
            period="monthly"
        )
        
        assert result["trend"] == "insufficient_data"


class TestGetReportData:
    """Test report data retrieval"""
    
    def test_get_report_data(self):
        """Test getting report data"""
        from agents.logic_understanding_agent.main import get_report_data_impl
        
        result = get_report_data_impl(
            report_id="test-report-123",
            section="revenue"
        )
        
        assert result["report_id"] == "test-report-123"
        assert result["section"] == "revenue"
        assert "status" in result


@pytest.mark.asyncio
class TestAPI:
    """Test API endpoints"""
    
    async def test_health_endpoint(self):
        """Test health check endpoint"""
        from agents.logic_understanding_agent.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["agent"] == "logic-understanding"
        assert "tools" in data
        assert "google_search" in data["tools"]
    
    async def test_chat_endpoint_mock(self):
        """Test chat endpoint with mocked Gemini"""
        from agents.logic_understanding_agent.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        with patch('agents.logic_understanding_agent.main.model') as mock_model:
            # Mock the model response
            mock_chat = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Test response"
            mock_chat.send_message.return_value = mock_response
            mock_model.start_chat.return_value = mock_chat
            
            response = client.post(
                "/chat",
                params={"message": "Test question"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
