"""
Data service for handling JSON file operations.
"""

import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Base paths for different data types
DATA_DIR = 'data'
USERS_DIR = os.path.join(DATA_DIR, 'users')
SUBJECTS_DIR = os.path.join(DATA_DIR, 'subjects')
ACHIEVEMENTS_DIR = os.path.join(DATA_DIR, 'achievements')

def get_file_path(filename):
    """Get the full path for a data file."""
    if filename.startswith('users/'):
        return os.path.join(DATA_DIR, filename)
    elif filename.startswith('subjects/'):
        return os.path.join(DATA_DIR, filename)
    elif filename.startswith('achievements/'):
        return os.path.join(DATA_DIR, filename)
    return os.path.join(DATA_DIR, filename)

def load_data(filename):
    """
    Load data from a JSON file.
    Args:
        filename: Name of the JSON file (e.g., 'users/users.json')
    Returns:
        dict: Loaded data or empty dict if file doesn't exist
    """
    try:
        file_path = get_file_path(filename)
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return {}
            
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {str(e)}")
        return {}

def save_data(filename, data):
    """
    Save data to a JSON file.
    Args:
        filename: Name of the JSON file (e.g., 'users/users.json')
        data: Data to save
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        file_path = get_file_path(filename)
        
        # Update metadata
        if isinstance(data, dict):
            data.setdefault('metadata', {})
            data['metadata']['last_updated'] = datetime.utcnow().isoformat()
            data['metadata']['version'] = '1.0'
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving data to {file_path}: {str(e)}")
        return False

# Convenience functions for common operations
def get_user(user_id):
    """Get a user by ID."""
    users = load_data('users/users.json').get('users', [])
    return next((user for user in users if user['id'] == user_id), None)

def get_subject(subject_id):
    """Get a subject by ID."""
    subjects = load_data('subjects/subjects.json').get('subjects', [])
    return next((subject for subject in subjects if subject['id'] == subject_id), None)

def get_user_achievements(user_id):
    """Get achievements for a user."""
    achievements_data = load_data('achievements/achievements.json')
    user_achievements = next(
        (ua for ua in achievements_data.get('user_achievements', [])
         if ua['user_id'] == user_id),
        {'achievements': [], 'total_points': 0}
    )
    return user_achievements

def update_user_progress(user_id, subject_id, topic_id):
    """Update a user's progress in a subject."""
    try:
        subjects_data = load_data('subjects/subjects.json')
        subject = next((s for s in subjects_data.get('subjects', [])
                       if s['id'] == subject_id), None)
        
        if not subject:
            return False
            
        # Find user enrollment
        enrollment = next((e for e in subject.get('enrolled_users', [])
                         if e['user_id'] == user_id), None)
        
        if not enrollment:
            return False
            
        # Update completed topics
        if topic_id not in enrollment['completed_topics']:
            enrollment['completed_topics'].append(topic_id)
            
        # Calculate progress
        total_topics = sum(len(section['topics']) for section in subject['sections'])
        completed_topics = len(enrollment['completed_topics'])
        enrollment['progress'] = round((completed_topics / total_topics) * 100)
        enrollment['last_activity'] = datetime.utcnow().isoformat()
        
        # Save changes
        return save_data('subjects/subjects.json', subjects_data)
        
    except Exception as e:
        logger.error(f"Error updating user progress: {str(e)}")
        return False