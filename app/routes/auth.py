"""
Authentication routes for the application.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from ..services.data_service import load_data, save_data
from ..models import User
import uuid
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'true'
        
        users_data = load_data('users.json')
        user_data = next(
            (user for user in users_data.get('users', []) if user['username'] == username),
            None
        )
        
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
            
        flash('Invalid username or password', 'error')
        
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    """Logout user."""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.register'))
            
        users_data = load_data('users.json')
        users = users_data.get('users', [])
        
        # Check if username already exists
        if any(user['username'] == username for user in users):
            flash('Username already exists', 'error')
            return redirect(url_for('auth.register'))
            
        # Create new user
        new_user = {
            'id': str(uuid.uuid4()),
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'is_admin': False,
            'is_active': True,
            'created_at': datetime.utcnow().isoformat()
        }
        
        users.append(new_user)
        users_data['users'] = users
        save_data('users.json', users_data)
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password page."""
    if request.method == 'POST':
        email = request.form.get('email')
        users_data = load_data('users.json')
        user = next(
            (user for user in users_data.get('users', []) if user['email'] == email),
            None
        )
        
        if user:
            # TODO: Implement password reset email functionality
            flash('Password reset instructions have been sent to your email.', 'info')
            return redirect(url_for('auth.login'))
            
        flash('Email not found', 'error')
        
    return render_template('auth/forgot_password.html') 