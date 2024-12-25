"""
Configuration module for the application.
"""

import os
from datetime import timedelta

class Config:
    """Base configuration."""
    
    # Basic Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    DEBUG = False
    TESTING = False
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_COOKIE_SAMESITE = 'Strict'
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # CSRF protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY', 'csrf-secret-key')
    
    # Request size limits
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    
    # Rate limiting
    RATELIMIT_DEFAULT = "100/hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Data directory
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    # Cache settings
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = 'app.log'
    
    # Security headers
    TALISMAN_FORCE_HTTPS = True
    TALISMAN_STRICT_TRANSPORT_SECURITY = True
    TALISMAN_CONTENT_SECURITY_POLICY = {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' 'unsafe-eval' https://stackpath.bootstrapcdn.com https://code.jquery.com https://cdn.jsdelivr.net",
        'style-src': "'self' 'unsafe-inline' https://stackpath.bootstrapcdn.com",
        'font-src': "'self' https://stackpath.bootstrapcdn.com",
        'img-src': "'self' data: https:",
    }

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    ENV = 'development'
    
    # Override security settings for development
    JWT_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    TALISMAN_FORCE_HTTPS = False
    
    # More permissive rate limiting
    RATELIMIT_DEFAULT = "200/hour"
    
    # More detailed logging
    LOG_LEVEL = 'DEBUG'
    
    # Development-specific paths
    LOG_FILE = 'logs/development.log'

class TestingConfig(Config):
    """Test configuration."""
    TESTING = True
    DEBUG = True
    ENV = 'testing'
    
    # Disable security features for testing
    WTF_CSRF_ENABLED = False
    JWT_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    TALISMAN_ENABLED = False
    
    # Disable rate limiting for tests
    RATELIMIT_ENABLED = False
    
    # Use memory cache for testing
    CACHE_TYPE = 'null'
    
    # Test-specific paths
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests', 'data')
    LOG_FILE = 'logs/testing.log'

class ProductionConfig(Config):
    """Production configuration."""
    ENV = 'production'
    
    # Ensure all security features are enabled
    DEBUG = False
    TESTING = False
    
    # Use Redis for rate limiting and caching in production
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')
    
    # Stricter rate limiting
    RATELIMIT_DEFAULT = "50/hour"
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    LOG_FILE = '/var/log/app/app.log'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 