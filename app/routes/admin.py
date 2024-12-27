"""
Admin routes for the application.

This module handles all admin-related functionality including:
- User management (CRUD operations)
- Subject management (CRUD operations)
- Section management within subjects
- Topic management within sections
- Admin dashboard statistics
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from ..services.data_service import load_data, save_data
from ..utils.validators import validate_username, validate_password
from ..services.session_service import get_active_sessions, get_active_sessions_count, remove_session
from ..utils.decorators import role_required
import uuid
from datetime import datetime, UTC
import json
import logging

# Configure logger for admin module
logger = logging.getLogger(__name__)

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/')
@login_required
@role_required('admin')
def index():
    """Admin dashboard with statistics."""
    stats = {
        'total_users': len(load_data('users.json').get('users', [])),
        'total_subjects': len(load_data('subject_database.json').get('subjects', [])),
        'active_sessions': get_active_sessions_count()
    }
    return render_template('admin/dashboard.html', stats=stats)

# Alias dashboard to index for backward compatibility
@admin.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    """Redirect to admin index for consistency."""
    return redirect(url_for('admin.index'))

@admin.route('/users')
@login_required
@role_required('admin')
def users():
    """User management interface."""
    users_data = load_data('users.json').get('users', [])
    return render_template('admin/users.html', users=users_data)

@admin.route('/subjects')
@login_required
@role_required('admin')
def subjects():
    """Subject management interface."""
    subjects_data = load_data('subject_database.json').get('subjects', [])
    return render_template('admin/subjects.html', subjects=subjects_data)

@admin.route('/subjects/add', methods=['POST'])
@login_required
@role_required('admin')
def add_subject():
    """Add a new subject."""
    try:
        # Load existing subjects
        subjects_data = load_data('subject_database.json')
        subjects = subjects_data.get('subjects', [])

        # Create new subject
        new_subject = {
            'id': str(uuid.uuid4()),
            'name': request.form['name'],
            'description': request.form['description'],
            'category': request.form['category'],
            'level': request.form['level'],
            'is_published': request.form.get('is_published') == 'on',
            'created_at': datetime.now(UTC).isoformat(),
            'updated_at': datetime.now(UTC).isoformat(),
            'instructor_id': current_user.id,
            'sections': [],
            'enrolled_users': [],
            'requirements': [],
            'tags': []
        }

        # Handle thumbnail upload
        if 'thumbnail' in request.files:
            file = request.files['thumbnail']
            if file and file.filename:
                # TODO: Implement file upload handling
                new_subject['thumbnail'] = file.filename

        # Add to subjects list
        subjects.append(new_subject)

        # Save updated subjects
        if save_data('subject_database.json', {'subjects': subjects}):
            flash('Subject added successfully', 'success')
        else:
            flash('Error saving subject', 'error')

    except Exception as e:
        logger.error(f'Error adding subject: {str(e)}')
        flash('Error adding subject', 'error')

    return redirect(url_for('admin.subjects'))

@admin.route('/subjects/edit/<subject_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_subject(subject_id):
    """Edit an existing subject."""
    subjects_data = load_data('subject_database.json')
    subjects = subjects_data.get('subjects', [])
    subject = next((s for s in subjects if s['id'] == subject_id), None)

    if not subject:
        flash('Subject not found', 'error')
        return redirect(url_for('admin.subjects'))

    if request.method == 'POST':
        try:
            # Update subject
            subject.update({
                'name': request.form['name'],
                'description': request.form['description'],
                'category': request.form['category'],
                'level': request.form['level'],
                'is_published': request.form.get('is_published') == 'on',
                'updated_at': datetime.now(UTC).isoformat()
            })

            # Handle thumbnail upload
            if 'thumbnail' in request.files:
                file = request.files['thumbnail']
                if file and file.filename:
                    # TODO: Implement file upload handling
                    subject['thumbnail'] = file.filename

            # Save changes
            if save_data('subject_database.json', {'subjects': subjects}):
                flash('Subject updated successfully', 'success')
            else:
                flash('Error saving changes', 'error')

            return redirect(url_for('admin.subjects'))

        except Exception as e:
            logger.error(f'Error updating subject: {str(e)}')
            flash('Error updating subject', 'error')

    return render_template('admin/edit_subject.html', subject=subject)

@admin.route('/subjects/delete/<subject_id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_subject(subject_id):
    """Delete a subject."""
    try:
        subjects_data = load_data('subject_database.json')
        subjects = subjects_data.get('subjects', [])
        
        # Find and remove subject
        subject = next((s for s in subjects if s['id'] == subject_id), None)
        if subject:
            subjects.remove(subject)
            
            # Save changes
            if save_data('subject_database.json', {'subjects': subjects}):
                flash('Subject deleted successfully', 'success')
            else:
                flash('Error deleting subject', 'error')
        else:
            flash('Subject not found', 'error')

    except Exception as e:
        logger.error(f'Error deleting subject: {str(e)}')
        flash('Error deleting subject', 'error')

    return redirect(url_for('admin.subjects'))

@admin.route('/settings')
@login_required
@role_required('admin')
def settings():
    """Admin settings interface."""
    # Load admin settings from configuration or database
    admin_settings = {
        'site_name': current_app.config.get('SITE_NAME', 'Learning Platform'),
        'maintenance_mode': current_app.config.get('MAINTENANCE_MODE', False),
        'registration_enabled': current_app.config.get('REGISTRATION_ENABLED', True),
        'max_upload_size': current_app.config.get('MAX_UPLOAD_SIZE', '5MB'),
        'allowed_file_types': current_app.config.get('ALLOWED_FILE_TYPES', ['pdf', 'doc', 'docx']),
    }
    return render_template('admin/settings.html', settings=admin_settings)

@admin.route('/settings/update', methods=['POST'])
@login_required
@role_required('admin')
def update_settings():
    """Update admin settings."""
    try:
        # Update application settings
        current_app.config['SITE_NAME'] = request.form.get('site_name', 'Learning Platform')
        current_app.config['MAINTENANCE_MODE'] = request.form.get('maintenance_mode') == 'on'
        current_app.config['REGISTRATION_ENABLED'] = request.form.get('registration_enabled') == 'on'
        current_app.config['MAX_UPLOAD_SIZE'] = request.form.get('max_upload_size', '5MB')
        
        # Save settings to configuration file or database
        flash('Settings updated successfully', 'success')
    except Exception as e:
        logger.error(f'Error updating admin settings: {str(e)}')
        flash('Error updating settings', 'error')
    
    return redirect(url_for('admin.settings'))

# Add more admin routes as needed 