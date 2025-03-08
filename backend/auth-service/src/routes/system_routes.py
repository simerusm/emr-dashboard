import os
import time
import psutil
import platform
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, current_app, g

from ..models import User, RefreshToken
from ..services import AuthService
from ..utils import get_db_session, close_db_session
from ..middleware.auth_middleware import authenticate, require_permissions, require_roles, get_redis_client

# Create the blueprint
system_bp = Blueprint('system', __name__)

# Store server start time
SERVER_START_TIME = time.time()

@system_bp.route('/health', methods=['GET'])
def health():
    """Enhanced health check endpoint with detailed diagnostics."""
    db_session = get_db_session()
    
    try:
        # Check database connection
        db_healthy = False
        try:
            # Simple query to check database connection
            db_session.execute("SELECT 1").fetchone()
            db_healthy = True
        except Exception as e:
            current_app.logger.error(f"Database health check failed: {str(e)}")
        
        # Check Redis connection if used for rate limiting
        redis_healthy = False
        try:
            if hasattr(current_app.config, 'RATELIMIT_STORAGE_URL'):
                redis_client = get_redis_client()
                redis_client.ping()
                redis_healthy = True
        except Exception as e:
            current_app.logger.error(f"Redis health check failed: {str(e)}")
        
        # Basic system metrics
        uptime_seconds = time.time() - SERVER_START_TIME
        
        # Convert to days, hours, minutes, seconds
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Format uptime as string
        uptime = f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
        
        # Process information
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        cpu_percent = process.cpu_percent(interval=0.1)
        
        # Response data
        status = "ok" if db_healthy else "degraded"
        response = {
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": uptime,
            "checks": {
                "database": "healthy" if db_healthy else "unhealthy",
                "redis": "healthy" if redis_healthy else "not configured" if not hasattr(current_app.config, 'RATELIMIT_STORAGE_URL') else "unhealthy"
            },
            "system": {
                "memory_usage_mb": round(memory_info.rss / 1024 / 1024, 2),
                "cpu_percent": round(cpu_percent, 2),
                "python_version": platform.python_version(),
                "platform": platform.platform()
            }
        }
        
        # Add version information if available
        try:
            version_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'version.txt')
            with open(version_path, 'r') as version_file:
                response["version"] = version_file.read().strip()
        except (FileNotFoundError, IOError):
            response["version"] = "unknown"
        
        return jsonify(response), 200 if status == "ok" else 503
    except Exception as e:
        current_app.logger.error(f"Health check error: {str(e)}")
        return jsonify({
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }), 500
    finally:
        close_db_session()

@system_bp.route('/metrics', methods=['GET'])
@authenticate
@require_roles(['admin'])
def metrics():
    """Endpoint to expose basic application metrics for monitoring."""
    db_session = get_db_session()
    try:
        # User metrics
        total_users = db_session.query(User).count()
        active_users = db_session.query(User).filter_by(is_active=True).count()
        
        # Session metrics
        total_active_sessions = db_session.query(RefreshToken).filter_by(
            is_revoked=False
        ).filter(
            RefreshToken.expires_at > datetime.utcnow()
        ).count()
        
        # Login metrics (could be tracked in a separate table in a real implementation)
        recent_logins = db_session.query(User).filter(
            User.last_login_at > datetime.utcnow() - timedelta(days=1)
        ).count()
        
        # System metrics
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        uptime_seconds = time.time() - SERVER_START_TIME
        
        return jsonify({
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": int(uptime_seconds),
            "user_metrics": {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": total_users - active_users,
                "recent_logins_24h": recent_logins
            },
            "session_metrics": {
                "active_sessions": total_active_sessions
            },
            "system_metrics": {
                "memory_usage_mb": round(memory_info.rss / 1024 / 1024, 2),
                "cpu_percent": round(process.cpu_percent(interval=0.1), 2),
                "open_file_descriptors": len(process.open_files()),
                "thread_count": process.num_threads()
            }
        }), 200
    finally:
        close_db_session()

# Optional: Add a catch-all route for 404s
@system_bp.app_errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found", "message": str(e)}), 404