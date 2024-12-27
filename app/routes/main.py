"""
Main routes for the application.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from ..services.data_service import (
    load_data, save_data, get_user, get_subject, 
    get_user_achievements
)
from ..services.session_service import get_active_sessions_count
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

main = Blueprint('main', __name__)

def calculate_total_progress(subjects):
    """Calculate total progress across all enrolled subjects."""
    if not subjects:
        return 0
    total_progress = sum(
        next((e['progress'] for e in subject.get('enrolled_users', [])
              if e['user_id'] == current_user.id), 0)
        for subject in subjects
    )
    return round(total_progress / len(subjects), 1)

# Public routes
@main.route('/')
def index():
    """Landing page."""
    subjects_data = load_data('subjects/subjects.json')
    featured_subjects = subjects_data.get('subjects', [])[:6]  # Get first 6 subjects
    return render_template('public/home.html', featured_subjects=featured_subjects)

@main.route('/about')
def about():
    """About page."""
    return render_template('public/about.html')

@main.route('/terms')
def terms():
    """Terms of Service page."""
    return render_template('public/terms.html')

@main.route('/subjects')
def subjects():
    """List all subjects."""
    subjects_data = load_data('subjects/subjects.json')
    subjects = subjects_data.get('subjects', [])
    categories = subjects_data.get('categories', [])
    
    if current_user.is_authenticated:
        # Show different views based on role
        if current_user.role == 'admin':
            return render_template('subjects/admin_view.html', 
                                 subjects=subjects,
                                 categories=categories)
        else:
            # Get user's enrolled subjects
            enrolled_subject_ids = [
                subject['id'] for subject in subjects 
                if any(e['user_id'] == current_user.id 
                      for e in subject.get('enrolled_users', []))
            ]
            return render_template('subjects/student_view.html', 
                                 subjects=subjects,
                                 categories=categories,
                                 enrolled_subject_ids=enrolled_subject_ids)
    else:
        # Public view with limited information
        return render_template('public/subjects.html', 
                             subjects=subjects,
                             categories=categories)

@main.route('/subject/<subject_id>')
def subject_detail(subject_id):
    """Show subject details."""
    subject = get_subject(subject_id)
    if not subject:
        flash('Subject not found', 'error')
        return redirect(url_for('main.subjects'))
    
    # Get user's enrollment status and progress if authenticated
    user_enrollment = None
    if current_user.is_authenticated:
        user_enrollment = next(
            (e for e in subject.get('enrolled_users', [])
             if e['user_id'] == current_user.id),
            None
        )
    
    return render_template('public/subject_detail.html', 
                         subject=subject,
                         user_enrollment=user_enrollment)

# User dashboard routes
@main.route('/dashboard')
@login_required
def dashboard():
    """User dashboard."""
    user = get_user(current_user.id)
    
    if user['role'] == 'admin':
        # Admin dashboard
        users_data = load_data('users/users.json')
        subjects_data = load_data('subjects/subjects.json')
        stats = {
            'total_users': len(users_data.get('users', [])),
            'total_subjects': len(subjects_data.get('subjects', [])),
            'active_sessions': get_active_sessions_count()
        }
        return render_template('dashboard/admin_dashboard.html', stats=stats)
    else:
        # User dashboard
        subjects_data = load_data('subjects/subjects.json')
        enrolled_subjects = [
            subject for subject in subjects_data.get('subjects', [])
            if any(e['user_id'] == current_user.id for e in subject.get('enrolled_users', []))
        ]
        
        # Get user achievements
        achievements = get_user_achievements(current_user.id)
        
        user_data = {
            'subjects': enrolled_subjects,
            'progress': calculate_total_progress(enrolled_subjects),
            'achievements': achievements.get('achievements', [])
        }
        return render_template('dashboard/user_dashboard.html', user_data=user_data)

@main.route('/profile')
@login_required
def profile():
    """User profile page."""
    # Load user data
    user = get_user(current_user.id)
    
    # Get user's enrolled subjects
    subjects_data = load_data('subjects', 'subjects.json')
    enrolled_subjects = [
        subject for subject in subjects_data.get('subjects', [])
        if any(e['user_id'] == current_user.id for e in subject.get('enrolled_users', []))
    ]
    
    # Calculate user statistics
    user_stats = {
        'subjects_enrolled': len(enrolled_subjects),
        'completed_subjects': sum(1 for s in enrolled_subjects 
                                if any(e['user_id'] == current_user.id and e['progress'] == 100 
                                      for e in s.get('enrolled_users', []))),
        'in_progress_subjects': sum(1 for s in enrolled_subjects 
                                  if any(e['user_id'] == current_user.id and 0 < e['progress'] < 100 
                                        for e in s.get('enrolled_users', []))),
        'total_progress': calculate_total_progress(enrolled_subjects) if enrolled_subjects else 0,
        'join_date': user.get('created_at', 'Unknown'),
        'last_login': user.get('last_login', 'Never')
    }
    
    return render_template('dashboard/profile.html', 
                         user=user,
                         user_stats=user_stats,
                         enrolled_subjects=enrolled_subjects)

@main.route('/settings')
@login_required
def settings():
    """User settings page."""
    user = get_user(current_user.id)
    
    # Initialize settings if they don't exist
    if user and 'settings' not in user:
        user['settings'] = {
            'timezone': 'UTC',
            'notifications': {
                'email': False,
                'push': False
            }
        }
        # Save the initialized settings
        users_data = load_data('users/users.json')
        users = users_data.get('users', [])
        save_data('users/users.json', {'users': users})
    
    return render_template('dashboard/settings.html', user=user)

@main.route('/settings/account', methods=['POST'])
@login_required
def update_account_settings():
    """Update account settings."""
    try:
        timezone = request.form.get('timezone')
        email_notifications = request.form.get('email_notifications') == 'on'
        push_notifications = request.form.get('push_notifications') == 'on'
        
        # Load user data
        users_data = load_data('users/users.json')
        users = users_data.get('users', [])
        user = next((u for u in users if u['id'] == current_user.id), None)
        
        if user:
            # Update user settings
            user['settings'] = user.get('settings', {})
            user['settings'].update({
                'timezone': timezone,
                'notifications': {
                    'email': email_notifications,
                    'push': push_notifications
                }
            })
            
            # Save changes
            if save_data('users/users.json', {'users': users}):
                flash('Settings updated successfully', 'success')
            else:
                flash('Error saving settings', 'error')
        else:
            flash('User not found', 'error')
            
    except Exception as e:
        current_app.logger.error(f'Error updating settings: {str(e)}')
        flash('Error updating settings', 'error')
        
    return redirect(url_for('main.settings'))

@main.route('/settings/password', methods=['POST'])
@login_required
def update_password():
    """Update user password."""
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([current_password, new_password, confirm_password]):
            flash('All password fields are required', 'error')
            return redirect(url_for('main.settings'))
            
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return redirect(url_for('main.settings'))
            
        # Load user data
        users_data = load_data('users.json')
        users = users_data.get('users', [])
        user = next((u for u in users if u['id'] == current_user.id), None)
        
        if user and check_password_hash(user['password'], current_password):
            # Update password
            user['password'] = generate_password_hash(new_password)
            
            # Save changes
            if save_data('users.json', {'users': users}):
                flash('Password updated successfully', 'success')
            else:
                flash('Error updating password', 'error')
        else:
            flash('Current password is incorrect', 'error')
            
    except Exception as e:
        current_app.logger.error(f'Error updating password: {str(e)}')
        flash('Error updating password', 'error')
        
    return redirect(url_for('main.settings'))

@main.route('/settings/notifications', methods=['POST'])
@login_required
def update_notifications():
    """Update notification settings."""
    try:
        email_notifications = request.form.get('email_notifications') == 'on'
        push_notifications = request.form.get('push_notifications') == 'on'
        
        # Load user data
        users_data = load_data('users.json')
        users = users_data.get('users', [])
        user = next((u for u in users if u['id'] == current_user.id), None)
        
        if user:
            # Update notification settings
            user['settings'] = user.get('settings', {})
            user['settings']['notifications'] = {
                'email': email_notifications,
                'push': push_notifications
            }
            
            # Save changes
            if save_data('users.json', {'users': users}):
                flash('Notification settings updated', 'success')
            else:
                flash('Error saving notification settings', 'error')
        else:
            flash('User not found', 'error')
            
    except Exception as e:
        current_app.logger.error(f'Error updating notification settings: {str(e)}')
        flash('Error updating notification settings', 'error')
        
    return redirect(url_for('main.settings')) 