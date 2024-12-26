"""
Application initialization module.
"""

import os
from flask import Flask, request, session
from flask_jwt_extended import JWTManager
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, user_loaded_from_request
from flask_wtf.csrf import CSRFProtect
from config.config import config
from .services.data_service import load_data
from .services.session_service import track_session
from .models import User
from .error_handlers import register_error_handlers
import uuid

jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
login_manager = LoginManager()
csrf = CSRFProtect()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

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
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    app = Flask(__name__, template_folder=template_dir)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    jwt.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Security headers
    csp = app.config.get('TALISMAN_CONTENT_SECURITY_POLICY', {})
    Talisman(app, 
             content_security_policy=csp,
             force_https=app.config.get('TALISMAN_FORCE_HTTPS', True))
    
    # Register blueprints
    from .routes import auth, main
    from .admin import admin
    from .api import api
    
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(admin)
    app.register_blueprint(api)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Ensure required directories exist
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)
    log_dir = os.path.dirname(app.config['LOG_FILE'])
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    @app.before_request
    def before_request():
        """Set up session tracking before each request."""
        if not session.get('_id'):
            session['_id'] = str(uuid.uuid4())
        session['ip_address'] = request.remote_addr
        track_session()

    @user_loaded_from_request.connect
    def on_user_loaded(sender, user):
        """Track session when user is loaded."""
        track_session()
    
    return app