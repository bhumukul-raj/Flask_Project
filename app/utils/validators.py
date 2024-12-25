"""
Validators Module

This module provides validation functions for various data types used in the application.
It includes validators for:
- Usernames
- Passwords
- Email addresses
- Content types
- File names

Each validator returns a tuple of (is_valid, error_message) to provide
detailed feedback about validation failures.
"""

import re
import logging

# Configure logger for validators
logger = logging.getLogger(__name__)

def validate_username(username):
    """
    Validate a username against security requirements.
    
    Requirements:
    - Length between 3 and 20 characters
    - Only alphanumeric characters and underscores
    - Must start with a letter
    - Case insensitive (stored and compared in lowercase)
    
    Args:
        username (str): The username to validate
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    try:
        # Check if username is a string
        if not isinstance(username, str):
            logger.warning('Username validation failed: not a string')
            return False, 'Username must be a string'
            
        # Check length
        if len(username) < 3 or len(username) > 20:
            logger.warning(f'Username validation failed: invalid length ({len(username)})')
            return False, 'Username must be between 3 and 20 characters'
            
        # Check characters using regex
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username):
            logger.warning('Username validation failed: invalid characters')
            return False, 'Username must start with a letter and contain only letters, numbers, and underscores'
            
        logger.debug(f'Username validation successful: {username}')
        return True, None
        
    except Exception as e:
        logger.error(f'Error during username validation: {str(e)}')
        return False, 'Validation error occurred'

def validate_password(password):
    """
    Validate a password against security requirements.
    
    Requirements:
    - Minimum length of 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    
    Args:
        password (str): The password to validate
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    try:
        # Check if password is a string
        if not isinstance(password, str):
            logger.warning('Password validation failed: not a string')
            return False, 'Password must be a string'
            
        # Check length
        if len(password) < 8:
            logger.warning('Password validation failed: too short')
            return False, 'Password must be at least 8 characters long'
            
        # Check for required character types
        if not re.search(r'[A-Z]', password):
            logger.warning('Password validation failed: missing uppercase')
            return False, 'Password must contain at least one uppercase letter'
            
        if not re.search(r'[a-z]', password):
            logger.warning('Password validation failed: missing lowercase')
            return False, 'Password must contain at least one lowercase letter'
            
        if not re.search(r'\d', password):
            logger.warning('Password validation failed: missing number')
            return False, 'Password must contain at least one number'
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            logger.warning('Password validation failed: missing special character')
            return False, 'Password must contain at least one special character'
            
        logger.debug('Password validation successful')
        return True, None
        
    except Exception as e:
        logger.error(f'Error during password validation: {str(e)}')
        return False, 'Validation error occurred'

def validate_email(email):
    """
    Validate an email address.
    
    Requirements:
    - Must match standard email format
    - Must not exceed 254 characters (RFC 5321)
    - Local part must not exceed 64 characters
    - Domain part must be valid
    
    Args:
        email (str): The email address to validate
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    try:
        # Check if email is a string
        if not isinstance(email, str):
            logger.warning('Email validation failed: not a string')
            return False, 'Email must be a string'
            
        # Check length
        if len(email) > 254:
            logger.warning('Email validation failed: too long')
            return False, 'Email address is too long'
            
        # Validate format using regex
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            logger.warning('Email validation failed: invalid format')
            return False, 'Invalid email format'
            
        # Split email into local and domain parts
        local, domain = email.split('@')
        
        # Check local part length
        if len(local) > 64:
            logger.warning('Email validation failed: local part too long')
            return False, 'Email local part is too long'
            
        logger.debug(f'Email validation successful: {email}')
        return True, None
        
    except Exception as e:
        logger.error(f'Error during email validation: {str(e)}')
        return False, 'Validation error occurred'

def validate_content_type(content_type):
    """
    Validate content type for learning materials.
    
    Valid content types:
    - text: Plain text content
    - video: Video content (URL)
    - quiz: Interactive quiz
    - assignment: Assignment submission
    
    Args:
        content_type (str): The content type to validate
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    try:
        valid_types = ['text', 'video', 'quiz', 'assignment']
        
        if not isinstance(content_type, str):
            logger.warning('Content type validation failed: not a string')
            return False, 'Content type must be a string'
            
        if content_type not in valid_types:
            logger.warning(f'Content type validation failed: invalid type ({content_type})')
            return False, f'Content type must be one of: {", ".join(valid_types)}'
            
        logger.debug(f'Content type validation successful: {content_type}')
        return True, None
        
    except Exception as e:
        logger.error(f'Error during content type validation: {str(e)}')
        return False, 'Validation error occurred'