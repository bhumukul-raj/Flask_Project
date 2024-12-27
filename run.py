#!/usr/bin/env python
"""
Flask Application Runner

This script handles the initialization and running of the Flask application
with proper environment setup and configuration loading.
"""

import os
import click
import logging
from logging.handlers import RotatingFileHandler
from app import create_app
from dotenv import load_dotenv
from pathlib import Path

def setup_logging(app):
    """Set up logging before application starts."""
    # Ensure logs directory exists
    log_dir = os.path.dirname(app.config['LOG_FILE'])
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, mode=0o755, exist_ok=True)
    
    # Configure logging
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    # File handler
    file_handler = RotatingFileHandler(
        app.config['LOG_FILE'],
        maxBytes=10485760,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Log startup information
    app.logger.info('Application startup')
    app.logger.info(f'Environment: {app.config["ENV"]}')
    app.logger.info(f'Debug mode: {app.debug}')
    app.logger.info(f'Logging to: {app.config["LOG_FILE"]}')

try:
    # Try to load the .env file
    load_dotenv(encoding='utf-8')
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")

# Clean and set FLASK_ENV
flask_env = os.getenv('FLASK_ENV', 'development')
if flask_env:
    # Remove any comments and whitespace
    flask_env = flask_env.split('#')[0].strip()
    if not flask_env:
        flask_env = 'development'
else:
    flask_env = 'development'

# Create the Flask application instance
app = create_app(flask_env)

# Set up logging immediately after app creation
setup_logging(app)

@click.group()
def cli():
    """Flask application CLI commands."""
    pass

@cli.command()
@click.option('--host', default='127.0.0.1', help='The host to bind to.')
@click.option('--port', default=5000, help='The port to bind to.')
@click.option('--reload/--no-reload', default=True, help='Enable or disable reload on code changes.')
def run(host, port, reload):
    """Run the Flask application server."""
    app.logger.info(f"Starting server on http://{host}:{port}")
    
    # Additional environment setup
    if app.config['ENV'] == 'development':
        os.environ['FLASK_DEBUG'] = '1'
        app.logger.info("Debug mode: enabled")
        app.logger.info("Reload on code changes: enabled")
    
    # Log available routes
    app.logger.info("\nAvailable routes:")
    for rule in app.url_map.iter_rules():
        app.logger.info(f"{rule.endpoint}: {rule.rule}")
    
    # Run the application
    app.run(host=host, port=port, use_reloader=reload)

@cli.command()
def init():
    """Initialize the application (create necessary directories and files)."""
    app.logger.info("Initializing application...")
    
    # Create necessary directories
    directories = [
        'logs',
        'data',
        app.config.get('UPLOAD_FOLDER', 'uploads'),
        'instance'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        app.logger.info(f"Created directory: {directory}")
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        with open('.env', 'w', encoding='utf-8') as f:
            f.write("""# Flask Environment Variables
FLASK_ENV=development
FLASK_APP=run.py
FLASK_DEBUG=1

# Security Keys
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
WTF_CSRF_SECRET_KEY=your-csrf-secret-key-change-in-production

# Database Configuration
DATABASE_URL=sqlite:///app.db

# Redis Configuration
#REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=DEBUG""")
        app.logger.info("Created .env file with default configuration")
    
    app.logger.info("\nInitialization complete!")
    app.logger.info("You can now run the application with: python run.py run")

if __name__ == '__main__':
    cli() 