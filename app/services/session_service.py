"""
Session Service Module

This module handles session tracking and management.
"""

from datetime import datetime, timedelta
from flask import session
from flask_login import current_user

# Store active sessions in memory (use Redis in production)
active_sessions = {}

def track_session():
    """Track current user session."""
    if current_user.is_authenticated:
        session_id = session.get('_id')
        if session_id:
            # Clean up any existing sessions for this user
            cleanup_user_sessions(current_user.get_id())
            # Update or create session
            active_sessions[session_id] = {
                'user_id': current_user.get_id(),
                'username': current_user.username,
                'last_activity': datetime.utcnow(),
                'ip_address': session.get('ip_address', 'unknown')
            }

def cleanup_user_sessions(user_id):
    """Remove all sessions for a specific user."""
    to_remove = []
    for session_id, session_data in active_sessions.items():
        if session_data['user_id'] == user_id:
            to_remove.append(session_id)
    
    for session_id in to_remove:
        active_sessions.pop(session_id, None)

def cleanup_sessions(max_age_minutes=30):
    """Remove expired sessions."""
    current_time = datetime.utcnow()
    expired = []
    for session_id, session_data in active_sessions.items():
        last_activity = session_data['last_activity']
        if current_time - last_activity > timedelta(minutes=max_age_minutes):
            expired.append(session_id)
    
    for session_id in expired:
        active_sessions.pop(session_id, None)

def get_active_sessions():
    """Get list of active sessions."""
    cleanup_sessions()
    return active_sessions

def get_active_sessions_count():
    """Get count of active sessions."""
    cleanup_sessions()
    return len(active_sessions)

def remove_session(session_id):
    """Remove a specific session."""
    active_sessions.pop(session_id, None)

def clear_user_sessions(user_id):
    """Clear all sessions for a specific user."""
    cleanup_user_sessions(user_id) 