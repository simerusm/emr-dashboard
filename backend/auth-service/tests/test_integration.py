import json
import unittest
import time
from datetime import datetime, timedelta

from src.app import app
from src.models import User, Role, RefreshToken
from src.config import TestingConfig
from src.services import AuthService, RBACService
from src.utils import get_db_session, init_db, close_db_session

class TestIntegration(unittest.TestCase):
    """Integration tests for the authentication service."""
    
    def setUp(self):
        """Set up test client and database."""
        # Configure app for testing
        app.config.from_object(TestingConfig)
        self.client = app.test_client()
        
        # Initialize test database
        with app.app_context():
            init_db()
            
            # Create test roles and users
            db_session = get_db_session()
            
            # Create roles
            admin_role = Role(
                name="admin",
                description="Administrator role",
                permissions="create_user,read_user,update_user,delete_user,manage_roles"
            )
            
            user_role = Role(
                name="user",
                description="Regular user role",
                permissions="read_self,update_self"
            )
            
            db_session.add_all([admin_role, user_role])
            db_session.commit()
            
            # Create an admin user
            admin_user = User(
                email="admin@example.com",
                username="admin",
                password_hash=AuthService.hash_password("AdminPassword123!"),
                is_active=True
            )
            admin_user.roles.append(admin_role)
            
            db_session.add(admin_user)
            db_session.commit()
            
            close_db_session()
    
    def tearDown(self):
        """Clean up after tests."""
        pass
    
    def test_complete_user_lifecycle(self):
        """Test the complete user lifecycle from registration to deletion."""
        # 1. Register a new user
        registration_payload = {
            "email": "lifecycle@example.com",
            "username": "lifecycle",
            "password": "Lifecycle123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        reg_response = self.client.post(
            '/auth/register',
            json=registration_payload
        )
        
        self.assertEqual(reg_response.status_code, 201)
        reg_data = json.loads(reg_response.data)
        user_id = reg_data.get("user_id")
        
        # 2. Login as admin
        admin_login = {
            "email": "admin@example.com",
            "password": "AdminPassword123!"
        }
        
        admin_response = self.client.post('/auth/login', json=admin_login)
        admin_token = json.loads(admin_response.data).get("access_token")
        
        # 3. Login as the new user
        user_login = {
            "email": "lifecycle@example.com",
            "password": "Lifecycle123!"
        }
        
        login_response = self.client.post('/auth/login', json=user_login)
        self.assertEqual(login_response.status_code, 200)
        
        login_data = json.loads(login_response.data)
        user_token = login_data.get("access_token")
        refresh_token = login_data.get("refresh_token")
        
        # 4. Get user profile
        profile_response = self.client.get(
            '/users/me',
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        self.assertEqual(profile_response.status_code, 200)
        profile_data = json.loads(profile_response.data).get("user", {})
        self.assertEqual(profile_data.get("username"), "lifecycle")
        self.assertEqual(profile_data.get("first_name"), "Test")
        
        # 5. Update user profile
        update_payload = {
            "first_name": "Updated",
            "last_name": "Profile"
        }
        
        update_response = self.client.put(
            '/users/me',
            headers={"Authorization": f"Bearer {user_token}"},
            json=update_payload
        )
        
        self.assertEqual(update_response.status_code, 200)
        updated_data = json.loads(update_response.data).get("user", {})
        self.assertEqual(updated_data.get("first_name"), "Updated")
        self.assertEqual(updated_data.get("last_name"), "Profile")
        
        # 6. Change password
        change_payload = {
            "current_password": "Lifecycle123!",
            "new_password": "NewLifecycle123!"
        }
        
        change_response = self.client.post(
            '/users/me/change-password',
            headers={"Authorization": f"Bearer {user_token}"},
            json=change_payload
        )
        
        self.assertEqual(change_response.status_code, 200)
        
        # 7. Logout
        logout_payload = {
            "refresh_token": refresh_token
        }
        
        logout_response = self.client.post(
            '/users/me/logout',
            headers={"Authorization": f"Bearer {user_token}"},
            json=logout_payload
        )
        
        self.assertEqual(logout_response.status_code, 200)
        
        # 8. Login with new password
        new_login = {
            "email": "lifecycle@example.com",
            "password": "NewLifecycle123!"
        }
        
        new_login_response = self.client.post('/auth/login', json=new_login)
        self.assertEqual(new_login_response.status_code, 200)
        
        new_login_data = json.loads(new_login_response.data)
        new_user_token = new_login_data.get("access_token")
        
        # 9. Admin assigns additional role to user
        role_update_payload = {
            "roles": ["user", "admin"]
        }
        
        role_update_response = self.client.put(
            f'/admin/users/{user_id}/roles',
            headers={"Authorization": f"Bearer {admin_token}"},
            json=role_update_payload
        )
        
        self.assertEqual(role_update_response.status_code, 200)
        
        # 10. User should now have admin permissions
        roles_response = self.client.get(
            '/admin/roles',
            headers={"Authorization": f"Bearer {new_user_token}"}
        )
        
        self.assertEqual(roles_response.status_code, 200)
        
        # 11. Admin deactivates the user
        deactivate_response = self.client.post(
            f'/admin/users/{user_id}/deactivate',
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        self.assertEqual(deactivate_response.status_code, 200)
        
        # 12. User should no longer be able to login
        deactivated_login = {
            "email": "lifecycle@example.com",
            "password": "NewLifecycle123!"
        }
        
        deactivated_response = self.client.post('/auth/login', json=deactivated_login)
        self.assertEqual(deactivated_response.status_code, 401)
    
    def test_token_lifecycle(self):
        """Test the complete token lifecycle."""
        # Create a new user for this test
        db_session = get_db_session()
        
        token_user = User(
            email="token@example.com",
            username="tokenuser",
            password_hash=AuthService.hash_password("TokenPass123!"),
            is_active=True
        )
        
        user_role = db_session.query(Role).filter_by(name="user").first()
        token_user.roles.append(user_role)
        
        db_session.add(token_user)
        db_session.commit()
        
        close_db_session()
        
        # 1. Login to get tokens
        login_payload = {
            "email": "token@example.com",
            "password": "TokenPass123!"
        }
        
        login_response = self.client.post('/auth/login', json=login_payload)
        self.assertEqual(login_response.status_code, 200)
        
        login_data = json.loads(login_response.data)
        access_token = login_data.get("access_token")
        refresh_token = login_data.get("refresh_token")
        
        # 2. Access protected endpoint with access token
        protected_response = self.client.get(
            '/users/protected-test',
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        self.assertEqual(protected_response.status_code, 200)
        
        # 3. Use refresh token to get new tokens
        refresh_payload = {
            "refresh_token": refresh_token
        }
        
        refresh_response = self.client.post('/auth/refresh', json=refresh_payload)
        self.assertEqual(refresh_response.status_code, 200)
        
        refresh_data = json.loads(refresh_response.data)
        new_access_token = refresh_data.get("access_token")
        new_refresh_token = refresh_data.get("refresh_token")
        
        # 4. Original refresh token should no longer work
        repeat_refresh_response = self.client.post('/auth/refresh', json=refresh_payload)
        self.assertEqual(repeat_refresh_response.status_code, 401)
        
        # 5. New access token should work
        new_protected_response = self.client.get(
            '/users/protected-test',
            headers={"Authorization": f"Bearer {new_access_token}"}
        )
        
        self.assertEqual(new_protected_response.status_code, 200)
        
        # 6. Get user's active sessions
        sessions_response = self.client.get(
            '/users/me/sessions',
            headers={"Authorization": f"Bearer {new_access_token}"}
        )
        
        self.assertEqual(sessions_response.status_code, 200)
        sessions_data = json.loads(sessions_response.data)
        sessions = sessions_data.get("sessions", [])
        self.assertGreaterEqual(len(sessions), 1)
        
        # Extract session ID
        session_id = sessions[0].get("id")
        
        # 7. Revoke specific session
        revoke_response = self.client.delete(
            f'/users/me/sessions/{session_id}',
            headers={"Authorization": f"Bearer {new_access_token}"}
        )
        
        self.assertEqual(revoke_response.status_code, 200)
        
        # 8. New refresh token should no longer work
        new_refresh_payload = {
            "refresh_token": new_refresh_token
        }
        
        final_refresh_response = self.client.post('/auth/refresh', json=new_refresh_payload)
        self.assertEqual(final_refresh_response.status_code, 401)
    
    def test_rate_limiting(self):
        """Test that rate limiting is properly enforced."""
        # Make multiple requests in quick succession
        for i in range(5):
            self.client.get('/health')
        
        # Check if rate limit headers are present
        response = self.client.get('/health')
        headers = response.headers
        
        self.assertIn('X-RateLimit-Limit', headers)
        self.assertIn('X-RateLimit-Remaining', headers)
        self.assertIn('X-RateLimit-Reset', headers)
    
    def test_security_headers(self):
        """Test that security headers are properly set."""
        response = self.client.get('/health')
        headers = response.headers
        
        self.assertIn('Content-Security-Policy', headers)
        self.assertIn('X-Content-Type-Options', headers)
        self.assertIn('X-Frame-Options', headers)
        self.assertIn('X-XSS-Protection', headers)
        self.assertIn('Referrer-Policy', headers)
        self.assertIn('Permissions-Policy', headers)

if __name__ == '__main__':
    unittest.main()