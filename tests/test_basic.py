import pytest
import json
from app import create_app
from nexuschat.database import db

@pytest.fixture
def client():
    """Create a test client for the application."""
    app, socketio = create_app()
    if app is None:
        pytest.skip("Failed to create app - database connection issue")
    
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_index_page(client):
    """Test the main page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'NexusChat' in response.data

def test_register_endpoint_missing_data(client):
    """Test registration with missing data."""
    response = client.post('/api/register', 
                          data=json.dumps({}),
                          content_type='application/json')
    assert response.status_code == 400

def test_login_endpoint_missing_data(client):
    """Test login with missing data."""
    response = client.post('/api/login',
                          data=json.dumps({}),
                          content_type='application/json')
    assert response.status_code == 400

def test_history_endpoint_unauthorized(client):
    """Test history endpoint without authentication."""
    response = client.get('/api/history')
    assert response.status_code == 401

if __name__ == '__main__':
    pytest.main([__file__])



