# Flask Project Setup Guide

This is a Flask application with a comprehensive configuration setup for different environments (development, testing, and production).

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

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Initialize the Project**:
```bash
python run.py init
```

3. **Start the Development Server**:
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

The application uses different configurations based on the environment:

### Development (Default)
- Debug mode enabled
- Security features relaxed for development
- SQLite database
- In-memory rate limiting
- Detailed logging

### Testing
- In-memory SQLite database
- Security features disabled
- Shorter JWT expiration
- Separate test data directory

### Production
- Enhanced security
- Redis for caching and rate limiting
- Connection pooling
- Minimal logging
- Required environment variables:
  - SECRET_KEY
  - JWT_SECRET_KEY
  - WTF_CSRF_SECRET_KEY

## Environment Variables

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

5. **Session Security**:
   - HTTP-only cookies
   - Secure cookies (in production)
   - 7-day lifetime
   - Strict same-site policy

## File Upload Configuration

- Maximum file size: 10MB
- Upload directory: `/uploads`
- Supported in development and production

## Caching

- Development: Simple in-memory cache
- Production: Redis backend
- Default timeout: 5 minutes

## Logging

- Development: DEBUG level, `logs/development.log`
- Production: WARNING level, `/var/log/app/app.log`
- Format: `%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]`

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

## Dependencies

The project uses various Python packages categorized by their purpose:

### Core Flask Framework
- `Flask==3.1.0` - Web framework
- `Werkzeug==3.1.3` - WSGI utility library
- `Jinja2==3.1.5` - Template engine
- `click==8.1.8` - Command-line interface
- `itsdangerous==2.2.0` - Security helpers
- `blinker==1.9.0` - Signals support

### Flask Extensions
- `Flask-JWT-Extended==4.7.1` - JWT authentication
- `Flask-Login==0.6.3` - User session management
- `Flask-Limiter==3.9.2` - Rate limiting
- `Flask-Talisman==1.1.0` - Security headers
- `Flask-WTF==1.2.2` - Form handling and CSRF
- `Flask-SQLAlchemy==3.1.1` - ORM integration
- `Flask-Migrate==4.0.5` - Database migrations
- `Flask-Caching==2.1.0` - Caching support
- `Flask-Mail==0.9.1` - Email support

### Database and ORM
- `SQLAlchemy==2.0.25` - SQL toolkit and ORM
- `alembic==1.13.1` - Database migration tool
- `psycopg2-binary==2.9.9` - PostgreSQL adapter

### Security
- `PyJWT==2.8.0` - JSON Web Token implementation
- `cryptography==42.0.5` - Cryptographic recipes
- `bcrypt==4.1.2` - Password hashing
- `python-dotenv==1.0.1` - Environment variable management
- `WTForms==3.1.2` - Form validation

### Rate Limiting and Caching
- `limits==3.9.0` - Rate limiting utilities
- `redis==5.0.2` - Redis client
- `cachelib==0.9.0` - Caching library

### API and Serialization
- `marshmallow==3.20.2` - Object serialization/deserialization
- `webargs==8.4.0` - Request parsing
- `apispec==6.4.0` - API documentation

### Testing
- `pytest==8.0.2` - Testing framework
- `pytest-cov==4.1.0` - Coverage reporting
- `pytest-flask==1.3.0` - Flask testing utilities
- `coverage==7.4.1` - Code coverage measurement

### Development Tools
- `black==24.2.0` - Code formatter
- `flake8==7.0.0` - Code linter
- `isort==5.13.2` - Import sorter
- `mypy==1.8.0` - Static type checker

### Production
- `gunicorn==21.2.0` - WSGI HTTP Server
- `supervisor==4.2.5` - Process control system
- `python-dateutil==2.9.0` - Date utilities
- `pytz==2024.1` - Timezone support

### Utilities
- `email-validator==2.1.1` - Email validation
- `Pillow==10.2.0` - Image processing
- `requests==2.31.0` - HTTP library
- `rich==13.9.4` - Rich text formatting
- `python-slugify==8.0.4` - URL slug generation

### Documentation
- `Sphinx==7.2.6` - Documentation generator
- `sphinx-rtd-theme==2.0.0` - Documentation theme

### Installation Options

```bash
# Install all dependencies
pip install -r requirements.txt

# Install minimal (core only)
pip install -r requirements.txt --no-deps

# Install production dependencies (excluding dev tools)
pip install -r requirements.txt --no-dev
```

## Testing

The project includes a comprehensive test suite organized into different categories and utility scripts for route checking.

### Test Structure
```
tests/
├── __init__.py                     # Test package initialization
├── conftest.py                     # Shared test fixtures
├── functional/                     # Functional/Integration tests
│   ├── __init__.py
│   └── test_routes.py             # Route testing
├── unit/                          # Unit tests
│   ├── __init__.py
│   ├── test_content_blocks.py     # Content block testing
│   ├── test_content_validation.py # Content validation testing
│   ├── test_error_handlers.py     # Error handler testing
│   └── test_services.py          # Service testing
└── scripts/                       # Test utilities
    └── check_routes.py           # Interactive route checker
```

### Running Tests

1. **Run Complete Test Suite**:
```bash
pytest
```

2. **Run Tests by Category**:
```bash
# Functional tests only
pytest tests/functional/

# Unit tests only
pytest tests/unit/

# Specific test file
pytest tests/functional/test_routes.py
```

3. **Test Coverage Report**:
```bash
pytest --cov=app tests/
```

### Route Checker Utility

The project includes an interactive route checker script to verify endpoint accessibility.

1. **Start the Flask Application**:
```bash
python run.py run
```

2. **Run Route Checker** (in another terminal):
```bash
# Check public routes
python scripts/check_routes.py

# Check with authentication
python scripts/check_routes.py --auth

# Check with custom port
python scripts/check_routes.py --port 8000
```

The route checker will test:
- Public Routes
- Protected Routes (requiring authentication)
- API Routes
- Dynamic Routes (with URL parameters)

Results are displayed in a color-coded table:
- 🟢 Green: Success (200, 201)
- 🟡 Yellow: Redirect (302) or Unauthorized (401)
- 🔴 Red: Not Found (404) or Error

### Test Categories

1. **Functional Tests** (`tests/functional/`):
   - Route accessibility
   - Authentication flows
   - Authorization checks
   - Dynamic route parameters
   - API endpoints

2. **Unit Tests** (`tests/unit/`):
   - Content block handling
   - Content validation
   - Error handlers
   - Service functions
   - Data processing

### Test Configuration

The test suite uses different configurations for various environments:

1. **Development Testing**:
   - SQLite database
   - Debug mode enabled
   - Detailed error messages
   - In-memory caching

2. **Production Testing**:
   - Mocked external services
   - Strict security checks
   - Performance monitoring
   - Error logging

### Writing New Tests

1. **Unit Tests**:
```python
def test_my_function():
    # Arrange
    input_data = {...}
    
    # Act
    result = my_function(input_data)
    
    # Assert
    assert result == expected_output
```

2. **Functional Tests**:
```python
def test_my_route(client):
    # Arrange
    data = {...}
    
    # Act
    response = client.post('/my-route', json=data)
    
    # Assert
    assert response.status_code == 200
    assert response.json['key'] == expected_value
```

### Test Fixtures

Common test fixtures are available in `conftest.py`:
- `client`: Flask test client
- `auth_client`: Authenticated test client
- `admin_client`: Admin-authenticated client
- `api_client`: API test client with JWT token

### Continuous Integration

The test suite is integrated with CI/CD:
1. All tests run on pull requests
2. Coverage reports are generated
3. Test results are posted to PR comments
4. Failed tests block merging

For more detailed information about specific test categories or writing new tests, see the documentation in the respective test directories.

## Default Credentials

The application comes with a default admin user for initial setup:

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

The default admin account has the following permissions:
- Manage Users
- Manage Content
- View Analytics
- Manage Settings

## Quick Start Guide

### 1. Initial Setup

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd Flask_Project

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize the project
python run.py init
```

### 2. Start the Application

```bash
# Start the development server
python run.py run
```

The server will start at `http://localhost:5000`

### 3. Test the Routes

In another terminal:
```bash
# Check all routes
python scripts/check_routes.py
```

### 4. Default Login

You can access the application using these default credentials:

```
URL: http://localhost:5000/auth/login
Username: admin123
Password: Admin@123
```

### 5. Available Routes

#### Public Routes
- `GET /` - Home page
- `GET /auth/login` - Login page
- `GET /auth/register` - Registration page
- `GET /subjects` - Subject listing

#### Protected Routes (Requires Login)
- `GET /dashboard` - User dashboard
- `GET /subject/<id>` - Subject details
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/users` - User management
- `GET /admin/subjects` - Subject management

#### Admin Routes
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/users` - User management
- `GET /admin/subjects` - Subject management
- `GET /admin/add_user` - Add new user
- `GET /admin/edit_user` - Edit user
- `GET /admin/delete_user` - Delete user
- `GET /admin/change_password` - Change password

#### Content Management Routes
- `GET /admin/subjects/<subject_id>/sections` - Manage sections
- `GET /admin/subjects/<subject_id>/sections/add` - Add section
- `GET /admin/subjects/<subject_id>/sections/<section_id>` - Edit section
- `GET /admin/subjects/<subject_id>/sections/<section_id>/delete` - Delete section

#### API Routes (Requires JWT Token)
- `GET /api/subjects` - List all subjects
- `GET /api/subjects/<id>` - Get subject details
- `POST /api/subjects` - Create new subject
- `GET /api/users` - List all users
- `GET /api/sections/<id>` - Get section details
- `POST /api/sections/<id>/topics` - Create new topic

### 6. Testing Different User Types

1. **Admin Access**:
```bash
# Test admin routes
python scripts/check_routes.py --auth
```

2. **API Access**:
```bash
# First get JWT token
curl -X POST http://localhost:5000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin123", "password": "Admin@123"}'

# Use token in subsequent requests
curl http://localhost:5000/api/subjects \
     -H "Authorization: Bearer <your-token>"
```

### 7. Common Operations

1. **User Management**:
   - Add User: `/admin/add_user`
   - Edit User: `/admin/edit_user`
   - Delete User: `/admin/delete_user`

2. **Content Management**:
   - Add Subject: `/admin/add_subject`
   - Add Section: `/admin/subjects/<id>/sections/add`
   - Add Topic: `/admin/subjects/<id>/sections/<id>/topics/add`

3. **System Management**:
   - View Logs: `logs/development.log`
   - Check Sessions: `/admin/sessions`
   - Monitor Activity: `/admin/dashboard`

### 8. Development Tools

1. **Route Testing**:
```bash
# Test all routes
python scripts/check_routes.py

# Test with authentication
python scripts/check_routes.py --auth

# Test specific port
python scripts/check_routes.py --port 8000
```

2. **Database Operations**:
```bash
# Initialize database
flask db init

# Create migration
flask db migrate

# Apply migration
flask db upgrade
```

3. **Logging**:
```bash
# View logs
tail -f logs/development.log
```

### 9. Troubleshooting

1. **Server Issues**:
   - Check if Redis is running (for production)
   - Verify database connection
   - Check log files for errors

2. **Authentication Issues**:
   - Verify credentials in `users.json`
   - Check session configuration
   - Validate JWT token expiration

3. **Permission Issues**:
   - Verify user role in database
   - Check permission settings
   - Review access logs

