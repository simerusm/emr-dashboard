# test_app.py
import unittest
import json
from src.app import app

class TestAuthService(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get("status"), "ok")

    def test_registration_and_login(self):
        # Register a new user
        registration_payload = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "ValidPass123!"
        }
        reg_response = self.client.post(
            '/register',
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
            '/login',
            json=login_payload
        )
        self.assertEqual(login_response.status_code, 200)
        login_data = json.loads(login_response.data)
        self.assertIn("access_token", login_data)
        self.assertIn("refresh_token", login_data)

if __name__ == '__main__':
    unittest.main()