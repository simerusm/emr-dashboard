from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# By creating this, it will create all tables that Base is a derivation of
Base = declarative_base()

# Association table for many-to-many relationship between users and roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id')),
    Column('role_id', String, ForeignKey('roles.id'))
)

class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username}>"
    
    def to_dict(self, include_sensitive=False):
        """Convert user object to dictionary."""
        user_dict = {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "roles": [role.name for role in self.roles]
        }
        
        # Include sensitive information only if explicitly requested
        if include_sensitive:
            user_dict["verification_token"] = self.verification_token
        
        return user_dict


class Role(Base):
    """Role model for RBAC."""
    __tablename__ = 'roles'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200), nullable=True)
    
    # Permissions are a comma-separated list of permission strings
    permissions = Column(Text, nullable=False, default="")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    
    def __repr__(self):
        return f"<Role {self.name}>"
    
    def get_permissions(self):
        """Get list of permissions assigned to this role."""
        return self.permissions.split(',') if self.permissions else []


class RefreshToken(Base):
    """Refresh token model for JWT authentication."""
    __tablename__ = 'refresh_tokens'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    token = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow)
    
    # Device information for security
    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
    
    def __repr__(self):
        return f"<RefreshToken {self.id}>"