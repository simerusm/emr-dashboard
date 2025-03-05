from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from ..config import app_config
from ..models import Base

# Create engine and session factory
engine = create_engine(app_config.SQLALCHEMY_DATABASE_URI)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def init_db():
    """Initialize the database schema."""
    Base.metadata.create_all(engine)

def get_db_session():
    """Get a database session."""
    session = Session()
    try:
        return session
    finally:
        session.close()

def close_db_session(exception=None):
    """Close the database session."""
    Session.remove()