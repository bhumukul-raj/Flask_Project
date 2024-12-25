"""
Application initialization module.
"""

import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from .config import config
from .services.data_service import load_data
from .models import User

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
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    app = Flask(__name__, template_folder=template_dir)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    jwt.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Security headers
    csp = {
        'default-src': "'self'",
        'img-src': "'self' data: https:",
        'script-src': "'self' 'unsafe-inline' 'unsafe-eval' https://stackpath.bootstrapcdn.com https://code.jquery.com https://cdn.jsdelivr.net",
        'style-src': "'self' 'unsafe-inline' https://stackpath.bootstrapcdn.com",
        'font-src': "'self' https://stackpath.bootstrapcdn.com",
    }
    Talisman(app, content_security_policy=csp)
    
    # Register blueprints
    from .routes import auth, main
    from .admin import admin
    
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(admin)
    
    return app