"""
Data Service Module

This module provides data access and manipulation functions for the application.
It handles all JSON file operations and data validation.

Functions:
    load_data: Load data from a JSON file
    save_data: Save data to a JSON file
    validate_data: Validate data structure before saving
    validate_content_block: Validate content block structure and content

Note:
    All functions in this module handle file operations safely and include
    proper error handling and logging.
"""

import json
import logging
from pathlib import Path
from urllib.parse import urlparse
import os
from flask import current_app

# Configure logger for data service
logger = logging.getLogger(__name__)

# Valid content block types and their constraints
VALID_BLOCK_TYPES = {
    'text': {'max_length': 100000},  # 100KB
    'code': {'max_length': 50000},   # 50KB
    'image': {
        'allowed_schemes': {'https'},
        'max_url_length': 2048,
        'max_caption_length': 500,
        'max_alt_length': 500
    },
    'table': {
        'max_headers': 20,
        'max_rows': 1000,
        'max_cell_length': 1000
    }
}

def load_data(filename):
    """
    Load data from a JSON file in the data directory.
    
    Args:
        filename (str): Name of the JSON file to load (e.g., 'users.json')
        
    Returns:
        dict: The loaded data if successful, empty dict if file doesn't exist
        
    Raises:
        json.JSONDecodeError: If the file contains invalid JSON
    """
    file_path = os.path.join(current_app.config['DATA_DIR'], filename)
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except json.JSONDecodeError:
        return {}

def save_data(filename, data):
    """
    Save data to a JSON file in the data directory.
    
    Args:
        filename (str): Name of the JSON file to save to (e.g., 'users.json')
        data (dict): The data to save
        
    Returns:
        bool: True if save was successful, False otherwise
        
    Note:
        This function will create the data directory if it doesn't exist.
    """
    file_path = os.path.join(current_app.config['DATA_DIR'], filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        logger.info(f'Successfully saved data to {filename}')
        return True

def validate_data(data, schema):
    """
    Validate data against a predefined schema.
    
    Args:
        data (dict): The data to validate
        schema (dict): The schema to validate against
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    try:
        # Basic type checking
        if not isinstance(data, dict):
            logger.error('Data validation failed: root must be a dictionary')
            return False, 'Invalid data structure'
        
        # Check required fields
        for key, value in schema.items():
            if value.get('required', False) and key not in data:
                logger.error(f'Data validation failed: missing required field {key}')
                return False, f'Missing required field: {key}'
        
        logger.debug('Data validation successful')
        return True, None
    except Exception as e:
        logger.error(f'Error during data validation: {str(e)}')
        return False, 'Validation error occurred'

def validate_content_block(block: dict) -> tuple[bool, str]:
    """
    Validate content block structure and type.
    
    Args:
        block (dict): The content block to validate
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    try:
        if not isinstance(block, dict):
            logger.error('Content block validation failed: not a dictionary')
            return False, "Invalid block structure"
            
        if 'type' not in block or 'value' not in block:
            logger.error('Content block validation failed: missing required fields')
            return False, "Missing required fields"
            
        if block['type'] not in VALID_BLOCK_TYPES:
            logger.error(f'Content block validation failed: invalid type {block.get("type")}')
            return False, f"Invalid block type: {block['type']}"
            
        block_type = block['type']
        constraints = VALID_BLOCK_TYPES[block_type]
        
        if block_type in ['text', 'code']:
            if not isinstance(block['value'], str):
                return False, "Value must be a string"
            if len(block['value'].encode('utf-8')) > constraints['max_length']:
                return False, f"Content exceeds maximum length of {constraints['max_length']} bytes"
                
        elif block_type == 'image':
            if not isinstance(block['value'], dict):
                return False, "Image value must be an object"
            if not all(k in block['value'] for k in ['url', 'caption', 'alt_text']):
                return False, "Missing required image fields"
                
            url = urlparse(block['value']['url'])
            if url.scheme not in constraints['allowed_schemes']:
                return False, "Invalid URL scheme"
            if len(block['value']['url']) > constraints['max_url_length']:
                return False, "URL too long"
            if len(block['value']['caption']) > constraints['max_caption_length']:
                return False, "Caption too long"
            if len(block['value']['alt_text']) > constraints['max_alt_length']:
                return False, "Alt text too long"
                
        elif block_type == 'table':
            if not isinstance(block['value'], dict):
                return False, "Table value must be an object"
            if not all(k in block['value'] for k in ['headers', 'rows']):
                return False, "Missing required table fields"
                
            headers = block['value']['headers']
            rows = block['value']['rows']
            
            if not isinstance(headers, list) or not isinstance(rows, list):
                return False, "Headers and rows must be lists"
            if len(headers) > constraints['max_headers']:
                return False, "Too many headers"
            if len(rows) > constraints['max_rows']:
                return False, "Too many rows"
                
            # Check cell lengths
            for header in headers:
                if len(str(header)) > constraints['max_cell_length']:
                    return False, "Header cell too long"
            for row in rows:
                if not isinstance(row, list):
                    return False, "Row must be a list"
                if len(row) != len(headers):
                    return False, "Row length must match headers"
                for cell in row:
                    if len(str(cell)) > constraints['max_cell_length']:
                        return False, "Row cell too long"
                    
        logger.debug('Content block validation successful')
        return True, None
    except Exception as e:
        logger.error(f'Error during content block validation: {str(e)}')
        return False, 'Validation error occurred'