"""
Test module for admin.py

This module contains tests for the admin routes and functionality.
"""

import pytest
from flask import Flask, session
from flask_login import FlaskLoginClient
from app.admin import admin
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
    app.register_blueprint(admin)
    app.test_client_class = FlaskLoginClient
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def admin_user():
    """Create admin user data."""
    return {
        'id': '123e4567-e89b-12d3-a456-426614174000',
        'username': 'admin',
        'password': 'hashed_password',
        'role': 'admin',
        'created_at': datetime.now(UTC).isoformat(),
        'last_login': None
    }

@pytest.fixture
def regular_user():
    """Create regular user data."""
    return {
        'id': '987fcdeb-a654-3210-9876-543210987654',
        'username': 'user',
        'password': 'hashed_password',
        'role': 'user',
        'created_at': datetime.now(UTC).isoformat(),
        'last_login': None
    }

class TestAdminAccess:
    """Test suite for admin access control."""

    def test_admin_dashboard_access_unauthorized(self, client):
        """Test accessing admin dashboard without authentication."""
        response = client.get('/admin/dashboard')
        assert response.status_code == 302
        assert 'login' in response.location

    def test_admin_dashboard_access_non_admin(self, client, regular_user):
        """Test accessing admin dashboard with non-admin user."""
        with client.session_transaction() as sess:
            sess['user_id'] = regular_user['id']
            sess['role'] = regular_user['role']
        
        response = client.get('/admin/dashboard')
        assert response.status_code == 403

    def test_admin_dashboard_access_admin(self, client, admin_user):
        """Test accessing admin dashboard with admin user."""
        with client.session_transaction() as sess:
            sess['user_id'] = admin_user['id']
            sess['role'] = admin_user['role']
        
        response = client.get('/admin/dashboard')
        assert response.status_code == 200
        assert b'Admin Dashboard' in response.data

class TestUserManagement:
    """Test suite for user management functionality."""

    def test_list_users(self, client, admin_user, mocker):
        """Test listing all users."""
        mocker.patch('app.admin.load_data', return_value={'users': [admin_user]})
        
        with client.session_transaction() as sess:
            sess['user_id'] = admin_user['id']
            sess['role'] = admin_user['role']
        
        response = client.get('/admin/users')
        assert response.status_code == 200
        assert b'admin' in response.data

    def test_view_user(self, client, admin_user, regular_user, mocker):
        """Test viewing specific user details."""
        mocker.patch('app.admin.load_data', return_value={'users': [admin_user, regular_user]})
        
        with client.session_transaction() as sess:
            sess['user_id'] = admin_user['id']
            sess['role'] = admin_user['role']
        
        response = client.get(f'/admin/users/{regular_user["id"]}')
        assert response.status_code == 200
        assert regular_user['username'].encode() in response.data

    def test_delete_user(self, client, admin_user, regular_user, mocker):
        """Test deleting a user."""
        mock_load = mocker.patch('app.admin.load_data', return_value={'users': [admin_user, regular_user]})
        mock_save = mocker.patch('app.admin.save_data', return_value=True)
        
        with client.session_transaction() as sess:
            sess['user_id'] = admin_user['id']
            sess['role'] = admin_user['role']
        
        response = client.post(f'/admin/users/{regular_user["id"]}/delete')
        assert response.status_code == 302
        assert 'users' in response.location
        mock_save.assert_called_once()

class TestSubjectManagement:
    """Test suite for subject management functionality."""

    def test_list_subjects(self, client, admin_user, mocker):
        """Test listing all subjects."""
        test_subjects = [{'id': 'subject1', 'name': 'Test Subject'}]
        mocker.patch('app.admin.load_data', return_value={'subjects': test_subjects})
        
        with client.session_transaction() as sess:
            sess['user_id'] = admin_user['id']
            sess['role'] = admin_user['role']
        
        response = client.get('/admin/subjects')
        assert response.status_code == 200
        assert b'Test Subject' in response.data

    def test_add_subject(self, client, admin_user, mocker):
        """Test adding a new subject."""
        mock_load = mocker.patch('app.admin.load_data', return_value={'subjects': []})
        mock_save = mocker.patch('app.admin.save_data', return_value=True)
        
        with client.session_transaction() as sess:
            sess['user_id'] = admin_user['id']
            sess['role'] = admin_user['role']
        
        response = client.post('/admin/subjects/add', data={
            'name': 'New Subject',
            'description': 'Test description'
        })
        assert response.status_code == 302
        assert 'subjects' in response.location
        mock_save.assert_called_once()

    def test_edit_subject(self, client, admin_user, mocker):
        """Test editing an existing subject."""
        test_subject = {'id': 'subject1', 'name': 'Test Subject'}
        mock_load = mocker.patch('app.admin.load_data', return_value={'subjects': [test_subject]})
        mock_save = mocker.patch('app.admin.save_data', return_value=True)
        
        with client.session_transaction() as sess:
            sess['user_id'] = admin_user['id']
            sess['role'] = admin_user['role']
        
        response = client.post('/admin/subjects/subject1/edit', data={
            'name': 'Updated Subject',
            'description': 'Updated description'
        })
        assert response.status_code == 302
        assert 'subjects' in response.location
        mock_save.assert_called_once()

class TestSessionManagement:
    """Test suite for session management functionality."""

    def test_list_sessions(self, client, admin_user, mocker):
        """Test listing all active sessions."""
        test_sessions = {'user1': ['session1', 'session2']}
        mocker.patch('app.admin.get_all_sessions', return_value=test_sessions)
        
        with client.session_transaction() as sess:
            sess['user_id'] = admin_user['id']
            sess['role'] = admin_user['role']
        
        response = client.get('/admin/sessions')
        assert response.status_code == 200
        assert b'session1' in response.data

    def test_terminate_session(self, client, admin_user, mocker):
        """Test terminating a specific session."""
        mock_terminate = mocker.patch('app.admin.terminate_session', return_value=True)
        
        with client.session_transaction() as sess:
            sess['user_id'] = admin_user['id']
            sess['role'] = admin_user['role']
        
        response = client.post('/admin/sessions/user1/session1/terminate')
        assert response.status_code == 302
        assert 'sessions' in response.location
        mock_terminate.assert_called_once_with('user1', 'session1')

    def test_terminate_all_sessions(self, client, admin_user, mocker):
        """Test terminating all sessions for a user."""
        mock_terminate_all = mocker.patch('app.admin.terminate_all_sessions', return_value=True)
        
        with client.session_transaction() as sess:
            sess['user_id'] = admin_user['id']
            sess['role'] = admin_user['role']
        
        response = client.post('/admin/sessions/user1/terminate-all')
        assert response.status_code == 302
        assert 'sessions' in response.location
        mock_terminate_all.assert_called_once_with('user1') 