"""Development configuration."""

import os
from datetime import timedelta

# Debug mode
DEBUG = True

# Secret key for session management
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# JWT configuration
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
JWT_COOKIE_SECURE = False  # Set to True in production
JWT_COOKIE_CSRF_PROTECT = True
JWT_COOKIE_SAMESITE = 'Lax'

# Security headers
TALISMAN_FORCE_HTTPS = False  # Set to True in production

# Rate limiting
RATELIMIT_DEFAULT = "200 per day;50 per hour"
RATELIMIT_STORAGE_URL = "memory://"  # Use Redis in production

# Session configuration
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # Set to True in production
PERMANENT_SESSION_LIFETIME = timedelta(days=7)

# CSRF protection
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY', 'csrf-secret-key-change-in-production') 