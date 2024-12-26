"""
Authentication Service Test Module

This module contains test cases for the authentication service functionality.
It tests user authentication, user creation, and token generation operations.

The tests use pytest fixtures for dependency injection and mocking.
Each test case runs in an isolated Flask application context to ensure
proper handling of Flask's application-specific functionality.

Test Coverage:
- User Authentication (success, wrong password, nonexistent user)
- User Creation (success, duplicate username, invalid credentials)
- Token Generation

Dependencies:
- pytest: Testing framework
- Flask: Web framework
- Werkzeug: Password hashing
- unittest.mock: Mocking functionality
"""

import pytest
from werkzeug.security import generate_password_hash
from app.services.auth_service import authenticate_user, create_user, generate_token
from unittest.mock import patch, MagicMock
from flask import Flask

@pytest.fixture
def app():
    """Create and configure a new app instance for each test.
    
    Returns:
        Flask: A Flask application instance configured for testing.
    """
    app = Flask(__name__)
    app.config.update({
        'TESTING': True,
    })
    return app

@pytest.fixture
def mock_users_data():
    """Create mock user data for testing.
    
    This fixture provides a consistent set of test user data,
    including a pre-configured user with hashed password.
    
    Returns:
        dict: Mock user data structure.
    """
    return {
        'users': [
            {
                'id': 1,
                'username': 'testuser',
                'password': generate_password_hash('password123')
            }
        ]
    }

@pytest.fixture
def mock_load_data(mock_users_data):
    """Mock the load_data function from data_service.
    
    Args:
        mock_users_data: The mock user data fixture.
    
    Yields:
        MagicMock: A mock object that returns the mock user data.
    """
    with patch('app.services.auth_service.load_data') as mock:
        mock.return_value = mock_users_data
        yield mock

@pytest.fixture
def mock_save_data():
    """Mock the save_data function from data_service.
    
    Yields:
        MagicMock: A mock object for verifying save operations.
    """
    with patch('app.services.auth_service.save_data') as mock:
        yield mock

class TestAuthService:
    """Test suite for the Authentication Service.
    
    This class contains all test cases for the authentication service,
    organized by functionality being tested.
    """

    def test_authenticate_user_success(self, app, mock_load_data):
        """Test successful user authentication.
        
        Verifies that a user can successfully authenticate with correct credentials
        and receives a valid token.
        
        Args:
            app: Flask application fixture
            mock_load_data: Mock data loader fixture
        """
        with app.app_context():
            with patch('app.services.auth_service.generate_token') as mock_token:
                mock_token.return_value = 'dummy_token'
                result = authenticate_user('testuser', 'password123')
                
                assert result is not None
                assert result['username'] == 'testuser'
                assert result['id'] == 1
                assert result['token'] == 'dummy_token'

    def test_authenticate_user_wrong_password(self, app, mock_load_data):
        """Test authentication failure with incorrect password.
        
        Verifies that authentication fails when the password is incorrect.
        
        Args:
            app: Flask application fixture
            mock_load_data: Mock data loader fixture
        """
        with app.app_context():
            result = authenticate_user('testuser', 'wrongpassword')
            assert result is None

    def test_authenticate_user_nonexistent(self, app, mock_load_data):
        """Test authentication with non-existent user.
        
        Verifies that authentication fails for a username that doesn't exist.
        
        Args:
            app: Flask application fixture
            mock_load_data: Mock data loader fixture
        """
        with app.app_context():
            result = authenticate_user('nonexistent', 'password123')
            assert result is None

    def test_create_user_success(self, app, mock_load_data, mock_save_data):
        """Test successful user creation.
        
        Verifies that a new user can be created with valid credentials.
        
        Args:
            app: Flask application fixture
            mock_load_data: Mock data loader fixture
            mock_save_data: Mock data saver fixture
        """
        with app.app_context():
            result = create_user('newuser', 'Password123!')
            assert result is True
            mock_save_data.assert_called_once()

    def test_create_user_existing_username(self, app, mock_load_data, mock_save_data):
        """Test user creation with existing username.
        
        Verifies that user creation fails when the username already exists.
        
        Args:
            app: Flask application fixture
            mock_load_data: Mock data loader fixture
            mock_save_data: Mock data saver fixture
        """
        with app.app_context():
            result = create_user('testuser', 'Password123!')
            assert result is False
            mock_save_data.assert_not_called()

    def test_create_user_invalid_username(self, app, mock_load_data, mock_save_data):
        """Test user creation with invalid username.
        
        Verifies that user creation fails when the username is invalid
        (e.g., too short, invalid characters).
        
        Args:
            app: Flask application fixture
            mock_load_data: Mock data loader fixture
            mock_save_data: Mock data saver fixture
        """
        with app.app_context():
            with patch('app.services.auth_service.validate_username') as mock_validate:
                mock_validate.return_value = (False, 'Username must be between 3 and 20 characters')
                result = create_user('u', 'Password123!')  # Too short username
                assert result is False
                mock_save_data.assert_not_called()

    def test_create_user_invalid_password(self, app, mock_load_data, mock_save_data):
        """Test user creation with invalid password.
        
        Verifies that user creation fails when the password is invalid
        (e.g., too short, missing required characters).
        
        Args:
            app: Flask application fixture
            mock_load_data: Mock data loader fixture
            mock_save_data: Mock data saver fixture
        """
        with app.app_context():
            with patch('app.services.auth_service.validate_password') as mock_validate:
                mock_validate.return_value = (False, 'Password must be at least 8 characters long')
                result = create_user('newuser', 'weak')  # Too weak password
                assert result is False
                mock_save_data.assert_not_called()

    @patch('app.services.auth_service.create_access_token')
    def test_generate_token(self, mock_create_token, app):
        """Test JWT token generation.
        
        Verifies that a valid JWT token is generated for a user.
        
        Args:
            mock_create_token: Mock for the JWT token creation
            app: Flask application fixture
        """
        with app.app_context():
            mock_create_token.return_value = 'dummy_token'
            token = generate_token(1, 'testuser')
            assert token == 'dummy_token'
            mock_create_token.assert_called_once_with(identity=1) 