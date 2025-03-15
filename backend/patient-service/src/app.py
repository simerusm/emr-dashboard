from flask import Flask, jsonify, request, g
import logging
import traceback
from werkzeug.exceptions import HTTPException
import time
import uuid
from flask_caching import Cache
from flask_cors import CORS

from .config import app_config
from .utils.db import init_db, close_db_session, ensure_indexes
from .routes.patient_routes import patient_bp
from .middleware.security_middleware import setup_security_headers
from .middleware.auth_middleware import require_auth

# Create Flask application
def create_app(config_object=app_config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Set up logging
    logging.basicConfig(
        level=getattr(logging, app_config.LOG_LEVEL),
        format=app_config.LOG_FORMAT
    )

    # Set up CORS
    CORS(app, resources={r"/*": {"origins": app_config.CORS_ORIGINS}})

    # Set up caching
    cache = Cache(app)

    # Set up security headers
    setup_security_headers(app)

    # Initialize database
    with app.app_context():
        init_db()
        ensure_indexes()
        app.logger.info("Database initialized and indexes ensured")

    # Register blueprints
    app.register_blueprint(patient_bp)

    # Add request ID to each request for tracing
    @app.before_request
    def add_request_id():
        """Add a unique request ID to each request for tracing."""
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()

    # Log request and response details
    @app.after_request
    def log_request_info(response):
        """Log request and response details for monitoring."""
        # Calculate request duration
        duration = round((time.time() - g.get('start_time', time.time())) * 1000, 2)
        
        # Log request details
        app.logger.info(
            f"Request: {request.method} {request.path} | "
            f"Status: {response.status_code} | "
            f"Duration: {duration}ms | "
            f"Request ID: {g.get('request_id', 'N/A')}"
        )
        
        # Add request ID to response headers for tracing
        response.headers['X-Request-ID'] = g.get('request_id', 'N/A')
        
        return response

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        """Simple health check endpoint."""
        return jsonify({
            "status": "ok",
            "service": "patient-data-service",
            "version": app_config.APP_VERSION if hasattr(app_config, 'APP_VERSION') else "development"
        }), 200

    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        return jsonify({
            "error": "Bad Request",
            "message": str(error),
            "request_id": g.get('request_id', 'N/A')
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors."""
        return jsonify({
            "error": "Unauthorized",
            "message": str(error),
            "request_id": g.get('request_id', 'N/A')
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors."""
        return jsonify({
            "error": "Forbidden",
            "message": str(error),
            "request_id": g.get('request_id', 'N/A')
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        return jsonify({
            "error": "Not Found",
            "message": f"The requested URL {request.path} was not found on the server",
            "request_id": g.get('request_id', 'N/A')
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors."""
        return jsonify({
            "error": "Method Not Allowed",
            "message": f"The method {request.method} is not allowed for the requested URL",
            "request_id": g.get('request_id', 'N/A')
        }), 405

    @app.errorhandler(429)
    def too_many_requests(error):
        """Handle 429 Too Many Requests errors."""
        return jsonify({
            "error": "Too Many Requests",
            "message": "Rate limit exceeded",
            "request_id": g.get('request_id', 'N/A')
        }), 429

    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error errors."""
        # Log the error
        app.logger.error(f"500 Error: {str(error)}")
        app.logger.error(traceback.format_exc())
        
        # In development mode, include traceback
        if app.debug:
            return jsonify({
                "error": "Internal Server Error",
                "message": str(error),
                "traceback": traceback.format_exc(),
                "request_id": g.get('request_id', 'N/A')
            }), 500
        
        # In production, just return a generic message
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "request_id": g.get('request_id', 'N/A')
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
                "message": error.description,
                "request_id": g.get('request_id', 'N/A')
            }), error.code
        
        # In development mode, include traceback
        if app.debug:
            return jsonify({
                "error": "Internal Server Error",
                "message": str(error),
                "traceback": traceback.format_exc(),
                "request_id": g.get('request_id', 'N/A')
            }), 500
        
        # In production, just return a generic message
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "request_id": g.get('request_id', 'N/A')
        }), 500

    # Register teardown handler to ensure DB sessions are closed
    @app.teardown_appcontext
    def teardown_db(exception=None):
        """Ensure database sessions are closed at the end of the request."""
        close_db_session()

    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=(app_config.FLASK_ENV == 'development'))