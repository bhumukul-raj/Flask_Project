"""
Initialize and register all blueprints for the application.
"""

from flask import Blueprint
from .main import main
from .auth import auth
from .admin import admin

# Register all blueprints
def init_app(app):
    """Register blueprints with the app."""
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin, url_prefix='/admin') 