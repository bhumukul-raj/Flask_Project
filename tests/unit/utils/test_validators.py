"""
Test module for validators.py

This module contains tests for various validation functions.
"""

import pytest
from app.utils.validators import (
    validate_username, validate_password,
    validate_email, validate_content_type
)

class TestValidators:
    """Test suite for validation functions."""

    @pytest.mark.parametrize("username,expected_valid", [
        ("validuser", True),
        ("user123", True),
        ("valid_user_123", True),
        ("a" * 20, True),  # Max length
        ("ab", False),  # Too short
        ("a" * 21, False),  # Too long
        ("123user", False),  # Starts with number
        ("user@name", False),  # Invalid character
        ("user space", False),  # Contains space
        ("", False),  # Empty string
        (None, False),  # None
        (123, False),  # Wrong type
    ])
    def test_username_validation(self, username, expected_valid):
        """Test username validation with various inputs."""
        is_valid, _ = validate_username(username)
        assert is_valid is expected_valid

    @pytest.mark.parametrize("password,expected_valid", [
        ("Password123!", True),
        ("Abcd123!@#", True),
        ("Pass123$%^", True),
        ("Sh0rt!", False),  # Changed to be clearly too short (6 chars)
        ("password123", False),  # No uppercase
        ("PASSWORD123", False),  # No lowercase
        ("Passwordabc", False),  # No number
        ("Password123", False),  # No special char
        ("", False),  # Empty string
        (None, False),  # None
        (123, False),  # Wrong type
    ])
    def test_password_validation(self, password, expected_valid):
        """Test password validation with various inputs."""
        is_valid, _ = validate_password(password)
        assert is_valid is expected_valid

    @pytest.mark.parametrize("email,expected_valid", [
        ("test@example.com", True),
        ("user.name@domain.co.uk", True),
        ("user+tag@example.com", True),
        ("", False),  # Empty string
        ("invalid.email", False),  # No @
        ("@domain.com", False),  # No local part
        ("user@", False),  # No domain
        ("user@domain", False),  # No TLD
        ("a" * 65 + "@domain.com", False),  # Local part too long
        ("user@" + "a" * 255 + ".com", False),  # Total length too long
        (None, False),  # None
        (123, False),  # Wrong type
    ])
    def test_email_validation(self, email, expected_valid):
        """Test email validation with various inputs."""
        is_valid, _ = validate_email(email)
        assert is_valid is expected_valid

    @pytest.mark.parametrize("content_type,expected_valid", [
        ("text", True),
        ("video", True),
        ("quiz", True),
        ("assignment", True),
        ("invalid_type", False),
        ("", False),
        (None, False),
        (123, False),
    ])
    def test_content_type_validation(self, content_type, expected_valid):
        """Test content type validation with various inputs."""
        is_valid, _ = validate_content_type(content_type)
        assert is_valid is expected_valid

    def test_username_error_messages(self):
        """Test specific error messages for username validation."""
        # Too short
        is_valid, error = validate_username("ab")
        assert not is_valid
        assert "between 3 and 20 characters" in error

        # Invalid characters
        is_valid, error = validate_username("user@name")
        assert not is_valid
        assert "only letters, numbers, and underscores" in error

        # Wrong type
        is_valid, error = validate_username(123)
        assert not is_valid
        assert "must be a string" in error

    def test_password_error_messages(self):
        """Test specific error messages for password validation."""
        # Too short
        is_valid, error = validate_password("Short1!")
        assert not is_valid
        assert "at least 8 characters" in error

        # Missing uppercase
        is_valid, error = validate_password("password123!")
        assert not is_valid
        assert "uppercase letter" in error

        # Missing number
        is_valid, error = validate_password("Password!")
        assert not is_valid
        assert "one number" in error

    def test_email_error_messages(self):
        """Test specific error messages for email validation."""
        # Invalid format
        is_valid, error = validate_email("invalid.email")
        assert not is_valid
        assert "Invalid email format" in error

        # Too long
        is_valid, error = validate_email("a" * 255 + "@example.com")
        assert not is_valid
        assert "too long" in error

    def test_content_type_error_messages(self):
        """Test specific error messages for content type validation."""
        # Invalid type
        is_valid, error = validate_content_type("invalid_type")
        assert not is_valid
        assert "must be one of" in error

        # Wrong type
        is_valid, error = validate_content_type(123)
        assert not is_valid
        assert "must be a string" in error 