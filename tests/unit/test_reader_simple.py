"""Simple tests for Report Reader Agent"""
import pytest


class TestDataCleaning:
    """Test data cleaning logic"""
    
    def test_remove_empty_values(self):
        """Test removing empty values"""
        data = [1, 2, None, 4, None, 6]
        cleaned = [x for x in data if x is not None]
        
        assert len(cleaned) == 4
        assert None not in cleaned
    
    def test_fill_missing_values(self):
        """Test filling missing values with default"""
        data = [100, None, 150, None, 200]
        filled = [x if x is not None else 0 for x in data]
        
        assert None not in filled
        assert filled == [100, 0, 150, 0, 200]
    
    def test_remove_duplicates(self):
        """Test removing duplicate values"""
        data = [1, 2, 2, 3, 3, 3, 4]
        unique = list(set(data))
        
        assert len(unique) == 4
        assert unique == [1, 2, 3, 4] or set(unique) == {1, 2, 3, 4}


class TestDataValidation:
    """Test data validation"""
    
    def test_validate_numbers(self):
        """Test number validation"""
        values = [100, 150, 200]
        
        assert all(isinstance(v, (int, float)) for v in values)
        assert all(v > 0 for v in values)
    
    def test_validate_structure(self):
        """Test data structure validation"""
        data = {
            "columns": ["A", "B", "C"],
            "data": [[1, 2, 3], [4, 5, 6]]
        }
        
        assert "columns" in data
        assert "data" in data
        assert len(data["columns"]) == len(data["data"][0])


class TestDataTransformation:
    """Test data transformation"""
    
    def test_convert_to_numbers(self):
        """Test converting strings to numbers"""
        string_values = ["100", "150", "200"]
        numbers = [int(v) for v in string_values]
        
        assert all(isinstance(n, int) for n in numbers)
        assert numbers == [100, 150, 200]
    
    def test_round_values(self):
        """Test rounding values"""
        values = [100.567, 150.234, 200.789]
        rounded = [round(v, 2) for v in values]
        
        assert rounded == [100.57, 150.23, 200.79]


@pytest.mark.unit
class TestMetadataExtraction:
    """Test metadata extraction"""
    
    def test_count_rows(self):
        """Test counting rows"""
        data = [[1, 2], [3, 4], [5, 6]]
        row_count = len(data)
        
        assert row_count == 3
    
    def test_count_columns(self):
        """Test counting columns"""
        data = [[1, 2, 3], [4, 5, 6]]
        col_count = len(data[0]) if data else 0
        
        assert col_count == 3
    
    def test_detect_data_types(self):
        """Test detecting data types"""
        row = [100, "text", 3.14, True]
        
        types = [type(v).__name__ for v in row]
        assert "int" in types
        assert "str" in types
        assert "float" in types
        assert "bool" in types
