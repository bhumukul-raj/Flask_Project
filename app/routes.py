"""
Routes Module

This module defines all web routes for the application.
"""

import uuid
from datetime import datetime, UTC
from flask import Blueprint, jsonify, request, current_app, render_template, redirect, url_for, flash
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt,
    set_access_cookies, unset_jwt_cookies
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .services.data_service import load_data, save_data
from .utils.validators import validate_username, validate_password
from .models import User
import re
from functools import wraps
import time

auth = Blueprint('auth', __name__, url_prefix='/auth')
main = Blueprint('main', __name__)

# Simple in-memory rate limiting (should use Redis in production)
login_attempts = {}
MAX_ATTEMPTS = 20  # Increased for development
ATTEMPT_WINDOW = 60  # Reduced to 1 minute for development

def rate_limit(max_attempts: int, window: int):
    """Rate limiting decorator."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = request.remote_addr
            current_time = time.time()
            
            # Clean up old attempts
            login_attempts.update({
                k: v for k, v in login_attempts.items()
                if current_time - v['timestamp'] < window
            })
            
            # Check attempts for this IP
            if ip in login_attempts:
                attempts = login_attempts[ip]
                if attempts['count'] >= max_attempts:
                    return jsonify({
                        'error': 'Too many attempts. Please try again later.'
                    }), 429
                attempts['count'] += 1
            else:
                login_attempts[ip] = {
                    'count': 1,
                    'timestamp': current_time
                }
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@main.route('/')
def home():
    """Home page."""
    subjects_data = load_data('subject_database.json')
    featured_subjects = subjects_data.get('subjects', [])[:3]  # Get first 3 subjects as featured
    return render_template('public/home.html', featured_subjects=featured_subjects)

@main.route('/subjects')
def subjects():
    """List all subjects."""
    subjects_data = load_data('subject_database.json')
    subjects = subjects_data.get('subjects', [])
    return render_template('public/index.html', subjects=subjects)

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

@auth.route('/register', methods=['GET', 'POST'])
@rate_limit(MAX_ATTEMPTS, ATTEMPT_WINDOW)
def register():
    """Register a new user."""
    if request.method == 'GET':
        return render_template('auth/register.html')
        
    try:
        data = request.form
        if not data:
            flash('Missing form data', 'error')
            return redirect(url_for('auth.register'))
            
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return redirect(url_for('auth.register'))
            
        # Validate username
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            flash(error_msg, 'error')
            return redirect(url_for('auth.register'))
            
        # Validate password
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            flash(error_msg, 'error')
            return redirect(url_for('auth.register'))
            
        # Load existing users
        users_data = load_data('users.json')
        users = users_data.get('users', [])
        
        # Check if username exists (case-insensitive)
        if any(user.get('username', '').lower() == username.lower() for user in users):
            flash('Username already exists', 'error')
            return redirect(url_for('auth.register'))
            
        # Create new user
        user_data = {
            'id': str(uuid.uuid4()),
            'username': username,
            'password': generate_password_hash(password),
            'role': 'user',  # Default role
            'created_at': datetime.now(UTC).isoformat(),
            'last_login': None
        }
        
        # Create User object
        user = User(user_data)
        
        users.append(user.to_dict())
        if not save_data('users.json', {'users': users}):
            flash('Registration failed', 'error')
            return redirect(url_for('auth.register'))
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        current_app.logger.error(f"Error in registration: {str(e)}")
        flash('Registration failed', 'error')
        return redirect(url_for('auth.register'))

@auth.route('/login', methods=['GET', 'POST'])
@rate_limit(MAX_ATTEMPTS, ATTEMPT_WINDOW)
def login():
    """Log in a user."""
    if request.method == 'GET':
        return render_template('auth/login.html')
        
    try:
        data = request.form
        if not data:
            current_app.logger.debug("Missing form data")
            flash('Missing form data', 'error')
            return redirect(url_for('auth.login'))
            
        username = data.get('username')
        password = data.get('password')
        
        current_app.logger.debug(f"Login attempt - Username: {username}, Password length: {len(password) if password else 0}")
        
        if not username or not password:
            current_app.logger.debug("Username or password missing")
            flash('Username and password are required', 'error')
            return redirect(url_for('auth.login'))
            
        # Load users
        users_data = load_data('users.json')
        users = users_data.get('users', [])
        
        current_app.logger.debug(f"Loaded users count: {len(users)}")
        
        # Find user by username (case-insensitive)
        user_data = next(
            (u for u in users if u.get('username', '').lower() == username.lower()),
            None
        )
        
        current_app.logger.debug(f"Found user data: {user_data}")
        
        if not user_data:
            current_app.logger.debug("User not found")
            flash('Invalid credentials', 'error')
            return redirect(url_for('auth.login'))

        # Create User object
        user = User(user_data)
        
        # Verify password
        current_app.logger.debug("Verifying password...")
        current_app.logger.debug(f"Stored hash: {user_data['password']}")
        current_app.logger.debug(f"Input password: {password}")
        is_valid = check_password_hash(user_data['password'], password)
        current_app.logger.debug(f"Password valid: {is_valid}")
        
        if not is_valid:
            current_app.logger.debug("Invalid password")
            flash('Invalid credentials', 'error')
            return redirect(url_for('auth.login'))
            
        # Login the user
        login_user(user)
        current_app.logger.debug("User logged in successfully")
            
        # Update last login time
        user_data['last_login'] = datetime.now(UTC).isoformat()
        if not save_data('users.json', {'users': users}):
            current_app.logger.debug("Failed to save last login time")
            flash('Login failed', 'error')
            return redirect(url_for('auth.login'))
        
        flash('Login successful!', 'success')
        # Redirect admin users to admin dashboard, regular users to user dashboard
        if user.is_admin():
            return redirect(url_for('main.dashboard'))
        else:
            return redirect(url_for('main.dashboard'))
        
    except Exception as e:
        current_app.logger.error(f"Error in login: {str(e)}")
        flash('Login failed', 'error')
        return redirect(url_for('auth.login'))

@auth.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    try:
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        
        response = jsonify({'access_token': access_token})
        set_access_cookies(response, access_token)
        
        return response, 200
    except Exception as e:
        current_app.logger.error(f"Error in token refresh: {str(e)}")
        return jsonify({'error': 'Token refresh failed'}), 500

@auth.route('/logout')
@login_required
def logout():
    """Log out a user."""
    try:
        # Add token to blocklist if present
        jwt = get_jwt()
        if jwt:
            current_app.revoked_tokens.add(jwt["jti"])
        
        # Log out the user
        logout_user()
        
        response = redirect(url_for('main.home'))
        unset_jwt_cookies(response)
        flash('Logged out successfully', 'success')
        return response
    except Exception as e:
        current_app.logger.error(f"Error in logout: {str(e)}")
        flash('Logout failed', 'error')
        return redirect(url_for('main.home'))

@main.route('/dashboard')
@login_required
def dashboard():
    """User dashboard."""
    return render_template('dashboard.html')

@auth.route('/generate_hash/<password>')
def generate_hash(password):
    """Temporary route to generate password hash."""
    hashed = generate_password_hash(password)
    return jsonify({'hash': hashed})