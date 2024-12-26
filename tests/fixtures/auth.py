"""
Authentication Fixtures

This module provides fixtures for authentication-related tests.
"""

import pytest
from datetime import datetime, UTC
from app.models import User

@pytest.fixture
def test_user():
    """Create a test user for authentication tests."""
    return {
        'id': '123e4567-e89b-12d3-a456-426614174000',
        'username': 'testuser',
        'password': 'hashed_password',
        'role': 'user',
        'created_at': datetime.now(UTC).isoformat(),
        'last_login': None
    }

@pytest.fixture
def admin_user():
    """Create an admin user for authentication tests."""
    return {
        'id': '987fcdeb-a654-3210-9876-543210987654',
        'username': 'admin',
        'password': 'hashed_password',
        'role': 'admin',
        'created_at': datetime.now(UTC).isoformat(),
        'last_login': None
    }

@pytest.fixture
def mock_auth_token():
    """Create a mock authentication token."""
    return 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test_token' 