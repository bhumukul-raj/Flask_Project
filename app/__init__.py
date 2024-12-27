"""
Application initialization module.
"""

import os
from datetime import datetime, timedelta
from flask import Flask, request, session, redirect, url_for, flash
from flask_jwt_extended import JWTManager
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, user_loaded_from_request, current_user
from flask_wtf.csrf import CSRFProtect
from config.config import config
from .services.data_service import load_data
from .services.session_service import track_session
from .models import User
from .error_handlers import register_error_handlers
from .routes import init_app as init_routes
import uuid
import logging
from logging.handlers import RotatingFileHandler
import sys

jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
login_manager = LoginManager()
csrf = CSRFProtect()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def setup_logging(app):
    """Set up logging configuration."""
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(app.config['LOG_FILE'])
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, mode=0o755, exist_ok=True)

    # Set logging level
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    
    # Create formatter
    formatter = logging.Formatter(app.config.get(
        'LOG_FORMAT',
        '%(asctime)s [%(levelname)s] %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    # File handler
    file_handler = RotatingFileHandler(
        app.config['LOG_FILE'],
        maxBytes=10485760,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Remove existing handlers to avoid duplicates
    app.logger.handlers = []
    
    # Add handlers
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)
    
    # Set Flask logger as the main logger
    logging.getLogger('werkzeug').handlers = app.logger.handlers
    logging.getLogger('flask_login').handlers = app.logger.handlers
    
    # Log application startup
    app.logger.info(f'Application startup in {app.config["ENV"]} mode')
    app.logger.info(f'Logging to: {app.config["LOG_FILE"]}')

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    users_data = load_data('users.json')
    user_data = next(
        (user for user in users_data.get('users', []) if user['id'] == user_id),
        None
    )
    return User(user_data) if user_data else None

def create_app(config_name='development'):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    jwt.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Setup secure headers
    Talisman(app, content_security_policy=app.config.get('CSP', {}))
    
    # Setup logging
    setup_logging(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Initialize routes
    init_routes(app)
    
    # Register template filters
    from .utils.filters import format_datetime
    app.jinja_env.filters['datetime'] = format_datetime
    
    # Ensure secret key is set
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.urandom(32)
    
    # Set session configuration
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
    app.config['SESSION_COOKIE_SECURE'] = False if app.config['ENV'] == 'development' else True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Ensure required directories exist
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)
    
    def is_session_valid():
        """Check if the current session is valid and not expired."""
        if not current_user.is_authenticated:
            return True  # Don't validate session for unauthenticated users
            
        if '_id' not in session:
            return False
        
        last_activity = session.get('last_activity')
        if last_activity is None:
            return True  # New session
        
        try:
            if isinstance(last_activity, str):
                last_activity = datetime.fromisoformat(last_activity)
            session_timeout = app.config.get('PERMANENT_SESSION_LIFETIME', timedelta(days=1))
            return datetime.utcnow() - last_activity < session_timeout
        except (ValueError, TypeError):
            return True  # If there's any error parsing the timestamp, assume session is valid
    
    def update_session_activity():
        """Update the last activity timestamp for the session."""
        if current_user.is_authenticated:
            session['last_activity'] = datetime.utcnow().isoformat()
            session.permanent = True
    
    @app.before_request
    def before_request():
        """Set up session tracking and validation before each request."""
        # Skip session validation for static files and public endpoints
        if request.endpoint and (
            'static' in request.endpoint or
            request.endpoint.startswith(('auth.', 'main.')) or
            request.endpoint in ['auth.login', 'auth.logout', 'auth.register']
        ):
            return

        # Initialize session for authenticated users
        if current_user.is_authenticated and not session.get('_id'):
            session.permanent = True
            session['_id'] = str(uuid.uuid4())
            session['created_at'] = datetime.utcnow().isoformat()
            update_session_activity()
        
        # Validate session
        if not is_session_valid():
            session.clear()
            flash('Your session has expired. Please log in again.', 'warning')
            return redirect(url_for('auth.login', next=request.full_path))
        
        update_session_activity()

    @user_loaded_from_request.connect
    def on_user_loaded(sender, user):
        """Track session when user is loaded."""
        if user:
            update_session_activity()
        track_session()
    
    @app.context_processor
    def utility_processor():
        """Add utility functions and variables to template context."""
        return {
            'now': datetime.now()
        }
    
    return app