"""
Test module for routes.py

This module contains tests for the application routes.
"""

import pytest
from flask import Flask, session
from flask_login import FlaskLoginClient
from app.routes import auth, main
from app.models import User
from datetime import datetime, UTC
import json

@pytest.fixture
def app():
    """Create test Flask application."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.test_client_class = FlaskLoginClient
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def test_user():
    """Create test user data."""
    return {
        'id': '123e4567-e89b-12d3-a456-426614174000',
        'username': 'testuser',
        'password': 'hashed_password',
        'role': 'user',
        'created_at': datetime.now(UTC).isoformat(),
        'last_login': None
    }

class TestAuthRoutes:
    """Test suite for authentication routes."""

    def test_register_get(self, client):
        """Test GET request to register page."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data

    def test_register_post_success(self, client, mocker):
        """Test successful user registration."""
        mocker.patch('app.routes.load_data', return_value={'users': []})
        mocker.patch('app.routes.save_data', return_value=True)
        mocker.patch('app.routes.validate_username', return_value=(True, None))
        mocker.patch('app.routes.validate_password', return_value=(True, None))

        response = client.post('/auth/register', data={
            'username': 'newuser',
            'password': 'Password123!'
        })
        assert response.status_code == 302
        assert 'login' in response.location

    def test_login_get(self, client):
        """Test GET request to login page."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data

    def test_login_post_success(self, client, test_user, mocker):
        """Test successful login."""
        mocker.patch('app.routes.load_data', return_value={'users': [test_user]})
        mocker.patch('app.routes.check_password_hash', return_value=True)
        mocker.patch('app.routes.save_data', return_value=True)

        response = client.post('/auth/login', data={
            'username': test_user['username'],
            'password': 'password123',
            'remember': 'true'
        })
        assert response.status_code == 302
        assert 'dashboard' in response.location

    def test_logout(self, client, test_user):
        """Test user logout."""
        with client.session_transaction() as sess:
            sess['user_id'] = test_user['id']
        
        response = client.get('/auth/logout')
        assert response.status_code == 302
        assert 'home' in response.location

class TestMainRoutes:
    """Test suite for main routes."""

    def test_home_page(self, client):
        """Test home page access."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Home' in response.data

    def test_subjects_page_unauthorized(self, client):
        """Test subjects page access without authentication."""
        response = client.get('/subjects')
        assert response.status_code == 302
        assert 'login' in response.location

    def test_subjects_page_authorized(self, client, test_user, mocker):
        """Test subjects page access with authentication."""
        with client.session_transaction() as sess:
            sess['user_id'] = test_user['id']
        
        mocker.patch('app.routes.load_data', return_value={'subjects': []})
        response = client.get('/subjects')
        assert response.status_code == 200
        assert b'Subjects' in response.data

    def test_dashboard_unauthorized(self, client):
        """Test dashboard access without authentication."""
        response = client.get('/dashboard')
        assert response.status_code == 302
        assert 'login' in response.location

    def test_dashboard_authorized(self, client, test_user):
        """Test dashboard access with authentication."""
        with client.session_transaction() as sess:
            sess['user_id'] = test_user['id']
        
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'Dashboard' in response.data

class TestRateLimiting:
    """Test suite for rate limiting functionality."""

    def test_rate_limit_login(self, client):
        """Test rate limiting on login endpoint."""
        # Make multiple requests to trigger rate limit
        for _ in range(25):  # More than MAX_ATTEMPTS
            response = client.post('/auth/login', data={
                'username': 'test',
                'password': 'test'
            })
        
        # Next request should be rate limited
        response = client.post('/auth/login', data={
            'username': 'test',
            'password': 'test'
        })
        assert response.status_code == 429
        assert b'Too many attempts' in response.data

    def test_rate_limit_register(self, client):
        """Test rate limiting on register endpoint."""
        # Make multiple requests to trigger rate limit
        for _ in range(25):  # More than MAX_ATTEMPTS
            response = client.post('/auth/register', data={
                'username': 'test',
                'password': 'test'
            })
        
        # Next request should be rate limited
        response = client.post('/auth/register', data={
            'username': 'test',
            'password': 'test'
        })
        assert response.status_code == 429
        assert b'Too many attempts' in response.data 