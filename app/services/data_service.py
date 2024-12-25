"""
Data service module for handling file operations.
"""

import json
import os
import shutil
from pathlib import Path
from flask import current_app
from typing import Dict, Any
import threading
import tempfile

# File lock for thread safety
file_lock = threading.Lock()

def get_safe_path(filename: str) -> Path:
    """
    Get a safe file path within the data directory.
    
    Args:
        filename (str): Name of the file
        
    Returns:
        Path: Safe file path
    """
    data_dir = Path(current_app.config['DATA_DIR'])
    safe_path = data_dir / filename
    if not str(safe_path.resolve()).startswith(str(data_dir.resolve())):
        raise ValueError("Invalid file path")
    return safe_path

def load_data(filename: str) -> Dict[str, Any]:
    """
    Load data from a JSON file.
    
    Args:
        filename (str): Name of the file to load
        
    Returns:
        dict: Loaded data or empty dict if file doesn't exist
    """
    try:
        safe_path = get_safe_path(filename)
        if not safe_path.exists():
            return {}
            
        with file_lock:
            with open(safe_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
                
    except json.JSONDecodeError as e:
        current_app.logger.error(f"Error decoding JSON from {filename}: {str(e)}")
        return {}
    except Exception as e:
        current_app.logger.error(f"Error loading data from {filename}: {str(e)}")
        return {}

def save_data(filename: str, data: Dict[str, Any]) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        filename (str): Name of the file to save
        data (dict): Data to save
        
    Returns:
        bool: True if save was successful
    """
    try:
        # Validate data size
        data_size = len(json.dumps(data).encode('utf-8'))
        max_size = 10 * 1024 * 1024  # 10MB limit
        if data_size > max_size:
            raise ValueError(f"Data size exceeds maximum allowed size of {max_size} bytes")
            
        safe_path = get_safe_path(filename)
        
        # Create parent directory if it doesn't exist
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        
        with file_lock:
            # Write to a temporary file in the same directory as the target
            temp_path = safe_path.parent / f".tmp.{filename}"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            # Atomically replace the target file
            shutil.move(str(temp_path), str(safe_path))
            
            # Set file permissions
            os.chmod(safe_path, 0o644)
            
        current_app.logger.info(f"Saving data to: {filename}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Error saving data to {filename}: {str(e)}")
        if 'temp_path' in locals():
            try:
                os.unlink(temp_path)
            except:
                pass
        return False

def validate_content_block(block: Dict[str, Any]) -> bool:
    """
    Validate a content block.
    
    Args:
        block (dict): Content block to validate
        
    Returns:
        bool: True if block is valid
    """
    required_fields = ['id', 'type', 'value']
    if not all(field in block for field in required_fields):
        return False
        
    valid_types = ['text', 'code', 'image', 'video', 'link']
    if block['type'] not in valid_types:
        return False
        
    # Validate value based on type
    if block['type'] == 'text':
        if not isinstance(block['value'], str):
            return False
    elif block['type'] == 'code':
        if not isinstance(block['value'], str):
            return False
    elif block['type'] in ['image', 'video', 'link']:
        if not isinstance(block['value'], str) or not block['value'].startswith(('http://', 'https://')):
            return False
            
    return True