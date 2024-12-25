# Flask Learning Management System

A modern web application built with Flask for managing educational content and user authentication.

## Features

- User Authentication (Login/Register)
- JWT Token-based Authorization
- Subject Management
- Security Features (CSRF, Rate Limiting, Security Headers)
- Responsive UI with Bootstrap

## Project Structure

```
Flask_Project/
├── app/
│   ├── services/         # Business logic and data services
│   ├── utils/           # Utility functions and helpers
│   ├── __init__.py      # Application factory
│   └── routes.py        # Route definitions
├── config/              # Configuration files for different environments
├── data/                # JSON data storage
├── docs/                # Project documentation
├── templates/           # HTML templates
│   ├── auth/           # Authentication templates
│   └── public/         # Public page templates
├── tests/              # Test files
├── .env                # Environment variables
├── .gitignore         # Git ignore file
├── app.py             # Application entry point
└── requirements.txt   # Project dependencies
```

## Setup Instructions

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `.\venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the values in `.env`

5. Run the application:
   ```bash
   python app.py
   ```

## Security Features

- JWT Authentication
- CSRF Protection
- Rate Limiting
- Security Headers (via Flask-Talisman)
- Password Hashing

## API Endpoints

- `GET /` - Home page with subject listing
- `GET/POST /login` - User login
- `GET/POST /register` - User registration
- `GET /logout` - User logout (requires authentication)

## Development

### Running Tests
```bash
python -m pytest
```

### Configuration
- Development: `config/development.py`
- Production: `config/production.py`
- Testing: `config/testing.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

Username: admin123
Password: Admin@123456
Role: admin


Username: student
Password: Stu@123456
Role: user

