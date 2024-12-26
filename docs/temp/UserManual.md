# User Manual

## Getting Started

### Accessing the Application
1. Open your web browser
2. Navigate to `http://localhost:5000` (development) or your deployed URL
3. You'll see the home page with available subjects

### User Registration
1. Click "Register" in the navigation bar
2. Fill in the registration form:
   - Username (at least 3 characters)
   - Password (at least 6 characters)
3. Click "Register" button
4. You'll be redirected to the login page

### User Login
1. Click "Login" in the navigation bar
2. Enter your credentials:
   - Username
   - Password
3. Click "Login" button
4. Upon successful login, you'll receive an authentication token

### Viewing Subjects
1. Navigate to the home page
2. Browse the list of available subjects
3. Each subject card shows:
   - Subject name
   - Description
   - Available sections

### Security Best Practices
1. Password Guidelines:
   - Use at least 6 characters
   - Mix uppercase and lowercase
   - Include numbers and symbols
2. Token Security:
   - Don't share your authentication token
   - Log out when finished
   - Use HTTPS in production

### Troubleshooting

#### Login Issues
1. Verify your username and password
2. Check if caps lock is enabled
3. Ensure you're registered
4. Clear browser cache if needed

#### Access Issues
1. Check if you're logged in
2. Verify your token hasn't expired
3. Try logging out and back in

#### Browser Compatibility
- Supported browsers:
  - Chrome (recommended)
  - Firefox
  - Safari
  - Edge

### Support
For technical support:
1. Check the troubleshooting guide
2. Review error messages
3. Contact system administrator

## Features

### Authentication
- Secure user registration
- JWT-based authentication
- Password hashing
- Session management

### Content Management
- Browse subjects
- View subject details
- Organized content structure

### Security
- CSRF protection
- Rate limiting
- Secure password storage
- HTTPS support
