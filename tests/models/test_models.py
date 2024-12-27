"""
Test module for models.py

This module contains unit tests for the User model class. It verifies:
- User object creation and attribute assignment
- User authentication and authorization functionality
- Data conversion and serialization methods
- Flask-Login UserMixin integration

The tests use pytest fixtures to provide sample user data for both regular and admin users.
"""

import pytest
from app.models import User
from datetime import datetime, UTC

@pytest.fixture
def sample_user_data():
    """
    Create sample user data for testing.
    
    Returns:
        dict: A dictionary containing test user data with the following fields:
            - id: UUID string
            - username: Test username
            - password: Hashed password string
            - role: User role (default: 'user')
            - created_at: ISO format timestamp
            - last_login: None by default
    """
    return {
        'id': '123e4567-e89b-12d3-a456-426614174000',
        'username': 'testuser',
        'password': 'hashed_password',
        'role': 'user',
        'created_at': datetime.now(UTC).isoformat(),
        'last_login': None
    }

@pytest.fixture
def admin_user_data(sample_user_data):
    """
    Create sample admin user data for testing.
    
    Args:
        sample_user_data (dict): Base user data from sample_user_data fixture
    
    Returns:
        dict: A copy of sample_user_data with role set to 'admin'
    """
    admin_data = sample_user_data.copy()
    admin_data['role'] = 'admin'
    return admin_data

class TestUser:
    """
    Test suite for User model.
    
    This class contains tests that verify the User model's functionality,
    including object creation, authentication, authorization, and data conversion.
    Each test method focuses on a specific aspect of the User model.
    """

    def test_user_creation(self, sample_user_data):
        """
        Test creating a user from dictionary data.
        
        Verifies that all attributes are correctly assigned when creating
        a new User instance from a dictionary.
        """
        user = User(sample_user_data)
        assert user.id == sample_user_data['id']
        assert user.username == sample_user_data['username']
        assert user.password == sample_user_data['password']
        assert user.role == sample_user_data['role']
        assert user.created_at == sample_user_data['created_at']
        assert user.last_login == sample_user_data['last_login']

    def test_get_id(self, sample_user_data):
        """
        Test get_id method returns string.
        
        Verifies that the get_id method returns the user's ID as a string,
        which is required by Flask-Login's UserMixin interface.
        """
        user = User(sample_user_data)
        assert isinstance(user.get_id(), str)
        assert user.get_id() == str(sample_user_data['id'])

    def test_is_admin_regular_user(self, sample_user_data):
        """
        Test is_admin method returns False for regular users.
        
        Verifies that users with the 'user' role are not identified as administrators.
        This is crucial for proper access control throughout the application.
        """
        user = User(sample_user_data)
        assert not user.is_admin()

    def test_is_admin_admin_user(self, admin_user_data):
        """
        Test is_admin method returns True for admin users.
        
        Verifies that users with the 'admin' role are correctly identified
        as administrators, ensuring they can access admin-only functionality.
        """
        admin = User(admin_user_data)
        assert admin.is_admin()

    def test_to_dict(self, sample_user_data):
        """
        Test converting user object back to dictionary.
        
        Verifies that the to_dict method correctly serializes all User attributes
        back to a dictionary format, which is essential for data persistence
        and API responses.
        """
        user = User(sample_user_data)
        user_dict = user.to_dict()
        assert user_dict == sample_user_data

    def test_user_mixin_properties(self, sample_user_data):
        """
        Test UserMixin properties.
        
        Verifies that the Flask-Login UserMixin properties are correctly implemented:
        - is_authenticated: Should always be True for valid users
        - is_active: Should be True for valid users
        - is_anonymous: Should always be False for valid users
        """
        user = User(sample_user_data)
        assert user.is_authenticated
        assert user.is_active
        assert not user.is_anonymous 