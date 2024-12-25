# Setup Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for version control)

## Installation Steps

1. Clone the repository (if using Git):
   ```bash
   git clone <repository-url>
   cd Flask_Project
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - Unix/MacOS:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add the following variables:
     ```
     SECRET_KEY=your_secret_key
     JWT_SECRET_KEY=your_jwt_secret_key
     ```

## Configuration

### Development
- Uses `config/development.py`
- Debug mode enabled
- Detailed error messages
- No HTTPS enforcement

### Production
- Uses `config/production.py`
- Debug mode disabled
- HTTPS enforced
- Minimal error messages
- Rate limiting enabled

### Testing
- Uses `config/testing.py`
- Testing-specific configuration
- In-memory database
- CSRF disabled

## Running the Application

1. Development mode:
   ```bash
   python app.py
   ```

2. Production mode:
   ```bash
   export FLASK_ENV=production
   python app.py
   ```

3. Testing:
   ```bash
   python -m pytest
   ```

## Directory Structure Setup

1. Ensure these directories exist:
   ```
   Flask_Project/
   ├── app/
   │   ├── services/
   │   └── utils/
   ├── config/
   ├── data/
   ├── docs/
   ├── templates/
   │   ├── auth/
   │   └── public/
   └── tests/
   ```

2. Set proper permissions:
   - Make data directory writable
   - Protect .env file
   - Set proper file permissions

## Troubleshooting

### Common Issues

1. Template Not Found
   - Check template directory structure
   - Verify template_folder path in app initialization

2. Database Access
   - Check file permissions
   - Verify JSON file structure

3. Authentication Issues
   - Verify JWT secret key
   - Check token expiration
   - Validate CSRF token configuration
