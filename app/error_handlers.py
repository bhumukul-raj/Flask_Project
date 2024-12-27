"""Error handlers for the application."""

from flask import render_template, current_app
import traceback

def register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 Bad Request errors."""
        current_app.logger.error(f'Bad Request: {error}')
        return render_template('errors/400.html', error=str(error)), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        """Handle 401 Unauthorized errors."""
        current_app.logger.error(f'Unauthorized: {error}')
        return render_template('errors/401.html', error=str(error)), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 Forbidden errors."""
        current_app.logger.error(f'Forbidden: {error}')
        return render_template('errors/403.html', error=str(error)), 403

    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors."""
        current_app.logger.error(f'Not Found: {error}')
        return render_template('errors/404.html', error=str(error)), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error."""
        error_traceback = traceback.format_exc()
        current_app.logger.error(f'Internal Error: {error}\n{error_traceback}')
        return render_template('errors/500.html', 
                             error=str(error),
                             error_details=error_traceback if app.debug else None), 500

    @app.errorhandler(Exception)
    def unhandled_exception(error):
        """Handle unhandled exceptions."""
        error_traceback = traceback.format_exc()
        current_app.logger.error(f'Unhandled Exception: {error}\n{error_traceback}')
        return render_template('errors/500.html',
                             error="An unexpected error occurred.",
                             error_details=error_traceback if app.debug else None), 500 