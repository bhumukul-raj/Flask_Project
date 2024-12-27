"""
Test module for routes.py

This module contains tests for the main application routes.
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
from app.routes import main
from tests.conftest import TEST_USERS 