"""
Test module for hash_utils.py

This module contains tests for password hashing and verification functions.
"""

import pytest
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.hash_utils import generate_password_hash, check_password_hash

class TestHashUtils:
    """Test suite for hash utilities."""

    def test_password_hash_generation(self):
        """Test that password hashing generates different hashes for same password."""
        password = "test_password123"
        hash1 = generate_password_hash(password)
        hash2 = generate_password_hash(password)
        
        assert hash1 != hash2  # Should generate different hashes
        assert hash1 != password  # Hash should be different from original password
        assert 'scrypt:' in hash1  # Should use scrypt algorithm

    def test_password_verification(self):
        """Test that password verification works correctly."""
        password = "test_password123"
        password_hash = generate_password_hash(password)
        
        assert check_password_hash(password_hash, password) is True
        assert check_password_hash(password_hash, "wrong_password") is False

    def test_hash_with_special_characters(self):
        """Test hashing passwords with special characters."""
        password = "test@#$%^&*()_+"
        password_hash = generate_password_hash(password)
        
        assert check_password_hash(password_hash, password) is True

    def test_hash_with_unicode_characters(self):
        """Test hashing passwords with unicode characters."""
        password = "测试密码123"
        password_hash = generate_password_hash(password)
        
        assert check_password_hash(password_hash, password) is True

    def test_empty_password(self):
        """Test hashing empty password."""
        password = ""
        password_hash = generate_password_hash(password)
        
        assert check_password_hash(password_hash, password) is True
        assert check_password_hash(password_hash, "not_empty") is False

    @pytest.mark.parametrize("invalid_input", [
        None,
        123,
        ["password"],
        {"password": "test"}
    ])
    def test_invalid_password_types(self, invalid_input):
        """Test that invalid password types raise TypeError."""
        with pytest.raises((TypeError, AttributeError)):
            generate_password_hash(invalid_input) 