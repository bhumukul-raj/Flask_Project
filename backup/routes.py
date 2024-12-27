"""
Routes Module

This module contains all the routes for the application.
"""

from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    request, current_app, abort, jsonify
)
from flask_login import (
    login_user, logout_user, login_required,
    current_user
)
from werkzeug.security import check_password_hash, generate_password_hash
import uuid
from datetime import datetime

from app.services.data_service import load_data, save_data
from app.utils.validators import validate_password, validate_email
from app.models import User
from app.forms.auth_forms import LoginForm, RegistrationForm
from app.services.session_service import track_session

# Create blueprints
auth = Blueprint('auth', __name__)
main = Blueprint('main', __name__)