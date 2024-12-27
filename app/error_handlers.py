"""
Error handlers for the application.

This module contains error handlers for various HTTP error codes,
supporting both HTML and JSON responses based on the request type.
"""

from flask import render_template, jsonify, request
from werkzeug.exceptions import HTTPException
import logging
import re

logger = logging.getLogger(__name__)

def format_error_name(error_class_name):
    """Format error class name into a readable string.
    
    Example: 'BadRequest' -> 'Bad Request'
    """
    # Add space before capital letters and title case the result
    name = re.sub(r'(?<!^)(?=[A-Z])', ' ', error_class_name)
    return name.title()

def is_json_request():
    """Check if the request expects a JSON response."""
    if request.is_json:
        return True
    if request.accept_mimetypes.best == 'application/json':
        return True
    return False

def handle_error(error):
    """Generic error handler for all HTTP exceptions."""
    # Log the error
    logger.error(f"Error occurred: {error}")
    
    # Get error code and message
    code = getattr(error, 'code', 500)
    message = str(error.description if hasattr(error, 'description') else error)
    
    # Get error name
    error_name = format_error_name(error.__class__.__name__)
    
    # Return JSON response if requested
    if is_json_request():
        response = jsonify({
            'error': error_name,
            'message': message
        })
        response.status_code = code
        return response
    
    # Return HTML response
    return render_template('errors/error.html',
                         code=code,
                         message=message), code

def register_error_handlers(app):
    """Register error handlers with the Flask application."""
    # Register handler for all HTTP exceptions
    app.register_error_handler(HTTPException, handle_error)
    
    # Register handler for generic exceptions
    app.register_error_handler(Exception, handle_error) 