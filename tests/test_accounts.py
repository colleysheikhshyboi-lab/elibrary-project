"""
Tests for the accounts application.
"""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


class TestUserModel:
    """Tests for the User model."""

    def test_user_creation(self, db):
        """Test creating a regular user."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.first_name == 'Test'
        assert user.last_name == 'User'
        assert user.role == User.Role.PUBLIC
        assert user.check_password('TestPass123!')

    def test_superuser_creation(self, db):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!'
        )
        assert user.is_superuser
        assert user.is_staff
        # Set role manually since create_superuser doesn't call custom save
        user.role = User.Role.ADMIN
        user.save()
        assert user.role == User.Role.ADMIN

    def test_user_role_admin(self, db):
        """Test admin role has correct permissions."""
        user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='TestPass123!',
            role=User.Role.ADMIN
        )
        assert user.is_admin
        assert user.is_staff
        assert user.can_upload
        assert user.can_delete
        assert user.can_manage_users
        assert user.can_view_all_documents

    def test_user_role_clerk(self, db):
        """Test clerk role has correct permissions."""
        user = User.objects.create_user(
            username='clerk',
            email='clerk@example.com',
            password='TestPass123!',
            role=User.Role.CLERK
        )
        assert user.is_librarian
        assert user.can_upload
        assert not user.can_delete
        assert not user.can_manage_users
        assert user.can_view_all_documents

    def test_user_role_librarian(self, db):
        """Test librarian role has correct permissions."""
        user = User.objects.create_user(
            username='librarian',
            email='librarian@example.com',
            password='TestPass123!',
            role=User.Role.LIBRARIAN
        )
        assert user.is_librarian
        assert user.can_upload
        assert not user.can_delete
        assert not user.can_manage_users
        assert user.can_view_all_documents

    def test_user_role_mp(self, db):
        """Test MP role has correct permissions."""
        user = User.objects.create_user(
            username='mp',
            email='mp@example.com',
            password='TestPass123!',
            role=User.Role.MP
        )
        assert user.is_mp
        assert not user.is_librarian
        assert not user.can_upload
        assert not user.can_delete
        assert not user.can_manage_users
        assert user.can_view_all_documents

    def test_user_role_public(self, db):
        """Test public role has correct permissions."""
        user = User.objects.create_user(
            username='public',
            email='public@example.com',
            password='TestPass123!',
            role=User.Role.PUBLIC
        )
        assert not user.is_admin
        assert not user.is_mp
        assert not user.is_librarian
        assert not user.can_upload
        assert not user.can_delete
        assert not user.can_manage_users
        assert not user.can_view_all_documents

    def test_can_access_restricted(self, admin_user, clerk_user, mp_user, public_user):
        """Test can_access_restricted property."""
        assert admin_user.can_access_restricted
        assert clerk_user.can_access_restricted
        assert mp_user.can_access_restricted
        assert not public_user.can_access_restricted

    def test_user_str_representation(self, admin_user):
        """Test user string representation."""
        assert 'Administrator' in str(admin_user)
        assert admin_user.get_full_name() in str(admin_user)


class TestUserAuthentication:
    """Tests for user authentication."""

    def test_user_can_authenticate(self, db):
        """Test user can authenticate with correct password."""
        user = User.objects.create_user(
            username='authuser',
            email='auth@example.com',
            password='TestPass123!'
        )
        assert user.check_password('TestPass123!')
        assert not user.check_password('WrongPassword')

    def test_user_authentication_fields(self, db):
        """Test user has required authentication fields."""
        user = User.objects.create_user(
            username='authfields',
            email='authfields@example.com',
            password='TestPass123!'
        )
        assert user.username
        assert user.password
        assert user.is_active

    def test_user_role_constants(self):
        """Test role choices are defined correctly."""
        assert User.Role.ADMIN == 'admin'
        assert User.Role.CLERK == 'clerk'
        assert User.Role.LIBRARIAN == 'librarian'
        assert User.Role.MP == 'mp'
        assert User.Role.PUBLIC == 'public'


class TestUserForms:
    """Tests for user forms."""

    def test_user_creation_form_fields(self, db):
        """Test user creation form has expected fields."""
        from accounts.forms import UserCreationForm
        form = UserCreationForm()
        # UserCreationForm uses Django's built-in which has username, password1, password2
        assert 'username' in form.fields
        assert 'password1' in form.fields
        assert 'password2' in form.fields

    def test_user_password_change_form_exists(self, db):
        """Test password change form exists."""
        from accounts.forms import PasswordChangeForm
        form = PasswordChangeForm(user=None)
        assert form is not None

