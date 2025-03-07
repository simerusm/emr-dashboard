# Auth Microservice Setup

## Prerequisites
- Ensure you have Python 3.6 or higher installed.

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>/auth-service
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

4. **Run the Microservice**:
   ```bash
   python -m src.app
   ```

5. **Run the Test Cases**:
   ```bash
   python -m unittest discover -s tests -p "*.py"
   ```

## Endpoints

### 1. Register a New User

**Curl Command:**
```bash
curl -X POST http://localhost:5001/register \
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

**Curl Command:**
```bash
curl -X POST http://localhost:5001/login \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "ValidPass123!"}'
```

**Expected Output:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 3. Access Protected Endpoint

**Curl Command:**
```bash
curl -X GET http://localhost:5001/protected \
     -H "Authorization: Bearer <access_token>"
```
Replace `<access_token>` with the actual token received from the login response

**Expected Output:**
```json
{
    "message": "Hello, testuser! You have accessed a protected endpoint."
}
```