"""
Error Handlers Module

This module contains error handlers for the application.
"""

from flask import render_template, jsonify, request

def register_error_handlers(app):
    """Register error handlers for the application."""
    
    def is_json_request():
        """Check if the request expects JSON response."""
        return request.is_json or 'application/json' in request.headers.get('Accept', '')
    
    @app.errorhandler(400)
    def bad_request(e):
        if is_json_request():
            return jsonify(error='Bad Request'), 400
        return render_template('errors/error.html', 
                             error_code=400,
                             error_name='Bad Request',
                             error_description='The server could not understand the request.'), 400

    @app.errorhandler(401)
    def unauthorized(e):
        if is_json_request():
            return jsonify(error='Unauthorized'), 401
        return render_template('errors/error.html',
                             error_code=401,
                             error_name='Unauthorized',
                             error_description='Authentication is required to access this resource.'), 401

    @app.errorhandler(403)
    def forbidden(e):
        if is_json_request():
            return jsonify(error='Forbidden'), 403
        return render_template('errors/error.html',
                             error_code=403,
                             error_name='Forbidden',
                             error_description='You do not have permission to access this resource.'), 403

    @app.errorhandler(404)
    def not_found(e):
        if is_json_request():
            return jsonify(error='Not Found'), 404
        return render_template('errors/error.html',
                             error_code=404,
                             error_name='Not Found',
                             error_description='The requested resource was not found on the server.'), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        if is_json_request():
            return jsonify(error='Method Not Allowed'), 405
        return render_template('errors/error.html',
                             error_code=405,
                             error_name='Method Not Allowed',
                             error_description='The method is not allowed for the requested URL.'), 405

    @app.errorhandler(429)
    def too_many_requests(e):
        if is_json_request():
            return jsonify(error='Too Many Requests'), 429
        return render_template('errors/error.html',
                             error_code=429,
                             error_name='Too Many Requests',
                             error_description='You have made too many requests. Please try again later.'), 429

    @app.errorhandler(500)
    def internal_server_error(e):
        if is_json_request():
            return jsonify(error='Internal Server Error'), 500
        return render_template('errors/error.html',
                             error_code=500,
                             error_name='Internal Server Error',
                             error_description='An internal server error occurred.'), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        """Handle any uncaught exception."""
        app.logger.error(f"Uncaught exception: {str(e)}")
        if is_json_request():
            return jsonify(error='Internal Server Error'), 500
        return render_template('errors/error.html',
                             error_code=500,
                             error_name='Internal Server Error',
                             error_description='An unexpected error occurred.'), 500 