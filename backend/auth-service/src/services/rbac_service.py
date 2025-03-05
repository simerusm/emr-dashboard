from typing import List, Optional
from sqlalchemy.orm import Session

from ..models import Role, User

class RBACService:
    """Service for handling role-based access control."""
    
    @staticmethod
    def create_role(db_session: Session, name: str, description: str = None, permissions: List[str] = None) -> Role:
        """Create a new role."""
        perms_str = ','.join(permissions) if permissions else ""
        
        role = Role(
            name=name,
            description=description,
            permissions=perms_str
        )
        
        db_session.add(role)
        db_session.commit()
        
        return role
    
    @staticmethod
    def get_role_by_name(db_session: Session, name: str) -> Optional[Role]:
        """Get a role by name."""
        return db_session.query(Role).filter_by(name=name).first()
    
    @staticmethod
    def update_role_permissions(db_session: Session, role_name: str, permissions: List[str]) -> Optional[Role]:
        """Update the permissions for a role."""
        role = db_session.query(Role).filter_by(name=role_name).first()
        
        if not role:
            return None
        
        role.permissions = ','.join(permissions)
        db_session.commit()
        
        return role
    
    @staticmethod
    def delete_role(db_session: Session, role_name: str) -> bool:
        """Delete a role."""
        role = db_session.query(Role).filter_by(name=role_name).first()
        
        if not role:
            return False
        
        db_session.delete(role)
        db_session.commit()
        
        return True
    
    @staticmethod
    def get_user_permissions(user: User) -> List[str]:
        """Get all permissions for a user based on their roles."""
        permissions = []
        
        for role in user.roles:
            permissions.extend(role.get_permissions())
        
        # Remove duplicates
        return list(set(permissions))
    
    @staticmethod
    def user_has_permission(user: User, permission: str) -> bool:
        """Check if a user has a specific permission."""
        return permission in RBACService.get_user_permissions(user)
    
    @staticmethod
    def user_has_role(user: User, role_name: str) -> bool:
        """Check if a user has a specific role."""
        return any(role.name == role_name for role in user.roles)