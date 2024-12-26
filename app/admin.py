"""
Admin Module

This module handles all admin-related functionality including:
- User management (CRUD operations)
- Subject management (CRUD operations)
- Section management within subjects
- Topic management within sections
- Admin dashboard statistics

Routes:
- /admin/dashboard: Admin dashboard with statistics
- /admin/users: User management interface
- /admin/subjects: Subject management interface
- /admin/subjects/<subject_id>/sections: Section management interface
- /admin/subjects/<subject_id>/sections/<section_id>/topics: Topic management interface

Dependencies:
- Flask-Login for authentication
- JSON files for data storage
"""

import uuid
from datetime import datetime, UTC
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from .services.data_service import load_data, save_data
from .utils.validators import validate_username, validate_password
from .services.session_service import get_active_sessions, get_active_sessions_count, remove_session
import json
import logging

# Configure logger for admin module
logger = logging.getLogger(__name__)

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """
    Decorator to check if user has admin privileges.

    This decorator should be used after @login_required to ensure
    only authenticated admin users can access the protected routes.

    Args:
        f (function): The function to be decorated. This is the view function
                      that requires admin privileges to access.

    Returns:
        function: The wrapped function with admin check. This function will
                  perform the authentication and authorization checks before
                  allowing access to the original function.

    Raises:
        None directly, but may trigger a redirect if the user is not
        authenticated or lacks admin privileges.

    Note:
        This decorator assumes the use of Flask-Login for user authentication
        and that the User model has an `is_admin()` method.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            logger.warning(f'Unauthorized access attempt to admin area by user: {current_user.username if current_user.is_authenticated else "anonymous"}')
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def load_subject_by_id(subject_id):
    """
    Load a subject from the database by its ID.
    
    Args:
        subject_id (str): The ID of the subject to load
        
    Returns:
        dict: The subject data if found, None otherwise
        
    Note:
        This is a helper function used by various subject management routes.
    """
    try:
        subjects_data = load_data('subject_database.json')
        subjects = subjects_data.get('subjects', [])
        subject = next((s for s in subjects if s['id'] == subject_id), None)
        if subject:
            logger.debug(f'Subject loaded successfully: {subject_id}')
        else:
            logger.warning(f'Subject not found: {subject_id}')
        return subject
    except Exception as e:
        logger.error(f'Error loading subject {subject_id}: {str(e)}')
        return None

def save_subject(subject):
    """
    Save or update a subject in the database.
    
    Args:
        subject (dict): The subject data to save
        
    Returns:
        bool: True if save was successful, False otherwise
        
    Note:
        This function handles both creating new subjects and updating existing ones.
    """
    try:
        subjects_data = load_data('subject_database.json')
        subjects = subjects_data.get('subjects', [])
        
        subject_index = next((i for i, s in enumerate(subjects) if s['id'] == subject['id']), -1)
        if subject_index >= 0:
            subjects[subject_index] = subject
            logger.info(f'Subject updated: {subject["id"]}')
        else:
            subjects.append(subject)
            logger.info(f'New subject created: {subject["id"]}')
        
        return save_data('subject_database.json', {'subjects': subjects})
    except Exception as e:
        logger.error(f'Error saving subject {subject.get("id")}: {str(e)}')
        return False

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """
    Admin dashboard view showing system statistics and recent activities.
    
    Displays:
    - Total number of users
    - Total number of subjects
    - Active sessions count and details
    - Recent user activities (last 5 logins)
    
    Returns:
        rendered template: admin_dashboard.html with context data
    """
    try:
        # Load data for dashboard
        users_data = load_data('users.json')
        subjects_data = load_data('subject_database.json')
        
        # Calculate statistics
        user_count = len(users_data.get('users', []))
        subject_count = len(subjects_data.get('subjects', []))
        
        # Get active sessions
        active_sessions = get_active_sessions()
        active_sessions_count = get_active_sessions_count()
        
        # Get recent activities (last 5 logins)
        recent_activities = []
        for user in sorted(users_data.get('users', []), 
                          key=lambda x: x.get('last_login', ''), 
                          reverse=True)[:5]:
            if user.get('last_login'):
                recent_activities.append({
                    'user': user['username'],
                    'time': user['last_login'],
                    'action': 'Logged in'
                })
        
        logger.info(f'Admin dashboard accessed by {current_user.username}')
        return render_template('admin/admin_panel.html',
                             user_count=user_count,
                             subject_count=subject_count,
                             active_sessions=active_sessions,
                             active_sessions_count=active_sessions_count,
                             recent_activities=recent_activities)
    except Exception as e:
        logger.error(f'Error loading admin dashboard: {str(e)}')
        flash('Error loading dashboard data', 'error')
        return redirect(url_for('main.home'))

@admin.route('/terminate_session/<session_id>', methods=['POST'])
@login_required
@admin_required
def terminate_session(session_id):
    """Terminate a specific user session."""
    try:
        remove_session(session_id)
        flash('Session terminated successfully', 'success')
    except Exception as e:
        logger.error(f'Error terminating session: {str(e)}')
        flash('Error terminating session', 'error')
    return redirect(url_for('admin.dashboard'))

@admin.route('/users')
@login_required
@admin_required
def users():
    """Manage users."""
    users_data = load_data('users.json')
    return render_template('admin/manage_users.html', users=users_data.get('users', []))

@admin.route('/add_user', methods=['POST'])
@login_required
@admin_required
def add_user():
    """Add a new user."""
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'user')

        # Validate input
        if not username or not password:
            flash('Username and password are required', 'error')
            return redirect(url_for('admin.users'))

        # Validate username
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            flash(error_msg, 'error')
            return redirect(url_for('admin.users'))

        # Validate password
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            flash(error_msg, 'error')
            return redirect(url_for('admin.users'))

        # Load existing users
        users_data = load_data('users.json')
        users = users_data.get('users', [])

        # Check if username exists
        if any(user.get('username', '').lower() == username.lower() for user in users):
            flash('Username already exists', 'error')
            return redirect(url_for('admin.users'))

        # Create new user
        new_user = {
            'id': str(uuid.uuid4()),
            'username': username,
            'password': generate_password_hash(password),
            'role': role,
            'created_at': datetime.now(UTC).isoformat(),
            'last_login': None
        }

        users.append(new_user)
        if save_data('users.json', {'users': users}):
            flash('User added successfully', 'success')
        else:
            flash('Failed to add user', 'error')

        return redirect(url_for('admin.users'))
    except Exception as e:
        current_app.logger.error(f"Error adding user: {str(e)}")
        flash('Failed to add user', 'error')
        return redirect(url_for('admin.users'))

@admin.route('/edit_user', methods=['POST'])
@login_required
@admin_required
def edit_user():
    """Edit a user's role."""
    try:
        user_id = request.form.get('user_id')
        role = request.form.get('role')

        if not user_id or not role:
            flash('Invalid request', 'error')
            return redirect(url_for('admin.users'))

        # Load users
        users_data = load_data('users.json')
        users = users_data.get('users', [])

        # Find and update user
        for user in users:
            if user['id'] == user_id:
                if user['username'] == current_user.username:
                    flash('Cannot change your own role', 'error')
                    return redirect(url_for('admin.users'))
                user['role'] = role
                break

        if save_data('users.json', {'users': users}):
            flash('User updated successfully', 'success')
        else:
            flash('Failed to update user', 'error')

        return redirect(url_for('admin.users'))
    except Exception as e:
        current_app.logger.error(f"Error editing user: {str(e)}")
        flash('Failed to update user', 'error')
        return redirect(url_for('admin.users'))

@admin.route('/delete_user', methods=['POST'])
@login_required
@admin_required
def delete_user():
    """Delete a user."""
    try:
        user_id = request.form.get('user_id')

        if not user_id:
            flash('Invalid request', 'error')
            return redirect(url_for('admin.users'))

        # Load users
        users_data = load_data('users.json')
        users = users_data.get('users', [])

        # Find user to delete
        user_to_delete = next((user for user in users if user['id'] == user_id), None)
        if not user_to_delete:
            flash('User not found', 'error')
            return redirect(url_for('admin.users'))

        # Prevent self-deletion
        if user_to_delete['username'] == current_user.username:
            flash('Cannot delete your own account', 'error')
            return redirect(url_for('admin.users'))

        # Remove user
        users = [user for user in users if user['id'] != user_id]
        if save_data('users.json', {'users': users}):
            flash('User deleted successfully', 'success')
        else:
            flash('Failed to delete user', 'error')

        return redirect(url_for('admin.users'))
    except Exception as e:
        current_app.logger.error(f"Error deleting user: {str(e)}")
        flash('Failed to delete user', 'error')
        return redirect(url_for('admin.users'))

@admin.route('/subjects')
@login_required
@admin_required
def subjects():
    """Manage subjects."""
    subjects_data = load_data('subject_database.json')
    return render_template('admin/manage_subjects.html', subjects=subjects_data.get('subjects', []))

@admin.route('/add_subject', methods=['POST'])
@login_required
@admin_required
def add_subject():
    """Add a new subject."""
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        level = request.form.get('level')
        status = request.form.get('status', 'active')

        if not all([title, description, category, level]):
            flash('All fields are required', 'error')
            return redirect(url_for('admin.subjects'))

        # Load subjects
        subjects_data = load_data('subject_database.json')
        subjects = subjects_data.get('subjects', [])

        # Check if subject exists
        if any(subject.get('name', '').lower() == title.lower() for subject in subjects):
            flash('Subject already exists', 'error')
            return redirect(url_for('admin.subjects'))

        # Create new subject with sections array
        new_subject = {
            'id': title.lower().replace(' ', '-'),  # URL-friendly ID
            'name': title,
            'description': description,
            'created_at': datetime.now(UTC).isoformat(),
            'updated_at': datetime.now(UTC).isoformat(),
            'sections': []  # Initialize empty sections array
        }

        subjects.append(new_subject)
        if save_data('subject_database.json', {'subjects': subjects}):
            flash('Subject added successfully', 'success')
        else:
            flash('Failed to add subject', 'error')

        return redirect(url_for('admin.subjects'))
    except Exception as e:
        current_app.logger.error(f"Error adding subject: {str(e)}")
        flash('Failed to add subject', 'error')
        return redirect(url_for('admin.subjects'))

@admin.route('/edit_subject', methods=['POST'])
@login_required
@admin_required
def edit_subject():
    """Edit a subject."""
    try:
        subject_id = request.form.get('subject_id')
        title = request.form.get('title')
        description = request.form.get('description')

        if not all([subject_id, title, description]):
            flash('All fields are required', 'error')
            return redirect(url_for('admin.subjects'))

        # Load subjects
        subjects_data = load_data('subject_database.json')
        subjects = subjects_data.get('subjects', [])

        # Find and update subject
        for subject in subjects:
            if subject['id'] == subject_id:
                subject.update({
                    'name': title,
                    'description': description,
                    'updated_at': datetime.now(UTC).isoformat()
                })
                break

        if save_data('subject_database.json', {'subjects': subjects}):
            flash('Subject updated successfully', 'success')
        else:
            flash('Failed to update subject', 'error')

        return redirect(url_for('admin.subjects'))
    except Exception as e:
        current_app.logger.error(f"Error editing subject: {str(e)}")
        flash('Failed to update subject', 'error')
        return redirect(url_for('admin.subjects'))

@admin.route('/delete_subject', methods=['POST'])
@login_required
@admin_required
def delete_subject():
    """Delete a subject."""
    try:
        subject_id = request.form.get('subject_id')

        if not subject_id:
            flash('Invalid request', 'error')
            return redirect(url_for('admin.subjects'))

        # Load subjects
        subjects_data = load_data('subject_database.json')
        subjects = subjects_data.get('subjects', [])

        # Remove subject
        subjects = [subject for subject in subjects if subject['id'] != subject_id]
        if save_data('subject_database.json', {'subjects': subjects}):
            flash('Subject deleted successfully', 'success')
        else:
            flash('Failed to delete subject', 'error')

        return redirect(url_for('admin.subjects'))
    except Exception as e:
        current_app.logger.error(f"Error deleting subject: {str(e)}")
        flash('Failed to delete subject', 'error')
        return redirect(url_for('admin.subjects'))

@admin.route('/change_password', methods=['POST'])
@login_required
@admin_required
def change_password():
    """Change a user's password."""
    try:
        user_id = request.form.get('user_id')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not all([user_id, new_password, confirm_password]):
            flash('All fields are required', 'error')
            return redirect(url_for('admin.users'))

        # Check if passwords match
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('admin.users'))

        # Validate password
        is_valid, error_msg = validate_password(new_password)
        if not is_valid:
            flash(error_msg, 'error')
            return redirect(url_for('admin.users'))

        # Load users
        users_data = load_data('users.json')
        users = users_data.get('users', [])

        # Find and update user's password
        user_updated = False
        for user in users:
            if user['id'] == user_id:
                user['password'] = generate_password_hash(new_password)
                user_updated = True
                break

        if not user_updated:
            flash('User not found', 'error')
            return redirect(url_for('admin.users'))

        if save_data('users.json', {'users': users}):
            flash('Password changed successfully', 'success')
        else:
            flash('Failed to change password', 'error')

        return redirect(url_for('admin.users'))
    except Exception as e:
        current_app.logger.error(f"Error changing password: {str(e)}")
        flash('Failed to change password', 'error')
        return redirect(url_for('admin.users'))

@admin.route('/subjects/<subject_id>/sections')
@login_required
@admin_required
def manage_sections(subject_id):
    """Manage sections for a subject."""
    try:
        subject = load_subject_by_id(subject_id)
        if not subject:
            flash('Subject not found', 'error')
            return redirect(url_for('admin.subjects'))
        
        sections = subject.get('sections', [])
        return render_template('admin/manage_sections.html', 
                             subject=subject, 
                             sections=sections)
    except Exception as e:
        logger.error(f'Error loading sections: {str(e)}')
        flash('Error loading sections', 'error')
        return redirect(url_for('admin.subjects'))

@admin.route('/subjects/<subject_id>/sections/add', methods=['POST'])
@login_required
@admin_required
def add_section(subject_id):
    """Add a new section to a subject."""
    try:
        subject = load_subject_by_id(subject_id)
        if not subject:
            flash('Subject not found', 'error')
            return redirect(url_for('admin.subjects'))
        
        name = request.form.get('name')
        description = request.form.get('description')
        order = int(request.form.get('order', 1))
        
        if not name or not description:
            flash('Name and description are required', 'error')
            return redirect(url_for('admin.manage_sections', subject_id=subject_id))
        
        new_section = {
            'id': str(uuid.uuid4()),
            'name': name,
            'description': description,
            'order': order,
            'topics': [],
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        if 'sections' not in subject:
            subject['sections'] = []
        subject['sections'].append(new_section)
        
        if save_subject(subject):
            flash('Section added successfully', 'success')
        else:
            flash('Failed to add section', 'error')
        
        return redirect(url_for('admin.manage_sections', subject_id=subject_id))
    except Exception as e:
        logger.error(f'Error adding section: {str(e)}')
        flash('Error adding section', 'error')
        return redirect(url_for('admin.manage_sections', subject_id=subject_id))

@admin.route('/subjects/<subject_id>/sections/<section_id>', methods=['POST'])
@login_required
@admin_required
def edit_section(subject_id, section_id):
    """Edit a section."""
    try:
        subject = load_subject_by_id(subject_id)
        if not subject:
            flash('Subject not found', 'error')
            return redirect(url_for('admin.subjects'))
        
        sections = subject.get('sections', [])
        section = next((s for s in sections if s['id'] == section_id), None)
        if not section:
            flash('Section not found', 'error')
            return redirect(url_for('admin.manage_sections', subject_id=subject_id))
        
        name = request.form.get('name')
        description = request.form.get('description')
        order = int(request.form.get('order', section['order']))
        
        if not name or not description:
            flash('Name and description are required', 'error')
            return redirect(url_for('admin.manage_sections', subject_id=subject_id))
        
        section.update({
            'name': name,
            'description': description,
            'order': order,
            'updated_at': datetime.utcnow().isoformat()
        })
        
        if save_subject(subject):
            flash('Section updated successfully', 'success')
        else:
            flash('Failed to update section', 'error')
        
        return redirect(url_for('admin.manage_sections', subject_id=subject_id))
    except Exception as e:
        logger.error(f'Error updating section: {str(e)}')
        flash('Error updating section', 'error')
        return redirect(url_for('admin.manage_sections', subject_id=subject_id))

@admin.route('/subjects/<subject_id>/sections/<section_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_section(subject_id, section_id):
    """Delete a section."""
    try:
        subject = load_subject_by_id(subject_id)
        if not subject:
            flash('Subject not found', 'error')
            return redirect(url_for('admin.subjects'))
        
        sections = subject.get('sections', [])
        section = next((s for s in sections if s['id'] == section_id), None)
        if not section:
            flash('Section not found', 'error')
            return redirect(url_for('admin.manage_sections', subject_id=subject_id))
        
        subject['sections'] = [s for s in sections if s['id'] != section_id]
        
        if save_subject(subject):
            flash('Section deleted successfully', 'success')
        else:
            flash('Failed to delete section', 'error')
        
        return redirect(url_for('admin.manage_sections', subject_id=subject_id))
    except Exception as e:
        logger.error(f'Error deleting section: {str(e)}')
        flash('Error deleting section', 'error')
        return redirect(url_for('admin.manage_sections', subject_id=subject_id))

@admin.route('/subjects/<subject_id>/sections/<section_id>/topics')
@login_required
@admin_required
def manage_topics(subject_id, section_id):
    """Manage topics for a section."""
    try:
        subject = load_subject_by_id(subject_id)
        if not subject:
            flash('Subject not found', 'error')
            return redirect(url_for('admin.subjects'))
        
        section = next((s for s in subject.get('sections', []) if s['id'] == section_id), None)
        if not section:
            flash('Section not found', 'error')
            return redirect(url_for('admin.manage_sections', subject_id=subject_id))
        
        topics = section.get('topics', [])
        return render_template('admin/manage_topics.html',
                             subject=subject,
                             section=section,
                             topics=topics)
    except Exception as e:
        logger.error(f'Error loading topics: {str(e)}')
        flash('Error loading topics', 'error')
        return redirect(url_for('admin.manage_sections', subject_id=subject_id))

@admin.route('/subjects/<subject_id>/sections/<section_id>/topics/add', methods=['POST'])
@login_required
@admin_required
def add_topic(subject_id, section_id):
    """Add a new topic to a section."""
    try:
        subject = load_subject_by_id(subject_id)
        if not subject:
            flash('Subject not found', 'error')
            return redirect(url_for('admin.subjects'))
        
        sections = subject.get('sections', [])
        section = next((s for s in sections if s['id'] == section_id), None)
        if not section:
            flash('Section not found', 'error')
            return redirect(url_for('admin.manage_sections', subject_id=subject_id))
        
        name = request.form.get('name')
        description = request.form.get('description')
        order = int(request.form.get('order', 1))
        
        if not name or not description:
            flash('Name and description are required', 'error')
            return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))
        
        new_topic = {
            'id': str(uuid.uuid4()),
            'name': name,
            'description': description,
            'content_type': 'mixed',  # Default to mixed since we support multiple content types
            'order': order,
            'content_blocks': [],  # Initialize empty content blocks array
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        if 'topics' not in section:
            section['topics'] = []
        section['topics'].append(new_topic)
        
        if save_subject(subject):
            flash('Topic added successfully', 'success')
        else:
            flash('Failed to add topic', 'error')
        
        return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))
    except Exception as e:
        logger.error(f'Error adding topic: {str(e)}')
        flash('Error adding topic', 'error')
        return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))

def convert_block_value(old_type, new_type, value):
    """Convert block value from one type to another."""
    try:
        # If value is a string and new type expects JSON
        if isinstance(value, str) and new_type in ['table', 'image']:
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                # If string can't be parsed as JSON, create default structure
                if new_type == 'table':
                    value = {
                        'headers': ['Column 1', 'Column 2'],
                        'rows': [['Data', value[:100]]]  # Use old value as data
                    }
                elif new_type == 'image':
                    value = {
                        'url': '',
                        'caption': value[:100],  # Use old value as caption
                        'alt_text': value[:100]  # Use old value as alt text
                    }
        
        # If value is JSON and new type expects string
        elif isinstance(value, dict) and new_type in ['text', 'code']:
            if old_type == 'table':
                # Convert table to text representation
                headers = ' | '.join(value.get('headers', []))
                rows = [' | '.join(row) for row in value.get('rows', [])]
                value = headers + '\n' + '\n'.join(rows)
            elif old_type == 'image':
                # Convert image to text representation
                value = f"Image: {value.get('caption', '')}\nURL: {value.get('url', '')}"
        
        return value
    except Exception as e:
        logger.error(f'Error converting block value: {str(e)}')
        return value

@admin.route('/subjects/<subject_id>/sections/<section_id>/topics/<topic_id>/content/<block_id>', methods=['POST'])
@login_required
@admin_required
def edit_content_block(subject_id, section_id, topic_id, block_id):
    """Edit a content block."""
    try:
        subject = load_subject_by_id(subject_id)
        if not subject:
            flash('Subject not found', 'error')
            return redirect(url_for('admin.subjects'))
        
        section = next((s for s in subject.get('sections', []) if s['id'] == section_id), None)
        if not section:
            flash('Section not found', 'error')
            return redirect(url_for('admin.manage_sections', subject_id=subject_id))
        
        topic = next((t for t in section.get('topics', []) if t['id'] == topic_id), None)
        if not topic:
            flash('Topic not found', 'error')
            return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))
        
        block = next((b for b in topic.get('content_blocks', []) if b['id'] == block_id), None)
        if not block:
            flash('Content block not found', 'error')
            return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))
        
        block_type = request.form.get('type')
        block_value = request.form.get('value')
        
        if not block_type or not block_value:
            flash('Type and value are required', 'error')
            return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))
        
        # Validate block type
        if block_type not in ['text', 'code', 'image', 'table']:
            flash('Invalid content type', 'error')
            return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))
        
        # Handle type conversion
        if block_type != block['type']:
            block_value = convert_block_value(block['type'], block_type, block_value)
        
        # Handle table and image types which expect JSON objects
        if block_type in ['table', 'image']:
            try:
                if isinstance(block_value, str):
                    block_value = json.loads(block_value)
                
                # Validate structure
                if block_type == 'table' and not all(key in block_value for key in ['headers', 'rows']):
                    raise ValueError('Invalid table structure')
                elif block_type == 'image' and not all(key in block_value for key in ['url', 'caption', 'alt_text']):
                    raise ValueError('Invalid image structure')
                    
            except (json.JSONDecodeError, ValueError) as e:
                flash('Invalid format for content type', 'error')
                return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))
        
        # Update the block
        block['type'] = block_type
        block['value'] = block_value
        block['updated_at'] = datetime.utcnow().isoformat()
        topic['updated_at'] = datetime.utcnow().isoformat()
        
        if save_subject(subject):
            flash('Content block updated successfully', 'success')
        else:
            flash('Failed to update content block', 'error')
        
        return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))
    except Exception as e:
        logger.error(f'Error updating content block: {str(e)}')
        flash('Error updating content block', 'error')
        return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))

@admin.route('/subjects/<subject_id>/sections/<section_id>/topics/<topic_id>/content/<block_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_content_block(subject_id, section_id, topic_id, block_id):
    """Delete a content block."""
    try:
        subject = load_subject_by_id(subject_id)
        if not subject:
            flash('Subject not found', 'error')
            return redirect(url_for('admin.subjects'))
        
        section = next((s for s in subject.get('sections', []) if s['id'] == section_id), None)
        if not section:
            flash('Section not found', 'error')
            return redirect(url_for('admin.manage_sections', subject_id=subject_id))
        
        topic = next((t for t in section.get('topics', []) if t['id'] == topic_id), None)
        if not topic:
            flash('Topic not found', 'error')
            return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))
        
        # Remove the content block
        topic['content_blocks'] = [b for b in topic.get('content_blocks', []) if b['id'] != block_id]
        topic['updated_at'] = datetime.utcnow().isoformat()
        
        if save_subject(subject):
            flash('Content block deleted successfully', 'success')
        else:
            flash('Failed to delete content block', 'error')
        
        return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))
    except Exception as e:
        logger.error(f'Error deleting content block: {str(e)}')
        flash('Error deleting content block', 'error')
        return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))

@admin.route('/subjects/<subject_id>/sections/<section_id>/topics/<topic_id>', methods=['POST'])
@login_required
@admin_required
def edit_topic(subject_id, section_id, topic_id):
    """Edit a topic."""
    try:
        subject = load_subject_by_id(subject_id)
        if not subject:
            flash('Subject not found', 'error')
            return redirect(url_for('admin.subjects'))
        
        sections = subject.get('sections', [])
        section = next((s for s in sections if s['id'] == section_id), None)
        if not section:
            flash('Section not found', 'error')
            return redirect(url_for('admin.manage_sections', subject_id=subject_id))
        
        topics = section.get('topics', [])
        topic = next((t for t in topics if t['id'] == topic_id), None)
        if not topic:
            flash('Topic not found', 'error')
            return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))
        
        name = request.form.get('name')
        description = request.form.get('description')
        content_type = request.form.get('content_type')
        order = int(request.form.get('order', topic['order']))
        
        if not all([name, description, content_type]):
            flash('All fields are required', 'error')
            return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))
        
        topic.update({
            'name': name,
            'description': description,
            'content_type': content_type,
            'order': order,
            'updated_at': datetime.utcnow().isoformat()
        })
        
        if save_subject(subject):
            flash('Topic updated successfully', 'success')
        else:
            flash('Failed to update topic', 'error')
        
        return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))
    except Exception as e:
        logger.error(f'Error updating topic: {str(e)}')
        flash('Error updating topic', 'error')
        return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))

@admin.route('/subjects/<subject_id>/sections/<section_id>/topics/<topic_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_topic(subject_id, section_id, topic_id):
    """Delete a topic."""
    try:
        subject = load_subject_by_id(subject_id)
        if not subject:
            flash('Subject not found', 'error')
            return redirect(url_for('admin.subjects'))
        
        sections = subject.get('sections', [])
        section = next((s for s in sections if s['id'] == section_id), None)
        if not section:
            flash('Section not found', 'error')
            return redirect(url_for('admin.manage_sections', subject_id=subject_id))
        
        topics = section.get('topics', [])
        topic = next((t for t in topics if t['id'] == topic_id), None)
        if not topic:
            flash('Topic not found', 'error')
            return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))
        
        section['topics'] = [t for t in topics if t['id'] != topic_id]
        
        if save_subject(subject):
            flash('Topic deleted successfully', 'success')
        else:
            flash('Failed to delete topic', 'error')
        
        return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))
    except Exception as e:
        logger.error(f'Error deleting topic: {str(e)}')
        flash('Error deleting topic', 'error')
        return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id)) 