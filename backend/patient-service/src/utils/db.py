from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
import time
import logging

from ..config import app_config
from ..models.patient import Base

# Create the database engine with connection pooling
engine = create_engine(
    app_config.SQLALCHEMY_DATABASE_URI,
    poolclass=QueuePool,
    pool_size=app_config.DB_POOL_SIZE,
    max_overflow=app_config.DB_MAX_OVERFLOW,
    pool_timeout=app_config.DB_POOL_TIMEOUT,
    pool_recycle=app_config.DB_POOL_RECYCLE,
    echo=app_config.SQLALCHEMY_ECHO
)

# Add performance monitoring to SQL queries
if app_config.SQLALCHEMY_ECHO:
    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())
        
    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total_time = time.time() - conn.info['query_start_time'].pop()
        print(f"Query execution time: {total_time:.4f}s")
        if total_time > app_config.SLOW_QUERY_THRESHOLD:
            print(f"SLOW QUERY DETECTED: {statement}")
            # In production, you might want to log this to a monitoring system

# Create session factory - this creates new Session objects
session_factory = sessionmaker(bind=engine)

# Create a scoped session to ensure thread safety
# This returns the same Session object for the same thread
Session = scoped_session(session_factory)

def handle_enum_types():
    """Handle PostgreSQL enum types that may already exist."""
    from ..models.patient import Gender, BloodType
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    
    # Connect directly to the database to check and handle enum types
    try:
        conn = psycopg2.connect(
            host=app_config.DB_HOST,
            database=app_config.DB_NAME,
            user=app_config.DB_USER,
            password=app_config.DB_PASSWORD,
            port=app_config.DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if the gender enum exists
        cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_type WHERE typname = 'gender')")
        gender_exists = cursor.fetchone()[0]
        
        if gender_exists:
            # Get the current enum values
            cursor.execute("SELECT enum_range(NULL::gender)")
            current_values = cursor.fetchone()[0]
            logging.info(f"Existing gender enum values: {current_values}")
            
            # If we need to update the enum type values to match our model, we would do that here
            # For now, we'll just modify our model to match the database
            # This is done in the model definition
        
        # Check if bloodtype enum exists
        cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_type WHERE typname = 'bloodtype')")
        bloodtype_exists = cursor.fetchone()[0]
        
        if bloodtype_exists:
            # Get the current enum values
            cursor.execute("SELECT enum_range(NULL::bloodtype)")
            current_values = cursor.fetchone()[0]
            logging.info(f"Existing bloodtype enum values: {current_values}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logging.error(f"Error handling enum types: {str(e)}")

def init_db():
    """Initialize the database schema."""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    # First, handle any PostgreSQL enum types
    handle_enum_types()
    
    # Create all tables that don't exist with checkfirst=True
    Base.metadata.create_all(engine, checkfirst=True)

def get_db_session():
    """Get a database session."""
    return Session()

def close_db_session(exception=None):
    """Close the database session."""
    Session.remove()

def get_engine():
    """Get the SQLAlchemy engine."""
    return engine

# Index management for optimizing queries
def ensure_indexes():
    """
    Ensure that the necessary database indexes exist.
    This should be run during application startup.
    """
    # This function would programmatically create indexes that aren't
    # defined in the models, but are needed for performance.
    # For PostgreSQL, you can use the following pattern:
    connection = engine.connect()
    try:
        # Example: Index for patient search by name
        connection.execute(
            text("CREATE INDEX IF NOT EXISTS idx_patient_name ON patients ((lower(first_name) || ' ' || lower(last_name)));")
        )
        
        # Example: Index for text search
        connection.execute(
            text("""
            CREATE INDEX IF NOT EXISTS idx_patient_text_search 
            ON patients USING gin(to_tsvector('english', 
                coalesce(first_name,'') || ' ' || 
                coalesce(last_name,'') || ' ' || 
                coalesce(mrn,'')));
            """)
        )
        
        # Example: Partial index for active patients (if you frequently query only active patients)
        connection.execute(
            text("CREATE INDEX IF NOT EXISTS idx_active_patients ON patients (id) WHERE is_active = TRUE;")
        )

    except Exception as e:
        print(f"Error creating indexes: {e}")
    finally:
        connection.close()