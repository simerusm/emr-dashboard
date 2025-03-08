import json
import unittest
import jwt
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.app import app
from src.models import User, Role, RefreshToken
from src.config import TestingConfig
from src.services import AuthService, RBACService
from src.utils import get_db_session, init_db, close_db_session

class TestAuthService(unittest.TestCase):
    def setUp(self):
        """Set up test client and database."""
        # Configure app for testing
        app.config.from_object(TestingConfig)
        self.client = app.test_client()
        
        # Initialize test database
        with app.app_context():
            init_db()
            
            # Create test admin user and role
            db_session = get_db_session()
            
            # Create admin role
            admin_role = Role(
                name="admin",
                description="Administrator role",
                permissions="create_user,read_user,update_user,delete_user,manage_roles"
            )
            
            # Create regular user role
            user_role = Role(
                name="user",
                description="Regular user role",
                permissions="read_self,update_self"
            )
            
            db_session.add(admin_role)
            db_session.add(user_role)
            db_session.commit()
            
            # Create admin user
            admin_password_hash = AuthService.hash_password("AdminPassword123!")
            admin_user = User(
                email="admin@example.com",
                username="admin",
                password_hash=admin_password_hash,
                is_active=True
            )
            admin_user.roles.append(admin_role)
            
            # Create regular user
            user_password_hash = AuthService.hash_password("UserPassword123!")
            regular_user = User(
                email="user@example.com",
                username="regularuser",
                password_hash=user_password_hash,
                is_active=True
            )
            regular_user.roles.append(user_role)
            
            db_session.add(admin_user)
            db_session.add(regular_user)
            db_session.commit()
            
            close_db_session()
    
    def tearDown(self):
        """Clean up after tests."""
        pass
    
    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get("status"), "ok")
    
    def test_registration_and_login(self):
        """Test user registration and login flow."""
        # Register a new user
        registration_payload = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "ValidPass123!"
        }
        
        reg_response = self.client.post(
            '/auth/register',
            json=registration_payload
        )
        
        self.assertEqual(reg_response.status_code, 201)
        reg_data = json.loads(reg_response.data)
        self.assertIn("User created successfully", reg_data.get("message", ""))
        
        # Login with the new user
        login_payload = {
            "email": "newuser@example.com",
            "password": "ValidPass123!"
        }
        
        login_response = self.client.post(
            '/auth/login',
            json=login_payload
        )
        
        self.assertEqual(login_response.status_code, 200)
        login_data = json.loads(login_response.data)
        self.assertIn("access_token", login_data)
        self.assertIn("refresh_token", login_data)
        
        # Verify the access token
        access_token = login_data.get("access_token")
        payload = jwt.decode(
            access_token,
            TestingConfig.JWT_SECRET_KEY,
            algorithms=['HS256']
        )
        self.assertEqual(payload.get("username"), "newuser")
    
    def test_invalid_login(self):
        """Test login with invalid credentials."""
        login_payload = {
            "email": "user@example.com",
            "password": "WrongPassword123!"
        }
        
        response = self.client.post(
            '/auth/login',
            json=login_payload
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data.get("error"), "Invalid credentials")
    
    def test_protected_endpoint(self):
        """Test access to protected endpoint with authentication."""
        # Login to get token
        login_payload = {
            "email": "user@example.com",
            "password": "UserPassword123!"
        }
        
        login_response = self.client.post(
            '/auth/login',
            json=login_payload
        )
        
        self.assertEqual(login_response.status_code, 200)
        login_data = json.loads(login_response.data)
        access_token = login_data.get("access_token")
        
        # Access protected endpoint
        response = self.client.get(
            '/users/protected-test',
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("Hello", data.get("message", ""))
    
    def test_protected_endpoint_without_auth(self):
        """Test access to protected endpoint without authentication."""
        response = self.client.get('/users/protected-test')
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data.get("error"), "Missing authorization header")
    
    def test_refresh_token(self):
        """Test refresh token flow."""
        # Login to get tokens
        login_payload = {
            "email": "user@example.com",
            "password": "UserPassword123!"
        }
        
        login_response = self.client.post(
            '/auth/login',
            json=login_payload
        )
        
        self.assertEqual(login_response.status_code, 200)
        login_data = json.loads(login_response.data)
        refresh_token = login_data.get("refresh_token")
        
        # Use refresh token to get new access token
        refresh_payload = {
            "refresh_token": refresh_token
        }
        
        refresh_response = self.client.post(
            '/auth/refresh',
            json=refresh_payload
        )
        
        self.assertEqual(refresh_response.status_code, 200)
        refresh_data = json.loads(refresh_response.data)
        self.assertIn("access_token", refresh_data)
        self.assertIn("refresh_token", refresh_data)
        
        # Ensure old refresh token is no longer valid
        repeat_refresh_response = self.client.post(
            '/auth/refresh',
            json=refresh_payload
        )
        
        self.assertEqual(repeat_refresh_response.status_code, 401)
    
    def test_invalid_registration_data(self):
        """Test registration with invalid data."""
        # Test missing email
        invalid_payload = {
            "username": "invaliduser",
            "password": "ValidPass123!"
        }
        
        response = self.client.post(
            '/auth/register',
            json=invalid_payload
        )
        
        self.assertEqual(response.status_code, 400)
        
        # Test invalid email format
        invalid_payload = {
            "email": "not-an-email",
            "username": "invaliduser",
            "password": "ValidPass123!"
        }
        
        response = self.client.post(
            '/auth/register',
            json=invalid_payload
        )
        
        self.assertEqual(response.status_code, 400)
        
        # Test weak password
        invalid_payload = {
            "email": "weak@example.com",
            "username": "weakuser",
            "password": "password"
        }
        
        response = self.client.post(
            '/auth/register',
            json=invalid_payload
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_role_based_access(self):
        """Test role-based access control."""
        # Login as admin
        admin_login_payload = {
            "email": "admin@example.com",
            "password": "AdminPassword123!"
        }
        
        admin_login_response = self.client.post(
            '/auth/login',
            json=admin_login_payload
        )
        
        admin_token = json.loads(admin_login_response.data).get("access_token")
        
        # Login as regular user
        user_login_payload = {
            "email": "user@example.com",
            "password": "UserPassword123!"
        }
        
        user_login_response = self.client.post(
            '/auth/login',
            json=user_login_payload
        )
        
        user_token = json.loads(user_login_response.data).get("access_token")
        
        # Test admin access to admin endpoint
        admin_response = self.client.get(
            '/admin/roles',
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        self.assertEqual(admin_response.status_code, 200)
        
        # Test regular user access to admin endpoint (should fail)
        user_response = self.client.get(
            '/admin/roles',
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        self.assertEqual(user_response.status_code, 403)
    
    def test_user_profile(self):
        """Test user profile endpoint."""
        # Login as regular user
        login_payload = {
            "email": "user@example.com",
            "password": "UserPassword123!"
        }
        
        login_response = self.client.post(
            '/auth/login',
            json=login_payload
        )
        
        token = json.loads(login_response.data).get("access_token")
        
        # Get user profile
        profile_response = self.client.get(
            '/users/me',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        self.assertEqual(profile_response.status_code, 200)
        profile_data = json.loads(profile_response.data).get("user", {})
        self.assertEqual(profile_data.get("email"), "user@example.com")
        self.assertEqual(profile_data.get("username"), "regularuser")
        
        # Update user profile
        update_payload = {
            "first_name": "Updated",
            "last_name": "User"
        }
        
        update_response = self.client.put(
            '/users/me',
            headers={"Authorization": f"Bearer {token}"},
            json=update_payload
        )
        
        self.assertEqual(update_response.status_code, 200)
        updated_data = json.loads(update_response.data).get("user", {})
        self.assertEqual(updated_data.get("first_name"), "Updated")
        self.assertEqual(updated_data.get("last_name"), "User")
    
    def test_change_password(self):
        """Test password change functionality."""
        # Login as regular user
        login_payload = {
            "email": "user@example.com",
            "password": "UserPassword123!"
        }
        
        login_response = self.client.post(
            '/auth/login',
            json=login_payload
        )
        
        token = json.loads(login_response.data).get("access_token")
        
        # Change password
        change_payload = {
            "current_password": "UserPassword123!",
            "new_password": "NewUserPassword123!"
        }
        
        change_response = self.client.post(
            '/users/me/change-password',
            headers={"Authorization": f"Bearer {token}"},
            json=change_payload
        )
        
        self.assertEqual(change_response.status_code, 200)
        
        # Try logging in with old password (should fail)
        old_login_response = self.client.post(
            '/auth/login',
            json=login_payload
        )
        
        self.assertEqual(old_login_response.status_code, 401)
        
        # Login with new password
        new_login_payload = {
            "email": "user@example.com",
            "password": "NewUserPassword123!"
        }
        
        new_login_response = self.client.post(
            '/auth/login',
            json=new_login_payload
        )
        
        self.assertEqual(new_login_response.status_code, 200)
    
    def test_logout(self):
        """Test logout functionality."""
        # Login to get tokens
        login_payload = {
            "email": "user@example.com",
            "password": "UserPassword123!"
        }
        
        login_response = self.client.post(
            '/auth/login',
            json=login_payload
        )
        
        token_data = json.loads(login_response.data)
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        
        # Logout
        logout_payload = {
            "refresh_token": refresh_token
        }
        
        logout_response = self.client.post(
            '/users/me/logout',
            headers={"Authorization": f"Bearer {access_token}"},
            json=logout_payload
        )
        
        self.assertEqual(logout_response.status_code, 200)
        
        # Try using the refresh token after logout (should fail)
        refresh_payload = {
            "refresh_token": refresh_token
        }
        
        refresh_response = self.client.post(
            '/auth/refresh',
            json=refresh_payload
        )
        
        self.assertEqual(refresh_response.status_code, 401)

if __name__ == '__main__':
    unittest.main()