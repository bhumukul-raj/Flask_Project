"""
Test module for api.py

This module contains unit tests for the API routes and endpoints.
It verifies:
- API authentication and authorization
- Request handling and validation
- Response formatting and status codes
- Data manipulation through API endpoints
- Error handling and edge cases

The tests use Flask's test client with various fixtures to simulate
different authentication states and API requests.
"""

import pytest
from flask import Flask, session
from flask_login import FlaskLoginClient, LoginManager, login_user, logout_user
from datetime import datetime, UTC
from unittest.mock import MagicMock, patch
import os
import sys

# Add the project root to Python path to make app package importable
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

from app.models import User
from app.api import api
from tests.conftest import TEST_USERS 