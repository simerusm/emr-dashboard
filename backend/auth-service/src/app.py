from flask import Flask, jsonify, request, g
from .config import app_config
from .utils import init_db, get_db_session, close_db_session, setup_logging, Validator
from .services import AuthService, RBACService
from .middleware.auth_middleware import authenticate, require_permissions, require_roles, rate_limit
from sqlalchemy import inspect

app = Flask(__name__)
app.config.from_object(app_config)
setup_logging(app)
init_db()

# Health check route
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

# User Registration endpoint
@app.route('/register', methods=['POST'])
def register():
    """Endpoint to register a user. Db sessions saved in the AuthService functions."""

    data = request.get_json()
    is_valid, errors = Validator.validate_registration_data(data)
    if not is_valid:
        return jsonify({"errors": errors}), 400

    db_session = get_db_session()
    try:
        # Check if a user with the given email already exists
        if AuthService.get_user_by_email(db_session, data['email']):
            return jsonify({"error": "User already exists"}), 400

        # Create a new user and assign a default role
        user = AuthService.create_user(
            db_session,
            email=data['email'],
            username=data['username'],
            password=data['password'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        AuthService.assign_role_to_user(db_session, user, "user")
        
        return jsonify({"message": "User created successfully", "user_id": str(user.id)}), 201
    finally:
        close_db_session()

@app.route('/login', methods=['POST'])
def login():
    """Endpoint to verify login details of a user and generate JWT token. Db sessions saved in the AuthService functions."""

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    db_session = get_db_session()
    try:
        user = AuthService.get_user_by_email(db_session, email)
        if not user or not AuthService.verify_password(password, user.password_hash):
            return jsonify({"error": "Invalid credentials"}), 401

        access_token, refresh_token, token_jti = AuthService.generate_tokens(user)
        # Store refresh token in the database
        AuthService.store_refresh_token(db_session, user, token_jti)
        
        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 200
    finally:
        close_db_session()

@app.route('/protected', methods=['GET'])
@authenticate
def protected():
    # The authenticate middleware sets g.user_id, g.username, etc.
    return jsonify({
        "message": f"Hello, {g.username}! You have accessed a protected endpoint."
    }), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
