import os
from datetime import timedelta

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration object."""
    # Application settings
    APP_NAME = "Patient Data Service"
    
    # Database configuration
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "patient_data_db")
    
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Log SQL queries to console (for development)
    
    # Database connection pool settings
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))  # Default number of connections
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))  # Max extra connections when pool is full
    DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))  # Seconds to wait for a connection
    DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "1800"))  # Recycle connections after N seconds
    
    # Query performance settings
    SLOW_QUERY_THRESHOLD = float(os.getenv("SLOW_QUERY_THRESHOLD", "0.5"))  # Log queries slower than N seconds
    
    # API configuration
    API_PREFIX = "/api/v1"
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    # Authentication configuration
    AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:5001")
    
    # Pagination defaults
    DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
    MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", "100"))
    
    # Caching configuration
    CACHE_TYPE = os.getenv("CACHE_TYPE", "simple")  # Options: simple, redis, memcached
    CACHE_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "300"))  # 5 minutes default
    
    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Security settings
    ENABLE_CONTENT_SECURITY_POLICY = os.getenv("ENABLE_CONTENT_SECURITY_POLICY", "True").lower() == "true"
    ENABLE_HSTS = os.getenv("ENABLE_HSTS", "True").lower() == "true"
    
    # Rate limiting
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "200 per minute")
    RATELIMIT_STORAGE_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    LOG_LEVEL = "DEBUG"

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:password@localhost:5432/patient_data_test"
    LOG_LEVEL = "DEBUG"
    
    # Use smaller connection pool for testing
    DB_POOL_SIZE = 2
    DB_MAX_OVERFLOW = 2
    
    # Use in-memory cache for testing
    CACHE_TYPE = "simple"

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # More conservative pool settings for production
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "900"))  # 15 minutes
    
    # Use Redis for caching in production
    CACHE_TYPE = "redis"
    
    # Override with environment variables in production
    def __init__(self):
        required_env_vars = [
            "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME", "REDIS_URL"
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
            
# Determine which configuration to use based on environment
env = os.getenv("FLASK_ENV", "development")
config_map = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
}

app_config = config_map.get(env, DevelopmentConfig)()