"""
Configuration Module

This module contains configuration classes for different environments.
"""

import os
from datetime import timedelta

class Config:
    """Base configuration."""
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    TESTING = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    ENV = 'development'

class TestingConfig(Config):
    """Test configuration."""
    
    TESTING = True
    DEBUG = True
    ENV = 'testing'
    # Use temporary database for testing
    DATABASE = os.environ.get('TEST_DATABASE', ':memory:')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)

class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    ENV = 'production'
    # In production, these should be set through environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 