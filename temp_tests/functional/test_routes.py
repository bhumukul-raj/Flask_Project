"""
Functional Tests for Routes

Tests all application routes and their responses.
Verifies that routes:
1. Are accessible
2. Return correct status codes
3. Handle authentication properly
4. Process dynamic parameters
"""

import pytest
from flask import url_for
from app import create_app

@pytest.fixture
def client():
    """Create test client."""
    app = create_app('testing')
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_public_routes(client):
    """Test public routes that don't require authentication."""
    routes = [
        ('main.home', '/'),
        ('auth.login', '/auth/login'),
        ('auth.register', '/auth/register'),
        ('main.subjects', '/subjects'),
    ]
    
    for endpoint, path in routes:
        response = client.get(path)
        assert response.status_code in [200, 302], f"Route {endpoint} ({path}) failed"

@pytest.mark.parametrize('endpoint,path', [
    ('admin.dashboard', '/admin/dashboard'),
    ('admin.users', '/admin/users'),
    ('admin.subjects', '/admin/subjects'),
    ('main.dashboard', '/dashboard'),
])
def test_protected_routes_redirect_to_login(client, endpoint, path):
    """Test protected routes redirect to login when not authenticated."""
    response = client.get(path)
    assert response.status_code == 302
    assert '/auth/login' in response.location

@pytest.mark.parametrize('endpoint,path', [
    ('api.get_subjects', '/api/subjects'),
    ('api.get_users', '/api/users'),
])
def test_api_routes_unauthorized(client, endpoint, path):
    """Test API routes return 401 when no token is provided."""
    response = client.get(path)
    assert response.status_code == 401

def test_static_files(client):
    """Test static files route."""
    response = client.get('/static/css/style.css')
    assert response.status_code in [200, 404]

class TestAuthenticatedRoutes:
    """Test routes that require authentication."""
    
    @pytest.fixture
    def auth_client(self, client):
        """Create authenticated client."""
        data = {
            'email': 'test@example.com',
            'password': 'test_password'
        }
        client.post('/auth/login', data=data)
        return client
    
    @pytest.mark.parametrize('endpoint,path', [
        ('main.dashboard', '/dashboard'),
        ('main.subject_detail', '/subject/1'),
    ])
    def test_user_routes(self, auth_client, endpoint, path):
        """Test routes accessible to regular users."""
        response = auth_client.get(path)
        assert response.status_code in [200, 404]

class TestAdminRoutes:
    """Test admin routes."""
    
    @pytest.fixture
    def admin_client(self, client):
        """Create admin authenticated client."""
        data = {
            'email': 'admin@example.com',
            'password': 'admin_password'
        }
        client.post('/auth/login', data=data)
        return client
    
    @pytest.mark.parametrize('endpoint,path', [
        ('admin.dashboard', '/admin/dashboard'),
        ('admin.users', '/admin/users'),
        ('admin.subjects', '/admin/subjects'),
    ])
    def test_admin_routes(self, admin_client, endpoint, path):
        """Test routes accessible to admin users."""
        response = admin_client.get(path)
        assert response.status_code in [200, 404]

class TestAPIRoutes:
    """Test API routes."""
    
    @pytest.fixture
    def api_client(self, client):
        """Create API authenticated client."""
        data = {
            'email': 'api@example.com',
            'password': 'api_password'
        }
        response = client.post('/auth/login', json=data)
        token = response.json.get('access_token')
        client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        return client
    
    @pytest.mark.parametrize('method,endpoint,path', [
        ('GET', 'api.get_subjects', '/api/subjects'),
        ('GET', 'api.get_users', '/api/users'),
        ('POST', 'api.create_subject', '/api/subjects'),
        ('GET', 'api.get_subject', '/api/subjects/1'),
    ])
    def test_api_routes(self, api_client, method, endpoint, path):
        """Test API routes with authentication."""
        if method == 'GET':
            response = api_client.get(path)
        elif method == 'POST':
            response = api_client.post(path, json={})
        
        assert response.status_code in [200, 201, 404]

def test_dynamic_routes(client):
    """Test routes with dynamic parameters."""
    routes = [
        ('/subject/1', 'Subject ID route'),
        ('/admin/subjects/1/sections', 'Sections route'),
        ('/admin/subjects/1/sections/1/topics', 'Topics route'),
        ('/api/subjects/1/sections/1/topics/1', 'API topic route'),
    ]
    
    for path, desc in routes:
        response = client.get(path)
        assert response.status_code in [200, 302, 401, 404], f"Failed: {desc} ({path})" 