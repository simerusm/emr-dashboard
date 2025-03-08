from .auth_routes import auth_bp
from .user_routes import user_bp
from .admin_routes import admin_bp
from .system_routes import system_bp

__all__ = ['auth_bp', 'user_bp', 'admin_bp', 'system_bp']