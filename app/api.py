"""
API Routes Module

This module defines all API endpoints for the application.
"""

import os
from flask import Blueprint, jsonify, current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended.exceptions import NoAuthorizationError
from .services.data_service import load_data, save_data
from functools import wraps
import re
import time
from datetime import datetime, UTC
import threading
from urllib.parse import urlparse

api = Blueprint('api', __name__, url_prefix='/api')

# Thread-safe rate limiting
rate_limit_lock = threading.Lock()
api_requests = {}
MAX_REQUESTS = 100  # per window
REQUEST_WINDOW = 60  # 1 minute
MAX_CONTENT_SIZE = 5 * 1024 * 1024  # 5MB

# Constants
MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Valid content block types and their constraints
VALID_BLOCK_TYPES = {
    'text': {'max_length': 100000},  # 100KB
    'code': {'max_length': 50000},   # 50KB
    'image': {
        'allowed_schemes': {'https'},
        'max_url_length': 2048,
        'max_caption_length': 500,
        'max_alt_length': 500
    },
    'table': {
        'max_headers': 20,
        'max_rows': 1000,
        'max_cell_length': 1000
    }
}

def rate_limit(max_requests: int, window: int):
    """Thread-safe rate limiting decorator for API endpoints."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = request.remote_addr
            current_time = time.time()
            
            with rate_limit_lock:
                # Clean up old requests
                api_requests.update({
                    k: v for k, v in api_requests.items()
                    if current_time - v['timestamp'] < window
                })
                
                # Check requests for this IP
                if ip in api_requests:
                    requests = api_requests[ip]
                    if requests['count'] >= max_requests:
                        return jsonify({
                            'error': 'Rate limit exceeded. Please try again later.'
                        }), 429
                    requests['count'] += 1
                else:
                    api_requests[ip] = {
                        'count': 1,
                        'timestamp': current_time
                    }
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_subject_id(subject_id: int) -> bool:
    """Validate subject ID format and range."""
    return isinstance(subject_id, int) and 1 <= subject_id <= 9999

def validate_content_block(block: dict) -> tuple[bool, str]:
    """Validate content block structure and type."""
    if not isinstance(block, dict):
        return False, "Invalid block structure"
    if 'type' not in block or 'value' not in block:
        return False, "Missing required fields"
    if block['type'] not in VALID_BLOCK_TYPES:
        return False, f"Invalid block type: {block['type']}"
        
    block_type = block['type']
    constraints = VALID_BLOCK_TYPES[block_type]
    
    if block_type in ['text', 'code']:
        if not isinstance(block['value'], str):
            return False, "Value must be a string"
        if len(block['value'].encode('utf-8')) > constraints['max_length']:
            return False, f"Content exceeds maximum length of {constraints['max_length']} bytes"
            
    elif block_type == 'image':
        if not isinstance(block['value'], dict):
            return False, "Image value must be an object"
        if not all(k in block['value'] for k in ['url', 'caption', 'alt_text']):
            return False, "Missing required image fields"
            
        url = urlparse(block['value']['url'])
        if url.scheme not in constraints['allowed_schemes']:
            return False, "Invalid URL scheme"
        if len(block['value']['url']) > constraints['max_url_length']:
            return False, "URL too long"
        if len(block['value']['caption']) > constraints['max_caption_length']:
            return False, "Caption too long"
        if len(block['value']['alt_text']) > constraints['max_alt_length']:
            return False, "Alt text too long"
            
    elif block_type == 'table':
        if not isinstance(block['value'], dict):
            return False, "Table value must be an object"
        if not all(k in block['value'] for k in ['headers', 'rows']):
            return False, "Missing required table fields"
            
        headers = block['value']['headers']
        rows = block['value']['rows']
        
        if not isinstance(headers, list) or not isinstance(rows, list):
            return False, "Headers and rows must be lists"
        if len(headers) > constraints['max_headers']:
            return False, "Too many headers"
        if len(rows) > constraints['max_rows']:
            return False, "Too many rows"
            
        # Check cell lengths
        for header in headers:
            if len(str(header)) > constraints['max_cell_length']:
                return False, "Header cell too long"
        for row in rows:
            if not isinstance(row, list):
                return False, "Row must be a list"
            if len(row) != len(headers):
                return False, "Row length must match headers"
            for cell in row:
                if len(str(cell)) > constraints['max_cell_length']:
                    return False, "Row cell too long"
                    
    return True, ""

def sanitize_input(data: str, max_length: int = 1000) -> str:
    """Sanitize input data to prevent injection attacks."""
    if not isinstance(data, str):
        return ""
    # Allow alphanumeric, basic punctuation, and common symbols
    sanitized = re.sub(r'[^\w\s\-_.,!?@#$%^&*()[\]{}|;:\'\"<>\/+~`=]', '', data)
    # Limit length to prevent DoS
    return sanitized[:max_length]

def admin_required(f):
    """Decorator to check if user has admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            user_id = get_jwt_identity()
            if not user_id:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Load user data
            users_data = load_data('users.json')
            user = next(
                (u for u in users_data.get('users', []) if u.get('id') == user_id),
                None
            )
            
            if not user or user.get('role') != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
                
            return f(*args, **kwargs)
        except NoAuthorizationError:
            return jsonify({'error': 'Invalid or expired token'}), 401
        except Exception as e:
            current_app.logger.error(f"Error in admin check: {str(e)}")
            return jsonify({'error': 'Authentication error'}), 401
    return decorated_function

def validate_section_id(section_id: int) -> bool:
    """Validate section ID format and range."""
    return isinstance(section_id, int) and 1 <= section_id <= 9999

def validate_topic_id(topic_id: int) -> bool:
    """Validate topic ID format and range."""
    return isinstance(topic_id, int) and 1 <= topic_id <= 9999

def paginate(items: list, page: int = 1, per_page: int = DEFAULT_PAGE_SIZE) -> dict:
    """Paginate a list of items."""
    per_page = min(per_page, MAX_PAGE_SIZE)
    start = (page - 1) * per_page
    end = start + per_page
    
    return {
        'items': items[start:end],
        'total': len(items),
        'page': page,
        'per_page': per_page,
        'total_pages': (len(items) + per_page - 1) // per_page
    }

@api.route('/subjects')
@jwt_required()
@rate_limit(MAX_REQUESTS, REQUEST_WINDOW)
def get_subjects():
    """Get all subjects with pagination."""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', DEFAULT_PAGE_SIZE))
        
        subjects_data = load_data('subject_database.json')
        subjects = subjects_data.get('subjects', [])
        
        # Sanitize response data
        safe_subjects = [{
            'id': subject.get('id'),
            'name': sanitize_input(subject.get('name', '')),
            'description': sanitize_input(subject.get('description', '')),
            'created_at': subject.get('created_at'),
            'updated_at': subject.get('updated_at')
        } for subject in subjects]
        
        return jsonify(paginate(safe_subjects, page, per_page)), 200
    except Exception as e:
        current_app.logger.error(f"Error loading subjects: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/subjects/<int:subject_id>')
@jwt_required()
@rate_limit(MAX_REQUESTS, REQUEST_WINDOW)
def get_subject(subject_id):
    """
    Get a specific subject by ID.
    
    Args:
        subject_id (int): The ID of the subject to retrieve
        
    Returns:
        Response: JSON response with subject data
    """
    try:
        if not validate_subject_id(subject_id):
            return jsonify({'error': 'Invalid subject ID'}), 400
            
        subjects_data = load_data('subject_database.json')
        subjects = subjects_data.get('subjects', [])
        
        subject = next((s for s in subjects if s.get('id') == subject_id), None)
        if subject:
            # Sanitize response data
            safe_subject = {
                'id': subject.get('id'),
                'name': sanitize_input(subject.get('name', '')),
                'description': sanitize_input(subject.get('description', '')),
                'created_at': subject.get('created_at'),
                'updated_at': subject.get('updated_at'),
                'sections': subject.get('sections', [])
            }
            return jsonify(safe_subject), 200
        return jsonify({'error': 'Subject not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error loading subject {subject_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/subjects/<int:subject_id>/sections/<int:section_id>')
@jwt_required()
@rate_limit(MAX_REQUESTS, REQUEST_WINDOW)
def get_section(subject_id, section_id):
    """
    Get a specific section within a subject.
    
    Args:
        subject_id (int): The ID of the subject
        section_id (int): The ID of the section
        
    Returns:
        Response: JSON response with section data
    """
    try:
        if not validate_subject_id(subject_id):
            return jsonify({'error': 'Invalid subject ID'}), 400
            
        subjects_data = load_data('subject_database.json')
        subject = next((s for s in subjects_data.get('subjects', []) if s.get('id') == subject_id), None)
        
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
            
        section = next((s for s in subject.get('sections', []) if s.get('id') == section_id), None)
        
        if section:
            return jsonify(section), 200
        return jsonify({'error': 'Section not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error loading section {section_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/subjects/<int:subject_id>/sections/<int:section_id>/topics/<int:topic_id>')
@jwt_required()
@rate_limit(MAX_REQUESTS, REQUEST_WINDOW)
def get_topic(subject_id, section_id, topic_id):
    """
    Get a specific topic within a section.
    
    Args:
        subject_id (int): The ID of the subject
        section_id (int): The ID of the section
        topic_id (int): The ID of the topic
        
    Returns:
        Response: JSON response with topic data
    """
    try:
        if not validate_subject_id(subject_id):
            return jsonify({'error': 'Invalid subject ID'}), 400
            
        subjects_data = load_data('subject_database.json')
        subject = next((s for s in subjects_data.get('subjects', []) if s.get('id') == subject_id), None)
        
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
            
        section = next((s for s in subject.get('sections', []) if s.get('id') == section_id), None)
        
        if not section:
            return jsonify({'error': 'Section not found'}), 404
            
        topic = next((t for t in section.get('topics', []) if t.get('id') == topic_id), None)
        
        if topic:
            return jsonify(topic), 200
        return jsonify({'error': 'Topic not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error loading topic {topic_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/subjects', methods=['POST'])
@jwt_required()
@admin_required
@rate_limit(MAX_REQUESTS, REQUEST_WINDOW)
def create_subject():
    """Create a new subject."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Missing request data'}), 400
            
        name = data.get('name')
        description = data.get('description')
        
        if not name or not description:
            return jsonify({'error': 'Name and description are required'}), 400
            
        subjects_data = load_data('subject_database.json')
        subjects = subjects_data.get('subjects', [])
        
        # Generate new ID
        new_id = max((s.get('id', 0) for s in subjects), default=0) + 1
        
        # Create new subject
        new_subject = {
            'id': new_id,
            'name': name,
            'description': description,
            'created_at': datetime.now(UTC).isoformat(),
            'updated_at': datetime.now(UTC).isoformat(),
            'sections': []
        }
        
        subjects.append(new_subject)
        save_data('subject_database.json', {'subjects': subjects})
        
        return jsonify(new_subject), 201
    except Exception as e:
        current_app.logger.error(f"Error creating subject: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/subjects/<int:subject_id>', methods=['PUT'])
@jwt_required()
@admin_required
@rate_limit(MAX_REQUESTS, REQUEST_WINDOW)
def update_subject(subject_id):
    """Update an existing subject."""
    try:
        if not validate_subject_id(subject_id):
            return jsonify({'error': 'Invalid subject ID'}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Missing request data'}), 400
            
        subjects_data = load_data('subject_database.json')
        subjects = subjects_data.get('subjects', [])
        
        subject_index = next((i for i, s in enumerate(subjects) if s.get('id') == subject_id), None)
        
        if subject_index is None:
            return jsonify({'error': 'Subject not found'}), 404
            
        # Update subject
        subject = subjects[subject_index]
        subject['name'] = data.get('name', subject['name'])
        subject['description'] = data.get('description', subject['description'])
        subject['updated_at'] = datetime.now(UTC).isoformat()
        
        save_data('subject_database.json', {'subjects': subjects})
        
        return jsonify(subject), 200
    except Exception as e:
        current_app.logger.error(f"Error updating subject {subject_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/subjects/<int:subject_id>', methods=['DELETE'])
@jwt_required()
@admin_required
@rate_limit(MAX_REQUESTS, REQUEST_WINDOW)
def delete_subject(subject_id):
    """Delete a subject."""
    try:
        if not validate_subject_id(subject_id):
            return jsonify({'error': 'Invalid subject ID'}), 400
            
        subjects_data = load_data('subject_database.json')
        subjects = subjects_data.get('subjects', [])
        
        subject_index = next((i for i, s in enumerate(subjects) if s.get('id') == subject_id), None)
        
        if subject_index is None:
            return jsonify({'error': 'Subject not found'}), 404
            
        # Remove subject
        subjects.pop(subject_index)
        save_data('subject_database.json', {'subjects': subjects})
        
        return jsonify({'message': 'Subject deleted successfully'}), 200
    except Exception as e:
        current_app.logger.error(f"Error deleting subject {subject_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/users', methods=['GET'])
@jwt_required()
@admin_required
@rate_limit(MAX_REQUESTS, REQUEST_WINDOW)
def get_users():
    """Get list of users (admin only)."""
    try:
        users_data = load_data('users.json')
        users = users_data.get('users', [])
        
        # Remove sensitive information and sanitize
        safe_users = [{
            'id': user.get('id'),
            'username': sanitize_input(user.get('username', '')),
            'role': user.get('role', 'user'),
            'created_at': user.get('created_at'),
            'last_login': user.get('last_login')
        } for user in users]
        
        return jsonify({'users': safe_users}), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching users list: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.errorhandler(NoAuthorizationError)
def handle_auth_error(error):
    """Handle JWT-specific errors."""
    return jsonify({'error': 'Authentication required'}), 401

@api.errorhandler(Exception)
def handle_error(error):
    """Global error handler for API routes."""
    current_app.logger.error(f"Unhandled error: {str(error)}")
    if isinstance(error, NoAuthorizationError):
        return jsonify({'error': 'Authentication required'}), 401
    return jsonify({'error': 'Internal server error'}), 500 

@api.route('/sections/<int:section_id>', methods=['PUT'])
@jwt_required()
@admin_required
@rate_limit(MAX_REQUESTS, REQUEST_WINDOW)
def update_section(section_id):
    """Update an existing section."""
    try:
        if not validate_section_id(section_id):
            return jsonify({'error': 'Invalid section ID'}), 400
            
        if request.content_length and request.content_length > MAX_REQUEST_SIZE:
            return jsonify({'error': 'Request too large'}), 413
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Missing request data'}), 400
            
        subjects_data = load_data('subject_database.json')
        subjects = subjects_data.get('subjects', [])
        
        # Find the section in any subject
        section_found = False
        for subject in subjects:
            for section in subject.get('sections', []):
                if section.get('id') == section_id:
                    section['name'] = data.get('name', section['name'])
                    section['updated_at'] = datetime.now(UTC).isoformat()
                    section_found = True
                    break
            if section_found:
                break
                
        if not section_found:
            return jsonify({'error': 'Section not found'}), 404
            
        save_data('subject_database.json', {'subjects': subjects})
        return jsonify({'message': 'Section updated successfully'}), 200
    except Exception as e:
        current_app.logger.error(f"Error updating section {section_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/sections/<int:section_id>/topics', methods=['POST'])
@jwt_required()
@admin_required
@rate_limit(MAX_REQUESTS, REQUEST_WINDOW)
def create_topic(section_id):
    """Create a new topic in a section."""
    try:
        if not validate_section_id(section_id):
            return jsonify({'error': 'Invalid section ID'}), 400
            
        if request.content_length and request.content_length > MAX_REQUEST_SIZE:
            return jsonify({'error': 'Request too large'}), 413
            
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
            
        subjects_data = load_data('subject_database.json')
        subjects = subjects_data.get('subjects', [])
        
        # Find the section
        section_found = False
        for subject in subjects:
            for section in subject.get('sections', []):
                if section.get('id') == section_id:
                    # Generate new topic ID
                    topics = section.get('topics', [])
                    new_id = max((t.get('id', 0) for t in topics), default=0) + 1
                    
                    # Create new topic
                    new_topic = {
                        'id': new_id,
                        'name': data['name'],
                        'created_at': datetime.now(UTC).isoformat(),
                        'updated_at': datetime.now(UTC).isoformat(),
                        'content_blocks': []
                    }
                    
                    topics.append(new_topic)
                    section['topics'] = topics
                    section_found = True
                    break
            if section_found:
                break
                
        if not section_found:
            return jsonify({'error': 'Section not found'}), 404
            
        save_data('subject_database.json', {'subjects': subjects})
        return jsonify(new_topic), 201
    except Exception as e:
        current_app.logger.error(f"Error creating topic in section {section_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500 