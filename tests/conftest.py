"""
Configuration file for pytest.

This file contains global fixtures and configuration for all tests.
"""

import os
import sys
import pytest
from flask import Flask
from flask_login import FlaskLoginClient

# Add the parent directory to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

# Import fixtures from the fixtures package
pytest_plugins = [
    'tests.fixtures.auth',
    'tests.fixtures.data'
]