"""
Configuration file for pytest.

This file contains global fixtures and configuration for all tests.
"""

import os
import sys
import pytest
from datetime import datetime, UTC
from unittest.mock import MagicMock
from flask import Flask
from flask_login import FlaskLoginClient
from app.models import User

# Add the parent directory to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Test data for users
TEST_USERS = {
    'admin': {
        'id': '123e4567-e89b-12d3-a456-426614174000',
        'username': 'admin',
        'password': 'hashed_password',
        'role': 'admin',
        'created_at': datetime.now(UTC).isoformat(),
        'last_login': None
    },
    'user': {
        'id': '987fcdeb-a654-3210-9876-543210987654',
        'username': 'testuser',
        'password': 'hashed_password',
        'role': 'user',
        'created_at': datetime.now(UTC).isoformat(),
        'last_login': None
    }
}

# Test templates for admin views
ADMIN_TEMPLATES = {
    'base.html': """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{% block title %}Admin Panel{% endblock %}</title>
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('admin.dashboard') }}">Admin Panel</a>
                <div class="navbar-nav">
                    <a class="nav-link" href="{{ url_for('auth.logout') }}">Logout</a>
                </div>
            </div>
        </nav>
        <div class="container mt-4">
            {% block content %}{% endblock %}
        </div>
    </body>
    </html>
    """,
    'admin/admin_panel.html': """
    {% extends 'base.html' %}
    {% block content %}
    <div class="container">
        <h1>Admin Dashboard</h1>
        <div class="row mt-4">
            <div class="col-md-4">
                <a href="{{ url_for('admin.users') }}" class="btn btn-primary btn-block">Manage Users</a>
            </div>
            <div class="col-md-4">
                <a href="{{ url_for('admin.subjects') }}" class="btn btn-primary btn-block">Manage Subjects</a>
            </div>
        </div>
    </div>
    {% endblock %}
    """,
    'admin/manage_users.html': """
    {% extends 'base.html' %}
    {% block content %}
    <div class="container">
        <h1>Manage Users</h1>
        <div class="list-group mt-4">
            {% for user in users %}
            <div class="list-group-item">
                <h5>{{ user.username }}</h5>
                <p>Role: {{ user.role }}</p>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endblock %}
    """,
    'admin/manage_subjects.html': """
    {% extends 'base.html' %}
    {% block content %}
    <div class="container">
        <h1>Manage Subjects</h1>
        <div class="list-group mt-4">
            {% for subject in subjects %}
            <div class="list-group-item">
                <h5>{{ subject.name }}</h5>
                <p>{{ subject.description }}</p>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endblock %}
    """,
    'admin/manage_sections.html': """
    {% extends 'base.html' %}
    {% block content %}
    <div class="container">
        <h1>Manage Sections</h1>
        <div class="list-group mt-4">
            {% for section in sections %}
            <div class="list-group-item">
                <h5>{{ section.name }}</h5>
                <p>{{ section.description }}</p>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endblock %}
    """,
    'admin/manage_topics.html': """
    {% extends 'base.html' %}
    {% block content %}
    <div class="container">
        <h1>Manage Topics</h1>
        <div class="list-group mt-4">
            {% for topic in topics %}
            <div class="list-group-item">
                <h5>{{ topic.name }}</h5>
                <p>{{ topic.description }}</p>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endblock %}
    """
}

@pytest.fixture
def app():
    """Create test Flask application."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.test_client_class = FlaskLoginClient
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def test_user():
    """Create a test user for authentication tests."""
    return TEST_USERS['user']

@pytest.fixture
def mock_load_data():
    """Mock the load_data function."""
    return MagicMock(return_value={
        'users': [],
        'subjects': [],
        'sessions': {}
    })

@pytest.fixture
def mock_save_data():
    """Mock the save_data function."""
    return MagicMock(return_value=True)

@pytest.fixture
def test_data():
    """Create test data for database operations."""
    return {
        'users': [TEST_USERS['user']],
        'subjects': [],
        'sessions': {}
    }