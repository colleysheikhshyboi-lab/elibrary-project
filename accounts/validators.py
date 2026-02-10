"""
Custom password validators for enhanced security.
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class PasswordStrengthValidator:
    """
    Validates that passwords meet minimum strength requirements.
    """
    
    def __init__(self, min_length=12):
        self.min_length = min_length
    
    def validate(self, password, user=None):
        errors = []
        
        # Check minimum length
        if len(password) < self.min_length:
            errors.append(
                f'Password must be at least {self.min_length} characters long.'
            )
        
        # Check for uppercase letters
        if not any(char.isupper() for char in password):
            errors.append('Password must contain at least one uppercase letter.')
        
        # Check for lowercase letters
        if not any(char.islower() for char in password):
            errors.append('Password must contain at least one lowercase letter.')
        
        # Check for digits
        if not any(char.isdigit() for char in password):
            errors.append('Password must contain at least one digit.')
        
        # Check for special characters
        special_chars = '!@#$%^&*()_+-=[]{}|;\':",./<>?'
        if not any(char in special_chars for char in password):
            errors.append('Password must contain at least one special character.')
        
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self):
        return _(
            'Your password must be at least 12 characters long, '
            'contain uppercase and lowercase letters, digits, '
            'and special characters.'
        )


class CommonPasswordValidator:
    """
    Validates that passwords are not commonly used.
    """
    
    def validate(self, password, user=None):
        # List of common passwords to reject
        common_passwords = [
            'password', 'password123', '123456', '12345678',
            'qwerty', 'abc123', 'monkey123', 'letmein',
            'dragon', 'baseball', 'iloveyou', 'master',
            'sunshine', 'ashley', 'bailey', 'passw0rd',
            'shadow', '123123', '654321', 'superman',
            'qazwsx', 'michael', 'football', 'password1',
            'password2', 'welcome', 'hello', 'charlie',
            'donald', 'qwerty123', 'admin', 'root',
            'parliament', 'assembly', 'gambia', 'banjul'
        ]
        
        if password.lower() in common_passwords:
            raise ValidationError(
                'This password is too common. Please choose a more unique password.'
            )
    
    def get_help_text(self):
        return _(
            'Your password cannot be a commonly used password.'
        )


class UsernamePasswordValidator:
    """
    Validates that passwords don't contain the username.
    """
    
    def validate(self, password, user=None):
        if user and user.username:
            if user.username.lower() in password.lower():
                raise ValidationError(
                    'Your password cannot contain your username.'
                )
    
    def get_help_text(self):
        return _(
            'Your password cannot contain your username.'
        )
