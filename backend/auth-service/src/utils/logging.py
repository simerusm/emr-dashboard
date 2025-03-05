import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from flask import request, g

from ..config import app_config

def setup_logging(app):
    """Configure logging for the application."""
    log_level = getattr(logging, app_config.LOG_LEVEL)
    
    # Create formatters
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # Set up console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Set up file handler for logs
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'auth_service.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Configure Flask logger
    app.logger.setLevel(log_level)
    
    # Add request logging
    @app.before_request
    def log_request_info():
        """Log request information."""
        app.logger.debug(f"Request: {request.method} {request.path} from {request.remote_addr}")
    
    @app.after_request
    def log_response_info(response):
        """Log response information."""
        app.logger.debug(f"Response: {response.status}")
        return response

def get_logger(name):
    """Get a named logger."""
    return logging.getLogger(name)