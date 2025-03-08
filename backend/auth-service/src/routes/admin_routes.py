import re
from datetime import datetime
from flask import Blueprint, request, jsonify, g, current_app

from ..models import User, Role
from ..services import AuthService, RBACService
from ..utils import get_db_session, close_db_session
from ..middleware.auth_middleware import authenticate, require_permissions, require_roles

# Create the blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Apply admin role requirement to all routes in this blueprint
@admin_bp.before_request
@authenticate
@require_roles(['admin'])
def before_admin_request():
    """Ensure only admin users can access admin routes."""
    pass  # The decorators handle the verification

@admin_bp.route('/roles', methods=['GET'])
def get_all_roles():
    """Get all roles (admin only)."""
    db_session = get_db_session()
    try:
        roles = db_session.query(Role).all()
        
        result = [{
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "permissions": role.get_permissions()
        } for role in roles]
        
        return jsonify({
            "roles": result
        }), 200
    finally:
        close_db_session()

@admin_bp.route('/roles', methods=['POST'])
def create_role():
    """Create a new role (admin only)."""
    data = request.get_json()
    
    name = data.get('name')
    description = data.get('description')
    permissions = data.get('permissions', [])
    
    if not name:
        return jsonify({"error": "Role name is required"}), 400
    
    # Validate role name
    if not re.match(r'^[a-zA-Z0-9_-]{3,50}', name):
        return jsonify({
            "error": "Role name must be 3-50 characters and contain only alphanumeric characters, underscores, and hyphens"
        }), 400
    
    db_session = get_db_session()
    try:
        # Check if role already exists
        existing_role = RBACService.get_role_by_name(db_session, name)
        if existing_role:
            return jsonify({"error": f"Role '{name}' already exists"}), 400
        
        # Create new role
        role = RBACService.create_role(db_session, name, description, permissions)
        
        return jsonify({
            "message": "Role created successfully",
            "role": {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "permissions": role.get_permissions()
            }
        }), 201
    finally:
        close_db_session()

@admin_bp.route('/roles/<role_name>', methods=['GET'])
def get_role(role_name):
    """Get a specific role by name (admin only)."""
    db_session = get_db_session()
    try:
        role = RBACService.get_role_by_name(db_session, role_name)
        
        if not role:
            return jsonify({"error": f"Role '{role_name}' not found"}), 404
        
        return jsonify({
            "role": {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "permissions": role.get_permissions()
            }
        }), 200
    finally:
        close_db_session()

@admin_bp.route('/roles/<role_name>', methods=['PUT'])
def update_role(role_name):
    """Update a role (admin only)."""
    data = request.get_json()
    
    description = data.get('description')
    permissions = data.get('permissions')
    
    db_session = get_db_session()
    try:
        role = RBACService.get_role_by_name(db_session, role_name)
        
        if not role:
            return jsonify({"error": f"Role '{role_name}' not found"}), 404
        
        # Prevent modifying the admin role
        if role_name == 'admin' and permissions is not None:
            return jsonify({"error": "Cannot modify permissions for the admin role"}), 403
        
        # Update description if provided
        if description is not None:
            role.description = description
        
        # Update permissions if provided
        if permissions is not None:
            role.permissions = ','.join(permissions)
        
        db_session.commit()
        
        return jsonify({
            "message": "Role updated successfully",
            "role": {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "permissions": role.get_permissions()
            }
        }), 200
    finally:
        close_db_session()

@admin_bp.route('/roles/<role_name>', methods=['DELETE'])
def delete_role(role_name):
    """Delete a role (admin only)."""
    # Prevent deleting default roles
    if role_name in ['admin', 'user']:
        return jsonify({"error": f"Cannot delete the '{role_name}' role"}), 403
    
    db_session = get_db_session()
    try:
        result = RBACService.delete_role(db_session, role_name)
        
        if not result:
            return jsonify({"error": f"Role '{role_name}' not found"}), 404
        
        return jsonify({
            "message": f"Role '{role_name}' deleted successfully"
        }), 200
    finally:
        close_db_session()

@admin_bp.route('/users', methods=['GET'])
def get_all_users():
    """Get all users (admin only)."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Cap per_page to prevent excessive queries
    per_page = min(per_page, 100)
    
    db_session = get_db_session()
    try:
        # Get paginated users
        users = db_session.query(User).limit(per_page).offset((page - 1) * per_page).all()
        total = db_session.query(User).count()
        
        result = [user.to_dict() for user in users]
        
        return jsonify({
            "users": result,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        }), 200
    finally:
        close_db_session()

@admin_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user (admin only)."""
    db_session = get_db_session()
    try:
        user = AuthService.get_user_by_id(db_session, user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "user": user.to_dict(include_sensitive=True)
        }), 200
    finally:
        close_db_session()

@admin_bp.route('/users/<user_id>/roles', methods=['PUT'])
def update_user_roles(user_id):
    """Update roles for a user (admin only)."""
    data = request.get_json()
    roles = data.get('roles', [])
    
    if not roles:
        return jsonify({"error": "At least one role must be provided"}), 400
    
    db_session = get_db_session()
    try:
        user = AuthService.get_user_by_id(db_session, user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Clear existing roles
        user.roles = []
        
        # Add new roles
        for role_name in roles:
            role = RBACService.get_role_by_name(db_session, role_name)
            if role:
                user.roles.append(role)
            else:
                db_session.rollback()
                return jsonify({"error": f"Role '{role_name}' not found"}), 404
        
        db_session.commit()
        
        return jsonify({
            "message": "User roles updated successfully",
            "user": user.to_dict()
        }), 200
    finally:
        close_db_session()

@admin_bp.route('/users/<user_id>/activate', methods=['POST'])
def activate_user(user_id):
    """Activate a user account (admin only)."""
    db_session = get_db_session()
    try:
        user = AuthService.get_user_by_id(db_session, user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user.is_active = True
        db_session.commit()
        
        return jsonify({
            "message": "User activated successfully",
            "user": user.to_dict()
        }), 200
    finally:
        close_db_session()

@admin_bp.route('/users/<user_id>/deactivate', methods=['POST'])
def deactivate_user(user_id):
    """Deactivate a user account (admin only)."""
    # Prevent deactivating the last admin
    db_session = get_db_session()
    try:
        user = AuthService.get_user_by_id(db_session, user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Check if this is the last admin
        is_admin = any(role.name == 'admin' for role in user.roles)
        if is_admin:
            # Count other active admins
            admin_role = RBACService.get_role_by_name(db_session, 'admin')
            admins_count = db_session.query(User).filter(
                User.roles.contains(admin_role),
                User.is_active == True,
                User.id != user.id
            ).count()
            
            if admins_count == 0:
                return jsonify({
                    "error": "Cannot deactivate the last admin user"
                }), 403
        
        user.is_active = False
        db_session.commit()
        
        return jsonify({
            "message": "User deactivated successfully",
            "user": user.to_dict()
        }), 200
    finally:
        close_db_session()