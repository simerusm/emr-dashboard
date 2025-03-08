from datetime import datetime
import jwt
from flask import Blueprint, request, jsonify, g, current_app

from ..models import User
from ..services import AuthService
from ..utils import get_db_session, close_db_session, Validator
from ..middleware.auth_middleware import authenticate, require_permissions, require_roles

# Create the blueprint
user_bp = Blueprint('user', __name__, url_prefix='/users')

@user_bp.route('/me', methods=['GET'])
@authenticate
def get_current_user():
    """Get current authenticated user profile."""
    db_session = get_db_session()
    try:
        user = AuthService.get_user_by_id(db_session, g.user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "user": user.to_dict()
        }), 200
    finally:
        close_db_session()

@user_bp.route('/me', methods=['PUT', 'PATCH'])
@authenticate
def update_current_user():
    """Update current authenticated user profile."""
    data = request.get_json()
    
    # Fields that can be updated by the user
    allowed_fields = ['first_name', 'last_name', 'username']
    
    # Filter out fields that cannot be updated
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    # If username is being updated, validate it
    if 'username' in update_data:
        is_valid, error = Validator.validate_username(update_data['username'])
        if not is_valid:
            return jsonify({"error": error}), 400
    
    db_session = get_db_session()
    try:
        user = AuthService.get_user_by_id(db_session, g.user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Update user fields
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db_session.commit()
        
        return jsonify({
            "message": "User updated successfully",
            "user": user.to_dict()
        }), 200
    finally:
        close_db_session()

@user_bp.route('/me/change-password', methods=['POST'])
@authenticate
def change_password():
    """Change password for the current authenticated user."""
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({"error": "Current password and new password are required"}), 400
    
    # Validate new password
    is_valid, error = Validator.validate_password(new_password)
    if not is_valid:
        return jsonify({"error": error}), 400
    
    db_session = get_db_session()
    try:
        user = AuthService.get_user_by_id(db_session, g.user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Verify current password
        if not AuthService.verify_password(current_password, user.password_hash):
            return jsonify({"error": "Current password is incorrect"}), 401
        
        # Update password
        user.password_hash = AuthService.hash_password(new_password)
        
        # Revoke all refresh tokens for this user for security
        for token in user.refresh_tokens:
            token.is_revoked = True
        
        db_session.commit()
        
        # Generate new tokens
        access_token, refresh_token, token_jti = AuthService.generate_tokens(user)
        
        # Store new refresh token
        AuthService.store_refresh_token(
            db_session, 
            user, 
            token_jti,
            request.headers.get('User-Agent'),
            request.remote_addr
        )
        
        return jsonify({
            "message": "Password changed successfully",
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 200
    finally:
        close_db_session()

@user_bp.route('/me/logout', methods=['POST'])
@authenticate
def logout():
    """Logout current user by revoking the refresh token."""
    data = request.get_json()
    refresh_token = data.get('refresh_token')
    
    if not refresh_token:
        return jsonify({"message": "Logged out successfully"}), 200
    
    db_session = get_db_session()
    try:
        # Extract JTI from refresh token
        try:
            payload = jwt.decode(
                refresh_token,
                current_app.config.get('JWT_SECRET_KEY'),
                algorithms=['HS256'],
                options={"verify_exp": False}  # Don't verify expiration for logout
            )
            token_jti = payload.get('jti')
        except Exception:
            # If token is invalid, still return success
            return jsonify({"message": "Logged out successfully"}), 200
        
        # Revoke the token
        if token_jti:
            AuthService.revoke_refresh_token(db_session, token_jti)
        
        return jsonify({"message": "Logged out successfully"}), 200
    finally:
        close_db_session()

@user_bp.route('/me/sessions', methods=['GET'])
@authenticate
def get_active_sessions():
    """Get active sessions for the current user."""
    db_session = get_db_session()
    try:
        user = AuthService.get_user_by_id(db_session, g.user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get active refresh tokens
        active_tokens = [token for token in user.refresh_tokens 
                        if not token.is_revoked and token.expires_at > datetime.utcnow()]
        
        sessions = [{
            "id": token.id,
            "created_at": token.issued_at.isoformat() if token.issued_at else None,
            "expires_at": token.expires_at.isoformat() if token.expires_at else None,
            "user_agent": token.user_agent,
            "ip_address": token.ip_address
        } for token in active_tokens]
        
        return jsonify({
            "sessions": sessions
        }), 200
    finally:
        close_db_session()

@user_bp.route('/me/sessions/<session_id>', methods=['DELETE'])
@authenticate
def revoke_session(session_id):
    """Revoke a specific session for the current user."""
    db_session = get_db_session()
    try:
        user = AuthService.get_user_by_id(db_session, g.user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Find the refresh token
        token = next((token for token in user.refresh_tokens if token.id == session_id), None)
        
        if not token:
            return jsonify({"error": "Session not found"}), 404
        
        # Ensure the token belongs to the current user
        if token.user_id != g.user_id:
            return jsonify({"error": "Unauthorized"}), 401
        
        # Revoke the token
        token.is_revoked = True
        db_session.commit()
        
        return jsonify({
            "message": "Session revoked successfully"
        }), 200
    finally:
        close_db_session()

@user_bp.route('/me/sessions', methods=['DELETE'])
@authenticate
def revoke_all_sessions():
    """Revoke all sessions for the current user except the current one."""
    data = request.get_json()
    current_refresh_token = data.get('current_refresh_token')
    
    db_session = get_db_session()
    try:
        user = AuthService.get_user_by_id(db_session, g.user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        current_token_jti = None
        if current_refresh_token:
            try:
                payload = jwt.decode(
                    current_refresh_token,
                    current_app.config.get('JWT_SECRET_KEY'),
                    algorithms=['HS256'],
                    options={"verify_exp": False}
                )
                current_token_jti = payload.get('jti')
            except Exception:
                pass
        
        # Revoke all tokens except the current one
        for token in user.refresh_tokens:
            if not current_token_jti or token.token != current_token_jti:
                token.is_revoked = True
        
        db_session.commit()
        
        return jsonify({
            "message": "All other sessions revoked successfully"
        }), 200
    finally:
        close_db_session()

@user_bp.route('/protected-test', methods=['GET'])
@authenticate
def protected_test():
    """A protected test endpoint that only authenticated users can access."""
    return jsonify({
        "message": f"Hello, {g.username}! You have accessed a protected endpoint."
    }), 200