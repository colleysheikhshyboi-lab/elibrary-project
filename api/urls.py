"""
API URL Configuration for the e-Library system.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from . import views

app_name = 'api'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'members', views.MemberViewSet, basename='member')
router.register(r'constituencies', views.ConstituencyViewSet, basename='constituency')
router.register(r'parties', views.PartyViewSet, basename='party')
router.register(r'documents', views.DocumentViewSet, basename='document')
router.register(r'categories', views.DocumentCategoryViewSet, basename='category')

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    
    # API Documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger-ui'),
    
    # Authentication
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]

