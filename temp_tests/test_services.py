"""
Tests for data service functionality.
"""

import json
import os
import pytest
from pathlib import Path
from datetime import datetime, UTC
from app.services.data_service import load_data, save_data, validate_content_block

def test_load_data(app):
    """Test loading data from a JSON file."""
    with app.app_context():
        # Create test file in the test data directory
        test_data = {"test": "data"}
        test_file = 'test.json'
        
        # Save test data
        success = save_data(test_file, test_data)
        assert success
        
        # Load and verify data
        loaded_data = load_data(test_file)
        assert loaded_data == test_data

def test_save_data(app):
    """Test saving data to a JSON file."""
    with app.app_context():
        test_file = 'test.json'
        test_data = {"test": "data"}
        
        # Save data
        success = save_data(test_file, test_data)
        assert success
        
        # Verify file exists and contains correct data
        data_dir = Path(app.config['DATA_DIR'])
        file_path = data_dir / test_file
        assert file_path.exists()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
            assert loaded_data == test_data

def test_load_subject_database(app):
    """Test loading and validating subject database."""
    with app.app_context():
        # Create test subject data
        test_subject = {
            "id": "test-subject",
            "name": "Test Subject",
            "description": "Test description",
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
            "sections": []
        }
        
        # Save test data
        success = save_data('subject_database.json', {"subjects": [test_subject]})
        assert success
        
        # Load and verify data
        loaded_data = load_data('subject_database.json')
        assert 'subjects' in loaded_data
        assert len(loaded_data['subjects']) == 1
        assert loaded_data['subjects'][0]['id'] == test_subject['id']

def test_save_subject_database(app):
    """Test saving and loading complex subject data."""
    with app.app_context():
        # Create test subject with sections and topics
        test_subject = {
            "id": "test-subject",
            "name": "Python",
            "description": "Python programming language",
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
            "sections": [
                {
                    "id": "test-section",
                    "name": "Basics",
                    "description": "Basic concepts",
                    "order": 1,
                    "created_at": datetime.now(UTC).isoformat(),
                    "updated_at": datetime.now(UTC).isoformat(),
                    "topics": [
                        {
                            "id": "test-topic",
                            "name": "Introduction",
                            "description": "Introduction to Python",
                            "order": 1,
                            "created_at": datetime.now(UTC).isoformat(),
                            "updated_at": datetime.now(UTC).isoformat(),
                            "content_blocks": [
                                {
                                    "id": "test-block",
                                    "type": "text",
                                    "value": "Test content",
                                    "order": 1,
                                    "created_at": datetime.now(UTC).isoformat(),
                                    "updated_at": datetime.now(UTC).isoformat()
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        # Save test data
        success = save_data('subject_database.json', {"subjects": [test_subject]})
        assert success
        
        # Load and verify data structure
        loaded_data = load_data('subject_database.json')
        assert 'subjects' in loaded_data
        assert len(loaded_data['subjects']) == 1
        
        loaded_subject = loaded_data['subjects'][0]
        assert loaded_subject['id'] == test_subject['id']
        assert len(loaded_subject['sections']) == 1
        
        loaded_section = loaded_subject['sections'][0]
        assert loaded_section['id'] == test_subject['sections'][0]['id']
        assert len(loaded_section['topics']) == 1
        
        loaded_topic = loaded_section['topics'][0]
        assert loaded_topic['id'] == test_subject['sections'][0]['topics'][0]['id']
        assert len(loaded_topic['content_blocks']) == 1
        
        loaded_block = loaded_topic['content_blocks'][0]
        assert loaded_block['id'] == test_subject['sections'][0]['topics'][0]['content_blocks'][0]['id']

def test_validate_content_block():
    """Test content block validation."""
    # Valid text block
    valid_text = {
        "id": "test-text",
        "type": "text",
        "value": "Test content"
    }
    assert validate_content_block(valid_text)
    
    # Valid code block
    valid_code = {
        "id": "test-code",
        "type": "code",
        "value": "print('Hello')"
    }
    assert validate_content_block(valid_code)
    
    # Valid image block
    valid_image = {
        "id": "test-image",
        "type": "image",
        "value": "https://example.com/image.jpg"
    }
    assert validate_content_block(valid_image)
    
    # Invalid type
    invalid_type = {
        "id": "test-invalid",
        "type": "invalid",
        "value": "Test"
    }
    assert not validate_content_block(invalid_type)
    
    # Missing required field
    missing_field = {
        "id": "test-missing",
        "type": "text"
    }
    assert not validate_content_block(missing_field)
    
    # Invalid URL for image
    invalid_url = {
        "id": "test-invalid-url",
        "type": "image",
        "value": "not-a-url"
    }
    assert not validate_content_block(invalid_url)

def test_load_nonexistent_file(app):
    """Test loading a non-existent file."""
    with app.app_context():
        data = load_data('nonexistent.json')
        assert data == {}
