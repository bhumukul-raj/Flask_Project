#!/usr/bin/env python
"""
Flask Application Runner

This script handles the initialization and running of the Flask application
with proper environment setup and configuration loading.
"""

import os
import click
from app import create_app
from dotenv import load_dotenv

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

print(f"FLASK_ENV value: '{flask_env}'")

# Create the Flask application instance
app = create_app(flask_env)

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
    click.echo(f"Starting server in {app.config['ENV']} mode...")
    click.echo(f"Server running on http://{host}:{port}")
    
    # Additional environment setup
    if app.config['ENV'] == 'development':
        os.environ['FLASK_DEBUG'] = '1'
        click.echo("Debug mode: enabled")
        click.echo("Reload on code changes: enabled")
    
    # Print useful information
    click.echo("\nAvailable routes:")
    for rule in app.url_map.iter_rules():
        click.echo(f"{rule.endpoint}: {rule.rule}")
    
    # Run the application
    app.run(host=host, port=port, use_reloader=reload)

@cli.command()
def init():
    """Initialize the application (create necessary directories and files)."""
    # Create necessary directories
    directories = [
        'logs',
        'data',
        app.config.get('UPLOAD_FOLDER', 'uploads'),
        'instance'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        click.echo(f"Created directory: {directory}")
    
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
        click.echo("Created .env file with default configuration")
    
    click.echo("\nInitialization complete! You can now run the application with:")
    click.echo("python run.py run")

if __name__ == '__main__':
    cli() 