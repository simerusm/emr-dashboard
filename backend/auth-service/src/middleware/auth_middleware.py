import functools
from typing import List, Callable

from flask import request, g, jsonify, current_app
import jwt

from ..services import AuthService, RBACService
from ..utils.db import get_db_session

def authenticate(f):
    """Middleware to authenticate requests using JWT."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({"error": "Missing authorization header"}), 401
        
        parts = auth_header.split()
        
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            return jsonify({"error": "Invalid authorization header format"}), 401
        
        token = parts[1]
        valid, payload = AuthService.validate_access_token(token)
        
        if not valid:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Store user information in Flask's g object for access in route handlers
        g.user_id = payload.get('sub')
        g.username = payload.get('username')
        g.roles = payload.get('roles', [])
        g.permissions = payload.get('permissions', [])
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_permissions(permissions: List[str], require_all: bool = False):
    """Middleware to check if the user has required permissions."""
    def decorator(f):
        @functools.wraps(f)
        @authenticate
        def decorated_function(*args, **kwargs):
            # Get user permissions from g object set by authenticate middleware
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

def require_roles(roles: List[str], require_all: bool = False):
    """Middleware to check if the user has required roles."""
    def decorator(f):
        @functools.wraps(f)
        @authenticate
        def decorated_function(*args, **kwargs):
            # Get user roles from g object set by authenticate middleware
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

def rate_limit(limit: int = None):
    """Rate limiting middleware (placeholder implementation)."""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # In a production environment, you would implement proper rate limiting
            # using Redis or another distributed cache system
            
            # For now, just pass through
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator