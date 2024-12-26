"""
Tests for error handlers.
"""

def test_404_error(client):
    """Test 404 error handler."""
    response = client.get('/nonexistent-page')
    assert response.status_code == 404
    assert b'Not Found' in response.data

def test_404_error_json(client):
    """Test 404 error handler with JSON request."""
    response = client.get('/nonexistent-page', headers={'Accept': 'application/json'})
    assert response.status_code == 404
    assert response.json['error'] == 'Not Found'

def test_500_error(app, client):
    """Test 500 error handler."""
    @app.route('/trigger-error')
    def trigger_error():
        raise Exception('Test error')
        
    response = client.get('/trigger-error')
    assert response.status_code == 500
    assert b'Internal Server Error' in response.data

def test_500_error_json(app, client):
    """Test 500 error handler with JSON request."""
    @app.route('/trigger-error')
    def trigger_error():
        raise Exception('Test error')
        
    response = client.get('/trigger-error', headers={'Accept': 'application/json'})
    assert response.status_code == 500
    assert response.json['error'] == 'Internal Server Error'

def test_401_error(client):
    """Test 401 error handler."""
    response = client.get('/api/users')  # Protected endpoint
    assert response.status_code == 401
    assert b'Unauthorized' in response.data

def test_403_error(client, auth_headers):
    """Test 403 error handler."""
    # Modify auth_headers to use non-admin user
    response = client.get('/admin/dashboard', headers=auth_headers)
    assert response.status_code == 403
    assert b'Forbidden' in response.data 