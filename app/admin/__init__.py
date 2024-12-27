"""
Admin Blueprint

This module contains the admin routes and functionality.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from ..services.data_service import load_data, save_data
from werkzeug.security import generate_password_hash, check_password_hash

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/')
@admin.route('/index')
@login_required
@admin_required
def index():
    """Admin dashboard index page."""
    stats = {
        'total_users': len(load_data('users.json').get('users', [])),
        'total_subjects': len(load_data('subject_database.json').get('subjects', [])),
        'total_sessions': len(load_data('sessions.json').get('sessions', []))
    }
    return render_template('admin/index.html', stats=stats)

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with session monitoring."""
    sessions = load_data('sessions.json').get('sessions', [])
    return render_template('admin/dashboard.html', sessions=sessions)

@admin.route('/users')
@login_required
@admin_required
def users():
    """User management page."""
    users_data = load_data('users.json')
    users = users_data.get('users', [])
    return render_template('admin/users.html', users=users)

@admin.route('/add_user', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """Add new user page."""
    if request.method == 'POST':
        users_data = load_data('users.json')
        users = users_data.get('users', [])
        
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = request.form.get('is_admin') == 'true'
        
        # Check if username already exists
        if any(user['username'] == username for user in users):
            flash('Username already exists', 'error')
            return redirect(url_for('admin.add_user'))
        
        # Create new user
        new_user = {
            'id': str(len(users) + 1),
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'is_admin': is_admin,
            'is_active': True
        }
        
        users.append(new_user)
        users_data['users'] = users
        save_data('users.json', users_data)
        
        flash('User added successfully', 'success')
        return redirect(url_for('admin.users'))
        
    return render_template('admin/add_user.html')

@admin.route('/edit_user/<user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user page."""
    users_data = load_data('users.json')
    user = next(
        (user for user in users_data.get('users', []) if user['id'] == user_id),
        None
    )
    
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('admin.users'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        is_admin = request.form.get('is_admin') == 'true'
        is_active = request.form.get('is_active') == 'true'
        
        # Update user data
        user.update({
            'username': username,
            'email': email,
            'is_admin': is_admin,
            'is_active': is_active
        })
        
        save_data('users.json', users_data)
        flash('User updated successfully', 'success')
        return redirect(url_for('admin.users'))
        
    return render_template('admin/edit_user.html', user=user)

@admin.route('/delete_user/<user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete user."""
    users_data = load_data('users.json')
    users = users_data.get('users', [])
    
    # Find and remove user
    users_data['users'] = [user for user in users if user['id'] != user_id]
    save_data('users.json', users_data)
    
    return jsonify({'success': True})

@admin.route('/terminate_session/<session_id>', methods=['POST'])
@login_required
@admin_required
def terminate_session(session_id):
    """Terminate user session."""
    sessions_data = load_data('sessions.json')
    sessions = sessions_data.get('sessions', [])
    
    # Find and remove session
    sessions_data['sessions'] = [s for s in sessions if s['id'] != session_id]
    save_data('sessions.json', sessions_data)
    
    return jsonify({'success': True})

@admin.route('/change_password', methods=['GET', 'POST'])
@login_required
@admin_required
def change_password():
    """Change admin password page."""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return redirect(url_for('admin.change_password'))
            
        users_data = load_data('users.json')
        user = next(
            (user for user in users_data.get('users', []) if user['id'] == current_user.id),
            None
        )
        
        if not user or not check_password_hash(user['password'], current_password):
            flash('Current password is incorrect', 'error')
            return redirect(url_for('admin.change_password'))
            
        # Update password
        user['password'] = generate_password_hash(new_password)
        save_data('users.json', users_data)
        
        flash('Password changed successfully', 'success')
        return redirect(url_for('admin.index'))
        
    return render_template('admin/change_password.html') 