import functools
from typing import List, Callable

from flask import request, g, jsonify, current_app
import jwt
import time
import redis
from functools import wraps

from ..services import AuthService, RBACService
from ..utils.db import get_db_session

# Connect to Redis
redis_client = None

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

def get_redis_client():
    """Get or create Redis client."""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(current_app.config['RATELIMIT_STORAGE_URL'])
    return redis_client

def rate_limit(requests=100, per_seconds=60, key_func=None):
    """
    Rate limiting middleware using Redis.
    
    Args:
        requests: Maximum number of requests allowed in the time window
        per_seconds: Time window in seconds
        key_func: Function to generate a custom key for rate limiting (defaults to IP address)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get Redis client
            redis = get_redis_client()
            
            # Generate key for rate limiting
            if key_func:
                key = key_func()
            else:
                # Default: use IP address as key
                key = f"rate_limit:{request.remote_addr}"
            
            # Get current count for this key
            current = redis.get(key)
            
            # If key doesn't exist, initialize it
            if current is None:
                redis.setex(key, per_seconds, 1)
                current = 1
            else:
                current = int(current)
                if current >= requests:
                    # Too many requests
                    retry_after = redis.ttl(key)
                    response = jsonify({
                        "error": "Too many requests",
                        "retry_after": retry_after
                    })
                    response.headers["Retry-After"] = retry_after
                    return response, 429
                
                # Increment the counter
                redis.incr(key)
                # Ensure the key expires if it wasn't set before
                if redis.ttl(key) == -1:
                    redis.expire(key, per_seconds)
            
            # Add rate limit headers
            response = f(*args, **kwargs)
            
            # If response is a tuple (response, status_code)
            if isinstance(response, tuple):
                response_obj, status_code = response
                headers = {
                    "X-RateLimit-Limit": str(requests),
                    "X-RateLimit-Remaining": str(requests - current),
                    "X-RateLimit-Reset": str(redis.ttl(key))
                }
                # Add headers to the response
                if hasattr(response_obj, "headers"):
                    for key, value in headers.items():
                        response_obj.headers[key] = value
                return response_obj, status_code
            
            # If response is just the response object
            headers = {
                "X-RateLimit-Limit": str(requests),
                "X-RateLimit-Remaining": str(requests - current),
                "X-RateLimit-Reset": str(redis.ttl(key))
            }
            # Add headers to the response
            if hasattr(response, "headers"):
                for key, value in headers.items():
                    response.headers[key] = value
            return response
        
        return decorated_function
    
    return decorator