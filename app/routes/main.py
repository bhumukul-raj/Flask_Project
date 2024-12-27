"""
Main routes for the application.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from ..services.data_service import load_data, save_data

main = Blueprint('main', __name__)

# Public routes
@main.route('/')
def index():
    """Landing page."""
    featured_subjects = load_data('subject_database.json').get('subjects', [])[:6]  # Get first 6 subjects
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
    subjects_data = load_data('subject_database.json')
    subjects = subjects_data.get('subjects', [])
    return render_template('public/subjects.html', subjects=subjects)

@main.route('/subject/<subject_id>')
def subject_detail(subject_id):
    """Show subject details."""
    subjects_data = load_data('subject_database.json')
    subject = next(
        (s for s in subjects_data.get('subjects', []) if s.get('id') == subject_id),
        None
    )
    if not subject:
        flash('Subject not found', 'error')
        return redirect(url_for('main.subjects'))
    return render_template('public/subject_detail.html', subject=subject)

# User dashboard routes
@main.route('/dashboard')
@login_required
def dashboard():
    """User dashboard."""
    user_data = {
        'subjects': [],  # Get user's enrolled subjects
        'progress': 0,   # Calculate user's overall progress
        'achievements': []  # Get user's achievements
    }
    return render_template('dashboard/index.html', user_data=user_data)

@main.route('/profile')
@login_required
def profile():
    """User profile page."""
    return render_template('dashboard/profile.html')

@main.route('/settings')
@login_required
def settings():
    """User settings page."""
    return render_template('dashboard/settings.html') 