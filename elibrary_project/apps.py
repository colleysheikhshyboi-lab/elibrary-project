"""
App configuration for the e-library project.
"""

from django.apps import AppConfig


class ElibraryProjectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'elibrary_project'
    verbose_name = 'National Assembly e-Library'
