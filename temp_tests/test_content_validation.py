"""
Tests for content block validation.
"""

from app.services.data_service import validate_content_block

def test_valid_text_block():
    """Test validation of valid text block."""
    block = {
        'type': 'text',
        'value': 'Sample text content'
    }
    is_valid, _ = validate_content_block(block)
    assert is_valid

def test_valid_code_block():
    """Test validation of valid code block."""
    block = {
        'type': 'code',
        'value': 'print("Hello, World!")'
    }
    is_valid, _ = validate_content_block(block)
    assert is_valid

def test_valid_image_block():
    """Test validation of valid image block."""
    block = {
        'type': 'image',
        'value': {
            'url': 'https://example.com/image.jpg',
            'caption': 'Test image',
            'alt_text': 'A test image'
        }
    }
    is_valid, _ = validate_content_block(block)
    assert is_valid

def test_valid_table_block():
    """Test validation of valid table block."""
    block = {
        'type': 'table',
        'value': {
            'headers': ['Name', 'Age'],
            'rows': [
                ['John', '25'],
                ['Jane', '30']
            ]
        }
    }
    is_valid, _ = validate_content_block(block)
    assert is_valid

def test_invalid_block_type():
    """Test validation of invalid block type."""
    block = {
        'type': 'invalid',
        'value': 'content'
    }
    is_valid, error = validate_content_block(block)
    assert not is_valid
    assert 'Invalid block type' in error

def test_missing_required_fields():
    """Test validation of block with missing fields."""
    block = {
        'type': 'text'
    }
    is_valid, error = validate_content_block(block)
    assert not is_valid
    assert 'Missing required fields' in error

def test_text_block_too_long():
    """Test validation of text block exceeding length limit."""
    block = {
        'type': 'text',
        'value': 'x' * 200000  # Exceeds max length
    }
    is_valid, error = validate_content_block(block)
    assert not is_valid
    assert 'exceeds maximum length' in error

def test_invalid_image_url():
    """Test validation of image block with invalid URL."""
    block = {
        'type': 'image',
        'value': {
            'url': 'http://example.com/image.jpg',  # Not HTTPS
            'caption': 'Test image',
            'alt_text': 'A test image'
        }
    }
    is_valid, error = validate_content_block(block)
    assert not is_valid
    assert 'Invalid URL scheme' in error

def test_table_too_many_headers():
    """Test validation of table block with too many headers."""
    block = {
        'type': 'table',
        'value': {
            'headers': ['H' + str(i) for i in range(25)],  # More than max headers
            'rows': []
        }
    }
    is_valid, error = validate_content_block(block)
    assert not is_valid
    assert 'Too many headers' in error

def test_table_mismatched_rows():
    """Test validation of table block with mismatched row length."""
    block = {
        'type': 'table',
        'value': {
            'headers': ['Name', 'Age'],
            'rows': [
                ['John', '25'],
                ['Jane']  # Missing age
            ]
        }
    }
    is_valid, error = validate_content_block(block)
    assert not is_valid
    assert 'Row length must match headers' in error 