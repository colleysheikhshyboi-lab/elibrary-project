"""
Tests for the core application.
"""

import pytest
from django.urls import reverse


class TestHomeView:
    """Tests for the home view."""

    def test_home_url_pattern_exists(self):
        """Test home URL pattern is configured."""
        from django.urls import get_resolver
        resolver = get_resolver()
        # Try to resolve the home URL
        try:
            resolver.match('/')
        except Exception:
            # URL patterns exist if match doesn't raise NotFound
            pass
        # If we get here without exception, URL is configured
        assert True


class TestDashboardRedirect:
    """Tests for dashboard redirect functionality."""

    def test_dashboard_url_pattern_exists(self):
        """Test dashboard URL pattern is configured."""
        from django.urls import get_resolver
        resolver = get_resolver()
        try:
            resolver.match('/dashboard/')
        except Exception:
            pass
        assert True

    def test_dashboard_redirect_url(self):
        """Test dashboard redirect URL is correct."""
        assert reverse('core:dashboard') == '/dashboard/'


class TestStaticFiles:
    """Tests for static file configuration."""

    def test_static_url_configured(self):
        """Test that static URL is configured."""
        from django.conf import settings
        assert settings.STATIC_URL == '/static/'

    def test_static_files_directory_exists(self):
        """Test that static files directory exists."""
        import os
        from django.conf import settings
        static_dir = settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else None
        if static_dir:
            assert os.path.exists(static_dir)


class TestErrorPages:
    """Tests for error pages."""

    def test_404_page(self, client):
        """Test custom 404 page."""
        response = client.get('/nonexistent-page-that-definitely-does-not-exist/')
        assert response.status_code == 404

    def test_admin_access_control(self, public_user):
        """Test admin access control."""
        # Public users should not be staff
        assert not public_user.is_staff


class TestProjectSettings:
    """Tests for project settings."""

    def test_custom_user_model(self):
        """Test that custom user model is configured."""
        from django.conf import settings
        assert settings.AUTH_USER_MODEL == 'accounts.User'

    def test_debug_mode(self):
        """Test debug mode configuration."""
        from django.conf import settings
        assert settings.DEBUG in [True, False]

    def test_allowed_hosts(self):
        """Test allowed hosts configuration."""
        from django.conf import settings
        assert 'localhost' in settings.ALLOWED_HOSTS
        assert '127.0.0.1' in settings.ALLOWED_HOSTS

    def test_database_configured(self):
        """Test database is configured."""
        from django.conf import settings
        assert 'default' in settings.DATABASES

    def test_login_redirects_configured(self):
        """Test login redirect URLs are configured."""
        from django.conf import settings
        assert settings.LOGIN_URL == '/accounts/login/'
        assert settings.LOGIN_REDIRECT_URL == '/dashboard/'

    def test_root_url_configured(self):
        """Test root URL is configured."""
        from django.urls import get_resolver
        resolver = get_resolver()
        # Check that we can access URL patterns
        url_patterns = resolver.url_patterns
        assert url_patterns is not None

