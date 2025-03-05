import re
from typing import Dict, Any, Tuple, List, Optional

class Validator:
    """Utility class for validating input data."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Validate password strength.
        
        Requirements:
        - At least 8 characters long
        - Contains at least one uppercase letter
        - Contains at least one lowercase letter
        - Contains at least one digit
        - Contains at least one special character
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r"[0-9]", password):
            return False, "Password must contain at least one digit"
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is valid"
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """
        Validate username format.
        
        Requirements:
        - 3-30 characters long
        - Contains only alphanumeric characters, underscores, and hyphens
        - Starts with an alphanumeric character
        """
        if not 3 <= len(username) <= 30:
            return False, "Username must be 3-30 characters long"
        
        if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$", username):
            return False, "Username must contain only alphanumeric characters, underscores, and hyphens, and start with an alphanumeric character"
        
        return True, "Username is valid"
    
    @staticmethod
    def validate_registration_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate user registration data."""
        errors = []
        
        # Check required fields
        required_fields = ['email', 'username', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"{field.capitalize()} is required")
        
        # If any required fields are missing, return early
        if errors:
            return False, errors
        
        # Validate email
        if not Validator.validate_email(data['email']):
            errors.append("Invalid email format")
        
        # Validate username
        username_valid, username_error = Validator.validate_username(data['username'])
        if not username_valid:
            errors.append(username_error)
        
        # Validate password
        password_valid, password_error = Validator.validate_password(data['password'])
        if not password_valid:
            errors.append(password_error)
        
        # If there are any errors, return False and the list of errors
        if errors:
            return False, errors
        
        # If all validations pass, return True with an empty list of errors
        return True, []