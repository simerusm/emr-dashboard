# Auth Microservice

A production-grade authentication and authorization microservice built with Flask, SQLAlchemy, and JWT.

## Features

- **User Authentication**
  - User registration
  - Login with JWT tokens (access and refresh tokens)
  - Password reset flow
  - Session management

- **Authorization**
  - Role-Based Access Control (RBAC)
  - Fine-grained permissions system
  - Role and permission management
  - Protection of admin features

- **Security**
  - Rate limiting
  - Password strength enforcement
  - Secure password hashing
  - Protection against common attacks
  - Security headers (CSP, HSTS, etc.)

- **Production Ready**
  - Organized with Flask Blueprints
  - Comprehensive test suite
  - Proper error handling
  - Detailed logging
  - Monitoring endpoints
  - Docker support
  - Database migrations

## Prerequisites

- Python 3.9+
- PostgreSQL
- Redis

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   # Create a virtual environment
   python -m venv venv

   # Activate the virtual environment
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Requirements**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables**:
   Create a `.env` file in the root directory with the following variables:
   ```
   FLASK_ENV=development
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=auth_service_db
   JWT_SECRET_KEY=your_secret_key_here
   PASSWORD_SALT=your_password_salt_here
   REDIS_URL=redis://localhost:6379/0
   CORS_ORIGINS=http://localhost:3000
   ```

5. **Initialize the Database**:
   ```bash
   # Create PostgreSQL database
   createdb auth_service_db
   
   # Run database migrations
   flask db upgrade
   ```

6. **Run the Microservice**:
   ```bash
   # Run directly
   python -m src.app
   
   # Or with Flask
   flask run
   ```

## Testing the API with curl

### 1. Register a New User

```bash
curl -X POST http://localhost:5001/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "username": "testuser", "password": "ValidPass123!"}'
```

**Expected Output:**
```json
{
    "message": "User created successfully",
    "user_id": "137155ac-2dd0-410d-8245-8820b75ad1f0"
}
```

### 2. Login with the New User

```bash
curl -X POST http://localhost:5001/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "ValidPass123!"}'
```

**Expected Output:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": "137155ac-2dd0-410d-8245-8820b75ad1f0",
        "username": "testuser",
        "email": "test@example.com",
        "roles": []
    }
}
```

### 3. Access Protected Endpoint

```bash
curl -X GET http://localhost:5001/users/protected-test \
     -H "Authorization: Bearer <access_token>"
```
Replace `<access_token>` with the actual token received from the login response.

**Expected Output:**
```json
{
    "message": "Hello, testuser! You have accessed a protected endpoint."
}
```

### 4. Get User Profile

```bash
curl -X GET http://localhost:5001/users/me \
     -H "Authorization: Bearer <access_token>"
```

**Expected Output:**
```json
{
    "user": {
        "id": "137155ac-2dd0-410d-8245-8820b75ad1f0",
        "email": "test@example.com",
        "username": "testuser",
        "first_name": null,
        "last_name": null,
        "is_active": true,
        "created_at": "2023-08-15T12:34:56.789012",
        "last_login_at": "2023-08-15T12:34:56.789012",
        "roles": []
    }
}
```

### 5. Refresh Token

```bash
curl -X POST http://localhost:5001/auth/refresh \
     -H "Content-Type: application/json" \
     -d '{"refresh_token": "<refresh_token>"}'
```
Replace `<refresh_token>` with the actual refresh token received from the login response.

**Expected Output:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 6. Update User Profile

```bash
curl -X PUT http://localhost:5001/users/me \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <access_token>" \
     -d '{"first_name": "Test", "last_name": "User"}'
```

### 7. Health Check

```bash
curl -X GET http://localhost:5001/health
```

## Docker Setup

To run the service using Docker:

1. **Build and start the containers**:
   ```bash
   docker-compose up -d
   ```

2. **Access the service**:
   The service will be available at http://localhost:5001

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/
```

## Project Structure

The service is organized using Flask Blueprints:

- **Auth Blueprint** (`/auth`): Authentication endpoints
- **User Blueprint** (`/users`): User management endpoints 
- **Admin Blueprint** (`/admin`): Admin-only routes
- **System Blueprint**: Health checks and monitoring

## Security Notes

- Always use HTTPS in production
- Rotate JWT keys periodically
- Monitor failed login attempts
- Keep dependencies updated

## License

This project is licensed under the MIT License.