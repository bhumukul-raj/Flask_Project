"""
Authentication Service Module

This module handles user authentication and user creation operations.
"""

import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from flask_jwt_extended import create_access_token
from .data_service import load_data, save_data
from ..utils.validators import validate_username, validate_password

def generate_token(user_id: int, username: str) -> str:
    """
    Generate a JWT token for a user.
    
    Args:
        user_id (int): The user's ID
        username (str): The username
        
    Returns:
        str: The generated JWT token
    """
    return create_access_token(identity=user_id)

def authenticate_user(username: str, password: str) -> dict:
    """
    Authenticate a user with username and password.
    
    Args:
        username (str): The username to authenticate
        password (str): The password to verify
    
    Returns:
        dict: User data if authentication successful, None otherwise
    """
    try:
        users_data = load_data('data/users.json')
        users = users_data.get('users', [])
        
        user = next((u for u in users if u.get('username') == username), None)
        if user and check_password_hash(user.get('password', ''), password):
            token = generate_token(user.get('id'), username)
            return {
                'id': user.get('id'),
                'username': username,
                'token': token
            }
    except Exception as e:
        current_app.logger.error(f"Authentication error: {str(e)}")
    return None

def create_user(username: str, password: str) -> bool:
    """
    Create a new user with the given username and password.
    
    Args:
        username (str): The username for the new user
        password (str): The password for the new user
    
    Returns:
        bool: True if user creation successful, False if username already exists
    """
    try:
        # Validate username and password
        username_valid, username_error = validate_username(username)
        password_valid, password_error = validate_password(password)
        
        if not username_valid or not password_valid:
            current_app.logger.warning(f"Validation failed - Username: {username_error}, Password: {password_error}")
            return False

        users_data = load_data('data/users.json')
        users = users_data.get('users', [])
        
        if any(u.get('username') == username for u in users):
            return False
        
        user_id = len(users) + 1
        new_user = {
            'id': user_id,
            'username': username,
            'password': generate_password_hash(password)
        }
        
        users.append(new_user)
        save_data('data/users.json', {'users': users})
        
        return True
    except Exception as e:
        current_app.logger.error(f"User creation error: {str(e)}")
        return False