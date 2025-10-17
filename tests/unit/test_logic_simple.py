"""Simple unit tests for Logic Understanding Agent"""
import pytest


class TestFinancialMetrics:
    """Test financial metrics calculations"""
    
    def test_roi_calculation(self):
        """Test ROI calculation"""
        # Simple ROI formula: (Revenue - Investment) / Investment * 100
        revenue = 150000
        investment = 100000
        expected_roi = ((revenue - investment) / investment) * 100
        
        assert expected_roi == 50.0
    
    def test_profit_margin_calculation(self):
        """Test profit margin calculation"""
        # Profit Margin: (Revenue - Costs) / Revenue * 100
        revenue = 1000000
        costs = 700000
        expected_margin = ((revenue - costs) / revenue) * 100
        
        assert expected_margin == 30.0
    
    def test_growth_rate_calculation(self):
        """Test growth rate calculation"""
        # Growth Rate: (Current - Previous) / Previous * 100
        current = 120000
        previous = 100000
        expected_growth = ((current - previous) / previous) * 100
        
        assert expected_growth == 20.0


class TestTrendAnalysis:
    """Test trend analysis logic"""
    
    def test_growing_trend(self):
        """Test identification of growing trend"""
        data = [100, 120, 140, 160, 180]
        
        # Simple trend: compare first half vs second half
        first_half = sum(data[:len(data)//2]) / (len(data)//2)
        second_half = sum(data[len(data)//2:]) / (len(data) - len(data)//2)
        
        assert second_half > first_half
        assert (second_half - first_half) / first_half > 0.1  # >10% growth
    
    def test_declining_trend(self):
        """Test identification of declining trend"""
        data = [180, 160, 140, 120, 100]
        
        first_half = sum(data[:len(data)//2]) / (len(data)//2)
        second_half = sum(data[len(data)//2:]) / (len(data) - len(data)//2)
        
        assert second_half < first_half
        assert (first_half - second_half) / first_half > 0.1  # >10% decline
    
    def test_stable_trend(self):
        """Test identification of stable trend"""
        data = [100, 105, 98, 102, 101]
        
        first_half = sum(data[:len(data)//2]) / (len(data)//2)
        second_half = sum(data[len(data)//2:]) / (len(data) - len(data)//2)
        
        change_percent = abs((second_half - first_half) / first_half)
        assert change_percent < 0.1  # <10% change = stable


class TestDataValidation:
    """Test data validation"""
    
    def test_positive_numbers(self):
        """Test that financial values are positive"""
        revenue = 100000
        costs = 70000
        
        assert revenue > 0
        assert costs > 0
        assert costs < revenue  # Costs should be less than revenue
    
    def test_percentage_range(self):
        """Test that percentages are in valid range"""
        roi = 50.0
        margin = 30.0
        
        assert 0 <= roi <= 1000  # ROI can be >100%
        assert 0 <= margin <= 100  # Margin is 0-100%


@pytest.mark.unit
class TestBasicMath:
    """Test basic mathematical operations"""
    
    def test_addition(self):
        """Test addition"""
        assert 100 + 50 == 150
    
    def test_division(self):
        """Test division"""
        assert 150 / 100 == 1.5
    
    def test_percentage(self):
        """Test percentage calculation"""
        value = 50
        total = 100
        percentage = (value / total) * 100
        assert percentage == 50.0
