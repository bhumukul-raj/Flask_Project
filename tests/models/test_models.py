"""
Test module for models.py

This module contains tests for the User model class.
"""

import pytest
from app.models import User
from datetime import datetime, UTC

@pytest.fixture
def sample_user_data():
    """Create sample user data for testing."""
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
    """Create sample admin user data for testing."""
    admin_data = sample_user_data.copy()
    admin_data['role'] = 'admin'
    return admin_data

class TestUser:
    """Test suite for User model."""

    def test_user_creation(self, sample_user_data):
        """Test creating a user from dictionary data."""
        user = User(sample_user_data)
        assert user.id == sample_user_data['id']
        assert user.username == sample_user_data['username']
        assert user.password == sample_user_data['password']
        assert user.role == sample_user_data['role']
        assert user.created_at == sample_user_data['created_at']
        assert user.last_login == sample_user_data['last_login']

    def test_get_id(self, sample_user_data):
        """Test get_id method returns string."""
        user = User(sample_user_data)
        assert isinstance(user.get_id(), str)
        assert user.get_id() == str(sample_user_data['id'])

    def test_is_admin_regular_user(self, sample_user_data):
        """Test is_admin method returns False for regular users."""
        user = User(sample_user_data)
        assert not user.is_admin()

    def test_is_admin_admin_user(self, admin_user_data):
        """Test is_admin method returns True for admin users."""
        admin = User(admin_user_data)
        assert admin.is_admin()

    def test_to_dict(self, sample_user_data):
        """Test converting user object back to dictionary."""
        user = User(sample_user_data)
        user_dict = user.to_dict()
        assert user_dict == sample_user_data

    def test_user_mixin_properties(self, sample_user_data):
        """Test UserMixin properties."""
        user = User(sample_user_data)
        assert user.is_authenticated
        assert user.is_active
        assert not user.is_anonymous 