"""
URL configuration for e-library project.
Routes all URLs for the parliamentary document management system.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin interface (restricted to staff only)
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('accounts/', include('accounts.urls')),
    
    # Main document URLs
    path('documents/', include('documents.urls')),
    
    # Search URLs
    path('search/', include('search.urls')),
    
    # Home page
    path('', include('core.urls')),
    
    # Members directory
    path('members/', include('members.urls')),
    
    # API URLs
    path('api/', include('api.urls', namespace='api')),
]

# Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom admin site header
admin.site.site_header = "National Assembly e-Library Administration"
admin.site.site_title = "Parliamentary Library Admin"
admin.site.index_title = "Document Management System"
