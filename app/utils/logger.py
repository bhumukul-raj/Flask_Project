"""
Logging Configuration Module

This module sets up application-wide logging with proper formatting
and multiple handlers for different logging needs.
"""

import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from flask import has_request_context, request
from typing import Optional

class RequestFormatter(logging.Formatter):
    """Custom formatter that includes request information if available."""
    
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.method = request.method
        else:
            record.url = None
            record.remote_addr = None
            record.method = None
            
        return super().format(record)

def create_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    Create a logger instance with proper formatting and handlers.
    
    Args:
        name (str): Name of the logger
        log_file (str, optional): Path to the log file
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create formatter
    formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s - %(method)s %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if log_file:
        # Ensure logs directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # File handler with rotation by size
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Daily rotating file handler
        daily_handler = TimedRotatingFileHandler(
            log_file + '.daily',
            when='midnight',
            interval=1,
            backupCount=30
        )
        daily_handler.setFormatter(formatter)
        logger.addHandler(daily_handler)
    
    return logger

def configure_logging(app=None):
    """
    Configure application-wide logging.
    
    Args:
        app: Flask application instance (optional)
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Get log file path from config or use default
    log_file = 'logs/app.log'
    if app:
        log_file = app.config.get('LOG_FILE', log_file)
    
    # Create main application logger
    logger = create_logger('app', log_file)
    
    # Set Flask logger to use our configuration
    if app:
        app.logger.handlers = logger.handlers
        app.logger.setLevel(logger.level)
        
        # Log application startup
        app.logger.info('Application startup complete')