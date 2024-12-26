"""
Test module for error_handlers.py

This module contains integration tests for the application error handlers.
"""

import pytest
from flask import Flask, json, request
from werkzeug.exceptions import (
    BadRequest, Unauthorized, Forbidden, NotFound, 
    MethodNotAllowed, TooManyRequests, InternalServerError
)
from app.error_handlers import register_error_handlers

@pytest.fixture
def app():
    """Create test Flask application."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    register_error_handlers(app)
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

class TestHTMLErrorResponses:
    """Test suite for HTML error responses."""

    def test_400_bad_request(self, client):
        """Test HTML response for 400 Bad Request."""
        @client.application.route('/test-400')
        def test_400():
            raise BadRequest('Invalid input data')

        response = client.get('/test-400')
        assert response.status_code == 400
        assert b'Bad Request' in response.data
        assert b'Invalid input data' in response.data

    def test_401_unauthorized(self, client):
        """Test HTML response for 401 Unauthorized."""
        @client.application.route('/test-401')
        def test_401():
            raise Unauthorized('Authentication required')

        response = client.get('/test-401')
        assert response.status_code == 401
        assert b'Unauthorized' in response.data
        assert b'Authentication required' in response.data

    def test_403_forbidden(self, client):
        """Test HTML response for 403 Forbidden."""
        @client.application.route('/test-403')
        def test_403():
            raise Forbidden('Access denied')

        response = client.get('/test-403')
        assert response.status_code == 403
        assert b'Forbidden' in response.data
        assert b'Access denied' in response.data

    def test_404_not_found(self, client):
        """Test HTML response for 404 Not Found."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        assert b'Not Found' in response.data

    def test_405_method_not_allowed(self, client):
        """Test HTML response for 405 Method Not Allowed."""
        @client.application.route('/test-405', methods=['GET'])
        def test_405():
            return 'GET only'

        response = client.post('/test-405')
        assert response.status_code == 405
        assert b'Method Not Allowed' in response.data

    def test_429_too_many_requests(self, client):
        """Test HTML response for 429 Too Many Requests."""
        @client.application.route('/test-429')
        def test_429():
            raise TooManyRequests('Rate limit exceeded')

        response = client.get('/test-429')
        assert response.status_code == 429
        assert b'Too Many Requests' in response.data
        assert b'Rate limit exceeded' in response.data

    def test_500_internal_server_error(self, client):
        """Test HTML response for 500 Internal Server Error."""
        @client.application.route('/test-500')
        def test_500():
            raise InternalServerError('Server error occurred')

        response = client.get('/test-500')
        assert response.status_code == 500
        assert b'Internal Server Error' in response.data
        assert b'Server error occurred' in response.data

class TestJSONErrorResponses:
    """Test suite for JSON error responses."""

    def test_400_bad_request_json(self, client):
        """Test JSON response for 400 Bad Request."""
        @client.application.route('/test-400-json')
        def test_400_json():
            raise BadRequest('Invalid input data')

        response = client.get('/test-400-json', headers={'Accept': 'application/json'})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Bad Request'
        assert data['message'] == 'Invalid input data'

    def test_401_unauthorized_json(self, client):
        """Test JSON response for 401 Unauthorized."""
        @client.application.route('/test-401-json')
        def test_401_json():
            raise Unauthorized('Authentication required')

        response = client.get('/test-401-json', headers={'Accept': 'application/json'})
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == 'Unauthorized'
        assert data['message'] == 'Authentication required'

    def test_403_forbidden_json(self, client):
        """Test JSON response for 403 Forbidden."""
        @client.application.route('/test-403-json')
        def test_403_json():
            raise Forbidden('Access denied')

        response = client.get('/test-403-json', headers={'Accept': 'application/json'})
        assert response.status_code == 403
        data = json.loads(response.data)
        assert data['error'] == 'Forbidden'
        assert data['message'] == 'Access denied'

    def test_404_not_found_json(self, client):
        """Test JSON response for 404 Not Found."""
        response = client.get('/nonexistent-json', headers={'Accept': 'application/json'})
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'Not Found'

    def test_405_method_not_allowed_json(self, client):
        """Test JSON response for 405 Method Not Allowed."""
        @client.application.route('/test-405-json', methods=['GET'])
        def test_405_json():
            return 'GET only'

        response = client.post('/test-405-json', headers={'Accept': 'application/json'})
        assert response.status_code == 405
        data = json.loads(response.data)
        assert data['error'] == 'Method Not Allowed'

    def test_429_too_many_requests_json(self, client):
        """Test JSON response for 429 Too Many Requests."""
        @client.application.route('/test-429-json')
        def test_429_json():
            raise TooManyRequests('Rate limit exceeded')

        response = client.get('/test-429-json', headers={'Accept': 'application/json'})
        assert response.status_code == 429
        data = json.loads(response.data)
        assert data['error'] == 'Too Many Requests'
        assert data['message'] == 'Rate limit exceeded'

    def test_500_internal_server_error_json(self, client):
        """Test JSON response for 500 Internal Server Error."""
        @client.application.route('/test-500-json')
        def test_500_json():
            raise InternalServerError('Server error occurred')

        response = client.get('/test-500-json', headers={'Accept': 'application/json'})
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['error'] == 'Internal Server Error'
        assert data['message'] == 'Server error occurred'

class TestRequestTypeDetection:
    """Test suite for request type detection."""

    def test_json_request_detection(self, client):
        """Test detection of JSON requests."""
        @client.application.route('/test-detection')
        def test_detection():
            raise BadRequest('Test error')

        # Test with JSON content type
        response = client.get('/test-detection', 
                            content_type='application/json')
        assert response.is_json
        data = json.loads(response.data)
        assert 'error' in data

        # Test with JSON accept header
        response = client.get('/test-detection', 
                            headers={'Accept': 'application/json'})
        assert response.is_json
        data = json.loads(response.data)
        assert 'error' in data

        # Test with regular request
        response = client.get('/test-detection')
        assert not response.is_json
        assert b'Bad Request' in response.data

class TestErrorHandlerIntegration:
    """Test suite for error handler integration with app features."""

    def test_error_logging(self, client, caplog):
        """Test error logging functionality."""
        @client.application.route('/test-logging')
        def test_logging():
            raise InternalServerError('Test error for logging')

        response = client.get('/test-logging')
        assert response.status_code == 500
        assert any('Test error for logging' in record.message 
                  for record in caplog.records)

    def test_error_with_custom_message(self, client):
        """Test error handling with custom error messages."""
        @client.application.route('/test-custom-error')
        def test_custom_error():
            abort = BadRequest()
            abort.description = "Custom error description"
            raise abort

        response = client.get('/test-custom-error')
        assert response.status_code == 400
        assert b'Custom error description' in response.data 