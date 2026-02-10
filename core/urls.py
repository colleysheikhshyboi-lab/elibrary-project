"""
URL patterns for core/home views.
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
]
