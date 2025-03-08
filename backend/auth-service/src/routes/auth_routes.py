from datetime import datetime, timedelta
import secrets
from flask import Blueprint, request, jsonify, g, current_app, redirect

from ..models import User
from ..services import AuthService, RBACService
from ..utils import get_db_session, close_db_session, Validator
from ..middleware.auth_middleware import authenticate, require_permissions, require_roles

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
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

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint to verify login details of a user and generate JWT token."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    db_session = get_db_session()
    try:
        user = AuthService.get_user_by_email(db_session, email)
        
        # If user doesn't exist or is inactive, return generic error
        if not user or not user.is_active:
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Check if password is correct
        if not AuthService.verify_password(password, user.password_hash):
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Generate tokens and continue with login
        access_token, refresh_token, token_jti = AuthService.generate_tokens(
            user,
            user_agent=request.headers.get('User-Agent'),
            ip_address=request.remote_addr
        )
        
        # Store refresh token in the database
        AuthService.store_refresh_token(
            db_session,
            user,
            token_jti,
            user_agent=request.headers.get('User-Agent'),
            ip_address=request.remote_addr
        )
        
        # Update last login timestamp
        AuthService.update_last_login(db_session, user)
        
        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "roles": [role.name for role in user.roles]
            }
        }), 200
        
    finally:
        close_db_session()

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Endpoint to refresh access token using refresh token."""
    data = request.get_json()
    refresh_token = data.get('refresh_token')
    
    if not refresh_token:
        return jsonify({"error": "Refresh token is required"}), 400
    
    db_session = get_db_session()
    try:
        valid, user, token_jti = AuthService.validate_refresh_token(db_session, refresh_token)
        
        if not valid or not user:
            return jsonify({"error": "Invalid or expired refresh token"}), 401
        
        # Revoke the old refresh token for security
        AuthService.revoke_refresh_token(db_session, token_jti)
        
        # Generate new tokens
        access_token, new_refresh_token, new_token_jti = AuthService.generate_tokens(
            user, 
            request.headers.get('User-Agent'),
            request.remote_addr
        )
        
        # Store the new refresh token
        AuthService.store_refresh_token(
            db_session, 
            user, 
            new_token_jti,
            request.headers.get('User-Agent'),
            request.remote_addr
        )
        
        # Update last login timestamp
        AuthService.update_last_login(db_session, user)
        
        return jsonify({
            "access_token": access_token,
            "refresh_token": new_refresh_token
        }), 200
    finally:
        close_db_session()

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using a valid token."""
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    
    if not token or not new_password:
        return jsonify({"error": "Token and new password are required"}), 400
    
    # Validate password strength
    is_valid_password, password_error = Validator.validate_password(new_password)
    if not is_valid_password:
        return jsonify({"error": password_error}), 400
    
    db_session = get_db_session()
    try:
        # Find user with this reset token
        user = db_session.query(User).filter_by(
            password_reset_token=token,
        ).first()
        
        if not user:
            return jsonify({"error": "Invalid or expired token"}), 400
        
        # Check if token is expired
        if not user.password_reset_expires_at or user.password_reset_expires_at < datetime.utcnow():
            return jsonify({"error": "Reset token has expired"}), 400
        
        # Update the password
        user.password_hash = AuthService.hash_password(new_password)
        
        # Clear the reset token
        user.password_reset_token = None
        user.password_reset_expires_at = None
        
        # Revoke all refresh tokens for this user
        for token in user.refresh_tokens:
            token.is_revoked = True
        
        db_session.commit()
        
        return jsonify({"message": "Password has been reset successfully"}), 200
    
    except Exception as e:
        current_app.logger.error(f"Password reset error: {str(e)}")
        return jsonify({"error": "An error occurred processing your request"}), 500
    finally:
        close_db_session()