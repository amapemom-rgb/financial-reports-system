"""Unit tests for Report Reader Agent"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
import io


@pytest.fixture
def sample_dataframe():
    """Sample DataFrame for testing"""
    return pd.DataFrame({
        "Date": ["2024-01", "2024-02", "2024-03"],
        "Revenue": [100000, 150000, 180000],
        "Costs": [70000, 90000, 110000]
    })


class TestDataCleaning:
    """Test data cleaning functions"""
    
    def test_clean_dataframe_remove_empty_rows(self, sample_dataframe):
        """Test removing empty rows"""
        from agents.report_reader_agent.main import clean_dataframe, DataCleaningOptions
        
        # Add empty row
        df_with_empty = sample_dataframe.copy()
        df_with_empty.loc[3] = [None, None, None]
        
        options = DataCleaningOptions(remove_empty_rows=True)
        cleaned_df, warnings = clean_dataframe(df_with_empty, options)
        
        assert len(cleaned_df) == 3
        assert len(warnings) > 0
    
    def test_clean_dataframe_fill_missing(self, sample_dataframe):
        """Test filling missing values"""
        from agents.report_reader_agent.main import clean_dataframe, DataCleaningOptions
        
        df_with_missing = sample_dataframe.copy()
        df_with_missing.loc[1, "Revenue"] = None
        
        options = DataCleaningOptions(fill_missing_values=True)
        cleaned_df, warnings = clean_dataframe(df_with_missing, options)
        
        assert cleaned_df["Revenue"].isna().sum() == 0
    
    def test_clean_dataframe_convert_types(self):
        """Test type conversion"""
        from agents.report_reader_agent.main import clean_dataframe, DataCleaningOptions
        
        df = pd.DataFrame({
            "Numbers": ["100", "200", "300"],
            "Text": ["A", "B", "C"]
        })
        
        options = DataCleaningOptions(convert_types=True)
        cleaned_df, warnings = clean_dataframe(df, options)
        
        assert pd.api.types.is_numeric_dtype(cleaned_df["Numbers"])


class TestMetadataExtraction:
    """Test metadata extraction"""
    
    def test_extract_metadata(self, sample_dataframe):
        """Test metadata extraction from DataFrame"""
        from agents.report_reader_agent.main import extract_metadata
        
        metadata = extract_metadata(sample_dataframe)
        
        assert metadata["rows"] == 3
        assert metadata["columns"] == 3
        assert len(metadata["column_names"]) == 3
        assert "Revenue" in metadata["numeric_columns"]
        assert "Date" in metadata["text_columns"]


class TestDataframeConversion:
    """Test DataFrame to JSON conversion"""
    
    def test_dataframe_to_json(self, sample_dataframe):
        """Test converting DataFrame to JSON"""
        from agents.report_reader_agent.main import dataframe_to_json
        
        result = dataframe_to_json(sample_dataframe)
        
        assert "columns" in result
        assert "data" in result
        assert "summary" in result
        assert len(result["data"]) == 3
        assert result["summary"]["total_rows"] == 3


class TestExcelReader:
    """Test Excel file reading"""
    
    def test_read_excel_file_mock(self):
        """Test Excel reading with mock"""
        from agents.report_reader_agent.main import read_excel_file
        
        with patch('pandas.read_excel') as mock_read:
            mock_read.return_value = pd.DataFrame({"A": [1, 2, 3]})
            
            df = read_excel_file("test.xlsx")
            
            assert len(df) == 3
            assert "A" in df.columns


class TestAPI:
    """Test API endpoints"""
    
    def test_health_endpoint(self):
        """Test health check"""
        from agents.report_reader_agent.main import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["agent"] == "report-reader"
        assert "capabilities" in data
    
    def test_upload_excel_mock(self):
        """Test Excel upload endpoint"""
        from agents.report_reader_agent.main import app
        
        client = TestClient(app)
        
        # Create mock Excel file
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        
        with patch('agents.report_reader_agent.main.clean_dataframe') as mock_clean:
            mock_clean.return_value = (df, [])
            
            response = client.post(
                "/upload/excel",
                files={"file": ("test.xlsx", excel_buffer, "application/vnd.ms-excel")}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "data" in data
            assert "metadata" in data
    
    def test_read_sheets_mock(self):
        """Test Google Sheets reading"""
        from agents.report_reader_agent.main import app
        
        client = TestClient(app)
        
        with patch('agents.report_reader_agent.main.read_google_sheets') as mock_read:
            mock_df = pd.DataFrame({"Col1": [1, 2], "Col2": [3, 4]})
            mock_read.return_value = mock_df
            
            response = client.post(
                "/read/sheets",
                json={
                    "spreadsheet_id": "test-sheet-123",
                    "range": "A1:Z100"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
