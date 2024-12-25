"""Testing Configuration"""

import os
from datetime import timedelta

class Config:
    # Basic Flask Config
    SECRET_KEY = 'test_secret_key'
    DEBUG = True
    TESTING = True
    
    # JWT Configuration
    JWT_SECRET_KEY = 'test_jwt_secret'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Security Headers
    TALISMAN_FORCE_HTTPS = False
    TALISMAN_ENABLED = False
    
    # Rate Limiting
    RATELIMIT_ENABLED = False
    
    # CSRF Protection
    WTF_CSRF_ENABLED = False
    
    # Session Configuration
    SESSION_COOKIE_SECURE = False
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = 'logs/testing.log'
    
    # Test Data Paths
    TEST_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests', 'data')
