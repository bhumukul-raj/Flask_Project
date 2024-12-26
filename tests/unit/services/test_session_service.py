"""
Test module for session_service.py

This module contains tests for session tracking and management functions.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from app.services.session_service import (
    track_session, cleanup_user_sessions, cleanup_sessions,
    get_active_sessions, get_active_sessions_count,
    remove_session, clear_user_sessions, active_sessions
)

@pytest.fixture
def mock_current_user():
    """Create a mock current user."""
    user = Mock()
    user.is_authenticated = True
    user.get_id.return_value = "123"
    user.username = "testuser"
    return user

@pytest.fixture
def mock_session():
    """Create a mock Flask session."""
    return {
        '_id': 'session123',
        'ip_address': '127.0.0.1'
    }

@pytest.fixture
def sample_session_data():
    """Create sample session data."""
    return {
        'session123': {
            'user_id': '123',
            'username': 'testuser',
            'last_activity': datetime.utcnow(),
            'ip_address': '127.0.0.1'
        },
        'session456': {
            'user_id': '456',
            'username': 'otheruser',
            'last_activity': datetime.utcnow() - timedelta(minutes=40),
            'ip_address': '127.0.0.2'
        }
    }

class TestSessionService:
    """Test suite for session service functions."""

    def setup_method(self):
        """Setup method to clear active sessions before each test."""
        active_sessions.clear()

    def test_track_session(self, mock_current_user, mock_session):
        """Test session tracking for authenticated user."""
        with patch('app.services.session_service.current_user', mock_current_user):
            with patch('app.services.session_service.session', mock_session):
                track_session()
                
                assert 'session123' in active_sessions
                session_data = active_sessions['session123']
                assert session_data['user_id'] == '123'
                assert session_data['username'] == 'testuser'
                assert session_data['ip_address'] == '127.0.0.1'
                assert isinstance(session_data['last_activity'], datetime)

    def test_track_session_unauthenticated(self, mock_session):
        """Test session tracking for unauthenticated user."""
        mock_user = Mock()
        mock_user.is_authenticated = False
        
        with patch('app.services.session_service.current_user', mock_user):
            with patch('app.services.session_service.session', mock_session):
                track_session()
                assert 'session123' not in active_sessions

    def test_cleanup_user_sessions(self, sample_session_data):
        """Test cleaning up sessions for a specific user."""
        active_sessions.update(sample_session_data)
        cleanup_user_sessions('123')
        
        assert 'session123' not in active_sessions
        assert 'session456' in active_sessions

    def test_cleanup_sessions(self, sample_session_data):
        """Test cleaning up expired sessions."""
        active_sessions.update(sample_session_data)
        cleanup_sessions(max_age_minutes=30)
        
        assert 'session123' in active_sessions  # Recent session
        assert 'session456' not in active_sessions  # Expired session

    def test_get_active_sessions(self, sample_session_data):
        """Test retrieving active sessions."""
        active_sessions.update(sample_session_data)
        sessions = get_active_sessions()
        
        assert isinstance(sessions, dict)
        assert len(sessions) == 1  # Only non-expired sessions
        assert 'session123' in sessions

    def test_get_active_sessions_count(self, sample_session_data):
        """Test counting active sessions."""
        active_sessions.update(sample_session_data)
        count = get_active_sessions_count()
        
        assert isinstance(count, int)
        assert count == 1  # Only non-expired sessions

    def test_remove_session(self, sample_session_data):
        """Test removing a specific session."""
        active_sessions.update(sample_session_data)
        remove_session('session123')
        
        assert 'session123' not in active_sessions
        assert 'session456' in active_sessions

    def test_clear_user_sessions(self, sample_session_data):
        """Test clearing all sessions for a specific user."""
        active_sessions.update(sample_session_data)
        clear_user_sessions('123')
        
        assert 'session123' not in active_sessions
        assert 'session456' in active_sessions

    def test_cleanup_sessions_empty(self):
        """Test cleaning up sessions when there are none."""
        cleanup_sessions()
        assert len(active_sessions) == 0

    def test_cleanup_sessions_all_active(self):
        """Test cleaning up sessions when all are active."""
        current_time = datetime.utcnow()
        test_sessions = {
            'session1': {
                'user_id': '1',
                'username': 'user1',
                'last_activity': current_time,
                'ip_address': '127.0.0.1'
            },
            'session2': {
                'user_id': '2',
                'username': 'user2',
                'last_activity': current_time,
                'ip_address': '127.0.0.2'
            }
        }
        active_sessions.update(test_sessions)
        cleanup_sessions(max_age_minutes=30)
        
        assert len(active_sessions) == 2 