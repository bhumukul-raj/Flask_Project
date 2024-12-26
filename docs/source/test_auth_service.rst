Authentication Service Tests
=======================

This document details the test suite for the Authentication Service module.

Overview
--------

The test suite validates the core functionality of the authentication service, including:

* User authentication
* User creation
* Token generation
* Input validation
* Error handling

Test Configuration
-----------------

.. code-block:: python

    @pytest.fixture
    def app():
        """Create and configure a new app instance for each test."""
        app = Flask(__name__)
        app.config.update({'TESTING': True})
        return app

Test Data
---------

.. code-block:: python

    @pytest.fixture
    def mock_users_data():
        """Test user data fixture."""
        return {
            'users': [
                {
                    'id': 1,
                    'username': 'testuser',
                    'password': generate_password_hash('password123')
                }
            ]
        }

Test Cases
----------

Authentication Tests
~~~~~~~~~~~~~~~~~~

test_authenticate_user_success
****************************

.. automethod:: tests.services.test_auth_service.TestAuthService.test_authenticate_user_success

test_authenticate_user_wrong_password
**********************************

.. automethod:: tests.services.test_auth_service.TestAuthService.test_authenticate_user_wrong_password

test_authenticate_user_nonexistent
********************************

.. automethod:: tests.services.test_auth_service.TestAuthService.test_authenticate_user_nonexistent

User Creation Tests
~~~~~~~~~~~~~~~~~

test_create_user_success
***********************

.. automethod:: tests.services.test_auth_service.TestAuthService.test_create_user_success

test_create_user_existing_username
********************************

.. automethod:: tests.services.test_auth_service.TestAuthService.test_create_user_existing_username

test_create_user_invalid_username
*******************************

.. automethod:: tests.services.test_auth_service.TestAuthService.test_create_user_invalid_username

test_create_user_invalid_password
*******************************

.. automethod:: tests.services.test_auth_service.TestAuthService.test_create_user_invalid_password

Token Generation Tests
~~~~~~~~~~~~~~~~~~~~

test_generate_token
******************

.. automethod:: tests.services.test_auth_service.TestAuthService.test_generate_token

Test Fixtures
------------

The test suite uses several fixtures for dependency injection and mocking:

app
~~~

.. autofunction:: tests.services.test_auth_service.app

mock_users_data
~~~~~~~~~~~~~~

.. autofunction:: tests.services.test_auth_service.mock_users_data

mock_load_data
~~~~~~~~~~~~~

.. autofunction:: tests.services.test_auth_service.mock_load_data

mock_save_data
~~~~~~~~~~~~~

.. autofunction:: tests.services.test_auth_service.mock_save_data

Running the Tests
---------------

To run the authentication service tests:

.. code-block:: bash

    # Run all tests
    pytest tests/services/test_auth_service.py -v

    # Run specific test
    pytest tests/services/test_auth_service.py -v -k "test_authenticate_user_success"

    # Run with coverage
    pytest tests/services/test_auth_service.py -v --cov=app.services.auth_service

Test Coverage
------------

The test suite covers:

* Successful authentication scenarios
* Failed authentication attempts
* User creation validation
* Password validation
* Token generation
* Error handling
* Edge cases

Dependencies
-----------

* pytest
* Flask
* Werkzeug
* unittest.mock
* JWT Extended 