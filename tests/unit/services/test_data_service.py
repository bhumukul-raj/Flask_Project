"""
Test module for data_service.py

This module contains tests for data loading, saving, and validation functions.
"""

import pytest
import json
from pathlib import Path
from app.services.data_service import (
    load_data, save_data, validate_data, validate_content_block,
    VALID_BLOCK_TYPES
)

@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory for testing."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir

@pytest.fixture
def sample_data():
    """Sample data for testing."""
    return {
        'users': [
            {
                'id': 1,
                'username': 'testuser',
                'email': 'test@example.com'
            }
        ]
    }

@pytest.fixture
def sample_schema():
    """Sample schema for data validation."""
    return {
        'users': {
            'required': True,
            'type': 'list'
        }
    }

class TestDataService:
    """Test suite for data service functions."""

    def test_load_data_success(self, temp_data_dir, sample_data, monkeypatch):
        """Test successful data loading."""
        # Setup
        file_path = temp_data_dir / "test.json"
        with open(file_path, 'w') as f:
            json.dump(sample_data, f)
        
        monkeypatch.setattr('app.services.data_service.Path', lambda x: temp_data_dir)
        
        # Test
        result = load_data("test.json")
        assert result == sample_data
        assert isinstance(result, dict)
        assert 'users' in result

    def test_load_data_file_not_found(self, temp_data_dir, monkeypatch):
        """Test loading non-existent file."""
        monkeypatch.setattr('app.services.data_service.Path', lambda x: temp_data_dir)
        result = load_data("nonexistent.json")
        assert result == {}

    def test_load_data_invalid_json(self, temp_data_dir, monkeypatch):
        """Test loading invalid JSON file."""
        # Setup
        file_path = temp_data_dir / "invalid.json"
        with open(file_path, 'w') as f:
            f.write("invalid json content")
        
        monkeypatch.setattr('app.services.data_service.Path', lambda x: temp_data_dir)
        
        # Test
        with pytest.raises(json.JSONDecodeError):
            load_data("invalid.json")

    def test_save_data_success(self, temp_data_dir, sample_data, monkeypatch):
        """Test successful data saving."""
        monkeypatch.setattr('app.services.data_service.Path', lambda x: temp_data_dir)
        
        # Test
        result = save_data("test.json", sample_data)
        assert result is True
        
        # Verify file was created and contains correct data
        file_path = temp_data_dir / "test.json"
        assert file_path.exists()
        with open(file_path, 'r') as f:
            saved_data = json.load(f)
            assert saved_data == sample_data

    def test_validate_data_success(self, sample_data, sample_schema):
        """Test successful data validation."""
        is_valid, error = validate_data(sample_data, sample_schema)
        assert is_valid is True
        assert error is None

    def test_validate_data_invalid_structure(self, sample_schema):
        """Test validation with invalid data structure."""
        invalid_data = "not a dict"
        is_valid, error = validate_data(invalid_data, sample_schema)
        assert is_valid is False
        assert "Invalid data structure" in error

    def test_validate_data_missing_required(self, sample_schema):
        """Test validation with missing required field."""
        invalid_data = {}
        is_valid, error = validate_data(invalid_data, sample_schema)
        assert is_valid is False
        assert "Missing required field" in error

    @pytest.mark.parametrize("block_type,value,expected_valid", [
        ("text", {"type": "text", "value": "Sample text"}, True),
        ("code", {"type": "code", "value": "print('Hello')"}, True),
        ("image", {
            "type": "image",
            "value": {
                "url": "https://example.com/image.jpg",
                "caption": "Test image",
                "alt_text": "Test alt"
            }
        }, True),
        ("text", {"type": "text", "value": "x" * 100001}, False),  # Too long
        ("image", {
            "type": "image",
            "value": {
                "url": "ftp://example.com/image.jpg",  # Invalid scheme
                "caption": "Test",
                "alt_text": "Test"
            }
        }, False),
    ])
    def test_validate_content_block(self, block_type, value, expected_valid):
        """Test content block validation with various inputs."""
        is_valid, _ = validate_content_block(value)
        assert is_valid is expected_valid

    def test_validate_content_block_invalid_structure(self):
        """Test content block validation with invalid structure."""
        invalid_block = {"type": "text"}  # Missing value
        is_valid, error = validate_content_block(invalid_block)
        assert is_valid is False
        assert "Missing required fields" in error

    def test_validate_content_block_invalid_type(self):
        """Test content block validation with invalid type."""
        invalid_block = {"type": "invalid", "value": "test"}
        is_valid, error = validate_content_block(invalid_block)
        assert is_valid is False
        assert "Invalid block type" in error 