"""
Test module for api.py

This module contains tests for the API endpoints.
"""

import pytest
from flask import Flask, json
from app.api import api
from datetime import datetime, UTC

@pytest.fixture
def app():
    """Create test Flask application."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(api)
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def test_data():
    """Create test data."""
    return {
        'subjects': [
            {
                'id': 'subject1',
                'name': 'Test Subject 1',
                'sections': [
                    {
                        'id': 'section1',
                        'name': 'Test Section 1',
                        'topics': [
                            {
                                'id': 'topic1',
                                'name': 'Test Topic 1',
                                'content': 'Test content 1'
                            }
                        ]
                    }
                ]
            }
        ]
    }

class TestAPIEndpoints:
    """Test suite for API endpoints."""

    def test_get_subjects(self, client, mocker, test_data):
        """Test getting all subjects."""
        mocker.patch('app.api.load_data', return_value=test_data)
        
        response = client.get('/api/subjects')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['subjects']) == 1
        assert data['subjects'][0]['name'] == 'Test Subject 1'

    def test_get_subject(self, client, mocker, test_data):
        """Test getting a specific subject."""
        mocker.patch('app.api.load_data', return_value=test_data)
        
        response = client.get('/api/subjects/subject1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Test Subject 1'

    def test_get_subject_not_found(self, client, mocker, test_data):
        """Test getting a non-existent subject."""
        mocker.patch('app.api.load_data', return_value=test_data)
        
        response = client.get('/api/subjects/nonexistent')
        assert response.status_code == 404

    def test_get_section(self, client, mocker, test_data):
        """Test getting a specific section."""
        mocker.patch('app.api.load_data', return_value=test_data)
        
        response = client.get('/api/subjects/subject1/sections/section1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Test Section 1'

    def test_get_section_not_found(self, client, mocker, test_data):
        """Test getting a non-existent section."""
        mocker.patch('app.api.load_data', return_value=test_data)
        
        response = client.get('/api/subjects/subject1/sections/nonexistent')
        assert response.status_code == 404

    def test_get_topic(self, client, mocker, test_data):
        """Test getting a specific topic."""
        mocker.patch('app.api.load_data', return_value=test_data)
        
        response = client.get('/api/subjects/subject1/sections/section1/topics/topic1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Test Topic 1'
        assert data['content'] == 'Test content 1'

    def test_get_topic_not_found(self, client, mocker, test_data):
        """Test getting a non-existent topic."""
        mocker.patch('app.api.load_data', return_value=test_data)
        
        response = client.get('/api/subjects/subject1/sections/section1/topics/nonexistent')
        assert response.status_code == 404

class TestAPIValidation:
    """Test suite for API input validation."""

    def test_invalid_subject_id(self, client):
        """Test validation of invalid subject ID."""
        response = client.get('/api/subjects/invalid@id')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_invalid_section_id(self, client):
        """Test validation of invalid section ID."""
        response = client.get('/api/subjects/subject1/sections/invalid@id')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_invalid_topic_id(self, client):
        """Test validation of invalid topic ID."""
        response = client.get('/api/subjects/subject1/sections/section1/topics/invalid@id')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

class TestAPIRateLimiting:
    """Test suite for API rate limiting."""

    def test_rate_limit_subjects(self, client):
        """Test rate limiting on subjects endpoint."""
        # Make multiple requests to trigger rate limit
        for _ in range(25):  # More than MAX_ATTEMPTS
            response = client.get('/api/subjects')
        
        # Next request should be rate limited
        response = client.get('/api/subjects')
        assert response.status_code == 429
        data = json.loads(response.data)
        assert data['error'] == 'Too Many Requests'

    def test_rate_limit_sections(self, client):
        """Test rate limiting on sections endpoint."""
        # Make multiple requests to trigger rate limit
        for _ in range(25):  # More than MAX_ATTEMPTS
            response = client.get('/api/subjects/subject1/sections')
        
        # Next request should be rate limited
        response = client.get('/api/subjects/subject1/sections')
        assert response.status_code == 429
        data = json.loads(response.data)
        assert data['error'] == 'Too Many Requests'

class TestAPIErrorHandling:
    """Test suite for API error handling."""

    def test_internal_server_error(self, client, mocker):
        """Test handling of internal server error."""
        mocker.patch('app.api.load_data', side_effect=Exception('Test error'))
        
        response = client.get('/api/subjects')
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['error'] == 'Internal Server Error'

    def test_malformed_json(self, client):
        """Test handling of malformed JSON in request."""
        response = client.post('/api/subjects', 
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Bad Request' 