"""
Integration tests for error handlers.

This module tests the error handling functionality across the application,
including both HTML and JSON responses.
"""

import pytest
from flask import Flask, jsonify, request, render_template, json
from werkzeug.exceptions import (
    BadRequest, Unauthorized, Forbidden, NotFound,
    MethodNotAllowed, TooManyRequests, InternalServerError
)
import os
import sys

# Add the project root to Python path to make app package importable
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from app.error_handlers import register_error_handlers

@pytest.fixture
def app():
    """Create test Flask application with error handlers."""
    app = Flask(__name__)
    app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test_secret_key'
    })
    
    # Add template folder
    template_dir = os.path.join(project_root, 'app', 'templates')
    error_template_dir = os.path.join(template_dir, 'errors')
    os.makedirs(error_template_dir, exist_ok=True)
    
    # Create error template
    with open(os.path.join(error_template_dir, 'error.html'), 'w') as f:
        f.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error {{ code }}</title>
        </head>
        <body>
            <h1>Error {{ code }}</h1>
            <p>{{ message }}</p>
        </body>
        </html>
        """)
    
    app.template_folder = template_dir
    
    # Register error handlers
    register_error_handlers(app)
    
    # Test routes that raise errors
    @app.route('/bad-request')
    def bad_request():
        raise BadRequest('Bad request error')

    @app.route('/unauthorized')
    def unauthorized():
        raise Unauthorized('Unauthorized error')

    @app.route('/forbidden')
    def forbidden():
        raise Forbidden('Forbidden error')

    @app.route('/not-found')
    def not_found():
        raise NotFound('Not found error')

    @app.route('/method-not-allowed', methods=['GET'])
    def method_not_allowed():
        return 'GET only'

    @app.route('/too-many-requests')
    def too_many_requests():
        raise TooManyRequests('Too many requests error')

    @app.route('/internal-server-error')
    def internal_server_error():
        raise InternalServerError('Internal server error')

    @app.route('/custom-error')
    def custom_error():
        return render_template('errors/error.html', code=400, message='Custom error message')

    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

class TestHTMLErrorResponses:
    """Test HTML responses for various error codes."""

    def test_400_bad_request(self, client):
        """Test bad request error (400) HTML response."""
        response = client.get('/bad-request')
        assert response.status_code == 400
        assert b'Error 400' in response.data
        assert b'Bad request error' in response.data

    def test_401_unauthorized(self, client):
        """Test unauthorized error (401) HTML response."""
        response = client.get('/unauthorized')
        assert response.status_code == 401
        assert b'Error 401' in response.data
        assert b'Unauthorized error' in response.data

    def test_403_forbidden(self, client):
        """Test forbidden error (403) HTML response."""
        response = client.get('/forbidden')
        assert response.status_code == 403
        assert b'Error 403' in response.data
        assert b'Forbidden error' in response.data

    def test_404_not_found(self, client):
        """Test not found error (404) HTML response."""
        response = client.get('/not-found')
        assert response.status_code == 404
        assert b'Error 404' in response.data
        assert b'Not found error' in response.data

    def test_405_method_not_allowed(self, client):
        """Test method not allowed error (405) HTML response."""
        response = client.post('/method-not-allowed')
        assert response.status_code == 405
        assert b'Error 405' in response.data
        assert b'The method is not allowed for the requested URL.' in response.data

    def test_429_too_many_requests(self, client):
        """Test too many requests error (429) HTML response."""
        response = client.get('/too-many-requests')
        assert response.status_code == 429
        assert b'Error 429' in response.data
        assert b'Too many requests error' in response.data

    def test_500_internal_server_error(self, client):
        """Test internal server error (500) HTML response."""
        response = client.get('/internal-server-error')
        assert response.status_code == 500
        assert b'Error 500' in response.data
        assert b'Internal server error' in response.data

class TestJSONErrorResponses:
    """Test JSON responses for various error codes."""

    def test_400_bad_request_json(self, client):
        """Test bad request error (400) JSON response."""
        response = client.get('/bad-request', headers={'Accept': 'application/json'})
        assert response.status_code == 400
        assert response.is_json
        data = response.get_json()
        assert data['message'] == 'Bad request error'
        assert data['error'] == 'Bad Request'

    def test_401_unauthorized_json(self, client):
        """Test unauthorized error (401) JSON response."""
        response = client.get('/unauthorized', headers={'Accept': 'application/json'})
        assert response.status_code == 401
        assert response.is_json
        data = response.get_json()
        assert data['message'] == 'Unauthorized error'
        assert data['error'] == 'Unauthorized'

    def test_403_forbidden_json(self, client):
        """Test forbidden error (403) JSON response."""
        response = client.get('/forbidden', headers={'Accept': 'application/json'})
        assert response.status_code == 403
        assert response.is_json
        data = response.get_json()
        assert data['message'] == 'Forbidden error'
        assert data['error'] == 'Forbidden'

    def test_429_too_many_requests_json(self, client):
        """Test too many requests error (429) JSON response."""
        response = client.get('/too-many-requests', headers={'Accept': 'application/json'})
        assert response.status_code == 429
        assert response.is_json
        data = response.get_json()
        assert data['message'] == 'Too many requests error'
        assert data['error'] == 'Too Many Requests'

    def test_500_internal_server_error_json(self, client):
        """Test internal server error (500) JSON response."""
        response = client.get('/internal-server-error', headers={'Accept': 'application/json'})
        assert response.status_code == 500
        assert response.is_json
        data = response.get_json()
        assert data['message'] == 'Internal server error'
        assert data['error'] == 'Internal Server Error'

class TestRequestTypeDetection:
    """Test error handler's ability to detect request type."""

    def test_json_request_detection(self, client):
        """Test that JSON requests get JSON responses."""
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        response = client.get('/not-found', headers=headers)
        assert response.status_code == 404
        assert response.is_json
        data = response.get_json()
        assert 'message' in data
        assert 'error' in data

class TestErrorHandlerIntegration:
    """Test error handler integration with the application."""

    def test_error_logging(self, client, caplog):
        """Test that errors are properly logged."""
        response = client.get('/internal-server-error')
        assert response.status_code == 500
        assert any('Internal server error' in record.message for record in caplog.records)

    def test_error_with_custom_message(self, client):
        """Test error handling with custom error message."""
        response = client.get('/custom-error')
        assert response.status_code == 200
        assert b'Custom error message' in response.data 