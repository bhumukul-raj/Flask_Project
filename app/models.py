"""
Models Module

This module contains the data models for the application.
"""

from flask_login import UserMixin

class User(UserMixin):
    """User model class."""
    
    def __init__(self, user_data):
        """Initialize user with data from database."""
        if not user_data or not isinstance(user_data, dict):
            raise ValueError("Invalid user data")
            
        # Required fields
        if 'id' not in user_data or 'username' not in user_data:
            raise ValueError("Missing required user fields")
            
        self.id = user_data['id']
        self.username = user_data['username']
        self.email = user_data.get('email')
        self.password = user_data.get('password')
        self.role = user_data.get('role', 'user')
        self._is_active = user_data.get('is_active', True)
        self.created_at = user_data.get('created_at')
        self.last_login = user_data.get('last_login')
    
    def get_id(self):
        """Return the user ID as a string."""
        return str(self.id)
    
    @property
    def is_authenticated(self):
        """Return True if user is authenticated."""
        return True
    
    @property
    def is_anonymous(self):
        """Return False as anonymous users aren't supported."""
        return False
        
    @property
    def is_active(self):
        """Return whether the user account is active."""
        return self._is_active
        
    @is_active.setter
    def is_active(self, value):
        """Set whether the user account is active."""
        self._is_active = bool(value)

    def is_admin(self):
        """Check if user has admin role."""
        return self.role == 'admin'

    def __repr__(self):
        """Return string representation of the user."""
        return f'<User {self.username}>' 