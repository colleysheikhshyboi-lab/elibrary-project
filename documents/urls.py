"""
URL patterns for documents app.
"""

from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # Document list and search
    path('', views.document_list, name='document_list'),
    path('search/', views.document_search, name='document_search'),
    path('stats/', views.document_stats, name='document_stats'),
    
    # Document CRUD operations
    path('upload/', views.document_upload, name='document_upload'),
    path('<slug:slug>/', views.document_detail, name='document_detail'),
    path('<slug:slug>/download/', views.document_download, name='document_download'),
    path('<slug:slug>/edit/', views.document_edit, name='document_edit'),
    path('<slug:slug>/delete/', views.document_delete, name='document_delete'),
    path('<slug:slug>/publish/', views.document_publish, name='document_publish'),
    path('<slug:slug>/unpublish/', views.document_unpublish, name='document_unpublish'),
]
