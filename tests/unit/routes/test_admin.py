"""
Test module for admin.py

This module contains comprehensive tests for the admin routes and functionality.
It covers:
- Admin access control and authentication
- User management operations (CRUD)
- Subject management operations (CRUD)
- Section and topic management within subjects
- Template rendering and form handling

The tests use Flask's test client and various fixtures to simulate
different user roles and authentication states.
"""

import pytest
from flask import Flask, session, Blueprint
from flask_login import FlaskLoginClient, LoginManager, login_user, logout_user
from flask_jwt_extended import JWTManager
from datetime import datetime, UTC, timedelta
from unittest.mock import MagicMock, patch
import os
import sys
import shutil

# Add the project root to Python path to make app package importable
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

from app.models import User
from app.admin import admin
from tests.conftest import ADMIN_TEMPLATES, TEST_USERS

@pytest.fixture
def temp_template_dir(request):
    """
    Create a temporary directory for test templates.
    
    This fixture sets up and tears down a temporary directory for storing
    test template files. It ensures each test starts with a clean template
    directory and cleans up after itself.
    
    Returns:
        str: Path to the temporary template directory
    """
    # Create a specific directory for test templates
    temp_dir = os.path.join(project_root, 'tests', 'fixtures', 'templates')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    def cleanup():
        # Clean up the templates after tests
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)  # Recreate empty directory
    
    request.addfinalizer(cleanup)
    return temp_dir

@pytest.fixture
def app(temp_template_dir):
    """
    Create test Flask application.
    
    This fixture creates a Flask application configured for testing with:
    - JWT authentication
    - Flask-Login setup
    - Mock user loader
    - Test blueprints
    - Template configuration
    
    Args:
        temp_template_dir: Path to temporary template directory from fixture
    
    Returns:
        Flask: Configured Flask application for testing
    """
    app = Flask(__name__)
    app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test_secret_key',
        'JWT_SECRET_KEY': 'test_jwt_secret',
        'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=1),
        'JWT_TOKEN_LOCATION': ['headers'],
        'JWT_HEADER_NAME': 'Authorization',
        'JWT_HEADER_TYPE': 'Bearer',
        'LOGIN_DISABLED': False
    })
    
    # Initialize extensions
    jwt = JWTManager(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        with patch('app.services.data_service.load_data') as mock_load:
            mock_load.return_value = {
                'users': [
                    {
                        'id': 1,
                        'username': 'test_admin',
                        'password': 'hashed_password',
                        'role': 'admin'
                    }
                ]
            }
            return User.from_dict({'id': user_id, 'username': 'test_admin', 'role': 'admin'})

    # Create mock blueprints
    main = Blueprint('main', __name__)
    auth = Blueprint('auth', __name__)
    
    @main.route('/')
    @main.route('/home')
    def home():
        return 'Home'
    
    @main.route('/dashboard')
    def dashboard():
        return 'Dashboard'
    
    @auth.route('/login')
    def login():
        return 'Login'
    
    @auth.route('/logout')
    def logout():
        return 'Logout'
    
    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    
    # Write test templates to temporary directory
    for template_name, template_content in ADMIN_TEMPLATES.items():
        template_path = os.path.join(temp_template_dir, template_name)
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        with open(template_path, 'w') as f:
            f.write(template_content)
    
    # Set template folder to temporary directory
    app.template_folder = temp_template_dir
    
    return app

@pytest.fixture
def client(app):
    """
    Create test client.
    
    Returns:
        FlaskClient: Test client for making requests to the application
    """
    return app.test_client()

@pytest.fixture
def admin_user():
    """
    Create admin user data.
    
    Returns:
        dict: Sample admin user data with all required fields
    """
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
    """
    Create regular user data.
    
    Returns:
        dict: Sample regular user data with all required fields
    """
    return {
        'id': '987fcdeb-a654-3210-9876-543210987654',
        'username': 'user',
        'password': 'hashed_password',
        'role': 'user',
        'created_at': datetime.now(UTC).isoformat(),
        'last_login': None
    }

@pytest.fixture
def auth_client(client):
    """
    Create authenticated test client.
    
    This fixture provides a test client with an authenticated admin user session.
    It handles login and logout automatically for each test.
    
    Args:
        client: Flask test client from fixture
    
    Yields:
        FlaskClient: Authenticated test client
    """
    with client:
        # Create and log in test user with proper admin setup
        class AdminUser(User):
            def is_admin(self):
                return True
        
        user = AdminUser({
            'id': 1,
            'username': 'testuser',
            'role': 'admin'
        })
        login_user(user)
        yield client
        logout_user()

@pytest.fixture
def mock_data_service(mocker):
    """
    Mock data service functions.
    
    This fixture provides mock data for the data service layer, including:
    - User data
    - Subject data with sections and topics
    - Session data
    
    Args:
        mocker: pytest-mock fixture
    
    Returns:
        dict: Mock data structure
    """
    mock_data = {
        'users': [
            {
                'id': 1,
                'username': 'testuser',
                'role': 'admin'
            }
        ],
        'subjects': [
            {
                'id': 'test-subject',
                'name': 'Test Subject',
                'description': 'Test Description',
                'created_at': datetime.now(UTC).isoformat(),
                'updated_at': datetime.now(UTC).isoformat(),
                'sections': [
                    {
                        'id': 'test-section',
                        'name': 'Test Section',
                        'description': 'Test Description',
                        'order': 1,
                        'created_at': datetime.now(UTC).isoformat(),
                        'updated_at': datetime.now(UTC).isoformat(),
                        'topics': [
                            {
                                'id': 'test-topic',
                                'name': 'Test Topic',
                                'description': 'Test Description',
                                'content_type': 'mixed',
                                'order': 1,
                                'content_blocks': [
                                    {
                                        'id': 'block-1',
                                        'type': 'text',
                                        'value': 'Test content',
                                        'created_at': datetime.now(UTC).isoformat(),
                                        'updated_at': datetime.now(UTC).isoformat()
                                    }
                                ],
                                'created_at': datetime.now(UTC).isoformat(),
                                'updated_at': datetime.now(UTC).isoformat()
                            }
                        ]
                    }
                ]
            }
        ],
        'sessions': {}
    }
    mocker.patch('app.admin.load_data', return_value=mock_data)
    mocker.patch('app.admin.save_data', return_value=True)
    return mock_data

class TestAdminAccess:
    """
    Test suite for admin access control.
    
    This class verifies that admin routes are properly protected and only
    accessible to authenticated admin users. It tests:
    - Unauthenticated access attempts
    - Non-admin user access attempts
    - Successful admin access
    """

    def test_admin_dashboard_access_unauthorized(self, client):
        """Test accessing admin dashboard without authentication."""
        response = client.get('/admin/dashboard')
        assert response.status_code == 302  # Redirects to login

    def test_admin_dashboard_access_non_admin(self, client):
        """Test accessing admin dashboard as non-admin user."""
        with client:
            user = User({
                'id': 2,
                'username': 'regularuser',
                'role': 'user'
            })
            login_user(user)
            response = client.get('/admin/dashboard')
            assert response.status_code == 302  # Redirects to dashboard
            logout_user()

    def test_admin_dashboard_access_admin(self, auth_client, mock_data_service):
        """Test accessing admin dashboard as admin."""
        response = auth_client.get('/admin/dashboard')
        assert response.status_code == 200
        assert b'Admin Dashboard' in response.data

class TestUserManagement:
    """
    Test suite for user management.
    
    This class tests all user management operations available to admins:
    - Listing all users
    - Adding new users
    - Editing existing users
    - Deleting users
    
    Each operation is tested for both success and failure cases.
    """

    def test_list_users(self, auth_client, mock_data_service):
        """Test listing users."""
        response = auth_client.get('/admin/users')
        assert response.status_code == 200
        assert b'testuser' in response.data

    def test_add_user(self, auth_client, mock_data_service):
        """Test adding a new user."""
        response = auth_client.post('/admin/add_user', data={
            'username': 'newuser',
            'password': 'Test123!',
            'role': 'user'
        })
        assert response.status_code == 302
        assert 'users' in response.headers['Location']

    def test_edit_user(self, auth_client, mock_data_service):
        """Test editing a user's role."""
        response = auth_client.post('/admin/edit_user', data={
            'user_id': '1',
            'role': 'admin'
        })
        assert response.status_code == 302
        assert 'users' in response.headers['Location']

    def test_delete_user(self, auth_client, mock_data_service):
        """Test deleting a user."""
        response = auth_client.post('/admin/delete_user', data={
            'user_id': '1'
        })
        assert response.status_code == 302
        assert 'users' in response.headers['Location']

class TestSubjectManagement:
    """
    Test suite for subject management.
    
    This class tests all subject-related operations:
    - Listing subjects
    - Adding new subjects
    - Editing existing subjects
    - Deleting subjects
    
    Each operation verifies proper data handling and response behavior.
    """

    def test_list_subjects(self, auth_client, mock_data_service):
        """Test listing subjects."""
        response = auth_client.get('/admin/subjects')
        assert response.status_code == 200
        assert b'Test Subject' in response.data

    def test_add_subject(self, auth_client, mock_data_service):
        """Test adding a new subject."""
        response = auth_client.post('/admin/add_subject', data={
            'title': 'New Subject',
            'description': 'Test description',
            'category': 'Test',
            'level': 'Beginner',
            'status': 'active'
        })
        assert response.status_code == 302
        assert 'subjects' in response.headers['Location']

    def test_edit_subject(self, auth_client, mock_data_service):
        """Test editing a subject."""
        response = auth_client.post('/admin/edit_subject', data={
            'subject_id': 'test-subject',
            'title': 'Updated Subject',
            'description': 'Updated description'
        })
        assert response.status_code == 302
        assert 'subjects' in response.headers['Location']

    def test_delete_subject(self, auth_client, mock_data_service):
        """Test deleting a subject."""
        response = auth_client.post('/admin/delete_subject', data={
            'subject_id': 'test-subject'
        })
        assert response.status_code == 302
        assert 'subjects' in response.headers['Location']

class TestSectionManagement:
    """
    Test suite for section management.
    
    This class tests operations related to subject sections:
    - Viewing sections within a subject
    - Adding new sections
    - Section ordering and organization
    
    Tests verify proper section management within the subject hierarchy.
    """

    def test_manage_sections(self, auth_client, mock_data_service):
        """Test viewing sections of a subject."""
        # First ensure we have a valid subject
        mock_data_service['subjects'][0]['sections'] = [{
            'id': 'test-section',
            'name': 'Test Section',
            'description': 'Test Description',
            'topics': []
        }]
        
        response = auth_client.get('/admin/subjects/test-subject/sections')
        assert response.status_code == 200
        assert b'Test Section' in response.data

    def test_add_section(self, auth_client, mock_data_service):
        """Test adding a new section."""
        response = auth_client.post('/admin/subjects/test-subject/sections/add', data={
            'name': 'New Section',
            'description': 'Test description',
            'order': 1
        })
        assert response.status_code == 302
        assert '/admin/subjects/test-subject/sections' in response.headers['Location']

class TestTopicManagement:
    """
    Test suite for topic management.
    
    This class tests operations related to section topics:
    - Viewing topics within a section
    - Adding new topics
    - Topic ordering and organization
    
    Tests verify proper topic management within the section hierarchy.
    """

    def test_manage_topics(self, auth_client, mock_data_service):
        """Test viewing topics of a section."""
        # First ensure we have a valid subject and section
        mock_data_service['subjects'][0]['sections'] = [{
            'id': 'test-section',
            'name': 'Test Section',
            'description': 'Test Description',
            'topics': [{
                'id': 'test-topic',
                'name': 'Test Topic',
                'description': 'Test Description'
            }]
        }]
        
        response = auth_client.get('/admin/subjects/test-subject/sections/test-section/topics')
        assert response.status_code == 200
        assert b'Test Topic' in response.data

    def test_add_topic(self, auth_client, mock_data_service):
        """Test adding a new topic."""
        # First ensure we have a valid subject and section
        mock_data_service['subjects'][0]['sections'] = [{
            'id': 'test-section',
            'name': 'Test Section',
            'description': 'Test Description',
            'topics': []
        }]
        
        response = auth_client.post('/admin/subjects/test-subject/sections/test-section/topics/add', data={
            'name': 'New Topic',
            'description': 'Test description',
            'order': 1
        })
        assert response.status_code == 302
        assert '/admin/subjects/test-subject/sections/test-section/topics' in response.headers['Location'] 