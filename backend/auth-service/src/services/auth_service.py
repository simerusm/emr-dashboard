import datetime
import uuid
from typing import Dict, Tuple, Optional, List

import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session
from passlib.hash import pbkdf2_sha256

from ..models import User, RefreshToken, Role
from ..config import app_config

class AuthService:
    """Service for handling authentication logic."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using PBKDF2 with SHA-256."""
        return pbkdf2_sha256.using(salt=app_config.PASSWORD_SALT.encode()).hash(password)
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        return pbkdf2_sha256.verify(password, password_hash)
    
    @staticmethod
    def generate_tokens(user: User, user_agent: str = None, ip_address: str = None) -> Tuple[str, str]:
        """Generate access and refresh tokens for a user."""
        # Create access token
        access_token_payload = {
            'sub': str(user.id),
            'username': user.username,
            'roles': [role.name for role in user.roles],
            'permissions': [perm for role in user.roles for perm in role.get_permissions()],
            'exp': datetime.datetime.utcnow() + app_config.JWT_ACCESS_TOKEN_EXPIRES,
            'iat': datetime.datetime.utcnow(),
            'jti': str(uuid.uuid4())
        }
        
        access_token = jwt.encode(
            access_token_payload,
            app_config.JWT_SECRET_KEY,
            algorithm='HS256'
        )
        
        # Create refresh token
        refresh_token_jti = str(uuid.uuid4())
        refresh_token_payload = {
            'sub': str(user.id),
            'exp': datetime.datetime.utcnow() + app_config.JWT_REFRESH_TOKEN_EXPIRES,
            'iat': datetime.datetime.utcnow(),
            'jti': refresh_token_jti
        }
        
        refresh_token = jwt.encode(
            refresh_token_payload,
            app_config.JWT_SECRET_KEY,
            algorithm='HS256'
        )
        
        return access_token, refresh_token, refresh_token_jti
    
    @staticmethod
    def store_refresh_token(db_session: Session, user: User, token_jti: str, 
                          user_agent: str = None, ip_address: str = None) -> RefreshToken:
        """Store a refresh token in the database."""
        expires_at = datetime.datetime.utcnow() + app_config.JWT_REFRESH_TOKEN_EXPIRES
        
        refresh_token = RefreshToken(
            token=token_jti,
            user_id=user.id,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        db_session.add(refresh_token)
        db_session.commit()
        
        return refresh_token
    
    @staticmethod
    def revoke_refresh_token(db_session: Session, token_jti: str) -> bool:
        """Revoke a refresh token."""
        token = db_session.query(RefreshToken).filter_by(token=token_jti).first()
        
        if token:
            token.is_revoked = True
            db_session.commit()
            return True
        
        return False
    
    @staticmethod
    def validate_access_token(token: str) -> Tuple[bool, Dict]:
        """Validate an access token."""
        try:
            payload = jwt.decode(
                token,
                app_config.JWT_SECRET_KEY,
                algorithms=['HS256']
            )
            return True, payload
        except InvalidTokenError:
            return False, {}
    
    @staticmethod
    def validate_refresh_token(db_session: Session, token: str) -> Tuple[bool, Optional[User], str]:
        """Validate a refresh token and return associated user if valid."""
        try:
            # Decode the token
            payload = jwt.decode(
                token,
                app_config.JWT_SECRET_KEY,
                algorithms=['HS256']
            )
            
            user_id = payload.get('sub')
            token_jti = payload.get('jti')
            
            # Check if the token exists and is not revoked
            db_token = db_session.query(RefreshToken).filter_by(
                token=token_jti,
                is_revoked=False
            ).first()
            
            if not db_token:
                return False, None, ""
            
            # Check if the token is expired
            if db_token.expires_at < datetime.datetime.utcnow():
                db_token.is_revoked = True
                db_session.commit()
                return False, None, ""
            
            # Get the associated user
            user = db_session.query(User).filter_by(id=uuid.UUID(user_id)).first()
            
            if not user or not user.is_active:
                return False, None, ""
            
            return True, user, token_jti
            
        except InvalidTokenError:
            return False, None, ""
    
    @staticmethod
    def get_user_by_email(db_session: Session, email: str) -> Optional[User]:
        """Get a user by email."""
        return db_session.query(User).filter_by(email=email).first()
    
    @staticmethod
    def get_user_by_username(db_session: Session, username: str) -> Optional[User]:
        """Get a user by username."""
        return db_session.query(User).filter_by(username=username).first()
    
    @staticmethod
    def get_user_by_id(db_session: Session, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        try:
            return db_session.query(User).filter_by(id=uuid.UUID(user_id)).first()
        except ValueError:
            return None
    
    @staticmethod
    def create_user(db_session: Session, email: str, username: str, password: str, 
                    first_name: str = None, last_name: str = None) -> User:
        """Create a new user."""
        password_hash = AuthService.hash_password(password)
        
        user = User(
            email=email,
            username=username,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            verification_token=str(uuid.uuid4())
        )
        
        db_session.add(user)
        db_session.commit()
        
        return user
    
    @staticmethod
    def assign_role_to_user(db_session: Session, user: User, role_name: str) -> bool:
        """Assign a role to a user."""
        role = db_session.query(Role).filter_by(name=role_name).first()
        
        if not role:
            return False
        
        user.roles.append(role)
        db_session.commit()
        
        return True
    
    @staticmethod
    def update_last_login(db_session: Session, user: User) -> User:
        """Update the last login timestamp for a user."""
        user.last_login_at = datetime.datetime.utcnow()
        db_session.commit()
        return user
    
    @staticmethod
    def clean_expired_tokens(db_session: Session) -> int:
        """Clean up expired refresh tokens."""
        expired_tokens = db_session.query(RefreshToken).filter(
            RefreshToken.expires_at < datetime.datetime.utcnow()
        ).all()
        
        count = len(expired_tokens)
        
        for token in expired_tokens:
            db_session.delete(token)
        
        db_session.commit()
        return count