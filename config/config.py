"""
Flask Application Configuration

This module contains comprehensive configuration classes for different environments.
Each configuration inherits from the base Config class and overrides specific settings.
"""

import os
from datetime import timedelta

class Config:
    """Base configuration."""
    
    # Basic Flask Config
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production')
    TESTING = False
    DEBUG = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'change-this-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers', 'cookies']
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_COOKIE_SAMESITE = 'Lax'
    
    # Security Headers
    TALISMAN_FORCE_HTTPS = True
    TALISMAN_STRICT_TRANSPORT_SECURITY = True
    TALISMAN_CONTENT_SECURITY_POLICY = {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' 'unsafe-eval' https://stackpath.bootstrapcdn.com https://code.jquery.com https://cdn.jsdelivr.net",
        'style-src': "'self' 'unsafe-inline' https://stackpath.bootstrapcdn.com",
        'font-src': "'self' https://stackpath.bootstrapcdn.com",
        'img-src': "'self' data: https:",
    }
    
    # Rate Limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_HEADERS_ENABLED = True
    
    # Session Configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY', 'change-this-in-production')
    
    # Database Configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    
    # Request size limits
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    
    # Cache settings
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # Data and Upload directories
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    
    # Logging Configuration
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'app.log')


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    ENV = 'development'
    
    # Override security for development
    TALISMAN_FORCE_HTTPS = False
    SESSION_COOKIE_SECURE = False
    JWT_COOKIE_SECURE = False
    
    # Development-specific settings
    SQLALCHEMY_ECHO = True
    RATELIMIT_ENABLED = False
    LOG_LEVEL = 'DEBUG'
    CACHE_TYPE = 'simple'
    
    # Use memory for rate limiting in development
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Development log file
    LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'development.log')


class TestingConfig(Config):
    """Test configuration."""
    
    TESTING = True
    DEBUG = True
    ENV = 'testing'
    
    # Test-specific settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    RATELIMIT_ENABLED = False
    CACHE_TYPE = 'null'
    TALISMAN_ENABLED = False
    
    # Test data directory and log file
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests', 'data')
    LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'testing.log')


class ProductionConfig(Config):
    """Production configuration."""
    
    ENV = 'production'
    DEBUG = False
    
    def __init__(self):
        """Initialize production configuration and validate environment variables."""
        super().__init__()
        if os.environ.get('FLASK_ENV') == 'production':
            # Ensure these are set in production
            self.SECRET_KEY = os.environ.get('SECRET_KEY')
            self.JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
            self.WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY')
            
            if not all([self.SECRET_KEY, self.JWT_SECRET_KEY, self.WTF_CSRF_SECRET_KEY]):
                raise ValueError("Production environment requires SECRET_KEY, JWT_SECRET_KEY, and WTF_CSRF_SECRET_KEY to be set")
    
    # Production-specific settings
    RATELIMIT_DEFAULT = "50/hour"  # Stricter rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    LOG_LEVEL = 'WARNING'
    
    # Use Redis for caching in production
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')
    
    # Production database settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # Production log file
    LOG_FILE = '/var/log/app/app.log'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Debug print to see available configurations
print(f"Available configurations: {list(config.keys())}") 