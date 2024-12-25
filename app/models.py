"""
Models Module

This module contains the data models for the application.
"""

from flask_login import UserMixin

class User(UserMixin):
    """User model class."""
    
    def __init__(self, user_data):
        """Initialize user with data from JSON."""
        self.id = user_data.get('id')
        self.username = user_data.get('username')
        self.password = user_data.get('password')
        self.role = user_data.get('role', 'user')
        self.created_at = user_data.get('created_at')
        self.last_login = user_data.get('last_login')
    
    def get_id(self):
        """Return the user ID as a string."""
        return str(self.id)
    
    def is_admin(self):
        """Return True if the user is an admin."""
        return self.role == 'admin'
    
    def to_dict(self):
        """Convert user object to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'role': self.role,
            'created_at': self.created_at,
            'last_login': self.last_login
        } 