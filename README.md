# Flask Project - Complete Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Project Checklist](#project-checklist)
3. [Project Structure](#project-structure)
4. [Quick Start](#quick-start)
5. [Setup Guide](#setup-guide)
6. [Configuration](#configuration)
7. [User Manual](#user-manual)
8. [API Documentation](#api-documentation)
9. [Security Features](#security-features)
10. [Testing](#testing)
11. [Dependencies](#dependencies)
12. [Production Deployment](#production-deployment)

## Project Overview
This is a Flask application with a comprehensive configuration setup for different environments (development, testing, and production).

## Project Checklist

### ✅ Completed Tasks

#### Project Structure
- [x] Basic project structure setup
- [x] App package with blueprints
- [x] Services directory with auth and data services
- [x] Utils directory with helper functions
- [x] Config directory for different environments
- [x] Templates directory for HTML files
- [x] Tests directory structure
- [x] Data directory for JSON storage

#### Security Setup
- [x] JWT authentication implementation
- [x] CSRF protection
- [x] Rate limiting
- [x] Security headers with Talisman
- [x] Environment variables setup
- [x] Password hashing implementation

#### Basic Features
- [x] User authentication service
- [x] Data service for JSON operations
- [x] Basic routing setup
- [x] Index page template
- [x] Dependencies in requirements.txt

### 📝 Pending Tasks

#### Configuration
- [ ] Development configuration settings
- [ ] Production configuration settings
- [ ] Testing configuration settings

#### Templates
- [ ] Login page template
- [ ] Registration page template
- [ ] Error pages (404, 500)
- [ ] User dashboard template

#### Documentation
- [ ] API documentation
- [ ] Setup instructions
- [ ] User manual
- [ ] API endpoints documentation
- [ ] Database schema documentation

#### Testing
- [ ] Route tests
- [ ] Service tests
- [ ] Authentication tests
- [ ] Integration tests

#### Main Application
- [ ] Complete app.py implementation
- [ ] Error handlers
- [ ] Logging configuration
- [ ] Database initialization

#### Additional Features
- [ ] User profile management
- [ ] Password reset functionality
- [ ] Email verification
- [ ] Admin dashboard
- [ ] User roles and permissions
- [ ] API rate limiting rules

#### Security Enhancements
- [ ] Input validation
- [ ] Output sanitization
- [ ] Session management
- [ ] Password complexity rules
- [ ] Audit logging

#### Deployment
- [ ] Production deployment guide
- [ ] Docker configuration
- [ ] CI/CD setup
- [ ] Backup strategy
- [ ] Monitoring setup

### 🔍 Notes
- Keep track of completed items by checking them off
- Prioritize security-related tasks
- Add new items as needed
- Review and update regularly

## Project Structure
```
Flask_Project/
├── app/                    # Application package
│   ├── __init__.py        # Application factory
│   ├── admin.py           # Admin views
│   ├── api.py             # API endpoints
│   ├── error_handlers.py  # Error handling
│   ├── models.py          # Database models
│   ├── routes.py          # Main routes
│   ├── services/          # Business logic
│   └── utils/             # Utility functions
├── config/                # Configuration package
│   ├── __init__.py
│   └── config.py         # Environment configurations
├── data/                  # Application data storage
├── instance/             # Instance-specific files
├── logs/                 # Application logs
├── uploads/              # File uploads
├── .env                  # Environment variables
├── requirements.txt      # Project dependencies
└── run.py               # Application runner
```

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for version control)

### Installation Steps
1. **Clone the repository** (if using Git):
   ```bash
   git clone <repository-url>
   cd Flask_Project
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Unix/MacOS
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the Project**:
   ```bash
   python run.py init
   ```

5. **Start the Development Server**:
   ```bash
   python run.py run
   ```

### Custom Server Options
```bash
# Change host and port
python run.py run --host=0.0.0.0 --port=8000

# Disable auto-reload
python run.py run --no-reload
```

## Configuration

### Environment Setup
Create a `.env` file in the project root:

```ini
# Flask Environment Variables
FLASK_ENV=development
FLASK_APP=run.py
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
WTF_CSRF_SECRET_KEY=your-csrf-secret-key-change-in-production

# Database Configuration
DATABASE_URL=sqlite:///app.db

# Redis Configuration (for production)
# REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=DEBUG
```

### Environment Configurations

1. **Development (Default)**
   - Debug mode enabled
   - Security features relaxed
   - SQLite database
   - In-memory rate limiting
   - Detailed logging

2. **Testing**
   - In-memory SQLite database
   - Security features disabled
   - Shorter JWT expiration
   - Separate test data directory

3. **Production**
   - Enhanced security
   - Redis for caching and rate limiting
   - Connection pooling
   - Minimal logging

## User Manual

### Accessing the Application
1. Open your web browser
2. Navigate to `http://localhost:5000` (development) or your deployed URL
3. You'll see the home page with available subjects

### Default Credentials
```
Username: admin123
Password: Admin@123
Role: admin
Email: admin@example.com
```

**Important Security Notes**:
1. Change these credentials immediately after first login
2. Create new admin accounts for production use
3. Disable or delete the default admin account in production

### User Registration
1. Click "Register" in the navigation bar
2. Fill in the registration form:
   - Username (at least 3 characters)
   - Password (at least 6 characters)
3. Click "Register" button

### User Login
1. Click "Login" in the navigation bar
2. Enter your credentials
3. Click "Login" button

## API Documentation

### Authentication Endpoints

#### Login
- **URL:** `/login`
- **Method:** `POST`
- **Data Params:**
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Success Response:** (200)
  ```json
  {
    "access_token": "string"
  }
  ```

#### Register
- **URL:** `/register`
- **Method:** `POST`
- **Data Params:**
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```

#### Logout
- **URL:** `/logout`
- **Method:** `GET`
- **Headers Required:**
  - Authorization: Bearer {token}

## Security Features

1. **JWT Authentication**:
   - Access tokens (1 hour expiry)
   - Refresh tokens (30 days expiry)
   - CSRF protection for cookies

2. **Security Headers**:
   - HTTPS enforcement (in production)
   - Strict Transport Security
   - Content Security Policy
   - Secure cookies

3. **Rate Limiting**:
   - Development: Disabled
   - Production: 50 requests per hour
   - Redis backend in production

4. **CSRF Protection**:
   - WTF-CSRF enabled
   - 1-hour token lifetime
   - Secure key configuration

## Testing

### Running Tests
```bash
# Run complete test suite
pytest

# Run tests by category
pytest tests/functional/
pytest tests/unit/

# Test coverage report
pytest --cov=app tests/
```

### Test Structure
```
tests/
├── __init__.py
├── conftest.py
├── functional/
│   ├── __init__.py
│   └── test_routes.py
├── unit/
│   ├── __init__.py
│   └── test_services.py
└── scripts/
    └── check_routes.py
```

## Dependencies

### Core Flask Framework
- Flask==3.1.0
- Werkzeug==3.1.3
- Jinja2==3.1.5
- click==8.1.8
- itsdangerous==2.2.0
- blinker==1.9.0

### Flask Extensions
- Flask-JWT-Extended==4.7.1
- Flask-Login==0.6.3
- Flask-Limiter==3.9.2
- Flask-Talisman==1.1.0
- Flask-WTF==1.2.2
- Flask-SQLAlchemy==3.1.1
- Flask-Migrate==4.0.5
- Flask-Caching==2.1.0
- Flask-Mail==0.9.1

[Full dependency list in requirements.txt]

## Production Deployment

1. Set environment variables:
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=<your-secret-key>
   export JWT_SECRET_KEY=<your-jwt-secret-key>
   export WTF_CSRF_SECRET_KEY=<your-csrf-secret-key>
   ```

2. Set up Redis (for caching and rate limiting)
3. Configure proper logging directory
4. Use a production WSGI server (e.g., gunicorn)
5. Set up HTTPS
6. Configure database connection pool

## Troubleshooting

### Common Issues
1. **Template Not Found**
   - Check template directory structure
   - Verify template_folder path

2. **Database Access**
   - Check file permissions
   - Verify JSON file structure

3. **Authentication Issues**
   - Verify JWT secret key
   - Check token expiration
   - Validate CSRF token configuration

### Browser Compatibility
- Supported browsers:
  - Chrome (recommended)
  - Firefox
  - Safari
  - Edge

For additional support or questions, please refer to the documentation in the respective directories or contact the system administrator. 