"""
Routes Module

This module defines all web routes for the application.
"""

import uuid
from datetime import datetime, UTC
from flask import Blueprint, jsonify, request, current_app, render_template, redirect, url_for, flash, session
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
from .services.session_service import remove_session, clear_user_sessions

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
    return render_template('public/home.html')

@main.route('/subjects')
@login_required
def subjects():
    """List all subjects. Only accessible to authenticated users."""
    subjects_data = load_data('subject_database.json')
    subjects = subjects_data.get('subjects', [])
    return render_template('public/index.html', subjects=subjects)

@main.route('/subject/<subject_id>')
@login_required
def subject_detail(subject_id):
    """Show subject details. Only accessible to authenticated users."""
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
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('auth/login.html')
        
        try:
            # Load users
            users_data = load_data('users.json')
            users = users_data.get('users', [])
            
            # Find user by username (case-insensitive)
            user_data = next(
                (u for u in users if u.get('username', '').lower() == username.lower()),
                None
            )
            
            if not user_data:
                flash('Invalid username or password', 'error')
                return render_template('auth/login.html')
            
            # Create User object and verify password
            user = User(user_data)
            if not check_password_hash(user_data['password'], password):
                flash('Invalid username or password', 'error')
                return render_template('auth/login.html')
            
            # Clear any existing sessions for this user
            clear_user_sessions(user.get_id())
            
            # Log in the user
            login_user(user, remember=remember)
            
            # Update last login time
            user_data['last_login'] = datetime.now(UTC).isoformat()
            save_data('users.json', {'users': users})
            
            # Create JWT token
            access_token = create_access_token(identity=user.get_id())
            response = redirect(url_for('main.dashboard'))
            set_access_cookies(response, access_token)
            
            flash('Login successful', 'success')
            return response
            
        except Exception as e:
            current_app.logger.error(f"Login error: {str(e)}")
            flash('An error occurred during login. Please try again.', 'error')
            return render_template('auth/login.html')
    
    return render_template('auth/login.html')

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
        # Get session ID before logging out
        session_id = session.get('_id')
        
        # Log out the user
        logout_user()
        
        # Remove session from active sessions
        if session_id:
            remove_session(session_id)
        
        # Try to get JWT token if it exists
        try:
            jwt = get_jwt()
            if jwt:
                current_app.revoked_tokens.add(jwt["jti"])
        except Exception:
            # No JWT token found, which is fine
            pass
        
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
    return render_template('dashboard/dashboard.html')