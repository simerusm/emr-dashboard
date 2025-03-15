import functools
import requests
import json
from flask import request, g, jsonify, current_app
from functools import wraps

def require_auth(f):
    """Middleware to authenticate requests using JWT via auth service."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({"error": "Missing authorization header"}), 401
        
        parts = auth_header.split()
        
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            return jsonify({"error": "Invalid authorization header format"}), 401
        
        token = parts[1]
        
        # Validate token with auth service
        try:
            response = requests.get(
                f"{current_app.config.get('AUTH_SERVICE_URL')}/validate-token",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                return jsonify({"error": "Invalid or expired token"}), 401
            
            # Store user information in Flask's g object
            user_data = response.json().get('user', {})
            g.user_id = user_data.get('id')
            g.username = user_data.get('username')
            g.roles = user_data.get('roles', [])
            g.permissions = user_data.get('permissions', [])
            
            return f(*args, **kwargs)
        except requests.RequestException as e:
            current_app.logger.error(f"Error validating token with auth service: {str(e)}")
            return jsonify({"error": "Authentication service unavailable"}), 503
    
    return decorated_function

def require_permissions(permissions, require_all=False):
    """Middleware to check if the user has required permissions."""
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            # Get user permissions from g object set by require_auth
            user_permissions = g.permissions
            
            if require_all:
                # Check if user has all required permissions
                if not all(perm in user_permissions for perm in permissions):
                    return jsonify({"error": "Insufficient permissions"}), 403
            else:
                # Check if user has any of the required permissions
                if not any(perm in user_permissions for perm in permissions):
                    return jsonify({"error": "Insufficient permissions"}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator

def require_roles(roles, require_all=False):
    """Middleware to check if the user has required roles."""
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            # Get user roles from g object set by require_auth
            user_roles = g.roles
            
            if require_all:
                # Check if user has all required roles
                if not all(role in user_roles for role in roles):
                    return jsonify({"error": "Insufficient roles"}), 403
            else:
                # Check if user has any of the required roles
                if not any(role in user_roles for role in roles):
                    return jsonify({"error": "Insufficient roles"}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator