from flask import Flask, jsonify, request, g
from werkzeug.exceptions import HTTPException
import traceback
import sys
import redis
import os
from flask_cors import CORS

from .config import app_config
from .utils import init_db, get_db_session, close_db_session, setup_logging
from .models import Base
from .routes import auth_bp, user_bp, admin_bp, system_bp
from .middleware.security_middleware import setup_security_headers

# Create and configure the app
app = Flask(__name__)
app.config.from_object(app_config)

# Set up CORS
CORS(app, resources={r"/*": {"origins": app.config.get('CORS_ORIGINS', '*')}})

# Set up logging
setup_logging(app)

# Set up security headers
setup_security_headers(app)

# Initialize database
init_db()

# Register blueprints
app.register_blueprint(auth_bp)  # /auth/...
app.register_blueprint(user_bp)  # /users/...
app.register_blueprint(admin_bp)  # /admin/...
app.register_blueprint(system_bp)  # / and /health, /metrics

# Register error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request", "message": str(error)}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Unauthorized", "message": str(error)}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({"error": "Forbidden", "message": str(error)}), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found", "message": str(error)}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed", "message": str(error)}), 405

@app.errorhandler(429)
def too_many_requests(error):
    return jsonify({"error": "Too many requests", "message": str(error)}), 429

@app.errorhandler(500)
def internal_server_error(error):
    # Log the error
    app.logger.error(f"500 Error: {str(error)}")
    
    # In development mode, include traceback
    if app.debug:
        traceback_str = traceback.format_exc()
        return jsonify({
            "error": "Internal server error",
            "message": str(error),
            "traceback": traceback_str
        }), 500
    
    # In production, just return a generic message
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

@app.errorhandler(Exception)
def handle_exception(error):
    """Handle all unhandled exceptions."""
    # Log the error
    app.logger.error(f"Unhandled Exception: {str(error)}")
    app.logger.error(traceback.format_exc())
    
    # Handle HTTPExceptions differently
    if isinstance(error, HTTPException):
        return jsonify({
            "error": error.name,
            "message": error.description
        }), error.code
    
    # In development mode, include traceback
    if app.debug:
        traceback_str = traceback.format_exc()
        return jsonify({
            "error": "Internal server error",
            "message": str(error),
            "traceback": traceback_str
        }), 500
    
    # In production, just return a generic message
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

# Register teardown handler to ensure DB sessions are closed
@app.teardown_appcontext
def teardown_db(exception=None):
    """Ensure database sessions are closed at the end of the request."""
    close_db_session()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)