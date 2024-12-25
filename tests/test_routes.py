"""
Test routes module.
"""

import pytest
from werkzeug.security import generate_password_hash
from app.services.data_service import save_data

class TestAuthRoutes:
    """Test authentication routes."""
    
    def test_register(self, client):
        """Test user registration."""
        response = client.post('/auth/register', json={
            'username': 'newuser',
            'password': 'Test123!'
        })
        assert response.status_code == 201
        assert 'user_id' in response.json
        
    def test_register_missing_data(self, client):
        """Test registration with missing data."""
        response = client.post('/auth/register', json={})
        assert response.status_code == 400
        
    def test_login(self, app, client):
        """Test user login."""
        with app.app_context():
            # Create test user
            test_user = {
                'id': 'test-user-id',
                'username': 'testuser',
                'password': generate_password_hash('Test123!'),
                'role': 'admin'
            }
            save_data('users.json', {'users': [test_user]})
            
            # Try to log in
            response = client.post('/auth/login', json={
                'username': 'testuser',
                'password': 'Test123!'
            })
            assert response.status_code == 200
            assert 'access_token' in response.json
        
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post('/auth/login', json={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401
        
    def test_logout(self, client, auth_headers):
        """Test user logout."""
        if not auth_headers:
            pytest.skip("No auth token available")
        response = client.post('/auth/logout', headers=auth_headers)
        assert response.status_code == 200
        
class TestAPIRoutes:
    """Test API routes."""
    
    def test_get_users_with_auth(self, client, auth_headers):
        """Test getting users list with authentication."""
        if not auth_headers:
            pytest.skip("No auth token available")
        response = client.get('/api/users', headers=auth_headers)
        assert response.status_code == 200
        assert 'users' in response.json
        
    def test_get_users_without_auth(self, client):
        """Test getting users list without authentication."""
        response = client.get('/api/users')
        assert response.status_code == 401
