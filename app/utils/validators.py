"""
Validation Utilities

This module provides validation functions for user input and data.
"""

import re
from typing import Tuple

def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username format.
    
    Requirements:
    - 3-32 characters long
    - Contains only letters, numbers, and underscores
    - Starts with a letter
    
    Args:
        username (str): Username to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(username) < 3 or len(username) > 32:
        return False, "Username must be between 3 and 32 characters long"
        
    if not username[0].isalpha():
        return False, "Username must start with a letter"
        
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username):
        return False, "Username can only contain letters, numbers, and underscores"
        
    return True, ""

def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password complexity.
    
    Requirements:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one number
    - Contains at least one special character
    
    Args:
        password (str): Password to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
        
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
        
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
        
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
        
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
        
    return True, ""

def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email address format.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not isinstance(email, str):
        return False, "Email must be a string"
        
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
        
    return True, ""

def sanitize_input(text: str) -> str:
    """
    Sanitize input text to prevent XSS attacks.
    
    Args:
        text (str): Text to sanitize
        
    Returns:
        str: Sanitized text
    """
    if not isinstance(text, str):
        return ""
        
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    
    # Convert special characters to HTML entities
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    
    return text

def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(pattern.match(url))

def sanitize_html(text: str) -> str:
    """
    Remove HTML tags from text.
    
    Args:
        text (str): Text to sanitize
        
    Returns:
        str: Sanitized text
    """
    return re.sub(r'<[^>]*?>', '', text)