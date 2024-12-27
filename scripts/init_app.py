#!/usr/bin/env python3
"""
Application initialization script.
Creates necessary directories and files for the application.
"""

import os
import sys
from pathlib import Path

def init_app():
    """Initialize the application directory structure and files."""
    # Get the root directory
    root_dir = Path(__file__).parent.parent.absolute()
    
    # Directories to create
    directories = {
        'logs': root_dir / 'logs',
        'data': root_dir / 'data',
        'uploads': root_dir / 'uploads',
        'instance': root_dir / 'instance',
    }
    
    # Create directories with proper permissions
    for name, path in directories.items():
        try:
            path.mkdir(mode=0o755, parents=True, exist_ok=True)
            print(f"✓ Created directory: {path}")
        except Exception as e:
            print(f"✗ Error creating {name} directory: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Create .env file if it doesn't exist
    env_file = root_dir / '.env'
    if not env_file.exists():
        try:
            with open(env_file, 'w') as f:
                f.write("""# Flask application environment variables
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=change-this-in-production
JWT_SECRET_KEY=change-this-in-production
WTF_CSRF_SECRET_KEY=change-this-in-production

# Database configuration
DATABASE_URL=sqlite:///app.db

# Redis configuration (if used)
# REDIS_URL=redis://localhost:6379/0

# Mail configuration (if used)
# MAIL_SERVER=smtp.gmail.com
# MAIL_PORT=587
# MAIL_USE_TLS=True
# MAIL_USERNAME=your-email@gmail.com
# MAIL_PASSWORD=your-password
""")
            print(f"✓ Created .env file: {env_file}")
        except Exception as e:
            print(f"✗ Error creating .env file: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Create empty __init__.py files in directories that need them
    init_files = [
        root_dir / 'app' / '__init__.py',
        root_dir / 'tests' / '__init__.py',
        root_dir / 'config' / '__init__.py',
    ]
    
    for init_file in init_files:
        if not init_file.parent.exists():
            init_file.parent.mkdir(parents=True, exist_ok=True)
        if not init_file.exists():
            init_file.touch()
            print(f"✓ Created file: {init_file}")
    
    print("\n✓ Application initialized successfully!")
    print("\nNext steps:")
    print("1. Edit the .env file with your configuration")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run the application: flask run")

if __name__ == '__main__':
    init_app() 