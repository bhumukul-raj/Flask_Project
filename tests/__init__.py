"""
Flask Auth Service Test Suite

This package contains all tests for the Flask Auth Service application.
Organized into the following packages:

tests/
├── unit/                       # Unit tests package
│   ├── routes/                 # Route tests
│   │   ├── test_admin.py      # Admin route tests
│   │   ├── test_api.py        # API route tests
│   │   └── test_routes.py     # Main route tests
│   ├── services/              # Service tests
│   │   └── test_auth_service.py  # Authentication service tests
│   └── utils/                 # Utility tests
│       ├── test_hash_utils.py # Password hashing tests
│       ├── test_logger.py     # Logging tests
│       └── test_validators.py # Input validation tests
├── integration/               # Integration tests
│   └── test_error_handlers.py # Error handling tests
└── models/                    # Model tests
    └── test_models.py         # User model tests
"""

__version__ = '1.0.0'
