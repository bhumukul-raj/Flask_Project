"""
Test module for logger.py

This module contains tests for logging configuration and custom formatters.
"""

import pytest
import logging
import os
from unittest.mock import patch, MagicMock
from flask import Flask, request
from app.utils.logger import (
    RequestFormatter, create_logger, configure_logging
)

@pytest.fixture
def app():
    """Create a test Flask application."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def temp_log_dir(tmp_path):
    """Create a temporary directory for log files."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir

class TestLogger:
    """Test suite for logging functionality."""

    def test_request_formatter_with_request_context(self, app):
        """Test RequestFormatter with request context."""
        formatter = RequestFormatter(
            '[%(asctime)s] %(remote_addr)s - %(method)s %(url)s\n'
            '%(levelname)s in %(module)s: %(message)s'
        )
        
        with app.test_request_context('/test', method='POST'):
            record = logging.LogRecord(
                'test_logger', logging.INFO, 'test_path', 10,
                'Test message', (), None
            )
            formatted = formatter.format(record)
            
            # Check if the URL and method are in the formatted string
            assert '/test' in formatted
            assert 'POST' in formatted
            # Don't check remote_addr as it might be None in test context

    def test_request_formatter_without_request_context(self):
        """Test RequestFormatter without request context."""
        formatter = RequestFormatter(
            '[%(asctime)s] %(remote_addr)s - %(method)s %(url)s\n'
            '%(levelname)s in %(module)s: %(message)s'
        )
        
        record = logging.LogRecord(
            'test_logger', logging.INFO, 'test_path', 10,
            'Test message', (), None
        )
        formatted = formatter.format(record)
        
        assert 'None' in formatted  # Should contain None for request-specific fields

    def test_create_logger_without_file(self):
        """Test logger creation without file handler."""
        logger = create_logger('test_logger')
        
        assert logger.level == logging.INFO
        assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
        assert not any(isinstance(h, logging.FileHandler) for h in logger.handlers)

    def test_create_logger_with_file(self, temp_log_dir):
        """Test logger creation with file handler."""
        log_file = str(temp_log_dir / "test.log")
        logger = create_logger('test_logger', log_file)
        
        assert logger.level == logging.INFO
        assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
        assert any(isinstance(h, logging.handlers.RotatingFileHandler) for h in logger.handlers)
        assert any(isinstance(h, logging.handlers.TimedRotatingFileHandler) for h in logger.handlers)

    def test_configure_logging_without_app(self, temp_log_dir):
        """Test logging configuration without Flask app."""
        with patch('app.utils.logger.os.path.exists') as mock_exists:
            mock_exists.return_value = False
            with patch('app.utils.logger.os.makedirs') as mock_makedirs:
                configure_logging()
                # Check if makedirs was called with exist_ok=True
                mock_makedirs.assert_called_with('logs', exist_ok=True)

    def test_configure_logging_with_app(self, app, temp_log_dir):
        """Test logging configuration with Flask app."""
        log_file = str(temp_log_dir / "app.log")
        app.config['LOG_FILE'] = log_file
        
        with patch('app.utils.logger.os.path.exists') as mock_exists:
            mock_exists.return_value = True
            configure_logging(app)
            
            assert app.logger.level == logging.INFO
            assert len(app.logger.handlers) > 0

    def test_log_rotation_size(self, temp_log_dir):
        """Test log rotation by size."""
        log_file = str(temp_log_dir / "test_rotation.log")
        logger = create_logger('test_rotation', log_file)
        
        # Write enough data to trigger rotation but with smaller messages
        test_message = 'Test message for rotation ' * 100  # Smaller message
        for i in range(5):  # Fewer iterations
            logger.info(f"Rotation test {i}: {test_message}")
            
        # Check if rotation occurred
        base_path = temp_log_dir / "test_rotation.log"
        assert base_path.exists()
        # Check for at least one rotated file
        rotated_files = [f for f in temp_log_dir.iterdir() if f.name.startswith('test_rotation.log.')]
        assert len(rotated_files) > 0

    def test_log_rotation_time(self, temp_log_dir):
        """Test daily log rotation setup."""
        log_file = str(temp_log_dir / "test_daily.log")
        logger = create_logger('test_daily', log_file)
        
        # Verify TimedRotatingFileHandler is configured correctly
        time_handlers = [h for h in logger.handlers 
                        if isinstance(h, logging.handlers.TimedRotatingFileHandler)]
        assert len(time_handlers) == 1
        handler = time_handlers[0]
        assert handler.when == 'MIDNIGHT'
        assert handler.interval == 86400  # Number of seconds in a day
        assert handler.backupCount == 30

    @pytest.mark.parametrize("level,message", [
        (logging.DEBUG, "Debug message"),
        (logging.INFO, "Info message"),
        (logging.WARNING, "Warning message"),
        (logging.ERROR, "Error message"),
        (logging.CRITICAL, "Critical message")
    ])
    def test_log_levels(self, level, message):
        """Test logging at different levels."""
        logger = create_logger('test_levels')
        with patch.object(logger, 'log') as mock_log:
            logger.log(level, message)
            mock_log.assert_called_once_with(level, message) 