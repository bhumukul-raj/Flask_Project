"""
Authentication routes for the application.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from ..services.data_service import load_data, save_data
from ..models import User
from ..forms.auth_forms import LoginForm, RegistrationForm
import uuid
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        users_data = load_data('users.json')
        user_data = next(
            (user for user in users_data.get('users', []) if user['username'] == form.username.data),
            None
        )
        
        if user_data and check_password_hash(user_data['password'], form.password.data):
            user = User(user_data)
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
            
        flash('Invalid username or password', 'error')
        
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    """Logout user."""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Register page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        users_data = load_data('users.json')
        users = users_data.get('users', [])
        
        # Check if username exists
        if any(user['username'] == form.username.data for user in users):
            flash('Username already exists', 'error')
            return render_template('auth/register.html', form=form)
            
        # Create new user
        new_user = {
            'id': str(uuid.uuid4()),
            'username': form.username.data,
            'email': form.email.data,
            'password': generate_password_hash(form.password.data),
            'role': 'user',
            'created_at': datetime.utcnow().isoformat(),
            'last_login': None
        }
        
        users.append(new_user)
        if save_data('users.json', {'users': users}):
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Error creating account', 'error')
            
    return render_template('auth/register.html', form=form)

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