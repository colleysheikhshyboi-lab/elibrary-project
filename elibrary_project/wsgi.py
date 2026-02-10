"""
WSGI config for e-library project.
It exposes the WSGI callable as a module-level variable named ``application``.
Optimized for deployment with WhiteNoise for static files.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elibrary_project.settings')

application = get_wsgi_application()
