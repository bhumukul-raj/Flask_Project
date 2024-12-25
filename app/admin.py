"""
Admin Module

This module handles all admin-related routes and functionality.
"""

import uuid
from datetime import datetime, UTC
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from .services.data_service import load_data, save_data
from .utils.validators import validate_username, validate_password
import json

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to check if user is an admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard."""
    # Load data for dashboard
    users_data = load_data('users.json')
    subjects_data = load_data('subject_database.json')
    
    # Calculate statistics
    user_count = len(users_data.get('users', []))
    subject_count = len(subjects_data.get('subjects', []))
    active_sessions = 1  # This should be implemented with proper session tracking
    
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
    
    return render_template('admin/admin_dashboard.html',
                         user_count=user_count,
                         subject_count=subject_count,
                         active_sessions=active_sessions,
                         recent_activities=recent_activities)

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
@admin_required
def manage_sections(subject_id):
    subject = load_subject_by_id(subject_id)
    if not subject:
        flash('Subject not found.', 'danger')
        return redirect(url_for('admin.subjects'))
    
    sections = subject.get('sections', [])
    return render_template('admin/manage_sections.html', subject=subject, sections=sections)

@admin.route('/subjects/<subject_id>/sections/add', methods=['POST'])
@admin_required
def add_section(subject_id):
    subject = load_subject_by_id(subject_id)
    if not subject:
        flash('Subject not found.', 'danger')
        return redirect(url_for('admin.subjects'))
    
    name = request.form.get('name')
    description = request.form.get('description')
    order = int(request.form.get('order', 1))
    
    if not name or not description:
        flash('Name and description are required.', 'danger')
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
    save_subject(subject)
    
    flash('Section added successfully.', 'success')
    return redirect(url_for('admin.manage_sections', subject_id=subject_id))

@admin.route('/subjects/<subject_id>/sections/<section_id>', methods=['POST'])
@admin_required
def edit_section(subject_id, section_id):
    subject = load_subject_by_id(subject_id)
    if not subject:
        flash('Subject not found.', 'danger')
        return redirect(url_for('admin.subjects'))
    
    sections = subject.get('sections', [])
    section = next((s for s in sections if s['id'] == section_id), None)
    if not section:
        flash('Section not found.', 'danger')
        return redirect(url_for('admin.manage_sections', subject_id=subject_id))
    
    name = request.form.get('name')
    description = request.form.get('description')
    order = int(request.form.get('order', section['order']))
    
    if not name or not description:
        flash('Name and description are required.', 'danger')
        return redirect(url_for('admin.manage_sections', subject_id=subject_id))
    
    section['name'] = name
    section['description'] = description
    section['order'] = order
    section['updated_at'] = datetime.utcnow().isoformat()
    
    save_subject(subject)
    flash('Section updated successfully.', 'success')
    return redirect(url_for('admin.manage_sections', subject_id=subject_id))

@admin.route('/subjects/<subject_id>/sections/<section_id>/delete', methods=['POST'])
@admin_required
def delete_section(subject_id, section_id):
    subject = load_subject_by_id(subject_id)
    if not subject:
        flash('Subject not found.', 'danger')
        return redirect(url_for('admin.subjects'))
    
    sections = subject.get('sections', [])
    section = next((s for s in sections if s['id'] == section_id), None)
    if not section:
        flash('Section not found.', 'danger')
        return redirect(url_for('admin.manage_sections', subject_id=subject_id))
    
    subject['sections'] = [s for s in sections if s['id'] != section_id]
    save_subject(subject)
    
    flash('Section deleted successfully.', 'success')
    return redirect(url_for('admin.manage_sections', subject_id=subject_id))

@admin.route('/subjects/<subject_id>/sections/<section_id>/topics')
@admin_required
def manage_topics(subject_id, section_id):
    subject = load_subject_by_id(subject_id)
    if not subject:
        flash('Subject not found.', 'danger')
        return redirect(url_for('admin.subjects'))
    
    sections = subject.get('sections', [])
    section = next((s for s in sections if s['id'] == section_id), None)
    if not section:
        flash('Section not found.', 'danger')
        return redirect(url_for('admin.manage_sections', subject_id=subject_id))
    
    topics = section.get('topics', [])
    return render_template('admin/manage_topics.html', subject=subject, section=section, topics=topics)

@admin.route('/subjects/<subject_id>/sections/<section_id>/topics/add', methods=['POST'])
@admin_required
def add_topic(subject_id, section_id):
    subject = load_subject_by_id(subject_id)
    if not subject:
        flash('Subject not found.', 'danger')
        return redirect(url_for('admin.subjects'))
    
    sections = subject.get('sections', [])
    section = next((s for s in sections if s['id'] == section_id), None)
    if not section:
        flash('Section not found.', 'danger')
        return redirect(url_for('admin.manage_sections', subject_id=subject_id))
    
    name = request.form.get('name')
    description = request.form.get('description')
    content_type = request.form.get('content_type')
    order = int(request.form.get('order', 1))
    
    if not all([name, description, content_type]):
        flash('All fields are required.', 'danger')
        return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))
    
    new_topic = {
        'id': str(uuid.uuid4()),
        'name': name,
        'description': description,
        'content_type': content_type,
        'order': order,
        'content': '',
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    
    if 'topics' not in section:
        section['topics'] = []
    section['topics'].append(new_topic)
    save_subject(subject)
    
    flash('Topic added successfully.', 'success')
    return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))

@admin.route('/subjects/<subject_id>/sections/<section_id>/topics/<topic_id>', methods=['POST'])
@admin_required
def edit_topic(subject_id, section_id, topic_id):
    subject = load_subject_by_id(subject_id)
    if not subject:
        flash('Subject not found.', 'danger')
        return redirect(url_for('admin.subjects'))
    
    sections = subject.get('sections', [])
    section = next((s for s in sections if s['id'] == section_id), None)
    if not section:
        flash('Section not found.', 'danger')
        return redirect(url_for('admin.manage_sections', subject_id=subject_id))
    
    topics = section.get('topics', [])
    topic = next((t for t in topics if t['id'] == topic_id), None)
    if not topic:
        flash('Topic not found.', 'danger')
        return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))
    
    name = request.form.get('name')
    description = request.form.get('description')
    content_type = request.form.get('content_type')
    order = int(request.form.get('order', topic['order']))
    
    if not all([name, description, content_type]):
        flash('All fields are required.', 'danger')
        return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))
    
    topic['name'] = name
    topic['description'] = description
    topic['content_type'] = content_type
    topic['order'] = order
    topic['updated_at'] = datetime.utcnow().isoformat()
    
    save_subject(subject)
    flash('Topic updated successfully.', 'success')
    return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))

@admin.route('/subjects/<subject_id>/sections/<section_id>/topics/<topic_id>/delete', methods=['POST'])
@admin_required
def delete_topic(subject_id, section_id, topic_id):
    subject = load_subject_by_id(subject_id)
    if not subject:
        flash('Subject not found.', 'danger')
        return redirect(url_for('admin.subjects'))
    
    sections = subject.get('sections', [])
    section = next((s for s in sections if s['id'] == section_id), None)
    if not section:
        flash('Section not found.', 'danger')
        return redirect(url_for('admin.manage_sections', subject_id=subject_id))
    
    topics = section.get('topics', [])
    topic = next((t for t in topics if t['id'] == topic_id), None)
    if not topic:
        flash('Topic not found.', 'danger')
        return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))
    
    section['topics'] = [t for t in topics if t['id'] != topic_id]
    save_subject(subject)
    
    flash('Topic deleted successfully.', 'success')
    return redirect(url_for('admin.manage_topics', subject_id=subject_id, section_id=section_id))

def load_subject_by_id(subject_id):
    try:
        with open('data/subject_database.json', 'r') as f:
            data = json.load(f)
            subjects = data.get('subjects', [])
            return next((s for s in subjects if s['id'] == subject_id), None)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def save_subject(subject):
    try:
        with open('data/subject_database.json', 'r') as f:
            data = json.load(f)
            subjects = data.get('subjects', [])
        
        subject_index = next((i for i, s in enumerate(subjects) if s['id'] == subject['id']), -1)
        if subject_index >= 0:
            subjects[subject_index] = subject
        
        with open('data/subject_database.json', 'w') as f:
            json.dump({'subjects': subjects}, f, indent=4)
            
    except (FileNotFoundError, json.JSONDecodeError):
        return False
    return True 