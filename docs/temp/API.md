# API Documentation

## Authentication Endpoints

### Login
- **URL:** `/login`
- **Method:** `POST`
- **Data Params:**
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Success Response:**
  - **Code:** 200
  - **Content:**
    ```json
    {
      "access_token": "string"
    }
    ```
- **Error Response:**
  - **Code:** 401
  - **Content:**
    ```json
    {
      "msg": "Bad username or password"
    }
    ```

### Register
- **URL:** `/register`
- **Method:** `POST`
- **Data Params:**
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Success Response:**
  - **Code:** 302
  - **Content:** Redirects to login page
- **Error Response:**
  - **Code:** 400
  - **Content:**
    ```json
    {
      "msg": "Registration failed"
    }
    ```

### Logout
- **URL:** `/logout`
- **Method:** `GET`
- **Headers Required:**
  - Authorization: Bearer {token}
- **Success Response:**
  - **Code:** 200
  - **Content:**
    ```json
    {
      "msg": "Successfully logged out"
    }
    ```
- **Error Response:**
  - **Code:** 401
  - **Content:**
    ```json
    {
      "msg": "Missing Authorization Header"
    }
    ```

## Content Endpoints

### Get Subjects
- **URL:** `/`
- **Method:** `GET`
- **Success Response:**
  - **Code:** 200
  - **Content:** HTML page with subjects list
- **Sample Response Data Structure:**
  ```json
  {
    "subjects": [
      {
        "id": 1,
        "name": "Subject Name",
        "description": "Subject Description",
        "sections": [
          {
            "id": 1,
            "name": "Section Name",
            "topics": [...]
          }
        ]
      }
    ]
  }
  ```

## Security Features

### CSRF Protection
- All forms include CSRF token
- Token must be included in POST requests
- Failure to include token results in 400 error

### Rate Limiting
- API endpoints are rate-limited
- Exceeding limit results in 429 error

### JWT Authentication
- Required for protected endpoints
- Token must be included in Authorization header
- Format: `Authorization: Bearer {token}`
