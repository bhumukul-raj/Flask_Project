"""
Tests for content block validation functionality.

This module provides comprehensive tests for validating different types of content blocks:
- Text blocks: Plain text content with length limits
- Code blocks: Programming code snippets
- Image blocks: Image data with URL validation
- Table blocks: Structured data with header and row validation

Required Implementation:
    The tests in this module require the implementation of validate_content_block function
    in app/services/data_service.py with the following signature:
    
    def validate_content_block(block: dict) -> Tuple[bool, Optional[str]]:
        '''
        Validate a content block's structure and data.
        
        Args:
            block: Dictionary containing the content block data with 'type' and 'value' keys
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
            - is_valid: True if validation passes, False otherwise
            - error_message: None if valid, error description if invalid
        '''
        pass

Validation Rules:
    1. Text Blocks:
       - Maximum length: 200,000 characters
       - Must be string type
       
    2. Code Blocks:
       - Must be string type
       - No specific length limit
       
    3. Image Blocks:
       - Must have URL (HTTPS only)
       - Must have caption
       - Must have alt_text
       
    4. Table Blocks:
       - Must have headers (max 20)
       - Must have rows
       - Row length must match header length
"""

from app.services.data_service import validate_content_block

def test_valid_text_block():
    """
    Test validation of a valid text block.
    
    A valid text block should:
    1. Have 'text' type
    2. Have string value
    3. Not exceed length limit
    """
    block = {
        'type': 'text',
        'value': 'Sample text content'
    }
    is_valid, _ = validate_content_block(block)
    assert is_valid

def test_valid_code_block():
    """
    Test validation of a valid code block.
    
    A valid code block should:
    1. Have 'code' type
    2. Have string value containing code
    """
    block = {
        'type': 'code',
        'value': 'print("Hello, World!")'
    }
    is_valid, _ = validate_content_block(block)
    assert is_valid

def test_valid_image_block():
    """
    Test validation of a valid image block.
    
    A valid image block should have:
    1. HTTPS URL
    2. Non-empty caption
    3. Non-empty alt_text
    """
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
    """
    Test validation of a valid table block.
    
    A valid table block should have:
    1. Headers array (1-20 headers)
    2. Rows array
    3. Each row length matching headers length
    """
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
    """
    Test validation of block with invalid type.
    
    Should fail validation when:
    1. Type is not one of: text, code, image, table
    2. Error message should indicate invalid type
    """
    block = {
        'type': 'invalid',
        'value': 'content'
    }
    is_valid, error = validate_content_block(block)
    assert not is_valid
    assert 'Invalid block type' in error

def test_missing_required_fields():
    """
    Test validation of block with missing required fields.
    
    Should fail validation when:
    1. 'type' key is missing
    2. 'value' key is missing
    3. Error message should indicate missing fields
    """
    block = {
        'type': 'text'
        # Missing 'value' field
    }
    is_valid, error = validate_content_block(block)
    assert not is_valid
    assert 'Missing required fields' in error

def test_text_block_too_long():
    """
    Test validation of oversized text block.
    
    Should fail validation when:
    1. Text length exceeds 200,000 characters
    2. Error message should indicate length issue
    """
    block = {
        'type': 'text',
        'value': 'x' * 200000  # Exceeds max length
    }
    is_valid, error = validate_content_block(block)
    assert not is_valid
    assert 'exceeds maximum length' in error

def test_invalid_image_url():
    """
    Test validation of image block with invalid URL.
    
    Should fail validation when:
    1. URL scheme is not HTTPS
    2. Error message should indicate URL scheme issue
    """
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
    """
    Test validation of table block with excessive headers.
    
    Should fail validation when:
    1. Number of headers exceeds 20
    2. Error message should indicate header limit issue
    """
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
    """
    Test validation of table block with inconsistent row length.
    
    Should fail validation when:
    1. Any row length doesn't match header count
    2. Error message should indicate row length mismatch
    """
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