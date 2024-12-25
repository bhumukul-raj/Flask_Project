"""
Test configuration and fixtures.
"""

import os
import pytest
from pathlib import Path
from werkzeug.security import generate_password_hash
from app import create_app
from app.services.data_service import save_data

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create the app with test config
    app = create_app('testing')
    
    # Create test data directory if it doesn't exist
    data_dir = Path(app.config['DATA_DIR'])
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a test user
    test_user = {
        'id': 'test-user-id',
        'username': 'testuser',
        'password': generate_password_hash('Test123!'),
        'role': 'admin'
    }
    
    with app.app_context():
        # Save test user data
        save_data('users.json', {'users': [test_user]})
    
    yield app
    
    # Clean up test data directory after tests
    for file in data_dir.glob('*.json'):
        try:
            file.unlink()
        except:
            pass
    try:
        data_dir.rmdir()
    except:
        pass

@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture
def auth_headers(app, client):
    """Get authentication headers for test requests."""
    # Log in and get the access token
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'Test123!'
    })
    
    if response.status_code == 200:
        token = response.json.get('access_token')
        return {'Authorization': f'Bearer {token}'}
    return {} 