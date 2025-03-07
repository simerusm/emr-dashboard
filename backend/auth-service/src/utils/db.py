from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from ..config import app_config
from ..models import Base

engine = create_engine(app_config.SQLALCHEMY_DATABASE_URI) # Manages db connection
session_factory = sessionmaker(bind=engine) # Creates Session objects to interact with the binded db
Session = scoped_session(session_factory) # Ensures each thread/request has its own Session instance

def init_db():
    """Initialize the database schema."""
    Base.metadata.create_all(engine)

def get_db_session():
    """Get a database session."""
    return Session()

def close_db_session(exception=None):
    """Close the database session, cleans up the thread-local session registry."""
    Session.remove()