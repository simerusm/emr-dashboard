from flask import request, g

def setup_security_headers(app):
    """Configure security headers for the application."""
    
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses."""
        # Content Security Policy
        if app.config.get('ENABLE_CONTENT_SECURITY_POLICY', True):
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "object-src 'none'"
            )
        
        # HTTP Strict Transport Security
        if app.config.get('ENABLE_HSTS', True):
            # max-age=31536000 means one year
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # X-Content-Type-Options
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # X-Frame-Options
        response.headers['X-Frame-Options'] = 'DENY'
        
        # X-XSS-Protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer-Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Feature-Policy / Permissions-Policy
        response.headers['Permissions-Policy'] = (
            'camera=(), microphone=(), geolocation=(), interest-cohort=()'
        )
        
        return response

    @app.before_request
    def validate_content_type():
        """Validate Content-Type header for JSON API endpoints."""
        if request.method in ['POST', 'PUT', 'PATCH']:
            if not request.path.startswith('/static/') and not request.path.startswith('/health'):
                content_type = request.headers.get('Content-Type', '')
                if 'application/json' not in content_type:
                    return {'error': 'Content-Type must be application/json'}, 415